# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

from typing import List, Tuple

from app.core.adb import Adb
from app.data.models import Device, File
from app.data.repositories import android_adb, python_adb


class FileRepository:
    @classmethod
    def capture_screenshot(cls) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.capture_screenshot()
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.capture_screenshot()
        return None

    @classmethod
    def battery_level(cls) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.battery_level()
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.battery_level()
        return None

    @classmethod
    def is_android_root(cls) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.is_android_root()
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.is_android_root()
        return None

    @classmethod
    def android_version(cls) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.android_version()
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.android_version()
        return None

    @classmethod
    def file(cls, path: str) -> Tuple[File, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.file(path=path)
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.file(path=path)
        return None

    @classmethod
    def files(cls) -> Tuple[List[File], str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.files()
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.files()
        return None

    @classmethod
    def rename(cls, file: File, name: str) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.rename(file, name)
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.rename(file, name)
        return None

    @classmethod
    def open_file(cls, file: File) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.open_file(file)
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.open_file(file)
        return None

    @classmethod
    def delete(cls, file: File) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.delete(file)
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.delete(file)
        return None

    @classmethod
    def download(cls, progress_callback: callable, source: File, destination: str, delete_too: bool) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.download(
                progress_callback=progress_callback,
                source=source,
                destination=destination,
                delete_too=delete_too
            )
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.download(
                progress_callback=progress_callback,
                source=source,
                destination=destination,
                delete_too=delete_too
            )
        return None

    @classmethod
    def new_folder(cls, name) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.new_folder(name=name)
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.new_folder(name=name)
        return None

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )
        return None

class DeviceRepository:
    @classmethod
    def devices(cls) -> Tuple[List[Device], str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.devices()
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.devices()
        return None

    @classmethod
    def connect(cls, device_id) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.connect(device_id=device_id)
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.connect(device_id=device_id)
        return None

    @classmethod
    def disconnect(cls) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.disconnect()
        if Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.disconnect()
        return None
