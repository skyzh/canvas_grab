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
from datetime import datetime, timezone
import sys
import requests
from download_file_ex import download_file
import toml
from sys import exit
WINDOWS = os.name == "nt"
if WINDOWS:
    from win32_setctime import setctime
colorama.init()

if not pathlib.Path("config.toml").exists():
    src = pathlib.Path("config.example.toml")
    if not src.exists():
        if sys._MEIPASS:  # for portable exe created by pyinstaller
            # load config from temporary dirertory
            src = pathlib.Path(os.path.join(
                sys._MEIPASS, "config.example.toml"))
        else:
            print(
                f"{Fore.RED}Config not found, default config not found either{Style.RESET_ALL}")
            if WINDOWS:
                # for windows double-click user
                input()
            exit()
    dst = pathlib.Path("config.toml")
    dst.write_text(src.read_text())
    print(f"{Fore.RED}Config not found, using default config{Style.RESET_ALL}")

config = {}

with open("config.toml") as f:
    config = toml.load(f)

API_URL = config["API"].get("API_URL", "https://oc.sjtu.edu.cn")
API_KEY = config["API"].get("API_KEY", "")
NAME_TEMPLATE = config['COURSE_FOLDER'].get('NAME_TEMPLATE', '{NAME}')
REPLACE_ILLEGAL_CHAR_WITH = config['COURSE_FOLDER'].get(
    'REPLACE_ILLEGAL_CHAR_WITH', '-')
CHECKPOINT_FILE = config["CHECKPOINT"].get(
    "CHECKPOINT_FILE", "files/.checkpoint")
BASE_DIR = config['SYNC'].get('BASE_DIR', 'files')
OVERRIDE_FILE_TIME = config['SYNC'].get('OVERRIDE_FILE_TIME', True)
MAX_SINGLE_FILE_SIZE = config['SYNC'].get('MAX_SINGLE_FILE_SIZE', 100)
ALLOW_FILE_EXTENSION = []
ALLOW_FILE_EXTENSION.extend(config['SYNC'].get('ALLOW_FILE_EXTENSION', []))
for ext_groups in config['SYNC'].get('ALLOW_FILE_EXTENSION_GROUP', []):
    ALLOW_FILE_EXTENSION.extend(config['EXTENSION'].get(ext_groups, []))
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

try:
    print(f"{Fore.BLUE}Logged in to {API_URL} as {canvas.get_current_user()}{Style.RESET_ALL}")
except canvasapi.exceptions.InvalidAccessToken:
    print(f"{Fore.RED}Invalid access token, please check your API_KEY in config file")
    if WINDOWS:
        # for windows double-click user
        input()
    exit()


def do_download(file) -> (bool, str):
    if not any(file.display_name.lower().endswith(pf) for pf in ALLOW_FILE_EXTENSION):
        return (False, f"{Fore.BLACK}{Back.WHITE}filtered by extension")
    if file.size >= MAX_SINGLE_FILE_SIZE * 1024 * 1024:
        return (False, f"{Fore.BLACK}{Back.WHITE}file too big: {file.size // 1024 / 1000} MB")
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
    r = re.match(
        r"\((?P<semester_id>[0-9\-]+)\)-(?P<sjtu_id>[A-Za-z0-9]+)-(?P<classroom_id>.+)-(?P<name>.+)\Z", course.course_code)
    template_map = {
        r"{CANVAS_ID}": str(course.id),
        r"{SJTU_ID}": r["sjtu_id"],
        r"{SEMESTER_ID}": r["semester_id"],
        r"{CLASSROOM_ID}": r["classroom_id"],
        r"{NAME}": course.name.replace("（", "(").replace("）", ")")
    }

    folderName = NAME_TEMPLATE
    for old, new in template_map.items():
        folderName = folderName.replace(old, new)
    name = re.sub(r'[/\\:*?"<>|]', REPLACE_ILLEGAL_CHAR_WITH, folderName)
    return folderName


def process_course(course: canvasapi.canvas.Course) -> [(str, str)]:
    name = parse_course_folder_name(course)
    print(f"{Fore.CYAN}Course {course.course_code}{Style.RESET_ALL}")
    folders = {folder.id: folder.full_name for folder in course.get_folders()}

    for file in course.get_files():
        folder = folders[file.folder_id] + "/"
        if folder.startswith("course files/"):
            folder = folder[len("course files/"):]

        directory = f"{BASE_DIR}/{name}/{folder}"
        path = f"{directory}{file.display_name}"

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
                f"    {Fore.GREEN}{'Update' if update_flag else 'New'} {file.display_name} ({file.size // 1024 / 1000}MB){Style.RESET_ALL}")
            download_file(file.url, "    Downloading", path)
            if OVERRIDE_FILE_TIME:
                c_time = datetime.strptime(
                    file.created_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
                m_time = datetime.strptime(
                    file.updated_at, '%Y-%m-%dT%H:%M:%SZ').replace(tzinfo=timezone.utc).timestamp()
                a_time = time.time()
                if WINDOWS:
                    setctime(path, c_time)
                os.utime(path, (a_time, m_time))
            checkpoint[json_key] = { "updated_at": file.updated_at }
            new_files_list.append(path)
        else:
            print(
                f"    {Style.DIM}Ignore {file.display_name}: {reason}{Style.RESET_ALL}")
        do_checkpoint()


courses = canvas.get_courses()

try:
    for course in courses:
        if hasattr(course, "name"):
            try:
                process_course(course)
            except canvasapi.exceptions.Unauthorized as e:
                print(
                    f"{Fore.RED}An error occoured when processing this course: {e}{Style.RESET_ALL}")
        else:
            print(f"{Fore.YELLOW}Course {course.id}: not available{Style.RESET_ALL}")
except KeyboardInterrupt:
    pass

do_checkpoint()

if len(new_files_list) == 0:
    print("All files up to date")
else:
    print(f"{Fore.GREEN}{len(new_files_list)} New or Updated files:{Style.RESET_ALL}")
    for f in new_files_list:
        print(f)

print(f"{Fore.CYAN}Done.")
