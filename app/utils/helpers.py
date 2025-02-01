import requests
import os
import json
from dotenv import load_dotenv
from datetime import datetime
from googletrans import Translator
import logging

logger = logging.getLogger(__name__)

BASE_DIR = os.getenv('BASE_DIR')

USERS_FILE = os.getenv('DB_PATH')

def get_city_from_coords(latitude, longitude):
    api_key = os.getenv('OPENCAGE_API_KEY')

    url = f"https://api.opencagedata.com/geocode/v1/json?q={latitude}+{longitude}&key={api_key}&no_annotations=1"

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()
        if data['results']:

            logger.info(f"Был получен город по координатам - {data['results'][0]['components'].get('city', 'Город не найден')}")
            return data['results'][0]['components'].get('city', 'Город не найден')
        else:
            logger.warning("Город не найден")
            return 'Error'
    else:
        logger.error("Ошибка при поиске города")
        return None


# Функция для чтения данных из JSON
def read_users():
    try:
        with open(USERS_FILE, "r", encoding="utf-8") as file:
            logger.info("Пользователи получены")
            return json.load(file)
    except FileNotFoundError:
        logger.warning("Файл с пользователями не найден")
        return {}
    except json.JSONDecodeError:
        logger.warning("Проблемы с файлом")
        return {}

# Функция для записи данных в JSON
def write_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as file:
        logger.info("Данные о пользователях обновлены")
        json.dump(users, file, indent=4, ensure_ascii=False)

def get_daily_path():
    """Возвращает путь к папке для текущего дня."""
    today = datetime.now()
    year = today.strftime("%Y")
    month = today.strftime("%m")
    day = today.strftime("%d")

    # Формируем путь
    daily_path = os.path.join(BASE_DIR, year, month, day)

    # Если папки нет, создаем
    os.makedirs(daily_path, exist_ok=True)

    return daily_path

def get_users_file_path():
    """Возвращает путь к файлу users.json для текущего дня."""
    daily_path = get_daily_path()
    return os.path.join(daily_path, "users.json")

def load_data():
    """Загружает данные из users.json."""
    file_path = get_users_file_path()

    # Если файл не существует, создаем пустой JSON
    if not os.path.exists(file_path):
        with open(file_path, "w") as file:
            json.dump({}, file)

    # Читаем данные из файла
    with open(file_path, "r") as file:
        data = json.load(file)

    logger.info("Получена информация пользователей за день")

    return data

def save_data(data):
    """Сохраняет данные в users.json."""
    file_path = get_users_file_path()
    with open(file_path, "w") as file:
        logger.info("Информация о пользователях за день обновлена")
        json.dump(data, file, indent=4)

def log_user_data(user_id, calories, water_ml, burned_calories = 0):
    """
    Логирует данные о калориях и воде для пользователя.

    :param user_id: Идентификатор пользователя
    :param calories: Количество потребленных калорий
    :param water_ml: Количество выпитой воды (в мл)
    """
    data = load_data()

    # Если данных для пользователя нет, создаем запись
    if str(user_id) not in data:
        data[str(user_id)] = {"calories": 0, "water_ml": 0, 'burned_calories': 0}

    # Обновляем данные
    data[str(user_id)]["calories"] += calories
    data[str(user_id)]["water_ml"] += water_ml
    data[str(user_id)]["burned_calories"] += burned_calories

    # Сохраняем изменения
    save_data(data)

def calculate_bmr(weight, height, age, gender):
    if gender == "male":
        bmr = 88.362 + (13.397 * int(weight)) + (4.799 * int(height)) - (5.677 * int(age))
    else:
        bmr = 447.593 + (9.247 * int(weight)) + (3.098 * int(height)) - (4.330 * int(age))
    return bmr

def calculate_tdee(bmr, activity_level):
    if activity_level == "low":
        tdee = bmr * 1.2
    elif activity_level == "medium":
        tdee = bmr * 1.375
    elif activity_level == "high":
        tdee = bmr * 1.55
    elif activity_level == "very_high":
        tdee = bmr * 1.725
    else:
        tdee = bmr * 1.9
    return tdee

def calculate_goal_calories(tdee, goal):
    if goal == "loss":
        return round(tdee * 0.8)
    elif goal == "maintenance":
        return round(tdee)
    elif goal == "gain":
        return round(tdee * 1.2)
    else:
        raise ValueError("Invalid goal")

def calculate_water_goal(user_id):
    user = (read_users())[user_id]
    age = int(user["user_age"])
    weight = int(user["user_weight"])
    activity_level = user["user_activity_level"]

    if user:
        if age:
            if int(age) <= 30:
                base_water = weight * 40
            elif 30 < age <= 55:
                base_water = weight * 35
            else:
                base_water = weight * 30
        else:
            base_water = weight * 30

        if activity_level == "medium":
            base_water += 500
        elif activity_level == "high":
            base_water += 1000
        elif activity_level == "very_high":
            base_water += 1500
    else:
        raise ValueError("Не удалось получить информацию о пользователе")

    return round(base_water, 0)

async def translate_to_english(product_name: str) -> str:
    translator = Translator()
    translation = await translator.translate(product_name, src='auto', dest='en')
    logger.info(f"Текс {product_name} переведен в {translation}")
    return translation.text

def get_nutrionix_api_header():
    return {
        "x-app-id": os.getenv('NUTRIONIX_API_ID'),
        "x-app-key": os.getenv('NUTRIONIX_API_KEY'),
        "Content-Type": "application/json"
    }

def get_calories(product: str, weight: int):
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = get_nutrionix_api_header()
    data = {"query": f"{weight}g {product}"}

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        result = response.json()
        calories = result["foods"][0]["nf_calories"]
        return calories
    else:
        raise ValueError("Не удалось получить информацию о продукте")

def get_calories_goal(user_id):
    user = (read_users())[user_id]

    return int(user['user_calories_goal'])


def get_burned_calories(user_id, activity: str, duration: int):
    user = (read_users())[user_id]
    url = "https://trackapi.nutritionix.com/v2/natural/exercise"
    headers = get_nutrionix_api_header()
    data = {
        "query": f"{activity} {duration} min",
        "weight_kg": int(user['user_weight'])
    }

    response = requests.post(url, headers=headers, json=data)
    result = response.json()

    if "exercises" in result:
        return result["exercises"][0]["nf_calories"]  # Возвращаем количество сожжённых калорий
    else:
        raise ValueError(f"Не удалось получить информацию о тренировке {activity}, которая длилась {duration}")
