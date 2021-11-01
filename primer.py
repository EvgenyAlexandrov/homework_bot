# homework_api/api_praktikum.py

import requests

PRACTICUM_TOKEN = 'AQAAAABRflG_AAYckX8x0-AMXUzviOWN2Ms7OPA'
url = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
headers = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}
payload = {'from_date': 1633103140}

# Делаем GET-запрос к эндпоинту url с заголовком headers и параметрами params
homework_statuses = requests.get(url, headers=headers, params=payload)
print(homework_statuses.json().get('homeworks')[0])
