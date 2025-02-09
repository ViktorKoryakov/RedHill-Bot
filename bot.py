# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2025 Виктор Коряков
# See LICENSE file in the project root for more details.

# [ IMPORTING / ИМПОРТ ]
import time
import datetime
import logging
import threading
import schedule
import pymorphy3
from admin_commands import *
from vk_api.longpoll import VkLongPoll, VkEventType
from widgets import get_quote
from keyboards import *
from dotenv import load_dotenv, find_dotenv
dt = datetime # Для случаев, когда лучше использовать полную версию слова, а не сокращение

# [ FUNCTIONS / ФУНКЦИИ ]
def is_date_holiday(date, holiday_type: str) -> bool:
    holidays = {
        'summer': (datetime.date(2024, 5, 27), datetime.date(2024, 9, 1)),
        'autumn': (datetime.date(2024, 10, 28), datetime.date(2024, 11, 4)),
        'winter (before New Year)': (datetime.date(2024, 12, 30), datetime.date(2024, 12, 31)),
        'winter (after New Year)': (datetime.date(2025, 1, 1), datetime.date(2025, 1, 12)),
        'spring': (datetime.date(2025, 3, 24), datetime.date(2025, 3, 31))
    }
    if holiday_type == 'any':
        for holiday_type in holidays:
            if holidays[holiday_type][0] <= date <= holidays[holiday_type][1]: return True
            continue
    return holidays[holiday_type][0] <= date <= holidays[holiday_type][1] if holiday_type in holidays else False

def automailing():
    users = get('users')
    today = f'Сегодня {dt.date.today().day} {get_rus_date("month")} {dt.date.today().year} года'
    quote = get_quote().split(' — ')
    quote_text = f'&#128173; Цитата дня: \n"{quote[0]}" \n&#128100; {quote[1]}'
    end_pattern = 'Хорошего дня! Пусть всё запланированное получится &#128521; \n- "Отключить авторассылку" - больше не получать такие сообщения'

    for user_id, user_info in users.items():
        if is_date_holiday(datetime.date.today(), 'any'): break

        if not user_info['get_automailing'] or (user_info['agreed_to_processing'] == 'Под вопросом'): continue

        try:
            if user_info['class'] != '':
                lessons = get_schedule(user_info["class"].upper(), dt.date.today())
                lessons_widget = f'&#128218; Расписание уроков для {user_info["class"].upper()} на сегодня: \n{lessons} \n&#10071; Возможны неточности. Советуем регулярно проверять классный чат и стенд "Школьная жизнь" '
                if lessons.startswith('Нет уроков'): continue
            else:
                lessons_widget = f'&#128218; Расписание уроков на сегодня: \nВы ещё не выбрали класс по умолчанию. \nЧтобы сделать это: "Расписание" -> (любой класс) -> "Выбрать классом по умолчанию"'

            greeting = f'Доброе утро, {user_info["name"]}! &#9728;' if user_info['agreed_to_processing'] else 'Доброе утро! &#9728;'
            send_msg(user_id, automailing_keyboard, f'{greeting} \n{today} \n\n{lessons_widget} \n\n{quote_text} \n\n{end_pattern}')
        except Exception: logging.exception(f'Произошла ошибка в результате отправки авторассылки пользователю')

def create_automailing():
    try:
        schedule.every().monday.at("07:15", tz = moscow_tz).do(automailing)
        schedule.every().tuesday.at("07:15", tz = moscow_tz).do(automailing)
        schedule.every().wednesday.at("07:15", tz = moscow_tz).do(automailing)
        schedule.every().thursday.at("07:15", tz = moscow_tz).do(automailing)
        schedule.every().friday.at("07:15", tz = moscow_tz).do(automailing)
        schedule.every().saturday.at("07:15", tz = moscow_tz).do(automailing)
    except Exception:
        logging.exception('Произошла ошибка при запланировании авторассылки')

    while True:
        schedule.run_pending()
        time.sleep(1)

def start_automailing():
    try:
        automailing_thread = threading.Thread(target=create_automailing)
        automailing_thread.daemon = True
        automailing_thread.start()
        print('Успешно запущена система авторассылки')
    except Exception: logging.exception('Произошла ошибка при запуске системы авторассылки')

def get_rus_date(value: str, source: str = None) -> str:
    """
    Возвращает русифицированную версию запрашиваемого компонента даты

    :param value: Компонент даты, который нужно получить (month, weekday, to_weekday)
    :type value: str

    :param source: Исходные данные (необязательно)
    :type source: str

    :rtype: str
    """
    months = {
        1: 'января',
        2: 'февраля',
        3: 'марта',
        4: 'апреля',
        5: 'мая',
        6: 'июня',
        7: 'июля',
        8: 'августа',
        9: 'сентября',
        10: 'октября',
        11: 'ноября',
        12: 'декабря'
    }

    weekdays = {
        0: 'понедельник',
        1: 'вторник',
        2: 'среда',
        3: 'четверг',
        4: 'пятница',
        5: 'суббота',
        6: 'воскресенье',
    }

    to_weekdays = {
        0: 'понедельник',
        1: 'вторник',
        2: 'среду',
        3: 'четверг',
        4: 'пятницу',
        5: 'субботу',
        6: 'воскресенье',
    }

    weekdays_reverse = {v: k for k, v in weekdays.items()}

    if (value == 'month'):
        return months.get(source if isinstance(source, int) else dt.date.today().month, '(ошибка)')
    elif (value == 'weekday'):
        return weekdays.get(source if source is not None else dt.date.today().weekday(), '(ошибка)')
    elif (value == 'to_weekday'):
        if isinstance(source, str):
            source = weekdays_reverse.get(source.lower(), None)
        return to_weekdays.get(source if source is not None else dt.date.today().weekday(), '(ошибка)')
    else: return '(ошибка)'

def get_word_form(num: int, word: str) -> str:
    """
    Получение окончания слова в зависимости от числа и падежа

    :param num: число, относительно которого ведётся расчёт окончания
    :type num: int

    :param word: слово-промпт (которое будет в результате)
    :type word: str

    :rtype: str
    """
    parsed_word = morph.parse(word)[0]
    parsed_word = parsed_word.make_agree_with_number(num)
    if num % 10 == 1 and num % 100 != 11:
        parsed_word = parsed_word.inflect({'masc'}).word
    else:
        parsed_word = parsed_word.word
    return parsed_word

def get_schedule(for_class: str, date: dt.date) -> str | bool:
    if isinstance(date, dt.datetime):
        date = date.date()

    lessons_schedule = get('schedule')
    public_holidays = {
        (4, 11): 'Нет уроков (День народного единства) &#127479;&#127482;',
        (23, 2): 'Нет уроков (День защитника Отечества) \nПоздравляем всех наших читателей с этим праздником! &#128084;',
        (8, 3): 'Нет уроков (Международный женский день) \nПоздравляем всех наших читательниц с этим праздником! &#128144;',
        (1, 5): 'Нет уроков (День труда) &#128736;',
        (9, 5): 'Нет уроков (День Победы) &#127895;',
        (12, 6): 'Нет уроков (летние каникулы + День России) &#127479;&#127482;'
    }

    school_holidays = {
        'autumn': 'Нет уроков (осенние каникулы)',
        'winter (before New Year)': f'Нет уроков (зимние каникулы) \nRed Hill поздравляет Вас с наступающим Новым {date.year+1} годом :) &#127876;',
        'winter (after New Year)': f'Нет уроков (зимние каникулы) \nRed Hill поздравляет Вас с наступившим Новым {date.year} годом :) &#127876;',
        'spring': 'Нет уроков (весенние каникулы)',
        'summer': 'Нет уроков (летние каникулы) \nRed Hill желает Вам отличного лета! &#9728;'
    }

    if (date.day, date.month) in public_holidays: return public_holidays[(date.day, date.month)]

    for holiday in school_holidays:
        if is_date_holiday(date, holiday): return school_holidays[holiday]

    return lessons_schedule[for_class][get_rus_date('weekday', date.weekday()).capitalize()]

def toggle_subscribition(id: int | str, subscribition: str) -> str:
    """
    Изменяет статус подписки на определённый тип рассылки

    :param id: ID пользователя ВКонтакте (цель)
    :type id: int | str

    :param subscribition: Тип рассылки ("mailing" / "automailing")
    :type subscribition: str

    :rtype: str
    """
    users_key = f'get_{subscribition}'
    is_enable = get('users')[str(id)][users_key]

    answer_pattern = {
        'mailing': 'рассылки',
        'automailing': 'авторассылки'
    }

    try:
        if is_enable:
            users[str(id)][users_key] = False
            end_pattern = 'выключено'
        else:
            users[str(id)][users_key] = True
            end_pattern = 'включено'
        dump('users', users)
        send_msg(id, get_profile_keyboard(id), f'&#9989; Получение {answer_pattern[subscribition]} успешно {end_pattern}.')
    except Exception:
        logging.exception(f'Ошибка при изменении статуса подписки "{subscribition}" у юзера (ID: {id})')
        send_msg(id, get_profile_keyboard(id), f'&#10060; Произошла ошибка при изменении статуса подписки. Разработчик уже уведомлён о проблеме. \nПожалуйста, попробуйте позже')
    finally: personal_account()

def is_spammer(user_id: int) -> bool:
    if 'activity' not in users[str(user_id)]:
        users[str(user_id)]['activity'] = []
    if 'has_antispam_warning' not in users[str(user_id)]:
        users[str(user_id)]['has_antispam_warning'] = False

    now = time.time()
    activity = users[str(user_id)]['activity']
    has_warning = users[str(user_id)]['has_antispam_warning']
    activity.append(now)
    activity = [timecode for timecode in activity if now - timecode <= 10] # Удаление сообщений старше 10 секунд
    users[str(user_id)]['activity'] = activity[-MAX_ACTIVITY_MEMORY:] # Выборка не более MAX_ACTIVITY_MEMORY сообщений (настройка в main.py)

    if len(activity) > 5: # Если 5+ сообщений за 10 секунд
        if not has_warning: # Если нет предупреждения, дать
            send_msg(sender, 0, f'Слишком быстро! \nПовторите попытку через несколько секунд')
            users[str(user_id)]['has_antispam_warning'] = True
        dump('users', users)
        return True # Не продолжать обработку команды

    if has_warning: # Если предупреждение есть, сбросить
        users[str(user_id)]['has_antispam_warning'] = False
    dump('users', users)
    return False # Продолжить обработку команды

# [ COMMANDS / КОМАНДЫ ]
def home_page():
    set_last_word(sender)
    send_msg(sender, 0, 'Главное меню \n\n&#10052; Бот в стадии частичной заморозки \n"О частичной заморозке" - подробнее')

def until_summer():
    set_last_word(sender)
    update_counter('Счётчик дней до лета')
    summer = moscow_tz.localize(dt.datetime(2025, 6, 1, 0, 0, 0)) # Временная метка начала лета
    now = dt.datetime.now(moscow_tz)

    tdelta = summer - now  # Первичный расчёт времени
    if now > summer: # Если срок прошёл
        summer = summer.replace(year = summer.year + (now.year - summer.year + 1)) # Меняем год на следующий
        tdelta = summer - now # Повторный расчёт времени
    hours, remainder = divmod(tdelta.seconds, 3600) # Рассчитываем часы и остаток в секундах
    minutes, seconds = divmod(remainder, 60) # Рассчитываем минуты и оставшиеся секунды
    remain_time = dt.time(hours, minutes, seconds).strftime('%H:%M:%S')

    send_msg(sender, 0, f'До лета {summer.year} {get_word_form(tdelta.days, "осталось")}: {tdelta.days} {get_word_form(tdelta.days, "день")}, {remain_time}')

def contacts_page():
    set_last_word(sender)
    update_counter('Контакты')
    send_msg(sender, contacts, f'Основная информация о школе: \n{"—"*10}\n• Полное наименование: Муниципальное бюджетное общеобразовательное учереждение "Средняя общеобразовательная школа с углублённым изучением отдельных предметов №47 города Кирова" \n• Сокращённое наименование: МБОУ СОШ с УИОП №47 г. Кирова \n• Почтовый адрес: 610050, г. Киров, ул. Андрея Упита, д. 9 \n• E-mail: sch47@kirovedu.ru \n\n• Официальный сайт: https://sch47-kirov.gosuslugi.ru/ \n• &#128214; Электронный дневник - https://one.43edu.ru \n• &#128187; [id{DEVELOPER_ID}|Разработчик бота] \n\n• &#128188; "Администрация" - информация об администрации и службах школы \n• &#128241; "Соцсети" - информационные площадки школы \n• &#9000; "Помочь боту" - как внести вклад в развитие бота \n\n&#127969; "Домой" - вернуться на главную страницу')

def about_bot_page():
    set_last_word(sender)
    update_counter('О боте')
    send_msg(sender, about_bot, f'Информация о RedHill боте \n\n&#10052; С 05.02.25 бот в стадии частичной заморозки \n\n• &#127874; День рождения бота - 1 октября 2023 года \n• &#128187; Идея и первичная разработка - [id{DEVELOPER_ID}|Виктор Коряков] \n&#129309; При поддержке администраторов Red Hill и неравнодушных людей \n\n• &#9000; "Помочь боту" - как внести свой вклад в развитие бота \n• &#127381; "Обновления" - информация о последнем обновлении \n• &#129782; "Благодарности" - люди, внесшие свой вклад в развитие бота')

def personal_account():
    set_last_word(sender, 'личный кабинет')
    if user_info['agreed_to_processing'] is True:
        send_msg(sender, get_profile_keyboard(sender), f'[ Личный кабинет ] \n• &#128290; ID: {sender} \n• &#9745; Cогласие на обработку персональных данных: {translate_bool(user_info["agreed_to_processing"])} \n• &#129706; Имя и фамилия: [id{sender}|{user_info["name"]} {user_info["surname"]}] \n• &#129703; Отслеживаемый класс: {user_info["class"]} \n• &#128200; Написано сообщений: {user_info["message_counter"]} \n• &#128229; Получение рассылки: {translate_bool(user_info["get_mailing"])} \n• &#128229; Получение авторассылки: {translate_bool(user_info["get_automailing"])} \n\n- "Удалить/собрать данные" - Дать согласие/отказаться от обработки некоторых данных \n- "Отключить/включить рассылку" - отписаться/подписаться на рассылку \n- "Отключить/включить авторассылку" - отписаться/подписаться на утреннюю авторассылку')
    else: send_msg(sender, get_profile_keyboard(sender), f'[ Личный кабинет ] \n• &#128290; ID: [id{sender}|{sender}] \n• &#9745; Cогласие на обработку персональных данных: {translate_bool(user_info["agreed_to_processing"])} \n• &#129703; Отслеживаемый класс: {user_info["class"]} \n• &#128200; Написано сообщений: {user_info["message_counter"]} \n• &#128229; Получение рассылки: {translate_bool(user_info["get_mailing"])} \n• &#128229; Получение авторассылки: {translate_bool(user_info["get_automailing"])} \n\n- "Собрать/удалить данные" - Дать согласие/отказаться от обработки некоторых данных \n- "Отключить/включить рассылку" - отписаться/подписаться на рассылку \n- "Отключить/включить авторассылку" - отписаться/подписаться на утреннюю авторассылку')

# [ SETTINGS / НАСТРОЙКИ ]
load_dotenv(find_dotenv())
go_to_work_dir()
logging.basicConfig(level=logging.INFO, filename='used_commands.log', format='%(asctime)s | %(levelname)s: %(message)s', filemode='a', encoding='utf-8')
longpoll = VkLongPoll(auth)
morph = pymorphy3.MorphAnalyzer()
# start_automailing()
logging.info('\nПерезагрузка бота успешно завершена\n')

# [ WORK / РАБОТА ]
for event in longpoll.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
        received_message = event.text
        received_message = received_message.lower()
        sender = event.user_id
        users = get('users')
        if str(sender) not in list(users.keys()):
            users.update({str(sender): {"agreed_to_processing": "Под вопросом",
                                            "name": "",
                                            "surname": "",
                                            "class": "",
                                            "choosen_class": "",
                                            "last_word": "",
                                            "message_counter": 1,
                                            "permissions": [],
                                            "activity": [],
                                            "has_antispam_warning": False,
                                            "get_mailing": True,
                                            "get_automailing": True}})
        else: users[str(sender)]['message_counter'] += 1
        dump("users", users)

        if is_banned(sender):
            if 'banned' not in users[str(sender)]['permissions']:
                users[str(sender)]["permissions"].append("banned")
                dump('users', sender)
            ban_info = get('bans')[sender]
            send_msg(sender, for_banned, f'&#10060; Вы были заблокированы администратором {ban_info["punisher"]} по причине "{ban_info["reason"]}". \nЕсли Вы считаете, что это ошибка - пожалуйста, обратитесь к [id{DEVELOPER_ID}|разработчику]')
            continue

        if is_spammer(sender): continue

        user_info = users[str(sender)]
        last_word = user_info['last_word']
        update_counter('Всего сообщений')

        # [ COMMANDS / КОМАНДЫ ]
        if (user_info['agreed_to_processing'] == "Под вопросом") and ((last_word in ['', 'согласие на обработку персональных данных']) and (received_message not in ['разрешить (1)', '1', '1)', '1.', '(1)', '[1]', 'разрешить', 'да', 'запретить (2)', '2', '2)', '2.', '(2)', '[2]', 'запретить', 'нет'])):
            if is_admin(sender): users[str(sender)]["permissions"].append("admin")
            users[str(sender)]['last_word'] = 'согласие на обработку персональных данных'
            dump("users", users)
            send_msg(sender, consent_to_processing, f'Здравствуйте! Добро пожаловать в наше сообщество! &#128075; \n\n&#128221; Чтобы начать пользоваться ботом, нам нужно ваше разрешение на сбор и обработку некоторых персональных данных. Это поможет улучшить его работу. \n&#128196; Какие данные собираются: \n• ID пользователя ВКонтакте (необходимо для отправки сообщений, отказаться нельзя) \n• Имя и фамилия пользователя ВКонтакте \n\n&#9745; В случае отказа некоторые функции бота могут быть недоступны. Вы в любой момент можете отозвать своё разрешение, написав [id{DEVELOPER_ID}|разработчику]. \n\n&#128214; Полезные ссылки: \n• Политика конфиденциальности: https://dev.vk.com/ru/privacy-policy \n• Пользовательское соглашение: https://dev.vk.com/ru/user-agreement \n\nРазрешаете сбор и обработку персональных данных? \n[1] Да \n[2] Нет')
        elif (user_info['agreed_to_processing'] == "Под вопросом") and (last_word == 'согласие на обработку персональных данных') and (received_message in ['запретить (2)', '2', '2)', '2.', '(2)', '[2]', 'нет', 'запретить']):
            users[str(sender)]['agreed_to_processing'] = False
            users[str(sender)]['last_word'] = ''
            dump("users", users)
            send_msg(sender, 0, 'Принял, когда будете готовы на сбор и обработку персональных данных - зайдите в "Личный кабинет" и нажмите на "Собрать данные". \nВам предоставлен ограниченный доступ к функционалу бота (некоторые функции могут работать некорректно) \n\nВы на главной странице. Для навигации можете использовать кнопки в меню. Приятного пользования нашим ботом и хорошего дня! &#9728;')
        elif (user_info['agreed_to_processing'] == "Под вопросом") and (last_word == 'согласие на обработку персональных данных') and (received_message in ['разрешить (1)', '1', '1)', '1.', '(1)', '[1]', 'да', 'разрешить']):
            users[str(sender)]['agreed_to_processing'] = True
            users[str(sender)]['name'] = auth.method('users.get', {'user_ids': sender})[0]['first_name']
            users[str(sender)]['surname'] = auth.method('users.get', {'user_ids': sender})[0]['last_name']
            users[str(sender)]['last_word'] = ''
            dump("users", users)
            send_msg(sender, 0, 'Вы подтвердили своё согласие на сбор и обработку персональных данных. Спасибо! \nВы всегда можете удалить свои персональные данные из системы в "Личном кабинете". \n\nВы на главной странице. Для навигации можете использовать кнопки в меню. Приятного пользования нашим ботом и хорошего дня! &#9728;')

        else:
            logging.info(f'{sender} написал "{received_message}"')

            if handle_admin_command(sender, last_word, received_message) is not False: pass
            elif received_message in ['начать', 'старт', 'start', 'хелп', 'help', 'помощь', 'команды']:
                set_last_word(sender)
                send_msg(sender, 0, '&#10052; С 05.02.25 бот в стадии частичной заморозки \n\nСписок команд: \n• Расписание - узнать расписание уроков \n• О частичной заморозке - как внести свой вклад в развитие бота \n• Звонки - расписание звонков \n• Контакты - основная информация \n• Соцсети - информационные площадки школы \n• Личный кабинет - панель управления данными \n• Обновления - список изменений \n• Благодарности - люди, внёсшие свой вклад в развитие бота \n• До лета - счётчик дней до лета \n• Главное меню - главная страница \n\nПриятного пользования нашим ботом!')
            elif received_message in ['расписание', 'уроки']:
                set_last_word(sender, 'расписание (главная страница)')
                # send_msg(sender, get_choosing_schedule_keyboard(sender), f'Для какого класса Вы хотите узнать расписание (например, 8Г)? \n\n&#10071; Возможны ошибки. Писать [id{DEVELOPER_ID}|разработчику] \n&#10071; Возможны единоразовые изменения в расписании. Отслеживайте стенд "Школьная жизнь" и читайте классный чат')
                send_msg(sender, get_choosing_schedule_keyboard(sender), f'Для какого класса Вы хотите узнать расписание (например, 8Г)? \n\n&#9999; Актуальность расписания: \n• 1 классы - &#10060; \n• 2 классы - &#10060; \n• 3 классы - &#10060; \n• 4 классы - &#10060; \n• 5 классы - &#10060; \n• 6 классы - &#10060; \n• 7 классы - &#10060; (&#9989; 7А) \n• 8 классы - &#10060; (&#9989; 8Г) \n• 9 классы - &#10060; (&#9989; 9В) \n• 10 классы - &#10060; \n• 11 классы - &#10060; \nХотите обновить расписание? Прочтите это - https://github.com/ViktorKoryakov/RedHill-Bot/blob/main/Памятка%20по%20переносу%20расписания.md \n\n&#10071; Возможны единоразовые изменения в расписании. Отслеживайте стенд "Школьная жизнь" и читайте классный чат')
            elif received_message in ['главное меню', 'домой', 'вернуться в главное меню', 'в главное меню']: home_page()
            elif received_message in ['до лета', 'счётчик дней до лета', 'лето через', 'когда лето', 'лето когда', 'жду лето', 'хочу лета', 'хочу лето', 'жду лета', 'сколько осталось до лета', 'сколько дней до лета', 'через сколько лето', 'через сколько дней лето']:
                until_summer()
            elif received_message in ['помочь боту', 'помочь redhill', 'помочь редхилу', 'помочь redhill-боту', 'помочь редхилл-боту', 'помочь редхил-боту', 'помочь redhill боту', 'помочь редхилл боту', 'помочь редхил боту', 'внести вклад', 'изменить расписание', 'стать разработчиком', 'информация о заморозке', 'заморозка', 'информация о частичной заморозке', 'инфа о заморозке', 'о заморозке', 'о частичной заморозке', 'инфа о частичной заморозке', 'частичная заморозка', 'почему бота заморозили']:
                send_msg(sender, partial_frost, f'&#8252; Информация о частичной заморозке &#8252; \n{"—"*10} \n• &#128187; Исходный код (помочь продукту): https://github.com/ViktorKoryakov/RedHill-Bot \n• &#9999; Как изменить расписание: https://github.com/ViktorKoryakov/RedHill-Bot/blob/main/Памятка%20по%20переносу%20расписания.md \n• &#10052; Начало частичной заморозки: 05.02.2025 \n\n&#128210; Вопрос-ответ \n&#10067; Почему RedHill Бот был частично заморожен? \n&#10069; В связи с возникшими затруднениями (нехватка времени, отсутствие мотивации, проблемы с разработкой) было принято решение частично заморозить продукт, но не закрывать его насовсем \n&#10067; Что значит "частичная заморозка"? \n&#10069; Бот продолжает функционировать, но его разработка приостанавливается на неопределённый срок, а код публиуется в открытый доступ для возможности самостоятельно вносить изменения. Никаких крупных обновлений, только мелкие изменения от сообщества \n&#10067; Что будет дальше? \n&#10069; До тех пор, пока это возможно и имеет смысл, бот будет работать. В ином случае либо разработка возобновляется, либо бот перестаёт существовать вовсе \n&#10067; Как я могу помочь в поддержке бота? \n&#10069; Перейдите на страницу с исходным кодом бота (ссылка выше) и в описании прочтите пункт "Как можно помочь" \n&#10067; Могу я стать новым разработчиком бота? \n&#10069; [id{DEVELOPER_ID}|Напишите] текущему разработчику')
            elif received_message in ['о боте', 'about bot', 'about the bot', 'about a bot', 'инфа о боте', 'информация о боте', 'команда проекта', 'команда продукта', 'назад (о боте)']:
                about_bot_page()
            elif received_message in ['информационные площадки школы', 'соцсети', 'соцсети школы']:
                set_last_word(sender)
                update_counter('Соцсети школы')
                send_msg(sender, social_networks, f'Информационные площадки школы: \n{"—"*10} \n• Red Hill в ВКонтакте - https://vk.com/redhill47 \n• Red Hill в Одноклассниках - https://ok.ru/group/70000002346199 \n• 47 высота - https://vk.com/ssc_47height \n• Музей "Светлица" - https://vk.com/svetlitsamuseeum \n• Бессмертный полк 47 - https://vk.com/bessmertniypolk47 \n• Библиотека школы - https://vk.com/club192165194 \n\n&#8505; "Назад (контакты)" - вернуться в контакты школы \n&#127969; "Домой" - вернуться в главное меню')
            elif received_message in ['контакты', 'назад (контакты)', 'инфа', 'информация']: contacts_page()
            elif received_message in ['подготовка к школе', 'подготовка', 'в первый раз в первый класс', 'как подготовиться к школе', 'скоро в школу', 'первый раз в первый класс']:
                set_last_word(sender)
                send_msg(sender, 0, f'&#127891; По вопросам, связанным с начальной школой и подготовкой к ней, обращайтесь к [id221574947|Шишкиной Светлане Леонидовне], куратору начальных классов. Она сможет ответить на интересующие Вас вопросы. \n&#9742; Также Вы всегда можете позвонить Светлане Леонидовне по номеру +7(8332)227-453')
            elif received_message in ['администрация', 'администрация и службы школы', 'службы школы']:
                set_last_word(sender)
                update_counter('Администрация школы')
                send_msg(sender, administration, f'Администрация и службы школы \n{"—"*10}\n Директор - Кодачигов Владимир Леонидович \nСекретарь учебной части - Орлова Дарья Викторовна \n[ Телефон: 22-74-50 ] \n\n Заместители директора по учебной работе: \n• Шишкина Светлана Леонидовна - куратор 1-4 классов \n• Жукова Ольга Владимировна - куратор 5, 11 классов \n• Черепанова Наталья Сергеевна - куратор 6 классов \n• Краева Ирина Аркадьевна - куратор 7-8 классов \n• Кокорина Екатерина Валерьевна - куратор 9 классов \n• Широкова Татьяна Владимировна - куратор 10 классов \n[ Телефон: 22-74-53 ] \n\nЗаместитель директора по воспитательной работе \n• Жукова Ольга Владимировна \n[ Телефон: 22-74-53 ] \n\nСоветники директора по воспитательной работе: \n• Половникова Алеся Александровна - старшие классы \n• Маркевич Надежда Александровна - младшие классы \n[ Телефон: 22-74-53 ] \n\nПедагог-библиотекарь \n• Ботвина Надежда Владимировна \n[ Телефон: 22-74-53 ] \n\nЗаместитель директора по административно-хозяйственной части: \n• Cчастливцева Любовь Юрьевна \n[ Телефон: 22-74-51 ] \n\nГлавный бухгалтер: \n• Мухачева Елена Анатольевна \n[ Телефон: 22-74-52 ] \n\nМедицинский работник - Ефимова Елена Витальевна \nСоциальный педагог - Громова Людмила Михайловна \nУчитель-логопед - Булычёва Валентина Петровна \nПедагоги-психологи - Караваева Мария Анатольевна, Каргапольцева Светлана Михайловна')
            elif (received_message in ['обновления', 'апдейты', 'upd', 'upds', 'апд', 'апдз', 'апдс', 'обновления бота', 'обновление бота']):
                set_last_word(sender)
                update_counter('Обновления')
                send_msg(sender, back_to_about_bot, f'Версия 2.1.13 \nДата обновления: 05.02.2025 \n\n• &#9889; Бот переходит в стадию частичной заморозки \n• По всему боту были добавлены упоминания о новом статусе бота, появились ссылки на открытый код бота \n• Вернули шкалу готовности расписания \n• Крупные и мелкие технические изменения \n\nНашли баг/ошибку/недоработку или у Вас есть идея/отзыв? \nСообщите тут - https://github.com/ViktorKoryakov/RedHill-Bot/issues')
            elif received_message in ['credits', 'благодарности']:
                set_last_word(sender)
                update_counter('Благодарности')
                send_msg(sender, back_to_about_bot, 'Разработчик бота выражает искреннюю благодарность людям, которые внесли свой вклад в развитие бота \n\n• Даниил А. \n• Александр К. \n• Ольга Ж. \n• Яша Л. \n• Егор Д. \n• Татьяна Ф. \n• Татьяна Ш. \n• Дарья З.')
            elif received_message in ['звонки', 'расписание звонков', 'назад (расписание звонков)']:
                set_last_word(sender, 'звонки')
                update_counter('Звонки')
                send_msg(sender, bells, 'Выберите расписание звонков, которое Вы хотите узнать: \n\n[1] Будние дни \n[2] По субботам \n[3] 1 классы')
            elif received_message in ['личный кабинет', 'кабинет', 'мой кабинет', 'обо мне', 'информация обо мне', 'инфа обо мне']: personal_account()
            elif received_message in ['отключить авторассылку', 'выключить авторассылку', 'отписаться от авторассылки', 'отказаться от авторассылки', 'включить авторассылку', 'подключить авторассылку', 'подписаться на авторассылку', 'согласиться на авторассылку']:
                toggle_subscribition(sender, "automailing")
            elif received_message in ['отключить рассылку', 'выключить рассылку', 'отписаться от рассылки', 'отказаться от рассылки', 'включить рассылку', 'подключить рассылку', 'подписаться на рассылку', 'согласиться на рассылку']:
                toggle_subscribition(sender, "mailing")
            elif received_message in ['удалить мои данные', 'удалите мои данные', 'удалить данные', 'отказаться от обработки некоторых данных']:
                if user_info['agreed_to_processing'] is True:
                    set_last_word(sender, 'подтверждение удаления данных')
                    send_msg(sender, unprocessing_confirm, f'&#8252; Внимание! \nВы собираетесь отказаться от сбора и обработки персональных данных. Несколько нюансов: \n\n• В случае подтверждения некоторые функции бота могут работать некорректно \n• Нажимая на кнопку "Подтвердить", Вы удалите из базы свои имя и фамилию пользователя ВКонтакте ({user_info["name"]} {user_info["surname"]}) \n• Удалить Ваш ID пользователя ВКонтакте нельзя, поскольку он используется для отправки сообщений \n• Вы можете снова включить сбор и обработку данных, командой "Собрать данные" в личном кабинете')
                else:
                    send_msg(sender, get_profile_keyboard(sender), '&#10060; У Вас уже отключен сбор и обработка персональных данных.')
                    personal_account()
            elif received_message in ['собрать данные', 'дать согласие на обработку некоторых данных', 'дать согласие на сбор и обработку некоторых данных', 'дать согласие на сбор и обработку персональных данных']:
                try:
                    if user_info['agreed_to_processing'] is False:
                        users[str(sender)]['agreed_to_processing'] = True
                        users[str(sender)]['name'] = auth.method('users.get', {'user_ids': sender})[0]['first_name']
                        users[str(sender)]['surname'] = auth.method('users.get', {'user_ids': sender})[0]['last_name']
                        dump('users', users)
                        send_msg(sender, get_profile_keyboard(sender), '&#9989; Сбор и обработка персональных данных произведены успешно.')
                    else:
                        send_msg(sender, get_profile_keyboard(sender), '&#10060; Ваши персональные данные уже собираются и обрабатываются.')
                except Exception:
                    logging.exception(f'Ошибка при сборе данных у юзера')
                    send_msg(sender, get_profile_keyboard(sender), f'&#10060; Произошла ошибка при сборе данных. Разработчик уже уведомлён о проблеме. \nПожалуйста, попробуйте позже')
                finally: personal_account()
            else:

                # [ ACTIONS FOLLOWING A SPECIFIC COMMAND / ДЕЙСТВИЯ, ИДУЩИЕ ПОСЛЕ ОПРЕДЕЛЁННОЙ КОМАНДЫ ]
                if last_word != '':
                    if last_word == 'расписание (главная страница)':
                        # update_counter('Расписание')
                        lessons_schedule = get('schedule')
                        if received_message.upper() in list(lessons_schedule.keys()):
                            choosen_class = received_message.upper()
                            users[str(sender)]["choosen_class"] = choosen_class
                            users[str(sender)]['last_word'] = 'расписание (выбор дня недели)'
                            dump("users", users)
                            send_msg(sender, get_schedule_keyboard(sender), f'Выбран {choosen_class} класс. \n- "Назад" - если ошиблись. \n\nНа какой день недели Вы хотите узнать расписание?')
                        else:
                            send_msg(sender, get_choosing_schedule_keyboard(sender), 'Извините, я не смог распознать введённый Вами класс. Попробуйте ещё раз (например, 8Г)')
                    elif last_word == 'расписание (выбор дня недели)':
                        choosen_class = user_info["choosen_class"]
                        weekday = get_rus_date('weekday')
                        month = get_rus_date('month')
                        if (received_message in ['сегодня']):
                            if (weekday == 'воскресенье'):
                                send_msg(sender, get_schedule_keyboard(sender), f'Cегодня {weekday}, {dt.date.today().day} {month} \nРасписание на воскресенье для {choosen_class}: \n{"—"*10} \nВыходной день. Хорошего отдыха!')
                            else:
                                send_msg(sender, get_schedule_keyboard(sender), f'Cегодня {weekday}, {dt.date.today().day} {month} \nРасписание на {get_rus_date("to_weekday")} для {choosen_class}: \n{"—"*10} \n{get_schedule(choosen_class, dt.date.today())}')
                        elif (received_message in ['завтра']):
                            tomorrow = dt.date.today()+dt.timedelta(days=1)
                            tomorrow_weekday = get_rus_date('weekday', tomorrow.weekday())
                            tomorrow_month = get_rus_date('month', tomorrow.month)
                            if (tomorrow_weekday == 'воскресенье'):
                                send_msg(sender, get_schedule_keyboard(sender), f'Cегодня {weekday}, {dt.date.today().day} {month} \nРасписание на воскресенье, {tomorrow.day} {tomorrow_month}, для {choosen_class}: \n{"—"*10} \nВыходной день. Хорошего отдыха!')
                            else:
                                send_msg(sender, get_schedule_keyboard(sender), f'Cегодня {weekday}, {dt.date.today().day} {month} \nРасписание на {get_rus_date("to_weekday", tomorrow_weekday)}, {tomorrow.day} {tomorrow_month}, для {choosen_class}: \n{"—"*10} \n{get_schedule(choosen_class, tomorrow)}')
                        elif (received_message in ['понедельник', 'вторник', 'среда', 'четверг', 'пятница', 'суббота']):
                            lessons_schedule = get('schedule')
                            send_msg(sender, get_schedule_keyboard(sender), f'Cегодня {weekday}, {dt.date.today().day} {month} \nРасписание на {get_rus_date("to_weekday", received_message)} для {choosen_class}: \n{"—"*10} \n{lessons_schedule[choosen_class][received_message.capitalize()]}')
                        elif (received_message == 'назад'):
                            users[str(sender)]['last_word'] = 'расписание (главная страница)'
                            users[str(sender)]["choosen_class"] = ""
                            dump("users", users)
                            send_msg(sender, get_choosing_schedule_keyboard(sender), 'Вы вернулись обратно \nДля какого класса Вы хотите узнать расписание (например, 8Г)?')
                        elif (received_message == 'выбрать классом по умолчанию'):
                            users[str(sender)]['class'] = choosen_class
                            dump('users', users)
                            send_msg(sender, get_schedule_keyboard(sender), f'&#9989; Вы выбрали "{choosen_class}" как класс по умолчанию \n- "Отменить класс по умолчанию" - отменить выбор \n\nНа какой день недели Вы хотите узнать расписание?')
                        elif (received_message == 'отменить класс по умолчанию'):
                            users[str(sender)]['class'] = ''
                            dump('users', users)
                            send_msg(sender, get_schedule_keyboard(sender), f'&#9989; Вы отменили выбор класса "{choosen_class}" как класса по умолчанию \n- «Выбрать классом по умолчанию» - обратное действие \n\nНа какой день недели Вы хотите узнать расписание?')
                        else:
                            send_msg(sender, get_schedule_keyboard(sender), f'Извините, я Вас не понял. Выбран {choosen_class} класс. \n- "Назад" - если ошиблись \nНа какой день недели Вы хотите узнать расписание (например, "Сегодня" или "Суббота")? \n\nНашли ошибку в расписании? Напишите об этом [id{DEVELOPER_ID}|разработчику]')
                    elif (last_word == 'звонки'):
                        if received_message in ['1', 'по будням', 'будни', 'будние дни']:
                            send_msg(sender, bells, f'Расписание звонков в будние дни: \n{"—"*10} \n1 урок - 8:00-8:40 (перемена 10 минут) \n2 урок - 8:50-9:30 (перемена 10 минут) \n3 урок - 9:40-10:20 (перемена 10 минут) \n4 урок - 10:30-11:10 (перемена 15 минут) \n5 урок - 11:25-12:05 (перемена 15 минут) \n6 урок - 12:20-13:00 (перемена 30 минут, пересменка) \n7 урок - 13:30-14:10 (перемена 10 минут) \n8 урок - 14:20-15:00 (перемена 10 минут) \n9 урок - 15:10-15:50 (перемена 20 минут) \n10 урок - 16:10-16:50 (перемена 10 минут) \n11 урок - 17:00-17:40 (перемена 10 минут) \n12 урок - 17:50-18:30 \n\nКружки и элективы проводятся с перерывом от основного расписания в 1 урок.')
                        elif received_message in ['2', 'по субботам', 'в субботу', 'суббота']:
                            send_msg(sender, bells, f'Расписание звонков в субботу: \n{"—"*10} \n1 урок - 8:00-8:40 (перемена 10 минут) \n2 урок - 8:50-9:30 (перемена 10 минут) \n3 урок - 9:40-10:20 (перемена 10 минут) \n4 урок - 10:30-11:10 (перемена 10 минут) \n5 урок - 11:20-12:00 (перемена 10 минут) \n6 урок - 12:10-12:50 (перемена 10 минут) \n7 урок - 13:00-13:40 (перемена 5 минут) \n8 урок - 13:45-14:15')
                        elif received_message in ['3', 'з', '1 классы', 'первые классы', '1ые классы', '1-ые классы', '1 класс', 'первый класс',
                                                'для первых классов', 'для 1 классов', 'для первого класса']:
                            send_msg(sender, bells, f'Расписание звонков для первых классов: \n(указано для 1 учебного интервала) \n{"—"*10} \n1 урок - 8:00-8:35 (перемена 15 минут) \n2 урок - 8:50-9:25 (перемена 15 минут) \n3 урок - 9:40-10:15 (перемена 20 минут) \n4 урок - 10:35-11:10 \n\nВ оздоровительных целях и для облегчения процесса адаптации детей к требованиям школы в 1-ых классах применяется "ступенчатый" метод постепенного наращивания учебной нагрузки: \n- I учебный интервал (сентябрь-октябрь) - 3 урока по 35 минут; \n- II учебный интервал (ноябрь-декабрь) - 4 урока по 35 минут; \n- Январь-май - 4 урока - по 40 минут.')
                        else:
                            send_msg(sender, bells, 'Извините, я Вас не понял. Введите: \n1 - для расписания звонков в будние дни \n2 - для расписания звонков в субботу \n3 - для расписания звонков у 1-ых классов')
                    elif last_word == 'подтверждение удаления данных':
                        if received_message == 'подтвердить':
                            users[str(sender)]['agreed_to_processing'] = False
                            users[str(sender)]['name'] = ''
                            users[str(sender)]['surname'] = ''
                            dump('users', users)
                            send_msg(sender, get_profile_keyboard(sender), '&#9989; Удаление персональных данных произведено успешно.')
                            personal_account()
                        elif received_message == 'отменить':
                            send_msg(sender, get_profile_keyboard(sender), '&#10060; Удаление персональных данных отменено.')
                            personal_account()
                        else: send_msg(sender, unprocessing_confirm, 'Пожалуйста, введите/выберите "Подтвердить" для удаления данных или "Отменить" для отмены операции.')
                    else: pass
                else:
                    set_last_word(sender)
                    send_msg(sender, 0, 'Извините, я Вас не понял. Напишите "Помощь" для списка команд')