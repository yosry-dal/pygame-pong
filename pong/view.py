# Rendering layer for the Pong game.
# This file is responsible for drawing everything the player sees:
# - background
# - center divider line
# - paddles
# - ball
# - score
# - menu
# - winner screen

import pygame

from .model import WINDOW_HEIGHT, WINDOW_WIDTH


class PongView:
    """Handles all drawing operations for the game."""

    def __init__(self, screen: pygame.Surface) -> None:
        # Store the screen object so we can draw onto it.
        self.screen = screen

        # Define colors used in the game.
        self.background_color = (12, 18, 30)
        self.foreground_color = (255, 255, 255)
        self.accent_color = (92, 168, 255)

        # Create fonts for different sizes of text.
        self.title_font = pygame.font.Font(None, 72)
        self.score_font = pygame.font.Font(None, 64)
        self.ui_font = pygame.font.Font(None, 32)

    def draw_background(self) -> None:
        """Clear the screen and draw the center divider line."""
        self.screen.fill(self.background_color)

        for y in range(0, WINDOW_HEIGHT, 28):
            pygame.draw.rect(
                self.screen,
                self.foreground_color,
                (WINDOW_WIDTH / 2 - 2, y, 4, 16),
            )

    def draw_paddles_and_ball(self, model) -> None:
        """Draw the paddles and ball from the model's current state."""
        left = model.left_paddle.rect
        right = model.right_paddle.rect
        ball = model.ball.rect

        pygame.draw.rect(self.screen, self.foreground_color, left)
        pygame.draw.rect(self.screen, self.foreground_color, right)
        pygame.draw.ellipse(self.screen, self.accent_color, ball)

    def draw_scores(self, model) -> None:
        """Draw the left and right side scores on the screen."""
        left_text = self.score_font.render(str(model.left_score), True, self.foreground_color)
        right_text = self.score_font.render(str(model.right_score), True, self.foreground_color)

        left_rect = left_text.get_rect(center=(WINDOW_WIDTH * 0.25, 60))
        right_rect = right_text.get_rect(center=(WINDOW_WIDTH * 0.75, 60))

        self.screen.blit(left_text, left_rect)
        self.screen.blit(right_text, right_rect)

    def draw_mode_label(self, mode) -> None:
        """Display the current mode on the screen."""
        label = "One Player" if mode == "single_player" else "Two Players"
        text = self.ui_font.render(label, True, self.foreground_color)
        rect = text.get_rect(center=(WINDOW_WIDTH / 2, 20))
        self.screen.blit(text, rect)

    def draw_menu(self, prompt: str) -> None:
        """Draw the menu screen with mode selection instructions."""
        self.draw_background()

        title = self.title_font.render("PONG", True, self.foreground_color)
        title_rect = title.get_rect(center=(WINDOW_WIDTH / 2, 150))
        self.screen.blit(title, title_rect)

        prompt_text = self.ui_font.render(prompt, True, self.foreground_color)
        prompt_rect = prompt_text.get_rect(center=(WINDOW_WIDTH / 2, 280))
        self.screen.blit(prompt_text, prompt_rect)

        instructions = [
            "1 - Single Player",
            "2 - Local Two Player",
            "Q - Quit",
        ]

        for index, line in enumerate(instructions):
            surface = self.ui_font.render(line, True, self.foreground_color)
            rect = surface.get_rect(center=(WINDOW_WIDTH / 2, 340 + index * 40))
            self.screen.blit(surface, rect)

    def draw_result(self, model, mode) -> None:
        """Draw the end-of-match screen with winner text and instructions."""
        self.draw_background()
        self.draw_scores(model)
        self.draw_paddles_and_ball(model)
        self.draw_mode_label(mode)

        winner = model.winner
        text = self.title_font.render(f"{winner} Wins!", True, self.foreground_color)
        text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, 250))
        self.screen.blit(text, text_rect)

        prompt = self.ui_font.render("Press R to restart or M for menu", True, self.foreground_color)
        prompt_rect = prompt.get_rect(center=(WINDOW_WIDTH / 2, 330))
        self.screen.blit(prompt, prompt_rect)

    def render(self, model, mode) -> None:
        """Draw the current game state during active play."""
        self.draw_background()
        self.draw_scores(model)
        self.draw_paddles_and_ball(model)
        self.draw_mode_label(mode)
