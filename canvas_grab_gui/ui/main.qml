import QtQuick
import QtQuick.Window
import QtQuick.Layouts
import QtQuick.Controls
import Qt.labs.qmlmodels

Window {
    id: window
    width: 800
    height: 600
    visible: true
    title: qsTr("Canvas Grab")

    ListView {
        id: idProgressListView
        width: parent.width
        height: parent.height
        spacing: 10

        model: py_sync_model
        delegate: chooser

        DelegateChooser {
            id: chooser
            role: "status"
            DelegateChoice { roleValue: "inProgress"; InProgress {} }
            DelegateChoice { roleValue: "done"; Done {} }
        }
    }
}
