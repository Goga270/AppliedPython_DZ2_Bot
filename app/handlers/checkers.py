from aiogram import types, Router
from aiogram.filters import Command
from utils import helpers
import logging

router = Router()
logger = logging.getLogger(__name__)

@router.message(Command('check_progress'))
async def check_progress_command(message: types.Message):
    logger.info("Вызвана команда /check_progress")
    user_id = str(message.from_user.id)
    current_data = helpers.load_data()
    calories_goal = helpers.get_calories_goal(user_id)
    water_goal = helpers.calculate_water_goal(user_id)
    if user_id in current_data:
        await message.answer(
            f"📊 Прогресс:\n"
            f"Вода:\n"
            f"- Выпито: {current_data[user_id]['water_ml']} мл из {water_goal} мл.\n"
            f"- Осталось: {int(water_goal) - int(current_data[user_id]['water_ml'])} мл.\n"
            f"Калории:\n"
            f"- Потреблено: {current_data[user_id]['calories']} ккал из {calories_goal} ккал.\n"
            f"- Сожжено: {current_data[user_id]['burned_calories']} ккал.\n"
            f"- Баланс: {int(current_data[user_id]['calories']) - int(current_data[user_id]['burned_calories'])} ккал.\n")
    else:
        await message.answer(f"Ошибка: Пользователь не найден в системе")

def register_handlers(dp):
    dp.include_router(router)