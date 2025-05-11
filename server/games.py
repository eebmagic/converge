def create_game(user_id):
    '''
    Creates a new game doc
    '''
    pass

def join_game(game_id, user_id):
    '''
    Updates a game doc to include a new player
    '''
    pass

def get_games(user_id):
    '''
    Gets IDs ofall games that a user is involved in (joined or created)
    '''
    pass

def get_game(game_id):
    '''
    Gets the full details for a game
    '''
    pass

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
