import pygame
import sys
import random

# --- 메타데이터 ---
__title__ = 'Python Brick Breaker'
__version__ = '0.4.0' # 시작 화면 및 상태 관리 추가
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
YELLOW = (255, 215, 0)

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

    # 폰트 설정
    score_font = pygame.font.SysFont(None, 36)
    title_font = pygame.font.SysFont(None, 80) # 제목용 큰 폰트
    sub_font = pygame.font.SysFont(None, 40)   # 안내 문구용 중간 폰트

    paddle = Paddle()
    ball = Ball()
    
    bricks = []
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
    
    # [1] 게임 상태 변수: 'START', 'PLAYING', 'GAME_OVER'
    game_state = 'START'

    running = True
    while running:
        # 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # 키 입력 처리 (상태에 따라 다르게 동작)
            if event.type == pygame.KEYDOWN:
                # [대기 상태일 때] 스페이스바 누르면 게임 시작
                if game_state == 'START':
                    if event.key == pygame.K_SPACE:
                        game_state = 'PLAYING'
                
                # [게임 중일 때] 치트키 사용 가능
                elif game_state == 'PLAYING':
                    if event.key == pygame.K_c: # 치트키
                         for brick in bricks: brick.active = False
                
                # [게임 오버 상태일 때] 스페이스바 누르면 재시작 (1레벨부터)
                elif game_state == 'GAME_OVER':
                    if event.key == pygame.K_SPACE:
                        score = 0
                        level = 1
                        ball.reset(level)
                        bricks = create_bricks()
                        game_state = 'PLAYING'

        screen.fill(WHITE) # 배경 지우기

        # --- 상태별 화면 그리기 및 로직 ---

        if game_state == 'START':
            # [시작 화면]
            title_text = title_font.render("BRICK BREAKER", True, BLUE)
            start_text = sub_font.render("Press SPACE to Start", True, BLACK)
            
            # 중앙 정렬
            screen.blit(title_text, title_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 - 50)))
            screen.blit(start_text, start_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2 + 20)))

        elif game_state == 'PLAYING':
            # [게임 플레이 화면]
            paddle.move()
            
            # 공 움직임 체크
            if not ball.move():
                game_state = 'GAME_OVER' # 공 떨어지면 상태 변경
            
            # 충돌 로직
            if ball.rect.colliderect(paddle.rect):
                collision_rect = ball.rect.clip(paddle.rect)
                if collision_rect.width < collision_rect.height:
                    ball.dx *= -1 
                else:
                    ball.dy *= -1 
                    ball.rect.bottom = paddle.rect.top 

            for brick in bricks:
                if brick.active and ball.rect.colliderect(brick.rect):
                    brick.active = False
                    score += 10 + (level * 2)
                    
                    collision_rect = ball.rect.clip(brick.rect)
                    if collision_rect.width >= collision_rect.height:
                        ball.dy *= -1 
                    else:
                        ball.dx *= -1 
                    break 

            # 클리어 체크
            if all(not brick.active for brick in bricks):
                # 잠시 멈춤 효과 없이 바로 메시지 띄우고 싶다면 여기 로직 수정 가능
                # 현재는 화면 멈춤(delay) 사용
                screen.fill(WHITE)
                # 객체들 마지막 모습 그리기
                paddle.draw(screen)
                ball.draw(screen)
                for brick in bricks: brick.draw(screen)
                
                clear_text = title_font.render(f"STAGE {level} CLEAR!", True, BLUE)
                screen.blit(clear_text, clear_text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)))
                pygame.display.flip()
                
                pygame.time.delay(2000) # 2초 대기
                
                level += 1
                ball.reset(level)
                for brick in bricks: brick.active = True

            # 그리기
            paddle.draw(screen)
            ball.draw(screen)
            for brick in bricks: brick.draw(screen)
            
            # 점수판
            score_text = score_font.render(f"Score: {score}  Level: {level}", True, DARK_GRAY)
            screen.blit(score_text, (10, 10))

        elif game_state == 'GAME_OVER':
            # [게임 오버 화면]
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