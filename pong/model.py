# Pong game model.
# This file contains the core rules and state of the game:
# - screen size
# - paddle and ball properties
# - score tracking
# - ball movement and collisions
# - CPU behavior in single-player mode

import math
import random

import pygame

# These values define the play area and gameplay behavior.
WINDOW_WIDTH = 900
WINDOW_HEIGHT = 600
PADDLE_WIDTH = 18
PADDLE_HEIGHT = 120
PADDLE_SPEED = 520
BALL_SIZE = 16
BALL_SPEED = 420
WINNING_SCORE = 7


class GameMode(str):
    """Represents the available game modes."""

    # Human plays against the computer.
    SINGLE_PLAYER = "single_player"

    # Two human players share the same keyboard.
    TWO_PLAYER = "two_player"


class Paddle:
    """Represents one paddle in the game."""

    def __init__(self, x: float, y: float) -> None:
        # pygame.Rect stores the paddle's position and size.
        self.rect = pygame.Rect(x, y, PADDLE_WIDTH, PADDLE_HEIGHT)
        self.speed = PADDLE_SPEED

    def move(self, direction: int, dt: float) -> None:
        """Move the paddle up or down.

        direction: -1 for up, 1 for down
        dt: time passed since last frame, in seconds
        """
        self.rect.y += direction * self.speed * dt

    def clamp(self, top: int, bottom: int) -> None:
        """Keep the paddle inside the screen boundaries."""
        self.rect.y = max(top, min(self.rect.y, bottom - self.rect.height))


class Ball:
    """Represents the ball and handles wall collisions."""

    def __init__(self) -> None:
        # A rectangle describes the ball's current position and size.
        self.rect = pygame.Rect(0, 0, BALL_SIZE, BALL_SIZE)

        # velocity stores the ball's movement direction and speed.
        self.velocity = pygame.Vector2(0, 0)

        # Start the ball in a random direction.
        self.reset()

    def reset(self) -> None:
        """Center the ball and send it in a random direction."""
        self.rect.center = (WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)

        angle = random.uniform(-0.8, 0.8)
        direction = random.choice((-1, 1))

        self.velocity.x = direction * BALL_SPEED * math.cos(angle)
        self.velocity.y = BALL_SPEED * math.sin(angle)

    def update(self, dt: float) -> None:
        """Move the ball and bounce it off the top and bottom walls."""
        self.rect.x += self.velocity.x * dt
        self.rect.y += self.velocity.y * dt

        # Bounce off the top wall.
        if self.rect.top <= 0:
            self.rect.top = 0
            self.velocity.y *= -1

        # Bounce off the bottom wall.
        elif self.rect.bottom >= WINDOW_HEIGHT:
            self.rect.bottom = WINDOW_HEIGHT
            self.velocity.y *= -1


class GameModel:
    """Contains the game state and all game rules for a match."""

    def __init__(self, mode: GameMode) -> None:
        self.mode = mode

        # Create both paddles.
        self.left_paddle = Paddle(30, WINDOW_HEIGHT / 2 - PADDLE_HEIGHT / 2)
        self.right_paddle = Paddle(
            WINDOW_WIDTH - 30 - PADDLE_WIDTH,
            WINDOW_HEIGHT / 2 - PADDLE_HEIGHT / 2,
        )

        # Create the ball and track scoreboard values.
        self.ball = Ball()
        self.left_score = 0
        self.right_score = 0
        self.winner = None

    @property
    def left_label(self) -> str:
        """Returns the label for the left side of the screen."""
        if self.mode == GameMode.SINGLE_PLAYER:
            return "Player"
        return "Left Player"

    @property
    def right_label(self) -> str:
        """Returns the label for the right side of the screen."""
        if self.mode == GameMode.SINGLE_PLAYER:
            return "CPU"
        return "Right Player"

    def handle_player_movement(self, left_direction: int, right_direction: int, dt: float) -> None:
        """Move each paddle based on player input.

        left_direction: -1 = move up, 1 = move down, 0 = no input
        right_direction: same idea for the right paddle
        dt: elapsed time since last frame
        """
        self.left_paddle.move(left_direction, dt)
        self.right_paddle.move(right_direction, dt)

        self.left_paddle.clamp(0, WINDOW_HEIGHT)
        self.right_paddle.clamp(0, WINDOW_HEIGHT)

    def update_cpu(self, dt: float) -> None:
        """Move the right paddle automatically during single-player mode."""
        if self.mode != GameMode.SINGLE_PLAYER:
            return

        target = self.ball.rect.centery
        current = self.right_paddle.rect.centery

        # If the CPU is not aligned with the ball, move toward it.
        if abs(target - current) > 8:
            direction = 1 if target > current else -1
            self.right_paddle.move(direction, dt)
            self.right_paddle.clamp(0, WINDOW_HEIGHT)

    def resolve_ball_collisions(self) -> None:
        """Bounce the ball off both paddles and adjust its angle."""

        left_paddle_rect = self.left_paddle.rect
        right_paddle_rect = self.right_paddle.rect

        # Check collision with the left paddle.
        if self.ball.rect.colliderect(left_paddle_rect):
            self.ball.rect.left = left_paddle_rect.right
            self.ball.velocity.x = abs(self.ball.velocity.x)

            impact = (
                self.ball.rect.centery - left_paddle_rect.centery
            ) / (left_paddle_rect.height / 2)

            self.ball.velocity.y = impact * BALL_SPEED * 0.9

        # Check collision with the right paddle.
        if self.ball.rect.colliderect(right_paddle_rect):
            self.ball.rect.right = right_paddle_rect.left
            self.ball.velocity.x = -abs(self.ball.velocity.x)

            impact = (
                self.ball.rect.centery - right_paddle_rect.centery
            ) / (right_paddle_rect.height / 2)

            self.ball.velocity.y = impact * BALL_SPEED * 0.9

    def update_ball(self, dt: float) -> None:
        """Move the ball, check collisions, and score points."""
        self.ball.update(dt)
        self.resolve_ball_collisions()

        # If the ball goes off the left side, the right side scores.
        if self.ball.rect.left <= 0:
            self.right_score += 1
            self.ball.reset()

        # If the ball goes off the right side, the left side scores.
        elif self.ball.rect.right >= WINDOW_WIDTH:
            self.left_score += 1
            self.ball.reset()

        # Update the winner once a player reaches the winning score.
        if self.left_score >= WINNING_SCORE or self.right_score >= WINNING_SCORE:
            self.winner = self.left_label if self.left_score >= WINNING_SCORE else self.right_label

    def reset_match(self) -> None:
        """Reset all match state for a new round."""
        self.left_score = 0
        self.right_score = 0
        self.winner = None

        self.ball.reset()
        self.left_paddle.rect.y = WINDOW_HEIGHT / 2 - PADDLE_HEIGHT / 2
        self.right_paddle.rect.y = WINDOW_HEIGHT / 2 - PADDLE_HEIGHT / 2
