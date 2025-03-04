# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

import datetime
import logging
import os
import shlex
from typing import List, Tuple

from usb1 import USBContext

from app.core.managers import PythonADBManager
from app.core.settings import SettingsOptions, Settings
from app.data.models import Device, File, FileType
from app.helpers.converters import __converter_to_permissions_default__
from app.services.adb_helper import ShellCommand


class FileRepository:
    @classmethod
    def capture_screenshot(cls) -> Tuple[str, str]:
        return "TODO", "None"

    @classmethod
    def battery_level(cls) -> Tuple[str, str]:
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        return "TODO", "None"

    @classmethod
    def is_android_root(cls) -> Tuple[str, str]:
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        return "TODO", "None"

    @classmethod
    def android_version(cls) -> Tuple[str, str]:
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        return "TODO", "None"

    @classmethod
    def file(cls, path: str) -> Tuple[File, str]:
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        try:
            path = PythonADBManager.set_current_path(path)
            mode, size, mtime = PythonADBManager.device.stat(path)
            file = File(
                name=os.path.basename(os.path.normpath(path)),
                size=size,
                date_time=datetime.datetime.utcfromtimestamp(mtime),
                permissions=__converter_to_permissions_default__(list(oct(mode)[2:]))
            )

            if file.type == FileType.LINK:
                args = ShellCommand.LS_LIST_DIRS + [shlex.quote(path) + '/']
                response = PythonADBManager.device.shell(shlex.join(args))
                file.link_type = FileType.UNKNOWN
                if response and response.startswith('d'):
                    file.link_type = FileType.DIRECTORY
                elif response and 'Not a' in response:
                    file.link_type = FileType.FILE
            file.path = path
            return file, None

        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
            return None, error

    @classmethod
    def files(cls) -> Tuple[List[File], str]:
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"

        files = []
        try:
            path = PythonADBManager.get_current_path()
            response = PythonADBManager.device.list(path)

            args = ShellCommand.LS_ALL_DIRS + [shlex.quote(path) + "*/"]
            dirs = PythonADBManager.device.shell(" ".join(args)).split()

            for file in response:
                if file.filename.decode() == '.' or file.filename.decode() == '..':
                    continue

                permissions = __converter_to_permissions_default__(list(oct(file.mode)[2:]))
                link_type = None
                if permissions[0] == 'l':
                    link_type = FileType.FILE
                    if str(path + file.filename.decode() + "/") in dirs:
                        link_type = FileType.DIRECTORY

                files.append(
                    File(
                        name=file.filename.decode(),
                        size=file.size,
                        path=(path + file.filename.decode()),
                        link_type=link_type,
                        date_time=datetime.datetime.utcfromtimestamp(file.mtime),
                        permissions=permissions,
                    )
                )

            return files, None

        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
            return files, error

    @classmethod
    def rename(cls, file: File, name: str) -> Tuple[str, str]:
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        if '/' in name or '\\' in name:
            return None, "Invalid name"

        try:
            args = [ShellCommand.MV, file.path, file.location + name]
            response = PythonADBManager.device.shell(shlex.join(args))
            if response:
                return None, response
            return None, None
        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
            return None, error

    @classmethod
    def open_file(cls, file: File) -> Tuple[str, str]:
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        try:
            args = [ShellCommand.CAT, shlex.quote(file.path)]
            if file.isdir:
                return None, f"Can't open. {file.path} is a directory"
            response = PythonADBManager.device.shell(shlex.join(args))
            return response, None
        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
            return None, error

    @classmethod
    def delete(cls, file: File) -> Tuple[str, str]:
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"
        try:
            args = [ShellCommand.RM, file.path]
            if file.isdir:
                args = ShellCommand.RM_DIR_FORCE + [file.path]
            response = PythonADBManager.device.shell(shlex.join(args))
            if response:
                return None, response
            return f"{'Folder' if file.isdir else 'File'} '{file.path}' has been deleted", None
        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
            return None, error

    class UpDownHelper:
        def __init__(self, callback: callable):
            self.callback = callback
            self.written = 0
            self.total = 0

        def call(self, path: str, written: int, total: int):
            if self.total != total:
                self.total = total
                self.written = 0

            self.written += written
            self.callback(path, int(self.written / self.total * 100))

    @classmethod
    def download(cls, progress_callback: callable, source: File, destination: str = None, delete_too: bool = False) -> Tuple[str, str]:
        if not destination:
            destination = Settings.get_value(SettingsOptions.DOWNLOAD_PATH, PythonADBManager.get_device())
            destination = destination.replace(" ", "_")

        helper = cls.UpDownHelper(progress_callback)
        destination = os.path.join(destination, os.path.basename(os.path.normpath(source)))
        if PythonADBManager.device and PythonADBManager.device.available and source:
            try:
                PythonADBManager.device.pull(
                    device_path=source.path,
                    local_path=destination,
                    progress_callback=helper.call
                )
                return f"Download successful!\nDest: {destination}", None
            except BaseException as error:
                logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
                return None, error
        return None, None

    @classmethod
    def new_folder(cls, name) -> Tuple[str, str]:
        if not PythonADBManager.device:
            return None, "No device selected!"
        if not PythonADBManager.device.available:
            return None, "Device not available!"

        try:
            args = [ShellCommand.MKDIR, (PythonADBManager.get_current_path() + name)]
            response = PythonADBManager.device.shell(shlex.join(args))
            return None, response

        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
            return None, error

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> Tuple[str, str]:
        helper = cls.UpDownHelper(progress_callback)
        destination = PythonADBManager.get_current_path() + os.path.basename(os.path.normpath(source))
        if PythonADBManager.device and PythonADBManager.device.available and PythonADBManager.get_current_path() and source:
            try:
                PythonADBManager.device.push(
                    local_path=source,
                    device_path=destination,
                    progress_callback=helper.call
                )
                return f"Upload successful!\nDest: {destination}", None
            except BaseException as error:
                logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
                return None, error
        return None, None


class DeviceRepository:
    @classmethod
    def devices(cls) -> Tuple[List[Device], str]:
        if PythonADBManager.device:
            PythonADBManager.device.close()

        errors = []
        devices = []
        for device in USBContext().getDeviceList(skip_on_error=True):
            for setting in device.iterSettings():
                if (setting.getClass(), setting.getSubClass(), setting.getProtocol()) == (0xFF, 0x42, 0x01):
                    try:
                        device_id = device.getSerialNumber()
                        PythonADBManager.connect(device_id)
                        device_name = " ".join(
                            PythonADBManager.device.shell(" ".join(ShellCommand.GETPROP_PRODUCT_MODEL)).split()
                        )
                        device_type = "device" if PythonADBManager.device.available else "unknown"
                        devices.append(Device(id=device_id, name=device_name, type=device_type))
                        PythonADBManager.device.close()
                    except BaseException as error:
                        logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
                        errors.append(str(error))

        return devices, str("\n".join(errors))

    @classmethod
    def connect(cls, device_id: str) -> Tuple[str, str]:
        try:
            if PythonADBManager.device:
                PythonADBManager.device.close()
            serial = PythonADBManager.connect(device_id)
            if PythonADBManager.device.available:
                device_name = " ".join(
                    PythonADBManager.device.shell(" ".join(ShellCommand.GETPROP_PRODUCT_MODEL)).split()
                )
                PythonADBManager.set_device(Device(id=serial, name=device_name, type="device"))
                return "Connection established", None
            return None, "Device not available"

        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
            return None, error

    @classmethod
    def disconnect(cls) -> Tuple[str, str]:
        try:
            if PythonADBManager.device:
                PythonADBManager.device.close()
                return "Disconnected", None
            return None, None
        except BaseException as error:
            logging.exception("Unexpected error=%s, type(error)=%s", error, type(error))
            return None, error
