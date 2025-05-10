"""
Streamlit frontend for the AI Interview Simulator.
"""
import streamlit as st
import config_module
import question_module
import evaluation_module

def main():
    # Set up the basic app configuration
    st.set_page_config(
        page_title="AI Interview Simulator",
        page_icon="💼",
        layout="centered",
    )
    
    # Initialize session state variables if they don't exist
    if "page" not in st.session_state:
        st.session_state.page = "welcome"
    if "interview_config" not in st.session_state:
        st.session_state.interview_config = None
    if "questions" not in st.session_state:
        st.session_state.questions = []
    if "current_question_idx" not in st.session_state:
        st.session_state.current_question_idx = 0
    if "responses" not in st.session_state:
        st.session_state.responses = []
    if "feedback" not in st.session_state:
        st.session_state.feedback = []
    
    # Page navigation functions
    def go_to_setup():
        st.session_state.page = "setup"
    
    def go_to_interview():
        st.session_state.page = "interview"
    
    def go_to_results():
        st.session_state.page = "results"
    
    def restart():
        st.session_state.page = "welcome"
        st.session_state.interview_config = None
        st.session_state.questions = []
        st.session_state.current_question_idx = 0
        st.session_state.responses = []
        st.session_state.feedback = []
    
    # Welcome Page
    if st.session_state.page == "welcome":
        display_welcome_page(go_to_setup)
    
    # Setup Page
    elif st.session_state.page == "setup":
        display_setup_page(go_to_interview)
    
    # Interview Page
    elif st.session_state.page == "interview":
        display_interview_page(go_to_results)
    
    # Results Page
    elif st.session_state.page == "results":
        display_results_page(restart)

def display_welcome_page(go_to_setup):
    st.title("Welcome to the AI Interview Simulator")
    
    st.markdown("""
    **Prepare for your next job interview with the help of AI!**
    
    This tool will:
    - Generate customized interview questions based on your target role
    - Evaluate your responses in real-time
    - Provide constructive feedback to help you improve
    
    Ready to start practicing? Click the button below!
    """)
    
    st.button("Start Interview Preparation", on_click=go_to_setup, use_container_width=True)
    
    with st.expander("How it works"):
        st.markdown("""
        1. **Setup**: Enter your target job role, job description, and difficulty level
        2. **Interview**: Answer questions generated based on your configuration
        3. **Feedback**: Receive detailed evaluation and suggestions for improvement
        
        Your responses are evaluated using advanced AI to provide constructive feedback!
        """)

def display_setup_page(go_to_interview):
    st.title("Interview Setup")
    
    # Form to collect interview configuration
    with st.form("interview_config_form"):
        job_role = st.text_input("Job Role (e.g., Software Engineer, Product Manager)", placeholder="Enter the role you're applying for")
        job_description = st.text_area("Job Description", placeholder="Paste the job description here...", height=150)
        difficulty = st.select_slider("Difficulty Level", options=["easy", "medium", "hard"], value="medium")
        num_questions = st.slider("Number of Questions", min_value=3, max_value=10, value=5, step=1)
        
        # Using form_submit_button instead of regular button with callback
        submit_button = st.form_submit_button("Generate Questions", use_container_width=True)
        
    # Process form after submission (outside the form)
    if submit_button:
        if not job_role or not job_description:
            st.error("Please fill in both the job role and job description fields.")
        else:
            # Create interview configuration
            with st.spinner("Setting up your interview..."):
                st.session_state.interview_config = {
                    "job_role": job_role,
                    "job_description": job_description,
                    "difficulty": difficulty,
                }
                
                # Generate questions using the existing module
                st.session_state.questions = question_module.generate_questions(
                    st.session_state.interview_config, 
                    num_questions=num_questions
                )
                
                if st.session_state.questions:
                    st.success(f"Generated {len(st.session_state.questions)} questions for your interview!")
                    # Move the button outside the form
                    st.button("Start Interview", on_click=go_to_interview, use_container_width=True)
                else:
                    st.error("Failed to generate questions. Please try again.")

def display_interview_page(go_to_results):
    st.title("Interview Simulation")
    
    # Display progress
    total_questions = len(st.session_state.questions)
    current_idx = st.session_state.current_question_idx
    
    # Display progress bar
    progress_text = f"Question {current_idx + 1} of {total_questions}"
    progress_percentage = (current_idx + 1) / total_questions
    st.progress(progress_percentage, text=progress_text)
    
    # Get current question
    current_question = st.session_state.questions[current_idx]
    
    # Display question
    st.markdown(f"### Question: {current_question}")
    
    # Response input area
    with st.form("response_form"):
        response = st.text_area("Your Answer", height=150, placeholder="Type your answer here...", key=f"response_{current_idx}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            submit_button = st.form_submit_button("Submit Answer", use_container_width=True)
        
        with col2:
            if current_idx > 0:
                back_button = st.form_submit_button("Previous Question", use_container_width=True)
            else:
                back_button = False
    
    # Process form submission (outside the form)
    if submit_button and response:
        # Process response
        with st.spinner("Evaluating your response..."):
            # Evaluate the response using the existing module
            feedback = evaluation_module.evaluate_response(
                current_question, 
                response, 
                st.session_state.interview_config
            )
            
            # Save response and feedback
            if len(st.session_state.responses) <= current_idx:
                st.session_state.responses.append(response)
                st.session_state.feedback.append(feedback)
            else:
                st.session_state.responses[current_idx] = response
                st.session_state.feedback[current_idx] = feedback
            
            # Move to next question or results if done
            if current_idx < total_questions - 1:
                st.session_state.current_question_idx += 1
                st.rerun()
            else:
                go_to_results()
    
    elif back_button and current_idx > 0:
        st.session_state.current_question_idx -= 1
        st.rerun()
    
    # Display feedback for the previous question if available
    if current_idx > 0 and len(st.session_state.feedback) >= current_idx:
        with st.expander("Feedback for previous question", expanded=False):
            prev_feedback = st.session_state.feedback[current_idx - 1]
            st.markdown("### Feedback for your previous answer")
            st.markdown(f"**Score**: {prev_feedback.get('score', 'N/A')}")
            st.markdown(f"**Strengths**: {prev_feedback.get('strengths', 'N/A')}")
            st.markdown(f"**Areas for Improvement**: {prev_feedback.get('areas_for_improvement', 'N/A')}")
            st.markdown(f"**Sample Answer**: {prev_feedback.get('sample_answer', 'N/A')}")

def display_results_page(restart):
    st.title("Interview Results")
    
    st.markdown("### Your Interview Summary")
    st.markdown(f"**Job Role**: {st.session_state.interview_config.get('job_role')}")
    st.markdown(f"**Difficulty**: {st.session_state.interview_config.get('difficulty')}")
    
    # Calculate average score
    scores = []
    for feedback in st.session_state.feedback:
        try:
            score = float(feedback.get('score', 0))
            scores.append(score)
        except (ValueError, TypeError):
            pass
    
    if scores:
        avg_score = sum(scores) / len(scores)
        st.markdown(f"**Average Score**: {avg_score:.1f} / 10")
    
    # Display questions, responses and feedback
    for i, (question, response, feedback) in enumerate(zip(
        st.session_state.questions, 
        st.session_state.responses, 
        st.session_state.feedback
    )):
        with st.expander(f"Question {i+1}: {question[:50]}...", expanded=False):
            st.markdown(f"**Question**: {question}")
            st.markdown(f"**Your Response**: {response}")
            st.markdown("#### Feedback")
            st.markdown(f"**Score**: {feedback.get('score', 'N/A')}")
            st.markdown(f"**Strengths**: {feedback.get('strengths', 'N/A')}")
            st.markdown(f"**Areas for Improvement**: {feedback.get('areas_for_improvement', 'N/A')}")
            st.markdown(f"**Sample Answer**: {feedback.get('sample_answer', 'N/A')}")
    
    # Buttons to restart or exit
    col1, col2 = st.columns(2)
    
    with col1:
        st.button("Start New Interview", on_click=restart, use_container_width=True)
    
    with col2:
        st.button("Exit", on_click=lambda: st.stop(), use_container_width=True)
    
    # General tips and resources
    with st.expander("Interview Tips", expanded=False):
        st.markdown("""
        ### General Interview Tips
        
        1. **Research the company** before your interview
        2. **Practice your answers** to common questions
        3. **Use the STAR method** (Situation, Task, Action, Result) for behavioral questions
        4. **Prepare questions** to ask the interviewer
        5. **Follow up** after the interview with a thank-you note
        """)

if __name__ == "__main__":
    main()
