# ADB File Explorer (python)
# Copyright (C) 2022  Azat Aldeshov
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import sys

from PyQt5.QtWidgets import QApplication

from app.core.adb import Adb
from app.core.application import Application
from app.core.resources import Resources
from app.gui.window import MainWindow
from app.helpers.tools import read_string_from_file

if __name__ == '__main__':
    Application()
    Adb.start()

    app = QApplication(sys.argv)
    app.setOrganizationName("ADBFileExplorer")
    app.setApplicationName("ADBFileExplorer")

    window = MainWindow()
    window.setStyleSheet(read_string_from_file(Resources.style_window))
    window.show()

    sys.exit(app.exec_())
