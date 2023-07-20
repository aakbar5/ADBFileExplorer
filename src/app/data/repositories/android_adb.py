# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
from typing import List, Tuple

from app.core.settings import Settings
from app.core.managers import ADBManager
from app.data.models import FileType, Device, File
from app.helpers.converters import convert_to_devices, convert_to_file, convert_to_file_list_a
from app.services import adb_helper


class FileRepository:
    @classmethod
    def file(cls, path: str) -> Tuple[File, str]:
        if not ADBManager.get_device():
            return None, "No device selected!"

        path = ADBManager.clear_path(path)
        args = adb_helper.ShellCommand.LS_LIST_DIRS + [path.replace(' ', r'\ ')]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData

        file = convert_to_file(response.OutputData.strip())
        if not file:
            return None, "Unexpected string:\n%s" % response.OutputData

        if file.type == FileType.LINK:
            args = adb_helper.ShellCommand.LS_LIST_DIRS + [path.replace(' ', r'\ ') + '/']
            response = adb_helper.shell(ADBManager.get_device().id, args)
            file.link_type = FileType.UNKNOWN
            if response.OutputData and response.OutputData.startswith('d'):
                file.link_type = FileType.DIRECTORY
            elif response.OutputData and response.OutputData.__contains__('Not a'):
                file.link_type = FileType.FILE
        file.path = path
        return file, response.ErrorData

    @classmethod
    def files(cls) -> Tuple[List[File], str]:
        if not ADBManager.get_device():
            return None, "No device selected!"

        path = ADBManager.path()
        args = adb_helper.ShellCommand.LS_ALL_LIST + [path.replace(' ', r'\ ')]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.IsSuccessful and response.ExitCode != 1:
            return [], response.ErrorData or response.OutputData

        if not response.OutputData:
            return [], response.ErrorData

        args = adb_helper.ShellCommand.LS_ALL_DIRS + [path.replace(' ', r'\ ') + "*/"]
        response_dirs = adb_helper.shell(ADBManager.get_device().id, args)
        if not response_dirs.IsSuccessful and response_dirs.ExitCode != 1:
            return [], response_dirs.ErrorData or response_dirs.OutputData

        dirs = response_dirs.OutputData.split() if response_dirs.OutputData else []
        files = convert_to_file_list_a(response.OutputData, dirs=dirs, path=path)
        return files, response.ErrorData

    @classmethod
    def rename(cls, file: File, name) -> Tuple[str, str]:
        if name.__contains__('/') or name.__contains__('\\'):
            return None, "Invalid name"
        args = [adb_helper.ShellCommand.MV, file.path.replace(' ', r'\ '), (file.location + name).replace(' ', r'\ ')]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        return None, response.ErrorData or response.OutputData

    @classmethod
    def open_file(cls, file: File) -> Tuple[str, str]:
        args = [adb_helper.ShellCommand.CAT, file.path.replace(' ', r'\ ')]
        if file.isdir:
            return None, "Can't open. %s is a directory" % file.path
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData
        return response.OutputData, response.ErrorData

    @classmethod
    def delete(cls, file: File) -> Tuple[str, str]:
        args = [adb_helper.ShellCommand.RM, file.path.replace(' ', r'\ ')]
        if file.isdir:
            args = adb_helper.ShellCommand.RM_DIR_FORCE + [file.path.replace(' ', r'\ ')]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.IsSuccessful or response.OutputData:
            return None, response.ErrorData or response.OutputData
        return "%s '%s' has been deleted" % ('Folder' if file.isdir else 'File', file.path), None

    class UpDownHelper:
        def __init__(self, callback: callable):
            self.messages = []
            self.callback = callback

        def call(self, data: str):
            if data.startswith('['):
                progress = data[1:4].strip()
                if progress.isdigit():
                    self.callback(data[7:], int(progress))
            elif data:
                self.messages.append(data)

    @classmethod
    def download(cls, progress_callback: callable, source: str, destination: str) -> Tuple[str, str]:
        if not destination:
            destination = Settings.device_downloads_path(ADBManager.get_device())
        if ADBManager.get_device() and source and destination:
            helper = cls.UpDownHelper(progress_callback)
            response = adb_helper.pull(ADBManager.get_device().id, source, destination, helper.call)
            if not response.IsSuccessful:
                return None, response.ErrorData or "\n".join(helper.messages)

            return "\n".join(helper.messages), response.ErrorData
        return None, None

    @classmethod
    def new_folder(cls, name) -> Tuple[str, str]:
        if not ADBManager.get_device():
            return None, "No device selected!"

        args = [adb_helper.ShellCommand.MKDIR, (ADBManager.path() + name).replace(' ', r"\ ")]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData
        return response.OutputData, response.ErrorData

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> Tuple[str, str]:
        if ADBManager.get_device() and ADBManager.path() and source:
            helper = cls.UpDownHelper(progress_callback)
            response = adb_helper.push(ADBManager.get_device().id, source, ADBManager.path(), helper.call)
            if not response.IsSuccessful:
                return None, response.ErrorData or "\n".join(helper.messages)

            return "\n".join(helper.messages), response.ErrorData
        return None, None


class DeviceRepository:
    @classmethod
    def devices(cls) -> Tuple[List[Device], str]:
        response = adb_helper.devices()
        if not response.IsSuccessful:
            return [], response.ErrorData or response.OutputData

        devices = convert_to_devices(response.OutputData)
        return devices, response.ErrorData

    @classmethod
    def connect(cls, device_id) -> Tuple[str, str]:
        if not device_id:
            return None, None

        response = adb_helper.connect(device_id)
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData
        return response.OutputData, response.ErrorData

    @classmethod
    def disconnect(cls) -> Tuple[str, str]:
        response = adb_helper.disconnect()
        if not response.IsSuccessful:
            return None, response.ErrorData or response.OutputData

        return response.OutputData, response.ErrorData
