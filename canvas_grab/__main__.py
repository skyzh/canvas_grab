#!/usr/bin/env python3

from colorama import init
import canvas_grab
from pathlib import Path
import toml
from termcolor import colored
from canvasapi.exceptions import ResourceDoesNotExist
import sys


class CanvasGrabCliError(Exception):
    pass


def request_reconfigure():
    if len(sys.argv) >= 2:
        if sys.argv[1] == 'configure':
            return True
    return False


def main():
    init()

    # First, welcome our users
    print("Thank you for using canvas_grab!")
    print(
        f'You are using version {canvas_grab.__version__}. If you have any questions, please file an issue at {colored("https://github.com/skyzh/canvas_grab/issues", "blue")}')
    print(
        f'You may review {colored("README.md", "green")} and {colored("LICENSE", "green")} shipped with this release')
    print('--------------------')

    # Then, load config and start setup wizard

    config_file = Path('config.toml')
    config = canvas_grab.config.Config()
    require_reconfigure = False
    if config_file.exists():
        try:
            config.from_config(toml.loads(
                config_file.read_text(encoding='utf8')))
        except KeyError as e:
            print(
                f'It seems that you have upgraded canvas_grab. Please reconfigure. ({colored(e, "red")} not found)')
            require_reconfigure = True
    if not config_file.exists() or request_reconfigure() or require_reconfigure:
        config.interact()
        Path('config.toml').write_text(
            toml.dumps(config.to_config()), encoding='utf8')

    # Finally, log in and start synchronize
    canvas = config.endpoint.login()
    print(f'You are logged in as {colored(canvas.get_current_user(), "cyan")}')

    courses = list(canvas.get_courses())
    available_courses, not_available = canvas_grab.utils.filter_available_courses(
        courses)
    print(
        f'Found {len(courses)} courses in total ({len(not_available)} of which not available)')
    filtered_courses = config.course_filter.get_filter().filter_course(
        available_courses)
    print(f'{len(available_courses) - len(filtered_courses)} courses ignored due to course filter configuration')

    course_name_parser = canvas_grab.course_parser.CourseParser()
    for idx, course in enumerate(filtered_courses):
        course_name = course.name
        print(
            f'({idx+1}/{len(filtered_courses)}) Course {colored(course_name, "cyan")} (ID: {course.id})')
        # take on-disk snapshot
        parsed_name = course_name_parser.get_parsed_name(course)
        print(f'  Download to {colored(parsed_name, "cyan")}')
        on_disk_path = f'{config.download_folder}/{parsed_name}'
        on_disk_snapshot = canvas_grab.snapshot.OnDiskSnapshot(
            on_disk_path).take_snapshot()
        on_disk_snapshot = config.file_filter.filter_files(on_disk_snapshot)

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
        canvas_snapshot = config.file_filter.filter_files(canvas_snapshot)

        # generate transfer plan
        planner = canvas_grab.planner.Planner(config.organize_mode.delete_file)
        plans = planner.plan(canvas_snapshot, on_disk_snapshot)
        print(colored(
            f'  Updating {len(plans)} files ({len(canvas_snapshot)} files on remote)'))
        # start download
        transfer = canvas_grab.transfer.Transfer()
        transfer.transfer(on_disk_path, plans)

    canvas_grab.version.check_latest_version()


if __name__ == '__main__':
    main()
