# System Design Document

## Table of Contents
- [1. Introduction](#1-introduction)
  - [1.1 Purpose](#11-purpose)
  - [1.2 Scope](#12-scope)
  - [1.3 System Overview](#13-system-overview)
  - [1.4 Design Considerations](#14-design-considerations)
- [2. Architecture Design](#2-architecture-design)
  - [2.1 High-Level Architecture](#21-high-level-architecture)
  - [2.2 Component Diagram](#22-component-diagram)
  - [2.3 Deployment Diagram](#23-deployment-diagram)
  - [2.4 Data Flow Diagram](#24-data-flow-diagram)
  - [2.5 Class Diagram](#25-class-diagram)
  - [2.6 Sequence Diagram](#26-sequence-diagram)
- [3. Module Design](#3-module-design)
  - [3.1 User Management](#31-user-management)
  - [3.2 Interview Configuration](#32-interview-configuration)
  - [3.3 Question Generation](#33-question-generation)
  - [3.4 Response Evaluation](#34-response-evaluation)
  - [3.5 Session Management](#35-session-management)
  - [3.6 Frontend](#36-frontend)
- [4. Database Design](#4-database-design)
  - [4.1 Data Models](#41-data-models)
  - [4.2 Data Storage Considerations](#42-data-storage-considerations)
- [5. LLM Integration](#5-llm-integration)
- [6. Security Design](#6-security-design)
- [7. User Interface Design](#7-user-interface-design)
- [8. Testing Strategy](#8-testing-strategy)
- [9. Deployment Strategy](#9-deployment-strategy)
- [10. Future Enhancements](#10-future-enhancements)
- [11. Appendix](#11-appendix)
  - [11.1 Technology Stack](#111-technology-stack)
  - [11.2 Development Timeline](#112-development-timeline)
  - [11.3 Resource Requirements](#113-resource-requirements)

## 1. Introduction

### 1.1 Purpose
This design document outlines the technical architecture and implementation details for the AI Interview Simulator, a Streamlit-based web application that helps users prepare for job interviews through AI-powered simulation, evaluation, and feedback.

### 1.2 Scope
The document covers all aspects of the current system design, including:
- Streamlit monolithic architecture
- SQLite database design
- LLM integration for question generation and evaluation
- User interface design
- Security considerations

### 1.3 System Overview
The AI Interview Simulator is a platform that allows users to practice job interviews in a realistic environment. The system generates customized interview questions based on job descriptions and user preferences, evaluates user responses in real-time, provides constructive feedback, and tracks progress over time. All logic is implemented in a single Streamlit app, with persistent data stored in SQLite.

### 1.4 Design Considerations
- **Current State**: Streamlit-based monolithic application with modular Python components.
- **Cloud-Native**: Can be deployed on Streamlit Cloud or similar platforms.
- **LLM Integration**: Leveraging LLMs for question generation and response evaluation.
- **Security and Privacy**: Protecting user data and ensuring privacy.
- **Accessibility**: Basic Streamlit accessibility features.
- **Scalability**: Limited by Streamlit and SQLite.
- **Modularity**: Python modules for database, question, and evaluation logic.

## 2. Architecture Design

**Note:** The current implementation is a monolithic Streamlit application (`streamlit_app.py`) that orchestrates calls to Python modules (`database.py`, `question_module.py`, `evaluation_module.py`). User session data is managed using Streamlit's session state and persisted via `database.py`.

### 2.1 High-Level Architecture
The AI Interview Simulator is a Streamlit web application. The frontend and backend logic are combined in a single process. The app interacts with LLM APIs for question generation and evaluation, and stores persistent data in a local SQLite database.

```
┌───────────────────────────────────────────────┐
│                User Browser                   │
│         (Streamlit Web Interface)             │
└───────────────┬───────────────────────────────┘
                │
                ▼
┌───────────────────────────────────────────────┐
│           Streamlit Application               │
│  ┌─────────────────────────────────────────┐  │
│  │           streamlit_app.py              │  │
│  │ ┌───────────────┐  ┌─────────────────┐  │  │
│  │ │ question_     │  │ evaluation_     │  │  │
│  │ │ module.py     │  │ module.py       │  │  │
│  │ └───────────────┘  └─────────────────┘  │  │
│  │ ┌───────────────┐                       │  │
│  │ │ database.py   │                       │  │
│  │ └───────────────┘                       │  │
│  └─────────────────────────────────────────┘  │
└─────────────────────────┬─────────────────────┘
                          │
                          ▼
                ┌────────────────────┐
                │   SQLite Database  │
                └────────────────────┘
```

### 2.2 Component Diagram

```
┌───────────────────────────────────────────────┐
│           Streamlit Application               │
├───────────────────────────────────────────────┤
│  ┌─────────────────────────────────────────┐  │
│  │ streamlit_app.py                        │  │
│  │  - UI rendering                         │  │
│  │  - User/session state                   │  │
│  │  - Orchestration                        │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │ database.py                             │  │
│  │  - User CRUD                            │  │
│  │  - Interview CRUD                       │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │ question_module.py                      │  │
│  │  - LLM question generation              │  │
│  └─────────────────────────────────────────┘  │
│  ┌─────────────────────────────────────────┐  │
│  │ evaluation_module.py                    │  │
│  │  - LLM response evaluation              │  │
│  └─────────────────────────────────────────┘  │
└───────────────────────────────────────────────┘
```

### 2.3 Deployment Diagram
```
┌───────────────────────────────────┐
│      Streamlit Cloud / Server     │
│                                   │
│  ┌───────────────────────────┐    │
│  │      Streamlit App        │    │
│  │  (streamlit_app.py +      │    │
│  │   Python modules)         │    │
│  └─────────────┬─────────────┘    │
│                │                  │
│  ┌─────────────▼─────────────┐    │
│  │      SQLite Database      │    │
│  │      (local file)         │    │
│  └───────────────────────────┘    │
│                                   │
└───────────────────────────────────┘
```

### 2.4 Data Flow Diagram
```
User
 │
 ▼
Streamlit UI (streamlit_app.py)
 │
 ├──> question_module.py (LLM API for questions)
 │
 ├──> evaluation_module.py (LLM API for feedback)
 │
 └──> database.py (SQLite for persistence)
```

### 2.5 Class Diagram

```
+-------------------+
|   User            |
+-------------------+
| - id: int         |
| - username: str   |
| - email: str      |
| - password_hash: str |
| - created_at: dt  |
+-------------------+

+-------------------+
|   Interview       |
+-------------------+
| - id: int         |
| - user_id: int    |
| - job_role: str   |
| - job_description: str |
| - difficulty: str |
| - questions: list[str] |
| - responses: list[str] |
| - feedback: list[Feedback] |
| - overall_feedback: dict |
| - overall_score: float   |
| - created_at: dt         |
+-------------------+

+-------------------+
|   Feedback        |
+-------------------+
| - score: float/str|
| - strengths: str  |
| - areas_for_improvement: str |
| - sample_answer: str         |
+-------------------+
```

### 2.6 Sequence Diagram

**Interview Session Sequence:**

```
User         Streamlit App      question_module   evaluation_module   database
 |                |                   |                 |                |
 |---login------->|                   |                 |                |
 |                |---validate------->|                 |                |
 |                |<--result----------|                 |                |
 |---setup------->|                   |                 |                |
 |                |---generate------->|                 |                |
 |                |   questions       |                 |                |
 |                |<--questions-------|                 |                |
 |---answer------>|                   |                 |                |
 |                |---evaluate------->|                 |                |
 |                |   response        |                 |                |
 |                |<--feedback--------|                 |                |
 |                |---save----------->|                 |                |
 |                |   interview       |                 |                |
 |                |                   |                 |                |
```

## 3. Module Design

### 3.1 User Management
- User registration and login (username/password)
- No admin roles or OAuth
- User session managed by Streamlit session state

### 3.2 Interview Configuration
- Job role, job description, difficulty, number of questions
- No advanced configuration (e.g., interview type, interviewer personality)

### 3.3 Question Generation
- LLM integration for dynamic question generation
- No question bank or follow-up logic

### 3.4 Response Evaluation
- LLM integration for response evaluation and feedback
- Scoring and feedback per question

### 3.5 Session Management
- Session state managed by Streamlit
- Interview history stored in SQLite

### 3.6 Frontend
- Streamlit UI for all user flows

## 4. Database Design

### 4.1 Data Models

**users** table:
```json
{
  "id": "integer (PRIMARY KEY)",
  "username": "string (UNIQUE)",
  "email": "string (UNIQUE)",
  "password_hash": "string",
  "created_at": "datetime"
}
```

**interviews** table:
```json
{
  "id": "integer (PRIMARY KEY)",
  "user_id": "integer (FOREIGN KEY to users.id)",
  "job_role": "string",
  "job_description": "text",
  "difficulty": "string",
  "questions": "TEXT (JSON array of question strings)",
  "responses": "TEXT (JSON array of response strings or null)",
  "feedback": "TEXT (JSON array of feedback objects)",
  "overall_feedback": "TEXT (JSON object)",
  "overall_score": "REAL",
  "created_at": "datetime"
}
```

**Feedback object (in feedback array):**
```json
{
  "score": "float | string ('N/A')",
  "strengths": "string",
  "areas_for_improvement": "string",
  "sample_answer": "string"
}
```

### 4.2 Data Storage Considerations
- User data and interview history are stored in a local SQLite database.
- Passwords are hashed.

## 5. LLM Integration

- LLM APIs are used for question generation and response evaluation.
- Prompt engineering is handled in the respective modules.
- LLM responses are parsed and stored as structured JSON.

## 6. Security Design

- User authentication via username/password.
- Passwords are hashed in the database.
- No advanced role-based access or OAuth.
- HTTPS recommended for deployment.

## 7. User Interface Design

- Streamlit UI with the following pages:
  - Welcome (intro, login/signup, start/view history)
  - Login/Signup forms
  - Dashboard (interview history)
  - Interview setup (job role, description, difficulty, number of questions)
  - Interview simulation (question, response, feedback)
  - Results (summary, per-question feedback)
- Basic accessibility via Streamlit

## 8. Testing Strategy

- Unit and integration tests for Python modules (if implemented)
- Manual UI testing

## 9. Deployment Strategy

- Deployable on Streamlit Cloud or similar platforms
- SQLite database included with app

## 10. Future Enhancements

- Voice and video interaction
- Advanced configuration and analytics
- Microservices refactor

## 11. Appendix

### 11.1 Technology Stack

- Python 3.x
- Streamlit
- SQLite
- LLM provider APIs (e.g., OpenAI, Mistral)

### 11.2 Development Timeline

- Phase 1: Terminal-based prototype (complete)
- Phase 2: Streamlit frontend (current)
- Phase 3: Microservices/cloud deployment (future)

### 11.3 Resource Requirements

- 2 developers with Python and GenAI experience
- LLM API credits
- Streamlit Cloud or similar hosting
