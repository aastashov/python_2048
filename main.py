from __future__ import annotations

import curses
import random
from copy import deepcopy

screen = curses.initscr()
curses.noecho()
curses.cbreak()
screen.keypad(True)


class Keyboard:
    KEY_Q: int = ord("q")
    KEY_UNDO: int = ord("r")


class YouAreWin(Exception):
    def __str__(self):
        return "You are win!"


class GameOver(Exception):
    def __str__(self):
        return "Game over"


TypeRow = list[int, int, int, int]
TypeTable = list[TypeRow, TypeRow, TypeRow, TypeRow,]


class Game:
    table: TypeTable = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    previous_table: TypeTable = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]

    moves = 0
    score = 0

    def set_rundom_number(self):
        empty_positions: list[list[int, int]] | list = []
        for x, row in enumerate(self.table):
            if 2048 in row:
                raise YouAreWin

            for y, number in enumerate(row):
                if number != 0:
                    continue

                empty_positions.append([x, y])

        if not empty_positions:
            raise GameOver()

        x, y = random.choice(empty_positions)  # type: int, int
        self.table[x][y] = random.choices([2, 4], weights=[20, 1])[0]

    def can_not_move(self) -> bool:
        can_not_move_x = self.on_left() == self.table and self.on_right() == self.table
        can_not_move_y = self.on_up() == self.table and self.on_down() == self.table
        return can_not_move_x and can_not_move_y

    def refresh_screen(self) -> None:
        screen.clear()
        self.print_statistic()
        self.print_table()

    def print_statistic(self):
        screen.addstr(f"Score: {self.score}; Moves: {self.moves}\n")

    def print_table(self):
        screen.addstr("\n".join(f"{row}" for row in self.table) + "\n")

    def save_point(self):
        self.previous_table = deepcopy(self.table)

    def create_table(self):
        self.set_rundom_number()
        self.set_rundom_number()
        self.save_point()
        self.print_table()

    @staticmethod
    def _move(table: TypeTable) -> int:
        score = 0
        for x, row in enumerate(table):
            while row.count(0):
                row.pop(row.index(0))

            match len(row):
                case 0:
                    table[x] = [0, 0, 0, 0]
                case 1:
                    table[x] = [row[0], 0, 0, 0]
                case 2:
                    if row[0] == row[1]:
                        table[x] = [row[0] + row[1], 0, 0, 0]
                        score += row[0]
                    else:
                        table[x] = [row[0], row[1], 0, 0]
                case 3:
                    if row[0] == row[1]:
                        table[x] = [row[0] + row[1], row[2], 0, 0]
                        score += row[0]
                    elif row[1] == row[2]:
                        table[x] = [row[0], row[1] + row[2], 0, 0]
                        score += row[1]
                    else:
                        table[x] = [row[0], row[1], row[2], 0]
                case 4:
                    if row[0] == row[1]:
                        table[x] = [row[0] + row[1], row[2], row[3], 0]
                        score += row[0]
                        if row[2] == row[3]:
                            table[x] = [row[0] + row[1], row[2] + row[3], 0, 0]
                            score += row[2]
                    elif row[1] == row[2]:
                        table[x] = [row[0], row[1] + row[2], row[3], 0]
                        score += row[1]
                    elif row[2] == row[3]:
                        table[x] = [row[0], row[1], row[2] + row[3], 0]
                        score += row[2]
        return score

    def on_up(self) -> tuple[TypeTable, int]:
        reversed_table = list(map(list, zip(*self.table)))
        score = self._move(reversed_table)
        return list(map(list, zip(*reversed_table))), score

    def on_down(self) -> tuple[TypeTable, int]:
        reversed_table = []
        for x, row in enumerate(list(zip(*self.table))):
            reversed_table.append(list(reversed(row)))

        score = self._move(reversed_table)

        new_table = deepcopy(self.table)
        for x, row in enumerate(reversed_table):
            new_table[x] = list(reversed(row))

        return list(map(list, zip(*new_table))), score

    def on_right(self) -> tuple[TypeTable, int]:
        reversed_table = []
        for row in self.table:
            reversed_table.append(list(reversed(row)))

        score = self._move(reversed_table)

        new_table = deepcopy(self.table)
        for x, row in enumerate(reversed_table):
            new_table[x] = list(reversed(row))
        return new_table, score

    def on_left(self) -> tuple[TypeTable, int]:
        new_table = deepcopy(self.table)
        score = self._move(new_table)
        return new_table, score

    def wait_input(self):
        while True:
            new_table: TypeTable | None = None
            score = 0

            key = screen.getch()
            match key:
                case Keyboard.KEY_Q:
                    raise KeyboardInterrupt
                # todo: need to fix
                # case Keyboard.KEY_UNDO:
                #     new_table = deepcopy(self.previous_table)
                case curses.KEY_UP:
                    new_table, score = self.on_up()
                case curses.KEY_DOWN:
                    new_table, score = self.on_down()
                case curses.KEY_RIGHT:
                    new_table, score = self.on_right()
                case curses.KEY_LEFT:
                    new_table, score = self.on_left()

            if new_table is None or new_table == self.table:
                continue

            # self.save_point()
            self.table = new_table
            self.set_rundom_number()

            self.moves += 1
            self.score += score

            self.refresh_screen()

            if self.can_not_move():
                raise GameOver()

    def new(self):
        screen.addstr("Welcome to 2048 game!\n")
        self.create_table()
        try:
            self.wait_input()
        except KeyboardInterrupt:
            curses.endwin()
            print("Bye!")
        except (GameOver, YouAreWin) as e:
            curses.endwin()
            print(e)


if __name__ == '__main__':
    game = Game()
    game.new()
