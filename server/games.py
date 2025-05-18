import os
from datetime import datetime
import numpy as np
from tqdm import tqdm
import re
import random
from bson import ObjectId
from pymongo import errors, ReturnDocument
from pymongo.errors import PyMongoError
from client import mongo_client
from utils import (
    generate_phraseID,
    get_optimal_word,
    compute_round_results,
    serialize_doc,
)

# Initialize collections at module load
db = mongo_client.wavelength
games_coll = db.games
rounds_coll = db.rounds

# Index for phraseID existence check
games_coll.create_index([('phraseID', 1)], unique=True)

### Service Functions ###

# 1. Create a new game
def create_game(player1):
    '''
    Creates a new game doc
    ObjectID is generated before the insert so that it can be saved as a str without needing an update call.
    '''
    if not player1:
        return {'error': 'Missing player1ID', 'status_code': 400}
    now = datetime.utcnow()
    new_oid = ObjectId()
    phraseID = generate_phraseID()
    game = {
        '_id': new_oid,
        'gameID': str(new_oid),
        'phraseID': phraseID,
        'player1ID': player1,
        'player2ID': None,
        'currentRoundNumber': None,
        'status': 'pending',
        'createdAt': now,
        'updatedAt': now
    }
    try:
        result = games_coll.insert_one(game)
    except PyMongoError as err:
        return {
            'error': f'Failed to create game: {err}',
            'status_code': 500
        }
    if not getattr(result, 'acknowledged', False):
        return {
            'error': 'Database did not acknowledge game creation',
            'status_code': 500
        }
    return serialize_doc(game)

# 2. Join a game
def join_game(gameID, player2):
    """
    Updates a game doc to include a new player
    """
    if not all([gameID, player2]):
        return {'error': 'Missing gameID or player2ID', 'status_code': 400}

    try:
        game = games_coll.find_one(
            {'gameID': gameID},
            {'player1ID': 1, 'status': 1, '_id': 0}
        )
    except PyMongoError as e:
        return {'error': f'Failed to fetch game: {e}', 'status_code': 500}

    if not game:
        return {'error': 'Game not found', 'status_code': 404}

    if game['status'] != 'pending':
        return {
            'error': f"Cannot join: game is already '{game['status']}'",
            'status_code': 400
        }

    if player2 == game['player1ID']:
        return {
            'error': 'Cannot join your own game',
            'status_code': 403
        }

    now = datetime.utcnow()
    try:
        updated = games_coll.find_one_and_update(
            {'gameID': gameID, 'status': 'pending'},
            {'$set': {
                'player2ID': player2,
                'status': 'in_progress',
                'currentRoundNumber': 1,
                'updatedAt': now
            }},
            return_document=ReturnDocument.AFTER
        )
    except PyMongoError as e:
        return {'error': f'Failed to join game: {e}', 'status_code': 500}

    if updated is None:
        return {'error': 'Game not found when updating', 'status_code': 404}

    return serialize_doc(updated)

# 3. Add a move (and possibly end or advance the game)
def add_move(gameID, userID, word):
    if not all([gameID, userID, word]):
        return {'error':'Missing gameID, roundNumber, userID, or word', 'status_code':400}

    # Fetch game and validate existence
    try:
        game = games_coll.find_one({'gameID': gameID})
    except errors.PyMongoError as e:
        return {'error': f'Failed to fetch game: {e}', 'status_code': 500}
    if not game:
        return {'error': 'Game not found', 'status_code': 404}

    # Check status
    if game['status'] != 'in_progress':
        return {'error': f"Cannot quit: game is '{game['status']}'", 'status_code': 400}

    # Validate player
    if userID not in {game.get('player1ID'), game.get('player2ID')}:
        return {'error': 'Invalid player', 'status_code': 403}

    now = datetime.utcnow()
    roundNumber = game['currentRoundNumber']
    optimal = get_optimal_word(gameID, roundNumber)

    # Upsert round with the guess
    try:
        upsert_res = rounds_coll.update_one(
            {'gameID': gameID, 'roundNumber': roundNumber},
            {
              '$setOnInsert': {
                'gameID':      gameID,
                'roundNumber': roundNumber,
                'optimalWord': optimal,
                'stage':       'collecting',
                'startedAt':   now
              },
              '$push': {
                'guesses': {
                  'userID':    userID,
                  'word':      word,
                  'timestamp': now
                }
              }
            },
            upsert=True
        )
    except PyMongoError as e:
        return {'error': f'Failed to record guess: {e}', 'status_code': 500}
    
    if not getattr(upsert_res, 'acknowledged', False):
        return {'error': 'Database did not acknowledge guess insert', 'status_code': 500}
    
    try:
        rd = rounds_coll.find_one({'gameID': gameID, 'roundNumber': roundNumber})
    except PyMongoError as e:
        return {'error': f'Failed to load round data: {e}', 'status_code': 500}
    
    if len(rd.get('guesses', [])) < 2:
        return {'success':True,'roundStage':'collecting'}

    # Score the round
    entries, playerSim = compute_round_results(gameID, roundNumber)
    try:
        score_res = rounds_coll.update_one(
            {'gameID': gameID, 'roundNumber': roundNumber},
            {'$set': {
                'results.entries':   entries,
                'results.playerSim': playerSim,
                'stage':             'scored',
                'endedAt':           now
            }}
        )
    except PyMongoError as e:
        return {'error': f'Failed to write round results: {e}', 'status_code': 500}

    if not getattr(score_res, 'acknowledged', False):
        return {'error': 'Database did not acknowledge scoring update', 'status_code': 500}

    try:
        if same:
            updated_game = games_coll.find_one_and_update(
                {'gameID': gameID},
                {'$set': {'status': 'won', 'updatedAt': now}},
                return_document=ReturnDocument.AFTER
            )
        else:
            updated_game = games_coll.find_one_and_update(
                {'gameID': gameID},
                {
                  '$inc': {'currentRoundNumber': 1},
                  '$set': {'updatedAt': now}
                },
                return_document=ReturnDocument.AFTER
            )
    except PyMongoError as e:
        return {'error': f'Failed to update game status: {e}', 'status_code': 500}

    if updated_game is None:
        return {'error': 'Game not found when updating status', 'status_code': 404}

    return {
        'success': True,
        'roundStage': 'scored',
        'game': serialize_doc(updated_game)
    }

# 4. Get game history
def get_game(gameID):
    '''
    Gets the full details for a game
    '''
    try:
        game = games_coll.find_one({'gameID': gameID})
    except PyMongoError as e:
        return {'error': f'Failed to fetch game: {e}', 'status_code': 500}

    if not game:
        return {'error': 'Game not found', 'status_code': 404}

    try:
        rounds = list(
            rounds_coll
              .find({'gameID': gameID})
              .sort('roundNumber', 1)
        )
    except PyMongoError as e:
        return {'error': f'Failed to fetch rounds: {e}', 'status_code': 500}

    payload = serialize_doc(game)
    payload['rounds'] = [serialize_doc(r) for r in rounds]
    return payload

# 5. Quit game (mark as lost)
def quit_game(gameID, userID):
    '''
    Update a game state to reflect a user ended it ("gave up")
    '''
    # Fetch game and validate existence
    try:
        game = games_coll.find_one({'gameID': gameID})
    except errors.PyMongoError as e:
        return {'error': f'Failed to fetch game: {e}', 'status_code': 500}
    if not game:
        return {'error': 'Game not found', 'status_code': 404}

    # Check status
    if game['status'] not in ('pending', 'in_progress'):
        return {'error': f"Cannot quit: game is '{game['status']}'", 'status_code': 400}

    # Validate player
    if userID not in {game.get('player1ID'), game.get('player2ID')}:
        return {'error': 'Invalid player', 'status_code': 403}

    try:
        updated = games_coll.find_one_and_update(
            {'gameID': gameID},
            {'$set': {'status': 'lost', 'updatedAt': datetime.utcnow()}},
            return_document=ReturnDocument.AFTER
        )
    except PyMongoError as e:
        return {'error': f'Failed to quit game: {e}', 'status_code': 500}

    if updated is None:
        return {'error': 'Game not found', 'status_code': 404}

    try:
        rounds = list(
            rounds_coll
              .find({'gameID': gameID})
              .sort('roundNumber', 1)
        )
    except PyMongoError as e:
        return {'error': f'Failed to fetch rounds: {e}', 'status_code': 500}

    payload = serialize_doc(updated)
    payload['rounds'] = [serialize_doc(r) for r in rounds]
    return payload

# 6. Get user's games
def get_user_games(userID):
    '''
    Gets IDs of all games that a user is involved in (joined or created)
    '''
    try:
        cursor = games_coll.find(
            {'$or': [{'player1ID': userID}, {'player2ID': userID}]},
            {'gameID': 1, '_id': 0}
        )
    except PyMongoError as e:
        return {'error': f'Failed to fetch user games: {e}', 'status_code': 500}

    return [g['gameID'] for g in cursor]
