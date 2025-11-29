import pygame
import sys
import random

# --- 메타데이터 ---
__title__ = 'Python Brick Breaker'
__version__ = '0.3.0' # 레벨 시스템 추가
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
YELLOW = (255, 255, 0) # 텍스트 강조용

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
        self.reset(1) # 레벨 1 속도로 시작

    # [변경] 레벨에 따라 공 속도가 빨라짐
    def reset(self, level):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            BALL_RADIUS * 2,
            BALL_RADIUS * 2
        )
        
        # 기본 속도 4 + 레벨당 1씩 증가 (예: 레벨 1=5, 레벨 2=6...)
        base_speed = 4 + level 
        
        self.dx = random.choice([-base_speed, base_speed]) 
        self.dy = -base_speed 

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

    # 폰트 설정 (점수용, 큰 메시지용)
    score_font = pygame.font.SysFont(None, 36)
    large_font = pygame.font.SysFont(None, 72) # 승리/패배 메시지용 큰 폰트

    paddle = Paddle()
    ball = Ball()
    
    bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            brick_x = 15 + col * (BRICK_WIDTH + 5)
            brick_y = 15 + row * (BRICK_HEIGHT + 5)
            bricks.append(Brick(brick_x, brick_y))
    
    score = 0
    level = 1 # [추가] 레벨 변수

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        paddle.move()
        
        if not ball.move():
            # 게임 오버 시 처리
            screen.fill(WHITE)
            text = large_font.render("GAME OVER", True, RED)
            # 화면 중앙에 배치
            text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(text, text_rect)
            pygame.display.flip()
            
            pygame.time.delay(2000) # 2초 대기
            
            # 초기화
            score = 0
            level = 1
            ball.reset(level)
            for brick in bricks: brick.active = True
        
        # 패들 충돌
        if ball.rect.colliderect(paddle.rect):
            collision_rect = ball.rect.clip(paddle.rect)
            if collision_rect.width < collision_rect.height:
                ball.dx *= -1 
            else:
                ball.dy *= -1 
                ball.rect.bottom = paddle.rect.top 

        # 벽돌 충돌
        for brick in bricks:
            if brick.active and ball.rect.colliderect(brick.rect):
                brick.active = False
                score += 10 + (level * 2) # 레벨이 높으면 점수도 더 줌
                
                collision_rect = ball.rect.clip(brick.rect)
                if collision_rect.width >= collision_rect.height:
                    ball.dy *= -1 
                else:
                    ball.dx *= -1 
                break 

        # [승리 조건 체크: 모든 벽돌이 깨졌는가?]
        if all(not brick.active for brick in bricks):
            # 1. 화면에 클리어 메시지 표시
            screen.fill(WHITE)
            clear_text = large_font.render(f"STAGE {level} CLEAR!", True, BLUE)
            text_rect = clear_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))
            screen.blit(clear_text, text_rect)
            pygame.display.flip()
            
            # 2. 2초간 멈춤 (플레이어가 성취감을 느낄 시간)
            pygame.time.delay(2000)
            
            # 3. 레벨 업 및 난이도 상승
            level += 1
            ball.reset(level) # 속도가 빨라진 공으로 리셋
            
            # 4. 벽돌 재생성
            for brick in bricks: brick.active = True

        screen.fill(WHITE)
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)

        # 점수 및 레벨 표시
        score_text = score_font.render(f"Score: {score}  Level: {level}", True, DARK_GRAY)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()