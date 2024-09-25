# Health Chat Application with RAG and LangGraph

A web-based health chat application that allows patients to interact with an AI-powered chatbot for health-related conversations. The chatbot can handle general inquiries, appointment scheduling, medication changes, and more, providing a personalized and context-aware experience.

## Table of Contents

- [Features](#features)
- [Bonus Features](#bonus-features)
- [Prerequisites](#prerequisites)
- [Setup Instructions](#setup-instructions)
- [Running the Application](#running-the-application)
- [Assumptions Made](#assumptions-made)
- [Using Key Features](#using-key-features)
- [Project Structure](#project-structure)
- [Acknowledgments](#acknowledgments)

---

## Features

- **Health-Related Conversations**: The chatbot responds to general health and lifestyle inquiries, focusing on the patient's medical condition and treatment.
- **Appointment Handling**: Detects and processes appointment change requests, allowing patients to reschedule appointments.
- **Medication Change Requests**: Handles requests related to medication changes or dosage adjustments.
- **Content Filtering**: Uses OpenAI's Moderation API to filter out disallowed or sensitive topics.
- **Conversation History Management**: Maintains conversation history with memory optimization to ensure efficient handling of dialogues.
- **Entity Extraction**: Extracts key entities from the conversation (e.g., medications, dates) using spaCy.
- **Knowledge Graph Integration**: Stores extracted entities in a Neo4j knowledge graph for dynamic querying and enriched interactions.
- **Conversation Summarization**: Generates summaries of the conversation, highlighting important medical information or concerns.
- **LLM-Agnostic Design**: Allows easy swapping of language models by changing environment variables.

---

## Bonus Features

- **Knowledge Graph and LLM Integration**: Incorporates a Neo4j knowledge graph to dynamically query additional patient data.
- **Multi-Agent System**: Uses LangChain to coordinate multiple models handling different tasks within the chat.
- **Conversation Summaries and Medical Insights**: Detects and outputs live conversation summaries and medical insights from ongoing conversations.
- **LLM-Agnostic Design with LangChain and LangGraph**: Ensures the application is LLM-agnostic for flexibility in language model selection.

---

## Prerequisites

- **Python 3.8 or higher**
- **Django 3.2 or higher**
- **Neo4j Community Edition (optional for knowledge graph)**
- **Virtual Environment Tool (optional but recommended)**
- **OpenAI API Key**
- **Neo4j Python Driver**
- **Required Python Packages**: See [Setup Instructions](#setup-instructions)

---

## Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/health_chat_app.git
cd health_chat_app
```

### 2. Create a Virtual Environment (Optional but Recommended)

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

# Neo4j Configuration (if using knowledge graph)
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

Follow the prompts to create a superuser account.

### 7. Add Initial Data

#### a. Add a Patient Record

You can add a patient using the Django admin interface or via the Django shell.

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
      medical_condition='Hypertension',
      medication_regimen='Lisinopril 10mg once daily',
      last_appointment='2023-09-01 10:00',
      next_appointment='2023-12-01 10:00',
      doctor_name='Dr. Smith'
  )
  exit()
  ```

#### b. Ensure Neo4j is Running (If Using Knowledge Graph)

- Download and install Neo4j Community Edition from the [official website](https://neo4j.com/download-center/).
- Start the Neo4j server and ensure it is running at `bolt://localhost:7687`.

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

## Assumptions Made

- **Single Patient Context**: The application currently assumes there is only one patient in the database. Multi-patient support with authentication is not implemented.
- **Environment Variables**: It is assumed that all necessary environment variables are correctly set in the `.env` file.
- **Neo4j Installation**: If you choose to use the knowledge graph features, it is assumed that Neo4j is installed and running locally.
- **Language Model**: The application uses OpenAI's GPT-3.5-turbo model by default, but can be configured to use other models.

---

## Using Key Features

### **1. Health-Related Conversations**

- **How to Use**: In the chat interface, type any general health question or inquiry related to your medical condition, medication, or lifestyle.
- **Example**: "What should I do if I forget to take my medication?"

### **2. Appointment Handling**

- **How to Use**: Request to reschedule or book an appointment by mentioning desired dates and times.
- **Example**: "Can I reschedule my appointment to next Friday at 3 PM?"
- **What Happens**: The bot will acknowledge your request and save it for review. The request will be displayed in the interface for your confirmation.

### **3. Medication Change Requests**

- **How to Use**: Mention any changes you want to make to your medication regimen.
- **Example**: "I think I need to increase my dosage."
- **What Happens**: The bot will inform you that your request will be conveyed to your doctor.

### **4. Content Filtering**

- **How to Use**: The bot automatically filters out disallowed topics. If you attempt to discuss such topics, the bot will politely inform you that it can only assist with health-related questions.

### **5. Conversation History Management**

- **How to Use**: Simply continue the conversation naturally. The bot maintains context over recent messages to provide coherent responses.

### **6. Entity Extraction and Knowledge Graph**

- **How to Use**: When you mention specific medications, symptoms, or other entities, the bot extracts and stores this information.
- **What Happens**: Extracted entities are saved in the Neo4j knowledge graph for enhanced interaction in future conversations.

### **7. Conversation Summarization**

- **How to Use**: At any point, the conversation summary is displayed in the interface.
- **What Happens**: The bot generates a summary highlighting important points from the conversation.

### **8. LLM-Agnostic Design**

- **How to Use**: If you wish to change the language model, update the `LLM_PROVIDER` and `LLM_MODEL` in the `.env` file.
- **Example**: Switching to a different model for testing or performance considerations.

---

## Project Structure

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

---

## Acknowledgments

- **Django**: For providing the web framework.
- **OpenAI**: For the language models and moderation API.
- **LangChain**: For simplifying LLM integration.
- **spaCy**: For natural language processing and entity extraction.
- **Neo4j**: For the graph database used in the knowledge graph integration.

---

**Note**: This application is a prototype developed for demonstration purposes and should not be used in a production environment without proper security audits and enhancements.

---

If you have any questions or encounter issues while setting up or running the application, please feel free to reach out.
