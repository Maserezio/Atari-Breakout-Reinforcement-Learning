import pygame
import random
import math
import json
import ast
import os
import csv
from datetime import datetime


class BreakoutGame:
    def __init__(self):
        # Game dimensions
        self.WIDTH = 450
        self.HEIGHT = 600

        # Colors
        self.WHITE = (255, 255, 255)
        self.BLUE = (0, 0, 255)
        self.RED = (255, 0, 0)
        self.BLACK = (0, 0, 0)
        self.GREEN = (0, 255, 0)
        self.ORANGE = (255, 165, 0)

        # Paddle dimensions
        self.PADDLE_WIDTH = 100
        self.PADDLE_HEIGHT = 20
        self.PADDLE_SPEED = 5
        self.MAX_PADDLE_SPEED = 2

        # Ball dimensions and speed
        self.BALL_RADIUS = 10
        self.BALL_SPEED_Y = 3
        # self.BALL_SPEED_X_CHOICES = [-2, -1, 0, 1, 2]
        self.BALL_SPEED_X_CHOICES = [0]
        self.BALL_SPEED_X_MAX = 2

        # Brick dimensions
        self.BRICK_WIDTH = 60
        self.BRICK_HEIGHT = 20
        self.BRICK_REWARD = 50
        self.PADDLE_REWARD = 10

        self.GAME_OVER = False

        # Initialize Pygame
        pygame.init()
        self.window = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption("Breakout")

        self.clock = pygame.time.Clock()

    def reset_game(self, layout, brick_number):
        bricks = self.reset_bricks(layout, brick_number)

        # Initialize paddle
        paddle_x = (self.WIDTH - self.PADDLE_WIDTH) // 2
        paddle_y = self.HEIGHT - self.PADDLE_HEIGHT - 10
        paddle_speed = 0

        # Initialize ball
        ball_x = (self.WIDTH - self.BALL_RADIUS) / 2
        ball_y = (self.HEIGHT - self.BALL_RADIUS) / 2
        ball_speed_x = random.choice(self.BALL_SPEED_X_CHOICES)
        ball_speed_y = random.uniform(-1, -1)  # Randomly select one of five directions directed upwards

        return paddle_x, paddle_y, paddle_speed, ball_x, ball_y, ball_speed_x, ball_speed_y, bricks

    def reset_bricks(self, layout_type, brick_number):
        if layout_type == 'rectangle':
            return self.reset_bricks_rectangle(brick_number)
        elif layout_type == 'circle':
            return self.reset_bricks_circle(brick_number)
        elif layout_type == 'triangle':
            return self.reset_bricks_triangle(brick_number)

    def reset_bricks_rectangle(self, brick_number=10):
        BRICK_COLS = min(brick_number, self.WIDTH // self.BRICK_WIDTH)
        BRICK_ROWS = (brick_number + BRICK_COLS - 1) // BRICK_COLS

        bricks = []

        total_width = BRICK_COLS * self.BRICK_WIDTH + 2 * self.BALL_RADIUS
        initial_x = (self.WIDTH - total_width) // 2 + self.BALL_RADIUS

        initial_y = self.HEIGHT // 12

        for row in range(BRICK_ROWS):
            for col in range(BRICK_COLS):
                brick_x = initial_x + col * self.BRICK_WIDTH
                brick_y = initial_y + row * self.BRICK_HEIGHT
                bricks.append((brick_x, brick_y, self.BRICK_WIDTH, self.BRICK_HEIGHT))

        return bricks

    def reset_bricks_circle(self, brick_number=10):
        bricks = []
        center_x = self.WIDTH // 2
        center_y = self.HEIGHT // 4
        radius = min(self.WIDTH, self.HEIGHT) // 4

        angle_step = 360 / brick_number

        for i in range(brick_number):
            angle_rad = math.radians(i * angle_step)
            x = center_x + radius * math.cos(angle_rad) - self.BRICK_WIDTH // 2
            y = center_y + radius * math.sin(angle_rad) - self.BRICK_HEIGHT // 2
            bricks.append((int(x), int(y), self.BRICK_WIDTH, self.BRICK_HEIGHT))

        return bricks

    def reset_bricks_triangle(self, brick_number=10):
        bricks = []
        triangle_rows = int(((-1 + math.sqrt(1 + 8 * brick_number)) / 2))  # Approximate number of rows in the triangle

        initial_y = self.HEIGHT // 12

        brick_counter = 0

        for row in range(triangle_rows):
            row_width = (row + 1) * self.BRICK_WIDTH  # Width of this row
            initial_x = (self.WIDTH - row_width) // 2  # x-coordinate of the first brick in the row

            for col in range(row + 1):
                if brick_counter >= brick_number:
                    break

                brick_x = initial_x + col * self.BRICK_WIDTH  # Position each brick in the row
                brick_y = initial_y + row * self.BRICK_HEIGHT
                bricks.append((brick_x, brick_y, self.BRICK_WIDTH, self.BRICK_HEIGHT))
                brick_counter += 1

        return bricks

    def draw_elements(self, paddle_x, paddle_y, ball_x, ball_y, bricks):
        self.window.fill(self.BLACK)

        pygame.draw.rect(self.window, self.ORANGE, (paddle_x, paddle_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT))
        pygame.draw.circle(self.window, self.RED, (ball_x, ball_y), self.BALL_RADIUS)

        for brick in bricks:
            pygame.draw.rect(self.window, self.GREEN, brick)
            pygame.draw.rect(self.window, self.BLACK, brick, 2)  # Add black outline to bricks

        pygame.display.flip()

    def move_paddle(self, paddle_x, paddle_speed):
        paddle_x += paddle_speed
        if paddle_x < 0:
            paddle_x = 0
        if paddle_x > self.WIDTH - self.PADDLE_WIDTH:
            paddle_x = self.WIDTH - self.PADDLE_WIDTH
        return paddle_x

    def move_ball(self, ball_x, ball_y, ball_speed_x, ball_speed_y):
        ball_x += ball_speed_x
        ball_y += ball_speed_y
        return ball_x, ball_y

    def check_wall_collision(self, ball_x, ball_y, ball_speed_x, ball_speed_y):
        if ball_x - self.BALL_RADIUS <= 0 or ball_x + self.BALL_RADIUS >= self.WIDTH:
            ball_speed_x *= -1
        if ball_y - self.BALL_RADIUS <= 0:
            ball_speed_y *= -1
        return ball_speed_x, ball_speed_y

    def check_paddle_collision(self, ball_x, ball_y, ball_speed_x, ball_speed_y, paddle_x, paddle_y, reward, kicks):
        paddle_rect = pygame.Rect(paddle_x, paddle_y, self.PADDLE_WIDTH, self.PADDLE_HEIGHT)
        ball_rect = pygame.Rect(ball_x - self.BALL_RADIUS, ball_y - self.BALL_RADIUS, self.BALL_RADIUS * 2,
                                self.BALL_RADIUS * 2)

        if ball_rect.colliderect(paddle_rect):
            ball_speed_y *= -1
            # REWARD
            reward += self.PADDLE_REWARD
            kicks += 1
            # Calculate the reflection angle based on the direction of the ball's incoming velocity
            if ball_speed_x < 0:
                angle = -math.pi / 4  # Reflect to the left
            else:
                angle = math.pi / 4  # Reflect to the right

            ball_speed_x = math.sin(angle) * self.BALL_SPEED_X_MAX

            # Adjust the ball's horizontal direction if it's in contact with both paddle and wall
            if (ball_speed_x < 0 and ball_x + self.BALL_RADIUS >= paddle_x + self.PADDLE_WIDTH) or (
                    ball_speed_x > 0 and ball_x - self.BALL_RADIUS <= paddle_x):
                ball_speed_x *= -1

            # Adjust the ball's vertical direction to prevent sticking
            if ball_speed_y > 0:
                ball_speed_y = -self.BALL_SPEED_Y

        return ball_speed_x, ball_speed_y, reward, kicks

    def check_brick_collision(self, ball_x, ball_y, ball_speed_x, ball_speed_y, bricks, reward, kicks):
        for brick in bricks:
            brick_rect = pygame.Rect(*brick)  # Convert to Rect
            if brick_rect.collidepoint(ball_x + ball_speed_x, ball_y):  # Check horizontal collision
                bricks.remove(brick)
                ball_speed_x *= -1
                reward += self.BRICK_REWARD
                kicks += 1
                return ball_speed_x, ball_speed_y, bricks, reward, kicks
            elif brick_rect.collidepoint(ball_x, ball_y + ball_speed_y):  # Check vertical collision
                bricks.remove(brick)
                ball_speed_y *= -1
                reward += self.BRICK_REWARD
                kicks += 1
                return ball_speed_x, ball_speed_y, bricks, reward, kicks
        return ball_speed_x, ball_speed_y, bricks, reward, kicks

    def update_game_state(self, layout, brick_number, action, paddle_x, paddle_speed, ball_x, ball_y, ball_speed_x,
                          ball_speed_y,
                          bricks, reward, kicks):
        if action == -1:
            paddle_speed = max(paddle_speed - 1, -self.MAX_PADDLE_SPEED)
        elif action == 1:
            paddle_speed = min(paddle_speed + 1, self.MAX_PADDLE_SPEED)
        else:
            paddle_speed = 0

        paddle_y = self.HEIGHT - self.PADDLE_HEIGHT - 10

        paddle_x = self.move_paddle(paddle_x, paddle_speed)
        ball_x, ball_y = self.move_ball(ball_x, ball_y, ball_speed_x, ball_speed_y)
        ball_speed_x, ball_speed_y = self.check_wall_collision(ball_x, ball_y, ball_speed_x, ball_speed_y)
        ball_speed_x, ball_speed_y, reward, kicks = self.check_paddle_collision(ball_x, ball_y, ball_speed_x,
                                                                                ball_speed_y, paddle_x,
                                                                                paddle_y, reward, kicks)
        ball_speed_x, ball_speed_y, bricks, reward, kicks = self.check_brick_collision(ball_x, ball_y, ball_speed_x,
                                                                                       ball_speed_y,
                                                                                       bricks, reward, kicks)

        if ball_y >= self.HEIGHT:
            bricks = self.reset_bricks(layout, brick_number)
            paddle_x = (self.WIDTH - self.PADDLE_WIDTH) // 2
            paddle_speed = 0
            ball_x = (self.WIDTH - self.BALL_RADIUS) / 2
            ball_y = (self.HEIGHT - self.BALL_RADIUS) / 2
            ball_speed_x = random.choice(self.BALL_SPEED_X_CHOICES)
            ball_speed_y = random.uniform(-1, -1)
            self.GAME_OVER = True

        return paddle_x, paddle_speed, ball_x, ball_y, ball_speed_x, ball_speed_y, bricks, reward, kicks

    def play(self, layout='rectangle', brick_number=5, num_episodes=20, learn_mode=True):
        win_count = 0
        reward = 0
        results = []

        # Initialize the agent's policy
        if os.path.exists('policy/policy_' + layout + '_' + str(brick_number) + '.json'):
            with open('policy/policy_' + layout + '_' + str(brick_number) + '.json', 'r') as f:
                policy_str = json.load(f)
            policy = {ast.literal_eval(key): value for key, value in policy_str.items()}
        else:
            policy = {}

        if os.path.exists('win_policy/win_policy_' + layout + '_' + str(brick_number) + '.json'):
            with open('win_policy/win_policy_' + layout + '_' + str(brick_number) + '.json', 'r') as f:
                win_policy_str = json.load(f)
            win_policy = {ast.literal_eval(key): value for key, value in win_policy_str.items()}
        else:
            win_policy = {}

        # if os.path.exists('lose_policy/lose_policy_' + layout + '_' + str(brick_number) + '.json'):
        #     with open('lose_policy/lose_policy_' + layout + '_' + str(brick_number) + '.json', 'r') as f:
        #         lose_policy_str = json.load(f)
        #     lose_policy = {ast.literal_eval(key): value for key, value in policy_str.items()}
        # else:
        #     lose_policy = {}

        start_ball_speed_x = None
        for epoch in range(num_episodes):
            paddle_x, paddle_y, paddle_speed, ball_x, ball_y, ball_speed_x, ball_speed_y, bricks = self.reset_game(
                layout,
                brick_number)

            if not start_ball_speed_x:
                start_ball_speed_x = ball_speed_x
            episode_memory = []  # Store state, action, reward tuples for the episode
            kicks = 0
            self.GAME_OVER = False
            print("Epoch", epoch)

            while not self.GAME_OVER:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.GAME_OVER = True
                reward -= 0.1
                # state_paddle_x = round(paddle_x / 20)
                # state_paddle_y = round(paddle_x / 20)
                # state_ball_x = round(ball_x / 20)
                # state_ball_y = round(ball_y / 20)

                state_paddle_x = round(paddle_x)
                state_paddle_y = round(paddle_x)
                state_ball_x = round(ball_x)
                state_ball_y = round(ball_y)

                state = (
                    state_paddle_x, state_paddle_y, state_ball_x, state_ball_y, ball_speed_x, ball_speed_y,
                    tuple(bricks))
                if learn_mode == True:
                    if state in win_policy.keys():
                        # if reward > win_policy[state][1]:
                        #     policy[state] = win_policy[state][0]
                        # else:
                        new_action = random.choice([-1, 0, 1])
                        while new_action == win_policy[state][0]:
                            new_action = random.choice([-1, 0, 1])
                        policy[state] = new_action
                    # else:
                    #     new_action = random.choice([-1, 0, 1])
                    #     while new_action == policy[state]:
                    #         new_action = random.choice([-1, 0, 1])
                    #     policy[state] = new_action
                else:
                    if state in win_policy.keys():
                        policy[state] = win_policy[state][0]
                # print(reward)
                if state not in policy.keys() or reward < -20 * brick_number:
                    # print("RANDOM")
                    # if state not in policy.keys() or kicks - (brick_number-len(tuple(bricks))) <= 3:
                    policy[state] = random.choice([-1, 0, 1])

                action = policy[state]

                paddle_x, paddle_speed, ball_x, ball_y, ball_speed_x, ball_speed_y, bricks, reward, kicks = self.update_game_state(
                    layout, brick_number, action, paddle_x, paddle_speed, ball_x, ball_y, ball_speed_x, ball_speed_y,
                    bricks, reward, kicks)
                # print("reward", reward)
                # print("kicks", kicks)
                # WIN!
                if len(bricks) == 0:
                    win_count += 1
                    print("WIN!!", win_count)

                    print("reward", reward)
                    episode_memory.append((state, action, 1000, kicks))

                    for state_mem, action_mem, reward_mem, kicks_mem in reversed(episode_memory):
                        policy[state_mem] = action_mem

                        if state_mem in win_policy:
                            if reward > win_policy[state_mem][1]:
                                win_policy[state_mem] = [action_mem, reward]
                        else:
                            win_policy[state_mem] = [action_mem, reward]

                    results.append(
                        [epoch + 1, "WIN", reward, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), start_ball_speed_x])

                    start_ball_speed_x = None
                    reward = 0
                    kicks = 0
                    self.GAME_OVER = True

                # LOSE
                if self.GAME_OVER == True and len(bricks) != 0:
                    # LOOSE

                    for state_mem, action_mem, reward_mem, kicks_mem in reversed(episode_memory):

                        if kicks_mem <= 1:
                            if state_mem in policy:
                                policy[state_mem] = random.choice([-1, 0, 1])
                        elif reward_mem / kicks_mem > 20:
                            # print(reward_mem)
                            policy[state_mem] = action_mem
                        else:
                            if state_mem in policy:
                                policy[state_mem] = random.choice([-1, 0, 1])

                    # episode_memory = episode_memory[::-1]
                    # max_kicks = max(item[3] for item in episode_memory)
                    #
                    # index_max_kicks = [index for index, item in enumerate(episode_memory) if
                    #                    item[3] == max_kicks]
                    # index_max_kicks = index_max_kicks[:-1]
                    #
                    # for index in index_max_kicks:
                    #     state_mem, action_mem, reward_mem, kicks_mem = episode_memory[index]
                    #
                    #     # -1 -> 0, 0 -> 1, 1 -> 2
                    #     # if state_mem not in lose_policy:
                    #     #     lose_policy[state_mem] = [None, None, None]
                    #     # lose_policy[state_mem][action_mem + 1] = action_mem
                    #     if state_mem in policy:
                    #         new_action = random.choice([-1, 0, 1])
                    #         # while new_action == action_mem or new_action in lose_policy[state_mem]:
                    #         while new_action == action_mem:
                    #             new_action = random.choice([-1, 0, 1])
                    #         policy[state_mem] = new_action

                    # episode_memory = [item for index, item in enumerate(episode_memory) if index not in index_max_kicks]

                    # for state_mem, action_mem, reward_mem, kicks_mem in episode_memory:
                    #     # print(reward_mem)
                    #     print(reward_mem)
                    #     if kicks_mem - (brick_number - len(state_mem[6])) <= 3:
                    #         policy[state_mem] = action_mem
                    #         # print("LOSE BUT WRITE")
                    #     elif reward_mem >= -50:
                    #         policy[state_mem] = action_mem
                    #     else:
                    #         # print("RANDOM")
                    #         new_action = action_mem
                    #         if state_mem in policy:
                    #             while new_action == action_mem:
                    #                 new_action = random.choice([-1, 0, 1])

                    # episode_memory = episode_memory[::-1]

                    results.append(
                        [epoch + 1, "LOSE", reward, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), start_ball_speed_x])
                    # episode_memory.append((state, action, reward, kicks))

                    start_ball_speed_x = None
                    reward = 0
                    kicks = 0
                    self.GAME_OVER = True

                if self.GAME_OVER != True and len(bricks) != 0:
                    episode_memory.append((state, action, reward, kicks))

                self.draw_elements(paddle_x, paddle_y, ball_x, ball_y, bricks)
                self.clock.tick(100000)

            # game_result = "WIN" if len(bricks) == 0 else "LOSE"
            # current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # results.append([epoch + 1, game_result, reward, current_time, start_ball_speed_x])

        with open('results/' + layout + '_' + str(brick_number) + '_' + str(learn_mode) + '_results.csv', mode='w',
                  newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["Epoch", "Result", "Score", "Date and Time", "Start"])
            writer.writerows(results)

        new_dict = {str(key): value for key, value in policy.items()}
        with open('policy/policy_' + layout + '_' + str(brick_number) + '.json', 'w') as f:
            json.dump(new_dict, f)

        new_win_dict = {str(key): value for key, value in win_policy.items()}
        with open('win_policy/win_policy_' + layout + '_' + str(brick_number) + '.json', 'w') as f:
            json.dump(new_win_dict, f)

        # new_lose_dict = {str(key): value for key, value in lose_policy.items()}
        # with open('lose_policy/lose_policy_' + layout + '_' + str(brick_number) + '.json', 'w') as f:
        #     json.dump(new_lose_dict, f)

        pygame.quit()


if __name__ == "__main__":
    game = BreakoutGame()
    game.play('rectangle', 6, 5000, learn_mode=True)
    # game.play('rectangle', 6, 1000, learn_mode=False)
    # game = BreakoutGame()
    # game.play('rectangle', 10, 1000, learn_mode=True)
    # game = BreakoutGame()
    # game.play('rectangle', 10, 1000, learn_mode=False)
    # game = BreakoutGame()
    # game.play('rectangle', 15, 1000, learn_mode=True)
    # game = BreakoutGame()
    # game.play('rectangle', 15, 1000, learn_mode=False)
    #
    # game = BreakoutGame()
    # game.play('triangle', 6, 1000, learn_mode=True)
    # game = BreakoutGame()
    # game.play('triangle', 6, 1000, learn_mode=False)
    # game = BreakoutGame()
    # game.play('triangle', 10, 1000, learn_mode=True)
    # game = BreakoutGame()
    # game.play('triangle', 10, 1000, learn_mode=False)
    # game = BreakoutGame()
    # game.play('triangle', 15, 1000, learn_mode=True)
    # game = BreakoutGame()
    # game.play('triangle', 15, 1000, learn_mode=False)
    #
    # game = BreakoutGame()
    # game.play('circle', 6, 1000, learn_mode=True)
    # game = BreakoutGame()
    # game.play('circle', 6, 1000, learn_mode=False)
    # game = BreakoutGame()
    # game.play('circle', 10, 1000, learn_mode=True)
    # game = BreakoutGame()
    # game.play('circle', 10, 1000, learn_mode=False)
    # game = BreakoutGame()
    # game.play('circle', 15, 1000, learn_mode=True)
    # game = BreakoutGame()
    # game.play('circle', 15, 1000, learn_mode=False)
    pygame.quit()
