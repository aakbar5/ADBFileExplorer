# ADB File Explorer
# Copyright (C) 2023  aakbar5

from pathlib import Path

from PyQt5.QtGui import QIntValidator
from PyQt5.QtWidgets import (QCheckBox, QComboBox, QDialog, QDialogButtonBox,
                             QFileDialog, QFormLayout, QGridLayout, QGroupBox,
                             QLineEdit, QHBoxLayout, QPushButton, QWidget)

from app.core.settings import SettingsOptions, Settings


class PerferenceDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Preferences...")
        dlg_layout = QGridLayout()
        self.setLayout(dlg_layout)

        # -------------------
        # ADB Settings
        adb_settings_grp_box = QGroupBox("ADB")
        dlg_layout.addWidget(adb_settings_grp_box)

        adb_settings_grp_box_layout = QFormLayout()
        adb_settings_grp_box.setLayout(adb_settings_grp_box_layout)

        options = ['python', 'external']
        self.widget_adb_core = QComboBox()
        self.widget_adb_core.addItems(options)
        idx = options.index(Settings.get_value(SettingsOptions.ADB_CORE))
        self.widget_adb_core.setCurrentIndex(idx)
        adb_settings_grp_box_layout.addRow("Adb core:", self.widget_adb_core)

        self.widget_adb_path = QLineEdit()
        self.widget_adb_path.setText(Settings.get_value(SettingsOptions.ADB_PATH))
        adb_settings_grp_box_layout.addRow("ADB path:", self.widget_adb_path)

        self.widget_adb_as_root = QCheckBox(self.tr('ADB as root'), self)
        if Settings.get_value(SettingsOptions.ADB_AS_ROOT) is True:
            self.widget_adb_as_root.setChecked(True)

        self.widget_adb_kill_server_at_exit = QCheckBox(self.tr('ADB Kill server at exit'), self)
        if Settings.get_value(SettingsOptions.ADB_KILL_AT_EXIT) is True:
            self.widget_adb_kill_server_at_exit.setChecked(True)

        adb_settings_grp_box_layout.addRow(self.widget_adb_as_root, self.widget_adb_kill_server_at_exit)

        # -- ADB key file
        self.adb_key_grp_box_layout = QGridLayout()

        file_browse = QPushButton('Browse')
        file_browse.clicked.connect(self.open_file_dialog)
        self.adb_key_file_name = QLineEdit()
        self.adb_key_file_name.setText(Settings.get_value(SettingsOptions.ADB_KEY_FILE_PATH))

        self.adb_key_grp_box_layout.addWidget(self.adb_key_file_name, 0, 0)
        self.adb_key_grp_box_layout.addWidget(file_browse, 0, 1)
        adb_settings_grp_box_layout.addRow("Adb key file", self.adb_key_grp_box_layout)

        # -------------------
        # General settings
        general_grp_box = QGroupBox("General")
        dlg_layout.addWidget(general_grp_box)

        general_grp_box_layout = QFormLayout()
        general_grp_box.setLayout(general_grp_box_layout)

        self.widget_notification_timeout = QLineEdit()
        self.widget_notification_timeout.setValidator(QIntValidator())
        val = Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT)
        self.widget_notification_timeout.setText(str(val))
        general_grp_box_layout.addRow("Notification timeout (ms):", self.widget_notification_timeout)

        self.statusbar_update_time = QLineEdit()
        self.statusbar_update_time.setValidator(QIntValidator())
        val = Settings.get_value(SettingsOptions.STATUSBAR_UPDATE_TIME)
        self.statusbar_update_time.setText(str(val))
        general_grp_box_layout.addRow("Update status bar (ms):", self.statusbar_update_time)

        self.widget_show_welcome = QCheckBox(self.tr('Show welcome on startup'), self)
        if Settings.get_value(SettingsOptions.SHOW_WELCOME_MSG) is True:
            self.widget_show_welcome.setChecked(True)

        self.widget_win_geometry = QCheckBox(self.tr('Restore window geometry'), self)
        if Settings.get_value(SettingsOptions.RESTORE_WIN_GEOMETRY) is True:
            self.widget_win_geometry.setChecked(True)
        general_grp_box_layout.addRow(self.widget_show_welcome, self.widget_win_geometry)

        self.widget_preserve_timestamp = QCheckBox(self.tr('Preserve timestamp'), self)
        if Settings.get_value(SettingsOptions.PRESERVE_TIMESTAMP) is True:
            self.widget_preserve_timestamp.setChecked(True)
        general_grp_box_layout.addRow(self.widget_preserve_timestamp)

        # -- Download folder group
        self.download_folder_grp_box_layout = QGridLayout()

        folder_browse = QPushButton('Browse')
        folder_browse.clicked.connect(self.open_dir_dialog)
        self.download_dir_name = QLineEdit()
        self.download_dir_name.setText(Settings.get_value(SettingsOptions.DOWNLOAD_PATH))

        self.download_folder_grp_box_layout.addWidget(self.download_dir_name, 0, 0)
        self.download_folder_grp_box_layout.addWidget(folder_browse, 0, 1)
        general_grp_box_layout.addRow("Download folder", self.download_folder_grp_box_layout)

        # -------------------
        # View settings
        view_settings_grp_box = QGroupBox("File view")
        dlg_layout.addWidget(view_settings_grp_box)

        view_settings_grp_box_layout = QFormLayout()
        view_settings_grp_box.setLayout(view_settings_grp_box_layout)

        options = ['Informal', 'ISO', 'Locale (24 Hours)', 'Locale (12 Hours)']
        idx = options.index(Settings.get_value(SettingsOptions.FILE_DATE_FORMAT))
        self.widget_date_format = QComboBox()
        self.widget_date_format.addItems(options)
        self.widget_date_format.setCurrentIndex(idx)
        view_settings_grp_box_layout.addRow("File timestamp:", self.widget_date_format)

        self.widget_sort_folders_before_file = QCheckBox(self.tr('Sort folders before files'), self)
        if Settings.get_value(SettingsOptions.SORT_FOLDERS_BEFORE_FILES) is True:
            self.widget_sort_folders_before_file.setChecked(True)
        view_settings_grp_box_layout.addWidget(self.widget_sort_folders_before_file)

        # HEADER = ['File', 'Permissions', 'Size', 'Date', 'MimeType']
        self.header_permission = QCheckBox(self.tr('Permission'), self)
        if Settings.get_value(SettingsOptions.HEADER_PERMISSION) is True:
            self.header_permission.setChecked(True)

        self.header_size = QCheckBox(self.tr('Size'), self)
        if Settings.get_value(SettingsOptions.HEADER_SIZE) is True:
            self.header_size.setChecked(True)

        self.header_date = QCheckBox(self.tr('Date'), self)
        if Settings.get_value(SettingsOptions.HEADER_DATE) is True:
            self.header_date.setChecked(True)

        self.header_mime_type = QCheckBox(self.tr('MimeType'), self)
        if Settings.get_value(SettingsOptions.HEADER_MIME_TYPE) is True:
            self.header_mime_type.setChecked(True)

        self.header_widget_layout = QHBoxLayout()
        self.header_widget_layout.addWidget(self.header_permission)
        self.header_widget_layout.addWidget(self.header_size)
        self.header_widget_layout.addWidget(self.header_date)
        self.header_widget_layout.addWidget(self.header_mime_type)

        self.header_widget = QWidget()
        self.header_widget.setLayout(self.header_widget_layout)
        view_settings_grp_box_layout.addWidget(self.header_widget)

        # -------------------
        # Dialog buttons
        btns_box = QDialogButtonBox()
        btns_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns_box.accepted.connect(self.accept)
        btns_box.rejected.connect(self.reject)
        dlg_layout.addWidget(btns_box)

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
