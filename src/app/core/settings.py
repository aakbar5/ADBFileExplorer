# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

import os

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
    STATUSBAR_UPDATE_TIME = 'statusbar_update_time'
    FILE_DATE_FORMAT = 'file_date_format'
    ADB_KEY_FILE_PATH = 'adb_key_file_path'
    SORT_FOLDERS_BEFORE_FILES = 'sort_folders_before_files'
    HEADER_PERMISSION = 'header_permission'
    HEADER_SIZE = 'header_size'
    HEADER_DATE = 'header_date'
    HEADER_MIME_TYPE = 'header_mime_type'

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
            cls.settings_.setValue(SettingsOptions.NOTIFICATION_TIMEOUT, 2000)

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

        if not cls.settings_.contains(SettingsOptions.STATUSBAR_UPDATE_TIME):
            cls.settings_.setValue(SettingsOptions.STATUSBAR_UPDATE_TIME, 100)

        if not cls.settings_.contains(SettingsOptions.FILE_DATE_FORMAT):
            cls.settings_.setValue(SettingsOptions.FILE_DATE_FORMAT, 'Informal')

        # os.path.expanduser('~/.android/adbkey')
        adb_key_file = os.path.join(os.path.expanduser('~'), '.android', 'adbkey')
        if not cls.settings_.contains(SettingsOptions.ADB_KEY_FILE_PATH):
            cls.settings_.setValue(SettingsOptions.ADB_KEY_FILE_PATH, adb_key_file)

        if not cls.settings_.contains(SettingsOptions.SORT_FOLDERS_BEFORE_FILES):
            cls.settings_.setValue(SettingsOptions.SORT_FOLDERS_BEFORE_FILES, True)

        if not cls.settings_.contains(SettingsOptions.HEADER_PERMISSION):
            cls.settings_.setValue(SettingsOptions.HEADER_PERMISSION, True)

        if not cls.settings_.contains(SettingsOptions.HEADER_SIZE):
            cls.settings_.setValue(SettingsOptions.HEADER_SIZE, True)

        if not cls.settings_.contains(SettingsOptions.HEADER_DATE):
            cls.settings_.setValue(SettingsOptions.HEADER_DATE, True)

        if not cls.settings_.contains(SettingsOptions.HEADER_MIME_TYPE):
            cls.settings_.setValue(SettingsOptions.HEADER_MIME_TYPE, True)

    @classmethod
    def to_bool(cls, value):
        if isinstance(value, str):
            if value.lower() == 'true':
                return True
            return False
        if value is None:
            return False
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
        if key == SettingsOptions.ADB_CORE:
            return str(raw_value)
        if key == SettingsOptions.ADB_AS_ROOT:
            return cls.to_bool(raw_value)
        if key == SettingsOptions.ADB_KILL_AT_EXIT:
            return cls.to_bool(raw_value)
        if key == SettingsOptions.PRESERVE_TIMESTAMP:
            return cls.to_bool(raw_value)
        if key == SettingsOptions.NOTIFICATION_TIMEOUT:
            return int(raw_value)
        if key == SettingsOptions.DOWNLOAD_PATH:
            if not os.path.isdir(raw_value):
                os.mkdir(raw_value)
            if device:
                device_name = device.name.replace(" ", "_")
                downloads_path = os.path.join(raw_value, device_name)
                if not os.path.isdir(downloads_path):
                    os.mkdir(downloads_path)
                return downloads_path
            return raw_value
        if key == SettingsOptions.SHOW_WELCOME_MSG:
            return cls.to_bool(raw_value)
        if key == SettingsOptions.RESTORE_WIN_GEOMETRY:
            return cls.to_bool(raw_value)
        if key == SettingsOptions.WIN_SIZE:
            return QSize(raw_value)
        if key == SettingsOptions.WIN_POS:
            return QPoint(raw_value)
        if key == SettingsOptions.STATUSBAR_UPDATE_TIME:
            return int(raw_value)
        if key == SettingsOptions.FILE_DATE_FORMAT:
            return str(raw_value)
        if key == SettingsOptions.ADB_KEY_FILE_PATH:
            return str(raw_value)
        if key == SettingsOptions.SORT_FOLDERS_BEFORE_FILES:
            return cls.to_bool(raw_value)
        if key == SettingsOptions.HEADER_PERMISSION:
            return cls.to_bool(raw_value)
        if key == SettingsOptions.HEADER_SIZE:
            return cls.to_bool(raw_value)
        if key == SettingsOptions.HEADER_DATE:
            return cls.to_bool(raw_value)
        if key == SettingsOptions.HEADER_MIME_TYPE:
            return cls.to_bool(raw_value)
        return raw_value
