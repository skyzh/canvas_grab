import os
from pathlib import Path
import time
from datetime import datetime

from colorama import Back, Fore, Style


def is_windows():
    return os.name == "nt"


if is_windows():
    from win32_setctime import setctime

file_regex = r"[\t\\\/:\*\?\"<>\|]"
path_regex = r"[\t:*?\"<>|]"


def remove_empty_dir(base: Path) -> bool:
    is_empty = True
    hidden_file = False
    for file in base.iterdir():
        if file.is_dir():
            is_empty = remove_empty_dir(file) and is_empty
        else:
            if file.name == ".DS_Store":
                hidden_file = True
            else:
                is_empty = False
    if is_empty:
        if hidden_file:
            (base / ".DS_Store").unlink()
        print(f"    {str(base)}")
        base.rmdir()
    return is_empty


def apply_datetime_attr(path, created_at: str, updated_at: str):
    c_time = datetime.strptime(
        created_at, r'%Y-%m-%dT%H:%M:%S%z').timestamp()
    m_time = datetime.strptime(
        updated_at, r'%Y-%m-%dT%H:%M:%S%z').timestamp()
    a_time = time.time()
    if is_windows():
        setctime(path, c_time)
    os.utime(path, (a_time, m_time))
