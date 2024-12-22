# RAG Movie Expert
### Pet-project for testing RAG technology


### How it works:
1. Retrieves the genre and the descripton of a movie from the user.
2. The genre and the description are embedded and concatenated into a longer vector
3. Finds k nearest neighbours in a FAISS vector database.
4. Feeds those top k movies to GPT-4o-mini, together with selected genre, desctiption, and further details of the movie.
5. GPT-4o-mini returns the movie that fits the user's query the best.

### Setup:
1. Download packages from requirements.txt 
2. (Optional) run generate_embeddings.py to create a FAISS vecor database of a movie dataset 
3. Set up OpenAi and Telegram Bot keys in a .env file (TELEGRAM_BOT_TOKEN, OPENAI_API_KEY)
4. Run tg_bot.py (if in Russia, set up base_url in open_ai_api.py)
