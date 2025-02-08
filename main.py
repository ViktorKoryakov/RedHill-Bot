# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2025 Виктор Коряков
# See LICENSE file in the project root for more details.

# [ IMPORTING / ИМПОРТ ]
import vk_api
import logging
import json
from pathlib import Path
from pytz import timezone
from os import getenv, chdir
from dotenv import load_dotenv, find_dotenv

# [ CONNECT WITH FILES / СОЕДИНЕНИЕ С ФАЙЛАМИ ]
def dump(filename: str, data: dict) -> None:
    """
    Сохраняет данные в JSON
    
    :param filename: Имя файла без ".json"
    :type filename: str

    :param data: Данные для сохранения в JSON
    :type data: dict

    :rtype: None
    """
    with open(f'{filename}.json', 'wt', encoding='utf-8') as outfile: json.dump(data, outfile, ensure_ascii=False)
    
def read_json(filename: str, default_data: dict) -> dict:
    try:
        with open(f'{filename}.json', 'rt', encoding='utf-8') as json_file: file = json.load(json_file)
    except FileNotFoundError:
        file = default_data
        dump(filename, file)
        logging.exception(f'Файл {filename}.json не обнаружен. Создаю новый файл')
    finally: return file

def get(type: str) -> dict:
    """
    Получает данные из JSON
    
    :param type: Какие данные рассчитывается получить
    :type type: str

    :rtype: dict
    """
    if type == 'users':
        filename = 'users'
        default_data = {}
    elif type == 'counters': 
        filename = 'counters'
        default_data = {"Всего сообщений": 0, "Расписание": 0, "Звонки": 0, "Контакты": 0, "Соцсети школы": 0, "Администрация школы": 0, "Счётчик дней до лета": 0, "О боте": 0, "Обновления": 0, "Благодарности": 0}
    elif type == "schedule":
        filename = 'lessons_schedule'
        default_data = {}
    elif type == 'bans':
        filename = 'bans'
        default_data = {}
    else: pass
    return read_json(filename, default_data)

def is_admin(user_id: int) -> bool:
    admins_ids = []
    for id in getenv('ADMINS_IDS').split(', '): admins_ids.append(id)
    return True if ((user_id in admins_ids) or (user_id == DEVELOPER_ID)) else False

def is_banned(user_id: int) -> bool:
    try:
        return True if user_id in get('bans') else False
    except Exception:
        logging.exception(f'Произошла ошибка при получении статуса блокировки юзера')

def set_last_word(user_id: int | str, value: str = '') -> None:
    """
    Устанавливает новое значение last_word конкретному человеку

    :param value: новое значение (нет значения - '')
    :type value: str

    :rtype: None
    """
    users = get('users')
    users[str(user_id)]['last_word'] = value
    dump("users", users)

def update_counter(counter: str) -> None:
    """
    Добавляет к выбранному счётчику 1 очко

    :param counter: Любой счётчик использований
    :type counter: str

    :rtype: None
    """

    counters = get("counters")
    try: 
        with open("counters.json", 'wt', encoding='utf-8') as json_file:
            try: counters[counter] += 1
            except KeyError: counters.update({counter: 1})
            json.dump(counters, json_file, ensure_ascii=False)
    except Exception: logging.exception(f'Не смог найти каунтер "{counter}" в counters.json. Использование команды не было засчитано')

def translate_bool(boolean: bool) -> str:
    """
    Переводит True и False в понятный обычному человеку язык

    :param boolean: значение True/False или функция, возвращающая True/False
    :type boolean: bool

    :rtype: str
    """
    return 'Да' if boolean is True else 'Нет'

def statistics() -> str:
    statistics_list: list[str] = []
    for counter, num in get('counters').items(): 
        statistics_list.append(': '.join([counter, str(num)]))
    return '\n'.join(statistics_list)

def go_to_work_dir() -> None:
    """
    Переводит работу в определённом файле в нужную директорию

    :rtype: None
    """
    
    directory = Path(__file__).parent.resolve(True).name
    path_to_dir = {
        'Test group': getenv('PATH_TO_TEST'),
        'Release group': getenv('PATH_TO_RELEASE'),
        'redhill_vkbot': getenv('PATH_TO_SERVER')
    }
    for name, path in path_to_dir.items():
        if directory == name and path:
            try:
                chdir(path_to_dir[name])
            except FileNotFoundError:
                logging.exception(f'Путь не найден \n')

# [ SETTINGS / НАСТРОЙКИ ]
go_to_work_dir()
load_dotenv(find_dotenv())
logging.basicConfig(level=logging.INFO, filename='used_commands.log', format='%(asctime)s | %(levelname)s: %(message)s', filemode='a', encoding='utf-8')
auth = vk_api.VkApi(token = getenv('TOKEN'))
moscow_tz = timezone('Europe/Moscow')
DEVELOPER_ID = int(getenv('DEVELOPER_ID'))
MAX_ACTIVITY_MEMORY = 30