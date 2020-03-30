import os
from pathlib import Path
from colorama import Fore, Back, Style


def is_windows():
    return os.name == "nt"


file_regex = r"[\\\/:\*\?\"<>\|]"


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
