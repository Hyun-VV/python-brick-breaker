import pygame
import sys

# --- 메타데이터 ---
__title__ = 'Python Brick Breaker'
__version__ = '0.2.2' # 인덱스 버그 수정
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
DARK_GRAY = (50, 50, 50)

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
        self.dx = 5 
        self.dy = -5

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

    score_font = pygame.font.SysFont(None, 36)

    paddle = Paddle()
    ball = Ball()
    
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            brick_x = 15 + col * (BRICK_WIDTH + 5)
            brick_y = 15 + row * (BRICK_HEIGHT + 5)
            bricks.append(Brick(brick_x, brick_y))
    
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
            score = 0 
            for brick in bricks: brick.active = True
        
        # [패들 충돌 로직]
        if ball.rect.colliderect(paddle.rect):
            collision_rect = ball.rect.clip(paddle.rect)
            
            if collision_rect.width < collision_rect.height:
                ball.dx *= -1 # 옆면
            else:
                ball.dy *= -1 # 윗면
                ball.rect.bottom = paddle.rect.top 

        # [수정된 벽돌 충돌 로직]
        # 반복문을 직접 돌면서 정확한 벽돌 객체를 찾습니다.
        for brick in bricks:
            if brick.active and ball.rect.colliderect(brick.rect):
                # 충돌 발생!
                brick.active = False
                score += 10
                
                # 물리 반사 계산 (v0.2.1의 로직을 여기로 가져옴)
                collision_rect = ball.rect.clip(brick.rect)
                
                if collision_rect.width >= collision_rect.height:
                    ball.dy *= -1 # 위아래 충돌
                else:
                    ball.dx *= -1 # 옆면 충돌
                
                break # 한 프레임에 벽돌 하나만 깨지도록 루프 종료

        if all(not brick.active for brick in bricks):
            print("You Win!")
            ball.reset()
            for brick in bricks: brick.active = True

        screen.fill(WHITE)
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)

        score_text = score_font.render(f"Score: {score}", True, DARK_GRAY)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()