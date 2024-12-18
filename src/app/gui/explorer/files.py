# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov

import sys
import os
from typing import Any

from PyQt5 import (QtCore, QtGui)
from PyQt5.QtCore import (QAbstractTableModel, QEvent, QModelIndex,
                          QObject, QPoint, QRect, QSize, QSortFilterProxyModel, Qt)
from PyQt5.QtGui import (QColor, QFont, QMovie, QPixmap)
from PyQt5.QtWidgets import (QAction, QFileDialog, QHBoxLayout, QHeaderView,
                             QInputDialog, QLabel, QMainWindow, QMenu, QMessageBox,
                             QShortcut, QSizePolicy, QStyledItemDelegate,
                             QStyleOptionViewItem, QTableView, QTextEdit,
                             QVBoxLayout, QWidget)

from app.core.adb import Adb
from app.core.managers import Global
from app.core.resources import Resources
from app.core.settings import SettingsOptions, Settings
from app.data.models import FileType, MessageData, MessageType
from app.data.repositories import FileRepository
from app.gui.explorer.statusbar import DeviceStatusThread
from app.gui.explorer.toolbar import UpButton, UploadTools, PathBar, HomeButton, RefreshButton, BackButton, ForwardButton, SearchBar
from app.helpers.lookup import QtEventsLookUp, MimeTypesLookUp
from app.helpers.tools import AsyncRepositoryWorker, ProgressCallbackHelper

HEADER = ['File', 'Permissions', 'Size', 'Date', 'MimeType']


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

        self.up_button = UpButton(self)
        self.up_button.setSizePolicy(policy)
        self.layout().addWidget(self.up_button)

        self.back_button = BackButton(self)
        self.back_button.setSizePolicy(policy)
        self.layout().addWidget(self.back_button)

        self.foward_button = ForwardButton(self)
        self.foward_button.setSizePolicy(policy)
        self.layout().addWidget(self.foward_button)

        self.refresh_button = RefreshButton(self)
        self.refresh_button.setSizePolicy(policy)
        self.layout().addWidget(self.refresh_button)

        self.path_bar = PathBar(self)
        policy.setHorizontalStretch(8)
        self.path_bar.setSizePolicy(policy)
        self.layout().addWidget(self.path_bar)

        self.search_bar = SearchBar(self)
        policy.setHorizontalStretch(4)
        self.search_bar.setSizePolicy(policy)
        self.layout().addWidget(self.search_bar)


class FileItemDelegate(QStyledItemDelegate):
    def sizeHint(self, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex) -> QtCore.QSize:
        result = super(FileItemDelegate, self).sizeHint(option, index)
        result.setHeight(40)
        return result

    def setEditorData(self, editor: QWidget, index: QtCore.QModelIndex):
        editor.setText(index.model().data(index, Qt.EditRole))

    def updateEditorGeometry(self, editor: QWidget, option: 'QStyleOptionViewItem', _index: QtCore.QModelIndex):
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

class CustomSortModel(QSortFilterProxyModel):
    def __init__(self):
        super(CustomSortModel, self).__init__()

    def lessThan(self, left, right):
        # left is of type # PyQt5.QtCore.QModelIndex

        # Get items
        items = self.sourceModel().items

        # Extract file objects
        left_file_object = items[left.row()]
        right_file_object = items[right.row()]

        # Extract file names
        left_text = left_file_object.name
        right_text = right_file_object.name

        # Check whether these are directories or not
        left_is_dir = left_file_object.isdir
        right_is_dir = right_file_object.isdir

        # Sort directories above files
        if Settings.get_value(SettingsOptions.SORT_FOLDERS_BEFORE_FILES) is True:
            if left_is_dir:
                if not right_is_dir:
                    return True if self.sortOrder() == Qt.AscendingOrder else False
            elif right_is_dir:
                return False if self.sortOrder() == Qt.AscendingOrder else True

        # Sort items of the same type (file or directory) lexicographically.
        if left_text.lower() < right_text.lower():
            return True
        else:
            return False


# Creating the table model
class TableViewModel(QAbstractTableModel):
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

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return HEADER[section]
        return None

    def data(self, index, role):
        col = index.column()

        # file_object is of type app.data.models.File
        file_object = self.items[index.row()]
        # print(f"loc={row}x{col}: {file_object}")

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if col == 0:
                return file_object.name
            if col == 1:
                return file_object.permissions
            if col == 2:
                return file_object.size
            if col == 3:
                return file_object.date
            if col == 4:
                file_type = file_object.type
                if file_type == FileType.DIRECTORY:
                    return ""
                if file_type == FileType.FILE:
                    ext = os.path.splitext(file_object.name)[1]
                    if ext in MimeTypesLookUp.keys():
                        return MimeTypesLookUp[ext]
                    return ""
        if role == Qt.DecorationRole and col == 0:
            return QPixmap(self.icon(file_object)).scaled(32, 32, Qt.KeepAspectRatio)
        if role == Qt.FontRole and col == 1:
            font = QFont("monospace")
            font.setStyleHint(QFont.Monospace)
            return font
        return None

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        file_object = self.items[index.row()]

        if role == Qt.EditRole and value:
            print(f"setData: {file_object.name} -> {value}")
            if file_object.name != value:
                _, error = FileRepository.rename(file_object, value)
                if error:
                    Global().communicate.notification.emit(
                        MessageData(
                            timeout=10000,
                            title="Rename",
                            body=f"<span style='color: red; font-weight: 600'> {error} </span>",
                        )
                    )
                Global.communicate.files_refresh.emit()
        return super(TableViewModel, self).setData(index, value, role)

    def flags(self, index) -> Qt.ItemFlags:
        if not index.isValid():
            return Qt.NoItemFlags

        flags = Qt.ItemIsSelectable | Qt.ItemIsEnabled
        if index.column() == 0:
            flags |= Qt.ItemIsEditable

        return flags

    def icon(self, file_object):
        file_type = file_object.type
        if file_type == FileType.DIRECTORY:
            return Resources.icon_folder
        if file_type == FileType.FILE:
            ext = os.path.splitext(file_object.name)[1]
            if ext in Resources.icons_files:
                return Resources.icons_files[ext]
            return Resources.icon_file

        if file_type == FileType.LINK:
            link_type = file_object.link_type
            if link_type == FileType.DIRECTORY:
                return Resources.icon_link_folder
            if link_type == FileType.FILE:
                return Resources.icon_link_file
            return Resources.icon_link_file_unknown
        return Resources.icon_file_unknown

    def columnCount(self, _parent):
        return len(HEADER)

    def rowCount(self, _parent):
        return len(self.items)

    def insertRows(self, position, rows, parent=QModelIndex()):
        self.beginInsertRows(parent, position, position + rows - 1)
        self.endInsertRows()
        return True


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

        #-- Tableview
        # Create the model for the QTableView
        self.table_model = TableViewModel()

        # Create the sorter model
        # self.table_sorting_model = QSortFilterProxyModel()
        self.table_sorting_model = CustomSortModel()
        self.table_sorting_model.setSourceModel(self.table_model)
        self.table_sorting_model.setFilterKeyColumn(0)
        Global().communicate.search_text_update.connect(self._change_search_text)
        Global().communicate.search_case_update.connect(self._change_search_case_sensitivity)

        # Setup the QTableView to enable sorting
        self.table_view = QTableView()
        self.table_view.setWindowTitle('File listing...')
        self.table_view.setModel(self.table_sorting_model)
        self.table_view.setSortingEnabled(True)
        self.table_view.sortByColumn(0, Qt.AscendingOrder)
        self.table_view.doubleClicked.connect(self.on_doubled_clicked)
        self.table_view.clicked.connect(self.on_clicked)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table_view.customContextMenuRequested.connect(self.context_menu)
        self.table_view.setItemDelegate(FileItemDelegate(self.table_view))
        self.table_view.setStyleSheet('font-size: 16px;')
        # self.table_view.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # self.table_view.resizeColumnsToContents()

        self.delete_key = QShortcut(QtCore.Qt.Key_Delete, self.table_view)
        self.delete_key.activated.connect(self.on_delete_key)

        self.table_view.installEventFilter(self)

        self.navigation_dict = dict()

        # Customize tableview header
        self.table_header = self.table_view.horizontalHeader()
        self.table_header.setStyleSheet("QHeaderView { font-weight: bold; font-size: 12pt; }")
        self.table_header.setDefaultAlignment(Qt.AlignCenter | Qt.Alignment(Qt.TextWordWrap))

        size_policy = QSizePolicy()
        size_policy.setVerticalPolicy(QSizePolicy.Maximum)
        size_policy.setHorizontalPolicy(QSizePolicy.Maximum)
        self.table_header.setSizePolicy(size_policy)

        # Set column sizes
        self.table_header.setSectionResizeMode(0, QHeaderView.Stretch)
        self.table_header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.table_header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table_header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        self.table_header.setSectionResizeMode(4, QHeaderView.ResizeToContents)

        if Settings.get_value(SettingsOptions.HEADER_PERMISSION) is False:
            self.table_view.setColumnHidden(1, True)

        if Settings.get_value(SettingsOptions.HEADER_SIZE) is False:
            self.table_view.setColumnHidden(2, True)

        if Settings.get_value(SettingsOptions.HEADER_DATE) is False:
            self.table_view.setColumnHidden(3, True)

        if Settings.get_value(SettingsOptions.HEADER_MIME_TYPE) is False:
            self.table_view.setColumnHidden(4, True)

        # self.table_view.horizontalHeader().setStretchLastSection(True)

        self.table_view.resizeColumnsToContents()
        self.layout().addWidget(self.table_view)

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

        # Emit device label for status bar
        device_name = Adb.manager().get_device().name
        Global().communicate.status_bar_device_label.emit(device_name)

        # Emit Android version for status bar
        lines = ['']
        data, _ = FileRepository.android_version()
        if data:
            lines = data.splitlines()
        Global().communicate.status_bar_android_version.emit(lines[0])

        # Emit Android root/unroot status for status bar
        data, _ = FileRepository.is_android_root()
        Global().communicate.status_bar_is_root.emit(data)

        # Setup thread to monitor device
        self.device_status_thread = DeviceStatusThread(Settings.get_value(SettingsOptions.STATUSBAR_UPDATE_TIME))
        self.device_status_thread.start()

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
                print("Drag object is not file or folder")

    def _change_search_text(self, val):
        print(f"SearchBar: SearchText -> {val}")
        if len(val) > 0:
            # Show filtered data
            self.table_sorting_model.setFilterRegExp(val)
        else:
            # Bring back the unfilter data
            self.table_sorting_model.setFilterRegExp(".*")

    def _change_search_case_sensitivity(self, val):
        print(f"SearchBar: CaseSensitive -> {val}")
        if val is True:
            self.table_sorting_model.setFilterCaseSensitivity(Qt.CaseSensitive)
        else:
            self.table_sorting_model.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def _get_selected_items(self):
        curr_idx = self.table_view.currentIndex()
        orig_idx = self.table_sorting_model.mapToSource(curr_idx)
        file_object = self.table_model.items[orig_idx.row()]
        return (file_object, orig_idx)

    @property
    def file(self):
        if self.table_view and self.table_view.currentIndex():
            return self.table_model.items[self.table_view.currentIndex().row()]
        return None

    @property
    def files(self):
        if self.table_view and len(self.table_view.selectionModel().selectedRows()) > 0:
            return map(lambda index: self.table_model.items[index.row()], self.table_view.selectionModel().selectedRows())
        return None

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
            self.table_model.clear()
            self.table_view.setHidden(True)
            self.loading.setHidden(False)
            self.empty_label.setHidden(True)
            self.loading_movie.start()

            # Then start async worker
            worker.start()
            Global().communicate.path_toolbar_refresh.emit()

    def app_close(self):
        self.device_status_thread.stop()
        Global().communicate.files_refresh.disconnect()

    def close(self) -> bool:
        self.app_close()
        return super(FileExplorerWidget, self).close()

    def _async_response(self, files: list, error: str):
        self.loading_movie.stop()
        self.loading.setHidden(True)

        if error:
            print(error, file=sys.stderr)
            device_lost_err = f"error: device '{Adb.manager().get_device().id}' not found\n"
            if error == device_lost_err:
                Global().communicate.device_disconnect.emit()

            if not files:
                Global().communicate.notification.emit(
                    MessageData(
                        title='Files',
                        timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                        body=f"<span style='color: red; font-weight: 600'> {error} </span>"
                    )
                )
        if not files:
            self.table_view.setHidden(True)
            self.empty_label.setHidden(False)
        else:
            print(f"FileExplorerWidget: Refreshed (Path: {Adb.manager().get_current_path()})")
            Global().communicate.device_connect.emit()
            self.table_view.setHidden(False)
            self.table_model.populate(files)
            self.table_view.setFocus()

            curr_path = Adb.manager().get_current_path()
            cur_row = self.navigation_dict.get(curr_path, None)
            if cur_row is not None:
                print("FileExplorerWidget: Refreshed -- restore selection")
                self.table_view.setCurrentIndex(cur_row)
                self.table_view.selectRow(cur_row.row())
                self.navigation_dict.pop(curr_path)

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        # print(f"FileExplorerWidget: eventFilter (event: {QtEventsLookUp[event.type()]})")

        if obj is self.table_view and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                self.on_enter_key()
        elif obj == self.table_view and event.type() == QEvent.Hide:
            self.device_status_thread.stop()
        return super(FileExplorerWidget, self).eventFilter(obj, event)

    def on_doubled_clicked(self, _mi):
        self.open_file()

    def on_clicked(self, _mi):
        file_object, _ = self._get_selected_items()
        print(f"on_clicked (focus: {self.table_view.hasFocus()}){file_object}")

    def on_delete_key(self):
        print('on_delete_key: table_view: ' + str(self.table_view.hasFocus()))
        if self.table_view.hasFocus():
            self.delete()

    def on_enter_key(self):
        if self.table_view.hasFocus():
            selected_count = len([f for f in self.files])
            print(f"on_enter_key: Count={selected_count}")
            if selected_count == 1:
                self.open_file()
            else:
                msg = str(selected_count) + " files are selected \n"
                QMessageBox.information(
                    self,
                    'Info',
                    msg,
                    QMessageBox.Ok, QMessageBox.Ok
                )

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
                    body=f"<span style='color: red; font-weight: 600'> {error} </span>"
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
        self.table_view.edit(self.table_view.currentIndex())

    def open_file(self):
        curr_path = Adb.manager().get_current_path()
        file_object, selected_row = self._get_selected_items()
        print(f"open_file # {file_object.path} (isDir:{file_object.isdir})")

        if file_object.isdir:
            if Adb.manager().set_current_path(file_object):
                self.navigation_dict[curr_path] = selected_row
                Global().communicate.files_refresh.emit()
        else:
            data, error = FileRepository.open_file(file_object)
            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        title='File',
                        timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                        body=f"<span style='color: red; font-weight: 600'> {error} </span>"
                    )
                )
            else:
                self.text_view_window = TextView(file_object.name, data)
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
                # TODO: show busy loading here
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
                            body=f"<span style='color: red; font-weight: 600'>{error}</span>",
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
            print(f"download_files: {title} -> {destination}")

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

    def download_n_delete_files(self):
        self.download_files(delete_too=True)

    def download_to_n_delete(self):
        self.download_to(delete_too=True)

    def file_properties(self):
        file = self.file

        # Prepare info
        info  = f"<br/><u><b>{str(file)}</b></u><br/>"
        info += f"<pre>Name:        {file.name or '-'}</pre>"
        info += f"<pre>Owner:       {file.owner or '-'}</pre>"
        info += f"<pre>Group:       {file.group or '-'}</pre>"
        info += f"<pre>Size:        {file.raw_size or '-'}</pre>"
        info += f"<pre>Permissions: {file.permissions or '-'}</pre>"
        info += f"<pre>Date:        {file.raw_date or '-'}</pre>"
        info += f"<pre>Type:        {file.type or '-'}</pre>"

        if file.type == FileType.LINK:
            info += f"<pre>Links to:    {file.link or '-'}</pre>"

        properties = QMessageBox(self)
        properties.setStyleSheet("background-color: #DDDDDD")
        icon = QPixmap(self.table_model.icon(self.file)).scaled(128, 128, Qt.KeepAspectRatio)
        properties.setIconPixmap(icon)
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
                        body=f"<span style='color: red; font-weight: 600'> {error} </span>",
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
