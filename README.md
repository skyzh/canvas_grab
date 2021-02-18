# canvas-grab

Grab all files on Canvas LMS to local directory.

This is v2 version of canvas_grab. For legacy version, refer to
[legacy](https://github.com/skyzh/canvas_grab/tree/legacy) branch.
## Getting Started

1. Install Python
2. Download https://github.com/skyzh/canvas_grab/archive/master.zip or `git clone https://github.com/skyzh/canvas_grab`
3. `pip install -r requirements.txt`, and `pip install -r requirements.windows.txt` if using Windows
4. `python main.py` and follow the wizard

See `Build and Run from Source` for more details.

You may interrupt the downloading process at any time. The program will automatically resume from where it stopped.

To upgrade, just replace `canvas_grab` with a more recent version.

If you have any questions, feel free to file an issue [here](https://github.com/skyzh/canvas_grab/issues).

## Build and Run from Source

First of all, please install Python 3.8+, and download source code.

For macOS or Linux users：

```bash
pip3 install -r requirements.txt
./main.py
```

For Windows users:
```powershell
pip install -r requirements.txt
pip install -r requirements.windows.txt
python main.py
```

## Common Issues

* **Acquire API token** Access Token can be obtained at "Account - Settings - New Access Token".
* **SJTU users** 请在[此页面](https://oc.sjtu.edu.cn/profile/settings#access_tokens_holder)内通过“创建新访问许可证”按钮生成访问令牌。
* **An error occurred** You'll see "An error occurred when processing this course" if there's no file in a course.
* **File not available** This file might have been included in an unpublished unit. canvas_grab cannot bypass restrictions.
* **No module named 'canvasapi'** You haven't installed the dependencies. Follow steps in "build and run from source" or download prebuilt binaries.
* **Error when checking update** It's normal if you don't have a stable connection to GitHub. You may regularly check updates by visiting this repo.
* **Reserved escape sequence used** please use "/" as the path seperator instead of "\\".
* **Duplicated files detected** There're two files of same name in same folder. You should download it from Canvas yourself.

## [Contributors](https://github.com/skyzh/canvas_grab/graphs/contributors)

[@skyzh](https://github.com/skyzh), 
[@danyang685](https://github.com/danyang685),
[@BugenZhao](https://github.com/BugenZhao),
[@ElectronicElephant](https://github.com/ElectronicElephant),
[@LuminousXLB](https://github.com/LuminousXLB),
[@squnit](https://github.com/squnit)

## License

MIT

Which means that we do not shoulder any responsibilities for, included but not limited to:

1. API key leaking
2. Users upload copyright material from website to the Internet
