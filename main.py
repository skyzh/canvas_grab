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
from utils import is_windows
from version import check_latest_version
import shlex

if is_windows():
    from win32_setctime import setctime

colorama.init()

print("Thank you for using canvas_grab!") 
print(f"If you have any questions, please file an issue at {Fore.BLUE}https://github.com/skyzh/canvas_grab/issues{Style.RESET_ALL}")
print(f"You may review {Fore.GREEN}README.md{Style.RESET_ALL} and {Fore.GREEN}LICENSE{Style.RESET_ALL} shipped with this release")

from config import *

canvas = Canvas(API_URL, API_KEY)

try:
    print(f'{Fore.BLUE}Logging in...{Style.RESET_ALL}')
    print(f"{Fore.GREEN}Logged in to {API_URL} as {canvas.get_current_user()}{Style.RESET_ALL}")
except canvasapi.exceptions.InvalidAccessToken:
    print(f"{Fore.RED}Invalid access token, please check your API_KEY in config file")
    if is_windows():
        # for windows double-click user
        input()
    exit()


def do_download(file) -> (bool, str):
    if not any(file.display_name.lower().endswith(pf) for pf in ALLOW_FILE_EXTENSION):
        return (False, "filtered by extension")
    if file.size >= MAX_SINGLE_FILE_SIZE * 1024 * 1024:
        return (False, f"size limit exceed")
    return (True, "")


checkpoint = {}
os.makedirs(pathlib.Path(CHECKPOINT_FILE).parent, exist_ok=True)
def do_checkpoint():
    with open(CHECKPOINT_FILE, 'w') as file:
        json.dump(checkpoint, file)


try:
    with open(CHECKPOINT_FILE, 'r') as file:
        checkpoint = json.load(file)
except:
    print(f"{Fore.RED}No checkpoint found")

new_files_list = []


def parse_course_folder_name(course: canvasapi.canvas.Course) -> str:
    if course.id in CUSTOM_NAME_OVERRIDE:
        return re.sub(r'[:*?"<>|]', REPLACE_ILLEGAL_CHAR_WITH, CUSTOM_NAME_OVERRIDE[course.id])
    
    r = re.match(
        r"\((?P<semester_id>[0-9\-]+)\)-(?P<sjtu_id>[A-Za-z0-9]+)-(?P<classroom_id>.+)-(?P<name>.+)\Z", course.course_code)
    
    template_map = {
        r"{CANVAS_ID}": str(course.id),
        r"{SJTU_ID}": r["sjtu_id"],
        r"{SEMESTER_ID}": r["semester_id"],
        r"{CLASSROOM_ID}": r["classroom_id"],
        r"{NAME}": re.sub(r'/\\', REPLACE_ILLEGAL_CHAR_WITH, course.name.replace("（", "(").replace("）", ")"))
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
            print(f"    {Fore.RED}This page has no attribute 'body'{Style.RESET_ALL}")
        yield (False, "failed to resolve page")
        return
    links = re.findall(r"\"(https:\/\/vshare.sjtu.edu.cn\/.*?)\"", page.body)
    if len(links) != 0:
        if VERBOSE_MODE:
            print(f"    {Style.DIM}unsupported link: vshare.sjtu.edu.cn{Style.RESET_ALL}")
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
                print(f"    {Fore.RED}Failed to resolve video: {e}{Style.RESET_ALL}")
            yield (False, "failed to resolve video")
            continue
        video_link = re.findall(r"src=\'(.*?.m3u8)\'", video_page)
        if len(video_link) != 1:
            if VERBOSE_MODE:
                print(f"    {Fore.RED}Failed to resolve video: video link {video_link} != 1{Style.RESET_ALL}")
            yield (False, "failed to resolve video")
            continue
        yield (True, video_link[0])
    pass

ffmpeg_commands = []

def process_course(course: canvasapi.canvas.Course):
    name = parse_course_folder_name(course)
    print(f"{Fore.CYAN}Course {course.course_code}{Style.RESET_ALL}")
    folders = {folder.id: folder.full_name for folder in course.get_folders()}
    reasons_of_not_download = {}

    for file in course.get_files():
        folder = folders[file.folder_id] + "/"
        folder = folder.lstrip("course files/")

        directory = os.path.join(BASE_DIR, name, folder)
        path = os.path.join(directory, file.display_name)

        json_key = f"{name}/{folder}{file}"

        d, reason = do_download(file)
        update_flag = False

        if pathlib.Path(path).exists():
            if json_key in checkpoint:
                if checkpoint[json_key]["updated_at"] == file.updated_at:
                    d = False
                    reason = "already downloaded"
                else:
                    update_flag = True
        else:
            if json_key in checkpoint:
                del checkpoint[json_key]
                do_checkpoint()

        if file.url == "":
            d = False
            reason = "file not available"

        if d:
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
        do_checkpoint()

    if ENABLE_VIDEO:
        for page in course.get_pages():
            for (result, msg) in resolve_video(page.show_latest_revision()):
                if result == True:
                    filename = msg.split("/")[-2]
                    json_key = f"{name}/{page.title}-{filename}"
                    path = os.path.join(BASE_DIR, name, f"{page.title}-{filename}")
                    if not Path(path).exists():
                        quoted_path = shlex.quote(path)
                        ffmpeg_commands.append(f"ffmpeg -i '{msg}' -c copy -bsf:a aac_adtstoasc {quoted_path}")
                else:
                    prev_cnt = reasons_of_not_download.get(msg, 0)
                    reasons_of_not_download[msg] = prev_cnt + 1

    for (reason, cnt) in reasons_of_not_download.items():
        print(f"    {Style.DIM}{cnt} files ignored: {reason}{Style.RESET_ALL}")

courses = canvas.get_courses()

try:
    for course in courses:
        if not hasattr(course, "name"):
            if VERBOSE_MODE:
                print(f"{Fore.YELLOW}Course {course.id}: not available{Style.RESET_ALL}")
        elif course.id in IGNOGED_CANVAS_ID:
            print(
                f"{Fore.CYAN}Ignored Course: {course.course_code}{Style.RESET_ALL}")
        else:
            try:
                process_course(course)
            except canvasapi.exceptions.Unauthorized as e:
                print(
                    f"{Fore.RED}An error occoured when processing this course: {e}{Style.RESET_ALL}")
except KeyboardInterrupt:
    pass

do_checkpoint()

if len(new_files_list) == 0:
    print("All files up to date")
else:
    print(f"{Fore.GREEN}{len(new_files_list)} New or Updated files:{Style.RESET_ALL}")
    for f in new_files_list:
        print(f)

if ENABLE_VIDEO:
    print(f"Please run the automatically-generated script {Fore.BLUE}download_video.sh{Style.RESET_ALL} to download all videos.")
    with open("download_video.sh", 'w') as file:
        file.write("\n".join(ffmpeg_commands))

check_latest_version()

print(f"{Fore.GREEN}Done.{Style.RESET_ALL}")

if is_windows():
    # for windows double-click user
    input()
