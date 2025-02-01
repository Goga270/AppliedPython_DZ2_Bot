from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from aiogram import types, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from utils import helpers
import logging

router = Router()
logger = logging.getLogger(__name__)

# Состояния для FSM
class ProfileInfoState(StatesGroup):
    user_id = State()
    user_gender = State()
    user_weight = State()
    user_height = State()
    user_age = State()
    user_activity_level = State()
    user_city = State()
    user_calories_goal = State()


def get_activity_level_keyboard():
    rows = [[InlineKeyboardButton(text="Low (Менее 2000 калорий в день)", callback_data="activity_low")],
            [InlineKeyboardButton(text="Medium (2001 - 2500 калорий в день)", callback_data="activity_medium")],
            [InlineKeyboardButton(text="High (2501 - 3000 калорий в день)", callback_data="activity_high")],
            [InlineKeyboardButton(text="Very High (более 3001 калорий в день)", callback_data="activity_very_high")]]

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    return keyboard

def get_gender_keyboard():
    rows = [[InlineKeyboardButton(text="Мужчина", callback_data="gender_male")],
            [InlineKeyboardButton(text="Женщина", callback_data="gender_female")]]

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    return keyboard

def get_activity_goal_keyboard():
    rows = [[InlineKeyboardButton(text="Похудение", callback_data="weight_loss")],
     [InlineKeyboardButton(text="Поддержание", callback_data="weight_maintenance")],
     [InlineKeyboardButton(text="Набор массы", callback_data="weight_gain")]]

    # Создаем клавиатуру с кнопками
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    return keyboard

def get_location_keyboard():
    # Создаем клавиатуру с обязательным полем keyboard (список кнопок)
    location_button = KeyboardButton(text="Отправить свою локацию", request_location=True)
    no_location_button = KeyboardButton(text="Я не хочу делиться локацией")

    # Создаем разметку с клавишами и параметрами
    markup = ReplyKeyboardMarkup(
        keyboard=[[location_button, no_location_button]],  # список кнопок
        resize_keyboard=True,
        one_time_keyboard=True
    )
    return markup

@router.message(Command('start'))
async def start(message: types.Message):
    logger.info("Вызвана команда /start")
    await message.answer("Привет! Я бот, которого создал Аладинский.Г.А, я помогу вам следить за вашим здоровьем!")

@router.message(Command('set_profile'))
async def set_profile_handler(message: types.Message, state: FSMContext):
    logger.info("Вызвана команда /set_profile")
    users = helpers.read_users()
    if str(message.from_user.id) in users:
        logger.warning(f"Пользователь с id = {message.from_user.id} уже зарегестрирован в системе")
        await message.answer("Вы уже зарегистрированы в системе")
        await state.clear()
    else:
        await state.update_data(user_id= str(message.from_user.id))
        await message.answer("Введите пожалуйста ваш пол!", reply_markup=get_gender_keyboard())
        await state.set_state(ProfileInfoState.user_gender)

@router.callback_query(StateFilter(ProfileInfoState.user_gender), lambda c: c.data.startswith("gender_"))
async def set_profile_gender(callback: types.CallbackQuery, state: FSMContext):
    logger.info("Бот запросил данные о поле")
    gender = callback.data.split("_")[1]
    await state.update_data(user_gender=gender)
    await callback.message.answer("Введите пожалуйста ваш вес!")
    await state.set_state(ProfileInfoState.user_weight)

@router.message(ProfileInfoState.user_weight)
async def set_profile_weight(message: types.Message, state: FSMContext):
    logger.info("Бот запросил данные о весе")
    weight = message.text
    await state.update_data(user_weight=weight)
    await message.answer("Спасибо! Теперь введите пожалуйста ваш рост (в см)")
    await state.set_state(ProfileInfoState.user_height)

@router.message(ProfileInfoState.user_height)
async def set_profile_height(message: types.Message, state: FSMContext):
    logger.info("Бот запросил данные о росте")
    height = message.text
    await state.update_data(user_height=height)
    await message.answer("Спасибо! Теперь введите пожалуйста ваш возраст!")
    await state.set_state(ProfileInfoState.user_age)

@router.message(ProfileInfoState.user_age)
async def set_profile_age(message: types.Message, state: FSMContext):
    logger.info("Бот запросил данные о возрасте")
    height = message.text
    await state.update_data(user_age=height)
    await message.answer("Спасибо! Теперь укажите пожалуйста вашу дневную норму активности", reply_markup=get_activity_level_keyboard())
    await state.set_state(ProfileInfoState.user_activity_level)

@router.callback_query(StateFilter(ProfileInfoState.user_activity_level), lambda c: c.data.startswith("activity_"))
async def set_profile_activity_level(callback: types.CallbackQuery, state: FSMContext):
    logger.info("Бот запросил данные о активности человека")
    activity_level = callback.data.split("_")[1]
    await state.update_data(user_activity_level=activity_level)
    await callback.message.answer(
        "Привет! 🌍 Можешь отправить мне свою локацию, чтобы я мог предложить тебе город, в котором ты находишься. 🏙️\nИли выбери вариант, если не хочешь делиться локацией. Если у вы не смогли отправить локацию, то просто введите ее в сообщениях.",
        reply_markup=get_location_keyboard())
    await state.set_state(ProfileInfoState.user_city)

@router.message(StateFilter(ProfileInfoState.user_city), F.location)
async def handle_location_test1(message: types.Message, state: FSMContext):
    if message.location:
        latitude = message.location.latitude
        longitude = message.location.longitude

        # Получаем город с помощью API
        city = helpers.get_city_from_coords(latitude, longitude)

        if city:
            # Предположительный город
            await message.answer(
                f"Я думаю, ты сейчас в городе: {city}.")
            await state.update_data(user_city=city)
            await message.answer("Определись с тем чего ты хочешь?", reply_markup=get_activity_goal_keyboard())
            await state.set_state(ProfileInfoState.user_calories_goal)
        else:
            await message.answer("Не удалось определить город. Введи свой город вручную.")

@router.message(StateFilter(ProfileInfoState.user_city), F.text)
async def handle_location_test2(message: types.Message, state: FSMContext):
    if message.text != "Я не хочу делиться локацией":
        user_city = message.text
        await state.update_data(user_city=user_city)
        await message.answer(f"Ты живешь в городе {user_city}? Отлично! 🏙️ Теперь мы можем продолжить. 😊")
        await message.answer("Определись с тем чего ты хочешь?", reply_markup=get_activity_goal_keyboard())
        await state.set_state(ProfileInfoState.user_calories_goal)
    else:
        await message.answer('Введите город вручную')

# Обработка отправки локации пользователем
@router.callback_query(StateFilter(ProfileInfoState.user_city))
async def handle_location(callback: types.CallbackQuery, state: FSMContext):
    if callback.message.location:
        latitude = callback.message.location.latitude
        longitude = callback.message.location.longitude

        # Получаем город с помощью API
        city = helpers.get_city_from_coords(latitude, longitude)

        if city:
            # Предположительный город
            await callback.message.answer(
                f"Я думаю, ты сейчас в городе: {city}.")
            await state.update_data(user_city=city)
            await callback.message.answer("Определись с тем чего ты хочешь?", reply_markup=get_activity_goal_keyboard())
            await state.set_state(ProfileInfoState.user_calories_goal)
        else:
            await callback.message.answer(
                "Не удалось определить город. Попробуй отправить свою локацию еще раз или введи свой город вручную.")
    elif callback.message.text == "Я не хочу делиться локацией":
        await callback.message.answer("Окей! 😊 Напиши мне свой город, и мы продолжим.")

@router.callback_query(StateFilter(ProfileInfoState.user_calories_goal), lambda c: c.data.startswith("weight_"))
async def set_profile_activity_level(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    callback_data = callback.data.split("_")[1]
    bmr = helpers.calculate_bmr(data['user_weight'], data['user_height'], data['user_age'], data['user_gender'])
    tdee = helpers.calculate_tdee(bmr, data['user_activity_level'])
    activity_goal = helpers.calculate_goal_calories(tdee, callback_data)
    await state.update_data(user_calories_goal = int(activity_goal))
    users = helpers.read_users()
    if data['user_id'] not in users:
        users[data['user_id']] = {
            "user_gender": data['user_gender'],
            "user_weight": data['user_weight'],
            "user_height": data['user_height'],
            "user_age": data['user_age'],
            "user_activity_level": data['user_activity_level'],
            "user_city": data['user_city'],
            "user_calories_goal": activity_goal
        }
        helpers.write_users(users)
        await callback.message.answer("Спасибо за ваши данные пользователь успешно зарегистрирован в системе")
    else:
        await callback.message.reply("Вы уже зарегистрированы!")


def register_handlers(dp):
    dp.include_router(router)