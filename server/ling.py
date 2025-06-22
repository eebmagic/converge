import numpy as np


FPATH = 'glove.6B.100d.txt'
wordset = set()
with open(FPATH, 'r', encoding='utf-8') as f:
    for line in f:
        word = line.strip().split()[0]
        wordset.add(word)

print(f'Built wordset of {len(wordset):,} words')


def validate_word(word):
    '''
    Check a word is valid (appears in embedding set)
    '''
    return word in wordset

def cos(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def optimal_word(a, b, a_vec, b_vec):
    '''
    Find the optimal word between two words
    '''
    if a == b:
        return a

    middle = (a_vec + b_vec) / 2
    closest = None
    closest_dist = 0

    with open(FPATH, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            word = parts[0]
            if word in [a, b]:
                continue

            vec = np.array(parts[1:], dtype=np.float32)

            dist = cos(middle, vec)
            if dist > closest_dist:
                closest_dist = dist
                closest = word

    return closest

def score_words(word1, word2):
    '''
    Score two words.
    Returns:
        - the cosine similarity between the two words
        - the optimal word (word between the two guesses)
    '''
    a_vec = None
    b_vec = None

    with open(FPATH, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split()
            word = parts[0]
            if word == word1:
                a_vec = np.array(parts[1:], dtype=np.float32)
            if word == word2:
                b_vec = np.array(parts[1:], dtype=np.float32)
            
            if a_vec is not None and b_vec is not None:
                break

    if a_vec is None or b_vec is None:
        return None, None
    
    score = float(cos(a_vec, b_vec))
    optimal = optimal_word(word1, word2, a_vec, b_vec)

    return {
        'score': score,
        'optimal': optimal,
    }

