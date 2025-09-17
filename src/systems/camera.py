"""
Camera system for handling viewport and rendering offset.
"""
import pygame
from typing import Tuple, Optional


class Camera:
    """Camera system for managing viewport and rendering offsets."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize camera.
        
        Args:
            screen_width: Width of the screen/viewport
            screen_height: Height of the screen/viewport
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = 0.0
        self.y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0
        self.follow_speed = 5.0
        self.bounds = None  # (min_x, min_y, max_x, max_y)
        
    def set_position(self, x: float, y: float) -> None:
        """
        Set camera position directly.
        
        Args:
            x: X position
            y: Y position
        """
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self._apply_bounds()
    
    def set_target(self, x: float, y: float) -> None:
        """
        Set camera target position for smooth following.
        
        Args:
            x: Target X position
            y: Target Y position
        """
        self.target_x = x
        self.target_y = y
    
    def follow_target(self, target_x: float, target_y: float, dt: float) -> None:
        """
        Smoothly follow a target position.
        
        Args:
            target_x: Target X position to follow
            target_y: Target Y position to follow
            dt: Delta time for smooth movement
        """
        # Center camera on target
        self.target_x = target_x - self.screen_width // 2
        self.target_y = target_y - self.screen_height // 2
        
        # Smooth movement towards target
        speed = self.follow_speed * dt * 60  # Normalize for 60 FPS
        
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        self.x += dx * speed
        self.y += dy * speed
        
        self._apply_bounds()
    
    def set_bounds(self, min_x: float, min_y: float, max_x: float, max_y: float) -> None:
        """
        Set camera movement bounds.
        
        Args:
            min_x: Minimum X position
            min_y: Minimum Y position
            max_x: Maximum X position
            max_y: Maximum Y position
        """
        self.bounds = (min_x, min_y, max_x, max_y)
        self._apply_bounds()
    
    def _apply_bounds(self) -> None:
        """Apply camera bounds constraints."""
        if self.bounds:
            min_x, min_y, max_x, max_y = self.bounds
            self.x = max(min_x, min(self.x, max_x - self.screen_width))
            self.y = max(min_y, min(self.y, max_y - self.screen_height))
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """
        Convert world coordinates to screen coordinates.
        
        Args:
            world_x: World X coordinate
            world_y: World Y coordinate
            
        Returns:
            Tuple of (screen_x, screen_y)
        """
        return (world_x - self.x, world_y - self.y)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """
        Convert screen coordinates to world coordinates.
        
        Args:
            screen_x: Screen X coordinate
            screen_y: Screen Y coordinate
            
        Returns:
            Tuple of (world_x, world_y)
        """
        return (screen_x + self.x, screen_y + self.y)
    
    def get_visible_area(self) -> Tuple[float, float, float, float]:
        """
        Get the visible area in world coordinates.
        
        Returns:
            Tuple of (left, top, right, bottom) in world coordinates
        """
        return (
            self.x,
            self.y,
            self.x + self.screen_width,
            self.y + self.screen_height
        )
    
    def is_visible(self, x: float, y: float, width: float, height: float) -> bool:
        """
        Check if a rectangle is visible in the camera view.
        
        Args:
            x: Rectangle X position
            y: Rectangle Y position
            width: Rectangle width
            height: Rectangle height
            
        Returns:
            True if rectangle is visible, False otherwise
        """
        left, top, right, bottom = self.get_visible_area()
        
        return not (x + width < left or x > right or y + height < top or y > bottom)
    
    def get_offset(self) -> Tuple[int, int]:
        """
        Get camera offset as integers for rendering.
        
        Returns:
            Tuple of (offset_x, offset_y)
        """
        return (int(self.x), int(self.y))