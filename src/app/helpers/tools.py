# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

import json
import logging
import os
import shutil
import subprocess

from PyQt5 import QtCore
from PyQt5.QtCore import QThread, QObject, QFile, QIODevice, QTextStream
from PyQt5.QtWidgets import QWidget

from adb_shell.auth.keygen import keygen
from adb_shell.auth.sign_pythonrsa import PythonRSASigner
from app.core.settings import SettingsOptions, Settings
from app.data.models import MessageData


class CommonProcess:
    """
    CommonProcess - executes subprocess then saves output data and exit code.
    If 'stdout_callback' is defined then every output data line will call this function

    Keyword arguments:
    arguments -- array list of arguments
    stdout -- define stdout (default subprocess.PIPE)
    stdout_callback -- callable function, params: (data: str) -> None (default None)
    """

    def __init__(self, arguments: list, stdout=subprocess.PIPE, stdout_callback: callable = None):
        self.error_data = None
        self.output_data = None
        self.is_okay = False
        if arguments:
            try:
                process = subprocess.Popen(arguments, stdout=stdout, stderr=subprocess.PIPE)
                if stdout == subprocess.PIPE and stdout_callback:
                    for line in iter(process.stdout.readline, b''):
                        stdout_callback(line.decode(encoding='utf-8'))
                data, error = process.communicate()
                self.exit_code = process.poll()
                self.is_okay = self.exit_code == 0
                self.error_data = error.decode(encoding='utf-8') if error else None
                self.output_data = data.decode(encoding='utf-8') if data else None
            except UnicodeDecodeError:
                self.error_data = "Can't open it, file format is uknown"
            except FileNotFoundError:
                self.error_data = f"Command {' '.join(arguments)} failed! File (command) '{arguments[0]}' not found!"
            except BaseException as error:
                logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
                self.error_data = str(error)


class AsyncRepositoryWorker(QThread):
    on_response = QtCore.pyqtSignal(object, object)  # Response : data, error

    def __init__(
            self,
            worker_id: int,
            name: str,
            repository_method: callable,
            arguments: tuple,
            response_callback: callable,
    ):
        super(AsyncRepositoryWorker, self).__init__()
        self.on_response.connect(response_callback)
        self.finished.connect(self.close)

        self.__repository_method = repository_method
        self.__arguments = arguments
        self.loading_widget = None
        self.closed = False
        self.id = worker_id
        self.name = name

    def run(self):
        data, error = self.__repository_method(*self.__arguments)
        self.on_response.emit(data, error)

    def close(self):
        if self.loading_widget:
            self.loading_widget.close()
        self.deleteLater()
        self.closed = True
        print(f"worker # {self.name} (id={self.id}) is closed")

    def set_loading_widget(self, widget: QWidget):
        self.loading_widget = widget

    def update_loading_widget(self, path, progress):
        if self.loading_widget and not self.closed:
            self.loading_widget.update_progress(f"SOURCE: {path}", progress)


class ProgressCallbackHelper(QObject):
    progress_callback = QtCore.pyqtSignal(str, int)

    def setup(self, parent: QObject, callback: callable):
        self.setParent(parent)
        self.progress_callback.connect(callback)


class Communicate(QObject):
    app_close = QtCore.pyqtSignal()

    files = QtCore.pyqtSignal()
    devices = QtCore.pyqtSignal()
    device_disconnect = QtCore.pyqtSignal()
    device_connect = QtCore.pyqtSignal()

    up = QtCore.pyqtSignal()
    files_refresh = QtCore.pyqtSignal()
    path_toolbar_refresh = QtCore.pyqtSignal()

    notification = QtCore.pyqtSignal(MessageData)

    status_bar_general = QtCore.pyqtSignal(str, int)  # Message, Duration
    status_bar_device_label = QtCore.pyqtSignal(str)  # Message
    status_bar_android_version = QtCore.pyqtSignal(str)  # Message
    status_bar_is_root = QtCore.pyqtSignal(int)  # int
    status_bar_battery_level = QtCore.pyqtSignal(str, str)  # Message

    search_text_update = QtCore.pyqtSignal(str)
    search_case_update = QtCore.pyqtSignal(bool)

def get_python_rsa_keys_signer(rerun=True) -> PythonRSASigner:
    priv_key = Settings.get_value(SettingsOptions.ADB_KEY_FILE_PATH)
    if os.path.isfile(priv_key):
        with open(priv_key, encoding="utf-8") as f:
            private = f.read()
        pubkey = priv_key + '.pub'
        if not os.path.isfile(pubkey):
            if shutil.which('ssh-keygen'):
                os.system(f'ssh-keygen -y -f {priv_key} > {pubkey}')
            else:
                raise OSError('Could not call ssh-keygen!')
        with open(pubkey, encoding="utf-8") as f:
            public = f.read()
        return PythonRSASigner(public, private)
    if rerun:
        # TODO: Testing this use-case
        keygen(priv_key)
        return get_python_rsa_keys_signer(False)
    return None

def read_string_from_file(path: str):
    file = QFile(path)
    if file.open(QIODevice.ReadOnly | QIODevice.Text):
        text = QTextStream(file).readAll()
        file.close()
        return text
    return str()


def quote_file_name(path: str):
    return '\'' + path + '\''


def json_to_dict(path: str):
    try:
        return dict(json.loads(read_string_from_file(path)))
    except BaseException as exception:
        logging.error("File %s. %s", path, exception)
        return {}
