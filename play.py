import math
import random
import time
import pygame

pygame.init()

WIDTH, HEIGHT = 800, 600
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Aim Trainer - Enhanced UI")

TARGET_PADDING = 30
LIVES = 3
TOP_BAR_HEIGHT = 50
BG_COLOR_START = (10, 10, 50)
BG_COLOR_END = (0, 100, 200)

LABEL_FONT = pygame.font.Font(pygame.font.match_font('verdana', bold=True), 26)
BUTTON_FONT = pygame.font.Font(pygame.font.match_font('verdana', bold=True), 32)

difficulties = {
    "Easy": 800,
    "Medium": 600,
    "Hard": 400
}

TARGET_EVENT = pygame.USEREVENT


def draw_text(win, text, font, color, x, y, centered=False):
    label = font.render(text, True, color)
    if centered:
        x -= label.get_width() // 2
        y -= label.get_height() // 2
    win.blit(label, (x, y))


def draw_gradient_background(win):
    for y in range(HEIGHT):
        color = (
            BG_COLOR_START[0] + (BG_COLOR_END[0] - BG_COLOR_START[0]) * y // HEIGHT,
            BG_COLOR_START[1] + (BG_COLOR_END[1] - BG_COLOR_START[1]) * y // HEIGHT,
            BG_COLOR_START[2] + (BG_COLOR_END[2] - BG_COLOR_START[2]) * y // HEIGHT,
        )
        pygame.draw.line(win, color, (0, y), (WIDTH, y))


def draw_button(win, rect, color, text, hover=False):
    border_radius = 20  # Coins arrondis
    shadow_offset = 5 if not hover else 2

    pygame.draw.rect(win, (50, 50, 50), (rect.x + shadow_offset, rect.y + shadow_offset, rect.width, rect.height),
                     border_radius=border_radius)

    pygame.draw.rect(win, color, rect, border_radius=border_radius)

    draw_text(win, text, BUTTON_FONT, "black", rect.centerx, rect.centery, centered=True)


def difficulty_selection():
    selected_difficulty = None
    while selected_difficulty is None:
        WIN.fill((20, 20, 50))
        draw_text(WIN, "Select Difficulty", BUTTON_FONT, "white", WIDTH // 2, 100, centered=True)

        easy_button = pygame.Rect(WIDTH // 2 - 100, 200, 200, 50)
        medium_button = pygame.Rect(WIDTH // 2 - 100, 300, 200, 50)
        hard_button = pygame.Rect(WIDTH // 2 - 100, 400, 200, 50)

        mouse_pos = pygame.mouse.get_pos()

        draw_button(WIN, easy_button, "green", "Easy", easy_button.collidepoint(mouse_pos))
        draw_button(WIN, medium_button, "orange", "Medium", medium_button.collidepoint(mouse_pos))
        draw_button(WIN, hard_button, "red", "Hard", hard_button.collidepoint(mouse_pos))

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if easy_button.collidepoint(event.pos):
                    selected_difficulty = "Easy"
                elif medium_button.collidepoint(event.pos):
                    selected_difficulty = "Medium"
                elif hard_button.collidepoint(event.pos):
                    selected_difficulty = "Hard"

    return difficulties[selected_difficulty]


class Target:
    MAX_SIZE = 30
    GROWTH_RATE = 0.3

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.size = 0
        self.grow = True

    def update(self):
        if self.size + self.GROWTH_RATE >= self.MAX_SIZE:
            self.grow = False
        if self.grow:
            self.size += self.GROWTH_RATE
        else:
            self.size -= self.GROWTH_RATE

    def draw(self, win):
        glow = self.size * 1.8
        pygame.draw.circle(win, (255, 140, 0, 100), (self.x, self.y), glow)
        pygame.draw.circle(win, (255, 69, 58), (self.x, self.y), self.size)
        pygame.draw.circle(win, (255, 255, 255), (self.x, self.y), self.size * 0.8)

    def collide(self, x, y):
        """ Vérifie si le clic de la souris touche la cible """
        dis = math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)
        return dis <= self.size


def draw(win, targets, elapsed_time, targets_hit, misses):
    draw_gradient_background(win)
    for target in targets:
        target.draw(win)
    draw_top_bar(win, elapsed_time, targets_hit, misses)


def draw_top_bar(win, time_elapsed, targets_hit, misses):
    pygame.draw.rect(win, (0, 0, 0), (0, 0, WIDTH, TOP_BAR_HEIGHT))

    accuracy = (targets_hit / max(1, (targets_hit + misses))) * 100
    draw_text(win, f"Time: {int(time_elapsed)}s", LABEL_FONT, "white", 10, 10)
    draw_text(win, f"Hits: {targets_hit}", LABEL_FONT, "green", 200, 10)
    draw_text(win, f"Misses: {misses}", LABEL_FONT, "red", 350, 10)
    draw_text(win, f"Accuracy: {accuracy:.1f}%", LABEL_FONT, "yellow", 500, 10)


def main():
    global TARGET_INCREMENT
    TARGET_INCREMENT = difficulty_selection()
    run = True
    targets = []
    clock = pygame.time.Clock()

    targets_hit = 0
    clicks = 0
    misses = 0
    start_time = time.time()

    pygame.time.set_timer(TARGET_EVENT, TARGET_INCREMENT)

    while run:
        clock.tick(60)
        click = False
        mouse_pos = pygame.mouse.get_pos()
        elapsed_time = time.time() - start_time

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == TARGET_EVENT:
                x = random.randint(TARGET_PADDING, WIDTH - TARGET_PADDING)
                y = random.randint(TARGET_PADDING + TOP_BAR_HEIGHT, HEIGHT - TARGET_PADDING)
                targets.append(Target(x, y))
            if event.type == pygame.MOUSEBUTTONDOWN:
                click = True
                clicks += 1

        for target in targets[:]:
            target.update()
            if target.size <= 0:
                targets.remove(target)
                misses += 1
            if click and target.collide(*mouse_pos):
                targets.remove(target)
                targets_hit += 1

        if misses >= LIVES:
            run = False  # Quitter proprement si le joueur perd

        draw(WIN, targets, elapsed_time, targets_hit, misses)
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()
