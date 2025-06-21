import uuid
import json
import os
from datetime import datetime
from datetime import timezone
import traceback
# Library imports
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

# Local imports
import users
import games

# Start server
load_dotenv()

app = Flask(__name__,
    static_folder='../frontend/build',
    static_url_path='')
CORS(app)


FILE = 'data.json'

def checkfile():
    datafile = os.path.join(os.path.dirname(__file__), FILE)
    if not os.path.exists(datafile):
        with open(datafile, 'w') as file:
            json.dump([], file)

    with open(datafile) as file:
        content = file.read()

    if not content:
        with open(datafile, 'w') as file:
            json.dump([], file)

    return datafile


def addToFile(link):
    # Create emtpy file if os.path does not exist
    datafile = checkfile()

    # Prepend to json file
    datestr = datetime.now(timezone.utc).isoformat()

    obj = {
        'idx': uuid.uuid4().hex,
        'link': link,
        'date': datestr,
    }

    try:
        data = readfile()
        data.insert(0, obj)

        with open(datafile, 'w') as file:
            json.dump(data, file)

        return True
    except Exception as e:
        print(f'failed to add to file with e', e)
        return False

def readfile():
    datafile = checkfile()
    with open(datafile) as file:
        content = json.load(file)

    return content

def deleteFromFile(idx):
    datafile = checkfile()
    try:
        data = readfile()
        data = [item for item in data if item['idx'] != idx]

        with open(datafile, 'w') as file:
            json.dump(data, file)

        return True
    except Exception as e:
        print(f'failed to delete from file with e', e)
        return False


# Serve React App
@app.route('/')
def serve():
    print(f'Serving static files from {app.static_folder}')
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/links', methods=['GET'])
def get_signin_url():
    '''
    Get all the last N links in the board.
    '''
    # Get request args
    offset = int(request.args.get('offset') or 0)
    n = int(request.args.get('n') or 10)

    # Read from the file
    data = readfile()
    payload = data[offset:offset+n]

    # Return payload
    return jsonify(payload), 200


@app.route('/add', methods=['POST'])
def login():
    '''
    POST a link to the board.
    Will add to a file.
    '''
    # Get request args
    link = request.json.get('link')

    if not link:
        return jsonify({'error': 'No link provided'}), 400

    # Try to add to the file
    try:
        success = addToFile(link)

        if not success:
            return jsonify({
                'success': False,
                'message': 'Server failed to post link',
            }), 500

        return jsonify({
            'success': True,
            'message': 'Added successully!',
        }), 200
    except Exception as e:
        print('Error posting link:', e)
        print('Full stack trace:')
        print(traceback.format_exc())
        payload = {
            'success': False,
            'message': 'Server failed to post link',
            'error': str(e),
        }
        return jsonify(payload), 500

@app.route('/delete/<idx>', methods=['DELETE'])
def delete_link(idx):
    '''
    DELETE a link from the board by its idx.
    '''
    try:
        success = deleteFromFile(idx)

        if not success:
            return jsonify({
                'success': False,
                'message': 'Server failed to delete link',
            }), 500

        return jsonify({
            'success': True,
            'message': 'Deleted successfully!',
        }), 200
    except Exception as e:
        print('Error deleting link:', e)
        return jsonify({
            'success': False,
            'message': 'Server failed to delete link',
            'error': str(e),
        }), 500

@app.route('/preview', methods=['GET'])
def get_preview():
    url = request.args.get('url')
    if not url:
        return jsonify({'error': 'No URL provided'}), 400

    try:
        preview = HLP.HyperLinkPreview(url=url)
        preview = preview.get_data()
        return jsonify(preview), 200
    except Exception as e:
        print('Error fetching preview:', e)
        return jsonify({
            'error': 'Failed to fetch preview',
            'message': str(e)
        }), 500

@app.route('/games', methods=['POST'])
def create_game():
    '''
    Create a new game
    '''
    try:
        header_data = request.headers.get('X-Custom-Data')
        user_id = json.loads(header_data).get('user')

        result, code = games.create_game(user_id=user_id)
        return jsonify(result), code
    except Exception as e:
        print('Error creating game:', e)
        return jsonify({'error': str(e)}), 500

@app.route('/games', methods=['GET'])
def get_games():
    '''
    Get all games
    '''
    try:
        header_data = request.headers.get('X-Custom-Data')
        user_id = json.loads(header_data).get('user')

        result, code = games.get_games(user_id=user_id)
        return jsonify(result), code
    except Exception as e:
        print('Error getting games:', e)
        return jsonify({'error': str(e)}), 500

@app.route('/games/<game_id>', methods=['GET'])
def get_game(game_id):
    '''
    Get a game by its id
    '''
    try:
        header_data = request.headers.get('X-Custom-Data')
        user_id = json.loads(header_data).get('user')

        result, code = games.get_game(game_id=game_id, user_id=user_id)
        return jsonify(result), code
    except Exception as e:
        print('Error getting game:', e)
        return jsonify({'error': str(e)}), 500

@app.route('/games/join', methods=['POST'])
def join_game():
    '''
    Join a game by its id
    '''
    try:
        header_data = request.headers.get('X-Custom-Data')
        user_id = json.loads(header_data).get('user')
        game_phrase = request.json.get('game_phrase')

        result, code = games.join_game(game_phrase=game_phrase, user_id=user_id)
        return jsonify(result), code
    except Exception as e:
        print('Error joining game:', e)
        return jsonify({'error': str(e)}), 500

@app.route('/users', methods=['POST'])
def create_user():
    '''
    Create a new user
    '''
    try:
        user_data = request.json
        response, code = users.create_user(user_data)
        return jsonify(response), code
    except Exception as e:
        print('Error creating user:', e)
        return jsonify({
            'error': f'Error creating user: {e}',
            'stack': traceback.format_exc()
        }), 500

@app.route('/users/<user_id>', methods=['GET'])
def get_user(user_id):
    '''
    Get a user by their id.
    '''
    try:
        response, code = users.get_user(user_id)
        return jsonify(response), code
    except Exception as e:
        print('Error getting user:', e)
        return jsonify({
            'error': f'Error getting user: {e}',
            'stack': traceback.format_exc()
        }), 500

@app.route('/users/<user_id>', methods=['PATCH'])
def update_user(user_id):
    '''
    Update a user by their id.
    '''
    try:
        changes = request.json
        response, code = users.update_user(user_id, changes)
        return jsonify(response), code
    except Exception as e:
        print('Error updating user:', e)
        return jsonify({
            'error': f'Error updating user: {e}',
            'stack': traceback.format_exc()
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 3024))
    app.run(debug=True, port=port)
