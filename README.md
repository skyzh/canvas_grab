# canvas-grab

Grab all files on Canvas LMS to local directory.

Download latest release
[here](https://github.com/skyzh/canvas_grab/archive/master.zip).

You may download prebuilt binary [here](https://github.com/skyzh/canvas_grab/releases).

Please offer an API key when running this program for the first time.
You may obtain API key in Canvas settings. 

## Configuration

You may configure canvas_grab in `config.toml`.
You can edit `config.toml` with your favourite text editor.
Refer to `config.example.toml` or `config.example.zh-hans.toml`
for documentation.

## Features

- **All Canvas-based sites are supported** Just specify Canvas endpoint in config.
- **Auto Checkpoint** A file will only be downloaded once. And the program will update the file if there's any update on Canvas.
- **File Type and Size Filter** You can specify maximum allowed file size. You may also filter files by their extensions.
- **Auto Retrying** If your network connection is not stable, the program will automatically retry downloading. You may interrupt at any time.
- **Auto Sorting** All files will be saved to their corresponding folders on Canvas. You may set folder name with placeholders like `{CANVAS_ID}-{NAME}`.

## Get started

First of all, please install Python 3.7+.

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

To re-download all files, remove checkpoint file `.checkpoint` and downloaded files folder `files/`.

## Common Issues

* **Acquire API Token** Access Token can be obtained at "Account - Settings - New Access Token".
* **SJTU Users** 请在[此页面](https://oc.sjtu.edu.cn/profile/settings)内通过**创建新访问许可证**按钮生成访问令牌。
* **Ignored Course** If you see the warning "Ignored Course" if canvas_grab has no access to a course. This is because (1) Course not available (2) Course from previous semesters are hidden.
* **An error occurred** You'll see "An error occoured when processing this course" if there's no file in a course.

## Screenshot

![image](https://user-images.githubusercontent.com/4198311/76405828-b71b1780-63c3-11ea-9c9e-59d0fcaf1de1.png)

## License

MIT
