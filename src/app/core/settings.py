# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import os

from PyQt5.QtCore import QSettings
from PyQt5.QtCore import QSettings, QPoint, QSize

from app.helpers.singleton import Singleton

class SettingsOptions:
    ADB_PATH = 'adb_path'
    ADB_CORE = 'adb_core'
    ADB_AS_ROOT = 'adb_as_root'
    ADB_KILL_AT_EXIT = 'adb_kill_at_exit'
    PRESERVE_TIMESTAMP = 'preserve_timestamp'
    NOTIFICATION_TIMEOUT = 'notification_timeout'
    DOWNLOAD_PATH = 'download_path'
    SHOW_WELCOME_MSG = 'show_welcome_msg'
    RESTORE_WIN_GEOMETRY = 'restore_win_geometry'
    WIN_SIZE = 'win_size'
    WIN_POS = 'win_pos'

class Settings(metaclass=Singleton):
    settings_ = None

    @classmethod
    def initialize(cls):
        if cls.settings_ is not None:
            return True

        cls.settings_ = QSettings('ADBFileExplorer', 'ADBFileExplorer')
        if not cls.settings_.contains(SettingsOptions.ADB_PATH):
            cls.settings_.setValue(SettingsOptions.ADB_PATH, 'adb')

        if not cls.settings_.contains(SettingsOptions.ADB_CORE):
            cls.settings_.setValue(SettingsOptions.ADB_CORE, 'external')

        if not cls.settings_.contains(SettingsOptions.ADB_AS_ROOT):
            cls.settings_.setValue(SettingsOptions.ADB_AS_ROOT, False)

        if not cls.settings_.contains(SettingsOptions.ADB_KILL_AT_EXIT):
            cls.settings_.setValue(SettingsOptions.ADB_KILL_AT_EXIT, False)

        if not cls.settings_.contains(SettingsOptions.PRESERVE_TIMESTAMP):
            cls.settings_.setValue(SettingsOptions.PRESERVE_TIMESTAMP, True)

        if not cls.settings_.contains(SettingsOptions.NOTIFICATION_TIMEOUT):
            cls.settings_.setValue(SettingsOptions.NOTIFICATION_TIMEOUT, 15000)

        user_download_folder = os.path.join(os.path.expanduser('~'), 'Downloads')
        if not cls.settings_.contains(SettingsOptions.DOWNLOAD_PATH):
            cls.settings_.setValue(SettingsOptions.DOWNLOAD_PATH, user_download_folder)

        if not cls.settings_.contains(SettingsOptions.SHOW_WELCOME_MSG):
            cls.settings_.setValue(SettingsOptions.SHOW_WELCOME_MSG, True)

        if not cls.settings_.contains(SettingsOptions.RESTORE_WIN_GEOMETRY):
            cls.settings_.setValue(SettingsOptions.RESTORE_WIN_GEOMETRY, True)

        if not cls.settings_.contains(SettingsOptions.WIN_SIZE):
            cls.settings_.setValue(SettingsOptions.WIN_SIZE, QSize(640, 480))

        if not cls.settings_.contains(SettingsOptions.WIN_POS):
            cls.settings_.setValue(SettingsOptions.WIN_POS, QPoint(50, 50))

    @classmethod
    def to_bool(cls, value):
        if type(value) is str:
            if value == 'true':
                return True
            elif value == 'True':
                return True
            else:
                return False
        elif value is None:
            return False
        else:
            return value

    @classmethod
    def set_value(cls, key, value):
        cls.settings_.setValue(key, value)

    @classmethod
    def get_value(cls, key, device = None):
        cls.initialize()
        raw_value = cls.settings_.value(key)
        if key == SettingsOptions.ADB_PATH:
            return str(raw_value)
        elif key == SettingsOptions.ADB_CORE:
            return str(raw_value)
        elif key == SettingsOptions.ADB_AS_ROOT:
            return cls.to_bool(raw_value)
        elif key == SettingsOptions.ADB_KILL_AT_EXIT:
            return cls.to_bool(raw_value)
        elif key == SettingsOptions.PRESERVE_TIMESTAMP:
            return cls.to_bool(raw_value)
        elif key == SettingsOptions.NOTIFICATION_TIMEOUT:
            return int(raw_value)
        elif key == SettingsOptions.DOWNLOAD_PATH:
            if not os.path.isdir(raw_value):
                os.mkdir(raw_value)
            if device:
                downloads_path = os.path.join(raw_value, device.name)
                if not os.path.isdir(downloads_path):
                    os.mkdir(downloads_path)
                return downloads_path
            return raw_value
        elif key == SettingsOptions.SHOW_WELCOME_MSG:
            return cls.to_bool(raw_value)
        elif key == SettingsOptions.RESTORE_WIN_GEOMETRY:
            return cls.to_bool(raw_value)
        elif key == SettingsOptions.WIN_SIZE:
            return QSize(raw_value)
        elif key == SettingsOptions.WIN_POS:
            return QPoint(raw_value)
        else:
            return raw_value
