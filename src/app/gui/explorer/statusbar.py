# ADB File Explorer
# Copyright (C) 2023  aakbar5

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout

from app.core.resources import Resources
from app.core.managers import Global

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
