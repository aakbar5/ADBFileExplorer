# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
import sys
import os
from typing import Any

from PyQt5 import QtCore, QtGui
from PyQt5.QtCore import (
    Qt, QObject,
    QModelIndex, QAbstractTableModel, QSortFilterProxyModel,
    QVariant,
    QRect, QSize, QEvent, QPoint
)
from PyQt5.QtGui import (
    QFont, QColor, QPalette,
    QPixmap, QMovie,
    QKeySequence
)
from PyQt5.QtWidgets import (
    QMenu, QAction, QShortcut,
    QWidget, QMessageBox, QFileDialog, QInputDialog,
    QStyledItemDelegate, QStyleOptionViewItem,
    QMainWindow, QTableView, QListView, QLabel, QTextEdit,
    QVBoxLayout, QSizePolicy, QHBoxLayout, QHeaderView,
    QAbstractScrollArea
)

from app.core.resources import Resources
from app.core.settings import SettingsOptions, Settings
from app.core.adb import Adb
from app.core.managers import Global
from app.data.models import FileType, MessageData, MessageType
from app.data.repositories import FileRepository
from app.gui.explorer.toolbar import UpButton, UploadTools, PathBar, HomeButton, RefreshButton, BackButton, ForwardButton, SearchBar
from app.helpers.tools import AsyncRepositoryWorker, ProgressCallbackHelper, read_string_from_file
from app.gui.explorer.statusbar import DeviceStatusThread
from app.helpers.lookup import QtEventsLookUp

HEADER = ['File', 'Permissions', 'Size', 'Date']


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

    # def paint(self, painter: QtGui.QPainter, option: 'QStyleOptionViewItem', index: QtCore.QModelIndex):
    #     if not index.data():
    #         return super(FileItemDelegate, self).paint(painter, option, index)

    #     self.initStyleOption(option, index)
    #     style = option.widget.style() if option.widget else QApplication.style()
    #     style.drawControl(QStyle.CE_ItemViewItem, option, painter, option.widget)

    #     line_color = QColor("#CCCCCC")
    #     text_color = option.palette.color(QPalette.Normal, QPalette.Text)

    #     top = option.rect.top()
    #     bottom = option.rect.height()

    #     first_start = option.rect.left() + 50
    #     second_start = option.rect.left() + int(option.rect.width() / 2.5)
    #     third_start = option.rect.left() + int(option.rect.width() / 1.75)
    #     fourth_start = option.rect.left() + int(option.rect.width() / 1.25)
    #     end = option.rect.width() + option.rect.left()

    #     self.paint_text(
    #         painter, index.data().name, text_color, option.displayAlignment,
    #         first_start, top, second_start - first_start - 4, bottom
    #     )

    #     self.paint_line(painter, line_color, second_start - 2, top, second_start - 1, bottom)

    #     self.paint_text(
    #         painter, index.data().permissions, text_color, Qt.AlignCenter | option.displayAlignment,
    #         second_start, top, third_start - second_start - 4, bottom
    #     )

    #     self.paint_line(painter, line_color, third_start - 2, top, third_start - 1, bottom)

    #     self.paint_text(
    #         painter, index.data().size, text_color, Qt.AlignCenter | option.displayAlignment,
    #         third_start, top, fourth_start - third_start - 4, bottom
    #     )

    #     self.paint_line(painter, line_color, fourth_start - 2, top, fourth_start - 1, bottom)

    #     self.paint_text(
    #         painter, index.data().date, text_color, Qt.AlignCenter | option.displayAlignment,
    #         fourth_start, top, end - fourth_start, bottom
    #     )

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
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return HEADER[section]

    def data(self, index, role):
        row = index.row()
        col = index.column()

        # fileObject is of type app.data.models.File
        fileObject = self.items[index.row()]
        # print(f"loc={row}x{col}: {fileObject}")

        if role == Qt.DisplayRole or role == Qt.EditRole:
            if col == 0:
                return fileObject.name
            elif col == 1:
                return fileObject.permissions
            elif col == 2:
                return fileObject.size
            elif col == 3:
                return fileObject.date
        elif role == Qt.DecorationRole and col == 0:
            return QPixmap(self.icon(fileObject)).scaled(32, 32, Qt.KeepAspectRatio)
        elif role == Qt.FontRole and col == 1:
            font = QFont("monospace")
            font.setStyleHint(QFont.Monospace)
            return font;

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        row = index.row()
        col = index.column()
        fileObject = self.items[index.row()]

        if role == Qt.EditRole and value:
            print(f"setData: {fileObject.name} -> {value}")
            if fileObject.name != value:
                print(f"  rename object")
                data, error = FileRepository.rename(fileObject, value)
                if error:
                    Global().communicate.notification.emit(
                        MessageData(
                            timeout=10000,
                            title="Rename",
                            body="<span style='color: red; font-weight: 600'> %s </span>" % error,
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

    def icon(self, fileObject):
        file_type = fileObject.type
        if file_type == FileType.DIRECTORY:
            return Resources.icon_folder
        elif file_type == FileType.FILE:
            ext = os.path.splitext(fileObject.name)[1]
            if ext in Resources.icons_files.keys():
                return Resources.icons_files[ext]
            else:
                return Resources.icon_file
        elif file_type == FileType.LINK:
            link_type = fileObject.link_type
            if link_type == FileType.DIRECTORY:
                return Resources.icon_link_folder
            elif link_type == FileType.FILE:
                return Resources.icon_link_file
            return Resources.icon_link_file_unknown
        return Resources.icon_file_unknown

    def columnCount(self, parent):
        return len(HEADER)

    def rowCount(self, parent):
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
        self.tableModel = TableViewModel()

        # Create the sorter model
        self.tableSortedModel = QSortFilterProxyModel()
        self.tableSortedModel.setSourceModel(self.tableModel)
        self.tableSortedModel.setFilterKeyColumn(0)
        Global().communicate.searchTextUpdate.connect(self._changeSearchText)
        Global().communicate.searchCaseUpdate.connect(self._changeSearchCaseSensitivity)

        # Setup the QTableView to enable sorting
        self.tableView = QTableView()
        self.tableView.setWindowTitle('File listing...')
        self.tableView.setModel(self.tableSortedModel)
        self.tableView.setSortingEnabled(True)
        self.tableView.sortByColumn(0, Qt.AscendingOrder)
        self.tableView.doubleClicked.connect(self.onDoubleClicked)
        self.tableView.clicked.connect(self.onClicked)
        self.tableView.setSelectionBehavior(QTableView.SelectRows)
        self.tableView.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tableView.customContextMenuRequested.connect(self.context_menu)
        self.tableView.setItemDelegate(FileItemDelegate(self.tableView))
        self.tableView.setStyleSheet('font-size: 16px;')
        # self.tableView.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
        # self.tableView.resizeColumnsToContents()

        self.deleteKey = QShortcut(QtCore.Qt.Key_Delete, self.tableView)
        self.deleteKey.activated.connect(self.onDeleteKey)

        self.tableView.installEventFilter(self)

        # Customize tableview header
        self.tableHeader = self.tableView.horizontalHeader()
        self.tableHeader.setStyleSheet("QHeaderView { font-size: 12pt; }")
        self.tableHeader.setDefaultAlignment(Qt.AlignCenter|Qt.Alignment(Qt.TextWordWrap))
        sizePol = QSizePolicy()
        sizePol.setVerticalPolicy(QSizePolicy.Maximum)
        sizePol.setHorizontalPolicy(QSizePolicy.Maximum)
        self.tableHeader.setSizePolicy(sizePol)

        # Set column sizes
        self.tableHeader.setSectionResizeMode(0, QHeaderView.Stretch)
        self.tableHeader.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self.tableHeader.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.tableHeader.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        # self.tableView.horizontalHeader().setStretchLastSection(True)

        self.tableView.resizeColumnsToContents()
        self.layout().addWidget(self.tableView)


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

        # Emit device lable for status bar
        device_name = Adb.manager().get_device().name
        Global().communicate.status_bar_device_label.emit(device_name)

        # Emit Android version for status bar
        data, _ = FileRepository.AndroidVersion()
        if data:
            lines = data.splitlines()
        Global().communicate.status_bar_android_version.emit(lines[0])

        # Emit Android root/unroot status for status bar
        data, _ = FileRepository.IsAndroidRoot()
        Global().communicate.status_bar_is_root.emit(data)

        # Setup thread to monitor device
        self.device_status_thread = DeviceStatusThread(Settings.get_value(SettingsOptions.STATUSBAR_UPDATE_TIME))
        self.device_status_thread.start()

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

    def _changeSearchText(self, val):
        print(f"SearchBar: SearchText -> {val}")
        if (len(val) > 0):
            # Show filtered data
            self.tableSortedModel.setFilterRegExp(val)
        else:
            # Bring back the unfilter data
            self.tableSortedModel.setFilterRegExp(".*")

    def _changeSearchCaseSensitivity(self, val):
        print(f"SearchBar: CaseSensitive -> {val}")
        if val == True:
            self.tableSortedModel.setFilterCaseSensitivity(Qt.CaseSensitive)
        else:
            self.tableSortedModel.setFilterCaseSensitivity(Qt.CaseInsensitive)

    def _getSelectedItems(self):
        # Note: Incase of filter is acitve curr_idx_row
        # will be different to that of orig_idx_row
        row_count = self.tableSortedModel.rowCount()
        curr_idx = self.tableView.currentIndex()
        curr_idx_row = self.tableView.currentIndex().row()
        orig_idx_row = self.tableSortedModel.mapToSource(curr_idx).row()

        fileObject = self.tableModel.items[orig_idx_row]
        return fileObject

    @property
    def file(self):
        if self.tableView and self.tableView.currentIndex():
            return self.tableModel.items[self.tableView.currentIndex().row()]

    @property
    def files(self):
        # indexes = self.tableView.selectionModel().selectedRows()
        # for index in sorted(indexes):
        #     print('Row %d is selected' % index.row())

        if self.tableView and len(self.tableView.selectionModel().selectedRows()) > 0:
            return map(lambda index: self.tableModel.items[index.row()], self.tableView.selectionModel().selectedRows())

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
            self.tableModel.clear()
            self.tableView.setHidden(True)
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
            self.tableView.setHidden(False)
            self.tableModel.populate(files)
            self.tableView.setFocus()

    def eventFilter(self, obj: 'QObject', event: 'QEvent') -> bool:
        print(f"FileExplorerWidget: eventFilter (event: {QtEventsLookUp[event.type()]})")
        # print(f"FileExplorerWidget: eventFilter {str(event)}")
        # if obj == self.tableView and \
        #         event.type() == QEvent.KeyPress and \
        #         event.matches(QKeySequence.InsertParagraphSeparator) and \
        #         not self.tableView.isPersistentEditorOpen(self.list.currentIndex()):
        #     self.open(self.tableView.currentIndex())

        if obj is self.tableView and event.type() == QtCore.QEvent.KeyPress:
            if event.key() in (QtCore.Qt.Key_Return, QtCore.Qt.Key_Enter):
                self.onEnterKey()
            else:
                print(f"FileExplorerWidget: KeyPress -> Misc")
        elif obj == self.tableView and event.type() == QEvent.Hide:
            self.device_status_thread.stop()

        return super(FileExplorerWidget, self).eventFilter(obj, event)

    def onDoubleClicked(self, mi):
        fileObject = self._getSelectedItems()
        print(f"onDoubleClicked: {fileObject}")
        if Adb.manager().set_current_path(fileObject):
            Global().communicate.files_refresh.emit()

    def onClicked(self, mi):
        # TODO: Once tableview is showing file list; use mouse to select anything; you
        # will find that bar is selected and control is coming to this function
        # at this point, press ENTER key I was hoping to received onEnterKey but it
        # is not happening.
        fileObject = self._getSelectedItems()
        print(f"onClicked (focus: {self.tableView.hasFocus()}){fileObject}")

    def onDeleteKey(self):
        print('onDeleteKey: tableView: ' + str(self.tableView.hasFocus()))
        if self.tableView.hasFocus():
            self.delete()

    def onEnterKey(self):
        if self.tableView.hasFocus():
            selectedCount = len([f for f in self.files])
            print(f"onEnterKey: Count={selectedCount}")
            if selectedCount == 1:
                self.open_file()
            else:
                msg += str(selectedCount) + " files are selected \n"
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
        self.tableView.edit(self.tableView.currentIndex())

    def open_file(self):
        fileObject = self._getSelectedItems()
        print(f"open_file: {fileObject.path}")

        if fileObject.isdir:
            print(f"open_file: is_dir")
            if Adb.manager().set_current_path(fileObject):
                Global().communicate.files_refresh.emit()
        else:
            data, error = FileRepository.open_file(fileObject)
            if error:
                Global().communicate.notification.emit(
                    MessageData(
                        title='File',
                        timeout=Settings.get_value(SettingsOptions.NOTIFICATION_TIMEOUT),
                        body="<span style='color: red; font-weight: 600'> %s </span>" % error
                    )
                )
            else:
                self.text_view_window = TextView(fileObject.name, data)
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
        file = self.file

        # Prepare info
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
        icon = QPixmap(self.tableModel.icon(self.file)).scaled(128, 128, Qt.KeepAspectRatio)
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
