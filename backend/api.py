from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from src.database.models import db_drop_and_create_all, setup_db, Drink
from src.auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
#db_drop_and_create_all()


# Helper Methods
def get_short_drinks():
    # Getting the drinks from the database and aborting with 500 status code if something goes wrong
    drinks = None
    try:
        drinks = Drink.query.all()
    except():
        return drinks
    # Getting drinks in its long repr
    drinks_serialized = [drink.short() for drink in drinks]
    # Returning the drinks in its short repr
    return drinks_serialized


def get_long_drinks():
    # Getting the drinks from the database and aborting with 500 status code if something goes wrong
    drinks = None
    try:
        drinks = Drink.query.all()
    except():
        return drinks
    # Getting drinks in its long repr
    drinks_serialized = [drink.long() for drink in drinks]
    # Returning the drinks in its long repr
    return drinks_serialized


# ROUTES


@app.route('/', methods=['GET'])
def index():
    return 'Welcome to Coffee API!'


@app.route('/drinks', methods=['GET'])
def get_drinks():
    # Getting the drinks from the database and aborting with 500 status code if something goes wrong
    drinks = get_short_drinks()
    if not drinks:
        abort(500)
    # Returning the response
    return jsonify({
        "success": True,
        "drinks": drinks
    }, 200)


@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_detail(token_map):
    # Getting the drinks from the database and aborting with 500 status code if something goes wrong
    drinks = get_long_drinks()
    if not drinks:
        abort(500)
    # Returning the response
    return jsonify({
        'success': True,
        'drinks': drinks
    }), 200


@app.route("/drinks", methods=['POST'])
@requires_auth('post:drinks')
def add_drink(token_map):
    # Getting the request data as JSON
    req_body = request.get_json()
    if req_body is None:
        abort(400)
    # Checking if the user posted an invalid data (id is passed from the frontend even though I don't use it)
    allowed_fields_of_drink = ['id', 'title', 'recipe']
    for field in req_body:
        if field not in allowed_fields_of_drink:
            abort(422)
    # Adding the drink to our database
    recipe = json.dumps(req_body['recipe']) #json.loads() doesn't work here
    drink = Drink(req_body['title'], recipe)
    operation_success = drink.insert()
    if not operation_success:
        abort(500)
    # Returning the response
    # Getting the drinks from the database and aborting with 500 status code if something goes wrong
    drinks = get_long_drinks()
    if not drinks:
        abort(500)
    return jsonify({
        'success': True,
        'drink_id': drink.id,
        'drinks': drinks
    }), 201



'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''


# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False,
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''


# Starting the server
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)

