# ADB File Explorer
# Copyright (C) 2023  aakbar5

import threading

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QSize, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout

from app.data.repositories import FileRepository
from app.core.resources import Resources
from app.core.managers import Global

class AndroidVersionWidget(QWidget):
    IconResource = Resources.icon_android
    IconSize = QSize(16, 16)
    HorizontalSpacing = 2

    def __init__(self, final_stretch=False):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.icon = QLabel()
        self.icon.setPixmap(QIcon(self.IconResource).pixmap(self.IconSize))
        self.icon.setVisible(False)
        layout.addWidget(self.icon)
        layout.addSpacing(self.HorizontalSpacing)

        self.text_widget = QLabel("")
        layout.addWidget(self.text_widget)

        if final_stretch:
            layout.addStretch()

        Global().communicate.status_bar_android_version.connect(self.update_text)

    def update_text(self, text):
        text = text.strip()
        if len(text) == 0:
            self.icon.setVisible(False)
        else:
            text = f"Android: {text}".ljust(15)
            self.icon.setVisible(True)
            self.text_widget.setText(text)

class DeviceLabelWidget(QWidget):
    IconResource = Resources.icon_tag
    IconSize = QSize(16, 16)
    HorizontalSpacing = 2

    def __init__(self, final_stretch=False):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.icon = QLabel()
        self.icon.setPixmap(QIcon(self.IconResource).pixmap(self.IconSize))
        self.icon.setVisible(False)
        layout.addWidget(self.icon)
        layout.addSpacing(self.HorizontalSpacing)

        self.text_widget = QLabel("")
        layout.addWidget(self.text_widget)

        if final_stretch:
            layout.addStretch()

        Global().communicate.status_bar_device_label.connect(self.update_text)

    def update_text(self, text):
        text = text.strip()
        if len(text) == 0:
            self.icon.setVisible(False)
        else:
            text = f"{text}".ljust(15)
            self.icon.setVisible(True)
            self.text_widget.setText(text)

class DeviceStatusThread(threading.Thread, QObject):
    finished = pyqtSignal()

    def __init__(self, delay_seconds=4):
        QObject.__init__(self)
        print("DeviceStatusThread init is called...")

        self._delay = delay_seconds
        self._stop_event = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        while not self._stop_event.isSet():
            data, _ = FileRepository.AndroidVersion()
            if data:
                lines = data.splitlines()
            Global().communicate.status_bar_android_version.emit(lines[0])

            self._stop_event.wait(self._delay)

        print("DeviceStatusThread is finished...")
        self.finished.emit()

    def stop(self):
        self._stop_event.set()
