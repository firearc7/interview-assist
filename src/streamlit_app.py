"""
Streamlit frontend for the AI Interview Simulator.
"""
import streamlit as st
import config_module
import question_module
import evaluation_module
import database
import json
from datetime import datetime

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
    if "user" not in st.session_state:
        st.session_state.user = None
    if "overall_analysis" not in st.session_state:
        st.session_state.overall_analysis = None
    
    # Display navbar if user is logged in
    if st.session_state.user:
        display_navbar()
    
    # Page navigation functions
    def go_to_setup():
        st.session_state.page = "setup"
    
    def go_to_login():
        st.session_state.page = "login"
    
    def go_to_signup():
        st.session_state.page = "signup"
    
    def go_to_dashboard():
        st.session_state.page = "dashboard"
    
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
        st.session_state.overall_analysis = None
    
    def logout():
        st.session_state.user = None
        restart()
    
    # Page routing
    if st.session_state.page == "welcome":
        display_welcome_page(go_to_setup, go_to_login, go_to_signup, go_to_dashboard)
    
    elif st.session_state.page == "login":
        display_login_page(go_to_dashboard)
    
    elif st.session_state.page == "signup":
        display_signup_page(go_to_login)
    
    elif st.session_state.page == "dashboard":
        display_dashboard_page(go_to_setup)
    
    elif st.session_state.page == "interview_history":
        # Extract interview_id from URL params if available
        try:
            interview_id = int(st.query_params.get("id", 0))
            display_interview_history_page(interview_id, go_to_dashboard)
        except (ValueError, TypeError):
            go_to_dashboard()
    
    elif st.session_state.page == "setup":
        display_setup_page(go_to_interview)
    
    elif st.session_state.page == "interview":
        display_interview_page(go_to_results)
    
    elif st.session_state.page == "results":
        display_results_page(restart, go_to_dashboard)

def display_navbar():
    """Display the navigation bar for logged-in users."""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if st.button("🏠 Dashboard", key="nav_dashboard"):
            st.session_state.page = "dashboard"
            st.rerun()
    
    with col2:
        st.write(f"Logged in as: **{st.session_state.user['username']}**")
    
    with col3:
        if st.button("🚪 Logout", key="nav_logout"):
            st.session_state.user = None
            st.session_state.page = "welcome"
            st.rerun()
    
    st.divider()

def display_welcome_page(go_to_setup, go_to_login, go_to_signup, go_to_dashboard):
    st.title("Welcome to the AI Interview Simulator")
    
    st.markdown("""
    **Prepare for your next job interview with the help of AI!**
    
    This tool will:
    - Generate customized interview questions based on your target role
    - Evaluate your responses in real-time
    - Provide constructive feedback to help you improve
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.session_state.user:
            st.button("Start Interview Preparation", on_click=go_to_setup, use_container_width=True)
        else:
            st.button("Login", on_click=go_to_login, use_container_width=True)
    
    with col2:
        if st.session_state.user:
            st.button("View Interview History", on_click=go_to_dashboard, use_container_width=True)
        else:
            st.button("Sign Up", on_click=go_to_signup, use_container_width=True)
    
    with st.expander("How it works"):
        st.markdown("""
        1. **Setup**: Enter your target job role, job description, and difficulty level
        2. **Interview**: Answer questions generated based on your configuration
        3. **Feedback**: Receive detailed evaluation and suggestions for improvement
        
        Your responses are evaluated using advanced AI to provide constructive feedback!
        """)

def display_login_page(go_to_dashboard):
    st.title("Login")
    
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Login", use_container_width=True)
    
    if submit:
        if not username or not password:
            st.error("Please enter both username and password")
        else:
            user = database.validate_user(username, password)
            if user:
                st.session_state.user = user
                st.success("Login successful!")
                go_to_dashboard()
                st.rerun()
            else:
                st.error("Invalid username or password")
    
    st.write("Don't have an account?")
    if st.button("Sign Up"):
        st.session_state.page = "signup"
        st.rerun()
    
    if st.button("Back to Welcome Page"):
        st.session_state.page = "welcome"
        st.rerun()

def display_signup_page(go_to_login):
    st.title("Sign Up")
    
    with st.form("signup_form"):
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")
        submit = st.form_submit_button("Sign Up", use_container_width=True)
    
    if submit:
        if not username or not email or not password or not confirm_password:
            st.error("Please fill out all fields")
        elif password != confirm_password:
            st.error("Passwords do not match")
        else:
            user_id = database.create_user(username, email, password)
            if user_id:
                st.success("Account created successfully! Please login.")
                go_to_login()
                st.rerun()
            else:
                st.error("Username or email already exists")
    
    st.write("Already have an account?")
    if st.button("Login"):
        st.session_state.page = "login"
        st.rerun()
    
    if st.button("Back to Welcome Page"):
        st.session_state.page = "welcome"
        st.rerun()

def display_dashboard_page(go_to_setup):
    st.title("Interview History Dashboard")
    
    if not st.session_state.user:
        st.warning("Please login to view your dashboard")
        if st.button("Go to Login"):
            st.session_state.page = "login"
            st.rerun()
        return
    
    # Get user's interviews from database
    user_id = st.session_state.user["id"]
    interviews = database.get_user_interviews(user_id)
    
    if not interviews:
        st.info("You haven't completed any interviews yet. Start one now!")
        if st.button("Start New Interview", use_container_width=True):
            go_to_setup()
            st.rerun()
        return
    
    # Display interviews as cards
    st.write(f"You have completed {len(interviews)} interviews.")
    
    if st.button("Start New Interview", use_container_width=True):
        go_to_setup()
        st.rerun()
    
    st.divider()
    
    for interview in interviews:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(f"Role: {interview['job_role']}")
            st.write(f"**Difficulty**: {interview['difficulty']}")
            st.write(f"**Date**: {datetime.fromisoformat(interview['created_at']).strftime('%Y-%m-%d %H:%M')}")
            
            if interview['overall_score']:
                st.write(f"**Score**: {float(interview['overall_score']):.1f}/10")
        
        with col2:
            view_button = st.button("View Details", key=f"view_{interview['id']}", use_container_width=True)
            if view_button:
                # Set query params and navigate to interview history page
                st.query_params.update({"id": interview['id']})
                st.session_state.page = "interview_history"
                st.rerun()
        
        st.divider()

def display_interview_history_page(interview_id, go_to_dashboard):
    if not st.session_state.user:
        st.warning("Please login to view interview details")
        if st.button("Go to Login"):
            st.session_state.page = "login"
            st.rerun()
        return
    
    if interview_id <= 0:
        st.error("Invalid interview ID")
        if st.button("Back to Dashboard"):
            go_to_dashboard()
            st.rerun()
        return
    
    # Get interview details from database
    interview_data = database.get_interview_details(interview_id)
    
    if not interview_data:
        st.error("Interview not found")
        if st.button("Back to Dashboard"):
            go_to_dashboard()
            st.rerun()
        return
    
    interview = interview_data["interview"]
    questions = interview_data["questions"]
    responses = interview_data["responses"]
    feedback = interview_data["feedback"]
    
    st.title("Interview Results")
    
    st.markdown("### Interview Summary")
    st.markdown(f"**Job Role**: {interview['job_role']}")
    st.markdown(f"**Difficulty**: {interview['difficulty']}")
    st.markdown(f"**Date**: {datetime.fromisoformat(interview['created_at']).strftime('%Y-%m-%d %H:%M')}")
    
    # Calculate average score
    scores = []
    for fb in feedback:
        if fb:
            try:
                score = float(fb.get('score', 0))
                scores.append(score)
            except (ValueError, TypeError):
                pass
    
    avg_score = sum(scores) / len(scores) if scores else 0
    st.markdown(f"**Average Score**: {avg_score:.1f} / 10")
    
    if interview['overall_feedback']:
        try:
            overall_analysis = json.loads(interview['overall_feedback'])
            
            st.markdown("### Overall Performance Analysis")
            st.markdown(overall_analysis.get("overall_analysis", "No analysis available."))
            
            # Display average score if available
            if "average_score" in overall_analysis:
                avg_score = overall_analysis["average_score"]
                st.markdown(f"**Overall Score**: {avg_score:.1f} / 10")
            
            st.markdown("#### Key Strengths")
            strengths = overall_analysis.get("key_strengths", ["No strengths identified."])
            for strength in strengths:
                st.markdown(f"- {strength}")
                
            st.markdown("#### Areas for Improvement")
            improvements = overall_analysis.get("improvement_areas", ["No improvement areas identified."])
            for area in improvements:
                st.markdown(f"- {area}")
                
            st.markdown("#### Preparation Tips")
            tips = overall_analysis.get("preparation_tips", ["No preparation tips available."])
            for tip in tips:
                st.markdown(f"- {tip}")
        except:
            st.markdown("### Overall Feedback")
            st.markdown(interview['overall_feedback'])
    
    # Display individual questions and answers
    st.markdown("### Question Details")
    
    for i in range(len(questions)):
        question = questions[i]
        response = responses[i] if i < len(responses) else None
        feedback_item = feedback[i] if i < len(feedback) else None

        with st.expander(f"Question {i+1}: {question[:50]}...", expanded=False):
            st.markdown(f"**Question**: {question}")
            st.markdown(f"**Your Response**: {response if response else '*No answer submitted*'}")
            
            if feedback_item:
                st.markdown("#### Feedback")
                score = feedback_item.get('score', 'N/A')
                score_display = str(score)
                try:
                    score_val = float(score)
                    score_display = f"{score_val:.1f} / 10"
                except (ValueError, TypeError):
                    pass

                st.markdown(f"**Score**: {score_display}")
                st.markdown(f"**Strengths**: {feedback_item.get('strengths', 'N/A')}")
                st.markdown(f"**Areas for Improvement**: {feedback_item.get('areas_for_improvement', 'N/A')}")
                st.markdown(f"**Sample Answer**: {feedback_item.get('sample_answer', 'N/A')}")
            else:
                st.markdown("#### Feedback")
                st.markdown("*Feedback not available for this question.*")
    
    if st.button("Back to Dashboard", use_container_width=True):
        go_to_dashboard()
        st.rerun()

def display_setup_page(go_to_interview):
    st.title("Interview Setup")
    
    # Form to collect interview configuration
    with st.form("interview_config_form"):
        job_role = st.text_input("Job Role (e.g., Software Engineer, Product Manager)", placeholder="Enter the role you're applying for")
        job_description = st.text_area("Job Description", placeholder="Paste the job description here...", height=150)
        difficulty = st.select_slider("Difficulty Level", options=["Easy", "Medium", "Hard"], value="Medium")
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
                    # Reset responses and feedback for new interview
                    st.session_state.responses = []
                    st.session_state.feedback = []
                    st.session_state.current_question_idx = 0
                    
                    # Button to start interview, appears after questions are generated
                    if st.button("Start Interview", on_click=go_to_interview, use_container_width=True, key="start_interview_main_button"):
                        pass # Callback handles navigation
                else:
                    st.error("Failed to generate questions. Please try again.")

def display_interview_page(go_to_results):
    st.title("Interview Simulation")

    total_questions = len(st.session_state.questions)
    current_idx = st.session_state.current_question_idx

    if not st.session_state.questions:
        st.error("No questions loaded. Please go back to setup.")
        if st.button("Back to Setup"):
            st.session_state.page = "setup"
            st.rerun()
        return

    progress_text = f"Question {current_idx + 1} of {total_questions}"
    progress_percentage = (current_idx + 1) / total_questions
    st.progress(progress_percentage, text=progress_text)

    current_question = st.session_state.questions[current_idx]
    st.markdown(f"### Question: {current_question}")

    is_previously_answered = current_idx < len(st.session_state.responses) and st.session_state.responses[current_idx] is not None

    # Callbacks for navigation buttons
    def _go_next_question_page():
        if st.session_state.current_question_idx < total_questions - 1:
            st.session_state.current_question_idx += 1
        # Streamlit handles rerun via on_click

    def _go_prev_question_page():
        if st.session_state.current_question_idx > 0:
            st.session_state.current_question_idx -= 1
        # Streamlit handles rerun via on_click

    if is_previously_answered:
        st.markdown("---")
        st.markdown("#### Your Answer:")
        st.text_area(
            label="Previously Submitted Answer",
            value=st.session_state.responses[current_idx],
            height=150,
            disabled=True,
            key=f"displayed_response_{current_idx}"
        )

        if current_idx < len(st.session_state.feedback) and st.session_state.feedback[current_idx]:
            feedback = st.session_state.feedback[current_idx]
            st.markdown("---")
            st.markdown("#### Feedback for This Answer:")
            
            score = feedback.get('score', 'N/A')
            strengths = feedback.get('strengths', 'N/A')
            areas_for_improvement = feedback.get('areas_for_improvement', 'N/A')
            sample_answer = feedback.get('sample_answer', 'N/A')

            score_display = str(score)
            try:
                score_val = float(score)
                score_display = f"{score_val:.1f} / 10"
            except (ValueError, TypeError):
                pass # score_display remains as is

            st.info(f"**Score**: {score_display}")
            st.success(f"**Strengths**: {strengths}")
            st.warning(f"**Areas for Improvement**: {areas_for_improvement}")
            with st.expander("View Sample Answer"):
                st.markdown(sample_answer)
        else:
            st.info("Feedback for this question is not available.")
        st.markdown("---")
    else:  # Current question to be answered
        with st.form("response_form"):
            response_text = st.text_area(
                "Your Answer",
                height=150,
                placeholder="Type your answer here...",
                key=f"response_input_{current_idx}"
            )
            submit_button = st.form_submit_button("Submit Answer", use_container_width=True)

        if submit_button:
            if not response_text.strip():
                st.warning("Please provide an answer before submitting.")
            else:
                with st.spinner("Evaluating your response..."):
                    feedback = evaluation_module.evaluate_response(
                        current_question,
                        response_text,
                        st.session_state.interview_config
                    )

                while len(st.session_state.responses) <= current_idx:
                    st.session_state.responses.append(None)
                while len(st.session_state.feedback) <= current_idx:
                    st.session_state.feedback.append(None)

                st.session_state.responses[current_idx] = response_text
                st.session_state.feedback[current_idx] = feedback

                if current_idx < total_questions - 1:
                    st.session_state.current_question_idx += 1
                    st.rerun()
                else:
                    go_to_results()
                    st.rerun()

    # Navigation buttons (common for both states)
    cols = st.columns(2)
    with cols[0]:
        if current_idx > 0:
            st.button("⬅️ Previous Question", on_click=_go_prev_question_page, use_container_width=True, key=f"prev_q_{current_idx}")
        else:
            st.write("") # Placeholder for layout consistency

    with cols[1]:
        if is_previously_answered:
            if current_idx < total_questions - 1:
                st.button("Next Question ➡️", on_click=_go_next_question_page, use_container_width=True, key=f"next_q_{current_idx}")
            else: # Last question, previously answered
                st.button("View Results ➡️", on_click=go_to_results, use_container_width=True, key=f"results_q_{current_idx}")
        # If not previously answered, submit button handles progression. No explicit next/results button here.
        # Adding placeholder for consistent layout if needed, or leave as is if submit button is prominent enough.
        else:
            st.write("") # Placeholder for layout consistency

    # The old expander for "Feedback for previous question" is removed as per requirements.

def display_results_page(restart, go_to_dashboard):
    st.title("Interview Results")
    
    st.markdown("### Your Interview Summary")
    st.markdown(f"**Job Role**: {st.session_state.interview_config.get('job_role')}")
    st.markdown(f"**Difficulty**: {st.session_state.interview_config.get('difficulty')}")
    
    # Calculate average score
    scores = []
    valid_feedback_count = 0
    for feedback_item in st.session_state.feedback:
        if feedback_item: # Check if feedback_item is not None
            try:
                score = float(feedback_item.get('score', 0))
                scores.append(score)
                valid_feedback_count +=1
            except (ValueError, TypeError):
                pass # Ignore if score is not a valid number
    
    if scores: # Recalculate avg_score based on valid feedback items
        avg_score = sum(scores) / len(scores) if scores else 0
        st.markdown(f"**Average Score**: {avg_score:.1f} / 10 (based on {len(scores)} evaluated questions)")
    elif valid_feedback_count == 0 and st.session_state.questions:
        st.markdown("**Average Score**: N/A (No valid feedback received for any question)")
    else:
        st.markdown("**Average Score**: N/A")
    
    # Generate overall analysis if not already done
    if not st.session_state.overall_analysis and st.session_state.responses and st.session_state.feedback:
        with st.spinner("Generating overall performance analysis..."):
            st.session_state.overall_analysis = evaluation_module.generate_overall_performance(
                st.session_state.questions,
                st.session_state.responses,
                st.session_state.feedback,
                st.session_state.interview_config
            )
    
    # Display overall analysis
    if st.session_state.overall_analysis:
        st.markdown("### Overall Performance Analysis")
        st.markdown(st.session_state.overall_analysis.get("overall_analysis", "No analysis available."))
        
        # Display average score if available
        if "average_score" in st.session_state.overall_analysis:
            avg_score = st.session_state.overall_analysis["average_score"]
            st.markdown(f"**Overall Score**: {avg_score:.1f} / 10")
        
        st.markdown("#### Key Strengths")
        strengths = st.session_state.overall_analysis.get("key_strengths", ["No strengths identified."])
        for strength in strengths:
            st.markdown(f"- {strength}")
        
        st.markdown("#### Areas for Improvement")
        improvements = st.session_state.overall_analysis.get("improvement_areas", ["No improvement areas identified."])
        for area in improvements:
            st.markdown(f"- {area}")
        
        st.markdown("#### Preparation Tips")
        tips = st.session_state.overall_analysis.get("preparation_tips", ["No preparation tips available."])
        for tip in tips:
            st.markdown(f"- {tip}")
    
    # Display questions, responses and feedback
    st.markdown("### Question Details")
    
    for i in range(len(st.session_state.questions)):
        question = st.session_state.questions[i]
        response = st.session_state.responses[i] if i < len(st.session_state.responses) else None
        feedback_item = st.session_state.feedback[i] if i < len(st.session_state.feedback) else None

        with st.expander(f"Question {i+1}: {question[:50]}...", expanded=False):
            st.markdown(f"**Question**: {question}")
            st.markdown(f"**Your Response**: {response if response else '*No answer submitted*'}")
            
            if feedback_item:
                st.markdown("#### Feedback")
                score = feedback_item.get('score', 'N/A')
                score_display = str(score)
                try:
                    score_val = float(score)
                    score_display = f"{score_val:.1f} / 10"
                except (ValueError, TypeError):
                    pass

                st.markdown(f"**Score**: {score_display}")
                st.markdown(f"**Strengths**: {feedback_item.get('strengths', 'N/A')}")
                st.markdown(f"**Areas for Improvement**: {feedback_item.get('areas_for_improvement', 'N/A')}")
                st.markdown(f"**Sample Answer**: {feedback_item.get('sample_answer', 'N/A')}")
            else:
                st.markdown("#### Feedback")
                st.markdown("*Feedback not available for this question.*")
    
    # Save interview to database if user is logged in
    if st.session_state.user and st.session_state.responses:
        overall_feedback = None
        if st.session_state.overall_analysis:
            try:
                overall_feedback = json.dumps(st.session_state.overall_analysis)
            except:
                overall_feedback = str(st.session_state.overall_analysis)
        
        interview_id = database.save_interview(
            user_id=st.session_state.user["id"],
            job_role=st.session_state.interview_config.get("job_role"),
            job_description=st.session_state.interview_config.get("job_description"),
            difficulty=st.session_state.interview_config.get("difficulty"),
            questions=st.session_state.questions,
            responses=st.session_state.responses,
            feedback=st.session_state.feedback,
            overall_feedback=overall_feedback,
            overall_score=avg_score if scores else None
        )
        
        if interview_id:
            st.success("Interview saved to your history!")
    
    # Buttons to restart or go to dashboard
    col1, col2 = st.columns(2)
    
    with col1:
        st.button("Start New Interview", on_click=restart, use_container_width=True)
    
    with col2:
        if st.session_state.user:
            if st.button("Go to Dashboard", on_click=go_to_dashboard, use_container_width=True):
                pass
        else:
            if st.button("Exit", on_click=lambda: st.stop(), use_container_width=True):
                pass

if __name__ == "__main__":
    main()
