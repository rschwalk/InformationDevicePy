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
        QUrl, QJsonDocument, qDebug, QAbstractListModel, QDateTime
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest

from modules.weatherdata import CurrentWeatherData, ForecastDataModel, \
        WeatherForecastData


class WeatherController(QObject):
    """
    Class to request the weather data and control the view
    """

    # noinspection PyUnresolvedReferences
    def __init__(self, parent=None):
        super(WeatherController, self).__init__(parent)

        self._dataReceived = False
        self._forecastDataReceived = False

        self._weather_data = CurrentWeatherData()
        self._weather_forecast_data = []
        self._data_model = ForecastDataModel()

        self._network_manager = QNetworkAccessManager(self)
        self._timer = QTimer(self)

        self._timer.timeout.connect(self.update_weather)

        self._current_weather = None
        self._forecast_weather = None
        self._api_key = ''

        self._last_update_time = ''

        self._requested_location = 'Dachau'

        try:
            with open('resources/api.txt') as f:
                self._api_key = f.readline()
        except FileNotFoundError:
            print('The api key is not found')

    weather_changed = pyqtSignal()

    @pyqtProperty('QString', notify=weather_changed)
    def location(self):
        """
        The location in the weather data.
        :return: string location name
        """
        return self._weather_data.location_name

    @pyqtProperty('QString', notify=weather_changed)
    def description(self):
        """
        The current weather description.
        :return: string description
        """
        return self._weather_data.description

    @pyqtProperty('QString', notify=weather_changed)
    def icon(self):
        """
        Icon for the current weather condition.
        :return: string the path to the icon
        """
        return self._weather_data.icon

    @pyqtProperty('QString', notify=weather_changed)
    def temp(self):
        """
        The current temperature.
        :return: string the formatted temperature
        """
        return str(self._weather_data.temperature)

    model_changed = pyqtSignal()

    @pyqtProperty(QAbstractListModel, notify=model_changed)
    def data_model(self):
        return self._data_model

    last_update_time_changed = pyqtSignal()

    @pyqtProperty('QString', notify=last_update_time_changed)
    def last_update_time(self):
        return self._last_update_time

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
        self._timer.stop()
        qDebug('Timer stopped')

    @pyqtProperty('QString')
    def requested_location(self):
        return self._requested_location

    @requested_location.setter
    def requested_location(self, value):
        self._requested_location = value
        self._request_weather_data()

    def weather_data_received(self):
        json_str = self._current_weather.readAll()
        json_doc = QJsonDocument.fromJson(json_str)
        self._read_current_weather_data(json_doc.object())

    def forecast_data_received(self):
        json_str = self._forecast_weather.readAll()
        json_doc = QJsonDocument.fromJson(json_str)
        self._read_forecast_data(json_doc.object())

    def update_weather(self):
        self._request_weather_data()

    def _read_current_weather_data(self, json_object):
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
                icon_path = '../../resources/weather_img/{0}.png'.format(icon)
                self._weather_data.icon = icon_path

            self.weather_changed.emit()

            self._last_update_time = QDateTime.currentDateTime().toString(
                        'h:mm')
            self.last_update_time_changed.emit()

    def _read_forecast_data(self, json_object):
        json_list = json_object['list'].toArray()
        self._weather_forecast_data = []
        for obj in json_list:
            json_list_object = obj.toObject()
            forecast_data = WeatherForecastData()

            # time
            time = json_list_object['dt'].toInt()
            forecast_data.time = time

            weather_array = json_list_object['weather'].toArray()
            weather_object = weather_array[0].toObject()

            # description
            desc = weather_object['description'].toString()
            forecast_data.description = desc

            # icon
            icon = weather_object['icon'].toString()
            icon_path = '../../resources/weather_img/{0}.png'.format(icon)
            forecast_data.icon = icon_path

            # temperature max / min
            temp_object = json_list_object['temp'].toObject()
            temp_min_double = temp_object['min'].toDouble()
            temp_max_double = temp_object['max'].toDouble()
            temp_min = int(round(temp_min_double))
            forecast_data.temp_min = temp_min
            temp_max = int(round(temp_max_double))
            forecast_data.temp_max = temp_max

            self._weather_forecast_data.append(forecast_data)

        self._data_model.set_all_data(self._weather_forecast_data)
        self.model_changed.emit()

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
            '={0},de&units=metric&APPID={1}'.format(self._requested_location,
                                                    self._api_key))
        request_current_weather = QNetworkRequest(api_call)
        self._current_weather = self._network_manager.get(
            request_current_weather)
        self._current_weather.finished.connect(self.weather_data_received)

        # forecast data
        api_call_forecast = QUrl(
            'http://api.openweathermap.org/data/2.5/forecast/daily?q={0},'
            'de&cnt=4&units=metric&APPID={1}'.format(self._requested_location,
                                                     self._api_key))
        request_forecast = QNetworkRequest(api_call_forecast)
        self._forecast_weather = self._network_manager.get(request_forecast)
        self._forecast_weather.finished.connect(self.forecast_data_received)
