# 2. Code Editor

Although there are many code editors available, the one we will use throughout this course is *Microsoft Visual Studio Code* (**VS Code**).

## Why VS Code

* Free to use. It is built on the open-source *Code - OSS* project (MIT licence); the build we download from Microsoft comes with its own free licence.
* Lightweight and fast.
* Cross-platform (available on Windows, macOS, and Linux).
* A large number of extensions for various programming languages and frameworks.
* Integrated terminal.
* Git integration.
* Debugging support.

## Installation of VS Code

The installation steps for VS Code differ by operating system. Below are the steps for **Windows 10/11**:

1. Open a browser and visit the official VS Code downloads page: [vscode download page](https://code.visualstudio.com/download).
1. Download and install the version for your operating system.
1. During installation, make sure to check the box that says **Add to PATH**.
1. After installation, open a **new** Command Prompt (a window that was already open does not see the updated PATH) and type `code --version` to verify the installation.
1. You should see the installed VS Code version printed in the terminal.
1. If you see an error message, revisit the installation steps and ensure that VS Code is added to PATH.

On macOS the `code` command is not added to PATH automatically: open the Command Palette (`Cmd + Shift + P`) and run *Shell Command: Install 'code' command in PATH*.

### Installation Video Guide

[Windows installation video guide](https://youtu.be/wU7IQLIOwoo)

[macOS installation video guide](https://youtu.be/w0xBQHKjoGo)

## Common Issues

* If you get an error related to the *script execution policy* (PowerShell refusing to run scripts, for example a virtual environment's `Activate.ps1`), refer to this video guide: [script execution policy video](https://youtu.be/c06Uu5yCetc?t=18).
* Changing the default terminal in VS Code: [change default terminal video](https://youtu.be/c06Uu5yCetc?t=71).

## Basic usage of VS Code

1. Open VS Code.
1. Open a folder or create a new file to start coding.
1. Use the integrated terminal by going to `View` > `Terminal` or pressing ``Ctrl + ` ``.
1. Install extensions by going to the Extensions view by clicking on the Extensions icon in the Activity Bar on the side of the window or pressing `Ctrl + Shift + X`.

On macOS use `Cmd` instead of `Ctrl` for `Cmd + Shift + X` (the terminal shortcut is still ``Ctrl + ` ``).

***VS Code tour video guide:*** [vscode tour video](https://youtu.be/yjeHLSrhPao).
