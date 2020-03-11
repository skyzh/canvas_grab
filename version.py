import requests
from colorama import Fore, Back, Style

GITHUB_RELEASE_URL = "https://api.github.com/repos/skyzh/canvas_grab/releases/latest"
VERSION = "v1.3.3"


def check_latest_version():
    version = ""
    try:
        version = requests.get(GITHUB_RELEASE_URL, timeout=3).json()
    except Exception as e:
        print(f"{Fore.RED}Failed to check update: {e}{Style.RESET_ALL}")
        return
    version = version.get("tag_name", "unknown")
    if version != VERSION:
        print(f"You're using version {Fore.GREEN}{VERSION}{Style.RESET_ALL}, "
              f"but the latest release is {Fore.GREEN}{version}{Style.RESET_ALL}.")
        print(f"Please visit {Fore.BLUE}https://github.com/skyzh/canvas_grab{Style.RESET_ALL} "
              "to download the latest version.")
    else:
        print("Just checked update. You're using latest version of canvas_grab. :)")
