# interview-assist

## Project Overview
Interview Assist is an AI-powered platform designed to help users prepare for job interviews by simulating realistic interview scenarios, providing customized questions, evaluating responses, and offering constructive feedback.

This project will be developed in phases:
1.  **Phase 1: Terminal-Based Modular System**: A functional command-line version with core logic.
2.  **Phase 2: Streamlit Frontend**: Integration with a web-based UI using Streamlit.
3.  **Phase 3: Microservices and Cloud Deployment**: Refactoring into a full microservices architecture and deploying to the cloud.

## Phase 1: Terminal-Based Modular System

This initial phase focuses on building the core logic of the Interview Assist application as a terminal-based program. The system will be split into independent Python modules, simulating a microservices-style architecture through function calls. Each module will be focused on a specific task and will leverage Generative AI where appropriate.

### Modules

The project will be organized within a `src` directory.

*   **`src/config_module.py`**:
    *   **Responsibility**: Handles user input for interview configuration (e.g., job role, job description, difficulty level).
    *   **Interaction**: Provides configuration data to other modules.

*   **`src/question_module.py`**:
    *   **Responsibility**: Generates interview questions based on the provided configuration.
    *   **GenAI Integration**: Uses a Large Language Model (LLM) to create relevant and dynamic questions.
    *   **Interaction**: Receives configuration from `config_module.py` (via `interview_flow.py`) and provides questions to the interview flow.

*   **`src/evaluation_module.py`**:
    *   **Responsibility**: Evaluates the user's responses to interview questions and generates constructive feedback.
    *   **GenAI Integration**: Uses an LLM to analyze responses for clarity, relevance, completeness, and to provide suggestions for improvement and sample answers.
    *   **Interaction**: Receives user responses (via `interview_flow.py`) and provides evaluation and feedback.

*   **`src/interview_flow.py`**:
    *   **Responsibility**: Orchestrates the overall interview process in the terminal. It manages the sequence of operations: getting configuration, generating questions, taking user responses, triggering evaluation, and displaying feedback.
    *   **Interaction**: Calls functions from `config_module.py`, `question_module.py`, and `evaluation_module.py`. Handles I/O with the user in the terminal.

*   **`src/main.py`**:
    *   **Responsibility**: The main entry point for the terminal-based application.
    *   **Interaction**: Initializes and starts the interview process by calling the `interview_flow.py` module.

### Data Flow
Data will be passed between these modules primarily through function arguments and return values. The `interview_flow.py` module will act as the central coordinator.

**Goal**: To have a working command-line pipeline that simulates an interview, demonstrating the core AI-driven question generation and response evaluation capabilities.