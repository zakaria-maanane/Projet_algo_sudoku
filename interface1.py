import pygame
import sys

# === Couleurs ===
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (66, 133, 244)
GREEN = (52, 168, 83)
RED = (200, 0, 0)

# === Fonction pour dessiner la grille ===
def draw_grid(win, sudoku, top_left_x, top_left_y, label, elapsed_time, font, small_font):
    cell_size = 50

    # Titre au-dessus
    label_surf = font.render(label, True, BLACK)
    win.blit(label_surf, (top_left_x, top_left_y - 40))

    # Grille
    for i in range(10):
        line_width = 3 if i % 3 == 0 else 1
        pygame.draw.line(win, BLACK, (top_left_x, top_left_y + i * cell_size),
                         (top_left_x + 9 * cell_size, top_left_y + i * cell_size), line_width)
        pygame.draw.line(win, BLACK, (top_left_x + i * cell_size, top_left_y),
                         (top_left_x + i * cell_size, top_left_y + 9 * cell_size), line_width)

    # Chiffres
    for i in range(9):
        for j in range(9):
            num = sudoku.grid[i][j]
            if num != 0:
                color = BLUE if sudoku.original_grid[i][j] == num else GREEN
                text = font.render(str(num), True, color)
                text_rect = text.get_rect(center=(top_left_x + j * cell_size + 25,
                                                  top_left_y + i * cell_size + 25))
                win.blit(text, text_rect)

    # Temps affiché à droite
    time_text = small_font.render(f"Temps : {elapsed_time:.4f} s", True, BLACK)
    time_x = top_left_x + 9 * cell_size + 30
    time_y = top_left_y + 9 * cell_size // 2 - 10
    win.blit(time_text, (time_x, time_y))

# === Fonction pour dessiner un bouton cliquable ===
def draw_button(win, text, x, y, w, h, font, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    pygame.draw.rect(win, RED, (x, y, w, h), border_radius=8)

    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        if click[0] == 1 and action:
            pygame.time.delay(200)
            action()

    text_surf = font.render(text, True, WHITE)
    text_rect = text_surf.get_rect(center=(x + w // 2, y + h // 2))
    win.blit(text_surf, text_rect)

# === Fonction principale d'affichage ===
def launch_interface(sudoku, elapsed_time, method_name, solved):
    pygame.init()
    WIDTH, HEIGHT = 900, 700
    win = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Sudoku Résolu - {method_name}")

    font = pygame.font.SysFont("comicsans", 30)
    small_font = pygame.font.SysFont("comicsans", 24)

    running = True

    def exit_program():
        nonlocal running
        running = False

    while running:
        win.fill(WHITE)

        if solved:
            draw_grid(win, sudoku, 80, 100, method_name, elapsed_time, font, small_font)
        else:
            msg = font.render(f"{method_name} : échec", True, RED)
            win.blit(msg, (150, 250))
            time_text = small_font.render(f"Temps : {elapsed_time:.4f} s", True, BLACK)
            win.blit(time_text, (200, 300))

        # Utilise exit_program au lieu de pygame.quit
        draw_button(win, "Quitter", 375, 570, 150, 40, font, action=exit_program)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.update()

    pygame.quit()
    sys.exit()
