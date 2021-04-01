import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Controls

RowLayout {
    Image {
        width: 30
        height: 30
        source: "icons/cloud-check.svg"
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
