"""
Scenes package for the Zelda-like 2D game.
Contains the scene system for managing different game states.
"""

from .scene import Scene
from .scene_manager import SceneManager
from .game_scene import GameScene
from .game_over_scene import GameOverScene

__all__ = ['Scene', 'SceneManager', 'GameScene', 'GameOverScene']