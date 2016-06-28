"""
    Copyright (C) 2016  Richard Schwalk

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys

import PyQt5
from os import path, environ
from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtQml import QQmlApplicationEngine

from modules.currenttime import CurrentTime
from modules.weather import WeatherController


if __name__ == '__main__':
    QGuiApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    environ['QT_LOGGING_TO_CONSOLE'] = '1'

    print(path.abspath(path.join(path.dirname(PyQt5.__file__), 'plugins')))

    app = QGuiApplication(sys.argv)
    app.addLibraryPath(path.abspath(path.join(path.dirname(PyQt5.__file__), 'plugins')))
    # filename = path.abspath(path.join(path.dirname(__file__), 'UIInfoDevice', 'UIInfoDevice.qml'))
    engine = QQmlApplicationEngine()

    cTime = CurrentTime()
    engine.rootContext().setContextProperty('curtime', cTime)

    weat = WeatherController()
    engine.rootContext().setContextProperty('weather', weat)

    engine.load(QUrl('UIInfoDevice/UIInfoDevice.qml'))

    sys.exit(app.exec_())
