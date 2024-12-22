import asyncio
import os
import logging
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import F

from main import MovieExpert

# 1. Load environment variables from .env
load_dotenv()
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# 2. Set up logging (optional but recommended)
logging.basicConfig(level=logging.INFO)

# 3. Create Bot & Dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

movie_expert = MovieExpert()


# 4. Define Finite State Machine (FSM) States
class MovieForm(StatesGroup):
    waiting_for_genre = State()
    waiting_for_description = State()
    waiting_for_additional = State()


# 5. START COMMAND HANDLER
async def cmd_start(message: Message, state: FSMContext):
    """
    Resets the state and asks the user for the movie genre.
    """
    await state.clear()  # Clear any previous state data
    await message.answer("Welcome! Please enter the genre of a movie:")
    await state.set_state(MovieForm.waiting_for_genre)


# 6. GENRE HANDLER
async def process_genre(message: Message, state: FSMContext):
    """
    Stores the genre and asks for the description.
    """
    genre = message.text.strip()
    await state.update_data(genre=genre)

    await message.answer("Got it! Now please provide a brief description of the movie:")
    await state.set_state(MovieForm.waiting_for_description)


# 7. DESCRIPTION HANDLER
async def process_description(message: Message, state: FSMContext):
    """
    Stores the description and asks for additional descriptors.
    """
    description = message.text.strip()
    await state.update_data(description=description)

    data = await state.get_data()
    user_genre = data.get("genre", "N/A")
    user_desc = data.get("description", "N/A")

    await message.answer(
        "Thanks! Lastly, enter any additional info you'd like to add. It can be the year, cast, anything."
    )

    movie_expert.db_search(user_genre, user_desc)

    await state.set_state(MovieForm.waiting_for_additional)


# 8. ADDITIONAL DESCRIPTORS HANDLER
async def process_additional(message: Message, state: FSMContext):
    """
    Stores additional descriptors, summarizes all data,
    and sends content from 'response_text.txt'.
    """
    additional = message.text.strip()

    while movie_expert.movies_found.empty:
        await asyncio.sleep(0.1)

    response = await movie_expert.final_choice(additional)

    await message.answer(response)

    # Clear the state so the user can start fresh if they type /start again
    await state.clear()


# 9. REGISTER HANDLERS
def register_handlers():
    # Register each function with the Dispatcher and the relevant filters:
    dp.message.register(cmd_start, Command(commands=["start"]))

    # When user is in waiting_for_genre, any text triggers process_genre
    dp.message.register(process_genre, MovieForm.waiting_for_genre, F.text)

    # When user is in waiting_for_description, any text triggers process_description
    dp.message.register(process_description, MovieForm.waiting_for_description, F.text)

    # When user is in waiting_for_additional, any text triggers process_additional
    dp.message.register(process_additional, MovieForm.waiting_for_additional, F.text)


# 10. MAIN ENTRY POINT
async def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env or environment variables.")

    register_handlers()  # Register all message handlers
    logging.info("Bot is starting...")

    # Start polling
    await dp.start_polling(bot)


# 11. RUN THE BOT
if __name__ == "__main__":
    asyncio.run(main())
