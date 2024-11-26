import tkinter as tk
import random

class GameObject(object):
    def __init__(self, canvas, item):
        self.canvas = canvas
        self.item = item

    def get_position(self):
        return self.canvas.coords(self.item)

    def move(self, x, y):
        self.canvas.move(self.item, x, y)

    def delete(self):
        self.canvas.delete(self.item)


class Ball(GameObject):
    def __init__(self, canvas, x, y):
        self.radius = 10
        self.direction = [1, -1]
        self.speed = 5
        item = canvas.create_oval(x - self.radius, y - self.radius,
                                  x + self.radius, y + self.radius,
                                  fill='white', outline="cyan", width=2)
        super(Ball, self).__init__(canvas, item)

    def update(self):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] <= 0 or coords[2] >= width:
            self.direction[0] *= -1
        if coords[1] <= 0:
            self.direction[1] *= -1
        x = self.direction[0] * self.speed
        y = self.direction[1] * self.speed
        self.move(x, y)

    def collide(self, game_objects):
        coords = self.get_position()
        x = (coords[0] + coords[2]) * 0.5
        if len(game_objects) > 1:
            self.direction[1] *= -1
        elif len(game_objects) == 1:
            game_object = game_objects[0]
            coords = game_object.get_position()
            if x > coords[2]:
                self.direction[0] = 1
            elif x < coords[0]:
                self.direction[0] = -1
            else:
                self.direction[1] *= -1

        for game_object in game_objects:
            if isinstance(game_object, Brick):
                game_object.hit()


class Paddle(GameObject):
    def __init__(self, canvas, x, y):
        self.width = 100
        self.height = 10
        self.ball = None
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill='#FF5733', outline="#FFBD33", width=3)
        super(Paddle, self).__init__(canvas, item)

    def set_ball(self, ball):
        self.ball = ball

    def move(self, offset):
        coords = self.get_position()
        width = self.canvas.winfo_width()
        if coords[0] + offset >= 0 and coords[2] + offset <= width:
            super(Paddle, self).move(offset, 0)
            if self.ball is not None:
                self.ball.move(offset, 0)


class Brick(GameObject):
    def __init__(self, canvas, x, y, hits):
        self.width = 75
        self.height = 20
        self.hits = hits
        color = random.choice(["#00FFFF", "#1E90FF", "#4682B4", "#5F9EA0"])  # Blue colors
        item = canvas.create_rectangle(x - self.width / 2,
                                       y - self.height / 2,
                                       x + self.width / 2,
                                       y + self.height / 2,
                                       fill=color, outline="white", tags='brick')
        super(Brick, self).__init__(canvas, item)

    def hit(self):
        self.hits -= 1
        if self.hits == 0:
            self.delete()
        else:
            self.canvas.itemconfig(self.item, fill="#D6D1F5")


class Game(tk.Frame):
    def __init__(self, master):
        super(Game, self).__init__(master)
        self.lives = 3
        self.score = 0
        self.width = 800
        self.height = 600
        self.canvas = tk.Canvas(self, bg='#2F4F4F', width=self.width, height=self.height)
        self.canvas.pack()
        self.pack()

        self.items = {}
        self.ball = None
        self.paddle = Paddle(self.canvas, self.width / 2, 550)
        self.items[self.paddle.item] = self.paddle

        for x in range(5, self.width - 5, 85):
            self.add_brick(x + 42.5, 50, 3)
            self.add_brick(x + 42.5, 80, 2)
            self.add_brick(x + 42.5, 110, 1)

        self.hud = None
        self.time_left = 15  # Start with 15 seconds for speed increase
        self.setup_game()
        self.canvas.focus_set()
        self.canvas.bind('<Left>', lambda _: self.paddle.move(-20))
        self.canvas.bind('<Right>', lambda _: self.paddle.move(20))

    def setup_game(self):
        self.add_ball()
        self.update_hud()
        self.text = self.draw_text(self.width / 2, self.height / 2, 'Press Space to Start', size=30)
        self.canvas.bind('<space>', lambda _: self.start_game())
        self.after(1000, self.update_timer)  # Start the timer

    def add_ball(self):
        if self.ball is not None:
            self.ball.delete()
        paddle_coords = self.paddle.get_position()
        x = (paddle_coords[0] + paddle_coords[2]) * 0.5
        self.ball = Ball(self.canvas, x, 530)
        self.paddle.set_ball(self.ball)

    def add_brick(self, x, y, hits):
        brick = Brick(self.canvas, x, y, hits)
        self.items[brick.item] = brick

    def draw_text(self, x, y, text, size='20', color="white"):
        font = ('Orbitron', size, "bold")
        return self.canvas.create_text(x, y, text=text, fill=color, font=font)

    def update_hud(self):
        text = f'Score: {self.score}       Lives: {self.lives}      Level Up in: {self.time_left}s'
        if self.hud is None:
            self.hud = self.draw_text(200, 20, text, 15)
        else:
            self.canvas.itemconfig(self.hud, text=text)

    def start_game(self):
        self.canvas.unbind('<space>')
        self.canvas.delete(self.text)
        self.paddle.ball = None
        self.game_loop()

    def game_loop(self):
        self.check_collisions()
        num_bricks = len(self.canvas.find_withtag('brick'))
        if num_bricks == 0:
            self.ball.speed = None
            self.draw_text(self.width / 2, self.height / 2, 'You Win!', size=40, color="gold")
        elif self.ball.get_position()[3] >= self.height:
            self.ball.speed = None
            self.lives -= 1
            if self.lives < 0:
                self.draw_text(self.width / 2, self.height / 2, 'Game Over', size=40, color="red")
            else:
                self.after(1000, self.setup_game)
        else:
            self.ball.update()
            self.after(50, self.game_loop)

    def check_collisions(self):
        ball_coords = self.ball.get_position()
        items = self.canvas.find_overlapping(*ball_coords)
        objects = [self.items[x] for x in items if x in self.items]
        self.ball.collide(objects)
        for obj in objects:
            if isinstance(obj, Brick):
                self.score += 10
        self.update_hud()

    def update_timer(self):
        self.time_left -= 1
        if self.time_left <= 0:
            self.increase_ball_speed()
            self.time_left = 15  # Reset the timer to 15 seconds
        self.update_hud()
        self.after(1000, self.update_timer)  # Update every second

    def increase_ball_speed(self):
        self.ball.speed += 1  # Increase speed every 15 seconds
        print(f'Ball speed increased: {self.ball.speed}')  # Debugging line to show speed increase


if __name__ == '__main__':
    root = tk.Tk()
    root.title('Game Break Those Bricks')
    game = Game(root)
    game.mainloop()
