# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
from PyQt5.QtCore import QObject, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QToolButton, QMenu, QWidget, QAction, QFileDialog, QInputDialog, QLineEdit, QHBoxLayout

from app.core.resources import Resources
from app.core.settings import SettingsOptions, Settings
from app.core.adb import Adb
from app.core.managers import Global
from app.data.models import MessageData, MessageType
from app.data.repositories import FileRepository
from app.helpers.tools import AsyncRepositoryWorker, ProgressCallbackHelper


class UploadTools(QToolButton):
    def __init__(self, parent):
        super(UploadTools, self).__init__(parent)
        self.menu = QMenu(self)
        self.uploader = self.FilesUploader()

        self.show_action = QAction(QIcon(Resources.icon_upload), 'Upload', self)
        self.show_action.triggered.connect(self.showMenu)
        self.setDefaultAction(self.show_action)

        upload_files = QAction(QIcon(Resources.icon_files_upload), '&Upload files', self)
        upload_files.triggered.connect(self.__action_upload_files__)
        self.menu.addAction(upload_files)

        upload_directory = QAction(QIcon(Resources.icon_folder_upload), '&Upload directory', self)
        upload_directory.triggered.connect(self.__action_upload_directory__)
        self.menu.addAction(upload_directory)

        upload_files = QAction(QIcon(Resources.icon_folder_create), '&Create folder', self)
        upload_files.triggered.connect(self.__action_create_folder__)
        self.menu.addAction(upload_files)
        self.setMenu(self.menu)

    def __action_upload_files__(self):
        file_names = QFileDialog.getOpenFileNames(self, 'Select files', '~')[0]

        if file_names:
            self.uploader.setup(file_names)
            self.uploader.upload()

    def __action_upload_directory__(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Select directory', '~')

        if dir_name:
            self.uploader.setup([dir_name])
            self.uploader.upload()

    def __action_create_folder__(self):
        text, ok = QInputDialog.getText(self, 'New folder', 'Enter new folder name:')

        if ok and text:
            data, error = FileRepository.new_folder(text)
            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                        title="Creating folder",
                        body="<span style='color: red; font-weight: 600'> %s </span>" % error,
                    )
                )
            if data:
                Global().communicate.notification.emit(
                    MessageData(
                        title="Creating folder",
                        timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                        body=data,
                    )
                )
            Global().communicate.files_refresh.emit()

    class FilesUploader:
        UPLOAD_WORKER_ID = 398

        def __init__(self):
            self.files = []

        def setup(self, files: list):
            self.files = files

        def upload(self, data=None, error=None):
            if self.files:
                helper = ProgressCallbackHelper()
                worker = AsyncRepositoryWorker(
                    worker_id=self.UPLOAD_WORKER_ID,
                    name="Upload",
                    repository_method=FileRepository.upload,
                    response_callback=self.upload,
                    arguments=(helper.progress_callback.emit, self.files.pop())
                )
                if Adb.worker().work(worker):
                    Global().communicate.notification.emit(
                        MessageData(
                            title="Uploading",
                            message_type=MessageType.LOADING_MESSAGE,
                            message_catcher=worker.set_loading_widget
                        )
                    )
                    helper.setup(worker, worker.update_loading_widget)
                    worker.start()
            else:
                Global().communicate.files_refresh.emit()

            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                        title='Upload error',
                        body="<span style='color: red; font-weight: 600'> %s </span>" % error,
                    )
                )
            if data:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Uploaded',
                        timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                        body=data,
                    )
                )


class HomeButton(QToolButton):
    def __init__(self, parent):
        super(HomeButton, self).__init__(parent)
        self.action = QAction(QIcon(Resources.icon_home), 'Home', self)
        self.action.triggered.connect(
            lambda: Global().communicate.files_refresh.emit() if Adb.worker().check(300) and Adb.manager().clear_path() else ''
        )
        self.setDefaultAction(self.action)


class RefreshButton(QToolButton):
    def __init__(self, parent):
        super(RefreshButton, self).__init__(parent)
        self.action = QAction(QIcon(Resources.icon_refresh), 'Refresh', self)
        self.action.setShortcut('F5')
        self.action.triggered.connect(
            lambda: Global().communicate.files_refresh.emit()
        )
        self.setDefaultAction(self.action)


class ParentButton(QToolButton):
    def __init__(self, parent):
        super(ParentButton, self).__init__(parent)
        self.action = QAction(QIcon(Resources.icon_up), 'Parent', self)
        self.action.setShortcut('Escape')
        self.action.triggered.connect(
            lambda: Global().communicate.files_refresh.emit() if Adb.worker().check(300) and Adb.manager().up() else ''
        )
        self.setDefaultAction(self.action)


class PathBar(QWidget):
    def __init__(self, parent: QWidget):
        super(PathBar, self).__init__(parent)
        self.setLayout(QHBoxLayout(self))

        # Reterive old path
        device_id = Adb.manager().get_device().id
        device_path = Adb.manager().path()
        old_device_path = Settings.get_value(f"{device_id}/path")
        if old_device_path:
            device_path = old_device_path

        self.device_path = device_path

        # setup text line
        self.text = QLineEdit(self)
        self.text.installEventFilter(self)
        self.text.setStyleSheet("padding: 5;")
        self.text.setText(self.device_path)
        self.text.textEdited.connect(self._update)
        self.text.returnPressed.connect(self._open_action)
        self.layout().addWidget(self.text)

        self.open = QToolButton(self)
        self.open.setStyleSheet("padding: 4;")
        self.open_action = QAction(QIcon(Resources.icon_open), 'Open folder', self)
        self.open_action.triggered.connect(self._open_action)
        self.open.setDefaultAction(self.open_action)
        self.layout().addWidget(self.open)

        self.layout().setContentsMargins(0, 0, 0, 0)
        Global().communicate.path_toolbar_refresh.connect(self._clear)

        # If old path is available,
        # update gui to move to different folder
        if old_device_path:
            self._open_action()

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        if obj == self.text and event.type() == QEvent.FocusIn:
            self.text.setText(self.device_path)
        elif obj == self.text and event.type() == QEvent.FocusOut:
            self.text.setText(self.device_path)
        return super(PathBar, self).eventFilter(obj, event)

    def _clear(self):
        self.device_path = Adb.manager().path()
        self.text.setText(self.device_path)

    def _update(self, text: str):
        self.device_path = text

    def _open_action(self):
        self.text.clearFocus()
        file, error = FileRepository.file(self.device_path)
        if error:
            Global().communicate.path_toolbar_refresh.emit()
            Global().communicate.notification.emit(
                MessageData(
                    timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                    title="Opening folder",
                    body="<span style='color: red; font-weight: 600'> %s </span>" % error,
                )
            )
        elif file and Adb.manager().go(file):
            Global().communicate.files_refresh.emit()
        else:
            Global().communicate.path_toolbar_refresh.emit()
            Global().communicate.notification.emit(
                MessageData(
                    timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                    title="Opening folder",
                    body="<span style='color: red; font-weight: 600'> Cannot open location </span>",
                )
            )
