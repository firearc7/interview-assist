# Interview Assist

Interview Assist is an interactive, AI-powered platform designed to help users prepare for job interviews. It simulates realistic interview scenarios, provides customized questions, evaluates responses in real-time, and offers constructive feedback to help users improve their interviewing skills.

## About The Project

This tool aims to provide a comprehensive practice environment for job seekers.

**Key Features:**

*   **Customizable Interviews:** Configure interviews based on target job role, job description, difficulty level, and number of questions.
*   **Dynamic Question Generation:** Leverages Large Language Models (LLMs) to generate relevant interview questions.
*   **Real-time Response Evaluation:** User answers are evaluated by an LLM, providing instant feedback.
*   **Constructive Feedback:** Receive detailed feedback including scores, strengths, areas for improvement, and sample answers.
*   **Overall Performance Analysis:** Get a summary of your performance after completing an interview session.
*   **User Authentication & History:** Registered users can track their progress, view past interviews, and analyze their performance over time.

**Technology Stack:**

*   **Frontend:** Streamlit
*   **Backend Logic:** Python
*   **AI/LLM Integration:** Python modules interacting with LLM APIs (e.g., Mistral AI, OpenAI)
*   **Database:** SQLite for user accounts and interview history

## Getting Started

Follow these instructions to set up and run the project locally.

**Prerequisites:**

*   Python 3.8 or higher
*   Git (for cloning the repository)
*   Access to an LLM provider API and an API key.

**Installation & Setup:**

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd interview-assist
    ```

2.  **Create and activate a virtual environment (recommended):**
    ```bash
    # For Windows
    python -m venv venv
    .\venv\Scripts\activate

    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install dependencies:**
    Navigate to the project root directory (`interview-assist`) where `requirements.txt` is located.
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure LLM API Keys:**
    The application requires API keys for the configured Large Language Model provider (e.g., Mistral AI). This is typically managed by the `src/config_module.py`. You may need to:
    *   Create a `.env` file in the project root and add your API key (e.g., `MISTRAL_API_KEY=your_api_key_here`), if `config_module.py` is set up to read from it.
    *   Or, set environment variables directly in your system.
    *   Refer to `src/config_module.py` (or its documentation if available) for specific instructions on API key setup.

5.  **Initialize the database (if required):**
    The database schema is typically created automatically on the first run or via a setup script if provided. Check `src/database.py` for details.

**Running the Application:**

1.  Ensure your virtual environment is activated and API keys are configured.
2.  Navigate to the project root directory (`interview-assist`).
3.  Run the Streamlit application:
    ```bash
    streamlit run src/streamlit_app.py
    ```
4.  Open your web browser and go to the local URL provided by Streamlit (usually `http://localhost:8501`).

## Running Tests

The project uses Python's built-in `unittest` framework for testing. Tests are located in the `tests/` directory.

**To run the tests:**

1.  Ensure you have installed all dependencies, including any testing-specific ones (usually covered by `requirements.txt`).
2.  Navigate to the project root directory (`interview-assist`).
3.  Run the following command in your terminal:
    ```bash
    python -m unittest discover -s tests -v
    ```
    Or, for a more general discovery if your `tests` directory is structured as a package:
    ```bash
    python -m unittest discover -v
    ```
    This command will discover and execute all tests within the `tests` directory and provide verbose output.

Tests cover core modules such as database interactions, question generation logic, and response evaluation, often using mocks for external dependencies like LLM APIs.
