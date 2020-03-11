from colorama import Fore, Back, Style
import pathlib
from pathlib import Path
import toml
import sys
import os
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
    config = {}
    if not Path(CONFIG_FILE).exists():
        print(f"{Fore.RED}Config not found, using default config. You may revisit 'config.toml' if you want to customize.{Style.RESET_ALL}")
        create_default_config()
    with open(CONFIG_FILE, encoding="utf8") as f:
        config = toml.load(f)

    if config["API"].get("API_KEY") == "PASTE YOUR API_KEY HERE":
        print(f"{Fore.BLUE}Welcome! First of all, you should paste your API_KEY here. It can be generated on your Canvas settings page (https://oc.sjtu.edu.cn/profile/settings).\n{Fore.GREEN}API_KEY:{Fore.MAGENTA}", end="")
        api_key = input().strip()
        if len(api_key) == 64:  # the only reasonable length for a valid API_KEY
            # No user will paste a dummy 64 length string here
            config["API"]["API_KEY"] = api_key
            config_file = Path(CONFIG_FILE)
            new_config_content = config_file.read_text(
                encoding="utf8").replace("PASTE YOUR API_KEY HERE", api_key)
            config_file.write_text(new_config_content)

    return config


config = load_config()

VERBOSE_MODE = config["SYNC"].get("VERBOSE", False)
API_URL = config["API"]["API_URL"]
API_KEY = config["API"]["API_KEY"]
NAME_TEMPLATE = config["COURSE_FOLDER"]["NAME_TEMPLATE"]
REPLACE_ILLEGAL_CHAR_WITH = config["COURSE_FOLDER"]["REPLACE_ILLEGAL_CHAR_WITH"]
CUSTOM_NAME_OVERRIDE = {int(i["CANVAS_ID"]): str(i["FOLDER_NAME"])
                        for i in config["COURSE_FOLDER"].get("CUSTOM_NAME", [])}
IGNOGED_CANVAS_ID = config["COURSE_FOLDER"].get("IGNOGED_CANVAS_ID", [])
CHECKPOINT_FILE = config["CHECKPOINT"]["CHECKPOINT_FILE"]
BASE_DIR = config["SYNC"]["BASE_DIR"]
OVERRIDE_FILE_TIME = config["SYNC"]["OVERRIDE_FILE_TIME"]
MAX_SINGLE_FILE_SIZE = config["SYNC"]["MAX_SINGLE_FILE_SIZE"]
ALLOW_FILE_EXTENSION = []
ALLOW_FILE_EXTENSION.extend(config["SYNC"]["ALLOW_FILE_EXTENSION"])

for ext_groups in config["SYNC"]["ALLOW_FILE_EXTENSION_GROUP"]:
    ALLOW_FILE_EXTENSION.extend(config["EXTENSION"].get(ext_groups, []))
