import os.path
import sys
import time
import requests
from tqdm import tqdm
from .utils import is_windows


def current_milli_time():
    return round(time.time() * 1000)


def download_file(url, desc, filename, file_size, verbose=False, req_timeout=(5, None)):
    with requests.get(url, stream=True, timeout=req_timeout) as r:
        r.raise_for_status()
        chunk_size = 1024
        if verbose:
            print("size = %d, url = %s" % (file_size, url))
        download_size = 0

        with open(filename + '.canvas_tmp', 'wb') as fp:
            with tqdm(
                total=file_size, unit='B',
                unit_scale=True,
                unit_divisor=1024,
                desc=desc, bar_format='{l_bar}{bar}{r_bar}', ascii=is_windows(),
                leave=False
            ) as pbar:
                lst_update = current_milli_time()
                for chunk in r.iter_content(chunk_size=chunk_size):
                    fp.write(chunk)
                    download_size += len(chunk)
                    current_time = current_milli_time()
                    if current_time - lst_update > 100:
                        yield float(download_size) / file_size
                        lst_update = current_time
                    pbar.update(len(chunk))
        if download_size != file_size:
            raise Exception(
                f"Incomplete file: expected {file_size}, downloaded {download_size}")
        os.replace(filename + '.canvas_tmp', filename)
    return
