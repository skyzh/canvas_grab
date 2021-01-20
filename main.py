#!/usr/bin/env python3

import configparser
from datetime import datetime
import multiprocessing
import os
import pathlib
import re
import shlex
import sys
import time
from pathlib import Path
from sys import exit

import canvasapi
import colorama
import requests
import toml
from canvasapi import Canvas
from colorama import Back, Fore, Style
from file_organizer import FileOrganizer, Link
from checkpoint import Checkpoint, CheckpointItem
from config import Config
from download_file_ex import download_file
from download_link import download_link
from utils import file_regex, is_windows, path_regex, remove_empty_dir, apply_datetime_attr
from version import VERSION, check_latest_version

multiprocessing.freeze_support()


checkpoint = None
new_files_list = []
updated_files_list = []
ffmpeg_commands = []
current_file_list = []
current_link_list = []
failure_file_list = []
config = Config()


def main():
    colorama.init()
    print("Thank you for using canvas_grab!")
    print(
        f"You are using version {VERSION}. If you have any questions, please file an issue at {Fore.BLUE}https://github.com/skyzh/canvas_grab/issues{Style.RESET_ALL}")
    print(
        f"You may review {Fore.GREEN}README(_zh-hans).md{Style.RESET_ALL} and {Fore.GREEN}LICENSE{Style.RESET_ALL} shipped with this release")
    config.load_config()
    if config.ENABLE_VIDEO:
        print(f"Note: You've enabled video download. You should install the required tools yourself.")
        print(
            f"      This is an experimental functionality and takes up large amount of bandwidth. {Fore.RED}Use at your own risk.{Style.RESET_ALL}")
    canvas = Canvas(config.API_URL, config.API_KEY)

    try:
        print(f'{Fore.BLUE}Logging in...{Style.RESET_ALL}')
        print(
            f"{Fore.GREEN}Logged in to {config.API_URL} as {canvas.get_current_user()}{Style.RESET_ALL}")
    except canvasapi.exceptions.InvalidAccessToken:
        print(
            f"{Fore.RED}Invalid access token, please check your config.API_KEY in config file")
        if is_windows():
            # for windows double-click user
            input()
        exit()

    try:
        global checkpoint
        checkpoint = Checkpoint(config.CHECKPOINT_FILE)
        checkpoint.load()
    except FileNotFoundError:
        print(f"{Fore.RED}No checkpoint found{Style.RESET_ALL}")

    courses = [course for course in canvas.get_courses() if hasattr(course, "name")]
    if config.WHITELIST_CANVAS_ID:
        print(f"{Fore.BLUE}Whilelist mode enabled{Style.RESET_ALL}")
        courses = [
            course for course in courses if course.id in config.WHITELIST_CANVAS_ID]
    try:
        for course in courses:
            if course.start_at:
                delta = -(datetime.strptime(
                    course.start_at, r'%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None) - datetime.now()).days
            else:
                delta = 0
            if course.id in config.IGNORED_CANVAS_ID:
                print(
                    f"{Fore.CYAN}Explicitly Ignored Course: {course.course_code}{Style.RESET_ALL}")
            elif config.RETAIN_COURSE_DAYS != 0 and delta > config.RETAIN_COURSE_DAYS:
                print(
                    f"{Fore.CYAN}Outdated Course: {course.course_code}{Style.RESET_ALL}")
            else:
                try:
                    process_course(course)
                except KeyboardInterrupt:
                    raise
                except canvasapi.exceptions.Unauthorized as e:
                    print(
                        f"{Fore.RED}An error occoured when processing this course (unauthorized): {e}{Style.RESET_ALL}")
                except canvasapi.exceptions.ResourceDoesNotExist as e:
                    print(
                        f"{Fore.RED}An error occoured when processing this course (resourse not exist): {e}{Style.RESET_ALL}")
        if config.SCAN_STALE_FILE:
            scan_stale_files(courses)
    except KeyboardInterrupt:
        print(f"{Fore.RED}Terminated due to keyboard interrupt.{Style.RESET_ALL}")

    checkpoint.dump()

    if new_files_list:
        print(
            f"{Fore.GREEN}{len(new_files_list)} new or updated files:{Style.RESET_ALL}")
        for f in new_files_list:
            print(f"    {f}")

    if updated_files_list:
        print(
            f"{Fore.GREEN}{len(updated_files_list)} files have a more recent version on Canvas:{Style.RESET_ALL}")
        for f in updated_files_list:
            print(f"    {f}")

    if failure_file_list:
        print(
            f"{Fore.YELLOW}{len(failure_file_list)} files are not downloaded:{Style.RESET_ALL}")
        for f in failure_file_list:
            print(f"    {f}")

    if not new_files_list and not updated_files_list:
        print("All files up to date")

    if config.ENABLE_VIDEO:
        print(f"{Fore.GREEN}{len(ffmpeg_commands)} videos resolved{Style.RESET_ALL}")
        print(
            f"Please run the automatically-generated script {Fore.BLUE}download_video.(sh/ps1){Style.RESET_ALL} to download all videos.")
        with open("download_video.sh", 'w') as file:
            file.write("\n".join(ffmpeg_commands))
        with open("download_video.ps1", 'w') as file:
            file.write("\n".join(ffmpeg_commands))

    if config.ALLOW_VERSION_CHECK:
        check_latest_version()

    print(f"{Fore.GREEN}Done.{Style.RESET_ALL}")

    if is_windows():
        # for windows double-click user
        input()


def scan_stale_files(courses):
    print(f"{Fore.CYAN}Scanning stale files{Style.RESET_ALL}")
    base_path = Path(config.BASE_DIR)

    file_list = []
    for file in current_file_list:
        file_list.append(str(Path(file)))
    for file in current_link_list:
        file_list.append(str(Path(file)))
    stale_file_list = []
    for course in courses:
        cource_path = base_path / parse_course_folder_name(course)
        for p in cource_path.rglob("*"):
            if p.is_file() and not p.name.startswith("."):
                if not str(p) in file_list:
                    print(f"    {str(p)}")
                    stale_file_list.append(p)
    if stale_file_list:
        print(f"{Fore.RED}Remove {len(stale_file_list)} files?{Style.RESET_ALL} (Press 'y' to continue) ", end="")
        if input() == "y":
            for file in stale_file_list:
                file.unlink()
            print(f"{Fore.GREEN}Remove empty directories.{Style.RESET_ALL}")
            try:
                for course in courses:
                    cource_path = base_path / parse_course_folder_name(course)
                    remove_empty_dir(cource_path)
            except Exception as e:
                print(
                    f"{Fore.RED}Failed to remove empty directories: {e}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Stale files removed.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}No action taken.{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}No stale files.{Style.RESET_ALL}")


def check_download_rule(file: canvasapi.canvas.File, path: Path, json_key: str) -> (bool, str, bool):
    if file.url == "":
        return (False, "file not available", False)

    if file.size is None:
        return (False, f"file link not available", False)

    update_flag = False
    updated_at = file.updated_at_date
    path_exist = Path(path).exists()

    global checkpoint
    history = checkpoint.get(json_key)

    if history and history.updated_at != updated_at:
        update_flag = True

    if not any(file.display_name.lower().endswith(pf) for pf in config.ALLOW_FILE_EXTENSION):
        return (False, "filtered by extension", update_flag)

    if file.size >= config.MAX_SINGLE_FILE_SIZE * 1024 * 1024:
        return (False, f"size limit exceed (>= {config.MAX_SINGLE_FILE_SIZE} MB)", update_flag)

    if history and config.NEVER_DOWNLOAD_AGAIN:
        return (False, "file has been downloaded before (config.NEVER_DOWNLOAD_AGAIN)", update_flag)

    if path_exist and config.NEVER_OVERWRITE_FILE:
        return (False, "file exists and will not be overwritten (config.NEVER_OVERWRITE_FILE)", update_flag)

    if history:
        if history.id != file.id and history.session == config.SESSION:
            print(
                f"    {Fore.YELLOW}Duplicated files detected. ({file.display_name}){Style.RESET_ALL}")
            return (False, "files with duplicated path", update_flag)

        checkpoint[json_key].session = config.SESSION

        if path_exist and history.updated_at == updated_at:
            return (False, "already downloaded and is latest version", update_flag)

    return (True, "", update_flag)


def replaceIllegalChar(filename, regex=path_regex):
    return re.sub(regex, config.REPLACE_ILLEGAL_CHAR_WITH, filename)


def parse_course_folder_name(course: canvasapi.canvas.Course) -> str:
    if course.id in config.CUSTOM_NAME_OVERRIDE:
        return replaceIllegalChar(config.CUSTOM_NAME_OVERRIDE[course.id])

    r = re.search(
        r"\((?P<semester_id>[0-9\-]+)\)-(?P<sjtu_id>[A-Za-z0-9]+)-(?P<classroom_id>.+)-(?P<name>.+)\Z", course.course_code)
    if r is not None:
        r = r.groupdict()
    else:
        r = {}

    if hasattr(course, "original_name"):
        course_name = course.original_name
        course_nickname = course.name
    else:
        course_name = course.name
        course_nickname = course.name

    template_map = {
        r"{CANVAS_ID}": str(course.id),
        r"{SJTU_ID}": r.get("sjtu_id", ""),
        r"{SEMESTER_ID}": r.get("semester_id", ""),
        r"{CLASSROOM_ID}": r.get("classroom_id", ""),
        r"{NAME}": replaceIllegalChar(course_name.replace("（", "(").replace("）", ")"), file_regex),
        r"{NICKNAME}": replaceIllegalChar(course_nickname.replace("（", "(").replace("）", ")"), file_regex),
        r"{COURSE_CODE}": course.course_code
    }

    folderName = config.NAME_TEMPLATE
    for old, new in template_map.items():
        folderName = folderName.replace(old, new)

    folderName = replaceIllegalChar(folderName)
    return folderName


def resolve_video(page: canvasapi.page.PageRevision) -> (bool, str):
    if config.VERBOSE_MODE:
        print(f"    {Fore.GREEN}Resolving page {page.title}{Style.RESET_ALL}")

    if not hasattr(page, "body") or page.body is None:
        if config.VERBOSE_MODE:
            print(
                f"    {Fore.RED}This page has no attribute 'body'{Style.RESET_ALL}")
        yield (False, "failed to resolve page")
        return

    links = re.findall(r"\"(https:\/\/vshare.sjtu.edu.cn\/.*?)\"", page.body)
    if links:
        if config.VERBOSE_MODE:
            print(
                f"    {Style.DIM}unsupported link: vshare.sjtu.edu.cn{Style.RESET_ALL}")
        for _ in range(len(links)):
            yield (False, "unsupported video link")

    links = re.findall(r"\"(https:\/\/v.sjtu.edu.cn\/.*?)\"", page.body)
    for link in links:
        try:
            video_page = requests.get(link, timeout=3).text
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if config.VERBOSE_MODE:
                print(
                    f"    {Fore.RED}Failed to resolve video: {e}{Style.RESET_ALL}")
            yield (False, "failed to resolve video")
            continue
        video_link = re.findall(r"src=\'(.*?.m3u8)\'", video_page)
        if len(video_link) != 1:
            if config.VERBOSE_MODE:
                print(
                    f"    {Fore.RED}Failed to resolve video: video link {video_link} != 1{Style.RESET_ALL}")
            yield (False, "failed to resolve video")
            continue
        yield (True, video_link[0])


def get_file_list(course: canvasapi.canvas.Course, organize_by: str) -> (canvasapi.canvas.File, str):
    if not isinstance(organize_by, FileOrganizer.By):
        organize_by = FileOrganizer.By(organize_by)

    another_mode = {
        FileOrganizer.By.MODULE: FileOrganizer.By.FILE,
        FileOrganizer.By.FILE: FileOrganizer.By.MODULE,
        FileOrganizer.By.MODULE_WITH_FILE: None
    }[organize_by]

    for mode in [organize_by, another_mode]:
        try:
            for (file, path) in FileOrganizer(course, mode, config).get():
                yield(file, path)
            return
        except canvasapi.exceptions.ResourceDoesNotExist:
            pass
        except canvasapi.exceptions.Unauthorized:
            pass
        except Exception:
            raise

        print(f"    {Fore.RED}unsupported organize mode: {mode.value}{Style.RESET_ALL}")

        if mode == FileOrganizer.By.MODULE_WITH_FILE:
            return
        elif mode == organize_by:
            print(f"    {Fore.YELLOW}{organize_by.value} mode not available, falling back to {another_mode.value} mode{Style.RESET_ALL}")
        elif mode == another_mode:
            # FIXME: THIS IS A FATAL STATE, NEED A BETTER RESPONSE
            pass


def process_course(course: canvasapi.canvas.Course):
    global checkpoint

    name = parse_course_folder_name(course)
    print(
        f"Course {Fore.CYAN}{course.course_code} (ID: {course.id}){Style.RESET_ALL}")

    reasons_of_not_download = {}

    organize_mode = config.ORGANIZE_BY

    if course.id in config.CUSTOM_ORGANIZE:
        organize_mode = config.CUSTOM_ORGANIZE[course.id]

    for (file, folder) in get_file_list(course, organize_mode):
        directory = os.path.join(config.BASE_DIR, name, folder).rstrip()
        filename = replaceIllegalChar(file.display_name, file_regex)
        path = os.path.join(directory, filename)
        json_key = f"{name}/{folder}{file}"

        if type(file) == Link:
            if config.ENABLE_LINK:
                Path(directory).mkdir(parents=True, exist_ok=True)
                path += '.url' if is_windows() else '.html'
                download_link(file.url, path)
                current_link_list.append(path)
                if config.OVERRIDE_FILE_TIME:
                    # cannot be implemented
                    # apply_datetime_attr(path, file.created_at, file.updated_at)
                    pass
            elif config.VERBOSE_MODE:
                print(
                    f"    {Style.DIM}Ignore {file.display_name}: {'ENABLE_LINK disabled'}{Style.RESET_ALL}")
            continue

        can_download, reason, update_flag = check_download_rule(
            file, path, json_key)

        if can_download:
            Path(directory).mkdir(parents=True, exist_ok=True)
            try:
                Path(path).unlink()
            except:
                pass
            print(
                f"    {Fore.GREEN}{'Update' if update_flag else 'New'}: {file.display_name} ({file.size // 1024 / 1000}MB){Style.RESET_ALL}")
            try:
                download_file(file.url, "    Downloading",
                              path, file.size, verbose=config.VERBOSE_MODE)
                if config.OVERRIDE_FILE_TIME:
                    apply_datetime_attr(path, file.created_at, file.updated_at)
                checkpoint[json_key] = CheckpointItem(
                    file.updated_at_date, file.id, config.SESSION)

                new_files_list.append(path)
            except Exception as e:
                print(
                    f"    {Fore.YELLOW}Failed to download: {e}{Style.RESET_ALL}")
                failure_file_list.append(path)
        else:
            if config.VERBOSE_MODE:
                print(
                    f"    {Style.DIM}Ignore {file.display_name}: {reason}{Style.RESET_ALL}")
            else:
                prev_cnt = reasons_of_not_download.get(reason, 0)
                reasons_of_not_download[reason] = prev_cnt + 1
            if update_flag:
                updated_files_list.append(path)
        current_file_list.append(path)
        checkpoint.dump()

    if config.ENABLE_VIDEO:
        for page in course.get_pages():
            for (result, msg) in resolve_video(page.show_latest_revision()):
                if result:
                    filename = msg.split("/")[-2]
                    json_key = f"{name}/{page.title}-{filename}"
                    path = os.path.join(config.BASE_DIR, name, f"{page.title}-{filename}")
                    path = replaceIllegalChar(path)
                    if not Path(path).exists():
                        quoted_path = shlex.quote(path)
                        ffmpeg_commands.append(f"{config.FFMPEG_PATH} -i '{msg}' -c copy -bsf:a aac_adtstoasc {quoted_path}")
                else:
                    prev_cnt = reasons_of_not_download.get(msg, 0)
                    reasons_of_not_download[msg] = prev_cnt + 1

    for (reason, cnt) in reasons_of_not_download.items():
        print(f"    {Style.DIM}{cnt} files ignored: {reason}{Style.RESET_ALL}")


if __name__ == '__main__':
    main()
