# ADB File Explorer
# Copyright (C) 2022  Azat Aldeshov
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QWidget, QLabel, QApplication

from app.core.resources import Resources
from app.core.application import Application


class About(QWidget):
    def __init__(self):
        super(QWidget, self).__init__()
        icon = QLabel(self)
        icon.setPixmap(QPixmap(Resources.icon_logo).scaled(64, 64, Qt.KeepAspectRatio))
        icon.move(168, 40)
        about_text = "<br/><br/>"
        about_text += "<b>ADB File Explorer</b><br/>"
        about_text += '<i>Version: %s </i><br/>' % Application.__version__
        about_text += '<br/>'
        about_text += "Open source application written in <i>Python</i><br/>"
        about_text += "UI Library: <i>PyQt5</i><br/>"

        az_link = 'https://github.com/Aldeshov/ADBFileExplorer'
        about_text += "Developer: Azat Aldeshov<br/>"
        about_text += "Github: <a target='_blank' href='%s'>%s</a>" % (az_link, az_link)
        about_text += "<br/>"

        aa_link = 'https://github.com/aakbar5/ADBFileExplorer'
        about_text += "Developer: aakbar<br/>"
        about_text += "Github: <a target='_blank' href='%s'>%s</a>" % (aa_link, aa_link)
        about_text += "<br/>"

        about_label = QLabel(about_text, self)
        about_label.setOpenExternalLinks(True)
        about_label.move(10, 100)

        self.setAttribute(Qt.WA_QuitOnClose, False)
        self.setWindowIcon(QIcon(Resources.icon_logo))
        self.setWindowTitle('About')
        self.setFixedHeight(320)
        self.setFixedWidth(400)

        center = QApplication.desktop().availableGeometry(self).center()
        self.move(int(center.x() - self.width() * 0.5), int(center.y() - self.height() * 0.5))
