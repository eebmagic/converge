import numpy as np


FPATH = 'glove.6B.100d.txt'
wordset = {}
with open(FPATH, 'r', encoding='utf-8') as f:
    for line in f:
        parts = line.strip().split()
        word = parts[0]

        if len(word) < 3:
            continue
        if not word.isalpha() or not word.isascii():
            continue

        # TODO: Filter the original dataset for this instead
        # TODO: Also filter for english words only

        vec = np.array(parts[1:], dtype=np.float32)
        wordset[word] = vec


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

    for word, vec in wordset.items():
        if word in [a, b]:
            continue

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
    a_vec = wordset[word1]
    b_vec = wordset[word2]
    
    score = float(cos(a_vec, b_vec))
    optimal = optimal_word(word1, word2, a_vec, b_vec)

    return {
        'score': score,
        'optimal': optimal,
    }

