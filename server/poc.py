# import gensim
# from gensim.models import Word2Vec
# from nltk.tokenize import word_tokenize
import numpy as np
from tqdm import tqdm

def load_glove(fpath):
    embeddings = {}
    with open(fpath, 'r', encoding='utf-8') as f:
        for line in tqdm(f):
            parts = line.strip().split()
            word = parts[0]
            vec = np.array(parts[1:], dtype=np.float32)
            embeddings[word] = vec
    return embeddings

def cos(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


glove_path = 'glove.6B.100d.txt'
glove = load_glove(glove_path)

print(glove['apple'])

E = [
    'nut',
    'spoiled',
    'sick',
    'flu',
    'cold',
    'syrup',
    'pharmacy',
    'thermometer',
    'doctor',
    'measure',
]

K = [
    'suspicion',
    'nugget',
    'chicken',
    'soup',
    'medicine',
    'pill',
    'suppository',
    'remedy',
    'temperature',
    'physician',
]


dists = []
labels = []
for a, b in zip(E, K):
    ag = glove[a]
    bg = glove[b]
    c = cos(ag, bg)
    dists.append(c)
    labels.append(f'{a}, {b}')

import matplotlib.pyplot as plt
plt.plot(dists)
plt.xticks(range(len(dists)), labels, rotation=45)
plt.show()
