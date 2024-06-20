# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import sys
import os
from typing import Any

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import Qt, QPoint, QModelIndex, QAbstractListModel, QVariant, QRect, QSize, QEvent, QObject
from PyQt5.QtGui import QPixmap, QColor, QPalette, QMovie, QKeySequence
from PyQt5.QtWidgets import QMenu, QAction, QMessageBox, QFileDialog, QStyle, QWidget, QStyledItemDelegate, \
    QStyleOptionViewItem, QApplication, QListView, QVBoxLayout, QLabel, QSizePolicy, QHBoxLayout, QTextEdit, \
    QMainWindow, QInputDialog, QShortcut

from app.core.resources import Resources
from app.core.settings import SettingsOptions, Settings
from app.core.adb import Adb
from app.core.managers import Global
from app.data.models import FileType, MessageData, MessageType
from app.data.repositories import FileRepository
from app.gui.explorer.toolbar import ParentButton, UploadTools, PathBar, HomeButton, RefreshButton
from app.helpers.tools import AsyncRepositoryWorker, ProgressCallbackHelper, read_string_from_file


class FileHeaderWidget(QWidget):
    def __init__(self, parent=None):
        super(FileHeaderWidget, self).__init__(parent)
        self.setLayout(QHBoxLayout(self))
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)

        self.file = QLabel('File', self)
        self.file.setContentsMargins(45, 0, 0, 0)
        policy.setHorizontalStretch(39)
        self.file.setSizePolicy(policy)
        self.layout().addWidget(self.file)

        self.permissions = QLabel('Permissions', self)
        self.permissions.setAlignment(Qt.AlignCenter)
        policy.setHorizontalStretch(18)
        self.permissions.setSizePolicy(policy)
        self.layout().addWidget(self.permissions)

        self.size = QLabel('Size', self)
        self.size.setAlignment(Qt.AlignCenter)
        policy.setHorizontalStretch(21)
        self.size.setSizePolicy(policy)
        self.layout().addWidget(self.size)

        self.date = QLabel('Date', self)
        self.date.setAlignment(Qt.AlignCenter)
        policy.setHorizontalStretch(22)
        self.date.setSizePolicy(policy)
        self.layout().addWidget(self.date)

        self.setStyleSheet("QWidget { background-color: #E5E5E5; font-weight: 500; border: 1px solid #C0C0C0 }")


class FileExplorerToolbar(QWidget):
    def __init__(self, parent=None):
        super(FileExplorerToolbar, self).__init__(parent)
        self.setLayout(QHBoxLayout(self))
        policy = QSizePolicy(QSizePolicy.Ignored, QSizePolicy.Preferred)
        policy.setHorizontalStretch(1)

        self.upload_tools = UploadTools(self)
        self.upload_tools.setSizePolicy(policy)
        self.layout().addWidget(self.upload_tools)

        self.home_button = HomeButton(self)
        self.home_button.setSizePolicy(policy)
        self.layout().addWidget(self.home_button)

        self.parent_button = ParentButton(self)
        self.parent_button.setSizePolicy(policy)
        self.layout().addWidget(self.parent_button)

        self.refresh_button = RefreshButton(self)
        self.refresh_button.setSizePolicy(policy)
        self.layout().addWidget(self.refresh_button)

        self.path_bar = PathBar(self)
        policy.setHorizontalStretch(8)
        self.path_bar.setSizePolicy(policy)
        self.layout().addWidget(self.path_bar)


class FileItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
        result = super(FileItemDelegate, self).sizeHint(option, index)
        result.setHeight(40)
        return result

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex):
        editor.setText(index.model().data(index, Qt.EditRole))

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        editor.setGeometry(
            option.rect.left() + 48, option.rect.top(), int(option.rect.width() / 2.5) - 55, option.rect.height()
        )

    def setModelData(self, editor: QWidget, model: QtCore.QAbstractItemModel, index: QtCore.QModelIndex):
        model.setData(index, editor.text(), Qt.EditRole)

    @staticmethod
    def paint_line(painter: QtGui.QPainter, color: QColor, x, y, w, h):
        painter.setPen(color)
        painter.drawLine(x, y, w, h)

    @staticmethod
    def paint_text(painter: QtGui.QPainter, text: str, color: QColor, options, x, y, w, h):
        painter.setPen(color)
        painter.drawText(QRect(x, y, w, h), options, text)

    def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
        if not index.data():
            return super(FileItemDelegate, self).paint(painter, option, index)

        self.initStyleOption(option, index)
        style = option.widget.style() if option.widget else QApplication.style()
        style.drawControl(QStyle.CE_ItemViewItem, option, painter, option.widget)

        line_color = QColor("#CCCCCC")
        text_color = option.palette.color(QPalette.Normal, QPalette.Text)

        top = option.rect.top()
        bottom = option.rect.height()

        first_start = option.rect.left() + 50
        second_start = option.rect.left() + int(option.rect.width() / 2.5)
        third_start = option.rect.left() + int(option.rect.width() / 1.75)
        fourth_start = option.rect.left() + int(option.rect.width() / 1.25)
        end = option.rect.width() + option.rect.left()

        self.paint_text(
            painter, index.data().name, text_color, option.displayAlignment,
            first_start, top, second_start - first_start - 4, bottom
        )

        self.paint_line(painter, line_color, second_start - 2, top, second_start - 1, bottom)

        self.paint_text(
            painter, index.data().permissions, text_color, Qt.AlignCenter | option.displayAlignment,
            second_start, top, third_start - second_start - 4, bottom
        )

        self.paint_line(painter, line_color, third_start - 2, top, third_start - 1, bottom)

        self.paint_text(
            painter, index.data().size, text_color, Qt.AlignCenter | option.displayAlignment,
            third_start, top, fourth_start - third_start - 4, bottom
        )

        self.paint_line(painter, line_color, fourth_start - 2, top, fourth_start - 1, bottom)

        self.paint_text(
            painter, index.data().date, text_color, Qt.AlignCenter | option.displayAlignment,
            fourth_start, top, end - fourth_start, bottom
        )


class FileListModel(QAbstractListModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = []

    def clear(self):
        self.beginResetModel()
        self.items.clear()
        self.endResetModel()

    def populate(self, files: list):
        self.beginResetModel()
        self.items.clear()
        self.items = files
        self.endResetModel()

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.items)

    def icon_path(self, index: QModelIndex = ...):
        file_type = self.items[index.row()].type
        if file_type == FileType.DIRECTORY:
            return Resources.icon_folder
        elif file_type == FileType.FILE:
            return Resources.icon_file
        elif file_type == FileType.LINK:
            link_type = self.items[index.row()].link_type
            if link_type == FileType.DIRECTORY:
                return Resources.icon_link_folder
            elif link_type == FileType.FILE:
                return Resources.icon_link_file
            return Resources.icon_link_file_unknown
        return Resources.icon_file_unknown

    def flags(self, index: QModelIndex) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        return Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.EditRole and value:
            data, error = FileRepository.rename(self.items[index.row()], value)
            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        timeout=10000,
                        title="Rename",
                        body="<span style='color: red; font-weight: 600'> %s </span>" % error,
                    )
                )
            Global.communicate.files_refresh.emit()
        return super(FileListModel, self).setData(index, value, role)

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        if not index.isValid():
            return QVariant()

        if role == Qt.DisplayRole:
            return self.items[index.row()]
        elif role == Qt.EditRole:
            return self.items[index.row()].name
        elif role == Qt.DecorationRole:
            return QPixmap(self.icon_path(index)).scaled(32, 32, Qt.KeepAspectRatio)
        return QVariant()


class FileExplorerWidget(QWidget):
    FILES_WORKER_ID = 300
    DOWNLOAD_WORKER_ID = 399

    def __init__(self, parent=None):
        super(FileExplorerWidget, self).__init__(parent)
        self.setAcceptDrops(True)
        self.uploader = UploadTools.FilesUploader()

        self.main_layout = QVBoxLayout(self)

        self.toolbar = FileExplorerToolbar(self)
        self.main_layout.addWidget(self.toolbar)

        self.header = FileHeaderWidget(self)
        self.main_layout.addWidget(self.header)

        self.list = QListView(self)
        self.model = FileListModel(self.list)

        self.list.setSpacing(1)
        self.list.setModel(self.model)
        self.list.installEventFilter(self)
        self.list.doubleClicked.connect(self.open)
        self.list.clicked.connect(self.onClicked)
        self.list.setItemDelegate(FileItemDelegate(self.list))
        self.list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.list.customContextMenuRequested.connect(self.context_menu)
        self.list.setStyleSheet(read_string_from_file(Resources.style_file_list))
        self.list.setSelectionMode(QListView.SelectionMode.ExtendedSelection)
        self.layout().addWidget(self.list)

        self.deleteKey = QShortcut(QtCore.Qt.Key_Delete, self.list)
        self.deleteKey.activated.connect(self.onDeleteKey)

        self.loading = QLabel(self)
        self.loading.setAlignment(Qt.AlignCenter)
        self.loading_movie = QMovie(Resources.anim_loading, parent=self.loading)
        self.loading_movie.setScaledSize(QSize(48, 48))
        self.loading.setMovie(self.loading_movie)
        self.main_layout.addWidget(self.loading)

        self.empty_label = QLabel("Folder is empty", self)
        self.empty_label.setAlignment(Qt.AlignCenter)
        self.empty_label.setStyleSheet("color: #969696; border: 1px solid #969696")
        self.layout().addWidget(self.empty_label)

        self.main_layout.setStretch(self.layout().count() - 1, 1)
        self.main_layout.setStretch(self.layout().count() - 2, 1)

        self.text_view_window = None
        self.setLayout(self.main_layout)

        Global().communicate.files_refresh.connect(self.update)
        Global().communicate.app_close.connect(self.app_close)

        device_name = Adb.manager().get_device().name
        Global().communicate.status_bar_device_label.emit(device_name)

    def onClicked(self):
        print(f"onClicked: list (Focus={self.list.hasFocus()})")

    def onDeleteKey(self):
        print(f"onDeleteKey: list (Focus={self.list.hasFocus()})")
        if self.list.hasFocus():
            self.delete()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        drag_objects = [u.toLocalFile() for u in event.mimeData().urls()]
        for obj in drag_objects:
            if os.path.isdir(obj) or os.path.isfile(obj):
                self.uploader.setup([obj])
                self.uploader.upload()
            else:
                print(f"Drag object is not file or folder")

    @property
    def file(self):
        if self.list and self.list.currentIndex():
            return self.model.items[self.list.currentIndex().row()]

    @property
    def files(self):
        if self.list and len(self.list.selectedIndexes()) > 0:
            return map(lambda index: self.model.items[index.row()], self.list.selectedIndexes())

    def update(self):
        super(FileExplorerWidget, self).update()
        worker = AsyncRepositoryWorker(
            name="Files",
            worker_id=self.FILES_WORKER_ID,
            repository_method=FileRepository.files,
            response_callback=self._async_response,
            arguments=()
        )
        if Adb.worker().work(worker):
            # First Setup loading view
            self.model.clear()
            self.list.setHidden(True)
            self.loading.setHidden(False)
            self.empty_label.setHidden(True)
            self.loading_movie.start()

            # Then start async worker
            worker.start()
            Global().communicate.path_toolbar_refresh.emit()

    def app_close(self):
        Global().communicate.files_refresh.disconnect()

    def close(self) -> bool:
        Global().communicate.files_refresh.disconnect()
        return super(FileExplorerWidget, self).close()

    def _async_response(self, files: list, error: str):
        self.loading_movie.stop()
        self.loading.setHidden(True)

        if error:
            print(error, file=sys.stderr)
            if not files:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Files',
                        timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                        body="<span style='color: red; font-weight: 600'> %s </span>" % error
                    )
                )
        if not files:
            self.empty_label.setHidden(False)
        else:
            self.list.setHidden(False)
            self.model.populate(files)
            self.list.setFocus()

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        if obj == self.list and \
                event.type() == QEvent.KeyPress and \
                event.matches(QKeySequence.InsertParagraphSeparator) and \
                not self.list.isPersistentEditorOpen(self.list.currentIndex()):
            self.open(self.list.currentIndex())
        return super(FileExplorerWidget, self).eventFilter(obj, event)

    def open(self, index: QModelIndex = ...):
        if Adb.manager().open(self.model.items[index.row()]):
            Global().communicate.files_refresh.emit()

    def context_menu(self, pos: QPoint):
        menu = QMenu()
        menu.addSection("Actions")

        action_copy = QAction('Copy to...', self)
        action_copy.setDisabled(True)
        menu.addAction(action_copy)

        action_move = QAction('Move to...', self)
        action_move.setDisabled(True)
        menu.addAction(action_move)

        menu.addSeparator()

        action_create_folder = QAction('Create folder', self)
        action_create_folder.triggered.connect(self.__action_create_folder__)
        menu.addAction(action_create_folder)

        action_upload_directory = QAction('Upload directory', self)
        action_upload_directory.triggered.connect(self.__action_upload_directory__)
        menu.addAction(action_upload_directory)

        action_upload_files = QAction('Upload files', self)
        action_upload_files.triggered.connect(self.__action_upload_files__)
        menu.addAction(action_upload_files)

        menu.addSeparator()

        action_rename = QAction('Rename', self)
        action_rename.triggered.connect(self.rename)
        menu.addAction(action_rename)

        action_open_file = QAction('Open', self)
        action_open_file.triggered.connect(self.open_file)
        menu.addAction(action_open_file)

        action_delete = QAction('Delete', self)
        action_delete.triggered.connect(self.delete)
        menu.addAction(action_delete)

        menu.addSeparator()

        action_download = QAction('Download', self)
        action_download.triggered.connect(self.download_files)
        menu.addAction(action_download)

        action_download_n_delete = QAction('Download n Delete', self)
        action_download_n_delete.triggered.connect(self.download_n_delete_files)
        menu.addAction(action_download_n_delete)

        menu.addSeparator()

        action_download_to = QAction('Download to...', self)
        action_download_to.triggered.connect(self.download_to)
        menu.addAction(action_download_to)

        action_download_to_n_delete = QAction('Download n Delete to...', self)
        action_download_to_n_delete.triggered.connect(self.download_to_n_delete)
        menu.addAction(action_download_to_n_delete)

        menu.addSeparator()

        action_properties = QAction('Properties', self)
        action_properties.triggered.connect(self.file_properties)
        menu.addAction(action_properties)

        menu.exec(self.mapToGlobal(pos))

    @staticmethod
    def show_notification(data, error, title_success, title_error):
        if error:
            Global().communicate.notification.emit(
                MessageData(
                    title=title_error,
                    timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                    body="<span style='color: red; font-weight: 600'> %s </span>" % error
                )
            )
        if data:
            Global().communicate.notification.emit(
                MessageData(
                    title=title_success,
                    timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                    body=data
                )
            )

    @staticmethod
    def default_download_response(data, error):
        FileExplorerWidget.show_notification(data, error, 'Downloaded', 'Download error')

    @staticmethod
    def default_download_n_delete_response(data, error):
        FileExplorerWidget.show_notification(data, error, 'Downloaded n Deleted', 'Download/Delete error')
        Global.communicate.files_refresh.emit()

    def rename(self):
        self.list.edit(self.list.currentIndex())

    def open_file(self):
        # QDesktopServices.openUrl(QUrl.fromLocalFile("downloaded_path")) open via external app
        if not self.file.isdir:
            data, error = FileRepository.open_file(self.file)
            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        title='File',
                        timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                        body="<span style='color: red; font-weight: 600'> %s </span>" % error
                    )
                )
            else:
                self.text_view_window = TextView(self.file.name, data)
                self.text_view_window.show()

    def delete(self):
        file_names = '\n'.join(map(lambda f: f.name, self.files))
        count = len([f for f in self.files])
        msg = "The following files will be delete:\n"
        if count == 1:
            msg += file_names
        else:
            msg += str(count) + " files"
        msg += "\n"

        reply = QMessageBox.critical(
            self,
            'Confirm Delete',
            msg,
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            for file in self.files:
                data, error = FileRepository.delete(file)
                if data:
                    Global().communicate.notification.emit(
                        MessageData(
                            timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                            title="Delete",
                            body=data,
                        )
                    )
                if error:
                    Global().communicate.notification.emit(
                        MessageData(
                            timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                            title="Delete",
                            body="<span style='color: red; font-weight: 600'> %s </span>" % error,
                        )
                    )
            Global.communicate.files_refresh.emit()

    def download_to(self, delete_too: bool = False):
        dir_name = QFileDialog.getExistingDirectory(self, 'Download to', '~')
        if dir_name:
            self.download_files(dir_name, delete_too=delete_too)

    def download_files(self, destination: str = None, delete_too: bool = False):
        callback = self.default_download_response
        if delete_too:
            callback = self.default_download_n_delete_response

        for file in self.files:
            # Build title of the notification card
            title = "Download "
            if delete_too:
                title += "& Delete "
            title += ": " + file.name
            print(f"download_files: {title} ->  {destination}")

            # Setup job
            helper = ProgressCallbackHelper()
            worker = AsyncRepositoryWorker(
                worker_id=self.DOWNLOAD_WORKER_ID,
                name=title,
                repository_method=FileRepository.download,
                response_callback=callback,
                arguments=(
                    helper.progress_callback.emit, file, destination, delete_too
                )
            )
            if Adb.worker().work(worker):
                Global().communicate.notification.emit(
                    MessageData(
                        title=title,
                        message_type=MessageType.LOADING_MESSAGE,
                        message_catcher=worker.set_loading_widget
                    )
                )
                helper.setup(worker, worker.update_loading_widget)
                worker.start()

    def download_n_delete_files(self, destination: str = None):
        self.download_files(delete_too=True)

    def download_to_n_delete(self):
        self.download_to(delete_too=True)

    def file_properties(self):
        file, error = FileRepository.file(self.file.path)
        file = file if file else self.file

        if error:
            Global().communicate.notification.emit(
                MessageData(
                    timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                    title="Opening folder",
                    body="<span style='color: red; font-weight: 600'> %s </span>" % error,
                )
            )

        info = "<br/><u><b>%s</b></u><br/>" % str(file)
        info += "<pre>Name:        %s</pre>" % file.name or '-'
        info += "<pre>Owner:       %s</pre>" % file.owner or '-'
        info += "<pre>Group:       %s</pre>" % file.group or '-'
        info += "<pre>Size:        %s</pre>" % file.raw_size or '-'
        info += "<pre>Permissions: %s</pre>" % file.permissions or '-'
        info += "<pre>Date:        %s</pre>" % file.raw_date or '-'
        info += "<pre>Type:        %s</pre>" % file.type or '-'

        if file.type == FileType.LINK:
            info += "<pre>Links to:    %s</pre>" % file.link or '-'

        properties = QMessageBox(self)
        properties.setStyleSheet("background-color: #DDDDDD")
        properties.setIconPixmap(
            QPixmap(self.model.icon_path(self.list.currentIndex())).scaled(128, 128, Qt.KeepAspectRatio)
        )
        properties.setWindowTitle('Properties')
        properties.setInformativeText(info)
        properties.exec_()

    # TODO: Duplicate function; think of having one copy
    def __action_upload_files__(self):
        file_names = QFileDialog.getOpenFileNames(self, 'Select files', '~')[0]

        if file_names:
            self.uploader.setup(file_names)
            self.uploader.upload()

    # TODO: Duplicate function; think of having one copy
    def __action_upload_directory__(self):
        dir_name = QFileDialog.getExistingDirectory(self, 'Select directory', '~')

        if dir_name:
            self.uploader.setup([dir_name])
            self.uploader.upload()

    # TODO: Duplicate function; think of having one copy
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

class TextView(QMainWindow):
    def __init__(self, filename, data):
        QMainWindow.__init__(self)

        self.setMinimumSize(QSize(500, 300))
        self.setWindowTitle(filename)

        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)
        self.text_edit.insertPlainText(data)
        self.text_edit.move(10, 10)
