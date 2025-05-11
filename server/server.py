import os
from datetime import datetime
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from pymongo import MongoClient
import games

### Flask & Mongo setup ###
app = Flask(__name__,
    static_folder='../frontend/build',
    static_url_path='')
CORS(app)

MONGO_URI = os.environ.get('MONGO_URI', 'mongodb://localhost:27017')
mongo_client = MongoClient(MONGO_URI)
games.mongo_client = mongo_client

### Endpoints ###

# Create a new game
@app.route('/games', methods=['POST'])
def create_game():
    data   = request.get_json() or {}
    result = games.create_game(
        data.get('gameID'),
        data.get('player1ID'),
        data.get('player2ID')
    )
    if 'error' in result:
        return jsonify(result), 400
    return jsonify(result), 200

# Submit a guess (and possibly end or advance the game)
@app.route('/games/<gameID>/rounds/<int:rn>/guess', methods=['POST'])
def submit_guess(gameID, rn):
    data   = request.get_json() or {}
    result = games.submit_guess(
        gameID, rn,
        data.get('userID'),
        data.get('word', '').strip().lower()
    )
    status = result.pop('status_code', 200)
    return jsonify(result), status

# Get game state + history
@app.route('/games/<gameID>', methods=['GET'])
def get_game_state(gameID):
    result = games.get_game_state(gameID)
    if not result:
        return jsonify({'error': 'Game not found'}), 404
    return jsonify(result), 200

# End game (mark as lost)
@app.route('/games/<gameID>/end', methods=['POST'])
def end_game(gameID):
    result = games.end_game(gameID)
    if 'error' in result:
        return jsonify(result), 404
    return jsonify(result), 200

# Serve frontend
@app.route('/')
def serve():
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get('PORT', 3024)))
