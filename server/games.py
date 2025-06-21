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

def join_game(game_phrase, user_id):
    '''
    Updates a game doc to include a new player
    '''
    print('inside join_game:', game_phrase)

    if not user_id:
        return {'error': 'No user id provided'}, 400
    
    if not game_phrase:
        return {'error': 'No game phrase provided'}, 400

    game, code = get_game_by_phrase(game_phrase, user_id)
    if code != 200:
        return game, code
    
    print('found game:', game)

    # If game is full, return error
    if game['player2']:
        if user_id in [game['player1'], game['player2']]:
            return utils.safe_bson(game), 200
        else:
            return {'error': 'Game is full'}, 403
    
    # If user is already in game, return error
    if user_id == game['player1']:
        return {'error': 'You cannot join your own game'}, 400

    # Update game doc to include new player
    print('game id:', game['_id'], type(game['_id']))
    usableId = bson.ObjectId(game['_id']['$oid'])
    print('usableId:', usableId, type(usableId))
    print('user_id:', user_id, type(user_id))
    result = db.games.find_one_and_update(
        {'_id': usableId},
        {'$set': {
            'player2': user_id,
            'game_state': 'in_progress',
            'updated_at': datetime.now(),
            'updated_by': user_id,
        }},
        return_document=True
    )
    print('result:', result)

    # Check that the update was successful
    if not result:
        return {'error': 'Failed to update game while joining'}, 500

    # Return the updated game
    return utils.safe_bson(result), 200

def get_games(user_id):
    '''
    Gets IDs ofall games that a user is involved in (joined or created)
    '''
    # Check user exists
    user = db.users.find_one({'provider_id': user_id})
    if not user:
        return {'error': 'User not found'}, 404

    # Get all games that the user is involved in
    games = db.games.find({
        '$or': [
            {'player1': user_id},
            {'player2': user_id}
        ]
    })

    # TODO: Enrich with actual details
    response = {
        'user': user,
        'games': [utils.safe_bson(game) for game in games],
    }

    # Enrich game objects with user details
    userCache = {}
    for game in response['games']:
        # Pull user data
        p1 = userCache.get(game['player1'], db.users.find_one({'provider_id': game['player1']}, {'_id': 0}))
        p2 = userCache.get(game['player2'], db.users.find_one({'provider_id': game['player2']}, {'_id': 0}))

        # Save to cache for other games in list
        userCache[game['player1']] = p1
        userCache[game['player2']] = p2

        # Enrich game with user details
        game['player1'] = utils.safe_bson(p1)
        game['player2'] = utils.safe_bson(p2)

    return utils.safe_bson(response), 200

def get_game(game_id, user_id):
    '''
    Gets the full details for a game
    '''
    game = db.games.find_one({'_id': bson.ObjectId(game_id)})
    if not game:
        return {'error': 'Game not found'}, 404

    if user_id != game['player1'] and user_id != game['player2']:
        return {'error': 'User not involved in game'}, 403

    # Enrich game with user details
    game['player1'] = utils.safe_bson(db.users.find_one({'provider_id': game['player1']}, {'_id': 0}))
    game['player2'] = utils.safe_bson(db.users.find_one({'provider_id': game['player2']}, {'_id': 0}))

    return utils.safe_bson(game), 200

def get_game_by_phrase(game_phrase, user_id):
    '''
    Gets a game by its key phrase
    '''
    game = db.games.find_one({'key_phrase': game_phrase})

    # If game not found, return error
    if not game:
        return {'error': 'Game not found'}, 404
    
    # If player in game, return game
    if user_id == game['player1'] or user_id == game['player2']:
        return utils.safe_bson(game), 200
    
    # If game full already and user not involved, return error
    if game['player2'] and user_id != game['player1'] and user_id != game['player2']:
        return {'error': 'Game not found'}, 403

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
