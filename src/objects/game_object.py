"""
GameObject base class for all game entities.
Provides basic functionality for position, size, rendering, and updates.
"""
import pygame
from typing import Tuple, Optional


class GameObject:
    """
    Base class for all game objects in the game.
    Provides common functionality like position, size, rendering interface.
    """
    
    def __init__(self, x: float, y: float, width: int = 32, height: int = 32):
        """
        Initialize a GameObject.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates  
            width: Width of the object in pixels
            height: Height of the object in pixels
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.sprite: Optional[pygame.Surface] = None
        self.active = True
        
    def update(self, dt: float) -> None:
        """
        Update the game object. Called every frame.
        
        Args:
            dt: Delta time since last frame in seconds
        """
        pass
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """
        Render the game object to the screen.
        
        Args:
            screen: Pygame surface to render to
            camera_x: Camera X offset for world-to-screen conversion
            camera_y: Camera Y offset for world-to-screen conversion
        """
        if not self.active or not self.sprite:
            return
            
        # Convert world coordinates to screen coordinates
        screen_x = self.x - camera_x
        screen_y = self.y - camera_y
        
        # Only render if object is visible on screen
        if (screen_x + self.width >= 0 and screen_x < screen.get_width() and
            screen_y + self.height >= 0 and screen_y < screen.get_height()):
            screen.blit(self.sprite, (screen_x, screen_y))
    
    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.
        
        Returns:
            pygame.Rect representing the object's bounds
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_position(self) -> Tuple[float, float]:
        """
        Get the current position of the object.
        
        Returns:
            Tuple of (x, y) coordinates
        """
        return (self.x, self.y)
    
    def set_position(self, x: float, y: float) -> None:
        """
        Set the position of the object.
        
        Args:
            x: New X coordinate
            y: New Y coordinate
        """
        self.x = x
        self.y = y
    
    def get_center(self) -> Tuple[float, float]:
        """
        Get the center point of the object.
        
        Returns:
            Tuple of (center_x, center_y) coordinates
        """
        return (self.x + self.width / 2, self.y + self.height / 2)
    
    def set_sprite(self, sprite: pygame.Surface) -> None:
        """
        Set the sprite for this object.
        
        Args:
            sprite: Pygame surface to use as the sprite
        """
        self.sprite = sprite
        if sprite:
            self.width = sprite.get_width()
            self.height = sprite.get_height()
    
    def destroy(self) -> None:
        """
        Mark this object for destruction/removal.
        """
        self.active = False
    
    def is_active(self) -> bool:
        """
        Check if this object is active.
        
        Returns:
            True if object is active, False otherwise
        """
        return self.active