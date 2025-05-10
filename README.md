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

## Phase 2: Streamlit Frontend

The second phase enhances the user experience by integrating a web-based user interface using Streamlit. This provides a more interactive and visually appealing way for users to engage with the application.

### Web Interface Features

* **Welcome Page**: Introduction to the application and its features
* **Setup Page**: Input form for job role, description, and other configuration options
* **Interview Simulation**: Interactive Q&A with real-time feedback
* **Results Summary**: Overall performance review and detailed feedback

### Running the Streamlit App

1. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up your Mistral API key:
   ```
   export MISTRAL_API_KEY=your_api_key_here
   ```

3. Run the Streamlit application:
   ```
   streamlit run src/streamlit_app.py
   ```

4. Alternatively, use the main entry point:
   ```
   python src/main.py
   ```
   This will automatically detect and run the Streamlit app.