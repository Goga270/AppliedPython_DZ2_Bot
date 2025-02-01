from aiogram import types, Router
from aiogram.filters import Command
from utils import helpers
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command('get_water_norm'))
async def get_water_norm(message: types.Message):
    logger.info("Вызвана компанда /get_water_norm")
    try:
        water_goal = helpers.calculate_water_goal(str(message.from_user.id))
        await message.answer(f"С учетом ваших данных ваша дневная норма воды состовляет - {water_goal} мл")
    except ValueError as e:
        await message.answer(f"Ошибка: {e}")

@router.message(Command('get_calories_norm'))
async def get_water_norm(message: types.Message):
    logger.info("Вызвана компанда /get_calories_norm")
    user = (helpers.read_users())[str(message.from_user.id)]
    await message.answer(f"С учетом ваших данных ваша дневная норма калорий состовляет - {user['user_calories_goal']} ккал")

def register_handlers(dp):
    dp.include_router(router)