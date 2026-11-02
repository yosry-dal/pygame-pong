# This is the entry point for the Pong game.
# It creates the controller and starts the main game loop.

from pong.controller import PongController


def main() -> None:
    """Create the controller instance and start the game."""
    controller = PongController()
    controller.run()


if __name__ == "__main__":
    # Run the game only when this file is executed directly.
    main()
