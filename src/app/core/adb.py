# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

import sys
from typing import Union

import adb_shell

from app.core.managers import PythonADBManager, ADBManager, WorkersManager
from app.core.settings import SettingsOptions, Settings
from app.helpers.singleton import Singleton
from app.services import adb_helper


class Adb(metaclass=Singleton):
    PYTHON_ADB_SHELL = 'python'  # Python library `adb-shell`
    EXTERNAL_TOOL_ADB = 'external'  # Command-line tool `adb`

    core = Settings.get_value(SettingsOptions.ADB_CORE)

    @classmethod
    def start(cls):
        if cls.core == cls.PYTHON_ADB_SHELL:
            if adb_helper.kill_server().is_okay:
                print("adb server stopped.")

            print(f'Using Python "adb-shell" version {adb_shell.__version__}')
        if cls.core == cls.EXTERNAL_TOOL_ADB and adb_helper.validate():
            print(adb_helper.version().output_data)

            adb_server = adb_helper.start_server()
            if adb_server.error_data:
                print(adb_server.error_data, file=sys.stderr)

            print(adb_server.output_data or 'ADB server running...')

    @classmethod
    def stop(cls):
        if cls.core == cls.PYTHON_ADB_SHELL:
            # Closing device connection
            if PythonADBManager.device and PythonADBManager.device.available:
                name = PythonADBManager.get_device().name if PythonADBManager.get_device() else "Unknown"
                print(f'Connection to device {name} closed')
                PythonADBManager.device.close()
            return True
        if cls.core == cls.EXTERNAL_TOOL_ADB:
            if adb_helper.kill_server().is_okay:
                print("ADB Server stopped")
            return True
        return None

    @classmethod
    def manager(cls) -> Union[ADBManager, PythonADBManager]:
        if cls.core == cls.PYTHON_ADB_SHELL:
            return PythonADBManager()
        if cls.core == cls.EXTERNAL_TOOL_ADB:
            return ADBManager()
        return None

    @classmethod
    def worker(cls) -> WorkersManager:
        return WorkersManager()
