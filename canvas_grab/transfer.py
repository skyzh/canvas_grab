import sys
from pathlib import Path
from retrying import retry
from termcolor import colored

from .download_file import download_file as df
from .utils import apply_datetime_attr, truncate_name

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
        for idx, (op, key, plan) in enumerate(plans):
            path = f'{base_path}/{key}'
            if op == 'add' or op == 'update':
                Path(path).parent.mkdir(parents=True, exist_ok=True)
                try:
                    Path(path).unlink()
                except Exception as e:
                    pass
                if plan.url == '':
                    print(f'  {colored("x (not available)", "yellow")} {key}')
                    continue
                download_file(
                    plan.url, f'({idx+1}/{len(plans)}) ' + truncate_name(plan.name), path, plan.size)
                apply_datetime_attr(path, plan.created_at, plan.modified_at)

            if op == 'delete':
                try:
                    Path(path).unlink()
                except Exception as e:
                    print(colored(f'Failed to remove file {path} {e}', 'red'))

            if op == 'add':
                print(f'  {colored("+", "green")} {key}')
            if op == 'update':
                print(f'  {colored("=", "green")} {key}')
            if op == 'delete':
                print(f'  {colored("-", "yellow")} {key}')
            if op == 'ignore':
                print(f'  {colored("x (ignored)", "yellow")} {key}')
