from sentence_transformers import SentenceTransformer
from jinja2 import Environment, BaseLoader
import faiss
import pandas as pd
import numpy as np

from open_ai_api import get_openai_response

env = Environment(loader=BaseLoader())


class MovieExpert:
    K_NEARST = 10

    genre: str
    overview: str
    movies_found: list

    def __init__(self):
        """Initialize the MovieExpert class"""
        self.model = SentenceTransformer('sentence-transformers/all-mpnet-base-v2')  # embedding model for Q&A datasets
        self.df = pd.read_csv('files/imdb_top_1000.csv')  # movie database
        self.index = faiss.read_index('files/db.index')

    def db_search(self, genre: str, overview: str):
        """Retrieval of k nearest movies out of a vector database by fusing genre and overview embeddings"""
        self.movies_found = []

        genre_emb = self.model.encode(genre + ' movie')
        description_emb = self.model.encode(overview)
        embedding = np.array([np.hstack((genre_emb, description_emb))])

        _, indices = self.index.search(embedding, self.K_NEARST)

        self.genre, self.overview = genre, overview
        self.movies_found = self.df.loc[*indices]

    async def final_choice(self, additional_info: str) -> str:
        prompt = self.prepare_prompt(additional_info)
        response = await get_openai_response(prompt)

        return response

    def prepare_prompt(self, additional_info: str) -> str:
        """Plugging variables in a template"""
        file = open('files/prompt.jinja2', 'r', encoding='utf-8')

        params = {
            "movies": self.movies_found,
            "genre": self.genre,
            "overview": self.overview,
            "add_info": additional_info,
            "k": self.K_NEARST
        }

        template = env.from_string(file.read())
        file.close()

        return template.render(**params)
