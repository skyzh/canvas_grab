#!/usr/bin/env python 
__author__  = "github.com/ruxi"
__license__ = "MIT"
import requests 
import tqdm     # progress bar
import os.path
def download_file(url, desc, filename=False, verbose=False):
    """
    Download file with progressbar
    
    Usage:
        download_file('http://web4host.net/5MB.zip')  
    """
    if not filename:
        local_filename = os.path.join(".",url.split('/')[-1])
    else:
        local_filename = filename
    r = requests.get(url, stream=True)
    file_size = int(r.headers['Content-Length'])
    chunk = 1
    chunk_size=1024
    num_bars = int(file_size / chunk_size)
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
                                    , dynamic_ncols = True
                                ):
            fp.write(chunk)
    return
