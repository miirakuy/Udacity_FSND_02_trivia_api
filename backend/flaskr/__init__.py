import os
from flask import (
  Flask, 
  request, 
  abort, 
  jsonify
)
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10

# Helper method
def paginate_questions(request, entry):
  page = request.args.get('page', 1, type=int)
  start = (page - 1) * QUESTIONS_PER_PAGE
  end = start + QUESTIONS_PER_PAGE

  questions = [question.format() for question in entry]
  current_questions = questions[start:end]

  return current_questions

def create_app(test_config=None):
  # create and configure the app
  app = Flask(__name__, instance_relative_config=True)
  setup_db(app)
  
  '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
  CORS(app, resource={r"/api.*": {"origin": "*"}})

  '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
  # CORS Headers
  @app.after_request
  def after_request(response):
    response.headers.add('Access-Control-Allow_Headers', 'Content-Type,Authorization,true')
    response.headers.add('Access-Contorl-Allow_Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

  '''
  @TODO: 
  Create an endpoint to handle GET requests 
  for all available categories.
  '''
  @app.route('/categories', methods=['GET'])
  def get_all_categories():
    categories = Category.query.order_by(Category.id).all()
    categories_list = [category.type for category in categories]
    
    return jsonify({
      'categories': categories_list
    })

  '''
  @TODO: 
  Create an endpoint to handle GET requests for questions, 
  including pagination (every 10 questions). 
  This endpoint should return a list of questions, 
  number of total questions, current category, categories. 

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions. 
  '''
  @app.route('/questions', methods=['GET'])
  def get_questions():
    question_entry = Question.query.order_by(Question.id).all()
    questions = paginate_questions(request, question_entry)

    if len(questions) == 0:
      abort(404)

    # iterate through category, and append to the category dictionary.
    category_entry = Category.query.order_by(Category.id).all()
    categories_dict = {}
    for category in category_entry:
      categories_dict[category.id] = category.type

    # create a list of questions's category
    current_category = [question['category'] for question in questions]

    return jsonify({
      'questions': questions,
      'total_questions': len(questions),
      'categories': categories_dict,
      'current_category': current_category
    })

  '''
  @TODO: 
  Create an endpoint to DELETE question using a question ID. 

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page. 
  '''
  @app.route('/questions/<int:question_id>', methods=['DELETE'])
  def delete_question(question_id):
    try:
      question = Question.query.filter(Question.id == question_id).one_or_none()

      if question is None:
        abort(404)

      question.delete()
      question_entry = Question.query.order_by(Question.id).all()
      questions = paginate_questions(request, question_entry)

      return jsonify({
        'success':True,
        'deleted': question_id,
        'questions': questions,
        'totak_questions': len(Question.query.all())
      })
    
    except:
      abort(422)

  '''
  @TODO: 
  Create an endpoint to POST a new question, 
  which will require the question and answer text, 
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab, 
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.  
  '''
  @app.route('/questions', methods=['POST'])
  def create_question():
    body = request.get_json()

    new_question = body.get('question', None)
    new_answer = body.get('answer', None)
    new_difficulty = body.get('difficulty', None)
    new_category = body.get('category', None)

    try:
      question = Question(question=new_question, answer=new_answer, difficulty=new_difficulty, category=new_category)
      question.insert()

      entry = Question.query.order_by(Question.id).all()
      current_questions = paginate_questions(request, entry)

      return jsonify({
        'success':True,
        'created': question.id,
        'questions': current_questions,
        'total_questions': len(Question.query.all())
      })

    except:
      abort(422)

  '''
  @TODO: 
  Create a POST endpoint to get questions based on a search term. 
  It should return any questions for whom the search term 
  is a substring of the question. 

  TEST: Search by any phrase. The questions list will update to include 
  only question that include that string within their question. 
  Try using the word "title" to start. 
  '''
  @app.route('/search', methods=['POST'])
  def get_questions_by_term():
    body = request.get_json()
    search_term = body.get('searchTerm', None)

    try:
      question_entry = Question.query.filter(Question.question.ilike('%{}%'.format(search_term))).all()
      current_category = [question.category for question in question_entry]

      return jsonify({
        'success': True,
        'questions': paginate_questions(request, question_entry),
        'total_questions': len(question_entry),
        'current_category': current_category
      })
    except:
      abort(422)

  '''
  @TODO: 
  Create a GET endpoint to get questions based on category. 

  TEST: In the "List" tab / main screen, clicking on one of the 
  categories in the left column will cause only questions of that 
  category to be shown. 
  '''
  @app.route('/categories/<int:category_id>/questions', methods=['GET'])
  def get_questions_by_category(category_id):
    try:
      category = Category.query.filter(Category.id == str(category_id)).one_or_none()
      entry = Question.query.filter_by(category=str(category_id)).all()
      current_questions = paginate_questions(request, entry)

      return jsonify({
        'Success': True,
        'questions': current_questions,
        'total_questions': len(entry),
        'current_category': category.type
      })

    except:
      abort(422) 

  '''
  @TODO: 
  Create a POST endpoint to get questions to play the quiz. 
  This endpoint should take category and previous question parameters 
  and return a random questions within the given category, 
  if provided, and that is not one of the previous questions. 

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not. 
  '''
  

  '''
  @TODO: 
  Create error handlers for all expected errors 
  including 404 and 422. 
  '''
  @app.errorhandler(404)
  def not_found(error):
    return jsonify({
      'success': False,
      'error': 404,
      'message': "resource not found"
    }), 404

  @app.errorhandler(422)
  def unprocessable(error):
    return jsonify({
      'success': False,
      'error': 422,
      'message': "unprocessable"
    }), 422
  
  @app.errorhandler(400)
  def bad_request(error):
    return jsonify({
      'success': False,
      'error': 400,
      'message': "bad request"
    }), 400
    
  @app.errorhandler(405)
  def method_not_allowed(error):
    return jsonify({
      'success': False,
      'error': 405,
      'message': "method_not_allowed"
    }), 405

  return app

    