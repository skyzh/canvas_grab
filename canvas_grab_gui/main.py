from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QStringListModel, Qt, QUrl
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QQmlApplicationEngine
import sys
import os
import canvas_grab
import threading
from .sync_model import SyncModel


class Main:
    def __init__(self):
        self._model = SyncModel()

    def _canvas_grab_run(self):
        self._model.run()

    def main(self):
        app = QGuiApplication(sys.argv)
        engine = QQmlApplicationEngine()
        engine.rootContext().setContextProperty('py_sync_model', self._model)
        engine.load(os.path.join(os.path.dirname(__file__), "ui/main.qml"))

        if not engine.rootObjects():
            sys.exit(-1)

        thread = threading.Thread(target=self._canvas_grab_run)
        thread.start()

        sys.exit(app.exec_())


if __name__ == "__main__":
    Main().main()
