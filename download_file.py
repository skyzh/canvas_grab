#!/usr/bin/env python
__author__ = "github.com/ruxi"
__license__ = "MIT"
from utils import is_windows
import os.path
import tqdm     # progress bar
import requests
import sys
import time


def download_file(url, desc, filename=False, verbose=False, req_timeout=(5, None)):
    """
    Download file with progressbar

    Usage:
        download_file('http://web4host.net/5MB.zip')  
    """
    if not filename:
        local_filename = os.path.join(".", url.split('/')[-1])
    else:
        local_filename = filename
    with requests.get(url, stream=True, timeout=req_timeout) as r:
        r.raise_for_status()
        file_size = int(r.headers.get('Content-Length', 0))
        chunk = 1
        chunk_size = 1024
        num_bars = int(file_size / chunk_size) + 1
        if verbose:
            print("size = %d, url = %s" % (file_size, url))
        download_size = 0

        with open(local_filename+'.canvas_tmp', 'wb') as fp:
            with tqdm.tqdm(
                r.iter_content(chunk_size=chunk_size),
                total=num_bars, unit='KB',
                desc=desc, bar_format='{l_bar}{bar}{r_bar}', ascii=is_windows()
            ) as pbar:
                for chunk in pbar:
                    fp.write(chunk)
                    download_size += len(chunk)
        if file_size != 0 and download_size != file_size:
            raise Exception("File download not complete")
        os.replace(local_filename+'.canvas_tmp', local_filename)
    return
