"""Pong package initialization.

This file exposes the main parts of the game so they can be imported cleanly
from the package. It makes the project easier to organize and understand.
"""

from .controller import PongController
from .model import GameMode, GameModel
from .view import PongView

# These are the public classes and enums that other code can use.
__all__ = ["PongController", "GameModel", "GameMode", "PongView"]
