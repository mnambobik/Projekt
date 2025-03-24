import random
import sys
import pygame
import sqlite3
from pygame.locals import *

# Nastavení okna
window_width = 600
window_height = 499
window = pygame.display.set_mode((window_width, window_height))  # Vytvoření herního okna
game_images = {}  # Slovník pro uložení obrázků
framepersecond = 32  # Počet snímků za sekundu

# Cesty k obrázkům
pipeimage = 'images/pipe.png'
background_image = 'images/background.jpg'
birdplayer_image = 'images/bird.png'

# Inicializace Pygame a fontu
pygame.init()
font = pygame.font.SysFont('Arial', 36)  # Font pro texty
game_over_font = pygame.font.SysFont('Arial', 48, bold=True)  # Font pro text "GAME OVER"

# Cesta k databázi SQLite
db_file = 'highscore.db'

# Funkce pro vytvoření databáze a tabulky
def create_db():
    conn = sqlite3.connect(db_file)  # Připojení k databázi
    cursor = conn.cursor()  # Vytvoření kurzoru pro SQL dotazy
    cursor.execute('''CREATE TABLE IF NOT EXISTS highscore (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        score INTEGER NOT NULL
                      )''')  # Vytvoření tabulky pro skóre
    conn.commit()  # Uložení změn
    conn.close()  # Zavření spojení

# Funkce pro získání 5 nejlepších skóre
def get_top_scores(limit=5):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f'SELECT score FROM highscore ORDER BY score DESC LIMIT {limit}')  # Výběr 5 nejlepších skóre
    scores = cursor.fetchall()  # Načtení výsledků
    conn.close()
    return [score[0] for score in scores]  # Vrácení listu skóre

# Funkce pro uložení skóre do databáze
def save_score(score):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO highscore (score) VALUES (?)', (score,))  # Vložení nového skóre
    conn.commit()
    conn.close()

# Funkce pro zobrazení úvodní obrazovky
def show_start_screen():
    """Zobrazí úvodní obrazovku a čeká na stisk ENTER pro start."""
    window.blit(game_images['background'], (0, 0))  # Zobrazení pozadí
    title_text = game_over_font.render("FLAPPY BIRD", True, (255, 255, 0))  # Zobrazení názvu hry
    start_text = font.render("Press ENTER to Start", True, (255, 255, 255))  # Zobrazení pokynu pro start

    # Vykreslení textů na obrazovku
    window.blit(title_text, (window_width // 2 - title_text.get_width() // 2, 150))
    window.blit(start_text, (window_width // 2 - start_text.get_width() // 2, 250))
    pygame.display.update()

    # Smyčka čekající na stisknutí klávesy
    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_RETURN:  # Stisk ENTER
                return

# Funkce pro zobrazení GAME OVER obrazovky
def show_game_over(your_score):
    """Zobrazí GAME OVER a umožní restart nebo ukončení s černým transparentním pozadím."""
    window.fill((0, 0, 0))  # Vyplnění okna černou barvou
    
    # Vytvoření černého overlay s transparentností (alpha)
    overlay = pygame.Surface((window_width, window_height))
    overlay.set_alpha(150)  # Nastavení transparentnosti (0-255)
    overlay.fill((0, 0, 0))  # Černá barva
    window.blit(overlay, (0, 0))  # Zobrazí overlay na celé obrazovce

    # Zobrazí "GAME OVER"
    text = game_over_font.render("GAME OVER", True, (255, 0, 0))  # Červený text pro GAME OVER
    score_text = font.render(f"Final Score: {your_score}", True, (255, 255, 255))  # Zobrazení výsledku
    top_scores_text = font.render(f"Top Scores:", True, (255, 255, 255))  # Zobrazení nápisu pro Top skóre
    restart_text = font.render("Press R to Restart or Esc to Exit", True, (200, 200, 200))  # Pokyn pro restart nebo exit

    # Vykreslení textů na obrazovku
    window.blit(text, (window_width // 2 - text.get_width() // 2, 150))
    window.blit(score_text, (window_width // 2 - score_text.get_width() // 2, 220))
    window.blit(top_scores_text, (window_width // 2 - top_scores_text.get_width() // 2, 270))

    # Zobrazíme 5 nejlepších skóre
    top_scores = get_top_scores()
    for i, score in enumerate(top_scores):
        score_text = font.render(f"{i+1}. {score}", True, (255, 255, 255))  # Zobrazení každého skóre
        window.blit(score_text, (window_width // 2 - score_text.get_width() // 2, 320 + i * 40))

    window.blit(restart_text, (window_width // 2 - restart_text.get_width() // 2, 400))  # Pokyn pro restart
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and event.key == K_r:
                return  # Restart hry

# Hlavní herní smyčka
def flappygame():
    """Hlavní herní smyčka."""
    your_score = 0
    horizontal = int(window_width / 5)
    vertical = int(window_width / 2)

    first_pipe = createPipe()
    second_pipe = createPipe()

    down_pipes = [
        {'x': window_width + 300, 'y': first_pipe[1]['y']},
        {'x': window_width + 300 + (window_width / 2), 'y': second_pipe[1]['y']},
    ]
    up_pipes = [
        {'x': window_width + 300, 'y': first_pipe[0]['y']},
        {'x': window_width + 300 + (window_width / 2), 'y': second_pipe[0]['y']},
    ]

    pipeVelX = -4
    bird_velocity_y = -9
    bird_Max_Vel_Y = 10
    birdAccY = 1
    bird_flap_velocity = -8
    bird_flapped = False

    while True:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()
            if event.type == KEYDOWN and (event.key == K_SPACE or event.key == K_UP):
                if vertical > 0:
                    bird_velocity_y = bird_flap_velocity
                    bird_flapped = True

        if isGameOver(horizontal, vertical, up_pipes, down_pipes):
            # Animace pádu ptáka před zobrazením GAME OVER
            while vertical < window_height - game_images['flappybird'].get_height():
                vertical += 5  # Rychlost pádu (lze upravit)
                window.blit(game_images['background'], (0, 0))
                for upperPipe, lowerPipe in zip(up_pipes, down_pipes):
                    window.blit(game_images['pipe'][0], (upperPipe['x'], upperPipe['y']))
                    window.blit(game_images['pipe'][1], (lowerPipe['x'], lowerPipe['y']))
                window.blit(game_images['flappybird'], (horizontal, vertical))
                pygame.display.update()
                framepersecond_clock.tick(framepersecond)

            save_score(your_score)  # Uloží skóre do databáze
            show_game_over(your_score)  # Zobrazí GAME OVER obrazovku s top 5
            return

        playerMidPos = horizontal + game_images['flappybird'].get_width() / 2
        for pipe in up_pipes:
            pipeMidPos = pipe['x'] + game_images['pipe'][0].get_width() / 2
            if pipeMidPos <= playerMidPos < pipeMidPos + 4:
                your_score += 1

        if bird_velocity_y < bird_Max_Vel_Y and not bird_flapped:
            bird_velocity_y += birdAccY

        bird_flapped = False
        playerHeight = game_images['flappybird'].get_height()
        vertical += min(bird_velocity_y, window_height - vertical - playerHeight)

        for upperPipe, lowerPipe in zip(up_pipes, down_pipes):
            upperPipe['x'] += pipeVelX
            lowerPipe['x'] += pipeVelX

        if 0 < up_pipes[0]['x'] < 5:
            newpipe = createPipe()
            up_pipes.append(newpipe[0])
            down_pipes.append(newpipe[1])

        if up_pipes[0]['x'] < -game_images['pipe'][0].get_width():
            up_pipes.pop(0)
            down_pipes.pop(0)

        window.blit(game_images['background'], (0, 0))
        for upperPipe, lowerPipe in zip(up_pipes, down_pipes):
            window.blit(game_images['pipe'][0], (upperPipe['x'], upperPipe['y']))
            window.blit(game_images['pipe'][1], (lowerPipe['x'], lowerPipe['y']))

        window.blit(game_images['flappybird'], (horizontal, vertical))

        score_text = font.render(f"Score: {your_score}", True, (255, 255, 255))  # Zobrazení skóre
        window.blit(score_text, (window_width - score_text.get_width() - 20, 20))

        pygame.display.update()
        framepersecond_clock.tick(framepersecond)

# Kontrola kolize
def isGameOver(horizontal, vertical, up_pipes, down_pipes):
    """Kontrola, zda došlo ke kolizi s trubkou nebo okrajem obrazovky."""
    if vertical + game_images['flappybird'].get_height() >= window_height or vertical < 0:
        return True
    for pipe in up_pipes:
        if vertical < pipe['y'] + game_images['pipe'][0].get_height() and abs(horizontal - pipe['x']) < game_images['pipe'][0].get_width():
            return True
    for pipe in down_pipes:
        if vertical + game_images['flappybird'].get_height() > pipe['y'] and abs(horizontal - pipe['x']) < game_images['pipe'][0].get_width():
            return True
    return False

# Vytvoření trubky
def createPipe():
    """Vytvoří novou trubku (horní a dolní) na obrazovce."""
    offset = window_height / 3
    y2 = offset + random.randrange(0, int(window_height - 1.2 * offset))
    pipeX = window_width + 10
    y1 = game_images['pipe'][0].get_height() - y2 + offset
    return [{'x': pipeX, 'y': -y1}, {'x': pipeX, 'y': y2}]

if __name__ == "__main__":
    create_db()  # Inicializace databáze
    pygame.init()
    framepersecond_clock = pygame.time.Clock()
    pygame.display.set_caption('Flappy Bird Game')

    # Načítání a úprava obrázků
    game_images['flappybird'] = pygame.image.load(birdplayer_image).convert_alpha()
    game_images['flappybird'] = pygame.transform.scale(game_images['flappybird'], (50, 35))

    game_images['background'] = pygame.image.load(background_image).convert_alpha()
    game_images['background'] = pygame.transform.scale(game_images['background'], (window_width, window_height))

    game_images['pipe'] = (
        pygame.transform.scale(pygame.transform.rotate(pygame.image.load(pipeimage).convert_alpha(), 180), (70, 300)),
        pygame.transform.scale(pygame.image.load(pipeimage).convert_alpha(), (70, 300))
    )

    show_start_screen()  # Úvodní obrazovka
    while True:
        flappygame()  # Hlavní herní smyčka

#1234568