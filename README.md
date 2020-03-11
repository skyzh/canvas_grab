# canvas-grab

Grab all files on Canvas LMS to local directory.

Download latest release
[here](https://github.com/skyzh/canvas_grab/archive/master.zip).

You may download prebuilt binary [here](https://github.com/skyzh/canvas_grab/releases).

Please offer an API key when running this program for the first time.
You may obtain API key in Canvas settings. 

## Configuration

You may set the following options in `config.toml`.
You can edit `config.toml` with your favourite text editor.

## Features

- **All CanvasLMS-based sites supported** Just specify Canvas endpoint in config.
- **Auto Checkpoint** A file will only be downloaded once. And the program will update the file if there's any update on Canvas.
- **Extension and Size Filter** You can specify maximum allowed file size. You may also filter files by extension.
- **Auto Retrying** If your network connection is not stable, the program will automatically retry downloading. You may interrupt at any time.
- **Auto Sorting** All files will be saved to their corresponding folders on Canvas. You may set folder name with placeholders like `{CANVAS_ID}-{NAME}`.

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


The program will automatically checkpoint your downloads. Therefore
it will not grab downloaded files, and will check if there's any update
on a file. Checkpoint is done after any new file downloaded.
You may interrupt at any time.

To re-download all files, remove `CHECKPOINT_FILE` or `BASE_DIR`.

## Common Issues

**上海交通大学用户**请在[此页面](https://oc.sjtu.edu.cn/profile/settings)内通过**创建新访问许可证**按钮生成访问令牌。

## Screenshot

![image](https://user-images.githubusercontent.com/4198311/76405828-b71b1780-63c3-11ea-9c9e-59d0fcaf1de1.png)
