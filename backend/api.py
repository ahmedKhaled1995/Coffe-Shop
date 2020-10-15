from flask import Flask, request, jsonify, abort
import json
from flask_cors import CORS

from src.database.models import db_drop_and_create_all, setup_db, Drink
from src.auth.auth import requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
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


@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(token_map, drink_id):
    # Checking if the drink exists in the db and if so, we fetch it
    drink = None
    try:
        drink = Drink.query.filter(Drink.id == drink_id).first()
        # Here we check if drink exists
        if not drink:
            abort(404)
    except():
        abort(500)
    # Getting the request body
    req_body = request.get_json()
    if req_body is None:
        abort(400)
    # Checking if the fields sent to be modified are valid
    allowed_fields_of_drink = ['id', 'title', 'recipe']
    for field in req_body:
        if field not in allowed_fields_of_drink:
            abort(422)
    # Updating the drink
    drink.title = req_body['title']
    drink.recipe = json.dumps(req_body['recipe'])
    operation_success = drink.update()
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
    }), 200


@app.route("/drinks/<int:drink_id>", methods=["DELETE"])
@requires_auth('delete:drinks')
def delete_drink(token_map, drink_id):
    # Checking if the drink exists in the db and if so, we fetch it
    drink = None
    try:
        drink = Drink.query.filter(Drink.id == drink_id).first()
        # Here we check if drink exists
        if not drink:
            abort(404)
    except():
        abort(500)
    # Getting the id of the drink that will be deleted (to return it in the response)
    id_to_return = drink.id
    # Deleting the drink
    operation_success = drink.delete()
    if not operation_success:
        abort(500)
    # Returning the response
    return jsonify({
        "success": True,
        "delete": id_to_return
    }, 200)

# Error Handling
'''
Example error handling for unprocessable entity
'''


@app.errorhandler(400)
def bad_request(error):
    return jsonify({
        'success': False,
        'error': 400,
        'message': "bad request"
    }), 400


@app.errorhandler(401)
def unauthorized(error):
    return jsonify({
        'success': False,
        'error': 401,
        'message': "Un authorized. Please authenticate!"
    }), 401


@app.errorhandler(403)
def forbidden(error):
    return jsonify({
        'success': False,
        'error': 403,
        'message': "Action forbidden!"
    }), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': 404,
        'message': "Not found"
    }), 404


@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


@app.errorhandler(500)
def server_error(error):
    return jsonify({
        'success': False,
        'error': 500,
        'message': "server error"
    }), 500


# Starting the server
if __name__ == "__main__":
    app.run(host='127.0.0.1', port=5000)

