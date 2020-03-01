# canvas-grab

Grab all files on Canvas LMS to local directory. Download latest release
[here](https://github.com/skyzh/canvas_grab/archive/master.zip).

```bash
pip3 install -r requirements.txt
./main.py
```

For Windows users:
```bash
pip install -r requirements.txt
python main.py
```

Please offer an API key in `config.py` before running this program.
You may obtain API key in Canvas settings. `config.py` should contain
the following content.

```python
# Canvas API URL
API_URL = "https://oc.sjtu.edu.cn"
# Canvas API key
API_KEY = "balahbalah"
```

The program will automatically checkpoint your downloads. Therefore
it will not grab downloaded files, and will check if there's any update
on a file. Checkpoint is done after any new file downloaded.
You may interrupt at any time.

You may change `do_download` function in `main.py` to filter files.
Currently the filter is set to ignore non-document files and too big files.

To re-download all files, remove `.checkpoint` file and `files` folder.
