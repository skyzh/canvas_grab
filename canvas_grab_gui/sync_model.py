from PySide6.QtCore import *
from time import sleep


class SyncModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    StatusRole = Qt.UserRole + 2
    StatusTextRole = Qt.UserRole + 3
    ProgressTextRole = Qt.UserRole + 4

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = [
            {'name': '软件工程', 'status': 'inProgress',
             'statusText': "扫描文件中",
             'progressText': "Module 1: 233333"},
            {'name': '软件工程', 'status': 'done'},
        ]

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == SyncModel.NameRole:
            return self.items[row]['name']
        if role == SyncModel.StatusRole:
            return self.items[row]['status']
        if role == SyncModel.StatusTextRole:
            return self.items[row]['statusText']
        if role == SyncModel.ProgressTextRole:
            return self.items[row]['progressText']

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def roleNames(self):
        return {
            SyncModel.NameRole: b'name',
            SyncModel.StatusRole: b'status',
            SyncModel.StatusTextRole: b'statusText',
            SyncModel.ProgressTextRole: b'progressText'
        }

    on_progress = Signal()

    @Slot()
    def run(self):
        for i in range(10):
            sleep(1)
            self.beginResetModel()
            self.items = [self.items[0]] + self.items
            self.endResetModel()
