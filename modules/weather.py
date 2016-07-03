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

from PyQt5.QtCore import QObject, QTimer, pyqtSignal, pyqtProperty, pyqtSlot, \
    QUrl, QJsonDocument, qDebug
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest


class WeatherController(QObject):
    """
    Class to request the weather data and control the view
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(WeatherController, self).__init__(parent)

        self._weather_data = WeatheData()
        self._network_manager = QNetworkAccessManager(self)
        self._timer = QTimer(self)

        self._timer.timeout.connect(self.update_weather)

        self._current_weather = None
        self._forecast_weather = None
        self._api_key = ''

        try:
            with open('resources/api.txt') as f:
                self._api_key = f.readline()
        except FileNotFoundError:
            print('The api key is not found')

    weather_changed = pyqtSignal()

    @pyqtProperty('QString', notify=weather_changed)
    def location(self):
        return self._weather_data.location_name

    @pyqtProperty('QString', notify=weather_changed)
    def description(self):
        return self._weather_data.description

    @pyqtProperty('QString', notify=weather_changed)
    def icon(self):
        return self._weather_data.icon

    @pyqtProperty('QString', notify=weather_changed)
    def temp(self):
        return str(self._weather_data.temperature)

    @pyqtSlot()
    def view_is_ready(self):
        """
        Request the weather data and start the timer when the view is ready,
        called from the view onCompleted.

        :rtype: none
        """
        self._request_weather_data()
        self._timer.start(3600000)

    @pyqtSlot()
    def stop_timer(self):
        pass

    def weather_data_received(self):
        json_str = self._current_weather.readAll()
        json_doc = QJsonDocument.fromJson(json_str)
        self._read_data(json_doc.object())

    def forecast_data_received(self):
        json_str = self._forecast_weather.readAll()
        json_doc = QJsonDocument.fromJson(json_str)
        self._read_forecast_data(json_doc.object())

    def update_weather(self):
        pass

    def _read_data(self, json_object):
        # location
        """
        Read the current weather data from the json object.

        :param json_object: The Json Object
        :return nothing
        """
        if 'name' not in json_object:
            self._weather_data.location_name = 'No data available!'
        else:
            name = json_object['name'].toString()
            qDebug(name)
            if name == '':
                message = json_object['message'].toString()
                self._weather_data.location_name = message
            else:
                self._weather_data.location_name = name

                # temperature
                tDo = json_object['main'].toObject()['temp'].toDouble()
                temp = int(round(tDo))
                self._weather_data.temperature = temp

                # description
                json_weather = json_object['weather'].toArray()[0].toObject()
                desc = json_weather['description'].toString()
                self._weather_data.description = desc

                # icon
                icon = json_weather['icon'].toString()
                temp_icon = '../resources/weather_img/{0}.png'.format(icon)
                self._weather_data.icon = temp_icon

            self.weather_changed.emit()

    def _read_forecast_data(self, json_object):
        json_list = json_object['list'].toArray()
        for obj in json_list:
            json_list_object = obj.toObject()

    def _request_weather_data(self):
        """
        Request the weather over Http request at openweathermap.org, you need
        an API key according to use the services.
        If the call is finished will call according function over Qt's
        signaling System.

        :return: nothing

        """

        # request current weather
        api_call = QUrl(
            'http://api.openweathermap.org/data/2.5/weather?q'
            '=Dachau,de&units=metric&APPID={0}'.format(self._api_key))
        request_current_weather = QNetworkRequest(api_call)
        self._current_weather = self._network_manager.get(
            request_current_weather)
        self._current_weather.finished.connect(self.weather_data_received)

        # forecast data
        api_call_forecast = QUrl(
            'http://api.openweathermap.org/data/2.5/forecast/daily?q=Dachau,'
            'de&cnt=4&units=metric&APPID={0}'.format(self._api_key))
        request_forecast = QNetworkRequest(api_call_forecast)
        self._forecast_weather = self._network_manager.get(request_forecast)
        self._forecast_weather.finished.connect(self.forecast_data_received)


class WeatheData:
    def __init__(self):
        self._dataRecived = False
        self._forecastDataRecived = False
        self._location_name = ''
        self._temperature = 0
        self._description = ''
        self._icon = ''

    @property
    def location_name(self):
        return self._location_name

    @location_name.setter
    def location_name(self, value):
        self._location_name = value

    @property
    def temperature(self):
        return self._temperature

    @temperature.setter
    def temperature(self, value):
        self._temperature = value

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, value):
        self._description = value

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value


class WeatherForecastData(object):

    """Docstring for WeatherForecastData. """

    def __init__(self):
        """TODO: to be defined1. """
        self._temp_min

    @property
    def temp_min(self):
        return self._temp_min

    @temp_min.setter
    def temp_min(self, value):
        self._temp_min = value
