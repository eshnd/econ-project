import pygame
import time
import sys
import random

pygame.init()

WIDTH, HEIGHT = 650, 450
screen = pygame.display.set_mode((WIDTH, HEIGHT))

WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)
RED = (200, 0, 0)

clock = pygame.time.Clock()
FPS = 60

NPCs = pygame.sprite.Group()
companies = pygame.sprite.Group()
stations = pygame.sprite.Group()
platforms = pygame.sprite.Group()
all_sprites = pygame.sprite.Group()

OSCALE = 2
health = 3
max_health = 3
score = 0
score_popup = ""
score_popup_timer = 0

PLAYER_WIDTH, PLAYER_HEIGHT = 34 * OSCALE, 34 * OSCALE
GRAVITY = 0.5
JUMP_POWER = 15
HSCALE = (21 * OSCALE, 30 * OSCALE)
HOFFSET = 20

station_freeze = 0
frozen_station = None
last_nestle_hit = 0
station_message = ""
station_message_timer = 0
npc_freeze_timer = 0 


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h):
        super().__init__()
        grass_img = pygame.image.load("./grass.png").convert_alpha()
        grass_img = pygame.transform.scale(grass_img, (w, h))
        self.image = grass_img
        self.rect = self.image.get_rect(topleft=(x, y))


class NPC(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("./homeless.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, HSCALE)
        self.rect = self.image.get_rect(topleft=(x, y))

    def hit(self):
        print("i have been hit")
        self.image.fill(GREEN, None, pygame.BLEND_RGBA_MULT)
        global NPCs, npc_freeze_timer, score, score_popup, score_popup_timer
        NPCs.remove(self)
        npc_freeze_timer = 120 
        score += 100
        score_popup = "+100"
        score_popup_timer = 60


class Nestle(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("./nestle.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (300 * 2.5, 197 * 2.5))
        self.rect = self.image.get_rect(topleft=(x, y))


class Station(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("./charity.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (199, 97))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.frozen = False

    def hit(self):
        global station_freeze, frozen_station, health, station_message, station_message_timer
        if station_freeze == 0 and not self.frozen:
            print("frozen for 3 seconds")
            station_freeze = 180
            frozen_station = self
            self.frozen = True
            self.image.fill(GREEN, None, pygame.BLEND_RGBA_MULT)
            health = max_health
            station_message = random.choice([
                "The Facing Hunger Foodbank brings volunteers, donors, and agencies together to feed nearly 130,000 people per year in several counties across the US.",
                "You can help people in need by volunteering for or donating to the Facing Hunger Foodbank!",
                "The Facing Hunger food bank is on a mission to feed people struggling with food insecurity by distributing nutritious food and groceries through our vast agency network."
            ])
            station_message_timer = 240


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.image.load("./player.png").convert_alpha()
        self.image = pygame.transform.scale(self.image, (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.vel_y = 0
        self.player_side = "right"
        self.on_platform = False
        self.prev_rect = self.rect.copy()

    def update(self, platforms, NPCs=[], companies=[], stations=[]):
        global health, station_freeze, last_nestle_hit, npc_freeze_timer

        keys = pygame.key.get_pressed()
        self.prev_rect = self.rect.copy()

        if station_freeze == 0 and npc_freeze_timer == 0:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.rect.x -= 5
                if self.player_side != "left":
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.player_side = "left"
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.rect.x += 5
                if self.player_side != "right":
                    self.image = pygame.transform.flip(self.image, True, False)
                    self.player_side = "right"

        self.vel_y += GRAVITY
        self.rect.y += self.vel_y
        self.on_platform = False

        hits = pygame.sprite.spritecollide(self, platforms, False)
        for platform in hits:
            if self.prev_rect.bottom <= platform.rect.top <= self.rect.bottom:
                self.rect.bottom = platform.rect.top
                self.vel_y = 0
                self.on_platform = True

        nhits = pygame.sprite.spritecollide(self, NPCs, False)
        for npc in nhits:
            npc.hit()

        shits = pygame.sprite.spritecollide(self, stations, False)
        for st in shits:
            if self.prev_rect.bottom <= st.rect.top <= self.rect.bottom:
                self.rect.bottom = st.rect.top
                self.vel_y = 0
                self.on_platform = True
                st.hit()

        chits = pygame.sprite.spritecollide(self, companies, False)
        for company in chits:
            now = time.time()
            if now - last_nestle_hit >= 1:
                health -= 3
                last_nestle_hit = now
                print(f"health: {health}")

        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_platform and station_freeze == 0 and npc_freeze_timer == 0:
            self.vel_y = -JUMP_POWER
            self.on_platform = False

        if self.rect.right < 0:
            self.rect.left = WIDTH
        if self.rect.left > WIDTH:
            self.rect.right = 0


def spawn_platform_row(y):
    global platform_counter
    platform_width = random.randint(80, 120)
    platform_height = 20
    x = random.randint(0, WIDTH - platform_width)
    platform_counter += 1

    if platform_counter % 8 == 0:
        s = Station(x, y - 20)
        stations.add(s)
        all_sprites.add(s)
    else:
        p = Platform(x, y, platform_width, platform_height)
        platforms.add(p)
        all_sprites.add(p)

        if platform_counter % random.randint(3, 5) == 0:
            npc_x = x + (platform_width // 2) - (HSCALE[0] // 2)
            npc_y = y - HSCALE[1]
            n = NPC(npc_x, npc_y)
            NPCs.add(n)
            all_sprites.add(n)


def draw_wrapped_text(surface, text, font, color, x, y, max_width):
    words = text.split(" ")
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    for i, line in enumerate(lines):
        rendered = font.render(line, True, color)
        rect = rendered.get_rect(center=(x, y + i * font.get_height()))
        surface.blit(rendered, rect)


def init_game():
    global c, player, camera_offset_y, platform_counter, last_platform_y, score, score_popup, score_popup_timer
    NPCs.empty()
    stations.empty()
    platforms.empty()
    all_sprites.empty()
    companies.empty()

    c = Nestle((WIDTH / 2) - (300 * 1.25), 600)
    companies.add(c)
    all_sprites.add(c)

    player.rect.topleft = (WIDTH // 2, HEIGHT - 100)
    player.vel_y = 0
    all_sprites.add(player)

    camera_offset_y = 0
    platform_counter = 0
    last_platform_y = HEIGHT - 20
    score = 0
    score_popup = ""
    score_popup_timer = 0

    ground = Platform(0, HEIGHT, WIDTH, 20)
    platforms.add(ground)
    all_sprites.add(ground)

    for i in range(10):
        spawn_platform_row(last_platform_y - 100 * (i + 1))
    last_platform_y -= 100 * 10


player = Player(WIDTH // 2, HEIGHT - 100)
all_sprites.add(player)
init_game()

running = True
idx = 0
font = pygame.font.SysFont("Arial", 24)

while running:
    idx += 1

    distance = player.rect.top - c.rect.bottom
    speed = 1 + min(max(distance / 1000, 0), 0.5)  
    if idx % 2 == 0:
        c.rect.y -= speed

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    player.update(platforms, NPCs, companies, stations)

    if player.rect.top < HEIGHT // 3:
        camera_offset_y = HEIGHT // 3 - player.rect.top
    else:
        camera_offset_y = 0

    while last_platform_y > player.rect.top - 600:
        spawn_platform_row(last_platform_y - 100)
        last_platform_y -= 100

    if station_freeze > 0:
        station_freeze -= 1
        if station_freeze == 0 and frozen_station:
            stations.remove(frozen_station)
            all_sprites.remove(frozen_station)
            frozen_station = None
            player.vel_y = -JUMP_POWER

    if npc_freeze_timer > 0:
        npc_freeze_timer -= 1

    for npc in list(NPCs):
        if npc.rect.top + camera_offset_y > HEIGHT:
            health -= 1
            NPCs.remove(npc)
            all_sprites.remove(npc)

    score = max(score, -(player.rect.y - HEIGHT))

    screen.fill((161, 197, 255))
    for sprite in all_sprites:
        offset_rect = sprite.rect.copy()
        offset_rect.y += camera_offset_y
        screen.blit(sprite.image, offset_rect)

    bar_width, bar_height = 150, 30
    bar_x = WIDTH - bar_width - 20
    bar_y = 20
    pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
    inner_width = int((health / max_health) * (bar_width - 4))
    pygame.draw.rect(screen, RED, (bar_x + 2, bar_y + 2, inner_width, bar_height - 4))
    text_surface = font.render("health", True, BLACK)
    text_rect = text_surface.get_rect(center=(bar_x + bar_width // 2, bar_y + bar_height // 2))
    screen.blit(text_surface, text_rect)

    score_surface = font.render(f"score: {score}", True, BLACK)
    score_rect = score_surface.get_rect(topleft=(20, 20))
    screen.blit(score_surface, score_rect)

    if station_message_timer > 0:
        draw_wrapped_text(screen, station_message, font, BLACK, WIDTH // 2, 60, WIDTH - bar_width - 40)
        station_message_timer -= 1

    if score_popup_timer > 0:
        popup_surface = font.render(score_popup, True, BLACK)
        popup_rect = popup_surface.get_rect(center=(WIDTH // 2, 100))
        screen.blit(popup_surface, popup_rect)
        score_popup_timer -= 1

    if health <= 0:
        screen.fill((161, 197, 255))
        draw_wrapped_text(screen, "game over :(", font, BLACK, WIDTH // 2, 60, WIDTH - bar_width - 40)
        score_surface = font.render(f"final score: {score}", True, BLACK)
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 120))
        screen.blit(score_surface, score_rect)
        restart_rect = pygame.Rect(WIDTH // 2 - 60, HEIGHT // 2, 120, 40)
        pygame.draw.rect(screen, BLUE, restart_rect)
        text_surf = font.render("RESTART", True, WHITE)
        text_rect = text_surf.get_rect(center=restart_rect.center)
        screen.blit(text_surf, text_rect)
        pygame.display.flip()

        waiting_restart = True
        while waiting_restart:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if restart_rect.collidepoint(event.pos):
                        health = max_health
                        npc_freeze_timer = 0
                        station_freeze = 0
                        frozen_station = None
                        player.vel_y = -JUMP_POWER
                        station_message = ""
                        station_message_timer = 0
                        init_game()
                        waiting_restart = False
        continue

    pygame.display.flip()

pygame.quit()
sys.exit()
