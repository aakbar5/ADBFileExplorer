# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import platform

from app.helpers.singleton import Singleton

class Application(metaclass=Singleton):
    __version__ = '1.3.0'
    __author__ = 'Azat Aldeshov'

    def __init__(self):
        print('─────────────────────────────────')
        print('ADB File Explorer v%s' % self.__version__)
        print('Copyright (C) 2022 %s' % self.__author__)
        print('─────────────────────────────────')
        print('Platform %s' % platform.platform())

