# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

个人 Python 练习项目，目前包含一个贪吃蛇小游戏。

## 运行方式

```bash
python snake_game.py
```

依赖 Python 3 标准库（tkinter），无需额外安装包。tkinter 通常随 Python 一起安装，如果缺失：

- **Windows**: 重新安装 Python 并勾选 "tcl/tk and IDLE" 选项
- **Linux**: `sudo apt install python3-tk`
- **macOS**: 使用官方 Python 安装器（Homebrew 版本可能不含 tkinter）

## 代码结构

- `snake_game.py` — 贪吃蛇游戏，单文件 tkinter 应用。`SnakeGame` 类封装了 UI 面板（设置面板 + 游戏画布）和游戏逻辑（移动、碰撞检测、得分）。游戏通过 `root.after()` 实现定时循环。顶部设置面板支持调节速度、蛇身颜色方案和食物颜色。
