from PySide6.QtGui import QGuiApplication
from PySide6.QtCore import QStringListModel, Qt, QUrl
from PySide6.QtQuick import QQuickView
from PySide6.QtQml import QQmlApplicationEngine
import sys
import os
import canvas_grab
import threading
from .sync_model import SyncModel
from colorama import init
from termcolor import colored
from time import sleep


class Main:
    def __init__(self):
        self._model = SyncModel()

    def _canvas_grab_run(self):
        config = self._config
        canvas = config.endpoint.login()
        user = canvas.get_current_user()
        self._model.update_login_user(user)
        courses = list(canvas.get_courses())
        available_courses, not_available = canvas_grab.utils.filter_available_courses(
            courses)
        filtered_courses = config.course_filter.get_filter().filter_course(
            available_courses)

        total_course_count = len(courses)
        not_available_count = len(not_available)
        filtered_count = len(available_courses) - len(filtered_courses)
        self._model.done_fetching_courses(
            f'您已经以 {user} 身份登录。共有 {total_course_count} 门课程需同步，其中 {not_available_count} 门无法访问，{filtered_count} 门已被过滤。')

        course_name_parser = canvas_grab.course_parser.CourseParser()
        for idx, course in enumerate(filtered_courses):
            course_name = course.name
            self._model.new_course_in_progress(
                f'({idx+1}/{len(filtered_courses)}) {course_name} (ID: {course.id})')
            # take on-disk snapshot
            parsed_name = course_name_parser.get_parsed_name(course)
            print(f'  Download to {colored(parsed_name, "cyan")}')
            on_disk_path = f'{config.download_folder}/{parsed_name}'
            on_disk_snapshot = canvas_grab.snapshot.OnDiskSnapshot(
                on_disk_path).take_snapshot()

            # take canvas snapshot
            canvas_snapshots = config.organize_mode.get_snapshots(course)
            canvas_snapshot = {}
            for canvas_snapshot_obj in canvas_snapshots:
                try:
                    canvas_snapshot = canvas_snapshot_obj.take_snapshot()
                except ResourceDoesNotExist:
                    print(
                        colored(f'{mode} not supported, falling back to alternative mode', 'yellow'))
                    continue
                break
            # generate transfer plan
            planner = canvas_grab.planner.Planner(
                config.organize_mode.delete_file)
            plans = planner.plan(
                canvas_snapshot, on_disk_snapshot, config.file_filter)
            print(colored(
                f'  Updating {len(plans)} objects '))
            # start download
            transfer = canvas_grab.transfer.Transfer()
            transfer.transfer(
                on_disk_path, f'{config.download_folder}/_canvas_grab_archive', plans)
            self._model.finish_course(
                f'{course_name} (ID: {course.id})',
                f'更新了 {len(plans)} 个文件。(远程 {len(canvas_snapshot)} -> 本地 {len(on_disk_snapshot)})')

        if not self._noupdate:
            canvas_grab.version.check_latest_version()

    def main(self):
        init()
        # Welcome users, and load configurations.
        try:
            _, self._noupdate, self._config = canvas_grab.get_options.get_options()
        except TypeError:
            # User canceled the configuration process
            return

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
