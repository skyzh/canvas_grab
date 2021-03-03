#!/usr/bin/env python3

from colorama import init
import canvas_grab
from pathlib import Path
import toml
from termcolor import colored
from canvasapi.exceptions import ResourceDoesNotExist
import sys


def get_options():
    import argparse

    def greeting():
        # First, welcome our users
        print("Thank you for using canvas_grab!")
        print(
            f'You are using version {canvas_grab.__version__}. If you have any questions, please file an issue at {colored("https://github.com/skyzh/canvas_grab/issues", "blue")}')
        print(
            f'You may review {colored("README.md", "green")} and {colored("LICENSE", "green")} shipped with this release')
        print(
            f'You may run this code with argument {colored(f"-h","cyan")} for command line usage')
        print('--------------------')

    # Argument Parser initiation
    parser = argparse.ArgumentParser(
        description='Grab all files on Canvas LMS to local directory.')

    # Interactive
    interactive_group = parser.add_mutually_exclusive_group()
    interactive_group.add_argument("-i", "--interactive", dest="interactive", action="store_true",
                                   default=True, help="Set the program to run in interactive mode (default action)")
    interactive_group.add_argument("-I", "--non-interactive", "--no-input", dest="interactive", action="store_false", default=True,
                                   help="Set the program to run in non-interactive mode. This can be used to exit immediately in case of profile corruption without getting stuck with the input.")

    # Reconfiguration
    parser.add_argument("-r", "--reconfigure", "--configure", dest="reconfigure", help="Reconfigure the tool.",
                        action="store_true")

    # Location Specification
    parser.add_argument("-o", "--download-folder", "--output",
                        dest="download", help="Set the download folder.")
    parser.add_argument("-c", "--config-file", dest="config_file", default="config.toml",
                        help="Specify the configuration file. The configurations are loaded in this order: arguments, file specified here, and the default config file config.toml.")

    # Generic Options
    # TODO quiet mode
    # parser.add_argument("-q", "--quiet",dest="quiet", help="Start the program in quiet mode. Only errors will be printed.",
    #                 action="store_true")
    parser.add_argument("--version", action="version",
                        version=canvas_grab.__version__)
    parser.add_argument("-k", "--keep-version", "--no-update", dest="noupdate", action="store_true",
                        default=False, help="Skip update checking. This will be helpful without a stable network connection and prevent reconfiguration.")

    args = parser.parse_args()

    # TODO quiet mode
    greeting()

    config_file = Path(args.config_file)
    config = canvas_grab.config.Config()
    config_fail = False
    if (not args.reconfigure) and config_file.exists():
        try:
            config.from_config(toml.loads(
                config_file.read_text(encoding='utf8')))
        except KeyError as e:
            print(
                f'It seems that you have upgraded canvas_grab. Please reconfigure. ({colored(e, "red")} not found)')
            config_fail = True
    if config_fail or args.reconfigure or not config_file.exists():
        if not args.interactive:
            print(
                "configuration file corrupted or not exist, and non interactive flag is set. Quit immediately.")
            exit(-1)
        try:
            config.interact()
        except KeyboardInterrupt:
            print("User canceled the configuration process")
            return
        Path(args.config_file).write_text(
            toml.dumps(config.to_config()), encoding='utf8')
    if args.download:
        config.download_folder = args.download

    return args.interactive, args.noupdate, config


def main():
    init()
    # Welcome users, and load configurations.
    try:
        interactive, noupdate, config = get_options()
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
