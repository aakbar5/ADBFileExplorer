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
    QGridLayout,
    QPushButton,
    QLabel,
    QFileDialog
)
from app.core.settings import SettingsOptions, Settings
from pathlib import Path

class PerferenceDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferences...")
        dlgLayout = QGridLayout()
        self.setLayout(dlgLayout)

        # -------------------
        # ADB Settings
        adbSettingsGrpBox = QGroupBox("ADB")
        dlgLayout.addWidget(adbSettingsGrpBox)

        adbSettingsGrpBoxLayout = QFormLayout()
        adbSettingsGrpBox.setLayout(adbSettingsGrpBoxLayout)

        options = ['python', 'external']
        self.widget_adb_core = QComboBox()
        self.widget_adb_core.addItems(options)
        idx = options.index(Settings.get_value(SettingsOptions.ADB_CORE))
        self.widget_adb_core.setCurrentIndex(idx)
        adbSettingsGrpBoxLayout.addRow("Adb core:", self.widget_adb_core)

        self.widget_adb_path = QLineEdit()
        self.widget_adb_path.setText(Settings.get_value(SettingsOptions.ADB_PATH))
        adbSettingsGrpBoxLayout.addRow("ADB path:", self.widget_adb_path)

        self.widget_adb_kill_server_at_exit = QCheckBox(self.tr('ADB Kill server at exit'), self)
        if Settings.get_value(SettingsOptions.ADB_KILL_AT_EXIT) == True:
            self.widget_adb_kill_server_at_exit.setChecked(True)
        adbSettingsGrpBoxLayout.addWidget(self.widget_adb_kill_server_at_exit)

        self.widget_adb_as_root = QCheckBox(self.tr('ADB as root'), self)
        if Settings.get_value(SettingsOptions.ADB_AS_ROOT) == True:
            self.widget_adb_as_root.setChecked(True)
        adbSettingsGrpBoxLayout.addWidget(self.widget_adb_as_root)


        # -------------------
        downloadSettingsGrpBox = QGroupBox("")
        dlgLayout.addWidget(downloadSettingsGrpBox)

        downloadSettingsGrpBoxLayout = QGridLayout()
        downloadSettingsGrpBox.setLayout(downloadSettingsGrpBoxLayout)

        # file selection
        file_browse = QPushButton('Browse')
        file_browse.clicked.connect(self.open_dir_dialog)
        self.download_dir_name = QLineEdit()
        self.download_dir_name.setText(Settings.get_value(SettingsOptions.DOWNLOAD_PATH))

        downloadSettingsGrpBoxLayout.addWidget(QLabel('Download folder'), 0, 0)
        downloadSettingsGrpBoxLayout.addWidget(self.download_dir_name, 0, 1)
        downloadSettingsGrpBoxLayout.addWidget(file_browse, 0 ,2)

        # -------------------
        adbKeySettingsGrpBox = QGroupBox("")
        dlgLayout.addWidget(adbKeySettingsGrpBox)

        adbKeySettingsGrpBoxLayout = QGridLayout()
        adbKeySettingsGrpBox.setLayout(adbKeySettingsGrpBoxLayout)

        # file selection
        file_browse = QPushButton('Browse')
        file_browse.clicked.connect(self.open_file_dialog)
        self.adb_key_file_name = QLineEdit()
        self.adb_key_file_name.setText(Settings.get_value(SettingsOptions.ADB_KEY_FILE_PATH))

        adbKeySettingsGrpBoxLayout.addWidget(QLabel('Adb key file'), 0, 0)
        adbKeySettingsGrpBoxLayout.addWidget(self.adb_key_file_name, 0, 1)
        adbKeySettingsGrpBoxLayout.addWidget(file_browse, 0 ,2)

        # -------------------
        # Startup settings
        startupSettingsGrpBox = QGroupBox("Startup")
        dlgLayout.addWidget(startupSettingsGrpBox)

        startupSettingsGrpBoxLayout = QFormLayout()
        startupSettingsGrpBox.setLayout(startupSettingsGrpBoxLayout)

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

        self.widget_preserve_timestamp = QCheckBox(self.tr('Preserve timestamp'), self)
        if Settings.get_value(SettingsOptions.PRESERVE_TIMESTAMP) == True:
            self.widget_preserve_timestamp.setChecked(True)
        startupSettingsGrpBoxLayout.addWidget(self.widget_preserve_timestamp)

        # -------------------
        # General settings
        generalSettingsGrpBox = QGroupBox("General")
        dlgLayout.addWidget(generalSettingsGrpBox)

        generalSettingsGrpBoxLayout = QFormLayout()
        generalSettingsGrpBox.setLayout(generalSettingsGrpBoxLayout)

        self.statusbar_update_time = QLineEdit()
        self.statusbar_update_time.setValidator(QIntValidator())
        val = Settings.get_value(SettingsOptions.STATUSBAR_UPDATE_TIME)
        self.statusbar_update_time.setText(str(val))
        generalSettingsGrpBoxLayout.addRow("Update status bar (ms):", self.statusbar_update_time)

        options = ['Informal', 'ISO', 'Locale (24 Hours)', 'Locale (12 Hours)']
        idx = options.index(Settings.get_value(SettingsOptions.FILE_DATE_FORMAT))
        self.widget_date_format = QComboBox()
        self.widget_date_format.addItems(options)
        self.widget_date_format.setCurrentIndex(idx)
        generalSettingsGrpBoxLayout.addRow("File timestamp:", self.widget_date_format)

        # -------------------
        # Dialog buttons
        btnBox = QDialogButtonBox()
        btnBox.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btnBox.accepted.connect(self.accept)
        btnBox.rejected.connect(self.reject)
        dlgLayout.addWidget(btnBox)

    def open_file_dialog(self):
        filename, ok = QFileDialog.getOpenFileName(self, "Select a File", "", "*")
        if filename:
            path = Path(filename)
            self.adb_key_file_name.setText(str(path))

    def open_dir_dialog(self):
        dir_name = QFileDialog.getExistingDirectory(self, "Select a Directory")
        if dir_name:
            path = Path(dir_name)
            self.download_dir_name.setText(str(path))
