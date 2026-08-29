from random import randint

import pygame as pg

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# White
WHITE_COLOR = (255, 255, 255)

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pg.display.set_caption('Змейка')

# Настройка времени:
clock = pg.time.Clock()


class GameObject:
    """Родительский класс."""

    def __init__(self, position=None, body_color=None):
        if position is None:
            self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        else:
            self.position = position

        if body_color is None:
            self.body_color = WHITE_COLOR
        else:
            self.body_color = body_color

    def draw(self):
        """
        Метод отрисовки.

        Метод должен быть реализован в классах - наследниках.
        Если этого не сделать, игра сообщит об ошибке.
        """
        raise NotImplementedError(
            f'Метод draw не реализован в классе {self.__class__.__name__}. '
            'Пожалуйста, переопределите его в классе - наследнике.'
        )

    def _draw_cell(self, position):
        """Используется внутри draw() классов - наследников"""
        rect = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, self.body_color, rect)
        pg.draw.rect(screen, BORDER_COLOR, rect, 1)


class Apple(GameObject):
    """
    Класс отвечающий за отрисовку и
    генерацию координат появления яблока.
    """

    def __init__(self, position=None, body_color=APPLE_COLOR):
        if position is None:
            start_pos = self._generate_initial_position()
        else:
            start_pos = position
        super().__init__(position=start_pos, body_color=body_color)

    def _generate_initial_position(self):
        cell_count_x = randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1)
        cell_count_y = randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1)
        return (cell_count_x * GRID_SIZE, cell_count_y * GRID_SIZE)

    def randomize_position(self, snake_positions):
        """Генерирует случайные координаты для яблока, избегая змею."""
        while True:
            cell_count_x = randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1)
            cell_count_y = randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1)
            new_position = (cell_count_x * GRID_SIZE, cell_count_y * GRID_SIZE)

            if new_position not in snake_positions:
                self.position = new_position
                break

    def draw(self):
        """Отрисовывает яблоко."""
        self._draw_cell(self.position)


class Snake(GameObject):
    """
    Класс отвечающий за движения
    и отрисовку змейки.
    """

    INVALID_MOVES = {
        UP: (pg.K_DOWN,),
        DOWN: (pg.K_UP,),
        LEFT: (pg.K_RIGHT,),
        RIGHT: (pg.K_LEFT,),
    }

    def __init__(self, body_color=SNAKE_COLOR):
        start_position = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) - GRID_SIZE)
        super().__init__(position=start_position, body_color=body_color)
        self.positions = [start_position]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.last = None
        self.score = 0

        self.needs_full_clear = False

    def move(self, apple_position):
        """Добавляет клеточку змейки в направлении движения
        и удаляет последнюю, плюс добавляет координаты в positions
        при росте. Возвращает True, если съели яблоко, иначе False.
        Также обновляет флаг needs_full_clear при проигрыше.
        """
        head_x, head_y = self.get_head_position()
        dir_x, dir_y = self.direction
        # расчёт новых координат для появления головы змеи
        new_x = (head_x + dir_x * GRID_SIZE) % SCREEN_WIDTH
        new_y = (head_y + dir_y * GRID_SIZE) % SCREEN_HEIGHT
        new_head = (new_x, new_y)
        # Рост = координаты головы в координатах яблока
        growing = (new_head == apple_position)
        # добавление головы в начало списка positions (тело змеи)
        self.positions.insert(0, new_head)
        # если нет роста - удаляет хвост
        old_tail = None
        if not growing:
            old_tail = self.positions.pop()

        # самоедство
        if new_head in self.positions[1:]:
            self.reset()
            self.needs_full_clear = True
            return False

        # рост
        if growing:
            self.grow()
            return True

        return old_tail

    def set_next_direction(self, key):
        """
        Устанавливает желаемое направление на основе нажатой клавиши.
        Использует таблицу запретов, чтобы избежать разворота на 180 градусов.
        """
        key_to_dir = {
            pg.K_UP: UP,
            pg.K_DOWN: DOWN,
            pg.K_LEFT: LEFT,
            pg.K_RIGHT: RIGHT,
        }

        allowed_direction = key_to_dir.get(key)

        if allowed_direction is None:
            return
        forbidden_direction = self.INVALID_MOVES.get(self.direction, ())
        if key in forbidden_direction:
            return
        self.next_direction = allowed_direction

    def grow(self):
        """Увеличивает длину змейки на 1."""
        self.length += 1

    def update_direction(self, next_direction=None):
        """
        Обновляет координаты появления головы змейки
        после выбора направления.
        """
        if self.next_direction:
            self.direction = self.next_direction

    def draw(self):
        """Отрисовывает все сегменты змейки."""
        for pos in self.positions[1:]:
            self._draw_cell(pos)

        self._draw_cell(self.get_head_position())

    def get_head_position(self):
        """Возвращает координат первого сегмента списка (головы)."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает игру в начальное положение и состояние."""
        start_x = SCREEN_WIDTH // 2
        start_y = (SCREEN_HEIGHT // 2) - GRID_SIZE
        start_position = (start_x, start_y)
        self.positions = [start_position]
        self.direction = RIGHT
        self.next_direction = None
        self.length = 1
        self.score = 0
        self.last = None


def main():
    """Основная функция, отвечающая за логику игры"""
    pg.init()

    snake = Snake()
    apple = Apple()
    apple.randomize_position(snake.positions)

    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw()
    apple.draw()
    pg.display.flip()

    running = True
    while running:
        running = handle_keys(snake)
        snake.update_direction()

        old_tail_or_ate = snake.move(apple.position)

        if old_tail_or_ate is True:
            apple.randomize_position(snake.positions)
        else:
            old_tail = old_tail_or_ate

            if snake.needs_full_clear:
                screen.fill(BOARD_BACKGROUND_COLOR)
                snake.needs_full_clear = False
            elif old_tail is not None:
                rect = pg.Rect(old_tail, (GRID_SIZE, GRID_SIZE))
                pg.draw.rect(screen, BOARD_BACKGROUND_COLOR, rect)

        apple.draw()
        snake.draw()

        pg.display.flip()
        clock.tick(SPEED)

    pg.quit()


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    for event in pg.event.get():
        if event.type == pg.QUIT:
            return False

        elif event.type == pg.KEYDOWN:
            game_object.set_next_direction(event.key)

    return True


if __name__ == '__main__':
    main()
