import pygame
import random
import math

# Game dimensions
WIDTH = 640
HEIGHT = 480

# Colors
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)

# Paddle dimensions
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 20
PADDLE_SPEED = 5
MAX_PADDLE_SPEED = 2

# Ball dimensions and speed
BALL_RADIUS = 10
BALL_SPEED_Y = 3
BALL_SPEED_X_CHOICES = [-2, -1, 0, 1, 2]

# Brick dimensions
BRICK_WIDTH = 60
BRICK_HEIGHT = 20
BRICK_ROWS = 5
BRICK_COLS = 10

BALL_SPEED_X_MAX = 2

NUM_PADDLE_PARTS = 5

# Reward
REWARD = -1

# Initialize Pygame
pygame.init()
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Breakout")

clock = pygame.time.Clock()

def reset_game():
    # Initialize paddle
    paddle_x = (WIDTH - PADDLE_WIDTH) // 2
    paddle_y = HEIGHT - PADDLE_HEIGHT - 10
    paddle_speed = 0

    # Initialize ball
    ball_x = random.randint(0, WIDTH - BALL_RADIUS)
    ball_y = HEIGHT // 2
    ball_speed_x = random.choice(BALL_SPEED_X_CHOICES)
    ball_speed_y = random.uniform(-1, -5)  # Randomly select one of five directions directed upwards

    # Create bricks
    bricks = reset_bricks()

    return paddle_x, paddle_y, paddle_speed, ball_x, ball_y, ball_speed_x, ball_speed_y, bricks

def reset_bricks():
    bricks = []
    total_width = BRICK_COLS * BRICK_WIDTH
    initial_x = (WIDTH - total_width) // 2
    initial_y = 50
    for row in range(BRICK_ROWS):
        for col in range(BRICK_COLS):
            brick_x = initial_x + col * BRICK_WIDTH
            brick_y = initial_y + row * BRICK_HEIGHT
            bricks.append(pygame.Rect(brick_x, brick_y, BRICK_WIDTH, BRICK_HEIGHT))
    return bricks

def draw_elements(paddle_x, paddle_y, ball_x, ball_y, bricks):
    # Clear the screen
    window.fill(BLACK)

    # Draw paddle, ball, and bricks
    pygame.draw.rect(window, ORANGE, (paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT))
    pygame.draw.circle(window, RED, (ball_x, ball_y), BALL_RADIUS)
    for brick in bricks:
        pygame.draw.rect(window, GREEN, brick)
        pygame.draw.rect(window, BLACK, brick, 2)  # Add black outline to bricks

    # Update the display
    pygame.display.flip()

def move_paddle(paddle_x, paddle_speed):
    paddle_x += paddle_speed
    if paddle_x < 0:
        paddle_x = 0
    if paddle_x > WIDTH - PADDLE_WIDTH:
        paddle_x = WIDTH - PADDLE_WIDTH
    return paddle_x

def move_ball(ball_x, ball_y, ball_speed_x, ball_speed_y):
    ball_x += ball_speed_x
    ball_y += ball_speed_y
    return ball_x, ball_y

def check_wall_collision(ball_x, ball_y, ball_speed_x, ball_speed_y):
    if ball_x - BALL_RADIUS <= 0 or ball_x + BALL_RADIUS >= WIDTH:
        ball_speed_x *= -1
    if ball_y - BALL_RADIUS <= 0:
        ball_speed_y *= -1
    return ball_speed_x, ball_speed_y

def check_paddle_collision(ball_x, ball_y, ball_speed_x, ball_speed_y, paddle_x, paddle_y):
    paddle_rect = pygame.Rect(paddle_x, paddle_y, PADDLE_WIDTH, PADDLE_HEIGHT)
    ball_rect = pygame.Rect(ball_x - BALL_RADIUS, ball_y - BALL_RADIUS, BALL_RADIUS * 2, BALL_RADIUS * 2)
    if ball_rect.colliderect(paddle_rect):
        ball_speed_y *= -1

        # Calculate the reflection angle based on the direction of the ball's incoming velocity
        if ball_speed_x < 0:
            angle = -math.pi / 4  # Reflect to the left
        else:
            angle = math.pi / 4  # Reflect to the right

        ball_speed_x = math.sin(angle) * BALL_SPEED_X_MAX

        # Adjust the ball's horizontal direction if it's in contact with both paddle and wall
        if (ball_speed_x < 0 and ball_x + BALL_RADIUS >= paddle_x + PADDLE_WIDTH) or (ball_speed_x > 0 and ball_x - BALL_RADIUS <= paddle_x):
            ball_speed_x *= -1

        # Adjust the ball's vertical direction to prevent sticking
        if ball_speed_y > 0:
            ball_speed_y = -BALL_SPEED_Y

    return ball_speed_x, ball_speed_y

def check_brick_collision(ball_x, ball_y, ball_speed_x, ball_speed_y, bricks):
    for brick in bricks:
        if brick.collidepoint(ball_x + ball_speed_x, ball_y):  # Check horizontal collision
            bricks.remove(brick)
            ball_speed_x *= -1
            return ball_speed_x, ball_speed_y, REWARD, bricks
        elif brick.collidepoint(ball_x, ball_y + ball_speed_y):  # Check vertical collision
            bricks.remove(brick)
            ball_speed_y *= -1
            return ball_speed_x, ball_speed_y, REWARD, bricks
    return ball_speed_x, ball_speed_y, 0, bricks

def update_game_state(action, paddle_x, paddle_speed, ball_x, ball_y, ball_speed_x, ball_speed_y, bricks):
    if action == -1:
        paddle_speed = max(paddle_speed - 1, -MAX_PADDLE_SPEED)
    elif action == 1:
        paddle_speed = min(paddle_speed + 1, MAX_PADDLE_SPEED)
    else:
        paddle_speed = 0

    paddle_x = move_paddle(paddle_x, paddle_speed)
    ball_x, ball_y = move_ball(ball_x, ball_y, ball_speed_x, ball_speed_y)
    ball_speed_x, ball_speed_y = check_wall_collision(ball_x, ball_y, ball_speed_x, ball_speed_y)
    ball_speed_x, ball_speed_y = check_paddle_collision(ball_x, ball_y, ball_speed_x, ball_speed_y, paddle_x, paddle_y)
    ball_speed_x, ball_speed_y, reward, bricks = check_brick_collision(ball_x, ball_y, ball_speed_x, ball_speed_y, bricks)

    if ball_y >= HEIGHT:
        bricks = reset_bricks()
        paddle_x = (WIDTH - PADDLE_WIDTH) // 2
        paddle_speed = 0
        ball_x = random.randint(0, WIDTH - BALL_RADIUS)
        ball_y = HEIGHT // 2
        ball_speed_x = random.choice(BALL_SPEED_X_CHOICES)
        ball_speed_y = random.uniform(-1, -5)

    return paddle_x, paddle_speed, ball_x, ball_y, ball_speed_x, ball_speed_y, reward, bricks

def main():
    paddle_x, paddle_y, paddle_speed, ball_x, ball_y, ball_speed_x, ball_speed_y, bricks = reset_game()

    game_over = False
    score = 0

    while not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            paddle_speed = max(paddle_speed - PADDLE_SPEED, -MAX_PADDLE_SPEED)
        elif keys[pygame.K_RIGHT]:
            paddle_speed = min(paddle_speed + PADDLE_SPEED, MAX_PADDLE_SPEED)
        else:
            paddle_speed = 0

        paddle_x = move_paddle(paddle_x, paddle_speed)
        ball_x, ball_y = move_ball(ball_x, ball_y, ball_speed_x, ball_speed_y)
        ball_speed_x, ball_speed_y = check_wall_collision(ball_x, ball_y, ball_speed_x, ball_speed_y)
        ball_speed_x, ball_speed_y = check_paddle_collision(ball_x, ball_y, ball_speed_x, ball_speed_y, paddle_x, paddle_y)
        ball_speed_x, ball_speed_y, reward, bricks = check_brick_collision(ball_x, ball_y, ball_speed_x, ball_speed_y, bricks)

        score += reward

        if ball_y >= HEIGHT:
            bricks = reset_bricks()
            paddle_x = (WIDTH - PADDLE_WIDTH) // 2
            paddle_speed = 0
            ball_x = random.randint(0, WIDTH - BALL_RADIUS)
            ball_y = HEIGHT // 2
            ball_speed_x = random.choice(BALL_SPEED_X_CHOICES)
            ball_speed_y = random.uniform(-1, -5)

        draw_elements(paddle_x, paddle_y, ball_x, ball_y, bricks)
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
