from sentence_transformers import SentenceTransformer
import faiss
import pandas as pd
import numpy as np


model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # embedding model for Q&A datasets
df = pd.read_csv('files/imdb_top_1000.csv')  # movie database

df['Genre'] = df['Genre'] + ' movie'

# making separate embeddings for the genre and description
genre_embs = model.encode(df['Genre'])
description_embs = model.encode(df['Overview'])

# joining those embeddings together: now it's a genre-description embedding base
embeddings = np.concatenate([genre_embs, description_embs], axis=1)

index = faiss.IndexFlatL2(embeddings.shape[1])
index.add(embeddings)

faiss.write_index(index, 'files/db.index')
