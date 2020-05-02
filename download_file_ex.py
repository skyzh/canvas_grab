from download_file import download_file as df
from retrying import retry
from colorama import Fore, Style
from pathlib import Path
import sys

TIMEOUT = 3
ATTEMPT = 3


def need_retrying(exception):
    return not isinstance(exception, KeyboardInterrupt)


@retry(retry_on_exception=need_retrying, stop_max_attempt_number=ATTEMPT, wait_fixed=1000)
def download_file(url, desc, filename, file_size, verbose=False):
    try:
        sys.stderr.flush()
        df(url, desc, filename, file_size, verbose, req_timeout=TIMEOUT)
        sys.stderr.flush()
    except KeyboardInterrupt:
        sys.stderr.flush()
        raise
    except Exception as e:
        sys.stderr.flush()
        print(
            f"    {Fore.RED}Retrying ({e})...{Style.RESET_ALL}")
        raise
