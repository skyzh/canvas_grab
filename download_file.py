#!/usr/bin/env python 
__author__  = "github.com/ruxi"
__license__ = "MIT"
import requests 
import tqdm     # progress bar
import os.path
from utils import is_windows

def download_file(url, desc, filename=False, verbose=False, req_timeout=(5, None)):
    """
    Download file with progressbar
    
    Usage:
        download_file('http://web4host.net/5MB.zip')  
    """
    if not filename:
        local_filename = os.path.join(".",url.split('/')[-1])
    else:
        local_filename = filename
    r = requests.get(url, stream=True, timeout=req_timeout)
    file_size = int(r.headers.get('Content-Length', 0))
    chunk = 1
    chunk_size=1024
    num_bars = int(file_size / chunk_size) + 1
    if verbose:
        print(dict(file_size=file_size))
        print(dict(num_bars=num_bars))

    with open(local_filename, 'wb') as fp:
        for chunk in tqdm.tqdm(
                                    r.iter_content(chunk_size=chunk_size)
                                    , total= num_bars
                                    , unit = 'KB'
                                    , desc = desc
                                    , bar_format = '{l_bar}{bar}{r_bar}'
                                    , ascii = is_windows()
                                ):
            fp.write(chunk)
    return
