# ADB File Explorer
# Copyright (C) 2023  aakbar5

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QLineEdit,
    QVBoxLayout,
    QCheckBox,
    QComboBox,
    QGroupBox,
    QRadioButton,
    QGridLayout
)
from app.core.settings import SettingsOptions, Settings

class PerferenceDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferences...")
        dlgLayout = QGridLayout()
        self.setLayout(dlgLayout)

        # -------------------
        # Startup settings
        startupSettingsGrpBox = QGroupBox("Startup")
        dlgLayout.addWidget(startupSettingsGrpBox)

        startupSettingsGrpBoxLayout = QFormLayout()
        startupSettingsGrpBox.setLayout(startupSettingsGrpBoxLayout)

        options = ['python', 'external']
        self.widget_adb_core = QComboBox()
        self.widget_adb_core.addItems(options)
        idx = options.index(Settings.get_value(SettingsOptions.ADB_CORE))
        self.widget_adb_core.setCurrentIndex(idx)
        startupSettingsGrpBoxLayout.addRow("Adb core:", self.widget_adb_core)

        self.widget_adb_path = QLineEdit()
        self.widget_adb_path.setText(Settings.get_value(SettingsOptions.ADB_PATH))
        startupSettingsGrpBoxLayout.addRow("ADB path:", self.widget_adb_path)

        self.widget_notification_timeout = QLineEdit()
        self.widget_notification_timeout.setValidator(QIntValidator())
        val = Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT)
        self.widget_notification_timeout.setText(str(val))
        startupSettingsGrpBoxLayout.addRow("Notification timeout (ms):", self.widget_notification_timeout)

        self.widget_show_welcome = QCheckBox(self.tr('Show welcome on startup'), self)
        if Settings.get_value(SettingsOptions.SHOW_WELCOME_MSG) == True:
            self.widget_show_welcome.setChecked(True)
        startupSettingsGrpBoxLayout.addWidget(self.widget_show_welcome)

        self.widget_win_geometry = QCheckBox(self.tr('Restore window geometry'), self)
        if Settings.get_value(SettingsOptions.RESTORE_WIN_GEOMETRY) == True:
            self.widget_win_geometry.setChecked(True)
        startupSettingsGrpBoxLayout.addWidget(self.widget_win_geometry)

        self.widget_adb_kill_server_at_exit = QCheckBox(self.tr('ADB Kill server at exit'), self)
        if Settings.get_value(SettingsOptions.ADB_KILL_AT_EXIT) == True:
            self.widget_adb_kill_server_at_exit.setChecked(True)
        startupSettingsGrpBoxLayout.addWidget(self.widget_adb_kill_server_at_exit)

        self.widget_preserve_timestamp = QCheckBox(self.tr('Preserve timestamp'), self)
        if Settings.get_value(SettingsOptions.PRESERVE_TIMESTAMP) == True:
            self.widget_preserve_timestamp.setChecked(True)
        startupSettingsGrpBoxLayout.addWidget(self.widget_preserve_timestamp)

        self.widget_adb_as_root = QCheckBox(self.tr('ADB as root'), self)
        if Settings.get_value(SettingsOptions.ADB_AS_ROOT) == True:
            self.widget_adb_as_root.setChecked(True)
        startupSettingsGrpBoxLayout.addWidget(self.widget_adb_as_root)

        # -------------------
        # Dialog buttons
        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btnBox.accepted.connect(self.accept)
        btnBox.rejected.connect(self.reject)
        dlgLayout.addWidget(btnBox)
