#!/usr/bin/env python3

# Import the Canvas class
from canvasapi import Canvas
import canvasapi
from colorama import Fore, Back, Style
import json
import pathlib
import os
import time
import sys
import requests
from download_file import download_file
from config import API_URL, API_KEY

# Initialize a new Canvas object
canvas = Canvas(API_URL, API_KEY)

CHECKPOINT_FILE = ".checkpoint"
BASE_DIR = f"{os.getcwd()}/files"

courses = canvas.get_courses()

def do_download(file) -> (bool, str):
    pfs = [".pptx", ".docx", ".ppt", ".pdf", ".doc", ".xlsx"]
    if not any(file.display_name.endswith(pf) for pf in pfs):
        return (False, "only download documents")
    if file.size >= 30 * 1024 * 1024:
        return (False, f"file too big: {file.size // 1024 // 1024} MB")
    return (True, "")

checkpoint = {}

def do_checkpoint():
    with open(CHECKPOINT_FILE, 'w') as file:
        json.dump(checkpoint, file)

try:
    with open(CHECKPOINT_FILE, 'r') as file:
        checkpoint = json.load(file)
except:
    print(f"{Fore.RED} No checkpoint found")

def process_course(course : canvasapi.canvas.Course) -> [(str, str)]:
    name = course.name.replace("（", "(").replace("）", ")")
    print(f"{Fore.CYAN} Course {name}{Style.RESET_ALL}")
    folders = {folder.id: folder.full_name for folder in course.list_folders()}
    for file in course.list_files():
        folder = folders[file.folder_id] + "/"
        if folder == "course files/":
            folder = ""

        directory = f"{BASE_DIR}/{name}/{folder}"
        path = f"{directory}/{file.display_name}"

        json_key = f"{name}/{folder}{file}"

        d, reason = do_download(file)

        if pathlib.Path(path).exists():
            if json_key in checkpoint:
                if checkpoint[json_key]["updated_at"] == file.updated_at:
                    d = False
                    reason = "already downloaded"

        if file.url == "":
            d = False
            reason = "url not available"
        if d:
            print(f"    {Fore.GREEN} Download {file.display_name} ({file.size // 1024 / 1000}MB){Style.RESET_ALL}")
            pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
            try:
                pathlib.Path(path).unlink()
            except:
                pass
            
            time.sleep(1)
            download_file(file.url, path)

            checkpoint[json_key] = { "updated_at": file.updated_at }
        else:
            print(f"    {Style.DIM} Ignore {file.display_name}: {reason} {Style.RESET_ALL}")
        do_checkpoint()

for course in courses:
    if hasattr(course, "name"):
        process_course(course)

do_checkpoint()
print(f"{Fore.CYAN} Done.")
