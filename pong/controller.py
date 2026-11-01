import sys

import pygame

from .model import GameMode, GameModel, WINDOW_HEIGHT, WINDOW_WIDTH
from .view import PongView


class PongController:
    def __init__(self) -> None:
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Pong")
        self.clock = pygame.time.Clock()
        self.view = PongView(self.screen)
        self.running = True

    def run(self) -> None:
        while self.running:
            mode = self.show_menu()
            if mode is None:
                break
            self.play_match(mode)

    def show_menu(self):
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
        model = GameModel(mode)

        while self.running:
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

            if mode == GameMode.TWO_PLAYER:
                if keys[pygame.K_w]:
                    left_direction = -1
                elif keys[pygame.K_s]:
                    left_direction = 1

                if keys[pygame.K_UP]:
                    right_direction = -1
                elif keys[pygame.K_DOWN]:
                    right_direction = 1
            else:
                if keys[pygame.K_w]:
                    left_direction = -1
                elif keys[pygame.K_s]:
                    left_direction = 1

            model.handle_player_movement(left_direction, right_direction, dt)
            model.update_cpu(dt)
            model.update_ball(dt)

            self.view.render(model, mode.value)
            pygame.display.flip()

        pygame.quit()
        sys.exit()
