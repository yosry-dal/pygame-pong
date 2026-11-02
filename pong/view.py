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

from .model import PADDLE_COLORS, WINDOW_HEIGHT, WINDOW_WIDTH


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

        pygame.draw.rect(self.screen, model.left_paddle.color, left)
        pygame.draw.rect(self.screen, model.right_paddle.color, right)
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

    def draw_hud(self, current_time: float, best_time: float) -> None:
        """Display the live survival timer and stored best score."""
        label = f"Run: {current_time:.1f}s   Best: {best_time:.1f}s"
        text = self.ui_font.render(label, True, self.foreground_color)
        rect = text.get_rect(center=(WINDOW_WIDTH / 2, 570))
        self.screen.blit(text, rect)

    def draw_menu(self, prompt: str, best_time: float = 0.0) -> None:
        """Draw the menu screen with mode selection instructions."""
        self.draw_background()

        title = self.title_font.render("PONG", True, self.foreground_color)
        title_rect = title.get_rect(center=(WINDOW_WIDTH / 2, 150))
        self.screen.blit(title, title_rect)

        best_text = self.ui_font.render(f"Best Survival: {best_time:.1f}s", True, self.foreground_color)
        best_rect = best_text.get_rect(center=(WINDOW_WIDTH / 2, 240))
        self.screen.blit(best_text, best_rect)

        prompt_text = self.ui_font.render(prompt, True, self.foreground_color)
        prompt_rect = prompt_text.get_rect(center=(WINDOW_WIDTH / 2, 290))
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

    def draw_paddle_selector(self, colors, selected_index: int, best_time: float) -> None:
        """Show the paddle color selection menu for single-player mode."""
        self.draw_background()

        title = self.title_font.render("PADDLE COLOR", True, self.foreground_color)
        title_rect = title.get_rect(center=(WINDOW_WIDTH / 2, 120))
        self.screen.blit(title, title_rect)

        best_text = self.ui_font.render(f"Best Survival: {best_time:.1f}s", True, self.foreground_color)
        best_rect = best_text.get_rect(center=(WINDOW_WIDTH / 2, 160))
        self.screen.blit(best_text, best_rect)

        for index, color_name in enumerate(colors):
            label = f"{index + 1}. {color_name.title()}"
            if index == selected_index:
                label = f"> {label} <"
                color = PADDLE_COLORS[color_name]
            else:
                color = self.foreground_color

            surface = self.ui_font.render(label, True, color)
            rect = surface.get_rect(center=(WINDOW_WIDTH / 2, 240 + index * 50))
            self.screen.blit(surface, rect)

        key_hint = self.ui_font.render("Left/Right to choose, Enter to confirm", True, self.foreground_color)
        key_rect = key_hint.get_rect(center=(WINDOW_WIDTH / 2, 520))
        self.screen.blit(key_hint, key_rect)

    def draw_result(self, model, mode, best_time: float) -> None:
        """Draw the end-of-match screen with winner text and instructions."""
        self.draw_background()
        self.draw_scores(model)
        self.draw_paddles_and_ball(model)
        self.draw_mode_label(mode)

        if mode == "single_player":
            survival_message = self.ui_font.render(f"Survival Time: {model.current_survival_time:.1f}s", True, self.foreground_color)
            survival_rect = survival_message.get_rect(center=(WINDOW_WIDTH / 2, 250))
            self.screen.blit(survival_message, survival_rect)

            best_message = self.ui_font.render(f"Best Survival: {best_time:.1f}s", True, self.foreground_color)
            best_rect = best_message.get_rect(center=(WINDOW_WIDTH / 2, 290))
            self.screen.blit(best_message, best_rect)

        winner = model.winner
        text = self.title_font.render(f"{winner} Wins!", True, self.foreground_color)
        text_rect = text.get_rect(center=(WINDOW_WIDTH / 2, 190))
        self.screen.blit(text, text_rect)

        prompt = self.ui_font.render("Press R to restart or M for menu", True, self.foreground_color)
        prompt_rect = prompt.get_rect(center=(WINDOW_WIDTH / 2, 330))
        self.screen.blit(prompt, prompt_rect)

    def render(self, model, mode, best_time: float) -> None:
        """Draw the current game state during active play."""
        self.draw_background()
        self.draw_scores(model)
        self.draw_paddles_and_ball(model)
        self.draw_mode_label(mode)
        if mode == "single_player":
            self.draw_hud(model.current_survival_time, best_time)
