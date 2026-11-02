# Controller for the Pong game.
# This file manages the game loop and the interaction between:
# - user input
# - game state
# - rendering
# - menu flow
# - game reset flow

import sys

import pygame

from .model import GameMode, GameModel, WINDOW_HEIGHT, WINDOW_WIDTH
from .view import PongView


class PongController:
    """Handles the main game loop and input handling."""

    def __init__(self) -> None:
        # Initialize Pygame and create the game window.
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong")

        # A clock keeps the game running at a consistent speed.
        self.clock = pygame.time.Clock()

        # The view is responsible for drawing objects on the screen.
        self.view = PongView(self.screen)

        # Controls whether the game loop is still running.
        self.running = True

    def run(self) -> None:
        """Start the menu loop and then run the selected match."""
        while self.running:
            mode = self.show_menu()
            if mode is None:
                break
            self.play_match(mode)

    def show_menu(self):
        """Display the start menu and wait for the user to choose a mode."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    return None

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        return GameMode.SINGLE_PLAYER
                    if event.key == pygame.K_2:
                        return GameMode.TWO_PLAYER
                    if event.key == pygame.K_q:
                        self.running = False
                        return None

            self.view.draw_menu("Press a mode to begin")
            pygame.display.flip()
            self.clock.tick(60)

    def play_match(self, mode: GameMode) -> None:
        """Run a complete game match based on the selected mode."""
        model = GameModel(mode)

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
                self.view.draw_result(model, mode.value)
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

            self.view.render(model, mode.value)
            pygame.display.flip()

        # Exit pygame cleanly if the loop ends.
        pygame.quit()
        sys.exit()
