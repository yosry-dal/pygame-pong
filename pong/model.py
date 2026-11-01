import math
import random

import pygame

WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 120
PADDLE_SPEED = 520
BALL_SIZE = 16
BALL_SPEED = 420
WINNING_SCORE = 7


class GameMode(str):
    SINGLE_PLAYER = "single_player"
    TWO_PLAYER = "two_player"


class Paddle:
    def __init__(self, x: float, y: float) -> None:
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move(self, direction: int, dt: float) -> None:
        self.rect.y += direction * self.speed * dt

    def clamp(self, top: int, bottom: int) -> None:
        self.rect.y = max(top, min(self.rect.y, bottom - self.rect.height))


class Ball:
    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)
        self.velocity = pygame.Vector2(0, 0)
        self.reset()

    def reset(self) -> None:
        self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        angle = random.uniform(-0.8, 0.8)
        direction = random.choice((-1, 1))
        self.velocity.x = direction * BALL_SPEED * math.cos(angle)
        self.velocity.y = BALL_SPEED * math.sin(angle)

    def update(self, dt: float) -> None:
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity.y *= -1
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity.y *= -1


class GameModel:
    def __init__(self, mode: GameMode) -> None:
        self.mode = mode
        self.left_paddle = Paddle(30, WINDOW_HEIGHT / 2 - PADDLE_HEIGHT / 2)
        self.right_paddle = Paddle(WINDOW_WIDTH - 30 - PADDLE_WIDTH, WINDOW_HEIGHT / 2 - PADDLE_HEIGHT / 2)
        self.ball = Ball()
        self.left_score = 0
        self.right_score = 0
        self.winner = None

    @property
    def left_label(self) -> str:
        if self.mode == GameMode.SINGLE_PLAYER:
            return "Player"
        return "Left Player"

    @property
    def right_label(self) -> str:
        if self.mode == GameMode.SINGLE_PLAYER:
            return "CPU"
        return "Right Player"

    def handle_player_movement(self, left_direction: int, right_direction: int, dt: float) -> None:
        self.left_paddle.move(left_direction, dt)
        self.right_paddle.move(right_direction, dt)
        self.left_paddle.clamp(0, WINDOW_HEIGHT)
        self.right_paddle.clamp(0, WINDOW_HEIGHT)

    def update_cpu(self, dt: float) -> None:
        if self.mode != GameMode.SINGLE_PLAYER:
            return

        target = self.ball.rect.centery
        current = self.right_paddle.rect.centery
        if abs(target - current) > 8:
            direction = 1 if target > current else -1
            self.right_paddle.move(direction, dt)
            self.right_paddle.clamp(0, WINDOW_HEIGHT)

    def resolve_ball_collisions(self) -> None:
        left_paddle_rect = self.left_paddle.rect
        right_paddle_rect = self.right_paddle.rect

        if self.ball.rect.colliderect(left_paddle_rect):
            self.ball.rect.left = left_paddle_rect.right
            self.ball.velocity.x = abs(self.ball.velocity.x)
            impact = (self.ball.rect.centery - left_paddle_rect.centery) / (left_paddle_rect.height / 2)
            self.ball.velocity.y = impact * BALL_SPEED * 0.9

        if self.ball.rect.colliderect(right_paddle_rect):
            self.ball.rect.right = right_paddle_rect.left
            self.ball.velocity.x = -abs(self.ball.velocity.x)
            impact = (self.ball.rect.centery - right_paddle_rect.centery) / (right_paddle_rect.height / 2)
            self.ball.velocity.y = impact * BALL_SPEED * 0.9

    def update_ball(self, dt: float) -> None:
        self.ball.update(dt)
        self.resolve_ball_collisions()

        if self.ball.rect.left <= 0:
            self.right_score += 1
            self.ball.reset()
        elif self.ball.rect.right >= WINDOW_WIDTH:
            self.left_score += 1
            self.ball.reset()

        if self.left_score >= WINNING_SCORE or self.right_score >= WINNING_SCORE:
            self.winner = self.left_label if self.left_score >= WINNING_SCORE else self.right_label

    def reset_match(self) -> None:
        self.left_score = 0
        self.right_score = 0
        self.winner = None
        self.ball.reset()
        self.left_paddle.rect.y = WINDOW_HEIGHT / 2 - PADDLE_HEIGHT / 2
        self.right_paddle.rect.y = WINDOW_HEIGHT / 2 - PADDLE_HEIGHT / 2
