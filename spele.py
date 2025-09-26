import pygame, sys, random, time

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 1024, 768
HUD_HEIGHT = 80
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pac-Man Style Scooter Escape")

FPS = 60
FramePerSec = pygame.time.Clock()

# Krāsas
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
YELLOW = (255, 255, 0)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)  # Enemy iestrēgšanas indikators

font = pygame.font.SysFont("Verdana", 30)

score = 0
last_score_time = time.time()
start_time = time.time()

pac_map = [
    "1111111111111111111111",
    "1000000000100000000001",
    "1011110110101111011101",
    "1010000100001000010101",
    "1010111111101111010101",
    "1000100000000001000101",
    "1111111111111111111111"
]

ROWS = len(pac_map)
COLS = len(pac_map[0])
TILE_SIZE_W = SCREEN_WIDTH // COLS
TILE_SIZE_H = (SCREEN_HEIGHT - HUD_HEIGHT) // ROWS
TILE_SIZE = min(TILE_SIZE_W, TILE_SIZE_H)

obstacles = []
for r_idx, row in enumerate(pac_map):
    for c_idx, tile in enumerate(row):
        if tile == "1":
            obstacles.append(pygame.Rect(c_idx*TILE_SIZE, r_idx*TILE_SIZE + HUD_HEIGHT, TILE_SIZE, TILE_SIZE))

dots = []
for r_idx, row in enumerate(pac_map):
    for c_idx, tile in enumerate(row):
        if tile == "0":
            dots.append(pygame.Rect(
                c_idx*TILE_SIZE + TILE_SIZE//2 -5,
                r_idx*TILE_SIZE + HUD_HEIGHT + TILE_SIZE//2 -5,
                10,10
            ))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.color = RED
        self.image = pygame.Surface((TILE_SIZE-10, TILE_SIZE-10))
        self.image.fill(self.color)
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.speed = 4

    def move(self, player, others):
        # pamata virziens uz player
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        move_options = [(self.speed,0),(-self.speed,0),(0,self.speed),(0,-self.speed)]
        random.shuffle(move_options)  # neliels randomness, lai neiestrēgtu

        moved = False
        for mx,my in sorted(move_options, key=lambda d: (d[0]-dx)**2 + (d[1]-dy)**2):
            new_rect = self.rect.move(mx,my)
            if any(new_rect.colliderect(ob) for ob in obstacles):
                continue
            if any(new_rect.colliderect(o.rect) for o in others if o!=self):
                continue
            self.rect = new_rect
            moved = True
            break

        # ja nevar kustēties → iestrēgšanas indikators
        self.color = RED if moved else GREEN
        self.image.fill(self.color)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE-10, TILE_SIZE-10))
        self.image.fill(BLUE)
        self.rect = self.image.get_rect()
        self.rect.center = (TILE_SIZE*2 + TILE_SIZE//2, HUD_HEIGHT + TILE_SIZE*5 + TILE_SIZE//2)
        self.speed = 12

    def update(self):
        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]:
            dx = -self.speed
        if keys[pygame.K_RIGHT]:
            dx = self.speed
        if keys[pygame.K_UP]:
            dy = -self.speed
        if keys[pygame.K_DOWN]:
            dy = self.speed

        # Player pārvietošanās + collisions ar sienām
        self.rect.x += dx
        if any(self.rect.colliderect(ob) for ob in obstacles):
            self.rect.x -= dx
        self.rect.y += dy
        if any(self.rect.colliderect(ob) for ob in obstacles):
            self.rect.y -= dy

    def draw(self, surface):
        surface.blit(self.image, self.rect)

P1 = Player()
enemies = [
    Enemy(TILE_SIZE*10 + TILE_SIZE//2, HUD_HEIGHT + TILE_SIZE*1 + TILE_SIZE//2),
    Enemy(TILE_SIZE*15 + TILE_SIZE//2, HUD_HEIGHT + TILE_SIZE*1 + TILE_SIZE//2),
    Enemy(TILE_SIZE*10 + TILE_SIZE//2, HUD_HEIGHT + TILE_SIZE*4 + TILE_SIZE//2)
]

PAUSED = False

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                PAUSED = not PAUSED

    if not PAUSED:
        DISPLAYSURF.fill(GRAY)
        pygame.draw.rect(DISPLAYSURF, WHITE, (0, HUD_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT-HUD_HEIGHT))

        # Update player
        P1.update()
        P1.draw(DISPLAYSURF)

        # Obstacles
        for ob in obstacles:
            pygame.draw.rect(DISPLAYSURF, BLACK, ob)

        # Dots
        for dot in dots:
            pygame.draw.ellipse(DISPLAYSURF, YELLOW, dot)

        # Savāc dotus
        for dot in dots[:]:
            if P1.rect.colliderect(dot):
                dots.remove(dot)
                score += 1

        # Update enemies
        for e in enemies:
            e.move(P1, enemies)
            e.draw(DISPLAYSURF)

        # Score ik pēc 10 sek
        if time.time() - last_score_time >= 10:
            score += 1
            last_score_time = time.time()

        # Timer
        elapsed_time = int(time.time() - start_time)
        timer_surf = font.render(f"Time: {elapsed_time}s", True, BLACK)
        score_surf = font.render(f"Score: {score}", True, BLACK)
        DISPLAYSURF.blit(score_surf, (20, 10))
        DISPLAYSURF.blit(timer_surf, (SCREEN_WIDTH - timer_surf.get_width() - 20, 10))

        # Sadursmes ar enemy
        for e in enemies:
            if P1.rect.colliderect(e.rect):
                if P1.rect.bottom <= e.rect.top + 10:
                    e.rect.topleft = (random.randint(TILE_SIZE, SCREEN_WIDTH-50), random.randint(HUD_HEIGHT+TILE_SIZE, SCREEN_HEIGHT-50))
                else:
                    score = 0
                    P1.rect.center = (TILE_SIZE*2 + TILE_SIZE//2, HUD_HEIGHT + TILE_SIZE*5 + TILE_SIZE//2)
                    start_time = time.time()
                    # Reset enemy pozīcijas
                    for en in enemies:
                        en.rect.topleft = (random.randint(TILE_SIZE, SCREEN_WIDTH-50), random.randint(HUD_HEIGHT+TILE_SIZE, SCREEN_HEIGHT-50))
                    # Reset dots
                    dots = []
                    for r_idx, row in enumerate(pac_map):
                        for c_idx, tile in enumerate(row):
                            if tile == "0":
                                dots.append(pygame.Rect(
                                    c_idx*TILE_SIZE + TILE_SIZE//2 -5,
                                    r_idx*TILE_SIZE + HUD_HEIGHT + TILE_SIZE//2 -5,
                                    10,10
                                ))
                    break
    else:
        pause_surf = font.render("PAUSE - Press ESC to resume", True, RED)
        DISPLAYSURF.blit(pause_surf, (SCREEN_WIDTH//2 - pause_surf.get_width()//2, SCREEN_HEIGHT//2))

    pygame.display.update()
    FramePerSec.tick(FPS)



