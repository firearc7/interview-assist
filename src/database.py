"""
Database module for handling SQLite operations.
"""
import sqlite3
import os
import hashlib
import json
from datetime import datetime

# Database file path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "interview_assist.db")

def init_db():
    """Initialize the database with necessary tables."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    ''')
    
    # Create interviews table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        job_role TEXT NOT NULL,
        job_description TEXT,
        difficulty TEXT NOT NULL,
        created_at TEXT NOT NULL,
        overall_score REAL,
        overall_feedback TEXT,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Create questions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER NOT NULL,
        question_text TEXT NOT NULL,
        order_num INTEGER NOT NULL,
        FOREIGN KEY (interview_id) REFERENCES interviews (id)
    )
    ''')
    
    # Create responses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS responses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        response_text TEXT,
        feedback JSON,
        FOREIGN KEY (question_id) REFERENCES questions (id)
    )
    ''')
    
    conn.commit()
    conn.close()

# User management functions
def hash_password(password):
    """Hash a password for storage."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, email, password):
    """Create a new user in the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (username, email, hash_password(password), datetime.now().isoformat())
        )
        conn.commit()
        user_id = cursor.lastrowid
        return user_id
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def validate_user(username, password):
    """Validate user credentials."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, username, password_hash FROM users WHERE username = ?", 
        (username,)
    )
    user = cursor.fetchone()
    conn.close()
    
    if user and user[2] == hash_password(password):
        return {"id": user[0], "username": user[1]}
    return None

def get_user(user_id):
    """Get user information by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, email, created_at FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()
    
    if user:
        return {"id": user[0], "username": user[1], "email": user[2], "created_at": user[3]}
    return None

# Interview management functions
def save_interview(user_id, job_role, job_description, difficulty, questions, responses, feedback, overall_feedback=None, overall_score=None):
    """Save a complete interview session."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # Insert interview
        cursor.execute(
            "INSERT INTO interviews (user_id, job_role, job_description, difficulty, created_at, overall_score, overall_feedback) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (user_id, job_role, job_description, difficulty, datetime.now().isoformat(), overall_score, overall_feedback)
        )
        interview_id = cursor.lastrowid
        
        # Insert questions and responses
        for i, question in enumerate(questions):
            cursor.execute(
                "INSERT INTO questions (interview_id, question_text, order_num) VALUES (?, ?, ?)",
                (interview_id, question, i)
            )
            question_id = cursor.lastrowid
            
            # Check if we have a response for this question
            if i < len(responses) and responses[i] is not None:
                feedback_json = None
                if i < len(feedback) and feedback[i] is not None:
                    feedback_json = json.dumps(feedback[i])
                
                cursor.execute(
                    "INSERT INTO responses (question_id, response_text, feedback) VALUES (?, ?, ?)",
                    (question_id, responses[i], feedback_json)
                )
        
        conn.commit()
        return interview_id
    except Exception as e:
        conn.rollback()
        print(f"Error saving interview: {e}")
        return None
    finally:
        conn.close()

def get_user_interviews(user_id):
    """Get all interviews for a user."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Enable row factory to get column names
    cursor = conn.cursor()
    
    cursor.execute(
        "SELECT * FROM interviews WHERE user_id = ? ORDER BY created_at DESC",
        (user_id,)
    )
    interviews = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return interviews

def get_interview_details(interview_id):
    """Get complete details of an interview including questions, responses, and feedback."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Get interview info
    cursor.execute("SELECT * FROM interviews WHERE id = ?", (interview_id,))
    interview = dict(cursor.fetchone())
    
    # Get questions, responses and feedback
    cursor.execute(
        """
        SELECT q.id, q.question_text, q.order_num, r.response_text, r.feedback
        FROM questions q
        LEFT JOIN responses r ON q.id = r.question_id
        WHERE q.interview_id = ?
        ORDER BY q.order_num
        """,
        (interview_id,)
    )
    
    results = cursor.fetchall()
    questions = []
    responses = []
    feedback = []
    
    for row in results:
        questions.append(row['question_text'])
        responses.append(row['response_text'])
        if row['feedback']:
            feedback.append(json.loads(row['feedback']))
        else:
            feedback.append(None)
    
    conn.close()
    
    return {
        "interview": interview,
        "questions": questions,
        "responses": responses,
        "feedback": feedback
    }

# Initialize the database when the module is imported
init_db()
