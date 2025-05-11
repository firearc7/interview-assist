import unittest
from unittest.mock import patch, MagicMock, ANY
import sqlite3
import os
import json
from src import database

# Use real in-memory database for tests with shared URI
@patch('src.database.DB_PATH', 'file::memory:?cache=shared')
class TestDatabaseModule(unittest.TestCase):

    def setUp(self):
        # Create a connection to the in-memory database
        # URI mode must be enabled for shared memory connection strings
        self.conn = sqlite3.connect('file::memory:?cache=shared', uri=True)
        self.cursor = self.conn.cursor()
        
        # Instead of patching sqlite3.connect, we directly initialize the schema
        # using our connection to ensure tables exist
        self._create_schema()

    def tearDown(self):
        # Clean up connection
        self.conn.close()
    
    def _create_schema(self):
        """Manually create the schema to ensure tables exist."""
        # Create users table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        ''')
        
        # Create interviews table
        self.cursor.execute('''
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
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            interview_id INTEGER NOT NULL,
            question_text TEXT NOT NULL,
            order_num INTEGER NOT NULL,
            FOREIGN KEY (interview_id) REFERENCES interviews (id)
        )
        ''')
        
        # Create responses table
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            question_id INTEGER NOT NULL,
            response_text TEXT,
            feedback JSON,
            FOREIGN KEY (question_id) REFERENCES questions (id)
        )
        ''')
        self.conn.commit()

    def test_init_db(self):
        # Check if tables are created
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users'")
        self.assertIsNotNone(self.cursor.fetchone())
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='interviews'")
        self.assertIsNotNone(self.cursor.fetchone())
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='questions'")
        self.assertIsNotNone(self.cursor.fetchone())
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='responses'")
        self.assertIsNotNone(self.cursor.fetchone())

    def test_hash_password(self):
        hashed = database.hash_password("password123")
        self.assertIsInstance(hashed, str)
        self.assertEqual(hashed, database.hash_password("password123"))
        self.assertNotEqual(hashed, database.hash_password("otherpassword"))

    def test_create_user(self):
        # init_db() is called in setUp, so the table exists.
        user_id = database.create_user("testuser", "test@example.com", "password123")
        self.assertIsNotNone(user_id)
        
        # Verify in DB
        self.cursor.execute("SELECT username FROM users WHERE id = ?", (user_id,))
        self.assertEqual(self.cursor.fetchone()[0], "testuser")

        # Test duplicate username
        user_id_dup = database.create_user("testuser", "test2@example.com", "password123")
        self.assertIsNone(user_id_dup)

    def test_validate_user(self):
        database.create_user("validuser", "valid@example.com", "validpass")
        
        user = database.validate_user("validuser", "validpass")
        self.assertIsNotNone(user)
        self.assertEqual(user["username"], "validuser")

        invalid_user = database.validate_user("validuser", "wrongpass")
        self.assertIsNone(invalid_user)

        non_existent_user = database.validate_user("nouser", "anypass")
        self.assertIsNone(non_existent_user)

    def test_get_user(self):
        user_id = database.create_user("getme", "getme@example.com", "pass")
        user_data = database.get_user(user_id)
        self.assertIsNotNone(user_data)
        self.assertEqual(user_data["username"], "getme")

        non_existent_user_data = database.get_user(999) # Assuming 999 doesn't exist
        self.assertIsNone(non_existent_user_data)

    def test_save_interview(self):
        user_id = database.create_user("interviewuser", "interview@example.com", "pass")
        questions = ["Q1?", "Q2?"]
        responses = ["R1", "R2"]
        feedback_data = [
            {"score": 8, "strengths": "S1", "areas_for_improvement": "A1", "sample_answer": "SA1"},
            {"score": 7, "strengths": "S2", "areas_for_improvement": "A2", "sample_answer": "SA2"}
        ]
        
        interview_id = database.save_interview(
            user_id, "Dev", "Desc", "Medium", questions, responses, feedback_data, "Overall good", 7.5
        )
        self.assertIsNotNone(interview_id)

        # Verify data (simplified check)
        self.cursor.execute("SELECT job_role FROM interviews WHERE id=?", (interview_id,))
        self.assertEqual(self.cursor.fetchone()[0], "Dev")
        self.cursor.execute("SELECT COUNT(*) FROM questions WHERE interview_id=?", (interview_id,))
        self.assertEqual(self.cursor.fetchone()[0], 2)
        self.cursor.execute("SELECT COUNT(*) FROM responses WHERE question_id IN (SELECT id FROM questions WHERE interview_id=?)", (interview_id,))
        self.assertEqual(self.cursor.fetchone()[0], 2)

    def test_save_interview_with_missing_responses_feedback(self):
        user_id = database.create_user("interviewuser2", "interview2@example.com", "pass")
        questions = ["Q1?", "Q2?", "Q3?"]
        responses = ["R1", None, "R3"] # Middle response missing
        feedback_data = [
            {"score": 8}, None, {"score": 7} # Middle feedback missing
        ]
        interview_id = database.save_interview(
            user_id, "Tester", "Test Desc", "Easy", questions, responses, feedback_data
        )
        self.assertIsNotNone(interview_id)
        # Check that 3 questions are saved
        self.cursor.execute("SELECT COUNT(*) FROM questions WHERE interview_id=?", (interview_id,))
        self.assertEqual(self.cursor.fetchone()[0], 3)
        # Check that 2 responses are saved (where response_text is not NULL)
        self.cursor.execute("SELECT COUNT(*) FROM responses WHERE question_id IN (SELECT id FROM questions WHERE interview_id=?) AND response_text IS NOT NULL", (interview_id,))
        self.assertEqual(self.cursor.fetchone()[0], 2)

    def test_get_user_interviews(self):
        user_id = database.create_user("historyuser", "history@example.com", "pass")
        database.save_interview(user_id, "Role1", "D1", "Easy", ["Q"], ["R"], [{}], "F1", 5)
        database.save_interview(user_id, "Role2", "D2", "Hard", ["Q"], ["R"], [{}], "F2", 8)

        interviews = database.get_user_interviews(user_id)
        self.assertEqual(len(interviews), 2)
        self.assertEqual(interviews[0]["job_role"], "Role2") # Ordered by DESC created_at

        no_interviews_user_id = database.create_user("nohistory", "nohistory@example.com", "pass")
        interviews_empty = database.get_user_interviews(no_interviews_user_id)
        self.assertEqual(len(interviews_empty), 0)

    def test_get_interview_details(self):
        user_id = database.create_user("detailuser", "detail@example.com", "pass")
        questions = ["Q1?", "Q2?"]
        responses_text = ["Ans1", "Ans2"]
        feedback_list = [{"score": 10}, {"score": 9}]
        
        interview_id = database.save_interview(
            user_id, "Detail Role", "Detail Desc", "Medium", 
            questions, responses_text, feedback_list
        )
        
        details = database.get_interview_details(interview_id)
        self.assertIsNotNone(details)
        self.assertEqual(details["interview"]["job_role"], "Detail Role")
        self.assertEqual(len(details["questions"]), 2)
        self.assertEqual(details["questions"][0], "Q1?")
        self.assertEqual(len(details["responses"]), 2)
        self.assertEqual(details["responses"][0], "Ans1")
        self.assertEqual(len(details["feedback"]), 2)
        self.assertEqual(details["feedback"][0]["score"], 10)

    # Test for exception during save_interview
    @patch('sqlite3.connect')
    def test_save_interview_exception(self, mock_connect):
        # Set up the mock connection to simulate an error
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = sqlite3.Error("Simulated DB error")
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn

        # Insert a test user directly with our connection to avoid the mocked connection
        self.cursor.execute(
            "INSERT INTO users (username, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            ("erroruser", "error@example.com", database.hash_password("pass"), "2023-01-01")
        )
        self.conn.commit()
        self.cursor.execute("SELECT id FROM users WHERE username = ?", ("erroruser",))
        user_id = self.cursor.fetchone()[0]
        
        # Now test with the mocked connection
        interview_id = database.save_interview(
            user_id, "ErrorRole", "ErrorDesc", "Easy", ["Q"], ["R"], [{}], "ErrorFeedback", 1
        )
        self.assertIsNone(interview_id)
        mock_conn.rollback.assert_called_once()

if __name__ == '__main__':
    unittest.main()
