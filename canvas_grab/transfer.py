import sys
from pathlib import Path
from retrying import retry
from termcolor import colored

from .download_file import download_file as df
from .utils import apply_datetime_attr

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
        print('  ' + colored(f'Retrying ({e})...', 'red'))
        raise


class Transfer(object):
    def transfer(self, base_path, plans):
        for key, plan in plans:
            path = f'{base_path}/{key}'
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            try:
                Path(path).unlink()
            except Exception as e:
                pass
            if plan.url == '':
                print("  " + colored(f'{key} not available yet', 'yellow'))
                continue
            download_file(plan.url, plan.name, path, plan.size)
            apply_datetime_attr(path, plan.created_at, plan.modified_at)