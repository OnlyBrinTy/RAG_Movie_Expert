from openai import AsyncOpenAI
from dotenv import load_dotenv
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# base_url = "https://api.proxyapi.ru/openai/v1"


class OpenAIClient:
    _instance = None

    def __new__(cls, api_key=OPENAI_API_KEY, base_url=None):
        if cls._instance is None:
            if not api_key or not isinstance(api_key, str):
                raise ValueError("API key is invalid. Please provide a valid OpenAI API key.")

            cls._instance = AsyncOpenAI(api_key=api_key, base_url=None)

        return cls._instance


openai_client = OpenAIClient()


async def get_openai_response(prompt: str, max_tokens=1024):
    response = await openai_client.chat.completions.create(
        model='gpt-4o-mini-2024-07-18',
        max_tokens=max_tokens,
        temperature=0.5,
        messages=[
            {"role": "system", "content": "You are an AI movie advisor. You help the user find a movie"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
