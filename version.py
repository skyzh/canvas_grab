import requests
from colorama import Fore, Back, Style
from packaging import version as ver_parser

GITHUB_RELEASE_URL = "https://api.github.com/repos/skyzh/canvas_grab/releases/latest"
VERSION = "v1.5.0"


def check_latest_version():
    version_obj = {}
    print()
    try:
        version_obj = requests.get(GITHUB_RELEASE_URL, timeout=3).json()
    except Exception as e:
        print(f"{Fore.RED}Failed to check update.{Style.RESET_ALL} It's normal if you don't have a stable network connection.")
        print(f"You may report the following message to developer: {e}")
        return
    version = version_obj.get("tag_name", "unknown")
    if version == "unknown":
        print("Failed to check update: unknown remote version")
    elif ver_parser.parse(version) > ver_parser.parse(VERSION):
        print(f"You're using version {Fore.GREEN}{VERSION}{Style.RESET_ALL}, "
              f"but the latest release is {Fore.GREEN}{version}{Style.RESET_ALL}.")
        print(f"Please visit {Fore.BLUE}https://github.com/skyzh/canvas_grab/releases{Style.RESET_ALL} "
              "to download the latest version.")
        print()
        print(version_obj.get("body", ""))
        print()
    elif ver_parser.parse(version) < ver_parser.parse(VERSION):
        print("Just checked update. You're using development version of canvas_grab. :)")
    else:
        print("Just checked update. You're using latest version of canvas_grab. :)")
