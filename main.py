#!/usr/bin/env python3

import canvasapi
from canvasapi import Canvas
import configparser
import colorama
from colorama import Fore, Back, Style
import json
import re
import pathlib
from pathlib import Path
import os
import time
from datetime import datetime
import sys
import requests
from download_file_ex import download_file
import toml
from sys import exit
from utils import is_windows, file_regex, path_regex, remove_empty_dir
from version import check_latest_version, VERSION
import shlex
from config import Config
import multiprocessing
multiprocessing.freeze_support()


if is_windows():
    from win32_setctime import setctime

checkpoint = {}
course_files = {}
new_files_list = []
updated_files_list = []
ffmpeg_commands = []
current_file_list = []
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

    os.makedirs(Path(config.CHECKPOINT_FILE).parent, exist_ok=True)

    try:
        with open(config.CHECKPOINT_FILE, 'r') as file:
            global checkpoint
            checkpoint = json.load(file)
    except:
        print(f"{Fore.RED}No checkpoint found{Style.RESET_ALL}")

    courses = [course for course in canvas.get_courses()
               if hasattr(course, "name")]

    try:
        for course in courses:
            if course.id in config.IGNORED_CANVAS_ID:
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
        if config.SCAN_STALE_FILE:
            scan_stale_files(courses)
    except KeyboardInterrupt:
        print(f"{Fore.RED}Terminated due to keyboard interrupt.{Style.RESET_ALL}")

    do_checkpoint()

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


def do_checkpoint():
    with open(config.CHECKPOINT_FILE+'.canvas_tmp', 'w') as file:
        json.dump(checkpoint, file)
    os.replace(config.CHECKPOINT_FILE+'.canvas_tmp', config.CHECKPOINT_FILE)


def scan_stale_files(courses):
    print(f"{Fore.CYAN}Scanning stale files{Style.RESET_ALL}")
    base_path = Path(config.BASE_DIR)

    file_list = []
    for file in current_file_list:
        file_list.append(str(Path(file)))
    stale_file_list = []
    for course in courses:
        cource_path = base_path/parse_course_folder_name(course)
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
                    cource_path = base_path/parse_course_folder_name(course)
                    remove_empty_dir(cource_path)
            except Exception as e:
                print(
                    f"{Fore.Red}Failed to remove empty directories: {e}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}Stale files removed.{Style.RESET_ALL}")
        else:
            print(f"{Fore.GREEN}No action taken.{Style.RESET_ALL}")
    else:
        print(f"{Fore.GREEN}No stale files.{Style.RESET_ALL}")


def check_download_rule(file, path, json_key) -> (bool, str, bool):
    if file.url == "":
        return (False, "file not available", False)
    
    if file.size is None:
        return (False, f"file link not available", False)

    update_flag = False
    updated_at = file.updated_at
    path_exist = Path(path).exists()

    if json_key in checkpoint:
        if checkpoint[json_key]["updated_at"] != updated_at:
            update_flag = True

    if not any(file.display_name.lower().endswith(pf) for pf in config.ALLOW_FILE_EXTENSION):
        return (False, "filtered by extension", update_flag)

    if file.size >= config.MAX_SINGLE_FILE_SIZE * 1024 * 1024:
        return (False, f"size limit exceed (>= {config.MAX_SINGLE_FILE_SIZE} MB)", update_flag)

    if json_key in checkpoint and config.NEVER_DOWNLOAD_AGAIN:
        return (False, "file has been downloaded before (config.NEVER_DOWNLOAD_AGAIN)", update_flag)

    if path_exist and config.NEVER_OVERWRITE_FILE:
        return (False, "file exists and will not be overwritten (config.NEVER_OVERWRITE_FILE)", update_flag)

    if json_key in checkpoint:
        if "id" in checkpoint[json_key] and "session" in checkpoint[json_key]:
            if checkpoint[json_key]["id"] != file.id:
                if checkpoint[json_key]["session"] == config.SESSION:
                    print(
                        f"    {Fore.YELLOW}Duplicated files detected. ({file.display_name}){Style.RESET_ALL}")
                    return (False, "files with duplicated path", update_flag)
        checkpoint[json_key]["session"] = config.SESSION

    if path_exist and json_key in checkpoint:
        if checkpoint[json_key]["updated_at"] == updated_at:
            return (False, "already downloaded and is latest version", update_flag)

    return (True, "", update_flag)


def replaceIlligalChar(filename, regex=path_regex):
    return re.sub(regex, config.REPLACE_ILLEGAL_CHAR_WITH, filename)


def parse_course_folder_name(course: canvasapi.canvas.Course) -> str:
    if course.id in config.CUSTOM_NAME_OVERRIDE:
        return replaceIlligalChar(config.CUSTOM_NAME_OVERRIDE[course.id])

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
        r"{NAME}": replaceIlligalChar(course_name.replace("（", "(").replace("）", ")"), file_regex),
        r"{NICKNAME}": replaceIlligalChar(course_nickname.replace("（", "(").replace("）", ")"), file_regex),
        r"{COURSE_CODE}": course.course_code
    }

    folderName = config.NAME_TEMPLATE
    for old, new in template_map.items():
        folderName = folderName.replace(old, new)
    folderName = replaceIlligalChar(folderName)
    return folderName


def resolve_video(page: canvasapi.page.PageRevision):
    title = page.title
    if config.VERBOSE_MODE:
        print(f"    {Fore.GREEN}Resolving page {title}{Style.RESET_ALL}")
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
        for i in range(len(links)):
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
    pass


def check_filelist_cache(course: canvasapi.canvas.Course):
    if course.id not in course_files:
        if 'files' in [tab.id for tab in course.get_tabs()]:
            course_files[course.id] = {
                file.id: file for file in course.get_files()}
        else:
            course_files[course.id] = None
    return course_files[course.id] != None


def get_files_in_course(course: canvasapi.canvas.Course):
    if check_filelist_cache(course):
        for file in course_files[course.id].values():
            yield file
    else:
        raise canvasapi.exceptions.ResourceDoesNotExist(
            "File tab is not supported.")


def get_file_in_course(course: canvasapi.canvas.Course, file_id: str):
    if check_filelist_cache(course):
        return course_files[course.id][file_id]
    else:
        return course.get_file(file_id)


def organize_by_file(course: canvasapi.canvas.Course) -> (canvasapi.canvas.File, str):
    folders = {folder.id: folder.full_name for folder in course.get_folders()}
    for file in get_files_in_course(course):
        folder = folders[file.folder_id] + "/"
        folder = folder.lstrip("course files/")
        yield (file, folder)


def organize_by_module(course: canvasapi.canvas.Course) -> (canvasapi.canvas.File, str):
    for module in course.get_modules():
        module_item_count = module.items_count
        module_item_position = module.position-1  # it begins with 1
        module_name = config.MODULE_FOLDER_TEMPLATE
        module_name = module_name.replace("{NAME}", re.sub(
            file_regex, "_", module.name.replace("（", "(").replace("）", ")")))
        if config.CONSOLIDATE_MODULE_SPACE:
            module_name = " ".join(module_name.split())
        module_name = module_name.replace(
            "{IDX}", str(module_item_position + config.MODULE_FOLDER_IDX_BEGIN_WITH))
        print(
            f"    Module {Fore.CYAN}{module_name} ({module_item_count} items){Style.RESET_ALL}")
        for item in module.get_module_items():
            if item.type == "File":
                yield get_file_in_course(course, item.content_id), module_name
            elif item.type in ["Page", "Discussion", "Assignment"]:
                page_url = item.html_url
            elif item.type == "ExternalUrl":
                page_url = item.external_url
            elif item.type == "SubHeader":
                pass
            else:
                if config.VERBOSE_MODE:
                    print(
                        f"    {Fore.YELLOW}Unsupported item type: {item.type}{Style.RESET_ALL}")


def organize_by_module_with_file(course: canvasapi.canvas.Course) -> (canvasapi.canvas.File, str):
    module_files_id = []
    for (file, path) in organize_by_module(course):
        yield (file, path)
        module_files_id.append(file.id)
    print(f"    {Fore.CYAN}File not in module{Style.RESET_ALL}")
    for (file, path) in organize_by_file(course):
        if not(file.id in module_files_id):
            yield (file, os.path.join("unmoduled", path))


def get_file_list(course: canvasapi.canvas.Course, organize_by: str) -> (canvasapi.canvas.File, str):
    if organize_by == "module_with_file":
        for (file, path) in organize_by_module_with_file(course):
            yield (file, path)
        return
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
                f"    {Fore.RED}unsupported organize mode: {config.ORGANIZE_BY}{Style.RESET_ALL}")
        return
    except canvasapi.exceptions.ResourceDoesNotExist:
        pass
    except canvasapi.exceptions.Unauthorized:
        pass
    except Exception:
        raise
    print(f"    {Fore.YELLOW}{organize_by} mode not available, falling back to {another_mode} mode{Style.RESET_ALL}")
    for (file, path) in get_file_list(course, another_mode):
        yield (file, path)


def process_course(course: canvasapi.canvas.Course):
    name = parse_course_folder_name(course)
    print(
        f"Course {Fore.CYAN}{course.course_code} (ID: {course.id}){Style.RESET_ALL}")

    reasons_of_not_download = {}

    organize_mode = config.ORGANIZE_BY

    if course.id in config.CUSTOM_ORGANIZE:
        organize_mode = config.CUSTOM_ORGANIZE[course.id]

    for (file, folder) in get_file_list(course, organize_mode):
        directory = os.path.join(config.BASE_DIR, name, folder)
        filename = replaceIlligalChar(file.display_name, file_regex)
        path = os.path.join(directory, filename)

        json_key = f"{name}/{folder}{file}"

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
                              path, verbose=config.VERBOSE_MODE)
                if config.OVERRIDE_FILE_TIME:
                    c_time = datetime.strptime(
                        file.created_at, '%Y-%m-%dT%H:%M:%S%z').timestamp()
                    m_time = datetime.strptime(
                        file.updated_at, '%Y-%m-%dT%H:%M:%S%z').timestamp()
                    a_time = time.time()
                    if is_windows():
                        setctime(path, c_time)
                    os.utime(path, (a_time, m_time))
                checkpoint[json_key] = {
                    "updated_at": file.updated_at,
                    "id": file.id,
                    "session": config.SESSION
                }
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
        do_checkpoint()

    if config.ENABLE_VIDEO:
        for page in course.get_pages():
            for (result, msg) in resolve_video(page.show_latest_revision()):
                if result == True:
                    filename = msg.split("/")[-2]
                    json_key = f"{name}/{page.title}-{filename}"
                    path = os.path.join(
                        config.BASE_DIR, name, f"{page.title}-{filename}")
                    path = replaceIlligalChar(path)
                    if not Path(path).exists():
                        quoted_path = shlex.quote(path)
                        ffmpeg_commands.append(
                            f"{config.FFMPEG_PATH} -i '{msg}' -c copy -bsf:a aac_adtstoasc {quoted_path}")
                else:
                    prev_cnt = reasons_of_not_download.get(msg, 0)
                    reasons_of_not_download[msg] = prev_cnt + 1

    for (reason, cnt) in reasons_of_not_download.items():
        print(f"    {Style.DIM}{cnt} files ignored: {reason}{Style.RESET_ALL}")


if __name__ == '__main__':
    main()
