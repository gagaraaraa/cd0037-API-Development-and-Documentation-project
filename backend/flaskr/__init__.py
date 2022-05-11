from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type = int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = list((question.format() for question in selection))
    current_questions = questions[start:end]

    return current_questions

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    """
    Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """
    CORS(app, resources={r"/*": {"origins": "*"}})

    """
    Use the after_request decorator to set Access-Control-Allow
    """
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    """
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route('/categories')
    def retrieve_categories():
        try:
            selection = Category.query.order_by(Category.id).all()
            categories = (category.format() for category in selection)
            categories = list(categories)

            if len(selection) == 0:
                abort(404)

            categories = Category.query.order_by(Category.id).all()
            categories_dict = {}
            for category in categories: 
                categories_dict[category.id] = category.type

            return jsonify({
                'success': True, 
                'categories': categories,
                'total_categories': len(selection),
                'categories' : categories_dict,
                'current_category' : None
            })

        except:
            abort(404)


    """
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route('/questions')
    def retrieve_questions():
        try:
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            if len(current_questions) == 0:
                abort(404)

            categories = Category.query.order_by(Category.id).all()
            categories_dict = {}
            for category in categories: 
                categories_dict[category.id] = category.type
        
            return jsonify({
                'success': True, 
                'questions': current_questions,
                'total_questions': len(Question.query.all()),
                'categories' : categories_dict,
                'current_category' : None
            })
        except:
            abort(404)
        

    @app.route('/categories/<int:category_id>/questions')
    def get_questions_for_category(category_id):
        try:
            selection = Question.query.order_by(Question.id).filter(Question.category == category_id).all()
            current_questions = paginate_questions(request, selection)

            if len(current_questions) == 0:
                abort(404)

            current_category = Category.query.filter(Category.id == category_id).one_or_none()
            category_name = current_category.type
        
            return jsonify({
                'success': True, 
                'questions': current_questions,
                'total_questions': len(selection),
                'current_category' : category_name
            })      

        except:
            abort(404)

    """
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        try:
            question = Question.query.filter(Question.id == question_id).one_or_none()
            
            if question is None:
                abort(404)
            
            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'success': True,
                # 'deleted': question_id,
                # 'questions': current_questions,
                # 'total_questions': len(Question.query.all())
            })
        
        except:
            abort(422)


    """
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        new_question = body.get('question', None)
        searchTerm = body.get('searchTerm', None)

        try:
            if searchTerm:
                selection = Question.query.order_by(Question.id).filter(Question.question.ilike('%{}%'.format(searchTerm))).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(selection)
                })

            else:
                question = Question(question=new_question, answer=new_answer, category=new_category, difficulty=new_difficulty)
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'created': question.id,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
        
        except:
            abort(422)



    """
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.
    """

    """
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route('/categories/<int:category_id>')
    def get_questions_from_category(category_id):
        try:
            selection = Question.query.filter(Question.category == category_id).all()
            current_questions = paginate_questions(request, selection)

            return jsonify({
                'succes': True,
                'questions': current_questions,
                'total_questions': len(selection)
            })
        except:
            abort(404)

    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """ 
    @app.route('/quizzes', methods=['POST'])
    def create_quiz():
        try:
            body = request.get_json()
            quizCategory = body.get('quiz_category', None)
            previousQuestion = body.get('previous_questions', None)
            quizCategory = quizCategory['id']
            selection = []

            if quizCategory == 0:
                questions = Question.query.all()
                # questions = Question.query.filter(Question.id.not_in(previousQuestion)).all
            else: 
                questions = Question.query.filter(Question.category == quizCategory).all()
            for question in questions:
                if question.id not in previousQuestion:
                    selection.append(question)
            
            if len(selection) == 0:
                return jsonify({
                    'question': False
                })

            random_question = random.choice(selection)
            previousQuestion.append(random_question.id)

            return jsonify({
                'question': {
                    'id' : random_question.id, 
                    'question' : random_question.question,
                    'answer' : random_question.answer,
                    'difficulty' : random_question.difficulty,
                    'category' : random_question.category
                },
                'success' : True,
                'previousQuestion' : previousQuestion
            })
        except:
            abort(422)

    """
    Create error handlers for all expected errors 
    including 404 and 422.
    """
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
        'success': False,
        'error': 400,
        'message': 'bad request'
        }), 400

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
        'success': False, 
        'error': 404,
        'message': 'Not found'
        }), 404
    
    @app.errorhandler(405)
    def not_allowed(error):
        return jsonify({
        'success': False,
        'error': 405,
        'message': 'method not allowed'
        }), 405

 
    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
        'success': False, 
        'error': 422,
        'message': 'unprocessable'
        }), 422
   
    @app.errorhandler(500)
    def internal_server_error(error):
        return jsonify({
        'success': False,
        'error': 500,
        'message': 'internal server error'
        }), 500
    
    return app

