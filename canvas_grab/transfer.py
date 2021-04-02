import sys
import os
from pathlib import Path
from retrying import retry
from termcolor import colored

from .download_file import download_file as df
from .utils import apply_datetime_attr, truncate_name
from .snapshot import SnapshotLink, SnapshotFile

TIMEOUT = 3
ATTEMPT = 3


def need_retrying(exception):
    return not isinstance(exception, KeyboardInterrupt)


@retry(retry_on_exception=need_retrying, stop_max_attempt_number=ATTEMPT, wait_fixed=1000)
def download_file(url, desc, filename, file_size, verbose=False):
    try:
        sys.stderr.flush()
        yield from df(url, desc, filename, file_size, verbose, req_timeout=TIMEOUT)
        sys.stderr.flush()
    except KeyboardInterrupt:
        sys.stderr.flush()
        raise
    except Exception as e:
        sys.stderr.flush()
        print('  ' + colored(f'Retrying ({e})...', 'red'))
        raise


class Transfer(object):
    def create_parent_folder(self, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)

    def transfer(self, base_path, archive_base_path, plans):
        for _ in self.yield_transfer():
            pass

    def sub_transfer_progress(self, of, total, download_progress):
        return 0.2 + (float(of) + download_progress) / total * 0.8

    def yield_transfer(self, base_path, archive_base_path, plans):
        yield (None, '传输文件中...', None)
        for idx, (op, key, plan) in enumerate(plans):
            path = f'{base_path}/{key}'
            archive_path = f'{archive_base_path}/{path}'

            if op == 'add' or op == 'update':
                self.create_parent_folder(path)
                file_obj = Path(path)
                if file_obj.exists():
                    self.create_parent_folder(archive_path)
                    file_obj.rename(archive_path)
                if plan.url == '':
                    print(f'  {colored("? (not available)", "yellow")} {key}')
                    continue
                if isinstance(plan, SnapshotFile):
                    download_file_task = download_file(
                        plan.url, f'({idx+1}/{len(plans)}) ' + truncate_name(plan.name), path, plan.size)
                    for progress in download_file_task:
                        yield (self.sub_transfer_progress(idx, len(plans), progress), None, None)
                    apply_datetime_attr(
                        path, plan.created_at, plan.modified_at)
                elif isinstance(plan, SnapshotLink):
                    Path(path).write_text(plan.content(), encoding='utf-8')
                else:
                    print(colored('Unsupported snapshot type', 'red'))

            if op == 'delete':
                file_obj = Path(path)
                if file_obj.exists():
                    self.create_parent_folder(archive_path)
                    file_obj.rename(archive_path)

            if op == 'add':
                print(f'  {colored("+", "green")} {key}')
                yield (None, None, f'下载 {key}')
            if op == 'update':
                print(f'  {colored("=", "green")} {key}')
                yield (None, None, f'更新 {key}')
            if op == 'delete':
                print(f'  {colored("-", "yellow")} {key}')
                yield (None, None, f'删除 {key}')
            if op == 'ignore':
                print(f'  {colored("? (ignored)", "yellow")} {key}')
                yield (None, None, f'忽略 {key}')
            if op == 'try-remove':
                print(f'  {colored("? (not on remote)", "yellow")} {key}')
                yield (None, None, f'忽略 {key}')

        self.clean_tree(base_path)

    def clean_tree(self, path) -> bool:
        """Remove empty folder recursively.
        Returns True if folder is deleted.
        """
        path = Path(path)
        if not path.is_dir():
            return True
        children = cleaned_children = list(path.glob('*'))
        for child_idx in reversed(range(len(children))):
            if children[child_idx].is_dir() and self.clean_tree(children[child_idx]):
                del cleaned_children[child_idx]
        if not cleaned_children:
            path.rmdir()
            return True
        return False
