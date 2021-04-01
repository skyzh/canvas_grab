from PySide6.QtCore import *
from time import sleep


class SyncModel(QAbstractListModel):
    NameRole = Qt.UserRole + 1
    StatusRole = Qt.UserRole + 2
    StatusTextRole = Qt.UserRole + 3
    ProgressTextRole = Qt.UserRole + 4
    ProgressRole = Qt.UserRole + 5
    IconNameRole = Qt.UserRole + 6

    def __init__(self, parent=None):
        super().__init__(parent)
        self.items = [
            {'name': '准备中', 'status': 'inProgress',
             'status_text': "请稍候",
             'progress_text': "正在登录到 Canvas LMS",
             'progress': 0.0}]

    def data(self, index, role=Qt.DisplayRole):
        row = index.row()
        if role == SyncModel.NameRole:
            return self.items[row]['name']
        if role == SyncModel.StatusRole:
            return self.items[row]['status']
        if role == SyncModel.StatusTextRole:
            return self.items[row]['status_text']
        if role == SyncModel.ProgressTextRole:
            return self.items[row]['progress_text']
        if role == SyncModel.ProgressRole:
            return self.items[row]['progress']
        if role == SyncModel.IconNameRole:
            return self.items[row]['icon_name']

    def rowCount(self, parent=QModelIndex()):
        return len(self.items)

    def roleNames(self):
        return {
            SyncModel.NameRole: b'name',
            SyncModel.StatusRole: b'status',
            SyncModel.StatusTextRole: b'statusText',
            SyncModel.ProgressTextRole: b'progressText',
            SyncModel.ProgressRole: b'progress',
            SyncModel.IconNameRole: b'iconName'
        }

    def update(self, func):
        self.beginResetModel()
        func()
        self.endResetModel()

    def update_login_user(self, user):
        self.beginResetModel()
        self.items[0]['progress_text'] = f'以 {user} 的身份登录'
        self.items[0]['status_text'] = '正在获取课程列表'
        self.items[0]['progress'] = 0.5
        self.endResetModel()

    def done_fetching_courses(self, text):
        self.beginResetModel()
        self.items[0] = {
            'name': '已登录到 Canvas LMS', 'status': 'done',
            'progress_text': text,
            'icon_name': 'box-arrow-in-right'
        }
        self.endResetModel()

    def new_course_in_progress(self, text):
        self.beginResetModel()
        self.items = [self.items[0], {
            'name': text, 'status': 'inProgress',
            'status_text': '请稍候',
            'progress_text': '正在扫描单元/文件列表',
            'progress': 0.0
        }] + self.items[1:]
        self.endResetModel()

    def finish_course(self, title, text):
        self.beginResetModel()
        self.items = [self.items[0], {
            'name': title, 'status': 'done',
            'progress_text': text,
            'icon_name': 'cloud-check'
        }] + self.items[2:]
        self.endResetModel()
