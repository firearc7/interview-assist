"""
Main entry point for the AI Interview Simulator terminal application.
"""
import subprocess
import os

def main():
    """
    Runs the main application.
    For Phase 1, it runs the terminal-based interview.
    For Phase 2 onwards, it can launch the Streamlit app.
    """
    # Check if streamlit_app.py exists to decide which interface to launch
    streamlit_app_path = os.path.join(os.path.dirname(__file__), "streamlit_app.py")

    if os.path.exists(streamlit_app_path):
        print("Launching Streamlit application...")
        try:
            subprocess.run(["streamlit", "run", streamlit_app_path], check=True)
        except FileNotFoundError:
            print("Error: Streamlit is not installed or not in PATH.")
            print("Please install Streamlit: pip install streamlit")
            print("Alternatively, to run the terminal version, ensure streamlit_app.py is not present or rename it.")
        except subprocess.CalledProcessError as e:
            print(f"Error running Streamlit application: {e}")
            print("Alternatively, to run the terminal version, ensure streamlit_app.py is not present or rename it.")
    else:
        print("Streamlit app not found. Running terminal-based interview.")
        # Fallback to original terminal-based flow if streamlit_app.py is missing
        try:
            import interview_flow
            interview_flow.start_interview()
        except ImportError:
            print("Error: Could not import interview_flow module for terminal version.")

if __name__ == "__main__":
    main()
