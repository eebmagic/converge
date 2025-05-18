import bson
import json
import os
import re
import random
import numpy as np
from tqdm import tqdm
from client import mongo_client

def safe_bson(bson_obj):
    '''
    Converts a bson object (with some non-json items) and converts it to a json object
    '''
    json_string = bson.json_util.dumps(bson_obj)
    json_obj = json.loads(json_string)

    return json_obj

# Initialize collections
db = mongo_client.wavelength
games_coll = db.games
rounds_coll = db.rounds

### Load GloVe embeddings for cosine similarity calculations and phraseID ###
def load_glove(fpath):
    embeddings = {}
    with open(fpath, 'r', encoding='utf-8') as f:
        for line in tqdm(f, desc="Loading GloVe"):
            parts = line.strip().split()
            word = parts[0]
            vec  = np.array(parts[1:], dtype=np.float32)
            embeddings[word] = vec
    return embeddings

def cos_sim(a, b):
    """
    Compute cosine similarity between two vectors a and b.
    Returns a Python float between -1.0 and 1.0.
    """
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

GLOVE_PATH = os.environ.get('GLOVE_PATH', 'glove.6B.100d.txt')
glove_embeddings = load_glove(GLOVE_PATH)

# phraseID generation
_word_pattern = re.compile(r'^[a-z]+$')
CANDIDATE_WORDS = [
    w for w in glove_embeddings.keys()
    if _word_pattern.match(w) and 3 <= len(w) <= 7
]

def generate_phraseID(max_tries=10):
    """
    Generate a phraseID not already in games_coll.
    """
    for _ in range(max_tries):
        phraseID = ' '.join(random.sample(CANDIDATE_WORDS, 3))
        if games_coll.count_documents({'phraseID': phraseID}, limit=1) == 0:
            return phraseID
    raise RuntimeError(f"Failed to generate unique phraseID after {max_tries} tries")


### Helper functions ###
def get_optimal_word(gameID, roundNumber):
    """
    For roundNumber > 1, fetch previous round's two guesses,
    compute their centroid embedding, and find the vocab word
    with highest cosine similarity to that centroid. Returns None
    if insufficient data or embeddings missing.
    """
    if roundNumber <= 1:
        return None
    prev = rounds_coll.find_one({'gameID': gameID, 'roundNumber': roundNumber - 1})
    if not prev or len(prev.get('guesses', [])) < 2:
        return None
    vecs = []
    for g in prev['guesses']:
        v = glove_embeddings.get(g['word'])
        if v is None:
            return None
        vecs.append(v)
    centroid = np.mean(vecs, axis=0)
    best_word = None
    best_sim  = -1.0
    for w, vec in glove_embeddings.items():
        sim = cos_sim(vec, centroid)
        if sim > best_sim:
            best_sim  = sim
            best_word = w
    return best_word

def compute_round_results(gameID, roundNumber):
    """
    Fetch the round doc, compute each guess's similarity to optimalWord,
    and the similarity between the two guesses (playerSim).
    Returns (entries_list, playerSim).
    """
    rd = rounds_coll.find_one({'gameID': gameID, 'roundNumber': roundNumber})
    optimal_word = rd.get('optimalWord')
    optimal_vec  = glove_embeddings.get(optimal_word)

    entries = []
    guess_vecs = []
    for guess in rd.get('guesses', []):
        w   = guess['word']
        vec = glove_embeddings.get(w)
        sim = cos_sim(vec, optimal_vec) if (vec is not None and optimal_vec is not None) else None
        entries.append({
            'userID':       guess['userID'],
            'word':         w,
            'optimalSim':   sim
        })
        guess_vecs.append(vec)

    # compute similarity between the two guess vectors
    if len(guess_vecs) == 2 and None not in guess_vecs:
        playerSim = cos_sim(guess_vecs[0], guess_vecs[1])
    else:
        playerSim = None
    return entries, playerSim


def serialize_doc(doc):
    d = doc.copy()
    d.pop('_id', None)
    return d
