import logging
import os
import requests
import telegram
import time

from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_TIME = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'

HOMEWORK_STATUSES = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена, в ней нашлись ошибки.'
}


def send_message(bot, message):
    """Отправляет сообщение."""
    bot.send_message(TELEGRAM_CHAT_ID, message)


def get_api_answer(url, current_timestamp):
    """Отправляет запрос к API домашки на эндпоинт."""
    headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
    payload = {'from_date': current_timestamp}
    try:
        homework_statuses = requests.get(url, headers=headers, params=payload)
        if homework_statuses.status_code != 200:
            logging.error('Нет ответа от сервера')
            raise Exception('Ответа нет')
    except requests.exceptions.RequestException:
        logging.error('Ошибка сети')
        raise Exception('Сетевая ошибка')
    return homework_statuses.json()


def parse_status(homework):
    """Достает данные из домашки, проверяет и возвращает сообщение."""
    status = homework[0]['status']
    verdict = HOMEWORK_STATUSES[status]
    homework_name = homework[0]['homework_name']
    if homework_name is None:
        raise Exception('Нет имени домашки')
    if verdict is None:
        logging.info(f'Вердикт: {verdict}')
        raise Exception('Нет результата')
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def check_response(response):
    """Проверяет полученный ответ на корректность,и не изменился ли статус."""
    homeworks = response.get('homeworks')
    if homeworks == []:
        logging.error('Задания списка домашки')
        raise Exception("Нет списка 'homework'")
    if not isinstance(homeworks, list):
        logging.error("Неверный формат 'homework'")
        raise Exception("Неверный формат 'homework'")
    if not homeworks:
        logging.error('Нет ключа "homeworks"')
        raise Exception('Нет ключа "homeworks"')
    status = homeworks[0]['status']
    if status not in HOMEWORK_STATUSES:
        logging.error('Статуст домашки неверен')
        raise Exception("Неправильный статус")
    return homeworks


def main():
    """Проверяет токены, запускает функции с выставлением таймера."""
    if TELEGRAM_CHAT_ID is None:
        logging.error('Нет id чата')
        raise Exception('Нет id чата')
    if TELEGRAM_TOKEN is None:
        logging.error('Нет токена бота')
        raise Exception('Нет токена бота')
    if PRACTICUM_TOKEN is None:
        logging.error('Нет токена практикума')
        raise Exception('Нет токена практикума')
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    updater = Updater(token=TELEGRAM_TOKEN)
    # current_timestamp = int(time.time())
    response = get_api_answer(ENDPOINT, 1633103140)
    homework = check_response(response)
    message = parse_status(homework)
    updater.dispatcher.add_handler(
        CommandHandler('homework',
                       send_message(bot, message))
    )
    while True:
        try:
            time.sleep(RETRY_TIME)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.error(message)
            time.sleep(RETRY_TIME)
            continue


if __name__ == '__main__':
    main()
