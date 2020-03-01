# canvas-grab

Grab all files on Canvas LSM to local directory.

```bash
pip3 install -r requirements.txt
./main.py
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

The program will automatically checkpoint your downloads, therefore
it will not grab downloaded files, and will check if there's any update
on a file.
