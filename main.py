import pygame
import sys
import random

# --- 메타데이터 ---
__title__ = 'Python Brick Breaker'
__version__ = '1.0.0' # 정식 배포 버전
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

# --- 헬퍼 함수 ---

def create_bricks():
    """초기 벽돌 배치를 생성하여 리스트로 반환합니다."""
    new_bricks = []
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            brick_x = 15 + col * (BRICK_WIDTH + 5)
            brick_y = 15 + row * (BRICK_HEIGHT + 5)
            new_bricks.append(Brick(brick_x, brick_y))
    return new_bricks

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
        self.reset(1)

    def reset(self, level):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            BALL_RADIUS * 2,
            BALL_RADIUS * 2
        )
        # 물리 계산을 위한 이전 프레임 위치 저장
        self.prev_rect = self.rect.copy()
        
        # 속도 설정 (최대 속도를 6으로 제한하여 터널링 방지)
        base_speed = min(4 + level, 6)
        self.dx = random.choice([-base_speed, base_speed]) 
        self.dy = -base_speed 

    def move(self):
        # 이동 전 현재 위치 저장
        self.prev_rect = self.rect.copy()
        
        self.rect.x += self.dx
        self.rect.y += self.dy
        
        # 벽 충돌 처리
        if self.rect.left <= 0 or self.rect.right >= SCREEN_WIDTH:
            self.dx *= -1
        if self.rect.top <= 0:
            self.dy *= -1
            
        # 바닥 충돌 (게임 오버)
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

    # 폰트 설정
    score_font = pygame.font.SysFont(None, 36)
    title_font = pygame.font.SysFont(None, 80)
    sub_font = pygame.font.SysFont(None, 40)

    # 객체 생성
    paddle = Paddle()
    ball = Ball()
    bricks = create_bricks() # 함수 분리로 깔끔해짐
    
    score = 0
    level = 1
    game_state = 'START'

    running = True
    while running:
        # 1. 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game_state == 'START':
                    if event.key == pygame.K_SPACE:
                        game_state = 'PLAYING'
                
                elif game_state == 'PLAYING':
                    if event.key == pygame.K_c: # 개발자 치트키
                         for brick in bricks: brick.active = False
                
                elif game_state == 'GAME_OVER':
                    if event.key == pygame.K_SPACE:
                        score = 0
                        level = 1
                        ball.reset(level)
                        bricks = create_bricks()
                        game_state = 'PLAYING'

        screen.fill(WHITE)

        # 2. 상태별 로직 및 그리기
        if game_state == 'START':
            title_text = title_font.render("BRICK BREAKER", True, BLUE)
            start_text = sub_font.render("Press SPACE to Start", True, BLACK)
            screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)))
            screen.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20)))

        elif game_state == 'PLAYING':
            paddle.move()
            
            if not ball.move():
                game_state = 'GAME_OVER' 
            
            # --- 패들 충돌 처리 ---
            if ball.rect.colliderect(paddle.rect):
                # 이전 프레임 위치를 확인하여 터널링 방지
                if not ball.prev_rect.colliderect(paddle.rect):
                    # 공이 위에서 내려올 때 (y축 중심 비교)
                    if ball.rect.centery < paddle.rect.centery:
                        ball.dy = -abs(ball.dy) # 무조건 위로 반사
                        ball.rect.bottom = paddle.rect.top 
                    else:
                        # 옆면 충돌
                        ball.dx *= -1
                        if ball.rect.centerx < paddle.rect.centerx:
                             ball.rect.right = paddle.rect.left
                        else:
                             ball.rect.left = paddle.rect.right

            # --- 벽돌 충돌 처리 ---
            collided_bricks = []
            for brick in bricks:
                if brick.active and ball.rect.colliderect(brick.rect):
                    # 이미 처리된 벽돌이거나, 이전 프레임부터 겹쳐있던 경우 무시
                    if brick in collided_bricks:
                        continue
                    if ball.prev_rect.colliderect(brick.rect):
                        continue
                    
                    brick.active = False
                    collided_bricks.append(brick)
                    score += 10 + (level * 2)
                    
                    # 겹침 깊이(penetration depth) 계산으로 정확한 충돌 면 판정
                    overlap_top = ball.rect.bottom - brick.rect.top
                    overlap_bottom = brick.rect.bottom - ball.rect.top
                    overlap_left = ball.rect.right - brick.rect.left
                    overlap_right = brick.rect.right - ball.rect.left
                    
                    min_overlap = min(overlap_top, overlap_bottom, overlap_left, overlap_right)
                    
                    if min_overlap == overlap_top and ball.dy > 0:
                        ball.dy *= -1
                        ball.rect.bottom = brick.rect.top
                    elif min_overlap == overlap_bottom and ball.dy < 0:
                        ball.dy *= -1
                        ball.rect.top = brick.rect.bottom
                    elif min_overlap == overlap_left and ball.dx > 0:
                        ball.dx *= -1
                        ball.rect.right = brick.rect.left
                    elif min_overlap == overlap_right and ball.dx < 0:
                        ball.dx *= -1
                        ball.rect.left = brick.rect.right

            # 스테이지 클리어 체크
            if all(not brick.active for brick in bricks):
                screen.fill(WHITE)
                clear_text = title_font.render(f"STAGE {level} CLEAR!", True, BLUE)
                screen.blit(clear_text, clear_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
                pygame.display.flip()
                
                pygame.time.delay(2000)
                
                level += 1
                ball.reset(level)
                bricks = create_bricks() 

            # 화면 그리기
            paddle.draw(screen)
            ball.draw(screen)
            for brick in bricks: brick.draw(screen)
            score_text = score_font.render(f"Score: {score}  Level: {level}", True, DARK_GRAY)
            screen.blit(score_text, (10, 10))

        elif game_state == 'GAME_OVER':
            over_text = title_font.render("GAME OVER", True, RED)
            score_msg = sub_font.render(f"Final Score: {score}", True, BLACK)
            retry_text = sub_font.render("Press SPACE to Retry", True, DARK_GRAY)
            screen.blit(over_text, over_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 60)))
            screen.blit(score_msg, score_msg.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
            screen.blit(retry_text, retry_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 50)))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()