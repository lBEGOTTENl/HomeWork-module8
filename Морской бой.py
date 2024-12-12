import random


class Dot:

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))


class Ship:

    def __init__(self, start, length, orientation):
        self.start = start
        self.length = length
        self.orientation = orientation
        self.hits = 0
        self.dots = self.get_ship_dots()

    def get_ship_dots(self):
        dots = []
        for i in range(self.length):
            if self.orientation == 'horizontal':
                dots.append(Dot(self.start.x, self.start.y + i))
            else:
                dots.append(Dot(self.start.x + i, self.start.y))
        return dots

    def is_sunk(self):
        return self.hits >= self.length


class ShipPlacementException(Exception):
    pass


class Board:

    def __init__(self):
        self.size = 6
        self.ships = []
        self.shots = set()
        self.field = [['О' for _ in range(self.size)] for _ in range(self.size)]

    def add_ship(self, ship):
        if not self.can_place_ship(ship):
            raise ShipPlacementException("Корабль не может быть размещен на данной позиции.")

        for dot in ship.dots:
            self.field[dot.x][dot.y] = '■'
        self.ships.append(ship)

    def can_place_ship(self, ship):
        for dot in ship.dots:
            if dot.x < 0 or dot.x >= self.size or dot.y < 0 or dot.y >= self.size:
                return False
            if self.field[dot.x][dot.y] != 'О':
                return False

            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if 0 <= dot.x + dx < self.size and 0 <= dot.y + dy < self.size:
                        if self.field[dot.x + dx][dot.y + dy] != 'О':
                            return False

        return True

    def print_board(self, show_ships=True):
        print("   | " + " | ".join(str(i + 1) for i in range(self.size)) + " |")
        for i, row in enumerate(self.field):
            row_to_print = []
            for cell in row:
                if cell == '■' and not show_ships:
                    row_to_print.append('О')
                else:
                    row_to_print.append(cell)
            print(f"{i + 1} | " + " | ".join(row_to_print) + " |")

    def shoot(self, dot):
        if dot in self.shots:
            raise ValueError("Вы уже стреляли в эту клетку!")

        self.shots.add(dot)
        for ship in self.ships:
            if dot in ship.dots:
                ship.hits += 1
                self.field[dot.x][dot.y] = 'X'
                return True
        self.field[dot.x][dot.y] = 'T'
        return False


class Player:

    def __init__(self):
        self.board = Board()

    def setup(self):
        raise NotImplementedError("Метод setup должен быть реализован в подклассах.")

    def shoot(self, dot):
        return self.board.shoot(dot)


class User(Player):
    def setup(self):
        print("Размещение кораблей пользователем:")
        ship_lengths = [3] + [2, 2] + [1, 1, 1, 1]
        for length in ship_lengths:
            while True:
                try:
                    user_input = input(f"Введите координаты начала корабля длиной {length} (x,y) и ориентацию (h/v): ")
                    x, y, orientation = user_input.split(',')
                    x, y = int(x.strip()) - 1, int(y.strip()) - 1
                    orientation = orientation.strip()

                    if orientation not in ['h', 'v']:
                        raise ShipPlacementException("Неверная ориентация! Используйте 'h' или 'v'.")

                    ship = Ship(Dot(x, y), length, 'horizontal' if orientation == 'h' else 'vertical')
                    self.board.add_ship(ship)
                    print(f"Корабль длиной {length} успешно размещен.")
                    break
                except (ValueError, IndexError):
                    print("Ошибка ввода! Убедитесь, что вводите корректные координаты и ориентацию.")
                except ShipPlacementException as e:
                    print(e)


class AI(Player):
    def setup(self):
        print("Размещение кораблей AI:")
        ship_lengths = [3] + [2, 2] + [1, 1, 1, 1]
        for length in ship_lengths:
            while True:
                orientation = random.choice(['horizontal', 'vertical'])
                x = random.randint(0, self.board.size - 1)
                y = random.randint(0, self.board.size - 1)
                ship = Ship(Dot(x, y), length, orientation)
                try:
                    self.board.add_ship(ship)
                    break
                except ShipPlacementException:
                    continue


class Game:
    def __init__(self):
        self.user = User()
        self.ai = AI()

    def random_ship_placement(self, board, ship_lengths):
        for length in ship_lengths:
            while True:
                orientation = random.choice(['horizontal', 'vertical'])
                x = random.randint(0, board.size - 1)
                y = random.randint(0, board.size - 1)
                ship = Ship(Dot(x, y), length, orientation)
                try:
                    board.add_ship(ship)
                    break
                except ShipPlacementException:
                    continue

    def start(self):
        ship_lengths = [3] + [2, 2] + [1, 1, 1, 1]

        self.random_ship_placement(self.user.board, ship_lengths)
        self.random_ship_placement(self.ai.board, ship_lengths)

        while True:
            self.user.board.print_board(show_ships=True)
            self.ai.board.print_board(show_ships=False)

            try:
                x = int(input("Введите координаты X для выстрела (1-6): ")) - 1
                y = int(input("Введите координаты Y для выстрела (1-6): ")) - 1
                hit = self.ai.shoot(Dot(x, y))
                if hit:
                    print("Попадание!")
                else:
                    print("Промах!")

                while True:
                    ai_x = random.randint(0, 5)
                    ai_y = random.randint(0, 5)
                    try:
                        ai_hit = self.user.shoot(Dot(ai_x, ai_y))
                        if ai_hit:
                            print("AI попал!")
                        else:
                            print("AI промахнулся!")
                        break
                    except ValueError as e:
                        print(e)

            except (ValueError, IndexError):
                print("Ошибка ввода! Убедитесь, что вводите корректные координаты.")

            if all(ship.is_sunk() for ship in self.ai.board.ships):
                print("Вы победили!")
                break
            elif all(ship.is_sunk() for ship in self.user.board.ships):
                print("")

if __name__ == "__main__":
    game = Game()
    game.start()