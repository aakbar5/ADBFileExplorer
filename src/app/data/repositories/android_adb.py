# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

from typing import List, Tuple
import shlex

from app.core.managers import ADBManager
from app.core.settings import SettingsOptions, Settings
from app.data.models import FileType, Device, File
from app.helpers.converters import convert_to_devices, convert_to_file, convert_to_file_list_a
from app.services import adb_helper


class FileRepository:
    @classmethod
    def battery_level(cls) -> Tuple[str, str]:
        # print(f"android_adb: battery_level")

        if not ADBManager.get_device():
            return None, "No device selected!"

        args = ['cmd', 'battery', 'get', 'level']
        response_level = adb_helper.shell(ADBManager.get_device().id, args)
        if not response_level.is_okay:
            return None, response_level.error_data or response_level.output_data

        args = ['cmd', 'battery', 'get', 'status']
        response_status = adb_helper.shell(ADBManager.get_device().id, args)
        if not response_status.is_okay:
            return None, response_status.error_data or response_status.output_data

        return response_level.output_data, response_status.output_data

    @classmethod
    def is_android_root(cls) -> Tuple[str, str]:
        # print(f"android_adb: is_android_root")

        if not ADBManager.get_device():
            return None, "No device selected!"

        args = ['id']
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.is_okay:
            return None, response.error_data or response.output_data

        is_root = response.output_data.find("uid=0(root)")
        return is_root, None

    @classmethod
    def android_version(cls) -> Tuple[str, str]:
        # print(f"android_adb: android_version")

        if not ADBManager.get_device():
            return None, "No device selected!"

        args = ['getprop', 'ro.build.version.release']
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.is_okay:
            return None, response.error_data or response.output_data

        return response.output_data, None

    @classmethod
    def file(cls, path: str) -> Tuple[File, str]:
        if not ADBManager.get_device():
            return None, "No device selected!"

        # TODO: Do we really need to chage current path
        path = ADBManager.set_current_path(path)
        args = adb_helper.ShellCommand.LS_LIST_DIRS + [shlex.quote(path)]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.is_okay:
            return None, response.error_data or response.output_data
        file = convert_to_file(response.output_data.strip())
        if not file:
            return None, f"Unexpected string:\n{response.output_data}"

        if file.type == FileType.LINK:
            args = adb_helper.ShellCommand.LS_LIST_DIRS + [shlex.quote(path) + '/']
            response = adb_helper.shell(ADBManager.get_device().id, args)
            file.link_type = FileType.UNKNOWN
            if response.output_data and response.output_data.startswith('d'):
                file.link_type = FileType.DIRECTORY
            elif response.output_data and 'Not a' in response.output_data:
                file.link_type = FileType.FILE
        file.path = path
        return file, response.error_data

    @classmethod
    def files(cls) -> Tuple[List[File], str]:
        if not ADBManager.get_device():
            return None, "No device selected!"

        path = ADBManager.get_current_path()
        args = adb_helper.ShellCommand.LS_ALL_LIST + [shlex.quote(path)]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.is_okay and response.exit_code != 1:
            return [], response.error_data or response.output_data

        if not response.output_data:
            return [], response.error_data

        args = adb_helper.ShellCommand.LS_ALL_DIRS + [shlex.quote(path) + "*/"]
        response_dirs = adb_helper.shell(ADBManager.get_device().id, args)
        if not response_dirs.is_okay and response_dirs.exit_code != 1:
            return [], response_dirs.error_data or response_dirs.output_data

        dirs = response_dirs.output_data.split() if response_dirs.output_data else []
        files = convert_to_file_list_a(response.output_data, dirs=dirs, path=path)
        return files, response.error_data

    @classmethod
    def rename(cls, file: File, name) -> Tuple[str, str]:
        if '/' in name or '\\' in name:
            return None, "Invalid name"
        args = [adb_helper.ShellCommand.MV, shlex.quote(file.path), shlex.quote(file.location + name)]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        return None, response.error_data or response.output_data

    @classmethod
    def open_file(cls, file: File) -> Tuple[str, str]:
        args = [adb_helper.ShellCommand.CAT, shlex.quote(file.path)]
        if file.isdir:
            return None, f"Can't open. {file.path} is a directory"
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.is_okay:
            return None, response.error_data or response.output_data
        return response.output_data, response.error_data

    @classmethod
    def delete(cls, file: File) -> Tuple[str, str]:
        args = [adb_helper.ShellCommand.RM, shlex.quote(file.path)]
        if file.isdir:
            args = adb_helper.ShellCommand.RM_DIR_FORCE + [shlex.quote(file.path)]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.is_okay or response.output_data:
            return None, response.error_data or response.output_data
        return f"{'Folder' if file.isdir else 'File'} '{file.path}' has been deleted", None

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
    def download(cls, progress_callback: callable, source: File, destination: str, delete_too: bool = False) -> Tuple[str, str]:
        if not destination:
            destination = Settings.get_value(SettingsOptions.DOWNLOAD_PATH, ADBManager.get_device())
            destination = destination.replace(" ", "_")

        if ADBManager.get_device() and source and destination:
            helper = cls.UpDownHelper(progress_callback)
            response = adb_helper.pull(ADBManager.get_device().id, source.path, destination, helper.call)

            if not response.is_okay:
                return None, response.error_data or "\n".join(helper.messages)
            if delete_too is True:
                return cls.delete(source)
            return "\n".join(helper.messages), response.error_data
        return None, None

    @classmethod
    def new_folder(cls, name) -> Tuple[str, str]:
        if not ADBManager.get_device():
            return None, "No device selected!"

        args = [adb_helper.ShellCommand.MKDIR, (ADBManager.get_current_path() + name).replace(' ', r"\ ")]
        response = adb_helper.shell(ADBManager.get_device().id, args)
        if not response.is_okay:
            return None, response.error_data or response.output_data
        return response.output_data, response.error_data

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> Tuple[str, str]:
        if ADBManager.get_device() and ADBManager.get_current_path() and source:
            helper = cls.UpDownHelper(progress_callback)
            response = adb_helper.push(ADBManager.get_device().id, source, ADBManager.get_current_path(), helper.call)
            if not response.is_okay:
                return None, response.error_data or "\n".join(helper.messages)

            return "\n".join(helper.messages), response.error_data
        return None, None


class DeviceRepository:
    @classmethod
    def devices(cls) -> Tuple[List[Device], str]:
        response = adb_helper.devices()
        if not response.is_okay:
            return [], response.error_data or response.output_data

        devices = convert_to_devices(response.output_data)
        return devices, response.error_data

    @classmethod
    def connect(cls, device_id) -> Tuple[str, str]:
        if not device_id:
            return None, None

        response = adb_helper.connect(device_id)
        if not response.is_okay:
            return None, response.error_data or response.output_data
        return response.output_data, response.error_data

    @classmethod
    def disconnect(cls) -> Tuple[str, str]:
        response = adb_helper.disconnect()
        if not response.is_okay:
            return None, response.error_data or response.output_data

        return response.output_data, response.error_data
