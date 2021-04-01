import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Controls

ColumnLayout {
    width: idProgressListView.width

    RowLayout {
        BusyIndicator {
            width: 30
            height: 30
            Layout.leftMargin: 5
            Layout.rightMargin: 5
        }
        Text {
            text: name
            font.pointSize: 20
            verticalAlignment: Text.AlignVCenter
        }
    }

    RowLayout {
        Text {
            text: statusText
            verticalAlignment: Text.AlignVCenter
            font.pointSize: 16
            Layout.leftMargin: 10
            Layout.rightMargin: 10
        }
        ProgressBar {
            id: bar
            value: progress
            Layout.fillWidth: true
            Layout.rightMargin: 10
        }
    }

    RowLayout {
        Image {
            width: 30
            height: 30
            source: "icons/info-circle-fill.svg"
            sourceSize: Qt.size(16, 16)
            Layout.leftMargin: 10
        }
        Text {
            text: progressText
            color: "steelblue"
            font.pointSize: 16
            verticalAlignment: Text.AlignVCenter
        }
    }
}
