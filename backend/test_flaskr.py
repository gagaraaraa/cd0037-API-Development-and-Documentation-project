import os
from os.path import join, dirname
from dotenv import load_dotenv
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

USERNAME = os.environ.get("USERNAME")
PASSWORD = os.environ.get("PASSWORD")
HOSTNAME = os.environ.get("HOSTNAME")


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        # self.database_path = "postgresql://{}/{}".format('localhost:5432', self.database_name)
        self.database_path = f'postgresql://{USERNAME}:{PASSWORD}@localhost:{HOSTNAME}/{self.database_name}'
        setup_db(self.app, self.database_path)

        self.new_question = {
            'question' : 'Which Tool song starts with "There s a shadow just behind me"',
            'answer' : 'Sober',
            'category' : '2',
            'difficulty' : 3
        }

        self.new_quiz = {'type': 'click', 'id': 0}

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_categories'])
        self.assertTrue(len(data['categories']))
    
    def test_retrieve_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    # def test_404_sent_requesting_beyond_valid_page(self):
    #     res = self.client().get('/questions?page=1000', json={'rating': 1})
    #     data = json.loads(res.data)
        
    #     self.assertEqual(res.status_code, 404)
    #     self.assertEqual(data['success'], False)
    #     self.assertEqual(data['message'], 'Not found')

    def test_get_questions_for_category(self):
        res = self.client().get('/categories/1/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))

    def test_404_send_request_for_invalid_category(self):
        res = self.client().get('/categories/100/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_delete_question(self):
        res = self.client().delete('/questions/30')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 5).one_or_none()
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)
    
    def test_422_delete_question_invalid_id(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(len(data['questions']))
    
    def test_405_question_creation_not_allowed(self):
        res = self.client().post('/questions/45', json=self.new_question)
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 405)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'method not allowed')

    def test_get_question_search_with_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'Butter'})
        data = json.loads(res.data)
        
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['total_questions'])
        self.assertEqual(len(data['questions']), 1)
        
    def test_get_question_search_without_results(self):
        res = self.client().post('/questions', json={'searchTerm': 'Svenja'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['total_questions'], 0)
        self.assertEqual(len(data['questions']), 0)
    
    def test_create_quizze(self):
        res = self.client().post('/quizzes', json={'quiz_category' : {'type': 'click', 'id': 0}, 'previous_questions' : [1]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['question']), 5)

    def test_422_create_quizze_without_all_data(self):
        res = self.client().post('/quizzes', json={'quiz_category' : {'type': 'click', 'id': 100}, 'previous_questions' : [1]})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()