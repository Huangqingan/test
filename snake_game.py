"""
贪吃蛇小游戏 — 柔和动画版
方向键 / WASD 控制移动，吃到食物得分，撞墙或撞自己扣一条命。
顶部面板调节速度、蛇身颜色、生命数等设置。
生命耗尽则游戏结束，按 R 键重新开始。

========== 视觉特性 ==========
- 柔和动画风，圆形蛇身拼接，无网格
- 圆点背景纹理，温润舒适
- 食物随机形状（圆形/星形/菱形/心形），分值不同
- 蛇身渐变色彩，圆润过渡
- 食物脉冲发光 + 粒子特效
- 得分弹窗动画
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
# 蛇身预设颜色
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
    "奶油白": {
        "head": "#fafafa", "body": "#e0e0e0", "outline": "#9e9e9e",
        "gradient_to": "#9e9e9e",
    },
}

# ────────────────────────────────
# 背景预设
# ────────────────────────────────
BG_PRESETS = {
    "深空黑": "#0d1117",
    "午夜蓝": "#0a0f1e",
    "石墨灰": "#1a1a1a",
    "墨绿": "#0a1a10",
    "暖褐": "#1c1814",
}

# ────────────────────────────────
# 食物类型定义（随机生成）
# ────────────────────────────────
FOOD_TYPES = {
    "circle": {"label": "圆形", "score": 10, "color": "#ff1744"},
    "star":   {"label": "星形", "score": 20, "color": "#ffc400"},
    "diamond":{"label": "菱形", "score": 15, "color": "#00e5ff"},
    "heart":  {"label": "心形", "score": 25, "color": "#ff4081"},
}

FOOD_TYPE_NAMES = list(FOOD_TYPES.keys())


# ────────────────────────────────
# 粒子系统
# ────────────────────────────────
class Particle:
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
        self.root.title("🐍 贪吃蛇 · 柔和动画版")
        self.root.resizable(False, False)
        self.root.configure(bg="#0d1117")

        # ── 核心状态 ──
        self.snake = []
        self.food = (0, 0)
        self.food_type = "circle"  # 当前食物形状类型
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.game_over = False
        self.paused = False
        self.current_lives = 3

        # ── 粒子 & 动画 ──
        self.particles: list[Particle] = []
        self.food_pulse_phase = 0.0
        self.score_pop_alpha = 0.0
        self.score_pop_start = 0.0
        self.score_pop_points = 0  # 记录得分点数
        self.score_pop_food_type = "circle"  # 触发弹窗时的食物类型（Bug-2）
        self.last_frame_time = time.time()
        self.animation_id = None
        self._respawn_after_id = None  # 自动重生回调 ID（Bug-1）

        # ── 背景点阵（预计算）──
        self._bg_dots: list[tuple[int, int, int]] = []
        self._build_background_dots()

        # ── 用户可调设置 ──
        self.speed = tk.IntVar(value=120)
        self.snake_preset = tk.StringVar(value="翡翠绿")
        self.bg_preset = tk.StringVar(value="深空黑")
        self.lives = tk.IntVar(value=3)

        self.build_ui()
        self.bind_keys()
        self.start_game()
        self.root.mainloop()

    def _build_background_dots(self):
        """预计算背景柔点位置和亮度，替代网格线"""
        random.seed(42)
        for _ in range(80):
            x = random.randint(10, WIDTH - 10)
            y = random.randint(10, HEIGHT - 10)
            alpha = random.randint(10, 30)
            self._bg_dots.append((x, y, alpha))

    # ═══════════════════════════════════════
    #  UI 构建
    # ═══════════════════════════════════════

    def build_ui(self):
        self.build_control_bar()
        self.build_status_bar()
        self.canvas = tk.Canvas(
            self.root, width=WIDTH, height=HEIGHT,
            bg="#0d1117", highlightthickness=0,
        )
        self.canvas.pack()
        self.canvas.bind("<Button-1>", lambda e: self.toggle_pause())

    def build_control_bar(self):
        bar = tk.Frame(self.root, bg="#161b22", padx=12, pady=10)
        bar.pack(fill="x")
        style = {"fg": "#c9d1d9", "bg": "#161b22", "font": ("Segoe UI", 9)}

        # 速度
        tk.Label(bar, text="⚡ 速度", **style).pack(side="left", padx=(0, 4))
        tk.Scale(
            bar, from_=300, to=50, variable=self.speed,
            orient="horizontal", length=100, showvalue=False,
            bg="#161b22", fg="#58a6ff", highlightthickness=0,
            troughcolor="#21262d", activebackground="#30363d",
            command=lambda _: self._update_speed_display(),
        ).pack(side="left", padx=(0, 4))
        self.speed_display = tk.Label(
            bar, text="", fg="#8b949e", bg="#161b22", font=("Segoe UI", 8),
        )
        self.speed_display.pack(side="left", padx=(0, 14))
        self._update_speed_display()
        self._sep(bar)

        # 蛇身颜色
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

        # 背景
        tk.Label(bar, text="🖼 背景", **style).pack(side="left", padx=(0, 5))
        for name, hex_c in BG_PRESETS.items():
            btn = tk.Label(
                bar, text="■", fg=hex_c, bg="#161b22",
                font=("Segoe UI", 12), cursor="hand2",
            )
            btn.pack(side="left", padx=1)
            btn.bind("<Button-1>", lambda e, n=name: self.bg_preset.set(n))
            self._tooltip(btn, name)
        self._sep(bar)

        # 食物类型说明
        tk.Label(bar, text="🍽 食物", **style).pack(side="left", padx=(0, 5))
        self.food_legend = tk.Label(
            bar, text="", fg="#8b949e", bg="#161b22",
            font=("Segoe UI", 8),
        )
        self.food_legend.pack(side="left", padx=(0, 0))
        self._update_food_legend()

        # 暂停 + 生命
        self.pause_btn = tk.Label(
            bar, text="⏯", fg="#8b949e", bg="#21262d",
            font=("Segoe UI", 14, "bold"), padx=12, pady=2, cursor="hand2",
        )
        self.pause_btn.pack(side="right", padx=(8, 0))
        self.pause_btn.bind("<Button-1>", lambda e: self.toggle_pause())
        self._tooltip(self.pause_btn, "暂停 / 继续 (空格)")

        tk.Label(bar, text="❤️ 生命", **style).pack(side="right", padx=(14, 4))
        tk.Scale(
            bar, from_=10, to=1, variable=self.lives,
            orient="horizontal", length=70, showvalue=True,
            bg="#161b22", fg="#f85149", highlightthickness=0,
            troughcolor="#21262d", activebackground="#30363d",
        ).pack(side="right", padx=(0, 0))

    def build_status_bar(self):
        self.status_bar = tk.Frame(self.root, bg="#0d1117", padx=14, pady=6)
        self.status_bar.pack(fill="x")
        self.score_display = tk.Label(
            self.status_bar, text="🏆 得分 0",
            fg="#c9d1d9", bg="#0d1117", font=("Segoe UI", 14, "bold"),
        )
        self.score_display.pack(side="left")
        self.lives_display = tk.Label(
            self.status_bar, text="", fg="#f85149", bg="#0d1117",
            font=("Segoe UI", 12),
        )
        self.lives_display.pack(side="right")
        self.game_tip = tk.Label(
            self.status_bar, text="方向键/WASD 移动 · 空格暂停 · R 重来",
            fg="#484f58", bg="#0d1117", font=("Segoe UI", 8),
        )
        self.game_tip.pack(side="bottom", pady=(2, 0))

    def _sep(self, parent):
        tk.Frame(parent, width=1, bg="#30363d").pack(
            side="left", fill="y", padx=8, pady=2)

    def _tooltip(self, widget, text):
        def show(_): self.game_tip.config(text=text, fg="#8b949e")
        def hide(_): self.game_tip.config(
            text="方向键/WASD 移动 · 空格暂停 · R 重来", fg="#484f58")
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
        self.food, self.food_type = self._spawn_food()
        self._update_displays()
        self.last_frame_time = time.time()
        self.root.after(self.speed.get(), self._game_tick)

    def _spawn_food(self):
        """生成食物：随机位置 + 随机类型"""
        while True:
            pos = (random.randint(0, ROWS - 1), random.randint(0, COLS - 1))
            if pos not in self.snake:
                ftype = random.choice(FOOD_TYPE_NAMES)
                return pos, ftype

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

        if not (0 <= new_head[0] < ROWS and 0 <= new_head[1] < COLS):
            self._lose_life("撞墙了！")
            return
        # Bug-3: 吃到食物时检查全身，否则排除蛇尾（蛇尾本次会被移除）
        body_to_check = self.snake if new_head == self.food else self.snake[:-1]
        if new_head in body_to_check:
            self._lose_life("咬到自己了！")
            return

        self.snake.insert(0, new_head)
        if new_head == self.food:
            pts = FOOD_TYPES[self.food_type]["score"]
            self.score += pts
            self._spawn_eat_particles(new_head, self.food_type)
            self._trigger_score_pop(pts, self.food_type)  # 先于 _spawn_food 传入旧类型
            self.food, self.food_type = self._spawn_food()
            self._update_displays()
            self._update_food_legend()
        else:
            self.snake.pop()

    def _update_animation(self):
        now = time.time()
        dt = min(now - self.last_frame_time, 0.1)
        self.last_frame_time = now
        self.food_pulse_phase += dt * 3.0
        # 更新粒子
        for p in self.particles[:]:
            p.life += dt
            if p.life >= p.max_life:
                self.particles.remove(p)
            else:
                p.x += p.vx
                p.y += p.vy
                p.vy += 0.05
        # 得分弹窗衰减
        if self.score_pop_alpha > 0:
            elapsed = now - self.score_pop_start
            self.score_pop_alpha = max(0, 1.0 - elapsed / 0.8)

    def _spawn_eat_particles(self, pos, ftype):
        r, c = pos
        cx = c * CELL_SIZE + CELL_SIZE / 2
        cy = r * CELL_SIZE + CELL_SIZE / 2
        color = FOOD_TYPES[ftype]["color"]
        count = FOOD_TYPES[ftype]["score"]  # 分值越高粒子越多
        for _ in range(count):
            self.particles.append(Particle(cx, cy, color))

    def _trigger_score_pop(self, pts, ftype):
        self.score_pop_alpha = 1.0
        self.score_pop_points = pts
        self.score_pop_food_type = ftype  # Bug-2: 记录触发弹窗时的食物类型
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
            self._respawn_after_id = self.root.after(2000, self._respawn)
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
        # Bug-1: 取消等待中的自动重生回调，防止双游戏循环
        if self._respawn_after_id:
            self.root.after_cancel(self._respawn_after_id)
            self._respawn_after_id = None
        self.root.unbind("r")
        self.root.unbind("R")
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.game_over = False
        self.paused = False
        self.particles.clear()
        self.food, self.food_type = self._spawn_food()
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
        bg_hex = BG_PRESETS[self.bg_preset.get()]
        c.config(bg=bg_hex)

        # 背景柔点（替代网格）
        self._draw_bg_dots(c, bg_hex)

        # 食物（脉冲动画 + 随机形状）
        self._draw_food(c)

        # 粒子
        self._draw_particles(c)

        # 蛇身（圆形拼接，柔和风格）
        self._draw_snake(c)

        # 得分弹窗
        self._draw_score_pop(c)

    def _draw_bg_dots(self, c, bg_hex):
        """柔和的背景点阵纹理，替代生硬的网格线"""
        # 根据背景亮度选点颜色
        r = int(bg_hex[1:3], 16)
        g = int(bg_hex[3:5], 16)
        b = int(bg_hex[5:7], 16)
        lum = 0.299 * r + 0.587 * g + 0.114 * b
        for x, y, alpha in self._bg_dots:
            actual_alpha = alpha + random.randint(-5, 5)
            actual_alpha = max(5, min(40, actual_alpha))
            sz = random.choice([1, 1, 1, 2])  # 大部分 1px，偶尔 2px
            # 用灰度表示透明度
            gray = int(255 * actual_alpha / 100)
            dot_color = f"#{gray:02x}{gray:02x}{gray:02x}" if lum < 30 else \
                        f"#{255-gray:02x}{255-gray:02x}{255-gray:02x}"
            c.create_oval(x - sz, y - sz, x + sz, y + sz,
                          fill=dot_color, outline="")

    def _draw_food(self, c):
        """食物：脉冲动画 + 随机形状渲染"""
        r, col = self.food
        cx = col * CELL_SIZE + CELL_SIZE / 2
        cy = r * CELL_SIZE + CELL_SIZE / 2
        ftype = self.food_type
        ft_info = FOOD_TYPES[ftype]
        color = ft_info["color"]
        pulse = (math.sin(self.food_pulse_phase) + 1) / 2

        # 外层光晕
        outer_r = CELL_SIZE / 2 + 3 + pulse * 5
        c.create_oval(
            cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r,
            fill="", outline=color, width=2, stipple="gray25",
        )

        # 根据类型画不同形状
        base_r = CELL_SIZE / 2 - 3
        if ftype == "circle":
            self._draw_food_circle(c, cx, cy, base_r, color)
        elif ftype == "star":
            self._draw_food_star(c, cx, cy, base_r * 0.85, color)
        elif ftype == "diamond":
            self._draw_food_diamond(c, cx, cy, base_r * 0.85, color)
        elif ftype == "heart":
            self._draw_food_heart(c, cx, cy, base_r * 0.75, color)

    def _draw_food_circle(self, c, cx, cy, r, color):
        """圆形食物 + 高光"""
        c.create_oval(cx - r, cy - r, cx + r, cy + r,
                      fill=color, outline=self._lighten(color, 40), width=1)
        hl_r = r * 0.35
        hl_off = r * 0.3
        c.create_oval(cx - hl_r - hl_off, cy - hl_r - hl_off,
                      cx + hl_r - hl_off, cy + hl_r - hl_off,
                      fill="#ffffff", outline="", stipple="gray50")

    def _draw_food_star(self, c, cx, cy, r, color):
        """五角星食物"""
        points = []
        for i in range(10):
            angle = math.pi / 2 + i * math.pi / 5
            radius = r if i % 2 == 0 else r * 0.4
            px = cx + radius * math.cos(angle)
            py = cy - radius * math.sin(angle)
            points.extend([px, py])
        c.create_polygon(*points, fill=color,
                         outline=self._lighten(color, 40), width=1, smooth=True)

    def _draw_food_diamond(self, c, cx, cy, r, color):
        """菱形食物"""
        points = [cx, cy - r, cx + r, cy, cx, cy + r, cx - r, cy]
        c.create_polygon(*points, fill=color,
                         outline=self._lighten(color, 40), width=1, smooth=True)

    def _draw_food_heart(self, c, cx, cy, r, color):
        """心形食物（用两个圆 + 三角近似）"""
        # 用平滑多边形近似心形
        points = []
        for i in range(20):
            t = i / 20 * 2 * math.pi
            x = 16 * math.sin(t) ** 3
            y = 13 * math.cos(t) - 5 * math.cos(2*t) - 2 * math.cos(3*t) - math.cos(4*t)
            scale = r / 8
            points.extend([cx + x * scale, cy - y * scale])
        c.create_polygon(*points, fill=color,
                         outline=self._lighten(color, 40), width=1, smooth=True)

    def _draw_snake(self, c):
        """蛇身：圆形拼接，柔和动画风"""
        preset = COLOR_PRESETS[self.snake_preset.get()]
        head_c = self._hex_to_rgb(preset["head"])
        tail_c = self._hex_to_rgb(preset["gradient_to"])
        n = len(self.snake)
        if n == 0:
            return

        seg_r = CELL_SIZE / 2 - 2  # 每段圆形半径

        for i, (r, col) in enumerate(self.snake):
            t = i / max(n - 1, 1)
            color = self._lerp_rgb(head_c, tail_c, t)

            cx = col * CELL_SIZE + CELL_SIZE / 2
            cy = r * CELL_SIZE + CELL_SIZE / 2

            if i == 0:
                # 蛇头：稍大圆 + 眼睛
                hr = seg_r + 2
                c.create_oval(cx - hr, cy - hr, cx + hr, cy + hr,
                              fill=color, outline=preset["outline"], width=2)
                self._draw_eyes(c, r, col, cx, cy, hr)
            elif i == n - 1:
                # 蛇尾：稍小圆
                tr = seg_r - 2
                c.create_oval(cx - tr, cy - tr, cx + tr, cy + tr,
                              fill=color, outline="", width=0)
            else:
                c.create_oval(cx - seg_r, cy - seg_r, cx + seg_r, cy + seg_r,
                              fill=color, outline=preset["outline"], width=1)

        # 段间填充，使蛇身平滑连接
        for i in range(n - 1):
            t_mid = (i + 0.5) / max(n - 1, 1)
            color_mid = self._lerp_rgb(head_c, tail_c, t_mid)
            r1, c1 = self.snake[i]
            r2, c2 = self.snake[i + 1]
            mx = (c1 + c2) / 2 * CELL_SIZE + CELL_SIZE / 2
            my = (r1 + r2) / 2 * CELL_SIZE + CELL_SIZE / 2
            bridge_r = seg_r - 1
            c.create_oval(mx - bridge_r, my - bridge_r, mx + bridge_r, my + bridge_r,
                          fill=color_mid, outline="", width=0)

    def _draw_eyes(self, c, _r, _col, cx, cy, r):
        """根据方向绘制蛇眼"""
        d = self.direction
        eye_r = max(2, int(r * 0.25))
        eye_offset = r * 0.4
        pupil_r = eye_r * 0.6

        if d == "Right":
            e1 = (cx + eye_offset, cy - eye_offset)
            e2 = (cx + eye_offset, cy + eye_offset)
        elif d == "Left":
            e1 = (cx - eye_offset, cy - eye_offset)
            e2 = (cx - eye_offset, cy + eye_offset)
        elif d == "Up":
            e1 = (cx - eye_offset, cy - eye_offset)
            e2 = (cx + eye_offset, cy - eye_offset)
        else:  # Down
            e1 = (cx - eye_offset, cy + eye_offset)
            e2 = (cx + eye_offset, cy + eye_offset)

        for ex, ey in (e1, e2):
            c.create_oval(ex - eye_r, ey - eye_r, ex + eye_r, ey + eye_r,
                          fill="white", outline="#111111", width=1)
            c.create_oval(ex - pupil_r, ey - pupil_r, ex + pupil_r, ey + pupil_r,
                          fill="#111111", outline="")

    def _draw_particles(self, c):
        for p in self.particles:
            alpha = 1 - p.life / p.max_life
            pr = int(p.size * alpha)
            if pr < 1:
                continue
            c.create_oval(p.x - pr, p.y - pr, p.x + pr, p.y + pr,
                          fill=p.color, outline="", stipple="gray50")

    def _draw_score_pop(self, c):
        if self.score_pop_alpha <= 0:
            return
        alpha = self.score_pop_alpha
        y_off = (1 - alpha) * 20
        pts = self.score_pop_points
        ft = self.score_pop_food_type  # Bug-2: 使用触发时的食物类型而非当前
        color = FOOD_TYPES[ft]["color"]
        c.create_text(
            WIDTH // 2, 30 - y_off,
            text=f"+{pts}",
            fill=self._fade_hex(color, alpha),
            font=("Segoe UI", 22, "bold"),
        )

    def _draw_overlay(self, title, subtitle, hint, color):
        c = self.canvas
        c.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", stipple="gray50")
        card_x1, card_y1 = 80, HEIGHT // 2 - 85
        card_x2, card_y2 = WIDTH - 80, HEIGHT // 2 + 85
        c.create_rectangle(card_x1, card_y1, card_x2, card_y2,
                           fill="#161b22", outline="#30363d", width=1)
        c.create_line(card_x1 + 20, HEIGHT // 2, card_x2 - 20, HEIGHT // 2,
                      fill="#21262d", width=1)
        c.create_text(WIDTH // 2, HEIGHT // 2 - 45, text=title,
                      fill=color, font=("Segoe UI", 20, "bold"))
        c.create_text(WIDTH // 2, HEIGHT // 2, text=subtitle,
                      fill="#c9d1d9", font=("Segoe UI", 14))
        c.create_text(WIDTH // 2, HEIGHT // 2 + 45, text=hint,
                      fill="#484f58", font=("Segoe UI", 10))

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
            label = "中速"
        elif v <= 220:
            label = "慢"
        else:
            label = "极慢"
        self.speed_display.config(text=f"{label} {v}ms")

    def _update_food_legend(self):
        lines = []
        for name, info in FOOD_TYPES.items():
            lines.append(f"{info['label']}({info['score']}分)")
        self.food_legend.config(text=" | ".join(lines))

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
        bg_r, bg_g, bg_b = 13, 17, 23
        r = int(bg_r + (r - bg_r) * alpha)
        g = int(bg_g + (g - bg_g) * alpha)
        b = int(bg_b + (b - bg_b) * alpha)
        return f"#{r:02x}{g:02x}{b:02x}"


if __name__ == "__main__":
    SnakeGame()
