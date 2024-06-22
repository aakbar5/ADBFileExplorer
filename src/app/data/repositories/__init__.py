# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
from typing import List, Tuple

from app.core.adb import Adb
from app.data.models import Device, File
from app.data.repositories import android_adb, python_adb


class FileRepository:
    @classmethod
    def IsAndroidRoot(cls) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.IsAndroidRoot()
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.IsAndroidRoot()

    @classmethod
    def AndroidVersion(cls) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.AndroidVersion()
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.AndroidVersion()

    @classmethod
    def file(cls, path: str) -> Tuple[File, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.file(path=path)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.file(path=path)

    @classmethod
    def files(cls) -> Tuple[List[File], str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.files()
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.files()

    @classmethod
    def rename(cls, file: File, name: str) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.rename(file, name)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.rename(file, name)

    @classmethod
    def open_file(cls, file: File) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.open_file(file)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.open_file(file)

    @classmethod
    def delete(cls, file: File) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.delete(file)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.delete(file)

    @classmethod
    def download(cls, progress_callback: callable, source: File, destination: str, delete_too: bool) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.download(
                progress_callback=progress_callback,
                source=source,
                destination=destination,
                delete_too=delete_too
            )
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.download(
                progress_callback=progress_callback,
                source=source,
                destination=destination,
                delete_too=delete_too
            )

    @classmethod
    def new_folder(cls, name) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.new_folder(name=name)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.new_folder(name=name)

    @classmethod
    def upload(cls, progress_callback: callable, source: str) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.FileRepository.upload(
                progress_callback=progress_callback,
                source=source
            )


class DeviceRepository:
    @classmethod
    def devices(cls) -> Tuple[List[Device], str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.devices()
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.devices()

    @classmethod
    def connect(cls, device_id) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.connect(device_id=device_id)
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.connect(device_id=device_id)

    @classmethod
    def disconnect(cls) -> Tuple[str, str]:
        if Adb.core == Adb.PYTHON_ADB_SHELL:
            return python_adb.DeviceRepository.disconnect()
        elif Adb.core == Adb.EXTERNAL_TOOL_ADB:
            return android_adb.DeviceRepository.disconnect()
