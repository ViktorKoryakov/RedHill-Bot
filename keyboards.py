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
    profile.add_button('Достижения', VkKeyboardColor.PRIMARY)
    profile.add_button('В главное меню', VkKeyboardColor.NEGATIVE)
    return profile

def get_schedule_keyboard(user_id: int) -> VkKeyboard:
    user_info = get('users')[str(user_id)]
    if user_info['class'] != user_info['choosen_class']: return choosing_weekday_sdc
    else: return choosing_weekday_usdc

def get_choosing_schedule_keyboard(user_id: int) -> VkKeyboard:
    user_info = get('users')[str(user_id)]
    keyboard = VkKeyboard(one_time=True)
    if user_info['class'] == '': pass
    else: 
        keyboard.add_button(user_info['class'].upper(), VkKeyboardColor.PRIMARY)
        keyboard.add_line()
    # keyboard.add_openlink_button('Помочь в переносе', f'https://vk.com/im?sel={DEVELOPER_ID}')
    keyboard.add_button('Главное меню', VkKeyboardColor.NEGATIVE)
    return keyboard
    

# [ SETTINGS OF KEYBOARDS / НАСТРОЙКИ КЛАВИАТУР ]
for_banned = VkKeyboard(one_time=True)
for_banned.add_openlink_button('Разработчик', f'https://vk.com/im?sel={DEVELOPER_ID}')

consent_to_processing = VkKeyboard(one_time=True)
consent_to_processing.add_button('Разрешить (1)', color=VkKeyboardColor.POSITIVE)
consent_to_processing.add_button('Запретить (2)', color=VkKeyboardColor.NEGATIVE)

main_page = VkKeyboard(one_time=False)
main_page.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
main_page.add_button('Звонки', color=VkKeyboardColor.PRIMARY)
main_page.add_line()
# main_page.add_button('Подготовка к школе', color=VkKeyboardColor.PRIMARY)
# main_page.add_line()
main_page.add_button('Контакты', color=VkKeyboardColor.SECONDARY)
main_page.add_button('Соцсети', color=VkKeyboardColor.SECONDARY)
main_page.add_line()
main_page.add_button('О боте', color=VkKeyboardColor.SECONDARY)
main_page.add_button('Личный кабинет', color=VkKeyboardColor.SECONDARY)

admin_main_page = VkKeyboard(one_time=False)
admin_main_page.add_button('Расписание', color=VkKeyboardColor.PRIMARY)
admin_main_page.add_button('Звонки', color=VkKeyboardColor.PRIMARY)
admin_main_page.add_line()
# admin_main_page.add_button('Подготовка к школе', color=VkKeyboardColor.PRIMARY)
# admin_main_page.add_line()
admin_main_page.add_button('Контакты', color=VkKeyboardColor.SECONDARY)
admin_main_page.add_button('Соцсети', color=VkKeyboardColor.SECONDARY)
admin_main_page.add_line()
admin_main_page.add_button('О боте', color=VkKeyboardColor.SECONDARY)
admin_main_page.add_button('Личный кабинет', color=VkKeyboardColor.SECONDARY)
admin_main_page.add_button('Админ-панель', color=VkKeyboardColor.SECONDARY)

choosing_weekday_sdc = VkKeyboard(one_time=False)
choosing_weekday_sdc.add_button('Сегодня', color=VkKeyboardColor.PRIMARY)
choosing_weekday_sdc.add_button('Завтра', color=VkKeyboardColor.PRIMARY)
choosing_weekday_sdc.add_line()
choosing_weekday_sdc.add_button('Понедельник', color=VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_button('Вторник', color=VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_button('Среда', color=VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_line()
choosing_weekday_sdc.add_button('Четверг', color=VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_button('Пятница', color=VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_button('Суббота', color=VkKeyboardColor.SECONDARY)
choosing_weekday_sdc.add_line()
choosing_weekday_sdc.add_button('Выбрать классом по умолчанию', color=VkKeyboardColor.PRIMARY)
choosing_weekday_sdc.add_line()
choosing_weekday_sdc.add_button('Назад', color=VkKeyboardColor.PRIMARY)
choosing_weekday_sdc.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

choosing_weekday_usdc = VkKeyboard(one_time=False)
choosing_weekday_usdc.add_button('Сегодня', color=VkKeyboardColor.PRIMARY)
choosing_weekday_usdc.add_button('Завтра', color=VkKeyboardColor.PRIMARY)
choosing_weekday_usdc.add_line()
choosing_weekday_usdc.add_button('Понедельник', color=VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_button('Вторник', color=VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_button('Среда', color=VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_line()
choosing_weekday_usdc.add_button('Четверг', color=VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_button('Пятница', color=VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_button('Суббота', color=VkKeyboardColor.SECONDARY)
choosing_weekday_usdc.add_line()
choosing_weekday_usdc.add_button('Отменить класс по умолчанию', color=VkKeyboardColor.NEGATIVE)
choosing_weekday_usdc.add_line()
choosing_weekday_usdc.add_button('Назад', color=VkKeyboardColor.PRIMARY)
choosing_weekday_usdc.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

contacts = VkKeyboard(one_time=False)
contacts.add_openlink_button('Сайт школы', link='https://shkola47kirov-r43.gosweb.gosuslugi.ru/')
contacts.add_openlink_button('Электронный дневник', link='https://one.43edu.ru/auth/login')
contacts.add_line()
contacts.add_button('Администрация и службы школы', color=VkKeyboardColor.SECONDARY)
contacts.add_line()
contacts.add_button('Соцсети школы', color=VkKeyboardColor.SECONDARY)
contacts.add_line()
contacts.add_openlink_button('Разработчик бота', link=f'https://vk.com/id{DEVELOPER_ID}')
contacts.add_button('Главное меню', color=VkKeyboardColor.NEGATIVE)

social_networks = VkKeyboard(one_time=False)
social_networks.add_openlink_button('Red Hill (ВКонтакте)', link='https://vk.com/redhill47')
social_networks.add_openlink_button('Red Hill (Одноклассники)', link='https://ok.ru/group/70000002346199')
social_networks.add_line()
social_networks.add_openlink_button('47 высота', link='https://vk.com/ssc_47height')
social_networks.add_openlink_button('Библиотека школы', link='https://vk.com/club192165194')
social_networks.add_line()
social_networks.add_openlink_button('Музей "Светлица"', link='https://vk.com/svetlitsamuseeum')
social_networks.add_openlink_button('Бессмертный полк 47', link='https://vk.com/bessmertniypolk47')
social_networks.add_line()
social_networks.add_button('Назад (контакты)', color=VkKeyboardColor.PRIMARY)
social_networks.add_button('В главное меню', color=VkKeyboardColor.NEGATIVE)

about_bot = VkKeyboard(one_time=False)
about_bot.add_openlink_button('Разработчик бота', link=f'https://vk.com/id{DEVELOPER_ID}')
about_bot.add_button('Благодарности', color=VkKeyboardColor.SECONDARY)
about_bot.add_line()
about_bot.add_button('Обновления', color=VkKeyboardColor.SECONDARY)
about_bot.add_line()
about_bot.add_button('В главное меню', color=VkKeyboardColor.NEGATIVE)

back_to_about_bot = VkKeyboard(one_time=False)
back_to_about_bot.add_button('Назад (о боте)', color=VkKeyboardColor.PRIMARY)
back_to_about_bot.add_line()
back_to_about_bot.add_button('В главное меню', color=VkKeyboardColor.NEGATIVE)

bells = VkKeyboard(one_time=False)
bells.add_button('Будние дни', color=VkKeyboardColor.PRIMARY)
bells.add_button('По субботам', color=VkKeyboardColor.PRIMARY)
bells.add_line()
bells.add_button('Для 1 классов', color=VkKeyboardColor.SECONDARY)
bells.add_line()
bells.add_button('В главное меню', color=VkKeyboardColor.NEGATIVE)

administration = VkKeyboard(one_time=False)
administration.add_button('Назад (контакты)', color=VkKeyboardColor.PRIMARY)
administration.add_button('В главное меню', color=VkKeyboardColor.NEGATIVE)

admin_panel = VkKeyboard(one_time=False)
admin_panel.add_button('Статистика всех команд', color=VkKeyboardColor.PRIMARY)
admin_panel.add_line()
admin_panel.add_button('Обновить', color=VkKeyboardColor.PRIMARY)
admin_panel.add_button('В главное меню', color=VkKeyboardColor.NEGATIVE)

back_to_admin_panel = VkKeyboard(one_time=False)
back_to_admin_panel.add_button('Обновить', color=VkKeyboardColor.PRIMARY)
back_to_admin_panel.add_button('Назад в админ-панель', color=VkKeyboardColor.NEGATIVE)
back_to_admin_panel.add_line()
back_to_admin_panel.add_button('В главное меню', color=VkKeyboardColor.NEGATIVE)

# [ Automailing Message Keyboard / Меню сообщения авторассылки ]
automailing_keyboard = VkKeyboard(one_time=True)
automailing_keyboard.add_button('Отключить авторассылку', color=VkKeyboardColor.SECONDARY)
automailing_keyboard.add_line()
automailing_keyboard.add_button('Главное меню', color=VkKeyboardColor.PRIMARY)

# [ Personal Account Keyboard / Меню личного кабинета ]
unprocessing_confirm = VkKeyboard(one_time=True)
unprocessing_confirm.add_button('Подтвердить', color=VkKeyboardColor.PRIMARY)
unprocessing_confirm.add_line()
unprocessing_confirm.add_button('Отменить', color=VkKeyboardColor.NEGATIVE)

# [ SETTINGS OF PROGRAM START / НАСТРОЙКИ СТАРТА ПРОГРАММЫ ]
if __name__ == '__main__': pass