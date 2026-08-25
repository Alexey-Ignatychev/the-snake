from random import randint

import pygame

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

# Скорость движения змейки:
SPEED = 10

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


# Тут опишите все классы игры.
class GameObject:
    """Родительский класс."""

    def __init__(self):
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = (255, 255, 255)

    def draw(self):
        """Пустой метод."""
        pass


class Apple(GameObject):
    """
    Класс отвечающий за отрисовку и
    генерацию координат появления яблока.
    """

    def __init__(self):
        super().__init__()
        self.body_color = APPLE_COLOR

    def randomize_position(self):
        """Генерирует случайные координаты для яблока."""
        cell_count_x = randint(0, (SCREEN_WIDTH // GRID_SIZE) - 1)
        cell_count_y = randint(0, (SCREEN_HEIGHT // GRID_SIZE) - 1)
        spawn_x = cell_count_x * GRID_SIZE
        spawn_y = cell_count_y * GRID_SIZE
        self.position = (spawn_x, spawn_y)

    def draw(self):
        """Отрисовывает яблоко."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)


class Snake(GameObject):
    """
    Класс отвечающий за движения
    и отрисовку змейки.
    """

    def __init__(self):
        super().__init__()
        start_x = SCREEN_WIDTH // 2
        start_y = (SCREEN_HEIGHT // 2) - GRID_SIZE
        self.positions = [(start_x, start_y)]
        self.length = 1
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None
        self.score = 0

    def move(self, apple):
        """Добавляет клеточку змейки в направлении движения
        и удаляет последнюю плюс добовляет координаты в positions
        при росте.
        """
        current_head = self.get_head_position()
        head_x = (
            current_head[0] + self.direction[0] * GRID_SIZE
        ) % SCREEN_WIDTH
        head_y = (
            current_head[1] + self.direction[1] * GRID_SIZE
        ) % SCREEN_HEIGHT
        new_head = (head_x, head_y)
        self.positions.insert(0, new_head)
        if new_head == apple.position:
            self.length += 1
            # pass
        if len(self.positions) > self.length:
            self.last = self.positions.pop()

    def update_direction(self):
        """
        Обновляет координаты появления головы змейки
        после выбора направления.
        """
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def draw(self):
        """Отрисовывает все сегменты змейки."""
        for position in self.positions[1:]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)
        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

    def get_head_position(self):
        """Возвращает координат первого сегмента списка (головы)."""
        return self.positions[0]

    def reset(self):
        """Сбрасывает змею в начальное положение и состояние."""
        start_x = SCREEN_WIDTH // 2
        start_y = (SCREEN_HEIGHT // 2) - GRID_SIZE
        self.positions = [(start_x, start_y)]
        self.direction = RIGHT
        self.next_direction = None
        self.length = 1
        self.score = 0
        self.last = None


def main():
    """Основная функция отвечающая за логику игры"""
    # Инициализация PyGame:
    pygame.init()
    # Тут нужно создать экземпляры классов.
    snake = Snake()
    apple = Apple()
    apple.randomize_position()
    running = True
    while running:
        handle_keys(snake)
        # Тут опишите основную логику игры.
        snake.update_direction()
        snake.move(apple)
        head_pos = snake.get_head_position()
        # укус яблока
        if head_pos == apple.position:
            snake.score += 1
            WIN_SCORE = 50
            if snake.score >= WIN_SCORE:
                print(f'ПОЗДРАВЛЯЮ! Вы набрали {snake.score} очков и победил!')
                snake.reset()
                apple.randomize_position()
                snake.score = 0
                continue
            while True:
                apple.randomize_position()
                if apple.position not in snake.positions:
                    break
        # укус питона
        if head_pos in snake.positions[1:]:
            print(f'Игра окончена! Змея укусила себя. Счет: {snake.score}.')
            snake.reset()
            apple.randomize_position()
            snake.score = 0
            continue

        screen.fill(BOARD_BACKGROUND_COLOR)
        snake.draw()
        apple.draw()
        pygame.display.update()

        clock.tick(SPEED)


def handle_keys(game_object):
    """Функция обработки действий пользователя"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if (
                event.key == pygame.K_UP
                and game_object.direction != DOWN
            ):
                game_object.next_direction = UP
            elif (
                event.key == pygame.K_DOWN
                and game_object.direction != UP
            ):
                game_object.next_direction = DOWN
            elif (
                event.key == pygame.K_LEFT
                and game_object.direction != RIGHT
            ):
                game_object.next_direction = LEFT
            elif (
                event.key == pygame.K_RIGHT
                and game_object.direction != LEFT
            ):
                game_object.next_direction = RIGHT


if __name__ == '__main__':
    main()
