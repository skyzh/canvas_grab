# canvas-grab

Grab all files on Canvas LMS to local directory.

![image](https://user-images.githubusercontent.com/4198311/75742884-0b7e2180-5d4a-11ea-800a-e57bd2fa42ac.png)

Download latest release
[here](https://github.com/skyzh/canvas_grab/archive/master.zip).

You may download prebuilt binary [here](https://github.com/skyzh/canvas_grab/releases).

Please offer an API key in `config.toml` before running this program.
You may obtain API key in Canvas settings. You can edit `config.toml`
with your favourite text editor.

## Configuration

You may set the following options in `config.toml`.

- Specify your Canvas API_KEY
- Custimize the file extension filter
- Custimize the style of course folder name
- Specify the folder for syncing
- ……

## Get started

Please install Python 3.7+ at first.

For macOS or Linux users：

```bash
pip3 install -r requirements.txt
./main.py
```

For Windows users:
```powershell
pip install -r requirements.windows.txt
python main.py
```

To create a portable .exe file on Windows with pyinstaller, run：

```powershell
pyinstaller main.py --hidden-import pkg_resources.py2_warn --add-data 'config.example.toml;.' --onefile
```


The program will automatically checkpoint your downloads. Therefore
it will not grab downloaded files, and will check if there's any update
on a file. Checkpoint is done after any new file downloaded.
You may interrupt at any time.

To re-download all files, remove `CHECKPOINT_FILE` or `BASE_DIR`.

## Common Issues

**上海交通大学用户**请在[此页面](https://oc.sjtu.edu.cn/profile/settings)内通过**创建新访问许可证**按钮生成访问令牌。
