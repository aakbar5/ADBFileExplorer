# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import logging
import posixpath
import os

from PyQt5.QtCore import QObject
from adb_shell.adb_device import AdbDeviceTcp, AdbDeviceUsb

from app.data.models import File, Device
from app.helpers.tools import Communicate, get_python_rsa_keys_signer, AsyncRepositoryWorker
from app.helpers.singleton import Singleton


class ADBManager:
    __metaclass__ = Singleton

    default_path = "/"

    __device = None

    __paths = []
    __pathIndex = -1

    @staticmethod
    def normalized_path(path: str) -> str:
        if not path or len(path) == 0:
            return ADBManager.default_path

        path = os.path.normcase(path)
        path = os.path.normpath(path)
        path = posixpath.normpath(path)
        if not path.endswith("/"):
            path += "/"
        return path

    @staticmethod
    def remove_entries(ls, lo, hi):
        res = ls
        for idx, _ in enumerate(ls):
            if idx in range(lo, hi + 1):
                res.pop(idx)
        return res

    @classmethod
    def reset(cls) -> bool:
        cls.__paths = []
        cls.__pathIndex = -1
        return True

    @classmethod
    def get_all_paths(cls) -> list:
        return cls.__paths

    @classmethod
    def is_back(cls) -> bool:
        return cls.__pathIndex > 0;

    @classmethod
    def is_forward(cls) -> bool:
        return cls.__pathIndex < len(cls.__paths) - 1;

    @classmethod
    def go_forward(cls) -> str:
        if not cls.is_forward():
            return None

        cls.__pathIndex += 1
        return cls.__paths[cls.__pathIndex]

    @classmethod
    def go_back(cls) -> str:
        if not cls.is_back():
            return None

        cls.__pathIndex -= 1
        return cls.__paths[cls.__pathIndex];

    @classmethod
    def go_home(cls) -> str:
        return cls.set_current_path(ADBManager.default_path)

    @classmethod
    def go_up(cls) -> bool:
        cpath = cls.get_current_path()
        if cpath:
            cpath = os.path.normpath(cpath)

            tokens = cpath.split(os.sep)
            tokens.pop()
            npath = '/'.join(tokens)

            if len(npath) == 0:
                npath = ADBManager.default_path

            if cls.set_current_path(npath):
                return True

        return False

    @classmethod
    def get_current_path(cls) -> str:
        if len(cls.__paths) > 0:
            return cls.__paths[cls.__pathIndex]

        return ADBManager.default_path

    @classmethod
    def set_current_path(cls, file) -> str:
        new_path = ADBManager.default_path

        if not file:
            print(f"set_current_path: file object is not valid")
            return new_path

        if isinstance(file, File):
            new_path = file.path
        elif isinstance(file, str):
            new_path = file
        else:
            return new_path

        count = len(cls.__paths)
        if count > 0:
            top_path = cls.__paths[cls.__pathIndex]
            if new_path == top_path:
                return new_path

        if cls.is_forward():
            start = cls.__pathIndex + 1
            end = count - cls.__pathIndex - 1
            cls.__paths = cls.remove_entries(cls.__paths, start, end)

        new_path = ADBManager.normalized_path(new_path)
        cls.__paths.append(new_path)
        cls.__pathIndex += 1
        return new_path

    @classmethod
    def get_device(cls) -> Device:
        return cls.__device

    @classmethod
    def set_device(cls, device: Device) -> bool:
        if device:
            cls.clear_device()
            cls.__device = device
            return True

    @classmethod
    def clear_device(cls):
        cls.__device = None
        cls.reset()


class PythonADBManager(ADBManager):
    signer = get_python_rsa_keys_signer()
    device = None

    @classmethod
    def connect(cls, device_id: str) -> str:
        if device_id.__contains__('.'):
            port = 5555
            host = device_id
            if device_id.__contains__(':'):
                host = device_id.split(':')[0]
                port = device_id.split(':')[1]
            cls.device = AdbDeviceTcp(host=host, port=port, default_transport_timeout_s=10.)
            cls.device.connect(rsa_keys=[cls.signer], auth_timeout_s=1.)
            return '%s:%s' % (host, port)

        cls.device = AdbDeviceUsb(serial=device_id, default_transport_timeout_s=3.)
        cls.device.connect(rsa_keys=[cls.signer], auth_timeout_s=30.)
        return device_id

    @classmethod
    def set_device(cls, device: Device) -> bool:
        super(PythonADBManager, cls).set_device(device)
        if not cls.device or not cls.device.available:
            try:
                cls.connect(device.id)
                return True
            except BaseException as error:
                logging.error(error)
                return False


class WorkersManager:
    """
    Async Workers Manager
    Contains a list of workers
    """
    __metaclass__ = Singleton
    instance = QObject()
    workers = []

    @classmethod
    def work(cls, worker: AsyncRepositoryWorker) -> bool:
        for _worker in cls.workers:
            if _worker == worker or _worker.id == worker.id:
                cls.workers.remove(_worker)
                del _worker
                break
        worker.setParent(cls.instance)
        cls.workers.append(worker)
        return True

    @classmethod
    def check(cls, worker_id: int) -> bool:
        for worker in cls.workers:
            if worker.id == worker_id:
                if worker.closed:
                    return True
                return False
        return False


class Global:
    __metaclass__ = Singleton
    communicate = Communicate()
