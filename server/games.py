# Library imports
import bson
from codename import codename
from datetime import datetime

# Local imports
from mongoInterface import db
import utils

def create_game(user_id):
    '''
    Creates a new game doc

    Args:
        user_id (str): The provider ID of the user creating the game

    Returns:
        tuple: A tuple containing the game ID and a status code
    '''
    # Check the user exists
    user = db.users.find_one({'provider_id': user_id})
    if not user:
        return {'error': 'User not found'}, 404

    # Construct the doc
    doc = {
        'key_phrase': codename(),
        'created_at': datetime.now(),
        'created_by': user_id,
        'updated_at': datetime.now(),
        'updated_by': user_id,
        'player1': user_id,
        'player2': None,
        'player1_moves': [],
        'player2_moves': [],
        'optimal_moves': [],
        'scores': [],
        'game_state': 'pending',
    }

    # Insert doc to mongo
    insert_result = db.games.insert_one(doc)

    return str(insert_result.inserted_id), 200

def join_game(game_id, user_id):
    '''
    Updates a game doc to include a new player
    '''
    pass

def get_games(user_id):
    '''
    Gets IDs ofall games that a user is involved in (joined or created)
    '''
    # Check user exists
    user = db.users.find_one({'provider_id': user_id})
    if not user:
        return {'error': 'User not found'}, 404

    # Get all games that the user is involved in
    games = db.games.find({'player1': user_id})

    # TODO: Enrich with actual details
    response = {
        'user': user,
        'games': [str(game['_id']) for game in games],
    }
    return utils.safe_bson(response), 200

def get_game(game_id):
    '''
    Gets the full details for a game
    '''
    game = db.games.find_one({'_id': bson.ObjectId(game_id)})
    if not game:
        return {'error': 'Game not found'}, 404

    # TODO: Enrich with actual details
    return utils.safe_bson(game), 200

def add_move(game_id, user_id, word):
    '''
    Adds a user's move to a game
    '''
    pass

def quit_game(game_id, user_id):
    '''
    Update a game state to reflect a user ended it ("gave up")
    '''
    pass
