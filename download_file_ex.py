from download_file import download_file as df
from retrying import retry
from colorama import Fore, Style
from pathlib import Path

TIMEOUT = 3
ATTEMPT = 5


def need_retrying(exception):
    return not isinstance(exception, KeyboardInterrupt)


@retry(retry_on_exception=need_retrying, stop_max_attempt_number=ATTEMPT, wait_fixed=1000)
def download_file(url, desc, filename, verbose=False):
    try:
        df(url, desc, filename, verbose, req_timeout=TIMEOUT)
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(
            f"    {Fore.RED}Retrying {Path(filename).name} ({e})...{Style.RESET_ALL}")
        raise
