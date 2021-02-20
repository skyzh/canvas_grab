# canvas-grab

Grab all files on Canvas LMS to local directory.

*Less is More.* In canvas_grab v2, we focus on stability and ease of use.
Now you don't have to tweak dozens of configurations. We have a very
simple setup wizard to help you get started!

For legacy version, refer to [legacy](https://github.com/skyzh/canvas_grab/tree/legacy) branch.

## Getting Started

1. Install Python
2. Download https://github.com/skyzh/canvas_grab/archive/master.zip or
   `git clone https://github.com/skyzh/canvas_grab`
3. Run `./canvas_grab.sh` (Linux, macOS) or `.\canvas_grab.ps1` (Windows) in Terminal.
   Please refer to `Build and Run from Source` for more information.
4. Get your API key at Canvas profile and you're ready to go!

You may interrupt the downloading process at any time. The program will automatically resume from where it stopped.

To upgrade, just replace `canvas_grab` with a more recent version.

If you have any questions, feel free to file an issue [here](https://github.com/skyzh/canvas_grab/issues).

## Build and Run from Source

First of all, please install Python 3.8+, and download source code.

We have prepared a simple script to automatically install dependencies and run canvas_grab.

For macOS or Linux users, open a Terminal and run:

```bash
./canvas_grab.sh
```

For Windows users:

1. Right-click Windows icon on taskbar, and select "Run Powershell (Administrator)".
2. Run `Set-ExecutionPolicy Restricted` in Powershell.
3. Open `canvas_grab` source file in file browser, Shift + Right-click on blank area, and select `Run Powershell here`.
4. Now you can start canvas_grab with a simple command:
    ```powershell
    .\canvas_grab.ps1
    ```

## Configure

The setup wizard will automatically create a configuration for you.
You can change `config.toml` to fit your needs. If you need to
re-configure, run `./canvas_grab.sh configure`.

## Common Issues

* **Acquire API token** Access Token can be obtained at "Account - Settings - New Access Token".
* **SJTU users** 请在[此页面](https://oc.sjtu.edu.cn/profile/settings#access_tokens_holder)内通过“创建新访问许可证”按钮生成访问令牌。
* **An error occurred** You'll see "An error occurred when processing this course" if there's no file in a course.
* **File not available** This file might have been included in an unpublished unit. canvas_grab cannot bypass restrictions.
* **No module named 'canvasapi'** You haven't installed the dependencies. Follow steps in "build and run from source" or download prebuilt binaries.
* **Error when checking update** It's normal if you don't have a stable connection to GitHub. You may regularly check updates by visiting this repo.
* **Reserved escape sequence used** please use "/" as the path seperator instead of "\\".
* **Duplicated files detected** There're two files of same name in same folder. You should download it from Canvas yourself.

## Screenshot

![image](https://user-images.githubusercontent.com/4198311/108496621-4673bf00-72e5-11eb-8978-8b8bdd4efea5.png)

## [Contributors](https://github.com/skyzh/canvas_grab/graphs/contributors)

[@skyzh](https://github.com/skyzh), 
[@danyang685](https://github.com/danyang685),
[@BugenZhao](https://github.com/BugenZhao),
[@ElectronicElephant](https://github.com/ElectronicElephant),
[@LuminousXLB](https://github.com/LuminousXLB),
[@squnit](https://github.com/squnit),
[@Kienyew](https://github.com/Kienyew)

## License

MIT

Which means that we do not shoulder any responsibilities for, included but not limited to:

1. API key leaking
2. Users upload copyright material from website to the Internet
