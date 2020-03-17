#!/usr/bin/env python3

from canvasapi import Canvas
import canvasapi
import configparser
from colorama import Fore, Back, Style
import colorama
import json
import re
import pathlib
import os
import time
from datetime import datetime
import sys
import requests
from download_file_ex import download_file
import toml
from sys import exit
from utils import is_windows, file_regex
from version import check_latest_version
import shlex
import multiprocessing
from config import *

if is_windows():
    from win32_setctime import setctime

checkpoint = {}
new_files_list = []
updated_files_list = []
ffmpeg_commands = []


def main():
    colorama.init()

    print("Thank you for using canvas_grab!")
    print(
        f"If you have any questions, please file an issue at {Fore.BLUE}https://github.com/skyzh/canvas_grab/issues{Style.RESET_ALL}")
    print(
        f"You may review {Fore.GREEN}README(_zh-hans).md{Style.RESET_ALL} and {Fore.GREEN}LICENSE{Style.RESET_ALL} shipped with this release")
    print(
        f"Please MAKE SURE that you've reviewed the LICENSE. Refer to {Fore.BLUE}https://github.com/skyzh/canvas_grab/issues/29{Style.RESET_ALL} for why we enforced you to take this action.")
    if ENABLE_VIDEO:
        print(f"Note: You've enabled video download. You should install the required tools yourself.")
        print(
            f"      This is an experimental functionality and takes up large amount of bandwidth. {Fore.RED}Use at your own risk.{Style.RESET_ALL}")

    canvas = Canvas(API_URL, API_KEY)

    try:
        print(f'{Fore.BLUE}Logging in...{Style.RESET_ALL}')
        print(
            f"{Fore.GREEN}Logged in to {API_URL} as {canvas.get_current_user()}{Style.RESET_ALL}")
    except canvasapi.exceptions.InvalidAccessToken:
        print(
            f"{Fore.RED}Invalid access token, please check your API_KEY in config file")
        if is_windows():
            # for windows double-click user
            input()
        exit()

    os.makedirs(pathlib.Path(CHECKPOINT_FILE).parent, exist_ok=True)

    try:
        with open(CHECKPOINT_FILE, 'r') as file:
            global checkpoint
            checkpoint = json.load(file)
    except:
        print(f"{Fore.RED}No checkpoint found")

    courses = canvas.get_courses()

    try:
        for course in courses:
            if not hasattr(course, "name"):
                if VERBOSE_MODE:
                    print(
                        f"{Fore.YELLOW}Course {course.id}: not available{Style.RESET_ALL}")
            elif course.id in IGNOGED_CANVAS_ID:
                print(
                    f"{Fore.CYAN}Ignored Course: {course.course_code}{Style.RESET_ALL}")
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
    except KeyboardInterrupt:
        print("{Fore.RED}Terminated due to keyboard interrupt.{Style.RESET_ALL}")

    do_checkpoint()

    if len(new_files_list) == 0:
        print("All files up to date")
    else:
        print(
            f"{Fore.GREEN}{len(new_files_list)} new or updated files:{Style.RESET_ALL}")
        for f in new_files_list:
            print(f)

    if len(updated_files_list) != 0:
        print(
            f"{Fore.GREEN}{len(updated_files_list)} files have a more recent version in Canvas:{Style.RESET_ALL}")
        for f in updated_files_list:
            print(f)

    if ENABLE_VIDEO:
        print(f"{Fore.GREEN}{len(ffmpeg_commands)} videos resolved{Style.RESET_ALL}")
        print(
            f"Please run the automatically-generated script {Fore.BLUE}download_video.(sh/ps1){Style.RESET_ALL} to download all videos.")
        with open("download_video.sh", 'w') as file:
            file.write("\n".join(ffmpeg_commands))
        with open("download_video.ps1", 'w') as file:
            file.write("\n".join(ffmpeg_commands))

    check_latest_version()

    print(f"{Fore.GREEN}Done.{Style.RESET_ALL}")

    if is_windows():
        # for windows double-click user
        input()


def do_checkpoint():
    with open(CHECKPOINT_FILE+'.canvas_tmp', 'w') as file:
        json.dump(checkpoint, file)
    os.replace(CHECKPOINT_FILE+'.canvas_tmp', CHECKPOINT_FILE)


def check_download_rule(file, path, json_key) -> (bool, str, bool):
    if file.url == "":
        return (False, "file not available", False)
    
    update_flag = False
    updated_at = file.updated_at

    if json_key in checkpoint:
        if checkpoint[json_key]["updated_at"] != updated_at:
            update_flag = True
    
    if not any(file.display_name.lower().endswith(pf) for pf in ALLOW_FILE_EXTENSION):
        return (False, "filtered by extension", update_flag)

    if file.size >= MAX_SINGLE_FILE_SIZE * 1024 * 1024:
        return (False, "size limit exceed", update_flag)

    if json_key in checkpoint and NEVER_DOWNLOAD_AGAIN:
        return (False, "file has been downloaded before (NEVER_DOWNLOAD_AGAIN)", update_flag)

    if pathlib.Path(path).exists() and NEVER_OVERWRITE_FILE:
        return (False, "file exists and will not be overwritten (NEVER_OVERWRITE_FILE)", update_flag)

    if json_key in checkpoint:
        if checkpoint[json_key]["updated_at"] == updated_at:
            return (False, "already downloaded and is latest version", update_flag)

    return (True, "", update_flag)


def parse_course_folder_name(course: canvasapi.canvas.Course) -> str:
    if course.id in CUSTOM_NAME_OVERRIDE:
        return re.sub(r'[:*?"<>|]', REPLACE_ILLEGAL_CHAR_WITH, CUSTOM_NAME_OVERRIDE[course.id])

    r = re.search(
        r"\((?P<semester_id>[0-9\-]+)\)-(?P<sjtu_id>[A-Za-z0-9]+)-(?P<classroom_id>.+)-(?P<name>.+)\Z", course.course_code)
    if r is not None:
        r = r.groupdict()
    else:
        r = {}
    template_map = {
        r"{CANVAS_ID}": str(course.id),
        r"{SJTU_ID}": r.get("sjtu_id", ""),
        r"{SEMESTER_ID}": r.get("semester_id", ""),
        r"{CLASSROOM_ID}": r.get("classroom_id", ""),
        r"{NAME}": re.sub(file_regex, REPLACE_ILLEGAL_CHAR_WITH, course.name.replace("（", "(").replace("）", ")")),
        r"{COURSE_CODE}": course.course_code
    }

    folderName = NAME_TEMPLATE
    for old, new in template_map.items():
        folderName = folderName.replace(old, new)
    folderName = re.sub(r'[:*?"<>|]', REPLACE_ILLEGAL_CHAR_WITH, folderName)
    return folderName


def resolve_video(page: canvasapi.page.PageRevision):
    title = page.title
    if VERBOSE_MODE:
        print(f"    {Fore.GREEN}Resolving page {title}{Style.RESET_ALL}")
    if not hasattr(page, "body") or page.body is None:
        if VERBOSE_MODE:
            print(
                f"    {Fore.RED}This page has no attribute 'body'{Style.RESET_ALL}")
        yield (False, "failed to resolve page")
        return
    links = re.findall(r"\"(https:\/\/vshare.sjtu.edu.cn\/.*?)\"", page.body)
    if len(links) != 0:
        if VERBOSE_MODE:
            print(
                f"    {Style.DIM}unsupported link: vshare.sjtu.edu.cn{Style.RESET_ALL}")
        for i in range(len(links)):
            yield (False, "unsupported video link")

    links = re.findall(r"\"(https:\/\/v.sjtu.edu.cn\/.*?)\"", page.body)
    for link in links:
        try:
            video_page = requests.get(link, timeout=3).text
        except KeyboardInterrupt:
            raise
        except Exception as e:
            if VERBOSE_MODE:
                print(
                    f"    {Fore.RED}Failed to resolve video: {e}{Style.RESET_ALL}")
            yield (False, "failed to resolve video")
            continue
        video_link = re.findall(r"src=\'(.*?.m3u8)\'", video_page)
        if len(video_link) != 1:
            if VERBOSE_MODE:
                print(
                    f"    {Fore.RED}Failed to resolve video: video link {video_link} != 1{Style.RESET_ALL}")
            yield (False, "failed to resolve video")
            continue
        yield (True, video_link[0])
    pass


def organize_by_file(course: canvasapi.canvas.Course) -> (canvasapi.canvas.File, str):
    folders = {folder.id: folder.full_name for folder in course.get_folders()}
    for file in course.get_files():
        folder = folders[file.folder_id] + "/"
        folder = folder.lstrip("course files/")
        yield (file, folder)


def organize_by_module(course: canvasapi.canvas.Course) -> (canvasapi.canvas.File, str):
    for m_idx, module in enumerate(course.get_modules()):
        print(f"    Module {Fore.CYAN}{module.name}{Style.RESET_ALL}")
        for item in module.get_module_items():
            if item.type == "File":
                yield (course.get_file(item.content_id), '%d ' % m_idx + re.sub(file_regex, "_", module.name.replace("（", "(").replace("）", ")")))


def get_file_list(course: canvasapi.canvas.Course, organize_by: str) -> (canvasapi.canvas.File, str):
    another_mode = ""
    try:
        if organize_by == "file":
            another_mode = "module"
            for (file, path) in organize_by_file(course):
                yield (file, path)
        elif organize_by == "module":
            another_mode = "file"
            for (file, path) in organize_by_module(course):
                yield (file, path)
        else:
            print(
                f"    {Fore.RED}unsupported organize mode: {ORGANIZE_BY}{Style.RESET_ALL}")
        return
    except canvasapi.exceptions.ResourceDoesNotExist:
        pass
    except canvasapi.exceptions.Unauthorized:
        pass
    except Exception:
        raise
    print(f"    {Fore.YELLOW}{organize_by} not available, falling back to {another_mode}{Style.RESET_ALL}")
    for (file, path) in get_file_list(course, another_mode):
        yield (file, path)


def process_course(course: canvasapi.canvas.Course):
    name = parse_course_folder_name(course)
    print(
        f"Course {Fore.CYAN}{course.course_code} (ID: {course.id}){Style.RESET_ALL}")

    reasons_of_not_download = {}

    for (file, folder) in get_file_list(course, ORGANIZE_BY):
        directory = os.path.join(BASE_DIR, name, folder)
        path = os.path.join(directory, file.display_name)

        json_key = f"{name}/{folder}{file}"

        can_download, reason, update_flag = check_download_rule(
            file, path, json_key)

        if can_download:
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
            try:
                pathlib.Path(path).unlink()
            except:
                pass
            print(
                f"    {Fore.GREEN}{'Update' if update_flag else 'New'}: {file.display_name} ({file.size // 1024 / 1000}MB){Style.RESET_ALL}")
            download_file(file.url, "    Downloading", path)
            if OVERRIDE_FILE_TIME:
                c_time = datetime.strptime(
                    file.created_at, '%Y-%m-%dT%H:%M:%S%z').timestamp()
                m_time = datetime.strptime(
                    file.updated_at, '%Y-%m-%dT%H:%M:%S%z').timestamp()
                a_time = time.time()
                if is_windows():
                    setctime(path, c_time)
                os.utime(path, (a_time, m_time))
            checkpoint[json_key] = {"updated_at": file.updated_at}
            new_files_list.append(path)
        else:
            if VERBOSE_MODE:
                print(
                    f"    {Style.DIM}Ignore {file.display_name}: {reason}{Style.RESET_ALL}")
            else:
                prev_cnt = reasons_of_not_download.get(reason, 0)
                reasons_of_not_download[reason] = prev_cnt + 1
            if update_flag:
                updated_files_list.append(path)

        do_checkpoint()

    if ENABLE_VIDEO:
        for page in course.get_pages():
            for (result, msg) in resolve_video(page.show_latest_revision()):
                if result == True:
                    filename = msg.split("/")[-2]
                    json_key = f"{name}/{page.title}-{filename}"
                    path = os.path.join(
                        BASE_DIR, name, f"{page.title}-{filename}")
                    if not Path(path).exists():
                        quoted_path = shlex.quote(path)
                        ffmpeg_commands.append(
                            f"{FFMPEG_PATH} -i '{msg}' -c copy -bsf:a aac_adtstoasc {quoted_path}")
                else:
                    prev_cnt = reasons_of_not_download.get(msg, 0)
                    reasons_of_not_download[msg] = prev_cnt + 1

    for (reason, cnt) in reasons_of_not_download.items():
        print(f"    {Style.DIM}{cnt} files ignored: {reason}{Style.RESET_ALL}")


if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
