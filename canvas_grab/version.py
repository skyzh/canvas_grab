import requests
from colorama import Back, Fore, Style
from packaging import version as ver_parser
from termcolor import colored

GITHUB_RELEASE_URL = "https://api.github.com/repos/skyzh/canvas_grab/releases/latest"
VERSION = "2.0.1"


def check_latest_version():
    version_obj = {}
    print()
    try:
        version_obj = requests.get(GITHUB_RELEASE_URL, timeout=3).json()
    except Exception as e:
        print(f"{colored('Failed to check update.', 'red')} It's normal if you don't have a stable network connection.")
        print(f"You may report the following message to developer: {e}")
        return
    version = version_obj.get("tag_name", "unknown")
    if version == "unknown":
        print("Failed to check update: unknown remote version")
    elif ver_parser.parse(version) > ver_parser.parse(VERSION):
        print(f"You're using version {colored(VERSION, 'green')}, "
              f"but the latest release is {colored(version, 'green')}.")
        print(f"Please visit {colored('https://github.com/skyzh/canvas_grab/releases', 'blue')} "
              "to download the latest version.")
        print()
        print(version_obj.get("body", ""))
        print()
    elif ver_parser.parse(version) < ver_parser.parse(VERSION):
        print("Just checked update. You're using development version of canvas_grab. :)")
    else:
        print("Just checked update. You're using latest version of canvas_grab. :)")
