# 个人编程练习项目

一个集合了贪吃蛇小游戏、AI 图片生成、Claude Code 技能生态的个人编程练习仓库。

## 项目内容

### 🐍 贪吃蛇游戏

高级版贪吃蛇，基于 Python tkinter 的桌面小游戏。

```bash
python snake_game.py
```

**视觉特性：**
- 柔和动画风，圆形蛇身拼接，无网格线
- 蛇身从头到尾渐变色彩，段间平滑过渡
- 食物随机 4 种形状（圆形 / 星形 / 菱形 / 心形），分值不同
- 食物脉冲光环 + 吃食物粒子爆发特效
- 得分弹窗动画、蛇眼随方向转动
- 毛玻璃风游戏结束面板

**操作方式：**
| 按键 | 功能 |
|------|------|
| 方向键 / WASD | 移动 |
| 空格 | 暂停 / 继续 |
| R | 重生 / 重新开始 |

**顶部面板可调设置：** 速度、蛇身颜色、背景、生命数（1-10）

**运行要求：** Python 3 + tkinter（标准库自带）。tkinter 缺失时：
- Windows：重新安装 Python 并勾选 "tcl/tk and IDLE"
- Linux：`sudo apt install python3-tk`
- macOS：使用官方 Python 安装器

---

### 🎨 Z-Image 免费生图

基于阿里 ModelScope Z-Image-Turbo，每天免费 2000 次。

```bash
# 需先配置 MODELSCOPE_API_KEY（见下方"环境配置"）
MODELSCOPE_API_KEY=$(grep MODELSCOPE_API_KEY ~/.claude/.env | cut -d= -f2) \
  python .agents/skills/zimage-skill/generate.py "一只金色的猫" cat.jpg
```

---

### 🛠 Claude Code 技能生态

项目集成了多个 Claude Code Agent Skills，位于 `.agents/skills/` 目录：

| 技能 | 功能 |
|------|------|
| opencli-browser | 驱动 Chrome 浏览器执行网页操作 |
| opencli-adapter-author | 为任意网站编写 OpenCLI 适配器 |
| opencli-autofix | 自动修复损坏的适配器 |
| opencli-usage | OpenCLI 使用指南 |
| opencli-browser-sitemap | 网站结构图谱导航 |
| smart-search | 基于 OpenCLI 的智能搜索路由器 |
| zimage-skill | 阿里 Z-Image-Turbo 免费生图（每天 2000 次） |
| art | Google Gemini 图片生成（16 种工作流，需付费） |
| find-skills | 从 skills.sh 搜索和安装技能 |
| skill-creator | 创建和管理自定义技能 |

**重装技能：**
```bash
npx skills experimental_install
```

**插件：** frontend-design（Anthropic 官方前端设计）

---

### 🔧 全局 CLI 工具 — OpenCLI

将任意网站转为命令行接口，支持 AI Agent 驱动 Chrome 浏览器。

```bash
npm install -g @jackwener/opencli
```

配置了小红书、B 站、知乎、Reddit、HackerNews 等数十个站点的适配器。需配合 Chrome 浏览器扩展使用。

```bash
# 查看可用站点
opencli list

# 搜索小红书
opencli xiaohongshu search "广州美食"
```

---

### 🤖 自定义 Agent

`.claude/agents/` 定义了 2 个 Claude Code 自定义 Agent，会在合适的场景自动触发：

| Agent | 触发条件 |
|-------|---------|
| ui-审美把关 | UI 元素被修改时自动审查美观度 |
| code-quality-gatekeeper | 重要代码改动后自动验证质量 |

---

## 环境配置

项目 API 密钥存储在 `~/.claude/.env` 中（不纳入版本控制）：

```ini
GOOGLE_API_KEY=xxx    # Google Gemini API（生图需付费）
MODELSCOPE_API_KEY=xxx # 阿里 ModelScope（免费生图）
```

**获取免费 ModelScope API Key：**
1. 打开 [modelscope.cn](https://modelscope.cn)，注册并绑定阿里云账号
2. 前往 [myaccesstoken](https://modelscope.cn/my/myaccesstoken) 创建 SDK 令牌
3. 将 Token 写入 `~/.claude/.env`

---

## 仓库信息

- **远程仓库：** [github.com/Huangqingan/test](https://github.com/Huangqingan/test)
- **分支：** master（直接 push，无需 PR）
