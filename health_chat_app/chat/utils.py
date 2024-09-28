import os
import re
import openai
import spacy
from dateutil import parser
from django.conf import settings
from .models import AppointmentChangeRequest
from neo4j import GraphDatabase
from datetime import datetime

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Set up OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

# Initialize LLM
from langchain.chat_models import ChatOpenAI

def initialize_llm():
    llm_provider = os.getenv('LLM_PROVIDER', 'openai')
    llm_model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    api_key = os.getenv('LLM_API_KEY', openai_api_key)

    if llm_provider == 'openai':
        return ChatOpenAI(model=llm_model, openai_api_key=api_key)
    else:
        raise ValueError("Unsupported LLM provider.")

llm = initialize_llm()


nlp = spacy.load('en_core_web_sm')


neo4j_uri = os.getenv('NEO4J_URI')
neo4j_user = os.getenv('NEO4J_USER')
neo4j_password = os.getenv('NEO4J_PASSWORD')

driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

def is_allowed_topic(user_input):
    try:
        response = openai.Moderation.create(
            input=user_input,
            api_key=openai_api_key
        )
        flagged = response["results"][0]["flagged"]
        if flagged:
            return False
        return True
    except Exception as e:
        print(f"Error during content moderation: {e}")
        
        return False

def detect_appointment_change(user_input):
    keywords = ['reschedule', 'appointment', 'schedule', 'cancel', 'book']
    for word in keywords:
        if word in user_input.lower():
            return True
    return False

def detect_medication_change(user_input):
    keywords = [
        'medication change', 'change medication', 'new medication',
        'stop medication', 'dosage', 'increase dosage', 'decrease dosage'
    ]
    for word in keywords:
        if word in user_input.lower():
            return True
    return False

def parse_requested_time(user_input):
    date_strings = re.findall(
        r'\b(?:on )?(?:\w{3,9} \d{1,2}(?:, \d{4})?)\b',
        user_input, re.IGNORECASE
    )
    time_strings = re.findall(
        r'\b(?:at )?\d{1,2}(?::\d{2})?(?:\s?[ap]m)?\b',
        user_input, re.IGNORECASE
    )

    date_time_str = ' '.join(date_strings + time_strings)
    try:
        requested_time = parser.parse(date_time_str)
        return requested_time
    except (ValueError, OverflowError):
        return None

def extract_medication_info(user_input):
    doc = nlp(user_input)
    medications = []
    for ent in doc.ents:
        if ent.label_ == 'DRUG':
            medications.append(ent.text)
    return medications

def extract_entities(user_input):
    doc = nlp(user_input)
    entities = {}
    for ent in doc.ents:
        entities[ent.label_] = ent.text
    return entities

def get_conversation_history(messages, max_tokens=500):
    conversation = ''
    total_tokens = 0
    for message in reversed(messages):
        
        message_text = f"{message.text}\n"
        message_tokens = len(message_text.split())
        if total_tokens + message_tokens > max_tokens:
            break
        conversation = message_text + conversation
        total_tokens += message_tokens
    return conversation

def save_entities_to_knowledge_graph(entities, patient):
    with driver.session() as session:
        
        session.run(
            """
            MERGE (p:Patient {name: $name})
            """,
            name=f"{patient.first_name} {patient.last_name}"
        )
        for label, value in entities.items():
            
            session.run(
                """
                MERGE (e:Entity {label: $label, value: $value})
                """,
                label=label,
                value=value
            )
            
            session.run(
                """
                MATCH (p:Patient {name: $name})
                MATCH (e:Entity {label: $label, value: $value})
                MERGE (p)-[:HAS_ENTITY]->(e)
                """,
                name=f"{patient.first_name} {patient.last_name}",
                label=label,
                value=value
            )

def summarize_conversation(messages):
    if not messages:
        return ""
    conversation = '\n'.join([msg.text for msg in messages])
    prompt = f"""
    Summarize the following conversation between a patient and an AI health assistant, highlighting any important medical information or concerns.

    Conversation:
    {conversation}

    Summary:
    """
    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"Error during summarization: {e}")
        return ""

def get_bot_response(user_input, patient):
    if not is_allowed_topic(user_input):
        return "I'm sorry, but I can only assist with health-related questions."

    # Handle appointment change requests
    if detect_appointment_change(user_input):
        requested_time = parse_requested_time(user_input)
        if requested_time:
            
            AppointmentChangeRequest.objects.create(patient=patient, requested_time=requested_time)
            requested_time_formatted = requested_time.strftime("%B %d, %Y at %I:%M %p")
            return f"I will convey your request to Dr. {patient.doctor_name} to reschedule to {requested_time_formatted}."
        else:
            return "Could you please specify the date and time you'd like to reschedule your appointment to?"

    # Handle medication change requests
    if detect_medication_change(user_input):
        medication_info = extract_medication_info(user_input)
        # Here you can save the medication change request to the database
        return f"I will inform Dr. {patient.doctor_name} about your request regarding medication changes."

   
    entities = extract_entities(user_input)
    save_entities_to_knowledge_graph(entities, patient)

    
    from .models import Message
    messages = Message.objects.filter(patient=patient).order_by('-timestamp')[:10]
    conversation_history = get_conversation_history(messages)

    
    next_appointment_formatted = patient.next_appointment.strftime("%B %d, %Y at %I:%M %p")

    
    prompt = f"""
    You are an AI health assistant for {patient.first_name} {patient.last_name}. As an AI health assistant, provide a concise, helpful, and empathetic response focusing on the patient's message. 

    Patient's Medical Information:
    - Condition: {patient.medical_condition}
    - Medication: {patient.medication_regimen}
    - Next Appointment: {next_appointment_formatted}
    - Doctor: {patient.doctor_name}

    Conversation History:
    {conversation_history}

    The patient says: "{user_input}"

   
    """

    try:
        response = llm.invoke(prompt)
        return response.content.strip()
    except Exception as e:
        print(f"Error during LLM call: {e}")
        return "I'm sorry, I'm having trouble processing your request right now."
