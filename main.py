import pygame
import sys

# --- 메타데이터 ---
__title__ = 'Python Brick Breaker'
__version__ = '0.2.0' # 버전 업데이트!
__author__ = 'Python Developer'

# --- 설정 상수 ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 10
BALL_RADIUS = 10
BRICK_WIDTH = 75
BRICK_HEIGHT = 20
BRICK_ROWS = 5
BRICK_COLS = 10
FPS = 60

# 색상 (R, G, B)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
DARK_GRAY = (50, 50, 50) # 점수판 색상

# --- 클래스 정의 ---

class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2 - PADDLE_WIDTH // 2,
            SCREEN_HEIGHT - 40,
            PADDLE_WIDTH,
            PADDLE_HEIGHT
        )
        self.speed = 8

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < SCREEN_WIDTH:
            self.rect.x += self.speed

    def draw(self, screen):
        pygame.draw.rect(screen, BLUE, self.rect)

class Ball:
    def __init__(self):
        self.reset()

    def reset(self):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            BALL_RADIUS * 2,
            BALL_RADIUS * 2
        )
        self.dx = 4
        self.dy = -4

    def move(self):
        self.rect.x += self.dx
        self.rect.y += self.dy
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.dx *= -1
        if self.rect.top <= 0:
            self.dy *= -1
        if self.rect.bottom >= SCREEN_HEIGHT:
            return False 
        return True 

    def draw(self, screen):
        pygame.draw.circle(screen, RED, self.rect.center, BALL_RADIUS)

class Brick:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, BRICK_WIDTH, BRICK_HEIGHT)
        self.active = True

    def draw(self, screen):
        if self.active:
            pygame.draw.rect(screen, GREEN, self.rect)
            pygame.draw.rect(screen, BLACK, self.rect, 1)

# --- 메인 게임 함수 ---

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(f"{__title__} v{__version__}")
    clock = pygame.time.Clock()

    # [1] 폰트 설정
    score_font = pygame.font.SysFont(None, 36)

    paddle = Paddle()
    ball = Ball()
    
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            brick_x = 15 + col * (BRICK_WIDTH + 5)
            brick_y = 15 + row * (BRICK_HEIGHT + 5)
            bricks.append(Brick(brick_x, brick_y))
    
    # [2] 점수 변수
    score = 0

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        paddle.move()
        
        if not ball.move():
            print(f"Game Over! Final Score: {score}")
            ball.reset()
            score = 0 # 점수 초기화
            for brick in bricks: brick.active = True
        
        if ball.rect.colliderect(paddle.rect):
            ball.dy *= -1
        
        for brick in bricks:
            if brick.active and ball.rect.colliderect(brick.rect):
                brick.active = False
                ball.dy *= -1 
                # [3] 점수 증가
                score += 10
                break 

        if all(not brick.active for brick in bricks):
            print("You Win!")
            ball.reset()
            for brick in bricks: brick.active = True

        screen.fill(WHITE)
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)

        # [4] 점수 그리기
        score_text = score_font.render(f"Score: {score}", True, DARK_GRAY)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()