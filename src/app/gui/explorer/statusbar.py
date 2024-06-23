# ADB File Explorer
# Copyright (C) 2023  aakbar5

import threading

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QObject, QSize, pyqtSignal
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout

from app.data.repositories import FileRepository
from app.core.resources import Resources
from app.core.managers import Global

class AndroidBatteryWidget(QWidget):
    HorizontalSpacing = 2
    IconSize = QSize(16, 16)

    def __init__(self, final_stretch=False):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.icon = QLabel()
        self.icon.setVisible(False)

        layout.addWidget(self.icon)
        layout.addSpacing(self.HorizontalSpacing)

        self.text_widget = QLabel("")
        layout.addWidget(self.text_widget)

        if final_stretch:
            layout.addStretch()

        Global().communicate.status_bar_battery_level.connect(self.update_text)

    def update_text(self, text_level, text_status):
        text_level = text_level.strip()
        text_status = text_status.strip()
        if len(text_level) == 0 or len(text_status) == 0:
            self.icon.setVisible(False)
        else:
            # Ref: https://developer.android.com/reference/android/hardware/BatteryState
            BATTERY_STATUS_FULL         = 5
            BATTERY_STATUS_NOT_CHARGING = 4
            BATTERY_STATUS_DISCHARGING  = 3
            BATTERY_STATUS_CHARGING     = 2
            BATTERY_STATUS_UNKNOWN      = 1

            int_level = int(text_level)
            int_status = int(text_status)

            battery_sts = "??"
            if int_status == BATTERY_STATUS_UNKNOWN:
                battery_sts = "??"
                battery_icon = QIcon(Resources.icon_battery_xx).pixmap(self.IconSize)
            elif int_status == BATTERY_STATUS_FULL:
                battery_sts = "100%"
                battery_icon = QIcon(Resources.icon_battery_100).pixmap(self.IconSize)
            elif int_status == BATTERY_STATUS_CHARGING:
                if int_level >= 1 and int_level <= 10:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_charging_10).pixmap(self.IconSize)
                elif int_level >= 11 and int_level <= 20:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_charging_20).pixmap(self.IconSize)
                elif int_level >= 21 and int_level <= 40:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_charging_40).pixmap(self.IconSize)
                elif int_level >= 41 and int_level <= 60:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_charging_60).pixmap(self.IconSize)
                elif int_level >= 61 and int_level <= 80:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_charging_80).pixmap(self.IconSize)
                elif int_level >= 81 and int_level <= 99:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_charging_90).pixmap(self.IconSize)
            elif int_status == BATTERY_STATUS_NOT_CHARGING:
                if int_level >= 1 and int_level <= 10:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_normal_10).pixmap(self.IconSize)
                elif int_level >= 11 and int_level <= 20:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_normal_20).pixmap(self.IconSize)
                elif int_level >= 21 and int_level <= 40:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_normal_40).pixmap(self.IconSize)
                elif int_level >= 41 and int_level <= 60:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_normal_60).pixmap(self.IconSize)
                elif int_level >= 61 and int_level <= 80:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_normal_80).pixmap(self.IconSize)
                elif int_level >= 81 and int_level <= 99:
                    battery_sts = f"{int_level}%".ljust(5)
                    battery_icon = QIcon(Resources.icon_battery_normal_90).pixmap(self.IconSize)

            self.icon.setPixmap(battery_icon)
            self.icon.setVisible(True)
            self.text_widget.setText(battery_sts)

class IsAndroidRootWidget(QWidget):
    IconSize = QSize(16, 16)
    HorizontalSpacing = 2

    def __init__(self, final_stretch=False):
        super(QWidget, self).__init__()

        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        self.IconLock = QIcon(Resources.icon_lock).pixmap(self.IconSize)
        self.IconUnlock = QIcon(Resources.icon_unlock).pixmap(self.IconSize)

        self.icon = QLabel()
        self.icon.setVisible(False)
        layout.addWidget(self.icon)
        layout.addSpacing(self.HorizontalSpacing)

        self.text_widget = QLabel("")
        layout.addWidget(self.text_widget)

        if final_stretch:
            layout.addStretch()

        Global().communicate.status_bar_is_root.connect(self.update_text)

    def update_text(self, integer):
        text = "User"
        icon = self.IconLock

        if integer == 0:
            text = "Root"
            icon = self.IconUnlock

        self.icon.setPixmap(icon)
        self.icon.setVisible(True)
        self.text_widget.setText(text)

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

    def __init__(self, delay_mseconds=1000):
        QObject.__init__(self)
        print("DeviceStatusThread init is called...")

        self._delay_sec = delay_mseconds / 1000
        self._stop_event = threading.Event()
        threading.Thread.__init__(self)

    def run(self):
        while not self._stop_event.isSet():
            data_level, data_sts = FileRepository.DeviceBatteryLevel()
            if data_level:
                lines_level = data_level.splitlines()
            if data_sts:
                lines_sts = data_sts.splitlines()
            Global().communicate.status_bar_battery_level.emit(lines_level[0], lines_sts[0])

            self._stop_event.wait(self._delay_sec)

        print("DeviceStatusThread is finished...")
        self.finished.emit()

    def stop(self):
        self._stop_event.set()
