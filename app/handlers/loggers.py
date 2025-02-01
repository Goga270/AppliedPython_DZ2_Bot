from aiogram import types, Router
from aiogram.filters import Command
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from utils import helpers
import re
import logging

router = Router()
logger = logging.getLogger(__name__)

# Состояния для FSM
class WaterState(StatesGroup):
    water_ml = State()

class CaloriesState(StatesGroup):
    product = State()
    weight_grams = State()

class WorkoutState(StatesGroup):
    activity = State()
    duration = State()


@router.message(Command('log_water'))
async def log_water_command(message: types.Message,  state: FSMContext):
    logger.info("Вызвана команда /log_water")
    await message.answer(f"Введите пожалуйста, то сколько вы выпили воды в МЛ(милилитрах)")
    await state.set_state(WaterState.water_ml)

@router.message(WaterState.water_ml)
async def log_water_handler(message: types.Message, state: FSMContext):
    water_count_string = message.text
    match = re.match(r'^\d+', water_count_string.strip())
    water_count_int = 0
    if match:
        water_count_int = int(match.group(0))
        logger.info(f"Получено сколько пользоваетль выпил воды = {water_count_int}")
    else:
        logger.warning("Пользователь ввел не число")
        await message.answer(f"Введите пожалуйста, то сколько вы выпили воды в МЛ(милилитрах), достаточно одного числа!")

    helpers.log_user_data(str(message.from_user.id), 0, water_count_int)
    current_data = helpers.load_data()
    await message.answer(f"Ваши данные внесены в систему")
    logger.info(f"Данные успешно внесены в систему: water_ml = {water_count_int}")
    if str(message.from_user.id) in current_data:
        water_goal = int(helpers.calculate_water_goal(str(message.from_user.id)))
        current_water_progress = int(current_data[str(message.from_user.id)]["water_ml"])
        if current_water_progress >= water_goal:
            await message.answer(
                f"🎉 Ура! Вы выполнили норму по воде!\n"
                f"💧 Выпито: {current_water_progress} мл из {water_goal} мл.\n"
                f"Отличная работа, продолжайте в том же духе! 💪"
            )
        else:
            remaining_water = water_goal - current_water_progress
            await message.answer(
                f"📊 Прогресс:\n"
                f"💧 Вода:\n"
                f"- Выпито: {current_water_progress} мл из {water_goal} мл.\n"
                f"❗ Осталось: {remaining_water} мл до выполнения нормы.\n"
                f"Вы справитесь! Попробуйте сделать еще один глоток воды. 🚰"
            )
        await state.clear()
    else:
        logger.error("Ошибка: Пользователь не найден в системе")
        await message.answer("Ошибка: Пользователь не найден в системе")
        await state.clear()

@router.message(Command('log_calories'))
async def log_calories_command(message: types.Message,  state: FSMContext):
    logger.info("Вызвана команда /log_calories")
    await message.answer('Введите продукт который вы употребили')
    await state.set_state(CaloriesState.product)

@router.message(CaloriesState.product)
async def log_calories_product(message: types.Message,  state: FSMContext):
    product = message.text
    logger.info(f"Получен продукт который пользователь съел - {product}")
    product_en = await helpers.translate_to_english(product)
    await state.update_data(product=product_en)
    await message.answer(f'Введите сколько граммов {product} вы съели')
    await state.set_state(CaloriesState.weight_grams)

@router.message(CaloriesState.weight_grams)
async def log_calories_weight(message: types.Message,  state: FSMContext):
    data = await state.get_data()
    weight_string = message.text
    match = re.match(r'^\d+', weight_string.strip())
    weight_int = 0
    if match:
        weight_int = int(match.group(0))
        logger.info(f"Получена граммовка съеденного продукта {weight_int}")
    else:
        logger.warning("Введено не число")
        await message.answer(f"Введите пожалуйста, то сколько вы съели в граммах, достаточно одного числа!")

    if weight_int != 0:
        try:
            calories = helpers.get_calories(data['product'], weight_int)
            helpers.log_user_data(str(message.from_user.id), int(calories), 0, 0)
            current_data = helpers.load_data()
            await message.answer(f"Ваши данные внесены в систему")
            logger.info(f"Данные внесены в систему: calories = {calories}")
            if str(message.from_user.id) in current_data:
                calories_goal = helpers.get_calories_goal(str(message.from_user.id))
                curr_calories_progress = int(current_data[str(message.from_user.id)]["calories"])

                if curr_calories_progress >= calories_goal:
                    await message.answer(
                        f"🎉 Ура! Вы выполнили норму по калориям!\n"
                        f"🍔 Калорий употреблено: {curr_calories_progress} Ккалл из {calories_goal} Ккалл.\n"
                        f"Постарайтесь больше не кушать сегодня иначе поправитесь!!"
                    )
                else:
                    remaining_calories = calories_goal - curr_calories_progress
                    await message.answer(
                        f"📊 Прогресс:\n"
                        f"🍔 Клории:\n"
                        f"- Употреблено: {curr_calories_progress} Ккалл из {calories_goal} Ккалл.\n"
                        f"❗ Осталось: {remaining_calories} Ккалл до выполнения нормы.\n"
                        f"Вы справитесь!"
                    )
                await state.clear()
            else:
                logger.error("Ошибка: Пользователь не найден в системе")
                await message.answer("Ошибка: Пользователь не найден в системе")
                await state.clear()
        except ValueError as e:
            logger.error(f"Ошибка: {e}")
            await message.answer(f"Ошибка: {e}")
            await state.clear()

@router.message(Command('log_workout'))
async def log_workout_command(message: types.Message,  state: FSMContext):
    logger.info("Вызвана команда /log_workout")
    await message.answer('Введите чем вы занимались')
    await state.set_state(WorkoutState.activity)
@router.message(WorkoutState.activity)
async def log_workout_activity(message: types.Message,  state: FSMContext):
    activity = message.text
    activity_en = await helpers.translate_to_english(activity)
    logger.info(f"Получено название активности {activity}")
    await state.update_data(activity=activity_en)
    await message.answer(f"Введите сколько времени занимались в минутах")
    await state.set_state(WorkoutState.duration)

@router.message(WorkoutState.duration)
async def log_workout_duration(message: types.Message,  state: FSMContext):
    data = await state.get_data()
    dur_string = message.text
    match = re.match(r'^\d+', dur_string.strip())
    dur_int = 0
    if match:
        dur_int = int(match.group(0))
        logger.info(f"Получена длительность активности - {dur_int}")
    else:
        logger.warning("Введено не число")
        await message.answer(f"Введите пожалуйста, то сколько вы тренировались в минутах, достаточно одного числа!")


    if dur_int != 0:
        try:
            burned_cal = helpers.get_burned_calories(str(message.from_user.id), data['activity'], dur_int)
            helpers.log_user_data(str(message.from_user.id), 0, 0, burned_cal)
            current_data = helpers.load_data()
            logger.info(f"Данные успешно внесены в систему: burned_calories = {burned_cal}")
            await message.answer(f"Ваши данные внесены в систему")
            if str(message.from_user.id) in current_data:
                await message.answer(
                    f"📊 Прогресс:\n"
                    f"🏃‍♂️🔥 Активность: {data['activity']} в течении {dur_int} минут\n"
                    f"🔥🍽️ Сожжено: {burned_cal} ккал.\n"
                    f"🔥 Всего сожжено: {current_data[str(message.from_user.id)]['burned_calories']} ккал.\n"
                    f"Вы отлично поработали!"
                )
                await state.clear()
            else:
                logger.error("Ошибка: Пользователь не найден в системе")
                await message.answer("Ошибка: Пользователь не найден в системе")
                await state.clear()
        except ValueError as e:
            logger.error(f"Ошибка: {e}")
            await message.answer(f"Ошибка: {e}")


def register_handlers(dp):
    dp.include_router(router)