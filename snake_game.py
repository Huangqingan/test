"""
贪吃蛇小游戏
方向键 / WASD 控制移动，吃到食物得分，撞墙或撞自己扣一条命。
顶部面板可以调节速度、蛇身颜色、生命数（1-10）等设置。
生命耗尽则游戏结束，按 R 键重新开始。
"""
import tkinter as tk
import random

WIDTH = 600
HEIGHT = 600
CELL_SIZE = 20


# ── 预设颜色方案 ──
COLOR_PRESETS = {
    "经典绿":  {"head": "#2ecc71", "body": "#27ae60", "outline": "#1e8449"},
    "天空蓝":  {"head": "#3498db", "body": "#2980b9", "outline": "#1c5980"},
    "活力橙":  {"head": "#f39c12", "body": "#e67e22", "outline": "#b8600f"},
    "樱花粉":  {"head": "#e91e63", "body": "#c2185b", "outline": "#8e0038"},
    "暗夜紫":  {"head": "#9b59b6", "body": "#8e44ad", "outline": "#5b2c6e"},
    "极简白":  {"head": "#ecf0f1", "body": "#bdc3c7", "outline": "#95a5a6"},
}


class SnakeGame:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("贪吃蛇")
        self.root.resizable(False, False)

        # ── 可调节设置 ──
        self.speed = tk.IntVar(value=120)          # 刷新间隔（毫秒）
        self.bg_color = tk.StringVar(value="#1a1a2e")
        self.food_color = tk.StringVar(value="#e74c3c")
        self.lives = tk.IntVar(value=3)            # 生命数
        self.snake_preset = "经典绿"                # 当前选中的颜色方案

        self.build_settings_panel()
        self.build_game_area()

        # 绑定方向键
        self.root.bind("<Up>",     lambda e: self.change_direction("Up"))
        self.root.bind("<Down>",   lambda e: self.change_direction("Down"))
        self.root.bind("<Left>",   lambda e: self.change_direction("Left"))
        self.root.bind("<Right>",  lambda e: self.change_direction("Right"))
        self.root.bind("w", lambda e: self.change_direction("Up"))
        self.root.bind("s", lambda e: self.change_direction("Down"))
        self.root.bind("a", lambda e: self.change_direction("Left"))
        self.root.bind("d", lambda e: self.change_direction("Right"))
        # 暂停
        self.root.bind("<space>", lambda e: self.toggle_pause())

        self.paused = False
        self.start_game()
        self.root.mainloop()

    # ─────────────── UI 搭建 ───────────────

    def build_settings_panel(self):
        """顶部设置面板"""
        panel = tk.Frame(self.root, bg="#2c2c3e", padx=10, pady=8)
        panel.pack(fill="x")

        # ── 速度调节 ──
        tk.Label(panel, text="🐍 速度", fg="white", bg="#2c2c3e",
                 font=("Arial", 10)).pack(side="left", padx=(0, 4))
        speed_scale = tk.Scale(
            panel, from_=300, to=50, variable=self.speed,
            orient="horizontal", length=120, showvalue=False,
            bg="#2c2c3e", fg="white", highlightthickness=0,
            troughcolor="#44445e", activebackground="#55557a",
            command=lambda _: self.update_speed_label()
        )
        speed_scale.pack(side="left", padx=(0, 4))
        self.speed_label = tk.Label(
            panel, text=self.speed_text(), fg="#bdc3c7", bg="#2c2c3e",
            font=("Arial", 9)
        )
        self.speed_label.pack(side="left", padx=(0, 16))

        # ── 蛇身颜色 ──
        tk.Label(panel, text="🎨 蛇身颜色", fg="white", bg="#2c2c3e",
                 font=("Arial", 10)).pack(side="left", padx=(0, 6))
        for name, colors in COLOR_PRESETS.items():
            btn = tk.Button(
                panel, text=name, bg=colors["head"], fg="white",
                font=("Arial", 8), padx=6, pady=2,
                activebackground=colors["body"],
                relief="ridge", borderwidth=1,
                command=lambda n=name: self.set_snake_color(n)
            )
            btn.pack(side="left", padx=2)

        # ── 食物颜色 ──
        tk.Label(panel, text="  🍎 食物颜色", fg="white", bg="#2c2c3e",
                 font=("Arial", 10)).pack(side="left", padx=(16, 6))
        food_colors = [
            ("红色", "#e74c3c"), ("金色", "#f1c40f"), ("紫色", "#9b59b6"),
            ("青色", "#00bcd4"), ("白色", "#ecf0f1"),
        ]
        for label, hex_color in food_colors:
            btn = tk.Button(
                panel, text=label, bg=hex_color,
                fg="black" if hex_color in ("#f1c40f", "#ecf0f1") else "white",
                font=("Arial", 8), padx=6, pady=2,
                relief="ridge", borderwidth=1,
                command=lambda c=hex_color: self.food_color.set(c)
            )
            btn.pack(side="left", padx=2)

        # ── 暂停 / 继续 ──
        self.pause_btn = tk.Button(
            panel, text="⏯ 暂停 (空格)", fg="white", bg="#7f8c8d",
            font=("Arial", 9), padx=8, pady=2,
            command=self.toggle_pause
        )
        self.pause_btn.pack(side="right", padx=(10, 0))

        # ── 生命数调节 ──
        tk.Label(panel, text="❤️ 生命", fg="white", bg="#2c2c3e",
                 font=("Arial", 10)).pack(side="right", padx=(16, 4))
        lives_scale = tk.Scale(
            panel, from_=100, to=1, variable=self.lives,
            orient="horizontal", length=80, showvalue=True,
            bg="#2c2c3e", fg="white", highlightthickness=0,
            troughcolor="#44445e", activebackground="#55557a",
        )
        lives_scale.pack(side="right", padx=(0, 16))

    def build_game_area(self):
        """得分标签 + 画布"""
        self.score_label = tk.Label(
            self.root, text="得分: 0", font=("Arial", 14, "bold"),
            fg="white", bg="#16162a"
        )
        self.score_label.pack(fill="x", pady=(0, 0))

        self.canvas = tk.Canvas(
            self.root, width=WIDTH, height=HEIGHT, bg=self.bg_color.get()
        )
        self.canvas.pack()

    # ─────────────── 设置回调 ───────────────

    def set_snake_color(self, name):
        self.snake_preset = name
        if not self.game_over:
            self.draw()

    def update_speed_label(self):
        self.speed_label.config(text=self.speed_text())

    def speed_text(self):
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
        return f"({label} · {v}ms)"

    def toggle_pause(self):
        if self.game_over:
            return
        self.paused = not self.paused
        if self.paused:
            self.pause_btn.config(text="▶ 继续 (空格)", bg="#e67e22")
        else:
            self.pause_btn.config(text="⏯ 暂停 (空格)", bg="#7f8c8d")
            self.game_loop()

    # ─────────────── 游戏逻辑 ───────────────

    def start_game(self):
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.score = 0
        self.game_over = False
        self.paused = False
        self.current_lives = self.lives.get()
        self.food = self.spawn_food()
        self.update_score()
        self.canvas.config(bg=self.bg_color.get())
        self.draw()
        self.root.after(self.speed.get(), self.game_loop)

    def spawn_food(self):
        while True:
            r = random.randint(0, (HEIGHT // CELL_SIZE) - 1)
            c = random.randint(0, (WIDTH // CELL_SIZE) - 1)
            if (r, c) not in self.snake:
                return (r, c)

    def change_direction(self, new_dir):
        opposites = {"Up": "Down", "Down": "Up", "Left": "Right", "Right": "Left"}
        if not self.game_over and new_dir != opposites.get(self.direction, ""):
            self.next_direction = new_dir

    def game_loop(self):
        if self.game_over or self.paused:
            return

        self.direction = self.next_direction
        head_row, head_col = self.snake[0]

        if self.direction == "Up":
            head_row -= 1
        elif self.direction == "Down":
            head_row += 1
        elif self.direction == "Left":
            head_col -= 1
        elif self.direction == "Right":
            head_col += 1

        new_head = (head_row, head_col)

        max_row = HEIGHT // CELL_SIZE
        max_col = WIDTH // CELL_SIZE
        if not (0 <= head_row < max_row and 0 <= head_col < max_col):
            self.end_game("撞墙了！")
            return

        if new_head in self.snake:
            self.end_game("撞到自己了！")
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 10
            self.update_score()
            self.food = self.spawn_food()
        else:
            self.snake.pop()

        self.draw()
        self.root.after(self.speed.get(), self.game_loop)

    def update_score(self):
        hearts = "❤️" * self.current_lives
        self.score_label.config(text=f"得分: {self.score}    {hearts}")

    def draw(self):
        self.canvas.delete("all")
        bg = self.bg_color.get()
        self.canvas.config(bg=bg)

        # 画网格线（浅色辅助线）
        grid_color = "#2a2a40" if bg == "#1a1a2e" else "#e0e0e0"
        for i in range(0, WIDTH, CELL_SIZE):
            self.canvas.create_line(i, 0, i, HEIGHT, fill=grid_color)
        for i in range(0, HEIGHT, CELL_SIZE):
            self.canvas.create_line(0, i, WIDTH, i, fill=grid_color)

        # 食物
        r, c = self.food
        x1 = c * CELL_SIZE + 2
        y1 = r * CELL_SIZE + 2
        self.canvas.create_oval(
            x1, y1, x1 + CELL_SIZE - 4, y1 + CELL_SIZE - 4,
            fill=self.food_color.get(), outline="", width=0
        )

        # 蛇身
        colors = COLOR_PRESETS[self.snake_preset]
        for i, (row, col) in enumerate(self.snake):
            x1 = col * CELL_SIZE + 1
            y1 = row * CELL_SIZE + 1
            x2 = x1 + CELL_SIZE - 2
            y2 = y1 + CELL_SIZE - 2
            if i == 0:
                fill = colors["head"]
                # 蛇头画大一点点，更明显
                self.canvas.create_rectangle(
                    x1 - 1, y1 - 1, x2 + 1, y2 + 1,
                    fill=fill, outline=colors["outline"], width=2
                )
            else:
                self.canvas.create_rectangle(
                    x1, y1, x2, y2,
                    fill=colors["body"], outline=colors["outline"], width=1
                )

    def end_game(self, reason):
        self.current_lives -= 1
        self.update_score()

        if self.current_lives > 0:
            # 还有命，重生（保留得分和生命数）
            self.game_over = True  # 等待重生期间阻止操作
            self.canvas.create_rectangle(
                0, 0, WIDTH, HEIGHT, fill="black", stipple="gray50"
            )
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2 - 20,
                text=f"{reason}  剩余生命: {self.current_lives}",
                fill="#f39c12", font=("Arial", 18, "bold")
            )
            self.canvas.create_text(
                WIDTH // 2, HEIGHT // 2 + 25,
                text="按 R 键或等待 2 秒自动重生",
                fill="#bdc3c7", font=("Arial", 13)
            )
            self.root.bind("r", lambda e: self.respawn())
            self.root.bind("R", lambda e: self.respawn())
            self.root.after(2000, self.respawn)
            return

        self.game_over = True
        # 半透明遮罩
        self.canvas.create_rectangle(
            0, 0, WIDTH, HEIGHT, fill="black", stipple="gray50"
        )
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 - 20,
            text=f"游戏结束 - {reason}",
            fill="white", font=("Arial", 20, "bold")
        )
        self.canvas.create_text(
            WIDTH // 2, HEIGHT // 2 + 25,
            text="按 R 键重新开始",
            fill="#bdc3c7", font=("Arial", 14)
        )
        self.root.bind("r", lambda e: self.restart())
        self.root.bind("R", lambda e: self.restart())

    def respawn(self):
        """保留得分和剩余生命，重新生成蛇和食物"""
        self.root.unbind("r")
        self.root.unbind("R")
        self.snake = [(5, 5), (5, 4), (5, 3)]
        self.direction = "Right"
        self.next_direction = "Right"
        self.game_over = False
        self.paused = False
        self.food = self.spawn_food()
        self.update_score()
        self.draw()
        self.root.after(self.speed.get(), self.game_loop)

    def restart(self):
        self.root.unbind("r")
        self.root.unbind("R")
        self.start_game()


if __name__ == "__main__":
    SnakeGame()
