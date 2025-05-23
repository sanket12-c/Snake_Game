import pygame
import sys
import random
import math

pygame.init()

# Set fullscreen mode and get display size
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()

# Adjust screen size to multiples of SNAKE_SIZE for grid alignment
SNAKE_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // SNAKE_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // SNAKE_SIZE
SCREEN_WIDTH = GRID_WIDTH * SNAKE_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * SNAKE_SIZE

BLACK = pygame.Color(0, 0, 0)
WHITE = pygame.Color(255, 255, 255)
GRAY = pygame.Color(120, 120, 120)
LIGHT_GRAY = pygame.Color(200, 200, 200)
DARK_GRAY = pygame.Color(30, 30, 30)
BLUE = pygame.Color(0, 120, 215)
RED = pygame.Color(255, 0, 0)
RED_DARK = pygame.Color(160, 0, 0)
YELLOW = pygame.Color(240, 230, 140)
GREEN_OPTIONS = [
    ("Classic Green", pygame.Color(0, 170, 0), pygame.Color(0, 230, 0)),
    ("Bright Lime", pygame.Color(50, 205, 50), pygame.Color(102, 255, 102)),
    ("Teal", pygame.Color(0, 128, 128), pygame.Color(64, 224, 208)),
    ("Orange", pygame.Color(255, 140, 0), pygame.Color(255, 165, 79)),
]

# Default settings
default_speed_index = 1  # Index for speed options
SPEED_OPTIONS = [6, 8, 10, 12, 14, 16, 18, 20]

pygame.display.set_caption('Snake Game - Fullscreen Mode')

clock = pygame.time.Clock()

font_title = pygame.font.SysFont('arial', 36, bold=True)
font_style = pygame.font.SysFont('arial', 25)
score_font = pygame.font.SysFont('consolas', 20)
popup_font = pygame.font.SysFont('arial', 22, bold=True)
small_font = pygame.font.SysFont('arial', 18)
button_font = pygame.font.SysFont('arial', 20, bold=True)

best_score = 0


def draw_text_center(surface, text, font, color, center):
    s = font.render(text, True, color)
    rect = s.get_rect(center=center)
    surface.blit(s, rect)


def draw_button(surface, rect, text, active=False):
    color = BLUE if active else GRAY
    pygame.draw.rect(surface, color, rect, border_radius=6)
    txt_surf = button_font.render(text, True, WHITE)
    txt_rect = txt_surf.get_rect(center=rect.center)
    surface.blit(txt_surf, txt_rect)


def draw_score(score):
    score_surf = score_font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_surf, (10, 10))


def start_menu_popup():
    global best_score
    popup_width = 380
    popup_height = 320
    popup_x = (SCREEN_WIDTH - popup_width) // 2
    popup_y = (SCREEN_HEIGHT - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

    button_width = 180
    button_height = 50
    spacing = 15
    play_button_rect = pygame.Rect(popup_x + (popup_width - button_width) // 2,
                                   popup_y + 120, button_width, button_height)
    settings_button_rect = pygame.Rect(popup_x + (popup_width - button_width) // 2,
                                       popup_y + 120 + button_height + spacing, button_width, button_height)
    exit_button_rect = pygame.Rect(popup_x + (popup_width - button_width) // 2,
                                   popup_y + 120 + 2 * (button_height + spacing), button_width, button_height)

    selected_button = 0  # 0=Play, 1=Settings, 2=Exit

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_UP, pygame.K_LEFT):
                    selected_button = (selected_button - 1) % 3
                elif event.key in (pygame.K_DOWN, pygame.K_RIGHT, pygame.K_TAB):
                    selected_button = (selected_button + 1) % 3
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if selected_button == 0:
                        return 'play'
                    elif selected_button == 1:
                        return 'settings'
                    elif selected_button == 2:
                        pygame.quit()
                        sys.exit()

        # Draw background & popup
        screen.fill(BLACK)
        pygame.draw.rect(screen, DARK_GRAY, popup_rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, popup_rect, 3, border_radius=12)

        # Title
        draw_text_center(screen, "Snake Game", font_title, GREEN_OPTIONS[default_speed_index][1], (SCREEN_WIDTH // 2, popup_y + 50))

        # Best score
        draw_text_center(screen, f"Best Score: {best_score}", font_style, WHITE, (SCREEN_WIDTH // 2, popup_y + 90))

        # Buttons
        draw_button(screen, play_button_rect, "Play", selected_button == 0)
        draw_button(screen, settings_button_rect, "Settings", selected_button == 1)
        draw_button(screen, exit_button_rect, "Exit", selected_button == 2)

        # Highlight button on mouse hover
        for idx, btn in enumerate([play_button_rect, settings_button_rect, exit_button_rect]):
            if btn.collidepoint(mouse_pos):
                selected_button = idx
                if mouse_clicked:
                    if selected_button == 0:
                        return 'play'
                    elif selected_button == 1:
                        return 'settings'
                    elif selected_button == 2:
                        pygame.quit()
                        sys.exit()

        pygame.display.update()
        clock.tick(30)


def settings_popup(current_color_index, current_speed_index):
    popup_width = 500
    popup_height = 350
    popup_x = (SCREEN_WIDTH - popup_width) // 2
    popup_y = (SCREEN_HEIGHT - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

    button_width = 140
    button_height = 45
    spacing = 10

    close_button_rect = pygame.Rect(popup_x + (popup_width - button_width) // 2,
                                    popup_y + popup_height - button_height - 20, button_width, button_height)

    # Snake color selection buttons rects
    snake_colors_rects = []
    color_button_size = 40
    color_start_x = popup_x + 40
    color_start_y = popup_y + 90
    color_spacing = 70
    for i in range(len(GREEN_OPTIONS)):
        r = pygame.Rect(color_start_x + i * color_spacing, color_start_y, color_button_size, color_button_size)
        snake_colors_rects.append(r)

    # Speed slider parameters
    speed_slider_rect = pygame.Rect(popup_x + 40, popup_y + 200, popup_width - 80, 40)
    slider_knob_radius = 12

    selected_color = current_color_index
    selected_speed = current_speed_index

    dragging = False

    while True:
        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True
                if speed_slider_rect.collidepoint(mouse_pos):
                    dragging = True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                dragging = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return selected_color, selected_speed

        # Handle dragging slider knob
        if dragging:
            x = max(speed_slider_rect.left, min(mouse_pos[0], speed_slider_rect.right))
            relative_x = x - speed_slider_rect.left
            n_positions = len(SPEED_OPTIONS) - 1
            selected_speed = round(relative_x / (speed_slider_rect.width / n_positions))

        screen.fill(BLACK)
        pygame.draw.rect(screen, DARK_GRAY, popup_rect, border_radius=12)
        pygame.draw.rect(screen, WHITE, popup_rect, 3, border_radius=12)

        draw_text_center(screen, "Settings", font_title, WHITE, (SCREEN_WIDTH // 2, popup_y + 50))

        label_color = small_font.render("Snake Color:", True, WHITE)
        screen.blit(label_color, (popup_x + 40, popup_y + 60))

        for i, r in enumerate(snake_colors_rects):
            color = GREEN_OPTIONS[i][1]
            pygame.draw.rect(screen, color, r, border_radius=5)
            if i == selected_color:
                pygame.draw.rect(screen, YELLOW, r, 4, border_radius=5)
            else:
                pygame.draw.rect(screen, WHITE, r, 2, border_radius=5)

        label_speed = small_font.render("Snake Speed:", True, WHITE)
        screen.blit(label_speed, (popup_x + 40, popup_y + 170))

        pygame.draw.rect(screen, GRAY, speed_slider_rect, border_radius=10)
        n_positions = len(SPEED_OPTIONS)
        interval = speed_slider_rect.width / (n_positions - 1)
        for i in range(n_positions):
            x = speed_slider_rect.left + i * interval
            line_height = 15
            pygame.draw.line(screen, WHITE, (x, speed_slider_rect.centery - line_height // 2),
                             (x, speed_slider_rect.centery + line_height // 2), 2)
            speed_text = small_font.render(str(SPEED_OPTIONS[i]), True, WHITE)
            txt_rect = speed_text.get_rect(center=(x, speed_slider_rect.centery + 25))
            screen.blit(speed_text, txt_rect)

        knob_x = speed_slider_rect.left + selected_speed * interval
        knob_y = speed_slider_rect.centery
        pygame.draw.circle(screen, BLUE, (int(knob_x), knob_y), slider_knob_radius)
        pygame.draw.circle(screen, WHITE, (int(knob_x), knob_y), slider_knob_radius, 2)

        for i, r in enumerate(snake_colors_rects):
            if r.collidepoint(mouse_pos):
                if mouse_clicked:
                    selected_color = i

        draw_button(screen, close_button_rect, "Close", close_button_rect.collidepoint(mouse_pos))
        if mouse_clicked and close_button_rect.collidepoint(mouse_pos):
            return selected_color, selected_speed

        pygame.display.update()
        clock.tick(30)


def draw_cylindrical_segment(surface, pos, radius, base_color, light_color):
    x, y = pos
    pygame.draw.circle(surface, base_color, (x + radius, y + radius), radius)
    highlight_rect = pygame.Rect(x + radius // 2, y + radius // 3, radius * 1.5, radius)
    pygame.draw.ellipse(surface, light_color, highlight_rect)


def draw_snake_head(surface, pos, radius, direction, base_color, light_color):
    x, y = pos
    center = (x + radius, y + radius)
    eye_color = WHITE
    pupil_color = BLACK

    pygame.draw.circle(surface, base_color, center, radius)
    highlight_rect = pygame.Rect(x + radius // 2, y + radius // 3, radius * 1.5, radius)
    pygame.draw.ellipse(surface, light_color, highlight_rect)

    eye_radius = radius // 5
    pupil_radius = eye_radius // 2

    offset = radius // 2
    if direction == 'UP':
        eye_pos_l = (center[0] - offset, center[1] - offset // 2)
        eye_pos_r = (center[0] + offset, center[1] - offset // 2)
    elif direction == 'DOWN':
        eye_pos_l = (center[0] - offset, center[1] + offset // 2)
        eye_pos_r = (center[0] + offset, center[1] + offset // 2)
    elif direction == 'LEFT':
        eye_pos_l = (center[0] - offset, center[1] - offset // 2)
        eye_pos_r = (center[0] - offset, center[1] + offset // 2)
    else:  # RIGHT
        eye_pos_l = (center[0] + offset, center[1] - offset // 2)
        eye_pos_r = (center[0] + offset, center[1] + offset // 2)

    pygame.draw.circle(surface, eye_color, eye_pos_l, eye_radius)
    pygame.draw.circle(surface, eye_color, eye_pos_r, eye_radius)
    pygame.draw.circle(surface, pupil_color, eye_pos_l, pupil_radius)
    pygame.draw.circle(surface, pupil_color, eye_pos_r, pupil_radius)

    tongue_length = radius
    tongue_width = radius // 5
    tongue_color = RED_DARK
    if direction == 'UP':
        tongue_start = (center[0], y)
        tongue_end_l = (center[0] - tongue_width, y - tongue_length)
        tongue_end_r = (center[0] + tongue_width, y - tongue_length)
    elif direction == 'DOWN':
        tongue_start = (center[0], y + 2 * radius)
        tongue_end_l = (center[0] - tongue_width, y + 2 * radius + tongue_length)
        tongue_end_r = (center[0] + tongue_width, y + 2 * radius + tongue_length)
    elif direction == 'LEFT':
        tongue_start = (x, center[1])
        tongue_end_l = (x - tongue_length, center[1] - tongue_width)
        tongue_end_r = (x - tongue_length, center[1] + tongue_width)
    else:  # RIGHT
        tongue_start = (x + 2 * radius, center[1])
        tongue_end_l = (x + 2 * radius + tongue_length, center[1] - tongue_width)
        tongue_end_r = (x + 2 * radius + tongue_length, center[1] + tongue_width)

    pygame.draw.line(surface, tongue_color, tongue_start, tongue_end_l, 3)
    pygame.draw.line(surface, tongue_color, tongue_start, tongue_end_r, 3)


def draw_heart(surface, pos, size):
    x, y = pos
    top_curve_radius = size // 4
    bottom_point = (x + size // 2, y + size)

    path = []
    for t in range(0, 21):
        theta = math.pi * t / 20
        px = x + top_curve_radius - top_curve_radius * math.cos(theta)
        py = y + top_curve_radius * math.sin(theta)
        path.append((px, py))
    path.append(bottom_point)
    for t in range(20, -1, -1):
        theta = math.pi * t / 20
        px = x + 3 * top_curve_radius + top_curve_radius * math.cos(theta)
        py = y + top_curve_radius * math.sin(theta)
        path.append((px, py))

    pygame.draw.polygon(surface, RED, path)


def game_over_popup(score):
    popup_width = 340
    popup_height = 180
    popup_x = (SCREEN_WIDTH - popup_width) // 2
    popup_y = (SCREEN_HEIGHT - popup_height) // 2
    popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

    button_width = 130
    button_height = 45
    play_button_rect = pygame.Rect(
        popup_x + 30, popup_y + popup_height - button_height - 30,
        button_width, button_height)
    exit_button_rect = pygame.Rect(
        popup_x + popup_width - button_width - 30, popup_y + popup_height - button_height - 30,
        button_width, button_height)

    option_selected = 0  # 0 = Play Again, 1 = Exit

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_TAB):
                    option_selected = 1 - option_selected
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if option_selected == 0:
                        return True
                    else:
                        pygame.quit()
                        sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = event.pos
                if play_button_rect.collidepoint(mouse_pos):
                    return True
                if exit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

        translucent = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        translucent.set_alpha(180)
        translucent.fill(DARK_GRAY)
        screen.blit(translucent, (0, 0))

        pygame.draw.rect(screen, BLACK, popup_rect, border_radius=10)
        pygame.draw.rect(screen, WHITE, popup_rect, 2, border_radius=10)

        game_over_text = font_style.render('Game Over!', True, RED)
        score_text = font_style.render(f'Score: {score}', True, WHITE)
        screen.blit(game_over_text, (popup_x + popup_width // 2 - game_over_text.get_width() // 2, popup_y + 30))
        screen.blit(score_text, (popup_x + popup_width // 2 - score_text.get_width() // 2, popup_y + 70))

        draw_button(screen, play_button_rect, 'Play Again', option_selected == 0)
        draw_button(screen, exit_button_rect, 'Exit', option_selected == 1)

        pygame.display.update()
        clock.tick(30)


def game_loop(snake_base_color, snake_light_color, speed):
    global best_score
    # Start centered snake on grid
    snake_pos = [GRID_WIDTH // 2 * SNAKE_SIZE, GRID_HEIGHT // 2 * SNAKE_SIZE]
    snake_body = [[snake_pos[0], snake_pos[1]]]

    def spawn_food():
        while True:
            x = random.randint(0, GRID_WIDTH - 1) * SNAKE_SIZE
            y = random.randint(0, GRID_HEIGHT - 1) * SNAKE_SIZE
            if [x, y] not in snake_body:
                return [x, y]

    food_pos = spawn_food()
    food_spawn = True

    direction = 'RIGHT'
    change_to = direction

    score = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and direction != 'DOWN':
                    change_to = 'UP'
                elif event.key == pygame.K_DOWN and direction != 'UP':
                    change_to = 'DOWN'
                elif event.key == pygame.K_LEFT and direction != 'RIGHT':
                    change_to = 'LEFT'
                elif event.key == pygame.K_RIGHT and direction != 'LEFT':
                    change_to = 'RIGHT'

        direction = change_to

        if direction == 'UP':
            snake_pos[1] -= SNAKE_SIZE
        elif direction == 'DOWN':
            snake_pos[1] += SNAKE_SIZE
        elif direction == 'LEFT':
            snake_pos[0] -= SNAKE_SIZE
        elif direction == 'RIGHT':
            snake_pos[0] += SNAKE_SIZE

        snake_body.insert(0, list(snake_pos))

        if snake_pos == food_pos:
            score += 1
            food_spawn = False
        else:
            snake_body.pop()

        if not food_spawn:
            food_pos = spawn_food()
            food_spawn = True

        screen.fill(BLACK)

        radius = SNAKE_SIZE // 2
        for segment in snake_body[1:]:
            draw_cylindrical_segment(screen, segment, radius, snake_base_color, snake_light_color)

        draw_snake_head(screen, snake_body[0], radius, direction, snake_base_color, snake_light_color)

        draw_heart(screen, food_pos, SNAKE_SIZE)

        # Check for hitting boundaries
        if (snake_pos[0] < 0 or snake_pos[0] >= SCREEN_WIDTH or
                snake_pos[1] < 0 or snake_pos[1] >= SCREEN_HEIGHT):
            break

        # Check self collision
        if snake_pos in snake_body[1:]:
            break

        draw_score(score)

        pygame.display.update()
        clock.tick(speed)

    if score > best_score:
        best_score = score

    return game_over_popup(score)


def main():
    global default_speed_index
    snake_color_idx = 0
    snake_speed_idx = default_speed_index

    while True:
        action = start_menu_popup()
        if action == 'play':
            base, light = GREEN_OPTIONS[snake_color_idx][1], GREEN_OPTIONS[snake_color_idx][2]
            play_again = game_loop(base, light, SPEED_OPTIONS[snake_speed_idx])
            if not play_again:
                break
        elif action == 'settings':
            cidx, sidx = settings_popup(snake_color_idx, snake_speed_idx)
            snake_color_idx, snake_speed_idx = cidx, sidx

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

