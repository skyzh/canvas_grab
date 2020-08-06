import math
import os
import pathlib
import sys
import time
from pathlib import Path

import toml
from colorama import Back, Fore, Style

from utils import is_windows

CONFIG_FILE = "config.toml"
CONFIG_EXAMPLE = "config.example.toml"


def create_default_config():
    if not Path(CONFIG_FILE).exists():
        src = Path(CONFIG_EXAMPLE)
        if not src.exists():
            if sys._MEIPASS:  # for portable exe created by pyinstaller
                # load config from temporary dirertory
                src = Path(sys._MEIPASS) / CONFIG_EXAMPLE
            else:
                print(
                    f"{Fore.RED}Config not found, default config not found either{Style.RESET_ALL}")
                if is_windows():
                    # for windows double-click user
                    input()
                exit()
        dst = Path(CONFIG_FILE)
        dst.write_bytes(src.read_bytes())


def load_config():
    if not Path(CONFIG_FILE).exists():
        print(f"{Fore.RED}Config not found, using default config. You may revisit 'config.toml' if you want to customize.{Style.RESET_ALL}")
        create_default_config()
    with open(CONFIG_FILE, encoding="utf8") as f:
        config = toml.load(f)

    if config["API"].get("API_KEY") == "PASTE YOUR API_KEY HERE":
        print(f"{Fore.BLUE}Welcome! First of all, you should paste your API_KEY here. It can be generated on your Canvas settings page (https://oc.sjtu.edu.cn/profile/settings).\n{Fore.GREEN}API_KEY: {Fore.MAGENTA}", end="")
        api_key = input().strip()
        while len(api_key) != 64:
            print(
                f"{Fore.RED}API KEY length NOT match. Please re-enter.\n{Fore.GREEN}API_KEY: {Fore.MAGENTA}", end="")
            api_key = input().strip()
        if len(api_key) == 64:  # the only reasonable length for a valid API_KEY
            # No user will paste a dummy 64 length string here
            # Otherwise they'll be warned when being logged in
            config["API"]["API_KEY"] = api_key
            config_file = Path(CONFIG_FILE)
            new_config_content = config_file.read_text(
                encoding="utf8").replace("PASTE YOUR API_KEY HERE", api_key)
            config_file.write_text(new_config_content, encoding='utf8')

        print(
            f"{Style.RESET_ALL}Please MAKE SURE that you've reviewed the LICENSE. Refer to {Fore.BLUE}https://github.com/skyzh/canvas_grab/issues/29{Style.RESET_ALL} for more explanation.")
        print(
            f"{Fore.BLUE}I've been acknowledged that I should NEVER publish copyright materials online.{Style.RESET_ALL}")
        print("Press [Enter] to continue")
        input()

    return config


class Config:
    def __init__(self):
        pass

    def load_config(self):
        config = load_config()

        self.VERBOSE_MODE = config["SYNC"].get("VERBOSE", False)
        self.API_URL = config["API"]["API_URL"]
        self.API_KEY = config["API"]["API_KEY"]
        self.NAME_TEMPLATE = config["COURSE_FOLDER"]["NAME_TEMPLATE"]
        self.MODULE_FOLDER_TEMPLATE = config["COURSE_FOLDER"].get("MODULE_FOLDER_TEMPLATE", "{IDX} {NAME}")
        self.MODULE_FOLDER_IDX_BEGIN_WITH = config["COURSE_FOLDER"].get("MODULE_FOLDER_IDX_BEGIN_WITH", 0)
        self.CONSOLIDATE_MODULE_SPACE = config["COURSE_FOLDER"].get("CONSOLIDATE_MODULE_SPACE", False)
        self.REPLACE_ILLEGAL_CHAR_WITH = config["COURSE_FOLDER"]["REPLACE_ILLEGAL_CHAR_WITH"]
        self.CUSTOM_NAME_OVERRIDE = {
            int(i["CANVAS_ID"]): str(i["FOLDER_NAME"])
            for i in config["COURSE_FOLDER"].get("CUSTOM_NAME", [])
        }
        self.CUSTOM_ORGANIZE = {
            int(i["CANVAS_ID"]): str(i["ORGANIZE_BY"])
            for i in config["COURSE_FOLDER"].get("ORGANIZE_BY", [])
        }
        self.IGNORED_CANVAS_ID = config["COURSE_FOLDER"].get("IGNORED_CANVAS_ID", [])
        self.CHECKPOINT_FILE = config["CHECKPOINT"]["CHECKPOINT_FILE"]
        self.BASE_DIR = config["SYNC"]["BASE_DIR"]
        self.OVERRIDE_FILE_TIME = config["SYNC"]["OVERRIDE_FILE_TIME"]
        self.MAX_SINGLE_FILE_SIZE = config["SYNC"]["MAX_SINGLE_FILE_SIZE"]
        self.ALLOW_FILE_EXTENSION = []
        self.ALLOW_FILE_EXTENSION.extend(config["SYNC"]["ALLOW_FILE_EXTENSION"])
        self.ENABLE_VIDEO = config["SYNC"].get("ENABLE_VIDEO", False)
        self.ENABLE_LINK = config["SYNC"].get("ENABLE_LINK", False)
        self.FFMPEG_PATH = config["SYNC"].get("FFMPEG_PATH", "ffmpeg")
        self.ORGANIZE_BY = config["SYNC"].get("ORGANIZE_BY", "file")
        self.NEVER_OVERWRITE_FILE = config["SYNC"].get("NEVER_OVERWRITE_FILE", False)
        self.NEVER_DOWNLOAD_AGAIN = config["SYNC"].get("NEVER_DOWNLOAD_AGAIN", False)
        self.SCAN_STALE_FILE = config["SYNC"].get("SCAN_STALE_FILE", False)
        self.SESSION = math.floor(time.time())
        self.ALLOW_VERSION_CHECK = config["SYNC"].get("ALLOW_VERSION_CHECK", True)
        self.WHITELIST_CANVAS_ID = config["COURSE_FOLDER"].get("WHITELIST_CANVAS_ID", [])

        for ext_groups in config["SYNC"]["ALLOW_FILE_EXTENSION_GROUP"]:
            self.ALLOW_FILE_EXTENSION.extend(config["EXTENSION"].get(ext_groups, []))
