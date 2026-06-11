# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

个人编程练习项目，包含贪吃蛇小游戏、图片生成工具，以及一系列 AI Agent Skills 和 CLI 工具。

## 运行方式

```bash
# 贪吃蛇游戏
python snake_game.py

# 免费图片生成（需 ModelScope API Key，已配好）
MODELSCOPE_API_KEY=$(grep MODELSCOPE_API_KEY ~/.claude/.env | cut -d= -f2) \
  python .agents/skills/zimage-skill/generate.py "你的提示词" output.jpg
```

依赖 Python 3 标准库（tkinter），tkinter 缺失时：
- **Windows**: 重新安装 Python 并勾选 "tcl/tk and IDLE" 选项
- **Linux**: `sudo apt install python3-tk`
- **macOS**: 使用官方 Python 安装器（Homebrew 版本可能不含 tkinter）

## 对话规则

- **每次任务结束后**，必须报告当前上下文窗口的占用比例。格式：`上下文占用: 25.3k / 1M (2.5%)`

## 代码结构

- `snake_game.py` — 高级版贪吃蛇，单文件 tkinter 应用。`SnakeGame` 类封装 UI 面板、画布渲染、游戏逻辑。特性：蛇身渐变色彩、食物脉冲动画、粒子爆发特效、得分弹窗动画、蛇眼随方向转动、卡片式游戏结束面板。顶部面板支持速度/蛇身颜色/食物颜色/背景/生命数调节
- `gen_image.py` — 简单图片生成脚本（Pollinations.ai 方案，已废弃不可用）

## 技能与工具生态

### Agent Skills
项目使用 `skills-lock.json` 锁定已安装的 Agent Skills，重装时执行：
```bash
npx skills experimental_install
```

已安装技能（`.agents/skills/`）：
- **opencli-browser** — 驱动 Chrome 浏览器执行网页操作
- **opencli-adapter-author** — 为任意网站编写 OpenCLI 适配器
- **opencli-autofix** — 自动修复损坏的适配器
- **opencli-usage** — OpenCLI 使用指南
- **opencli-browser-sitemap** — 网站结构图谱导航
- **smart-search** — 基于 OpenCLI 的智能搜索路由器
- **zimage-skill** — 阿里 Z-Image-Turbo 免费生图（每天 2000 次），API Key 存于 `~/.claude/.env`
- **art** — Google Gemini 图片生成（16 种工作流，需付费 API）
- **find-skills** — 从 skills.sh 搜索和安装技能（已复制到全局 `~/.claude/skills/`）
- **skill-creator** — 创建和管理自定义技能（已复制到全局 `~/.claude/skills/`）

### 全局 CLI 工具
- **OpenCLI** (`npm install -g @jackwener/opencli`) — 将任意网站转为 CLI，支持 AI Agent 驱动 Chrome 浏览器。需配合 Chrome 浏览器扩展使用。配置了小红书、B站、知乎、Reddit、HackerNews 等数十个站点。首次使用需 `opencli <site> login` 登录

### 插件
- **frontend-design** — Anthropic 官方前端设计技能（`frontend-design@claude-code-plugins`）

## 远程仓库

- **GitHub**: `git@github.com:Huangqingan/test.git`（master 分支）
- 无需 PR 流程，直接 push

## API 密钥

`~/.claude/.env` 中存储：
- `GOOGLE_API_KEY` — Google Gemini API（图片生成需付费）
- `MODELSCOPE_API_KEY` — 阿里 ModelScope（免费生图，每天 2000 次）

## 自定义 Agent

`.claude/agents/` 下定义了两个自定义 Agent：
- `ui-审美把关.md` — UI 设计审查
- `code-quality-gatekeeper.md` — 代码质量把关
