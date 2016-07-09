import QtQuick 2.4

WeatherForecastForm {
    anchors.fill: parent
    Component.onCompleted: weather.view_is_ready()
    Component.onDestruction: if (weather != null) weather.stop_timer()

    iconCurrent.source: weather.icon

    forecastListView {
        model: weather.data_model
        delegate: ForecastDelegate {}
    }


//    forecastListView.model: weather.dataModel
//    forecastListView.delegate: forecastDelegate
}