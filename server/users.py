# Local imports
from mongoInterface import db
import utils

def create_user(user_data):
    '''
    Creates a new user doc.

    Args:
        user_data (dict): A dictionary containing user data. Must include the REQUIRED_FIELDS.

    Returns:
        dict: A dictionary containing the mongo id and a status code.
    '''

    # Check that required fields are provided
    if not user_data:
        return {'error': 'No user data provided'}, 400

    missing_fields = []
    REQUIRED_FIELDS = ['name', 'email', 'provider', 'provider_id', 'details']
    for field in REQUIRED_FIELDS:
        if field not in user_data:
            missing_fields.append(field)

    if missing_fields:
        return {'error': f'User obj missing required fields: {missing_fields}'}, 400

    # Check a similar user doesn't already exist
    existing_user = db.users.find_one({
        'provider_id': user_data['provider_id'],
    })
    if existing_user:
        return {'error': 'User already exists'}, 400

    # Create the user
    create_result = db.users.insert_one(user_data)
    return {'user_id': str(create_result.inserted_id)}, 200

def get_user(user_id):
    '''
    Gets a user doc
    '''
    user = db.users.find_one({
        'provider_id': user_id,
    })

    # Check the user exists
    if not user:
        return {'error': 'User not found'}, 404

    user_safe = utils.safe_bson(user)
    return user_safe, 200


def update_user(user_id, changes):
    '''
    Updates a user doc
    '''
    # Check for the user
    old_user = db.users.find_one({
        'provider_id': user_id,
    })
    if not old_user:
        return {'error': 'User not found'}, 404

    # Check any changes are being made
    if not changes:
        return {'error': 'No updates provided'}, 400

    # Check valid changes are being submitted
    BLOCKED_KEYS = ['provider_id', 'provider']
    for key in changes:
        if key in BLOCKED_KEYS:
            return {'error': f'Cannot update blocked key: {key}'}, 400

    # Check that changes object has any actual updates compared to the old user
    changes_made = False
    for key, value in changes.items():
        if old_user[key] != value:
            changes_made = True
            break
    if not changes_made:
        return {'error': 'No updates provided'}, 400

    # Update the user
    db.users.update_one({
        'provider_id': user_id,
    }, {
        '$set': changes,
    })
    return {'success': 'User updated'}, 200


# We don't need this unless a user requests to be deleted probably?
# def delete_user(user_id):
#     '''
#     Deletes a user doc
#     '''
#     pass
