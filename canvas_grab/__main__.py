#!/usr/bin/env python3

from colorama import init
import canvas_grab
from pathlib import Path
from termcolor import colored
from canvasapi.exceptions import ResourceDoesNotExist
import sys


def main():
    init()
    # Welcome users, and load configurations.
    try:
        interactive, noupdate, config = canvas_grab.get_options.get_options()
    except TypeError:
        # User canceled the configuration process
        return

    # Finally, log in and start synchronize
    canvas = config.endpoint.login()
    print(f'You are logged in as {colored(canvas.get_current_user(), "cyan")}')

    courses = list(canvas.get_courses())
    available_courses, not_available = canvas_grab.utils.filter_available_courses(
        courses)
    filtered_courses = config.course_filter.get_filter().filter_course(
        available_courses)

    total_course_count = len(courses)
    not_available_count = len(not_available)
    filtered_count = len(available_courses) - len(filtered_courses)
    print(colored(
        f'{total_course_count} courses in total, {not_available_count} not available, {filtered_count} filtered', 'cyan'))

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

        # take canvas snapshot
        mode, canvas_snapshots = config.organize_mode.get_snapshots(course)
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
        planner = canvas_grab.planner.Planner(config.organize_mode.delete_file)
        plans = planner.plan(
            canvas_snapshot, on_disk_snapshot, config.file_filter)
        print(colored(
            f'  Updating {len(plans)} objects ({len(canvas_snapshot)} remote objects -> {len(on_disk_snapshot)} local objects)'))
        # start download
        transfer = canvas_grab.transfer.Transfer()
        transfer.transfer(
            on_disk_path, f'{config.download_folder}/_canvas_grab_archive', plans)

    if not noupdate:
        canvas_grab.version.check_latest_version()


if __name__ == '__main__':
    main()
