from functools import lru_cache
from os import name as os_name
from os import system as os_system
from random import randint
from threading import Thread
from time import sleep as time_sleep

import keyboard

BRAND = """
___________
\__    ___/___  __ __   ____ _____    ____   ___________
  |    | /  _ \|  |  \_/ ___\/\__  \  /    \ /  _ \_  __ \/
  |    |(  <_> )  |  /\  \___ / __ \|   |  (  <_> )  | \/
  |____| \____/|____/  \___  >____  /___|  /\____/|__|
                           \/     \/     \/
"""


class Item:
    def __init__(self, raw: str = " ", pos_x: int = 0, pos_y: int = 0) -> None:
        self.raw = raw
        self.pos_x, self.pos_y = pos_x, pos_y

    def set(self, x: int, y: int) -> None:
        self.pos_x, self.pos_y = x, y

    def __add__(self, other) -> str:
        return self.raw + other

    def __radd__(self, other) -> str:
        return self.raw + other

    def __repr__(self) -> str:
        return self.raw

    def __str__(self) -> str:
        return self.raw


class Scene:
    def __init__(self, me: str = "X", width: int = 50, height: int = 30) -> None:
        self.width = width
        self.height = height
        self.range_height = range(0, self.height - 1)
        self.range_width = range(0, self.width - 1)
        self.map = [[]]
        self.should_render = True
        self.env_generated = False
        self.trees = [
            Item("🌳"),
            Item("🌵"),
            Item("🪴"),
        ]
        self.pnjs = [Item("🐄"), Item("🐑"), Item("🐃"), Item("🐂"), Item("🐎"), Item("🐖")]
        self.me = Item(me)
        self.keys = ["Down", "Up", "Left", "Right"]
        self.egg = Item("🥚", randint(0, self.width - 2), randint(0, self.height - 2))
        self.score = 0
        self.egg_captured = 0
        self.time_egg_elapsed = 30
        self.moves = 1
        self.game_stoped = False
        self.grass = ' "'

    def wait(self) -> None:
        time_sleep(0.05)

    def clean_map(self):
        """map initialisation"""
        self.map = [
            [self.grass for y in range(0, self.height)] for x in range(0, self.width)
        ]

    def clean_screen(self) -> None:
        """Clean terminal depending on the os"""
        command = "clear"

        if os_name in ("nt", "dos"):
            command = "cls"
        os_system(command)

    @lru_cache
    def in_width(self, _x: int) -> bool:
        return self.width - 1 > _x >= 0

    @lru_cache
    def in_height(self, _y: int) -> bool:
        return self.height - 1 > _y >= 0

    @lru_cache
    def in_scene(self, item: Item) -> bool:
        return self.in_height(item.pos_y) and self.in_width(item.pos_x)

    def map_egg(self) -> None:
        self.map_it(self.egg)

    def map_it(self, item: Item) -> None:
        """Map an item if it's inside the scene"""
        if self.in_scene(item):
            self.map[item.pos_x][item.pos_y] = item.raw

    def clean_it(self, item: Item) -> None:
        """Clean an item if it's inside the scene"""
        if self.in_scene(item):
            self.map[item.pos_x][item.pos_y] = self.grass

    def clean_and_map(self, item: Item, x: int, y: int) -> None:
        """Clean and map"""
        self.clean_it(item)
        item.set(x, y)
        self.map_it(item)
        self.should_render = True

    def map_it_random(self, item: Item) -> None:
        item.set(randint(0, self.width - 1), randint(0, self.height - 1))

        self.map_it(item)

    def clean_and_map_random(self, item: Item) -> None:
        self.clean_it(item)
        self.map_it_random(item)

    def map_group(self, item, x: int, y: int, rrand: int = 1) -> None:
        """
        map an item in form of bloc
          x x x x
        x   x x x
        x x x x
        x x
        """
        self.map_it(Item(item.raw, x, y))
        self.map_it(Item(item.raw, x + rrand, y))
        self.map_it(Item(item.raw, x, y + rrand))
        self.map_it(Item(item.raw, x + rrand, y + rrand))
        self.map_it(Item(item.raw, x - rrand, y))
        self.map_it(Item(item.raw, x, y - rrand))
        self.map_it(Item(item.raw, x - rrand, y + rrand))
        self.map_it(Item(item.raw, x + rrand, y - rrand))
        self.map_it(Item(item.raw, x - rrand, y - rrand))

        self.map_it(Item(item.raw, x + rrand + 1, y))
        self.map_it(Item(item.raw, x, y + rrand + 1))
        self.map_it(Item(item.raw, x + rrand + 1, y - rrand))
        self.map_it(Item(item.raw, x - rrand, y + rrand + 1))

    def map_group_random(self, item: Item):
        rrand, x, y = (
            randint(0, 1),
            randint(0, self.width - 1),
            randint(0, self.height - 1),
        )
        self.map_group(item, x, y, rrand)

    def generate_env(self) -> None:
        """
        in a loop we generate the environment as tree, rocks, walls and pnjs
        """
        if not self.env_generated:
            for i in range(randint(1, 30)):
                tree = self.trees[randint(0, len(self.trees) - 1)]
                self.map_group_random(tree)

            for i in range(randint(1, 10)):
                self.map_group_random(Item("🪨"))

            for i in range(randint(1, 10)):
                self.map_group_random(Item("🧱"))

            for i in range(randint(3, 30)):
                self.map_it_random(self.pnjs[randint(0, len(self.pnjs) - 1)])

            self.env_generated = True

    def time_elapsed(self):
        """A detached thread to count the time in an infinite loop"""

        while True:
            if self.time_egg_elapsed == 0:
                print(BRAND)
                print(f" 🥇>>GAME OVER | YOUR SCORE: {self.score} <<🥇")
                print(
                    f"\n__EGGS: {self.egg_captured}/{self.egg} | MOVES: {self.moves}/👣"
                    + "_ " * self.width
                )
                self.game_stoped = True
                exit(0)

            self.time_egg_elapsed -= 1
            self.score = abs(
                int(self.egg_captured * 100 - (self.moves / 5))
                / (100 - self.time_egg_elapsed)
            )
            time_sleep(1)

    def print_map(self):
        """print the brand and the map"""
        print(BRAND)
        for j in self.range_height:
            for i in self.range_width:
                if i == self.width - 2:
                    print(self.map[i][j])
                else:
                    print(self.map[i][j], end=" ")

        print(
            f"\n__EGGS: {self.egg_captured}/{self.egg} | MOVES: {self.moves}/👣 | SCORE: {self.score}/🏆 | ELAPSED: {self.time_egg_elapsed}/⌛"
            + "_ " * self.width
        )

    def refresh_screen(self):
        """refresh the screen if the game is still playable"""
        self.clean_map()
        self.generate_env()
        while True:
            if self.game_stoped:
                break
            if self.should_render:
                self.clean_screen()
                self.print_map()
                self.should_render = False

            self.wait()

    def check_collision(self, next_x: int, next_y: int) -> bool:
        """depending on some item types, we detect collisions and prevent that
        to happen"""
        if self.map[next_x][next_y] in ["🪨", "🧱"] + [p.raw for p in self.pnjs]:
            return False
        return True

    def move_me_left(self) -> None:

        if self.in_width(self.me.pos_x - 1) and self.check_collision(
            self.me.pos_x - 1, self.me.pos_y
        ):
            self.clean_and_map(self.me, self.me.pos_x - 1, self.me.pos_y)

    def move_me_right(self) -> None:

        if self.in_width(self.me.pos_x + 1) and self.check_collision(
            self.me.pos_x + 1, self.me.pos_y
        ):
            self.clean_and_map(self.me, self.me.pos_x + 1, self.me.pos_y)

    def move_me_up(self) -> None:

        if self.in_height(self.me.pos_y - 1) and self.check_collision(
            self.me.pos_x, self.me.pos_y - 1
        ):
            self.clean_and_map(self.me, self.me.pos_x, self.me.pos_y - 1)

    def move_me_down(self) -> None:

        if self.in_height(self.me.pos_y + 1) and self.check_collision(
            self.me.pos_x, self.me.pos_y + 1
        ):
            self.clean_and_map(self.me, self.me.pos_x, self.me.pos_y + 1)

    def render(self, key: str) -> None:
        """render and handle player movements"""
        self.map_it(self.me)

        while True:
            if self.game_stoped:
                break

            self.map_egg()

            keyboard.wait(key)

            if key == "Left":
                self.move_me_left()

            if key == "Right":
                self.move_me_right()

            if key == "Down":
                self.move_me_down()

            if key == "Up":
                self.move_me_up()

            if self.me.pos_x == self.egg.pos_x and self.me.pos_y == self.egg.pos_y:
                self.egg.set(randint(0, self.width - 3), randint(0, self.height - 3))
                self.egg_captured += 1

            self.moves += 1


class Game:
    def __init__(self, me: str = "X") -> None:
        self.scene = Scene(me)

    def start(self):
        thread_scene = Thread(target=self.scene.refresh_screen)
        thread_scene.start()

        thread_time = Thread(target=self.scene.time_elapsed)
        thread_time.start()

        threads = [
            Thread(target=self.scene.render, kwargs={"key": key})
            for key in self.scene.keys
        ]

        for thread in threads:
            thread.start()


if __name__ == "__main__":
    g = Game("🐼")
    g.start()
