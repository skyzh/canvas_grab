import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Controls


ColumnLayout {
    width: idProgressListView.width

    RowLayout {
        Image {
            width: 30
            height: 30
            source: "icons/" + iconName + ".svg"
            sourceSize: Qt.size(30, 30)
            Layout.leftMargin: 10
            Layout.rightMargin: 10
            Layout.topMargin: 5
            Layout.bottomMargin: 5
        }
        Text {
            text: name
            font.pointSize: 20
            verticalAlignment: Text.AlignVCenter
        }
    }

    RowLayout {
        Text {
            text: progressText
            verticalAlignment: Text.AlignVCenter
            font.pointSize: 16
            Layout.leftMargin: 10
            Layout.rightMargin: 10
        }
    }
}
