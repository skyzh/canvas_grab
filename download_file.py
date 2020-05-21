#!/usr/bin/env python
__author__ = "github.com/ruxi"
__license__ = "MIT"
import os.path
import sys
import time

import requests
import tqdm  # progress bar

from utils import is_windows


def download_file(url, desc, filename, file_size, verbose=False, req_timeout=(5, None)):
    """
    Download file with progressbar

    Usage:
        download_file('http://web4host.net/5MB.zip')
    """
    with requests.get(url, stream=True, timeout=req_timeout) as r:
        r.raise_for_status()
        chunk_size = 1024
        num_bars = int(file_size / chunk_size) + 1
        if verbose:
            print("size = %d, url = %s" % (file_size, url))
        download_size = 0

        with open(filename + '.canvas_tmp', 'wb') as fp:
            with tqdm.tqdm(
                r.iter_content(chunk_size=chunk_size),
                total=num_bars, unit='KB',
                desc=desc, bar_format='{l_bar}{bar}{r_bar}', ascii=is_windows()
            ) as pbar:
                for chunk in pbar:
                    fp.write(chunk)
                    download_size += len(chunk)
        if download_size != file_size:
            raise Exception(
                f"Incomplete file: expected {file_size}, downloaded {download_size}")
        os.replace(filename + '.canvas_tmp', filename)
    return
