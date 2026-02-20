from __future__ import annotations

import json
import math
import random
import time
import tkinter as tk
from pathlib import Path


WIDTH = 920
HEIGHT = 620
SAVE_PATH = Path(__file__).with_name("save.json")


class NeonRun:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Neon Run")
        self.root.geometry(f"{WIDTH}x{HEIGHT}")
        self.root.minsize(800, 560)
        self.root.configure(bg="#05070f")

        self.canvas = tk.Canvas(root, bg="#060b1d", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.high_score = self._load_high_score()
        self.reset()

        self.keys: set[str] = set()
        self.root.bind("<KeyPress>", self.on_key_press)
        self.root.bind("<KeyRelease>", self.on_key_release)
        self.root.bind("<space>", self.on_dash)
        self.root.bind("<Escape>", lambda _e: self.toggle_pause())
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        self.last_t = time.perf_counter()
        self.loop()

    def reset(self) -> None:
        self.running = True
        self.paused = False
        self.game_over = False
        self.player_x = WIDTH * 0.5
        self.player_y = HEIGHT * 0.5
        self.player_r = 11
        self.speed = 230.0
        self.hp = 5
        self.score = 0
        self.multiplier = 1.0
        self.multiplier_t = 0.0
        self.elapsed = 0.0
        self.enemy_timer = 0.0
        self.orb_timer = 0.0
        self.flash_t = 0.0
        self.shake_t = 0.0
        self.dash_cd = 0.0
        self.dash_len = 0.0
        self.vx = 0.0
        self.vy = 0.0
        self.enemies: list[dict[str, float]] = []
        self.orbs: list[dict[str, float]] = []
        self.particles: list[dict[str, float]] = []
        for _ in range(7):
            self.spawn_orb()

    def on_key_press(self, event: tk.Event) -> None:
        self.keys.add(event.keysym.lower())
        if self.game_over and event.keysym.lower() == "r":
            self.reset()

    def on_key_release(self, event: tk.Event) -> None:
        key = event.keysym.lower()
        if key in self.keys:
            self.keys.remove(key)

    def on_dash(self, _event: tk.Event) -> None:
        if self.paused or self.game_over or self.dash_cd > 0:
            return
        dx, dy = self.current_move_dir()
        if dx == 0 and dy == 0:
            return
        dash_speed = 520.0
        self.vx = dx * dash_speed
        self.vy = dy * dash_speed
        self.dash_len = 0.16
        self.dash_cd = 1.0
        self.emit(self.player_x, self.player_y, 24, "#22d3ee", 2.4)

    def toggle_pause(self) -> None:
        if self.game_over:
            return
        self.paused = not self.paused

    def current_move_dir(self) -> tuple[float, float]:
        dx = 0.0
        dy = 0.0
        if "w" in self.keys or "up" in self.keys:
            dy -= 1.0
        if "s" in self.keys or "down" in self.keys:
            dy += 1.0
        if "a" in self.keys or "left" in self.keys:
            dx -= 1.0
        if "d" in self.keys or "right" in self.keys:
            dx += 1.0
        mag = math.hypot(dx, dy)
        if mag > 0:
            return dx / mag, dy / mag
        return 0.0, 0.0

    def spawn_enemy(self) -> None:
        side = random.randint(0, 3)
        if side == 0:
            x, y = random.uniform(0, WIDTH), -20
        elif side == 1:
            x, y = WIDTH + 20, random.uniform(0, HEIGHT)
        elif side == 2:
            x, y = random.uniform(0, WIDTH), HEIGHT + 20
        else:
            x, y = -20, random.uniform(0, HEIGHT)
        speed = random.uniform(70, 135) + self.elapsed * 2.1
        size = random.uniform(9, 15)
        self.enemies.append({"x": x, "y": y, "s": speed, "r": size})

    def spawn_orb(self) -> None:
        margin = 35
        x = random.uniform(margin, WIDTH - margin)
        y = random.uniform(margin, HEIGHT - margin)
        val = random.choice([10, 12, 15, 18])
        self.orbs.append({"x": x, "y": y, "r": 7, "v": val, "t": random.uniform(0, 6.28)})

    def emit(self, x: float, y: float, n: int, color: str, speed: float) -> None:
        for _ in range(n):
            a = random.uniform(0, math.tau)
            s = random.uniform(40, 180) * speed
            self.particles.append(
                {
                    "x": x,
                    "y": y,
                    "vx": math.cos(a) * s,
                    "vy": math.sin(a) * s,
                    "t": random.uniform(0.25, 0.8),
                    "c": color,
                }
            )

    def update(self, dt: float) -> None:
        if self.paused or self.game_over:
            return

        self.elapsed += dt
        self.enemy_timer += dt
        self.orb_timer += dt
        self.multiplier_t = max(0.0, self.multiplier_t - dt)
        self.flash_t = max(0.0, self.flash_t - dt)
        self.shake_t = max(0.0, self.shake_t - dt)
        self.dash_cd = max(0.0, self.dash_cd - dt)

        if self.multiplier_t <= 0:
            self.multiplier = max(1.0, self.multiplier - dt * 0.5)

        spawn_interval = max(0.22, 1.2 - self.elapsed * 0.014)
        while self.enemy_timer >= spawn_interval:
            self.enemy_timer -= spawn_interval
            self.spawn_enemy()

        if self.orb_timer >= 1.2 and len(self.orbs) < 16:
            self.orb_timer = 0.0
            self.spawn_orb()

        dx, dy = self.current_move_dir()
        if self.dash_len > 0:
            self.dash_len -= dt
            self.player_x += self.vx * dt
            self.player_y += self.vy * dt
        else:
            self.vx = dx * self.speed
            self.vy = dy * self.speed
            self.player_x += self.vx * dt
            self.player_y += self.vy * dt

        self.player_x = max(self.player_r, min(WIDTH - self.player_r, self.player_x))
        self.player_y = max(self.player_r, min(HEIGHT - self.player_r, self.player_y))

        for orb in self.orbs:
            orb["t"] += dt * 4.0

        i = 0
        while i < len(self.orbs):
            orb = self.orbs[i]
            if math.hypot(self.player_x - orb["x"], self.player_y - orb["y"]) <= self.player_r + orb["r"]:
                self.orbs.pop(i)
                gain = int(orb["v"] * self.multiplier)
                self.score += gain
                self.multiplier = min(4.0, self.multiplier + 0.18)
                self.multiplier_t = 1.5
                self.emit(orb["x"], orb["y"], 11, "#22d3ee", 1.2)
            else:
                i += 1

        i = 0
        while i < len(self.enemies):
            e = self.enemies[i]
            vx = self.player_x - e["x"]
            vy = self.player_y - e["y"]
            d = math.hypot(vx, vy)
            if d > 0:
                e["x"] += (vx / d) * e["s"] * dt
                e["y"] += (vy / d) * e["s"] * dt
            if d <= self.player_r + e["r"]:
                if self.dash_len > 0:
                    self.score += int(30 * self.multiplier)
                    self.emit(e["x"], e["y"], 18, "#f59e0b", 1.8)
                    self.enemies.pop(i)
                    continue
                self.hp -= 1
                self.flash_t = 0.18
                self.shake_t = 0.22
                self.emit(self.player_x, self.player_y, 20, "#ef4444", 1.8)
                self.enemies.pop(i)
                if self.hp <= 0:
                    self.end_game()
                    return
                i += 1
            else:
                i += 1

        i = 0
        while i < len(self.particles):
            p = self.particles[i]
            p["x"] += p["vx"] * dt
            p["y"] += p["vy"] * dt
            p["t"] -= dt
            p["vx"] *= 0.94
            p["vy"] *= 0.94
            if p["t"] <= 0:
                self.particles.pop(i)
            else:
                i += 1

        self.score += int(dt * (6 + self.elapsed * 0.6))

    def end_game(self) -> None:
        self.game_over = True
        if self.score > self.high_score:
            self.high_score = self.score
            self._save_high_score()

    def draw(self) -> None:
        self.canvas.delete("all")
        ox = random.uniform(-5, 5) if self.shake_t > 0 else 0
        oy = random.uniform(-5, 5) if self.shake_t > 0 else 0

        self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#060b1d", outline="")
        for x in range(0, WIDTH, 40):
            self.canvas.create_line(x + ox * 0.2, 0, x + ox * 0.2, HEIGHT, fill="#0e1c36")
        for y in range(0, HEIGHT, 40):
            self.canvas.create_line(0, y + oy * 0.2, WIDTH, y + oy * 0.2, fill="#0e1c36")

        for orb in self.orbs:
            bob = math.sin(orb["t"]) * 3.0
            x = orb["x"] + ox * 0.4
            y = orb["y"] + bob + oy * 0.4
            r = orb["r"]
            self.canvas.create_oval(x - r - 4, y - r - 4, x + r + 4, y + r + 4, fill="#22d3ee", outline="")
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#a5f3fc", outline="")

        for e in self.enemies:
            x = e["x"] + ox
            y = e["y"] + oy
            r = e["r"]
            self.canvas.create_oval(x - r - 2, y - r - 2, x + r + 2, y + r + 2, fill="#7f1d1d", outline="")
            self.canvas.create_oval(x - r, y - r, x + r, y + r, fill="#ef4444", outline="")

        pr = self.player_r + (2 if self.dash_len > 0 else 0)
        pc = "#22d3ee" if self.dash_len > 0 else "#67e8f9"
        x = self.player_x + ox
        y = self.player_y + oy
        self.canvas.create_oval(x - pr - 4, y - pr - 4, x + pr + 4, y + pr + 4, fill="#0e7490", outline="")
        self.canvas.create_oval(x - pr, y - pr, x + pr, y + pr, fill=pc, outline="")

        for p in self.particles:
            size = max(1, int(p["t"] * 5))
            self.canvas.create_oval(
                p["x"] - size + ox * 0.6,
                p["y"] - size + oy * 0.6,
                p["x"] + size + ox * 0.6,
                p["y"] + size + oy * 0.6,
                fill=str(p["c"]),
                outline="",
            )

        if self.flash_t > 0:
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#ef4444", stipple="gray50", outline="")

        self.canvas.create_text(16, 16, anchor="nw", fill="#dbeafe", font=("Consolas", 16, "bold"), text=f"Score  {self.score}")
        self.canvas.create_text(16, 44, anchor="nw", fill="#93c5fd", font=("Consolas", 12), text=f"High   {self.high_score}")
        self.canvas.create_text(16, 66, anchor="nw", fill="#93c5fd", font=("Consolas", 12), text=f"x{self.multiplier:.2f}")
        self.canvas.create_text(
            WIDTH - 12,
            18,
            anchor="ne",
            fill="#fca5a5",
            font=("Consolas", 12, "bold"),
            text="HP " + ("■" * self.hp),
        )
        dash_txt = "READY" if self.dash_cd <= 0 else f"{self.dash_cd:.1f}s"
        self.canvas.create_text(WIDTH - 12, 40, anchor="ne", fill="#7dd3fc", font=("Consolas", 12), text=f"DASH {dash_txt}")
        self.canvas.create_text(
            WIDTH - 12,
            HEIGHT - 12,
            anchor="se",
            fill="#94a3b8",
            font=("Consolas", 11),
            text="Move: WASD/Arrows   Dash: Space   Pause: Esc",
        )

        if self.paused:
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", stipple="gray50", outline="")
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 - 15, fill="#e2e8f0", font=("Consolas", 24, "bold"), text="PAUSED")
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 + 18, fill="#94a3b8", font=("Consolas", 12), text="Press Esc to resume")

        if self.game_over:
            self.canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="#000000", stipple="gray50", outline="")
            self.canvas.create_text(WIDTH / 2, HEIGHT / 2 - 28, fill="#fca5a5", font=("Consolas", 28, "bold"), text="GAME OVER")
            self.canvas.create_text(
                WIDTH / 2,
                HEIGHT / 2 + 6,
                fill="#e2e8f0",
                font=("Consolas", 15),
                text=f"Score {self.score}   High {self.high_score}",
            )
            self.canvas.create_text(
                WIDTH / 2,
                HEIGHT / 2 + 36,
                fill="#93c5fd",
                font=("Consolas", 12),
                text="Press R to restart",
            )

    def loop(self) -> None:
        now = time.perf_counter()
        dt = min(0.05, now - self.last_t)
        self.last_t = now
        self.update(dt)
        self.draw()
        self.root.after(16, self.loop)

    def _load_high_score(self) -> int:
        if not SAVE_PATH.exists():
            return 0
        try:
            data = json.loads(SAVE_PATH.read_text(encoding="utf-8"))
            return max(0, int(data.get("high_score", 0)))
        except (OSError, ValueError, json.JSONDecodeError):
            return 0

    def _save_high_score(self) -> None:
        try:
            SAVE_PATH.write_text(json.dumps({"high_score": self.high_score}), encoding="utf-8")
        except OSError:
            pass

    def on_close(self) -> None:
        self.root.destroy()


def main() -> None:
    root = tk.Tk()
    NeonRun(root)
    root.mainloop()


if __name__ == "__main__":
    main()
