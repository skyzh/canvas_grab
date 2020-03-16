# canvas-grab

Grab all files on Canvas LMS to local directory.

[中文说明](https://github.com/skyzh/canvas_grab/blob/master/README_zh-hans.md)

## Getting Started

If you have Python installed, download latest release
[here](https://github.com/skyzh/canvas_grab/archive/master.zip),
and follow the steps in "Build and Run from Source"

Otherwise, you may download prebuilt binary [here](https://github.com/skyzh/canvas_grab/releases). Here's a `canvas_grab(.exe)` file.

The program will ask you for an API key when running for the 
first time. You may obtain API key in Canvas settings. If you
want further customization, you may edit `config.toml`. Refer to
Configuration section.

You may interrupt the downloading process at any time. The program will automatically resume from where it stopped.

To re-download all files, remove checkpoint file `.checkpoint` and downloaded files folder `files/`.

## Configuration

You may configure canvas_grab in `config.toml`.
You can edit `config.toml` with your favourite text editor.
Refer to `config.example.toml` or `config.example.zh-hans.toml`
for documentation.

## Features

- **All Canvas-based sites are supported** Just specify Canvas endpoint in config.
- **Auto checkpoint** A file will only be downloaded once. And the program will update the file if there's any update on Canvas.
- **File size and type filter** You can specify maximum allowed file size. You may also filter files by their extensions.
- **Auto retrying** If your network connection is not stable, the program will automatically retry downloading. You may interrupt at any time.
- **Smart sorting** All files will be saved to their corresponding folder on Canvas. Furthermore, you may set course root folder name with placeholders like `{CANVAS_ID}-{NAME}`.
- **Organize by Module or by File** You can set file organization mode in config.
- **Video URL resolution** Currently we support resolve video URL from `v.sjtu.edu.cn`. Install `ffmpeg` and enable this functionality. Note that this is an EXPERIMENTAL functionality. Use at your own risk.

## Build and Run from Source

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

## Common Issues

* **Acquire API token** Access Token can be obtained at "Account - Settings - New Access Token".
* **SJTU users** 请在[此页面](https://oc.sjtu.edu.cn/profile/settings#access_tokens_holder)内通过“创建新访问许可证”按钮生成访问令牌。
* **Ignored course** If you see the warning "Ignored Course", then canvas_grab has no access to a course. This is because (1) Course not available (2) Course from previous semesters are hidden.
* **An error occurred** You'll see "An error occurred when processing this course" if there's no file in a course.
* **File not available** This file might have been included in an unpublished unit. canvas_grab cannot bypass restrictions.
* **No module named 'canvasapi'** You haven't installed the dependencies. Follow steps in "build and run from source" or download prebuilt binaries.
* **Error when checking update** It's normal if you don't have a stable connection to GitHub. You may regularly check updates by visiting this repo.
* **Unsupported Link** canvas_grab only supports resolving URL from `v.sjtu.edu.cn`. `vshare.sjtu.edu.cn` is not supported.
* **Download FFMPEG** Download ffmpeg executable [here](https://www.ffmpeg.org/download.html).
* **Invalid prebuilt binary on macOS** You should allow this application to run in "Preferences - Privacy"
* **Skip a course causing error** edit `config.toml`, add ID into `IGNORED_COURSE`.

## Screenshot

![image](https://user-images.githubusercontent.com/4198311/76405828-b71b1780-63c3-11ea-9c9e-59d0fcaf1de1.png)

## [Contributors](https://github.com/skyzh/canvas_grab/graphs/contributors)

[@skyzh](https://github.com/skyzh), 
[@danyang685](https://github.com/danyang685),
[@BugenZhao](https://github.com/BugenZhao)
[@ElectronicElephant](https://github.com/ElectronicElephant)

## License

MIT

```
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

Which means that we do not shoulder any responsibilities for, included but not limited to:

1. API key leaking
2. Users upload copyright material from website to the Internet
