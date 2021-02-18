#!/usr/bin/env python3

from colorama import init
import canvas_grab
from pathlib import Path
import toml
from termcolor import colored
from canvasapi.exceptions import ResourceDoesNotExist


class CanvasGrabCliError(Exception):
    pass


if __name__ == '__main__':
    init()

    config_file = Path('config.toml')
    config = canvas_grab.config.Config()
    if config_file.exists():
        config.from_config(toml.loads(config_file.read_text(encoding='utf8')))
    else:
        config.interact()
        Path('config.toml').write_text(
            toml.dumps(config.to_config()), encoding='utf8')

    canvas = config.endpoint.login()
    print(f'You are logged in as {colored(canvas.get_current_user(), "cyan")}')

    courses = list(canvas.get_courses())
    available_courses, not_available = canvas_grab.utils.filter_available_courses(
        courses)
    print(
        f'Found {len(courses)} courses in total, where {len(not_available)} courses are not available')
    filtered_courses = config.course_filter.course_filter.filter_course(
        available_courses)
    print(f'{len(available_courses) - len(filtered_courses)} courses ignored due to course filter configuration')
    for course in filtered_courses:
        course_name = course.name
        print(f'Course {colored(course_name, "cyan")}')
        # take on-disk snapshot
        on_disk_path = f'{config.download_folder}/{course_name}'
        on_disk_snapshot = canvas_grab.snapshot.OnDiskSnapshot(
            on_disk_path).take_snapshot()
        # take canvas snapshot
        mode = config.organize_mode.mode
        canvas_snapshot_module = canvas_grab.snapshot.CanvasModuleSnapshot(
            course)
        canvas_snapshot_file = canvas_grab.snapshot.CanvasFileSnapshot(course)
        if mode == 'module':
            canvas_snapshots = [canvas_snapshot_module, canvas_snapshot_file]
        elif mode == 'file':
            canvas_snapshots = [canvas_snapshot_file, canvas_snapshot_module]
        else:
            raise CanvasGrabCliError(f"Unsupported organize mode {mode}")
        canvas_snapshot = {}
        for canvas_snapshot_obj in canvas_snapshots:
            try:
                canvas_snapshot = canvas_snapshot_obj.take_snapshot()
            except ResourceDoesNotExist:
                print(
                    colored(f'{mode} not supported, falling back to alternative mode', 'yellow'))
                continue
            break
        planner = canvas_grab.planner.Planner()
        plans = planner.plan(canvas_snapshot, on_disk_snapshot)
        print(colored(
            f'  Updating {len(plans)} files, {len(canvas_snapshot)} files on remote'))
        transfer = canvas_grab.transfer.Transfer()
        transfer.transfer(on_disk_path, plans)
    canvas_grab.version.check_latest_version()
