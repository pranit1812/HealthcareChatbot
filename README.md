# Health Chat Application 

A web-based health chat application that allows patients to interact with an AI-powered chatbot for health-related conversations. The chatbot can handle general inquiries, appointment scheduling, medication changes, and more, providing a personalized and context-aware experience.

---



## Screenshots

### Screenshot 1
![Screenshot 2024-09-28 171638]

### Screenshot 2
![Screenshot 2024-09-28 171714]

### Screenshot 3
![Screenshot 2024-09-28 171915]


## Table of Contents

- [Features](#features)
- [Technologies Used](#technologies-used)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Usage Instructions](#usage-instructions)
- [Code Structure](#code-structure)
- [Implementation Details](#implementation-details)
  - [LangChain Integration](#langchain-integration)
  - [Knowledge Graph with Neo4j](#knowledge-graph-with-neo4j)
- [Memory Optimization](#memory-optimization)
- [Bonus Features Implemented](#bonus-features-implemented)
- [Assumptions Made](#assumptions-made)
- [Conclusion](#conclusion)
- [Acknowledgments](#acknowledgments)

---

## Features

### 1. Health-Related Conversations

- **Description**: The chatbot responds to general health and lifestyle inquiries, focusing on the patient's medical condition and treatment.
- **How it Works**: Users can type in any health-related questions, and the chatbot provides informative responses while encouraging consultation with their doctor for medical advice.

### 2. Appointment Handling

- **Description**: Detects and processes appointment change requests, allowing patients to reschedule appointments.
- **How it Works**:
  - The bot listens for keywords like "reschedule", "appointment", "schedule", "cancel", or "book".
  - When detected, it attempts to parse the requested date and time.
  - Saves the appointment change request for the doctor's review.
  - Acknowledges the patient's request in the conversation.

### 3. Medication Change Requests

- **Description**: Handles requests related to medication changes or dosage adjustments.
- **How it Works**:
  - Detects phrases indicating a desire to change medication or dosage.
  - Extracts relevant medication information using spaCy.
  - Informs the patient that their request will be conveyed to their doctor.

### 4. Content Filtering

- **Description**: Uses OpenAI's Moderation API to filter out disallowed or sensitive topics.
- **How it Works**:
  - Before processing user input, it checks the content against OpenAI's moderation policies.
  - If disallowed content is detected, the bot politely informs the user that it can only assist with health-related questions.

### 5. Conversation History Management

- **Description**: Maintains conversation history with memory optimization to ensure efficient handling of dialogues.
- **How it Works**:
  - Stores the last 10 messages or up to a maximum token count to provide context.
  - The conversation history is used to generate coherent and context-aware responses.

### 6. Entity Extraction

- **Description**: Extracts key entities (e.g., medications, dates) from the conversation using spaCy.
- **How it Works**:
  - Processes user input with spaCy's NLP model to identify and extract entities.
  - Entities are saved and used to enhance the conversation and provide personalized responses.

### 7. Knowledge Graph Integration

- **Description**: Stores extracted entities in a Neo4j knowledge graph for dynamic querying and enriched interactions.
- **How it Works**:
  - Connects to a Neo4j database using the Neo4j Python driver.
  - Stores patient information and extracted entities as nodes and relationships.
  - Allows for efficient retrieval and utilization of patient-specific data during conversations.

### 8. Conversation Summarization

- **Description**: Generates summaries of the conversation, highlighting important medical information or concerns.
- **How it Works**:
  - Uses the language model to summarize the conversation history.
  - Summaries are displayed in the chat interface for the patient's review.

### 9. LLM-Agnostic Design

- **Description**: Allows easy swapping of language models by changing environment variables.
- **How it Works**:
  - Utilizes LangChain to abstract interactions with the language model.
  - Configuration settings determine which LLM provider and model to use.
  - Supports different models and providers without significant code changes.

---

## Technologies Used

- **Python 3.8+**
- **Django 3.2+**
- **OpenAI API**
- **LangChain**
- **spaCy**
- **Neo4j Community Edition**
- **Neo4j Python Driver**
- **Python-dateutil**
- **HTML/CSS for Frontend**

---

## Setup Instructions

### Prerequisites

- **Python 3.8 or higher**
- **Neo4j Community Edition**
- **OpenAI API Key**

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/health_chat_app.git
cd health_chat_app
```

### 2. Create a Virtual Environment

```bash
python -m venv venv
```

Activate the virtual environment:

- **On Windows:**

  ```bash
  venv\Scripts\activate
  ```

- **On Unix or Linux:**

  ```bash
  source venv/bin/activate
  ```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

If you don't have a `requirements.txt` file, install the packages manually:

```bash
pip install django openai langchain-openai spacy python-dateutil neo4j python-dotenv
```

Download the spaCy English model:

```bash
python -m spacy download en_core_web_sm
```

### 4. Set Up Environment Variables

Create a `.env` file in the root directory of the project (same directory as `manage.py`):

```bash
touch .env
```

Add the following environment variables to the `.env` file:

```env
# OpenAI API Key
OPENAI_API_KEY=your-openai-api-key

# LLM Configuration
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

# Neo4j Configuration
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-neo4j-password
```

**Note**: Replace `your-openai-api-key` and `your-neo4j-password` with your actual API key and Neo4j password.

### 5. Set Up the Database

Apply migrations to set up the SQLite database:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser (Optional)

To access the Django admin interface:

```bash
python manage.py createsuperuser
```

### 7. Add Initial Data

#### a. Add a Patient Record

- **Using the Admin Interface**:

  Start the development server:

  ```bash
  python manage.py runserver
  ```

  Navigate to `http://127.0.0.1:8000/admin/`, log in with your superuser credentials, and add a new patient.

- **Using the Django Shell**:

  ```bash
  python manage.py shell
  ```

  In the shell:

  ```python
  from chat.models import Patient
  patient = Patient.objects.create(
      first_name='John',
      last_name='Doe',
      date_of_birth='1990-01-01',
      phone_number='1234567890',
      email='john.doe@example.com',
      medical_condition='Asthma',
      medication_regimen='Salbutamol inhaler (100 mcg) - 1-2 puffs every minute during attack, max 10 puffs',
      last_appointment='2023-09-01 10:00',
      next_appointment='2023-12-01 10:00',
      doctor_name='Dr. Smith'
  )
  exit()
  ```

#### b. Ensure Neo4j is Running

- **Download and Install Neo4j**:

  Download Neo4j Desktop from the [official website](https://neo4j.com/download/).

- **Start Neo4j**:

  - Create a new project and database in Neo4j Desktop.
  - Set the password and remember it for the `.env` file.
  - Start the database.

---

## Running the Application

### 1. Start the Development Server

```bash
python manage.py runserver
```

### 2. Access the Application

Open your web browser and navigate to:

```
http://127.0.0.1:8000/
```

---

## Usage Instructions

### **1. Health-Related Conversations**

- **How to Use**: In the chat interface, type any general health question or inquiry related to your medical condition, medication, or lifestyle.
- **Example**: "What should I do if I forget to take my medication?"

### **2. Appointment Handling**

- **How to Use**: Request to reschedule or book an appointment by mentioning desired dates and times.
- **Example**: "Can I reschedule my appointment to next Friday at 3 PM?"
- **What Happens**:
  - The bot acknowledges your request and saves it for review.
  - The request is displayed in the interface for your confirmation.

### **3. Medication Change Requests**

- **How to Use**: Mention any changes you want to make to your medication regimen.
- **Example**: "I think I need to increase my dosage."
- **What Happens**:
  - The bot informs you that your request will be conveyed to your doctor.

### **4. Content Filtering**

- **How to Use**: The bot automatically filters out disallowed topics. If you attempt to discuss such topics, the bot will politely inform you that it can only assist with health-related questions.

### **5. Conversation History Management**

- **How to Use**: Simply continue the conversation naturally. The bot maintains context over recent messages to provide coherent responses.

### **6. Entity Extraction and Knowledge Graph**

- **How to Use**: When you mention specific medications, symptoms, or other entities, the bot extracts and stores this information.
- **What Happens**:
  - Extracted entities are saved in the Neo4j knowledge graph for enhanced interaction in future conversations.

### **7. Conversation Summarization**

- **How to Use**: At any point, the conversation summary is displayed in the interface.
- **What Happens**:
  - The bot generates a summary highlighting important points from the conversation.

### **8. LLM-Agnostic Design**

- **How to Use**: If you wish to change the language model, update the `LLM_PROVIDER` and `LLM_MODEL` in the `.env` file.
- **Example**: Switching to a different model for testing or performance considerations.

---

## Code Structure

```
health_chat_app/
├── chat/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── urls.py
│   ├── views.py
│   ├── utils.py
│   └── templates/
│       └── chat/
│           └── chat.html
├── health_chat_app/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── static/
│   └── favicon.ico
├── .env
├── db.sqlite3
├── manage.py
├── requirements.txt
└── README.md
```

- **chat/**: Contains the main application code.
  - **models.py**: Defines the data models (Patient, Message, AppointmentChangeRequest).
  - **views.py**: Contains the view logic for handling requests and rendering responses.
  - **utils.py**: Contains utility functions for processing user input, generating responses, and interacting with the knowledge graph.
  - **templates/chat/chat.html**: The main HTML template for the chat interface.

---

## Implementation Details

### LangChain Integration

- **Purpose**: LangChain is used to abstract interactions with the language model, allowing for flexibility and easier management.
- **How it's Used**:
  - **LLM Initialization**: The `initialize_llm` function in `utils.py` uses LangChain to initialize the language model based on environment variables.
  - **Prompt Engineering**: Prompts are constructed to include patient information and conversation history, and passed to the language model via LangChain.
  - **LLM Invocation**: The `llm.invoke(prompt)` method is used to get responses from the language model.

### Knowledge Graph with Neo4j

- **Purpose**: Neo4j is used to create a knowledge graph that stores patient information and extracted entities for enriched interactions.
- **How it's Used**:
  - **Entity Extraction**: The `extract_entities` function uses spaCy to identify entities in the user's input.
  - **Data Storage**: The `save_entities_to_knowledge_graph` function stores entities and their relationships with the patient in the Neo4j database.
  - **Querying**: While not extensively used in the current implementation, the knowledge graph allows for dynamic querying of patient-specific data, which can be used to enhance responses.

---

## Memory Optimization

- **Conversation History Management**:
  - The `get_conversation_history` function retrieves recent messages up to a maximum token count to maintain context without overloading the language model.
  - This ensures that the bot can handle long conversations efficiently by only including relevant recent messages in the prompt.

---

## Bonus Features Implemented

- **Knowledge Graph and LLM Integration**:
  - Implemented using Neo4j to store and manage patient-related entities extracted from conversations.
- **Conversation Summarization**:
  - The bot generates summaries of the conversation, highlighting important medical information or concerns.
- **LLM-Agnostic Design with LangChain**:
  - The application is designed to be LLM-agnostic, allowing easy swapping of language models through environment variables.

---

## Assumptions Made

- **Single Patient Context**: The application assumes there is only one patient in the database. Multi-patient support with authentication is not implemented.
- **Environment Variables**: It is assumed that all necessary environment variables are correctly set in the `.env` file.
- **Neo4j Installation**: It is assumed that Neo4j is installed and running locally.
- **Language Model**: The application uses OpenAI's GPT-3.5-turbo model by default but can be configured to use other models.

---



## Conclusion

The Health Chat Application integrates advanced technologies to provide a responsive and intelligent chatbot for patients. By leveraging Django for the web framework, Neo4j for the knowledge graph, and LangChain for language model interactions, the app offers:

- Personalized and context-aware conversations.
- Efficient handling of appointment and medication requests.
- Enhanced data management through entity extraction and knowledge graphs.
- Flexibility in language model selection and configuration.

The application's architecture promotes scalability and extensibility, allowing for future enhancements such as:

- Adding authentication for multiple patients.
- Integrating additional data sources into the knowledge graph.
- Implementing more sophisticated natural language understanding.

---

## Acknowledgments

- **Django**: For providing the web framework.
- **OpenAI**: For the language models and moderation API.
- **LangChain**: For simplifying LLM integration.
- **spaCy**: For natural language processing and entity extraction.
- **Neo4j**: For the graph database used in the knowledge graph integration.

---



---
## Contact
 Author - Pranit Sehgal
 Email - pranitsehgal@gmail.com
