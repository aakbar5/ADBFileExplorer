# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import sys
from typing import Union

import adb_shell

from app.core.settings import SettingsOptions, Settings
from app.core.managers import PythonADBManager, ADBManager, WorkersManager
from app.helpers.singleton import Singleton
from app.services import adb_helper


class Adb(metaclass=Singleton):
    PYTHON_ADB_SHELL = 'python'  # Python library `adb-shell`
    EXTERNAL_TOOL_ADB = 'external'  # Command-line tool `adb`

    core = Settings.get_value(SettingsOptions.ADB_CORE)

    @classmethod
    def start(cls):
        if cls.core == cls.PYTHON_ADB_SHELL:
            if adb_helper.kill_server().IsSuccessful:
                print("adb server stopped.")

            print('Using Python "adb-shell" version %s' % adb_shell.__version__)

        elif cls.core == cls.EXTERNAL_TOOL_ADB and adb_helper.validate():
            print(adb_helper.version().OutputData)

            adb_server = adb_helper.start_server()
            if adb_server.ErrorData:
                print(adb_server.ErrorData, file=sys.stderr)

            print(adb_server.OutputData or 'ADB server running...')

    @classmethod
    def stop(cls):
        if cls.core == cls.PYTHON_ADB_SHELL:
            # Closing device connection
            if PythonADBManager.device and PythonADBManager.device.available:
                name = PythonADBManager.get_device().name if PythonADBManager.get_device() else "Unknown"
                print('Connection to device %s closed' % name)
                PythonADBManager.device.close()
            return True

        elif cls.core == cls.EXTERNAL_TOOL_ADB:
            if adb_helper.kill_server().IsSuccessful:
                print("ADB Server stopped")
            return True

    @classmethod
    def manager(cls) -> Union[ADBManager, PythonADBManager]:
        if cls.core == cls.PYTHON_ADB_SHELL:
            return PythonADBManager()
        elif cls.core == cls.EXTERNAL_TOOL_ADB:
            return ADBManager()

    @classmethod
    def worker(cls) -> WorkersManager:
        return WorkersManager()
