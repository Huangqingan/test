"""
贪吃蛇小游戏 — 高级版
方向键 / WASD 控制移动，吃到食物得分，撞墙或撞自己扣一条命。
顶部面板可以调节速度、蛇身颜色、食物颜色、生命数（1-10）等设置。
生命耗尽则游戏结束，按 R 键重新开始。

========== 视觉特性 ==========
- 深色高级主题，精致的配色方案
- 蛇身从头到尾渐变过渡
- 食物脉冲发光 + 旋转光环
- 吃食物时的粒子爆发特效
- 得分弹出动画
- 现代化的控制面板
- 精准的网格背景
- 毛玻璃风游戏结束面板
"""

import tkinter as tk
import random
import math
import time

WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20
COLS = WIDTH // CELL_SIZE   # 30
ROWS = HEIGHT // CELL_SIZE  # 30

# ────────────────────────────────
# 预设颜色方案（每个方案包含 head / body / outline / gradient_to）
# ────────────────────────────────
COLOR_PRESETS = {
    "翡翠绿": {
        "head": "#00e676", "body": "#00c853", "outline": "#009624",
        "gradient_to": "#1b5e20",
    },
    "电光蓝": {
        "head": "#448aff", "body": "#2979ff", "outline": "#004ecb",
        "gradient_to": "#0d47a1",
    },
    "霓虹橙": {
        "head": "#ff9100", "body": "#ff6d00", "outline": "#c43e00",
        "gradient_to": "#bf360c",
    },
    "玫红": {
        "head": "#ff4081", "body": "#f50057", "outline": "#b8003a",
        "gradient_to": "#880e4f",
    },
    "紫罗兰": {
        "head": "#e040fb", "body": "#d500f9", "outline": "#8e00aa",
        "gradient_to": "#4a148c",
    },
    "极简白": {
        "head": "#fafafa", "body": "#e0e0e0", "outline": "#9e9e9e",
        "gradient_to": "#616161",
    },
}

# ────────────────────────────────
# 食物预设
# ────────────────────────────────
FOOD_PRESETS = {
    "樱桃红": "#ff1744",
    "琥珀金": "#ffc400",
    "紫水晶": "#d500f9",
    "冰蓝色": "#00e5ff",
    "珍珠白": "#f5f5f5",
}

# ────────────────────────────────
# 背景预设
# ────────────────────────────────
BG_PRESETS = {
    "深空黑": "#0d1117",
    "午夜蓝": "#0a0f1e",
    "石墨灰": "#1a1a1a",
    "墨绿": "#0a1a10",
}

# ────────────────────────────────
# 粒子系统
# ────────────────────────────────
class Particle:
    """单个粒子"""
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size")

    def __init__(self, x, y, color):
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(1.5, 4.5)
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * speed
        self.vy = math.sin(angle) * speed
        self.life = 0.0
        self.max_life = random.uniform(0.3, 0.7)
        self.color = color
        self.size = random.randint(2, 5)


class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🐍 贪吃蛇 · 高级版")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d1117")

        # ── 核心状态 ──
        self.snake = []
        self.food = (0, 0)
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.game_over = False
        self.paused = False
        self.current_lives = 3

        # ── 粒子 & 动画 ──
        self.particles: list[Particle] = []
        self.food_pulse_phase = 0.0          # 食物脉冲相位
        self.score_pop_alpha = 0.0           # 得分弹窗透明度
        self.score_pop_start = 0.0
        self.last_frame_time = time.time()
        self.animation_id = None

        # ── 用户可调设置 ──
        self.speed = tk.IntVar(value=120)
        self.snake_preset = tk.StringVar(value="翡翠绿")
        self.food_preset = tk.StringVar(value="樱桃红")
        self.bg_preset = tk.StringVar(value="深空黑")
        self.lives = tk.IntVar(value=3)

        self.build_ui()
        self.bind_keys()
        self.start_game()
        self.root.mainloop()

    # ═══════════════════════════════════════
    #  UI 构建
    # ═══════════════════════════════════════

    def build_ui(self):
        # ── 顶部控制栏 ──
        self.build_control_bar()
        # ── 得分 & 状态栏 ──
        self.build_status_bar()
        # ── 游戏画布 ──
        self.canvas = tk.Canvas(
            self.root, width=WIDTH, height=HEIGHT,
            bg="#0d1117", highlightthickness=0,
        )
        self.canvas.pack()
        # 画布鼠标特效
        self.canvas.bind("<Button-1>", lambda e: self.toggle_pause())

    def build_control_bar(self):
        """现代化控制栏：半透明深色背景，圆润布局"""
        bar = tk.Frame(self.root, bg="#161b22", padx=12, pady=10)
        bar.pack(fill="x")

        style = {
            "fg": "#c9d1d9",
            "bg": "#161b22",
            "font": ("Segoe UI", 9),
        }

        # ── 速度滑块 ──
        tk.Label(bar, text="⚡ 速度", **style).pack(side="left", padx=(0, 4))
        tk.Scale(
            bar, from_=300, to=50, variable=self.speed,
            orient="horizontal", length=100, showvalue=False,
            bg="#161b22", fg="#58a6ff", highlightthickness=0,
            troughcolor="#21262d", activebackground="#30363d",
            command=lambda _: self._update_speed_display(),
        ).pack(side="left", padx=(0, 4))
        self.speed_display = tk.Label(
            bar, text="", fg="#8b949e", bg="#161b22",
            font=("Segoe UI", 8),
        )
        self.speed_display.pack(side="left", padx=(0, 14))
        self._update_speed_display()

        # 分隔线
        self._sep(bar)

        # ── 蛇身颜色 ──
        tk.Label(bar, text="🎨 蛇身", **style).pack(side="left", padx=(0, 5))
        for name in COLOR_PRESETS:
            c = COLOR_PRESETS[name]["head"]
            btn = tk.Label(
                bar, text="●", fg=c, bg="#161b22",
                font=("Segoe UI", 14), cursor="hand2",
            )
            btn.pack(side="left", padx=1)
            btn.bind("<Button-1>", lambda e, n=name: self.snake_preset.set(n))
            self._tooltip(btn, name)

        self._sep(bar)

        # ── 食物颜色 ──
        tk.Label(bar, text="🍎 食物", **style).pack(side="left", padx=(0, 5))
        for label, color in FOOD_PRESETS.items():
            btn = tk.Label(
                bar, text="●", fg=color, bg="#161b22",
                font=("Segoe UI", 14), cursor="hand2",
            )
            btn.pack(side="left", padx=1)
            btn.bind("<Button-1>", lambda e, c=label: self.food_preset.set(c))
            self._tooltip(btn, label)

        self._sep(bar)

        # ── 背景 ──
        tk.Label(bar, text="🖼 背景", **style).pack(side="left", padx=(0, 5))
        for name, hex_c in BG_PRESETS.items():
            btn = tk.Label(
                bar, text="■", fg=hex_c, bg="#161b22",
                font=("Segoe UI", 12), cursor="hand2",
            )
            btn.pack(side="left", padx=1)
            btn.bind("<Button-1>", lambda e, n=name: self.bg_preset.set(n))
            self._tooltip(btn, name)

        # ── 右侧：生命 & 暂停 ──
        # 暂停按钮
        self.pause_btn = tk.Label(
            bar, text="⏯", fg="#8b949e", bg="#21262d",
            font=("Segoe UI", 14, "bold"), padx=12, pady=2,
            cursor="hand2",
        )
        self.pause_btn.pack(side="right", padx=(8, 0))
        self.pause_btn.bind("<Button-1>", lambda e: self.toggle_pause())
        self._tooltip(self.pause_btn, "暂停 / 继续 (空格)")

        # 生命数滑块
        tk.Label(bar, text="❤️ 生命", **style).pack(side="right", padx=(14, 4))
        tk.Scale(
            bar, from_=10, to=1, variable=self.lives,
            orient="horizontal", length=70, showvalue=True,
            bg="#161b22", fg="#f85149", highlightthickness=0,
            troughcolor="#21262d", activebackground="#30363d",
        ).pack(side="right", padx=(0, 0))

    def build_status_bar(self):
        """得分 & 状态信息"""
        self.status_bar = tk.Frame(self.root, bg="#0d1117", padx=14, pady=6)
        self.status_bar.pack(fill="x")

        self.score_display = tk.Label(
            self.status_bar, text="🏆 得分 0",
            fg="#c9d1d9", bg="#0d1117",
            font=("Segoe UI", 14, "bold"),
        )
        self.score_display.pack(side="left")

        self.lives_display = tk.Label(
            self.status_bar, text="",
            fg="#f85149", bg="#0d1117",
            font=("Segoe UI", 12),
        )
        self.lives_display.pack(side="right")

        self.game_tip = tk.Label(
            self.status_bar, text="方向键/WASD 移动 · 空格暂停 · R 重来",
            fg="#484f58", bg="#0d1117",
            font=("Segoe UI", 8),
        )
        self.game_tip.pack(side="bottom", pady=(2, 0))

    def _sep(self, parent):
        """细分隔线"""
        tk.Frame(parent, width=1, bg="#30363d").pack(
            side="left", fill="y", padx=8, pady=2,
        )

    def _tooltip(self, widget, text):
        """简单 tooltip（hover 后更新状态栏提示）"""
        def show(_): self.game_tip.config(text=text, fg="#8b949e")
        def hide(_): self.game_tip.config(text="方向键/WASD 移动 · 空格暂停 · R 重来", fg="#484f58")
        widget.bind("<Enter>", show)
        widget.bind("<Leave>", hide)

    def bind_keys(self):
        r = self.root
        r.bind("<Up>",    lambda e: self._try_dir("Up"))
        r.bind("<Down>",  lambda e: self._try_dir("Down"))
        r.bind("<Left>",  lambda e: self._try_dir("Left"))
        r.bind("<Right>", lambda e: self._try_dir("Right"))
        r.bind("w", lambda e: self._try_dir("Up"))
        r.bind("s", lambda e: self._try_dir("Down"))
        r.bind("a", lambda e: self._try_dir("Left"))
        r.bind("d", lambda e: self._try_dir("Right"))
        r.bind("<space>", lambda e: self.toggle_pause())

    # ═══════════════════════════════════════
    #  游戏循环
    # ═══════════════════════════════════════

    def start_game(self):
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.game_over = False
        self.paused = False
        self.current_lives = self.lives.get()
        self.particles.clear()
        self.food = self._spawn_food()
        self._update_displays()
        self.last_frame_time = time.time()
        self.root.after(self.speed.get(), self._game_tick)

    def _spawn_food(self):
        while True:
            pos = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
            if pos not in self.snake:
                return pos

    def _try_dir(self, d):
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if not self.game_over and d != opposites.get(self.direction, ""):
            self.next_direction = d

    def _game_tick(self):
        if self.game_over or self.paused:
            return
        self._move()
        self._update_animation()
        self._draw()
        if not self.game_over:
            self.animation_id = self.root.after(self.speed.get(), self._game_tick)

    def _move(self):
        self.direction = self.next_direction
        r, c = self.snake[0]
        dr = {"Up": -1, "Down": 1, "Left": 0, "Right": 0}[self.direction]
        dc = {"Up": 0, "Down": 0, "Left": -1, "Right": 1}[self.direction]
        new_head = (r + dr, c + dc)

        # 撞墙
        if not (0 <= new_head[0] < ROWS and 0 <= new_head[1] < COLS):
            self._lose_life("撞墙了！")
            return
        # 撞自己
        if new_head in self.snake:
            self._lose_life("咬到自己了！")
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            self.score += 10
            self._spawn_eat_particles(new_head)
            self._trigger_score_pop()
            self.food = self._spawn_food()
            self._update_displays()
        else:
            self.snake.pop()

    def _update_animation(self):
        """更新粒子 & 动画参数"""
        now = time.time()
        dt = min(now - self.last_frame_time, 0.1)
        self.last_frame_time = now

        # 食物脉冲
        self.food_pulse_phase += dt * 3.0

        # 更新粒子
        for p in self.particles[:]:
            p.life += dt
            if p.life >= p.max_life:
                self.particles.remove(p)
            else:
                p.x += p.vx
                p.y += p.vy
                p.vy += 0.05  # 微重力

        # 得分弹窗衰减
        if self.score_pop_alpha > 0:
            elapsed = now - self.score_pop_start
            self.score_pop_alpha = max(0, 1.0 - elapsed / 0.8)

    def _spawn_eat_particles(self, pos):
        r, c = pos
        cx = c * CELL_SIZE + CELL_SIZE / 2
        cy = r * CELL_SIZE + CELL_SIZE / 2
        food_color = FOOD_PRESETS[self.food_preset.get()]
        for _ in range(16):
            self.particles.append(Particle(cx, cy, food_color))

    def _trigger_score_pop(self):
        self.score_pop_alpha = 1.0
        self.score_pop_start = time.time()

    def _lose_life(self, reason):
        self.current_lives -= 1
        self._update_displays()
        self.game_over = True

        if self.current_lives > 0:
            self._draw_overlay(
                title=f"💥 {reason}",
                subtitle=f"剩余生命 · {self.current_lives}",
                hint="等待 2 秒自动重生 · 或按 R 立即重生",
                color="#f0883e",
            )
            self.root.bind("r", lambda e: self._respawn())
            self.root.bind("R", lambda e: self._respawn())
            self.root.after(2000, self._respawn)
        else:
            self._draw_overlay(
                title="🕹️ 游戏结束",
                subtitle=f"最终得分 · {self.score}",
                hint="按 R 键重新开始",
                color="#f85149",
            )
            self.root.bind("r", lambda e: self._restart())
            self.root.bind("R", lambda e: self._restart())

    def _respawn(self):
        self.root.unbind("r")
        self.root.unbind("R")
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.game_over = False
        self.paused = False
        self.particles.clear()
        self.food = self._spawn_food()
        self._update_displays()
        self.last_frame_time = time.time()
        self.root.after(self.speed.get(), self._game_tick)

    def _restart(self):
        self.root.unbind("r")
        self.root.unbind("R")
        self.start_game()

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(fg="#f0883e", bg="#21262d")
        else:
            self.pause_btn.config(fg="#8b949e", bg="#21262d")
            self.last_frame_time = time.time()
            self.root.after(self.speed.get(), self._game_tick)

    # ═══════════════════════════════════════
    #  绘制
    # ═══════════════════════════════════════

    def _draw(self):
        c = self.canvas
        c.delete("all")
        bg = BG_PRESETS[self.bg_preset.get()]
        c.config(bg=bg)

        # ── 网格 ──
        self._draw_grid(c, bg)

        # ── 食物（带脉冲发光） ──
        self._draw_food(c)

        # ── 粒子 ──
        self._draw_particles(c)

        # ── 蛇身（渐变） ──
        self._draw_snake(c)

        # ── 得分弹窗 ──
        self._draw_score_pop(c)

    def _draw_grid(self, c, bg):
        """精致网格：根据背景亮度选择网格颜色"""
        # 判断背景明暗
        r = int(bg[1:3], 16)
        g = int(bg[3:5], 16)
        b = int(bg[5:7], 16)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        if lum < 40:
            grid_c = "#1a2230"
        elif lum < 80:
            grid_c = "#2a2a2a"
        else:
            grid_c = "#e8e8e8"

        for i in range(0, WIDTH, CELL_SIZE):
            c.create_line(i, 0, i, HEIGHT, fill=grid_c, width=1)
        for i in range(0, HEIGHT, CELL_SIZE):
            c.create_line(0, i, WIDTH, i, fill=grid_c, width=1)

    def _draw_food(self, c):
        """食物：多层光环脉冲 + 旋转装饰"""
        r, col = self.food
        cx = col * CELL_SIZE + CELL_SIZE / 2
        cy = r * CELL_SIZE + CELL_SIZE / 2
        food_color = FOOD_PRESETS[self.food_preset.get()]
        pulse = (math.sin(self.food_pulse_phase) + 1) / 2  # 0..1

        # 外层光晕（大圆，半透明）
        outer_r = CELL_SIZE / 2 + 4 + pulse * 4
        c.create_oval(
            cx - outer_r, cy - outer_r,
            cx + outer_r, cy + outer_r,
            fill="", outline=food_color, width=2,
            stipple="gray25",
        )

        # 主体
        base_r = CELL_SIZE / 2 - 3
        c.create_oval(
            cx - base_r, cy - base_r,
            cx + base_r, cy + base_r,
            fill=food_color, outline=self._lighten(food_color, 40), width=1,
        )

        # 高光
        hl_r = base_r * 0.35
        hl_off = base_r * 0.3
        c.create_oval(
            cx - hl_r - hl_off, cy - hl_r - hl_off,
            cx + hl_r - hl_off, cy + hl_r - hl_off,
            fill="#ffffff", outline="",
            stipple="gray50",
        )

    def _draw_snake(self, c):
        """蛇身：head → tail 渐变"""
        preset = COLOR_PRESETS[self.snake_preset.get()]
        head_c = self._hex_to_rgb(preset["head"])
        tail_c = self._hex_to_rgb(preset["gradient_to"])
        n = len(self.snake)
        if n == 0:
            return

        for i, (r, col) in enumerate(self.snake):
            t = i / max(n - 1, 1)
            color = self._lerp_rgb(head_c, tail_c, t)

            x1 = col * CELL_SIZE + 1
            y1 = r * CELL_SIZE + 1
            x2 = x1 + CELL_SIZE - 2
            y2 = y1 + CELL_SIZE - 2

            if i == 0:
                # 蛇头：大一号 + 圆角效果 + 眼睛
                pad = 1
                c.create_rectangle(
                    x1 - pad, y1 - pad, x2 + pad, y2 + pad,
                    fill=color, outline=preset["outline"], width=2,
                )
                # 眼睛
                self._draw_eyes(c, r, col, x1, y1, CELL_SIZE)
            elif i == n - 1:
                # 蛇尾：稍小
                c.create_rectangle(
                    x1 + 1, y1 + 1, x2 - 1, y2 - 1,
                    fill=color, outline="", width=0,
                )
            else:
                c.create_rectangle(
                    x1, y1, x2, y2,
                    fill=color, outline=preset["outline"], width=1,
                )

    def _draw_eyes(self, c, _r, _col, x1, y1, size):
        """根据方向画蛇眼睛"""
        d = self.direction
        s = size
        eye_r = 3
        # 两个眼睛的位置
        if d == "Right":
            e1 = (x1 + s - 5, y1 + 5)
            e2 = (x1 + s - 5, y1 + s - 5)
        elif d == "Left":
            e1 = (x1 + 5, y1 + 5)
            e2 = (x1 + 5, y1 + s - 5)
        elif d == "Up":
            e1 = (x1 + 5, y1 + 5)
            e2 = (x1 + s - 5, y1 + 5)
        else:  # Down
            e1 = (x1 + 5, y1 + s - 5)
            e2 = (x1 + s - 5, y1 + s - 5)

        for ex, ey in (e1, e2):
            c.create_oval(
                ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r,
                fill="white", outline="#111111", width=1,
            )
            c.create_oval(
                ex - 1.5, ey - 1.5, ex + 1.5, ey + 1.5,
                fill="#111111", outline="",
            )

    def _draw_particles(self, c):
        """绘制所有活跃粒子"""
        for p in self.particles:
            alpha = 1 - p.life / p.max_life
            r = int(p.size * alpha)
            if r < 1:
                continue
            c.create_oval(
                p.x - r, p.y - r, p.x + r, p.y + r,
                fill=p.color, outline="", stipple="gray50",
            )

    def _draw_score_pop(self, c):
        """得分 +10 弹窗动画"""
        if self.score_pop_alpha <= 0:
            return
        alpha = self.score_pop_alpha
        y_off = (1 - alpha) * 20  # 向上飘
        c.create_text(
            WIDTH // 2, 30 - y_off,
            text="+10",
            fill=self._fade_hex(FOOD_PRESETS[self.food_preset.get()], alpha),
            font=("Segoe UI", 22, "bold"),
        )

    def _draw_overlay(self, title, subtitle, hint, color):
        """统一的游戏结束/重生遮罩"""
        c = self.canvas
        # 半透明背景
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", stipple="gray50")
        # 卡片背景
        card_x1, card_y1 = 80, HEIGHT // 2 - 85
        card_x2, card_y2 = WIDTH - 80, HEIGHT // 2 + 85
        c.create_rectangle(
            card_x1, card_y1, card_x2, card_y2,
            fill="#161b22", outline="#30363d", width=1,
        )
        # 装饰线
        c.create_line(card_x1 + 20, HEIGHT // 2, card_x2 - 20, HEIGHT // 2,
                      fill="#21262d", width=1)

        c.create_text(
            WIDTH // 2, HEIGHT // 2 - 45,
            text=title, fill=color,
            font=("Segoe UI", 20, "bold"),
        )
        c.create_text(
            WIDTH // 2, HEIGHT // 2,
            text=subtitle, fill="#c9d1d9",
            font=("Segoe UI", 14),
        )
        c.create_text(
            WIDTH // 2, HEIGHT // 2 + 45,
            text=hint, fill="#484f58",
            font=("Segoe UI", 10),
        )

    # ═══════════════════════════════════════
    #  工具方法
    # ═══════════════════════════════════════

    def _update_displays(self):
        self.score_display.config(text=f"🏆 得分 {self.score}")
        hearts = "❤️" * self.current_lives + "🖤" * max(0, self.lives.get() - self.current_lives)
        self.lives_display.config(text=hearts)

    def _update_speed_display(self):
        v = self.speed.get()
        if v <= 70:
            label = "极快"
        elif v <= 100:
            label = "快"
        elif v <= 150:
            label = "中等"
        elif v <= 220:
            label = "慢"
        else:
            label = "极慢"
        self.speed_display.config(text=f"{label} {v}ms")

    @staticmethod
    def _hex_to_rgb(h):
        h = h.lstrip("#")
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)

    @staticmethod
    def _lerp_rgb(a, b, t):
        return "#%02x%02x%02x" % (
            int(a[0] + (b[0] - a[0]) * t),
            int(a[1] + (b[1] - a[1]) * t),
            int(a[2] + (b[2] - a[2]) * t),
        )

    @staticmethod
    def _lighten(hex_c, amount):
        r = min(255, int(hex_c[1:3], 16) + amount)
        g = min(255, int(hex_c[3:5], 16) + amount)
        b = min(255, int(hex_c[5:7], 16) + amount)
        return f"#{r:02x}{g:02x}{b:02x}"

    @staticmethod
    def _fade_hex(hex_c, alpha):
        r, g, b = int(hex_c[1:3], 16), int(hex_c[3:5], 16), int(hex_c[5:7], 16)
        bg_r, bg_g, bg_b = 13, 17, 23  # #0d1117
        r = int(bg_r + (r - bg_r) * alpha)
        g = int(bg_g + (g - bg_g) * alpha)
        b = int(bg_b + (b - bg_b) * alpha)
        return f"#{r:02x}{g:02x}{b:02x}"


if __name__ == "__main__":
    SnakeGame()
