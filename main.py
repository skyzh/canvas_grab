#!/usr/bin/env python3

from canvasapi import Canvas
import canvasapi
import configparser
from colorama import Fore, Back, Style
import colorama
import json
import pathlib
import os
import time
import sys
import requests
from download_file_ex import download_file
import toml
from sys import exit

colorama.init()

if not pathlib.Path("config.toml").exists():
    src = pathlib.Path("config.example.toml")
    dst = pathlib.Path("config.toml")
    dst.write_text(src.read_text())
    print(f"{Fore.RED}Config not found, using default config{Style.RESET_ALL}")

config = {}

with open("config.toml") as f:
    config = toml.load(f)

API_URL = config["API"].get("API_URL", "https://oc.sjtu.edu.cn")
API_KEY = config["API"].get("API_KEY", "")
USE_COURSE_ID = config["COURSE"].get("USE_COURSE_ID", False)
CHECKPOINT_FILE = config["CHECKPOINT"].get("CHECKPOINT_FILE", ".checkpoint")
BASE_DIR = f"{os.getcwd()}/{config['SYNC'].get('BASE_DIR', 'files')}"
MAX_SINGLE_FILE_SIZE = config['SYNC'].get('MAX_SINGLE_FILE_SIZE', 100)
ALLOW_FILE_EXTENSION = []
ALLOW_FILE_EXTENSION.extend(config['SYNC'].get('ALLOW_FILE_EXTENSION', []))
for ext_groups in config['SYNC'].get('ALLOW_FILE_EXTENSION_GROUP', []):
    ALLOW_FILE_EXTENSION.extend(config['EXTENSION'].get(ext_groups, []))
print(f"{Fore.CYAN}Allowed extensions: {' '.join(ALLOW_FILE_EXTENSION)}{Style.RESET_ALL}")
# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

try:
    print(f"{Fore.BLUE}Logged in to {API_URL} as {canvas.get_current_user()}{Style.RESET_ALL}")
except canvasapi.exceptions.InvalidAccessToken:
    print(f"{Fore.RED}Invalid access token, please check your API_KEY in config file")
    if os.name == "nt":
        # for windows double-click user
        input()
    exit()

def do_download(file) -> (bool, str):
    if not any(file.display_name.endswith(pf) for pf in ALLOW_FILE_EXTENSION):
        return (False, f"{Fore.BLACK}{Back.WHITE}filtered by extension")
    if file.size >= MAX_SINGLE_FILE_SIZE * 1024 * 1024:
        return (False, f"{Fore.BLACK}{Back.WHITE}file too big: {file.size // 1024 / 1000} MB")
    return (True, "")

checkpoint = {}

def do_checkpoint():
    with open(CHECKPOINT_FILE, 'w') as file:
        json.dump(checkpoint, file)

try:
    with open(CHECKPOINT_FILE, 'r') as file:
        checkpoint = json.load(file)
except:
    print(f"{Fore.RED}No checkpoint found")

new_files_list = []

def process_course(course : canvasapi.canvas.Course) -> [(str, str)]:
    name = course.name.replace("（", "(").replace("）", ")")
    print(f"{Fore.CYAN}Course {name} {course.course_code}{Style.RESET_ALL}")
    if USE_COURSE_ID:
        name = f"{course.id}-{name}"
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
            print(f"    {Fore.GREEN}{'Update' if update_flag else 'New'} {file.display_name} ({file.size // 1024 / 1000}MB){Style.RESET_ALL}")
            download_file(file.url, "    Downloading", path)

            checkpoint[json_key] = { "updated_at": file.updated_at }
            new_files_list.append(path)
        else:
            print(f"    {Style.DIM}Ignore {file.display_name}: {reason}{Style.RESET_ALL}")
        do_checkpoint()

courses = canvas.get_courses()

try:
    for course in courses:
        if hasattr(course, "name"):
            try:
                process_course(course)
            except canvasapi.exceptions.Unauthorized as e:
                print(f"{Fore.RED}An error occoured when processing this course: {e}{Style.RESET_ALL}")
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
