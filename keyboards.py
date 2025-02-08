# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2025 Виктор Коряков
# See LICENSE file in the project root for more details.

# [ IMPORTING / ИМПОРТ ]
from main import *
from vk_api.utils import get_random_id
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

# [ SEND MESSAGES FUNCTIONS / ФУНКЦИИ ОТПРАВКИ СООБЩЕНИЙ ]
def send_msg(send_to: int, keyboard: VkKeyboard | int, message) -> None:
    """
    Отправляет сообщение пользователю

    :param send_to: ID пользователя ВКонтакте, которому будет отправлено сообщение. Пользователь должен написать в бота хотя бы одно сообщение.
    :type send_to: int

    :param keyboard: Клавиатура VkKeyboard (0, если нужно главное меню)
    :type keyboard: VkKeyboard | int

    :param message: Текст сообщения
    :type message: Any

    :rtype: str
    """
    def check_admin_status() -> str:
        return admin_main_page.get_keyboard() if is_admin(send_to) else main_page.get_keyboard()

    # Если требуется клавиатура главного меню, в параметр keyboard нужно указать 0
    if keyboard == 0: auth.method('messages.send', {'user_id': send_to, 'message': message, 'random_id': get_random_id(), 'keyboard': check_admin_status()})
    else: auth.method('messages.send', {'user_id': send_to, 'message': message, 'random_id': get_random_id(), 'keyboard': keyboard.get_keyboard()})

def get_profile_keyboard(user_id: int) -> VkKeyboard:
    user_info: dict = get('users')[str(user_id)]
    profile = VkKeyboard()
    profile.add_button('Отключить рассылку' if user_info.get('get_mailing', False) else 'Включить рассылку')
    profile.add_button('Отключить авторассылку' if user_info.get('get_automailing', False) else 'Включить авторассылку')
    profile.add_line()
    profile.add_button('Удалить данные' if user_info.get('agreed_to_processing', False) else 'Собрать данные',
                        VkKeyboardColor.NEGATIVE if user_info.get('agreed_to_processing', False) else VkKeyboardColor.POSITIVE)
    profile.add_line()
    profile.add_button('В главное меню', VkKeyboardColor.NEGATIVE)
    return profile

def get_schedule_keyboard(user_id: int) -> VkKeyboard:
    user_info = get('users')[str(user_id)]
    if user_info['class'] != user_info['choosen_class']: return choosing_weekday_sdc
    else: return choosing_weekday_usdc

def get_choosing_schedule_keyboard(user_id: int) -> VkKeyboard:
    user_info = get('users')[str(user_id)]
    keyboard = VkKeyboard(True)
    if user_info['class'] == '': pass
    else: 
        keyboard.add_button(user_info['class'].upper(), VkKeyboardColor.PRIMARY)
        keyboard.add_line()
    keyboard.add_openlink_button('Как внести вклад', 'https://github.com/ViktorKoryakov/RedHill-Bot/blob/cf0a747d2e23b640c60e6380c5409be7fe1d3095/%D0%9F%D0%B0%D0%BC%D1%8F%D1%82%D0%BA%D0%B0%20%D0%BF%D0%BE%20%D0%BF%D0%B5%D1%80%D0%B5%D0%BD%D0%BE%D1%81%D1%83%20%D1%80%D0%B0%D1%81%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D1%8F.md')
    keyboard.add_line()
    keyboard.add_button('Главное меню', VkKeyboardColor.NEGATIVE)
    return keyboard
    

# [ SETTINGS OF KEYBOARDS / НАСТРОЙКИ КЛАВИАТУР ]
for_banned = VkKeyboard(True)
for_banned.add_openlink_button('Разработчик', f'https://vk.com/im?sel={DEVELOPER_ID}')

consent_to_processing = VkKeyboard(True)
consent_to_processing.add_button('Разрешить (1)', VkKeyboardColor.POSITIVE)
consent_to_processing.add_button('Запретить (2)', VkKeyboardColor.NEGATIVE)

main_page = VkKeyboard(False)
main_page.add_button('Расписание', VkKeyboardColor.PRIMARY)
main_page.add_button('Звонки', VkKeyboardColor.PRIMARY)
main_page.add_line()
main_page.add_button('О частичной заморозке', VkKeyboardColor.PRIMARY)
main_page.add_line()
# main_page.add_button('Подготовка к школе', VkKeyboardColor.PRIMARY)
# main_page.add_line()
main_page.add_button('Контакты', VkKeyboardColor.SECONDARY)
main_page.add_button('Соцсети', VkKeyboardColor.SECONDARY)
main_page.add_line()
main_page.add_button('О боте', VkKeyboardColor.SECONDARY)
main_page.add_button('Личный кабинет', VkKeyboardColor.SECONDARY)

admin_main_page = VkKeyboard(False)
admin_main_page.add_button('Расписание', VkKeyboardColor.PRIMARY)
admin_main_page.add_button('Звонки', VkKeyboardColor.PRIMARY)
admin_main_page.add_line()
admin_main_page.add_button('О частичной заморозке', VkKeyboardColor.PRIMARY)
admin_main_page.add_line()
# admin_main_page.add_button('Подготовка к школе', VkKeyboardColor.PRIMARY)
# admin_main_page.add_line()
admin_main_page.add_button('Контакты', VkKeyboardColor.SECONDARY)
admin_main_page.add_button('Соцсети', VkKeyboardColor.SECONDARY)
admin_main_page.add_line()
admin_main_page.add_button('О боте', VkKeyboardColor.SECONDARY)
admin_main_page.add_button('Личный кабинет', VkKeyboardColor.SECONDARY)
admin_main_page.add_button('Админ-панель', VkKeyboardColor.SECONDARY)

partial_frost = VkKeyboard(True)
partial_frost.add_openlink_button('Помочь продукту', 'https://github.com/ViktorKoryakov/RedHill-Bot')
partial_frost.add_line()
partial_frost.add_openlink_button('Как изменить расписание', 'https://github.com/ViktorKoryakov/RedHill-Bot/blob/cf0a747d2e23b640c60e6380c5409be7fe1d3095/%D0%9F%D0%B0%D0%BC%D1%8F%D1%82%D0%BA%D0%B0%20%D0%BF%D0%BE%20%D0%BF%D0%B5%D1%80%D0%B5%D0%BD%D0%BE%D1%81%D1%83%20%D1%80%D0%B0%D1%81%D0%BF%D0%B8%D1%81%D0%B0%D0%BD%D0%B8%D1%8F.md')
partial_frost.add_line()
partial_frost.add_openlink_button('Разработчик', f'https://vk.com/id{DEVELOPER_ID}')
partial_frost.add_button('В главное меню', VkKeyboardColor.NEGATIVE)

choosing_weekday_sdc = VkKeyboard(False)
choosing_weekday_sdc.add_button('Сегодня', VkKeyboardColor.PRIMARY)
choosing_weekday_sdc.add_button('Завтра', VkKeyboardColor.PRIMARY)
choosing_weekday_sdc.add_line()
choosing_weekday_sdc.add_button('Понедельник', VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_button('Вторник', VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_button('Среда', VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_line()
choosing_weekday_sdc.add_button('Четверг', VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_button('Пятница', VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_button('Суббота', VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_line()
choosing_weekday_sdc.add_button('Выбрать классом по умолчанию', VkKeyboardColor.PRIMARY)
choosing_weekday_sdc.add_line()
choosing_weekday_sdc.add_button('Назад', VkKeyboardColor.PRIMARY)
choosing_weekday_sdc.add_button('Главное меню', VkKeyboardColor.NEGATIVE)

choosing_weekday_usdc = VkKeyboard(False)
choosing_weekday_usdc.add_button('Сегодня', VkKeyboardColor.PRIMARY)
choosing_weekday_usdc.add_button('Завтра', VkKeyboardColor.PRIMARY)
choosing_weekday_usdc.add_line()
choosing_weekday_usdc.add_button('Понедельник', VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_button('Вторник', VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_button('Среда', VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_line()
choosing_weekday_usdc.add_button('Четверг', VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_button('Пятница', VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_button('Суббота', VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_line()
choosing_weekday_usdc.add_button('Отменить класс по умолчанию', VkKeyboardColor.NEGATIVE)
choosing_weekday_usdc.add_line()
choosing_weekday_usdc.add_button('Назад', VkKeyboardColor.PRIMARY)
choosing_weekday_usdc.add_button('Главное меню', VkKeyboardColor.NEGATIVE)

contacts = VkKeyboard(False)
contacts.add_openlink_button('Сайт школы', 'https://shkola47kirov-r43.gosweb.gosuslugi.ru/')
contacts.add_openlink_button('Электронный дневник', 'https://one.43edu.ru/auth/login')
contacts.add_line()
contacts.add_button('Администрация и службы школы', VkKeyboardColor.SECONDARY)
contacts.add_line()
contacts.add_button('Соцсети школы', VkKeyboardColor.SECONDARY)
contacts.add_line()
contacts.add_openlink_button('Разработчик', f'https://vk.com/id{DEVELOPER_ID}')
contacts.add_button('Помочь боту', VkKeyboardColor.SECONDARY)
contacts.add_line()
contacts.add_button('Главное меню', VkKeyboardColor.NEGATIVE)

social_networks = VkKeyboard(False)
social_networks.add_openlink_button('Red Hill (ВКонтакте)', 'https://vk.com/redhill47')
social_networks.add_openlink_button('Red Hill (Одноклассники)', 'https://ok.ru/group/70000002346199')
social_networks.add_line()
social_networks.add_openlink_button('47 высота', 'https://vk.com/ssc_47height')
social_networks.add_openlink_button('Библиотека школы', 'https://vk.com/club192165194')
social_networks.add_line()
social_networks.add_openlink_button('Музей "Светлица"', 'https://vk.com/svetlitsamuseeum')
social_networks.add_openlink_button('Бессмертный полк 47', 'https://vk.com/bessmertniypolk47')
social_networks.add_line()
social_networks.add_button('Назад (контакты)', VkKeyboardColor.PRIMARY)
social_networks.add_button('В главное меню', VkKeyboardColor.NEGATIVE)

about_bot = VkKeyboard(False)
about_bot.add_openlink_button('Разработчик бота', f'https://vk.com/id{DEVELOPER_ID}')
about_bot.add_line()
about_bot.add_button('Помочь боту', VkKeyboardColor.PRIMARY)
about_bot.add_line()
about_bot.add_button('Благодарности', VkKeyboardColor.SECONDARY)
about_bot.add_button('Обновления', VkKeyboardColor.SECONDARY)
about_bot.add_line()
about_bot.add_button('В главное меню', VkKeyboardColor.NEGATIVE)

back_to_about_bot = VkKeyboard(False)
back_to_about_bot.add_button('Назад (о боте)', VkKeyboardColor.PRIMARY)
back_to_about_bot.add_line()
back_to_about_bot.add_button('В главное меню', VkKeyboardColor.NEGATIVE)

bells = VkKeyboard(False)
bells.add_button('Будние дни', VkKeyboardColor.PRIMARY)
bells.add_button('По субботам', VkKeyboardColor.PRIMARY)
bells.add_line()
bells.add_button('Для 1 классов', VkKeyboardColor.SECONDARY)
bells.add_line()
bells.add_button('В главное меню', VkKeyboardColor.NEGATIVE)

administration = VkKeyboard(False)
administration.add_button('Назад (контакты)', VkKeyboardColor.PRIMARY)
administration.add_button('В главное меню', VkKeyboardColor.NEGATIVE)

admin_panel = VkKeyboard(False)
admin_panel.add_button('Статистика всех команд', VkKeyboardColor.PRIMARY)
admin_panel.add_line()
admin_panel.add_button('Обновить', VkKeyboardColor.PRIMARY)
admin_panel.add_button('В главное меню', VkKeyboardColor.NEGATIVE)

back_to_admin_panel = VkKeyboard(False)
back_to_admin_panel.add_button('Обновить', VkKeyboardColor.PRIMARY)
back_to_admin_panel.add_button('Назад в админ-панель', VkKeyboardColor.NEGATIVE)
back_to_admin_panel.add_line()
back_to_admin_panel.add_button('В главное меню', VkKeyboardColor.NEGATIVE)

# [ Automailing Message Keyboard / Меню сообщения авторассылки ]
automailing_keyboard = VkKeyboard(True)
automailing_keyboard.add_button('Отключить авторассылку', VkKeyboardColor.SECONDARY)
automailing_keyboard.add_line()
automailing_keyboard.add_button('Главное меню', VkKeyboardColor.PRIMARY)

# [ Mailing Message Keyboard / Меню сообщения рассылки ]
mailing_keyboard = VkKeyboard(True)
mailing_keyboard.add_button('Отключить рассылку', VkKeyboardColor.SECONDARY)
mailing_keyboard.add_line()
mailing_keyboard.add_button('Главное меню', VkKeyboardColor.PRIMARY)

# [ Personal Account Keyboard / Меню личного кабинета ]
unprocessing_confirm = VkKeyboard(True)
unprocessing_confirm.add_button('Подтвердить', VkKeyboardColor.PRIMARY)
unprocessing_confirm.add_line()
unprocessing_confirm.add_button('Отменить', VkKeyboardColor.NEGATIVE)

# [ SETTINGS OF PROGRAM START / НАСТРОЙКИ СТАРТА ПРОГРАММЫ ]
if __name__ == '__main__': pass