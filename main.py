import pygame
import sys
import random

# --- 메타데이터 ---
__title__ = 'Python Brick Breaker'
__version__ = '0.4.3' # 과거 위치 추적 물리 엔진 적용
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
        self.reset(1)

    def reset(self, level):
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 2,
            SCREEN_HEIGHT // 2,
            BALL_RADIUS * 2,
            BALL_RADIUS * 2
        )
        # [핵심] 이전 프레임의 위치를 저장할 변수
        self.prev_rect = self.rect.copy()
        
        # [버그 수정] 속도 제한으로 터널링 방지
        base_speed = min(4 + level, 6)  # 최대 속도를 6으로 제한 (패들 높이보다 작게)
        self.dx = random.choice([-base_speed, base_speed]) 
        self.dy = -base_speed 

    def move(self):
        # 움직이기 전에 현재 위치를 '과거 위치'로 저장
        self.prev_rect = self.rect.copy()
        
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
    title_font = pygame.font.SysFont(None, 80)
    sub_font = pygame.font.SysFont(None, 40)

    paddle = Paddle()
    ball = Ball()
    
    def create_bricks():
        new_bricks = []
        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                brick_x = 15 + col * (BRICK_WIDTH + 5)
                brick_y = 15 + row * (BRICK_HEIGHT + 5)
                new_bricks.append(Brick(brick_x, brick_y))
        return new_bricks

    bricks = create_bricks()
    
    score = 0
    level = 1
    game_state = 'START'

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            if event.type == pygame.KEYDOWN:
                if game_state == 'START':
                    if event.key == pygame.K_SPACE:
                        game_state = 'PLAYING'
                elif game_state == 'PLAYING':
                    if event.key == pygame.K_c: 
                         for brick in bricks: brick.active = False
                elif game_state == 'GAME_OVER':
                    if event.key == pygame.K_SPACE:
                        score = 0
                        level = 1
                        ball.reset(level)
                        bricks = create_bricks()
                        game_state = 'PLAYING'

        screen.fill(WHITE)

        if game_state == 'START':
            title_text = title_font.render("BRICK BREAKER", True, BLUE)
            start_text = sub_font.render("Press SPACE to Start", True, BLACK)
            screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)))
            screen.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20)))

        elif game_state == 'PLAYING':
            paddle.move()
            
            if not ball.move():
                game_state = 'GAME_OVER' 
            
            # [패들 충돌 로직 개선 - 정확한 반사 처리]
            if ball.rect.colliderect(paddle.rect):
                # 터널링 방지: 이전 프레임에서 이미 겹쳐있었는지 확인
                if not ball.prev_rect.colliderect(paddle.rect):
                    # 새로운 충돌 -> 반사 처리
                    # 공이 패들 위에 있으면 (y축으로 대부분 겹치면) 위에서 반사
                    if ball.rect.centery < paddle.rect.centery:
                        # 패들 윗면에서 반사
                        ball.dy = -abs(ball.dy)  # 음수로 설정 (위로 튕김)
                        ball.rect.bottom = paddle.rect.top  # 위치 보정
                    else:
                        # 패들 옆면에서 반사
                        ball.dx *= -1
                        if ball.rect.centerx < paddle.rect.centerx:
                             ball.rect.right = paddle.rect.left
                        else:
                             ball.rect.left = paddle.rect.right

            # [벽돌 충돌 로직 개선 - 관통 슛 버그 및 동시 충돌 무시 버그 해결]
            collided_bricks = []  # 이번 프레임에 충돌 처리한 벽돌들
            for brick in bricks:
                if brick.active and ball.rect.colliderect(brick.rect):
                    # [버그 수정] 이미 충돌 처리된 벽돌인지 확인 (동시 충돌 무시 해결)
                    if brick in collided_bricks:
                        continue
                    
                    # [버그 수정] 관통 슛 버그: 이전 프레임에서 벽돌과 겹쳐있었는지 확인
                    if ball.prev_rect.colliderect(brick.rect):
                        # 이미 겹쳐있던 상태 -> 새로운 충돌이 아님 (무시)
                        continue
                    
                    brick.active = False
                    collided_bricks.append(brick)
                    score += 10 + (level * 2)
                    
                    # [핵심 로직 개선] 겹침 거리로 정확한 충돌 면 판단
                    # 충돌 표면 계산 (어느 면과 충돌했는지 정확히 판정)
                    # 겹침 정도(penetration depth)를 각 방향별로 계산
                    overlap_top = ball.rect.bottom - brick.rect.top      # 위쪽 면
                    overlap_bottom = brick.rect.bottom - ball.rect.top   # 아래쪽 면
                    overlap_left = ball.rect.right - brick.rect.left     # 왼쪽 면
                    overlap_right = brick.rect.right - ball.rect.left    # 오른쪽 면
                    
                    # 가장 적은 겹침이 발생한 면이 실제 충돌한 면
                    min_overlap = min(overlap_top, overlap_bottom, overlap_left, overlap_right)
                    
                    if min_overlap == overlap_top and ball.dy > 0:  # 위에서 진입
                        ball.dy *= -1
                        ball.rect.bottom = brick.rect.top
                    elif min_overlap == overlap_bottom and ball.dy < 0:  # 아래에서 진입
                        ball.dy *= -1
                        ball.rect.top = brick.rect.bottom
                    elif min_overlap == overlap_left and ball.dx > 0:  # 왼쪽에서 진입
                        ball.dx *= -1
                        ball.rect.right = brick.rect.left
                    elif min_overlap == overlap_right and ball.dx < 0:  # 오른쪽에서 진입
                        ball.dx *= -1
                        ball.rect.left = brick.rect.right

            if all(not brick.active for brick in bricks):
                screen.fill(WHITE)
                clear_text = title_font.render(f"STAGE {level} CLEAR!", True, BLUE)
                screen.blit(clear_text, clear_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
                pygame.display.flip()
                pygame.time.delay(2000)
                level += 1
                ball.reset(level)
                bricks = create_bricks() 

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