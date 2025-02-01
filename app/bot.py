import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from config import TOKEN
from handlers import general, get_norms, checkers
from handlers import loggers
from aiogram.types import BotCommand

logging.basicConfig(
    level=logging.DEBUG,  # Логировать всё от INFO и выше
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()  # Вывод логов в консоль (Docker их перехватит)
    ]
)

logger = logging.getLogger(__name__)

# Создание бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать взаимодействие с ботом"),
        BotCommand(command="help", description="Список доступных команд"),
        BotCommand(command="set_profile", description="Настройка профиля"),
        BotCommand(command="get_water_norm", description="Норма воды"),
        BotCommand(command="get_calories_norm", description="Норма калорий"),
        BotCommand(command="log_water", description="Ввести употребленную воду"),
        BotCommand(command="log_calories", description="Ввести употребленные калории"),
        BotCommand(command="log_workout", description="Ввести тренировку"),
        BotCommand(command="check_progress", description="Показать прогресс")
    ]
    await bot.set_my_commands(commands)

async def main():
    # Регистрация обработчиков
    general.register_handlers(dp)
    get_norms.register_handlers(dp)
    loggers.register_handlers(dp)
    checkers.register_handlers(dp)

    await set_commands(bot)
    # Запуск бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    logger.info("Бот запущен!")
    asyncio.run(main())
