# -*- coding: utf-8 -*-
# MIT License
# Copyright (c) 2025 Виктор Коряков
# See LICENSE file in the project root for more details.

# [ IMPORTING | ИМПОРТ ]
from setuptools import setup, find_packages

setup(
    name = 'RedHill Бот',
    version = '2.1.11',
    license = 'MIT',
    author = 'Viktor Koryakov',
    author_email = 'vityakoryakov@yandex.com',
    description = 'Школьный бот с расписанием уроков, звонков и утренней авторассылкой',
    long_description=open('README.md').read(),
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/ViktorKoryakov/RedHill-Bot',
    packages = find_packages()
)