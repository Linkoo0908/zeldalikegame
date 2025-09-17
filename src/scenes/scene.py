"""
Base Scene class for the game's scene system.
Provides the interface that all scenes must implement.
"""
from abc import ABC, abstractmethod
from typing import Optional
import pygame


class Scene(ABC):
    """
    Abstract base class for all game scenes.
    Defines the interface that all scenes must implement.
    """
    
    def __init__(self, name: str):
        """
        Initialize the scene.
        
        Args:
            name: Unique name identifier for this scene
        """
        self.name = name
        self.active = False
        self.initialized = False
    
    @abstractmethod
    def initialize(self, game) -> None:
        """
        Initialize the scene with game resources.
        Called when the scene is first created or when it becomes active.
        
        Args:
            game: Reference to the main Game instance
        """
        pass
    
    @abstractmethod
    def cleanup(self) -> None:
        """
        Clean up scene resources.
        Called when the scene is being destroyed or replaced.
        """
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle a pygame event.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            True if the event was handled and should not be passed to other scenes,
            False if the event should continue to be processed
        """
        pass
    
    @abstractmethod
    def update(self, dt: float) -> None:
        """
        Update the scene state.
        
        Args:
            dt: Delta time since last frame in seconds
        """
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the scene to the screen.
        
        Args:
            screen: The pygame surface to render to
        """
        pass
    
    def on_enter(self) -> None:
        """
        Called when this scene becomes the active scene.
        Override in subclasses for scene-specific enter behavior.
        """
        self.active = True
    
    def on_exit(self) -> None:
        """
        Called when this scene is no longer the active scene.
        Override in subclasses for scene-specific exit behavior.
        """
        self.active = False
    
    def on_pause(self) -> None:
        """
        Called when this scene is paused (another scene is pushed on top).
        Override in subclasses for scene-specific pause behavior.
        """
        pass
    
    def on_resume(self) -> None:
        """
        Called when this scene is resumed (scene on top was popped).
        Override in subclasses for scene-specific resume behavior.
        """
        pass
    
    def is_active(self) -> bool:
        """
        Check if this scene is currently active.
        
        Returns:
            True if the scene is active, False otherwise
        """
        return self.active
    
    def is_initialized(self) -> bool:
        """
        Check if this scene has been initialized.
        
        Returns:
            True if the scene is initialized, False otherwise
        """
        return self.initialized
    
    def get_name(self) -> str:
        """
        Get the name of this scene.
        
        Returns:
            The scene's name
        """
        return self.name