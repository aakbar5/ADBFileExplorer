# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import os
import platform

from PyQt5.QtCore import QFile, QIODevice
from pkg_resources import resource_filename

from app.data.models import Device
from app.helpers.tools import Singleton, json_to_dict


class Application(metaclass=Singleton):
    __version__ = '1.3.0'
    __author__ = 'Azat Aldeshov'

    def __init__(self):
        print('─────────────────────────────────')
        print('ADB File Explorer v%s' % self.__version__)
        print('Copyright (C) 2022 %s' % self.__author__)
        print('─────────────────────────────────')
        print('Platform %s' % platform.platform())

