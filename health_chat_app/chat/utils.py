import os
import re
import openai
import spacy
from dateutil import parser
from django.conf import settings
from .models import AppointmentChangeRequest, Message, Patient  # Ensure Patient is imported
from neo4j import GraphDatabase
from datetime import datetime
import dateparser
# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Initialize Spacy NLP model
nlp = spacy.load('en_core_web_sm')

# Neo4j Configuration
neo4j_uri = os.getenv('NEO4J_URI')
neo4j_user = os.getenv('NEO4J_USER')
neo4j_password = os.getenv('NEO4J_PASSWORD')
driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

# LangChain Imports
from langchain.agents import initialize_agent
from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain.tools import Tool

# Initialize LLM using LangChain
def initialize_llm():
    llm_provider = os.getenv('LLM_PROVIDER', 'openai')
    llm_model = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    api_key = os.getenv('OPENAI_API_KEY')

    if llm_provider == 'openai':
        return ChatOpenAI(model=llm_model, openai_api_key=api_key)
    else:
        raise ValueError("Unsupported LLM provider.")

llm = initialize_llm()

# Initialize Conversation Memory
memory = ConversationBufferMemory()

# Define Tools

# Content Moderation Tool
def moderation_tool(user_input):
    try:
        response = openai.Moderation.create(
            input=user_input,
            api_key=os.getenv('OPENAI_API_KEY')
        )
        flagged = response["results"][0]["flagged"]
        return not flagged  # Return True if allowed, False if not
    except Exception as e:
        print(f"Error during content moderation: {e}")
        return False

moderation = Tool(
    name="Moderation",
    func=moderation_tool,
    description="Checks if the user input violates content moderation rules."
)

# Appointment Detection Tool
def detect_appointment_change(user_input):
    keywords = ['reschedule', 'appointment', 'schedule', 'cancel', 'book']
    return any(word in user_input.lower() for word in keywords)

appointment_tool = Tool(
    name="DetectAppointmentChange",
    func=detect_appointment_change,
    description="Detects if the user wants to change or reschedule an appointment."
)

# Medication Detection Tool
def detect_medication_change(user_input):
    keywords = [
        'medication change', 'change medication', 'new medication',
        'stop medication', 'dosage', 'increase dosage', 'decrease dosage'
    ]
    return any(word in user_input.lower() for word in keywords)

medication_tool = Tool(
    name="DetectMedicationChange",
    func=detect_medication_change,
    description="Detects if the user wants to change or adjust medication."
)

# Parse Requested Time Tool
def parse_requested_time(user_input):
    try:
        requested_time = dateparser.parse(user_input, settings={'PREFER_DATES_FROM': 'future'})
        return requested_time
    except Exception as e:
        print(f"Error during date parsing: {e}")
        return None

# Knowledge Graph Function (No longer wrapped as a tool)
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

# Summarization Tool
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
        response = llm.predict(prompt)
        return response.strip()
    except Exception as e:
        print(f"Error during summarization: {e}")
        return ""


# Entity Extraction Tool
def extract_entities(user_input):
    doc = nlp(user_input)
    entities = {}
    for ent in doc.ents:
        entities[ent.label_] = ent.text
    return entities

entity_extraction_tool = Tool(
    name="EntityExtraction",
    func=extract_entities,
    description="Extracts entities such as drugs or conditions from the user's input."
)

# Conversation History Tool
def get_conversation_history(patient, max_messages=10):
    messages = Message.objects.filter(patient=patient).order_by('-timestamp')[:max_messages]
    conversation = '\n'.join([msg.text for msg in reversed(messages)])
    memory.save_context({"input": conversation}, {"output": ""})
    return conversation

conversation_history_tool = Tool(
    name="ConversationHistory",
    func=get_conversation_history,
    description="Retrieves the conversation history for a given patient."
)

# Prompt Template
template = """
You are an AI health assistant for {first_name} {last_name}. As an AI health assistant, provide a concise, helpful, and empathetic response focusing on the patient's message.

Patient's Medical Information:
- Condition: {medical_condition}
- Medication: {medication_regimen}
- Next Appointment: {next_appointment}
- Doctor: {doctor_name}

Conversation History:
{conversation_history}

The patient says: "{user_input}"

Response:
"""

prompt_template = PromptTemplate(
    template=template,
    input_variables=[
        "first_name", "last_name", "medical_condition", "medication_regimen",
        "next_appointment", "doctor_name", "conversation_history", "user_input"
    ]
)

# Initialize Agent with Tools (knowledge_graph_tool removed)
tools = [
    moderation,
    appointment_tool,
    medication_tool,
    
    entity_extraction_tool,
    conversation_history_tool
]

agent = initialize_agent(
    tools=tools,
    llm=llm,
    agent="zero-shot-react-description",
    memory=memory
)

# Main Function to Get Bot Response
def get_bot_response(request, user_input, patient):
    # Access session
    session = request.session

    # Content Moderation
    if not moderation_tool(user_input):
        return "I'm sorry, but I can only assist with health-related questions."

    # Check if user is in the middle of rescheduling
    if session.get('pending_reschedule'):
        requested_time = parse_requested_time(user_input)
        print(f"Requested Time Parsed: {requested_time}")
        if requested_time:
            AppointmentChangeRequest.objects.create(patient=patient, requested_time=requested_time)
            requested_time_formatted = requested_time.strftime("%B %d, %Y at %I:%M %p")
            # Clear the pending state
            session['pending_reschedule'] = False
            return f"I will convey your request to Dr. {patient.doctor_name} to reschedule to {requested_time_formatted}."
        else:
            return "Could you please specify the date and time you'd like to reschedule your appointment to?"

    # Detect Appointment Change
    if detect_appointment_change(user_input):
        requested_time = parse_requested_time(user_input)
        print(f"Requested Time Parsed: {requested_time}")
        if requested_time:
            AppointmentChangeRequest.objects.create(patient=patient, requested_time=requested_time)
            requested_time_formatted = requested_time.strftime("%B %d, %Y at %I:%M %p")
            return f"I will convey your request to Dr. {patient.doctor_name} to reschedule to {requested_time_formatted}."
        else:
            # Set pending reschedule state
            session['pending_reschedule'] = True
            return "Could you please specify the date and time you'd like to reschedule your appointment to?"

    # Detect Medication Change
    if detect_medication_change(user_input):
        # Extract Medication Information
        medication_info = extract_entities(user_input)
        # Save to Knowledge Graph
        save_entities_to_knowledge_graph(medication_info, patient)
        return f"I will inform Dr. {patient.doctor_name} about your request regarding medication changes."

    # Extract Entities and Save to Knowledge Graph
    entities = extract_entities(user_input)
    save_entities_to_knowledge_graph(entities, patient)

    # Get Conversation History
    conversation_history = get_conversation_history(patient)

    # Format Next Appointment Date
    next_appointment_formatted = patient.next_appointment.strftime("%B %d, %Y at %I:%M %p")

    # Generate Prompt
    prompt = prompt_template.format(
        first_name=patient.first_name,
        last_name=patient.last_name,
        medical_condition=patient.medical_condition,
        medication_regimen=patient.medication_regimen,
        next_appointment=next_appointment_formatted,
        doctor_name=patient.doctor_name,
        conversation_history=conversation_history,
        user_input=user_input
    )

    # Get LLM Response
    try:
        response = llm.predict(prompt)
        return response.strip()
    except Exception as e:
        print(f"Error during LLM call: {e}")
        return "I'm sorry, I'm having trouble processing your request right now."
