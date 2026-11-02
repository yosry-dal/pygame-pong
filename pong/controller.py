# Controller for the Pong game.
# This file manages the game loop and the interaction between:
# - user input
# - game state
# - rendering
# - menu flow
# - game reset flow
# - high-score tracking and paddle unlocks

import json
import sys
from pathlib import Path

import pygame

from .model import GameMode, GameModel, PADDLE_UNLOCKS
from .view import PongView

PROGRESS_FILE = Path(__file__).resolve().parents[1] / "pong_progress.json"


class PongController:
    """Handles the main game loop, menu flow, and player progression."""

    def __init__(self) -> None:
        # Initialize Pygame and create the game window.
        pygame.init()
        self.screen = pygame.display.set_mode((900, 600))
        pygame.display.set_caption("Pong")

        # A clock keeps the game running at a consistent speed.
        self.clock = pygame.time.Clock()

        # The view is responsible for drawing objects on the screen.
        self.view = PongView(self.screen)

        # Controls whether the game loop is still running.
        self.running = True

        # Load saved high score progress for single-player mode.
        self.progress = self.load_progress()
        self.best_survival_time = float(self.progress.get("best_seconds", 0.0))
        self.unlocked_colors = self.progress.get("unlocked_colors", ["white"])
        self.selected_color = self.progress.get("selected_color", "white")

    def load_progress(self):
        """Load the saved survival best and unlocked paddle colors."""
        if not PROGRESS_FILE.exists():
            return {"best_seconds": 0.0, "unlocked_colors": ["white"], "selected_color": "white"}

        try:
            with PROGRESS_FILE.open("r", encoding="utf-8") as file:
                data = json.load(file)
        except (json.JSONDecodeError, OSError):
            return {"best_seconds": 0.0, "unlocked_colors": ["white"], "selected_color": "white"}

        data.setdefault("best_seconds", 0.0)
        data.setdefault("unlocked_colors", ["white"])
        data.setdefault("selected_color", "white")
        return data

    def save_progress(self) -> None:
        """Save the current high-score progress to disk."""
        payload = {
            "best_seconds": self.best_survival_time,
            "unlocked_colors": self.unlocked_colors,
            "selected_color": self.selected_color,
        }
        with PROGRESS_FILE.open("w", encoding="utf-8") as file:
            json.dump(payload, file, indent=2)

    def unlock_colors_for_time(self, survival_time: float) -> None:
        """Unlock any paddle colors whose requirement has been met."""
        unlocked = list(self.unlocked_colors)
        for color_name, threshold in PADDLE_UNLOCKS.items():
            if survival_time >= threshold and color_name not in unlocked:
                unlocked.append(color_name)

        self.unlocked_colors = unlocked

        if self.selected_color not in self.unlocked_colors:
            self.selected_color = "white"

        if survival_time > self.best_survival_time:
            self.best_survival_time = survival_time

        self.save_progress()

    def show_menu(self):
        """Display the start menu and wait for the user to choose a mode."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        selected_color = self.show_single_player_setup()
                        if selected_color is None:
                            continue
                        self.selected_color = selected_color
                        self.save_progress()
                        return GameMode.SINGLE_PLAYER, selected_color
                    if event.key == pygame.K_2:
                        return GameMode.TWO_PLAYER, "white"
                    if event.key == pygame.K_q:
                        self.running = False
                        return None

            self.view.draw_menu("Press a mode to begin", self.best_survival_time)
            pygame.display.flip()
            self.clock.tick(60)

    def show_single_player_setup(self):
        """Let the player choose a color from all unlocked paddle colors."""
        if not self.unlocked_colors:
            self.unlocked_colors = ["white"]

        selected_index = max(0, self.unlocked_colors.index(self.selected_color))

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return None
                    if event.key in (pygame.K_LEFT, pygame.K_a):
                        selected_index = (selected_index - 1) % len(self.unlocked_colors)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d):
                        selected_index = (selected_index + 1) % len(self.unlocked_colors)
                    elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                        choice = self.unlocked_colors[selected_index]
                        self.selected_color = choice
                        return choice

            self.view.draw_paddle_selector(self.unlocked_colors, selected_index, self.best_survival_time)
            pygame.display.flip()
            self.clock.tick(60)

    def run(self) -> None:
        """Start the menu loop and then run the selected match."""
        while self.running:
            selection = self.show_menu()
            if selection is None:
                break
            mode, selected_color = selection
            self.play_match(mode, selected_color)

    def play_match(self, mode: GameMode, selected_color: str = "white") -> None:
        """Run a complete game match based on the selected mode."""
        model = GameModel(mode, selected_color)

        while self.running:
            # Keep movement smooth and consistent across different computers.
            dt = self.clock.tick(60) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    return

                if event.type == pygame.KEYDOWN and event.key == pygame.K_m and model.winner is not None:
                    return

                if event.type == pygame.KEYDOWN and event.key == pygame.K_r and model.winner is not None:
                    model.reset_match()

            keys = pygame.key.get_pressed()

            if model.winner is not None:
                self.unlock_colors_for_time(model.current_survival_time)
                self.view.draw_result(model, mode.value, self.best_survival_time)
                pygame.display.flip()
                continue

            left_direction = 0
            right_direction = 0

            # Handle input based on the selected game mode.
            if mode == GameMode.TWO_PLAYER:
                # Player 1 moves the left paddle with W and S.
                if keys[pygame.K_w]:
                    left_direction = -1
                elif keys[pygame.K_s]:
                    left_direction = 1

                # Player 2 moves the right paddle with the arrow keys.
                if keys[pygame.K_UP]:
                    right_direction = -1
                elif keys[pygame.K_DOWN]:
                    right_direction = 1

            else:
                # In single-player mode, the left paddle is controlled by the human.
                if keys[pygame.K_w]:
                    left_direction = -1
                elif keys[pygame.K_s]:
                    left_direction = 1

            # Update the model state with the current input and time elapsed.
            model.handle_player_movement(left_direction, right_direction, dt)
            model.update_cpu(dt)
            model.update_ball(dt)

            self.view.render(model, mode.value, self.best_survival_time)
            pygame.display.flip()

        # Exit pygame cleanly if the loop ends.
        pygame.quit()
        sys.exit()
