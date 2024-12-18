# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

import platform

from app.helpers.singleton import Singleton

class Application(metaclass=Singleton):
    __version__ = '1.3.0'
    __author__ = 'Azat Aldeshov'

    def __init__(self):
        print('─────────────────────────────────')
        print(f'ADB File Explorer v{self.__version__}')
        print('─────────────────────────────────')
        print(f'Platform {platform.platform()}')
