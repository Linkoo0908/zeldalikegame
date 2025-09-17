"""
Door class for stage transitions and locked areas.
"""
import pygame
from typing import Tuple, Optional
from .game_object import GameObject


class Door(GameObject):
    """
    Door object that can be locked/unlocked and provides stage transitions.
    """
    
    def __init__(self, x: float, y: float, door_id: str, 
                 target_map: str = None, target_position: Tuple[float, float] = None,
                 width: float = 32, height: float = 32):
        """
        Initialize the Door.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
            door_id: Unique identifier for this door
            target_map: Path to target map (optional)
            target_position: Target position in new map (optional)
            width: Door width in pixels
            height: Door height in pixels
        """
        super().__init__(x, y, width, height)
        
        self.door_id = door_id
        self.target_map = target_map
        self.target_position = target_position or (0, 0)
        
        # Door state
        self.is_locked = True  # Doors start locked by default
        self.is_open = False
        self.unlock_condition = "clear_enemies"  # Condition to unlock
        
        # Visual properties
        self.locked_color = (139, 69, 19)    # Brown - locked door
        self.unlocked_color = (34, 139, 34)  # Green - unlocked door
        self.open_color = (255, 215, 0)      # Gold - open door
        
        # Animation properties
        self.glow_time = 0.0
        self.glow_speed = 3.0
        self.unlock_animation_time = 0.0
        self.unlock_animation_duration = 2.0
        self.is_unlocking = False
        
        # Interaction properties
        self.interaction_radius = 40  # Pixels - how close player needs to be
        self.can_interact = False
        
        # Create sprite
        self._create_sprite()
    
    def _create_sprite(self) -> None:
        """Create the visual sprite for this door."""
        self.sprite = pygame.Surface((self.width, self.height))
        self._update_sprite()
    
    def _update_sprite(self) -> None:
        """Update sprite based on current door state."""
        if self.is_open:
            color = self.open_color
        elif self.is_locked:
            color = self.locked_color
        else:
            color = self.unlocked_color
        
        self.sprite.fill(color)
        
        # Add door details
        if self.is_open:
            # Open door - show opening
            pygame.draw.rect(self.sprite, (0, 0, 0), (8, 4, 16, 24))  # Opening
            pygame.draw.rect(self.sprite, color, (2, 0, 6, 32))       # Left frame
            pygame.draw.rect(self.sprite, color, (24, 0, 6, 32))      # Right frame
        else:
            # Closed door
            pygame.draw.rect(self.sprite, color, (0, 0, self.width, self.height))
            
            # Door handle
            handle_color = (255, 255, 255) if not self.is_locked else (100, 100, 100)
            pygame.draw.circle(self.sprite, handle_color, (int(self.width * 0.8), int(self.height // 2)), 3)
            
            # Lock indicator
            if self.is_locked:
                # Draw lock symbol
                pygame.draw.rect(self.sprite, (50, 50, 50), (12, 10, 8, 6))  # Lock body
                pygame.draw.circle(self.sprite, (50, 50, 50), (16, 8), 3, 2)  # Lock shackle
            
            # Door panels
            pygame.draw.rect(self.sprite, tuple(max(0, c - 20) for c in color), (4, 4, self.width - 8, 10))
            pygame.draw.rect(self.sprite, tuple(max(0, c - 20) for c in color), (4, 18, self.width - 8, 10))
    
    def update(self, dt: float, player_position: Optional[Tuple[float, float]] = None) -> None:
        """
        Update the door state.
        
        Args:
            dt: Delta time since last frame in seconds
            player_position: Current player position for interaction checks
        """
        # Update glow animation
        self.glow_time += dt * self.glow_speed
        
        # Update unlock animation
        if self.is_unlocking:
            self.unlock_animation_time += dt
            if self.unlock_animation_time >= self.unlock_animation_duration:
                self.is_unlocking = False
                self.unlock_animation_time = 0.0
                self._update_sprite()
        
        # Check player interaction
        if player_position:
            distance = pygame.math.Vector2(
                player_position[0] - (self.x + self.width / 2),
                player_position[1] - (self.y + self.height / 2)
            ).length()
            
            self.can_interact = distance <= self.interaction_radius and not self.is_locked
    
    def unlock(self) -> None:
        """Unlock the door with animation."""
        if not self.is_locked:
            return
        
        print(f"Door {self.door_id} is unlocking!")
        self.is_locked = False
        self.is_unlocking = True
        self.unlock_animation_time = 0.0
        self._update_sprite()
    
    def open(self) -> None:
        """Open the door."""
        if self.is_locked:
            return
        
        print(f"Door {self.door_id} is opening!")
        self.is_open = True
        self._update_sprite()
    
    def close(self) -> None:
        """Close the door."""
        print(f"Door {self.door_id} is closing!")
        self.is_open = False
        self._update_sprite()
    
    def can_pass_through(self) -> bool:
        """
        Check if player can pass through this door.
        
        Returns:
            True if door is open and unlocked
        """
        return not self.is_locked and self.is_open
    
    def try_interact(self, player) -> bool:
        """
        Try to interact with the door.
        
        Args:
            player: Player attempting to interact
            
        Returns:
            True if interaction was successful
        """
        if not self.can_interact:
            return False
        
        if self.is_locked:
            print(f"Door {self.door_id} is locked!")
            return False
        
        if not self.is_open:
            self.open()
            return True
        
        return False
    
    def get_transition_data(self) -> Tuple[str, Tuple[float, float]]:
        """
        Get transition data for this door.
        
        Returns:
            Tuple of (target_map, target_position)
        """
        return (self.target_map, self.target_position)
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """
        Render the door to the screen.
        
        Args:
            screen: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if not self.active:
            return
        
        # Convert world coordinates to screen coordinates
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Only render if door is visible on screen
        if (screen_x + self.width >= 0 and screen_x < screen.get_width() and
            screen_y + self.height >= 0 and screen_y < screen.get_height()):
            
            # Render glow effect for unlocked/unlocking doors
            if not self.is_locked or self.is_unlocking:
                self._render_glow_effect(screen, screen_x, screen_y)
            
            # Render the main sprite
            screen.blit(self.sprite, (screen_x, screen_y))
            
            # Render interaction indicator
            if self.can_interact:
                self._render_interaction_indicator(screen, screen_x, screen_y)
    
    def _render_glow_effect(self, screen: pygame.Surface, screen_x: int, screen_y: int) -> None:
        """
        Render glow effect for unlocked doors.
        
        Args:
            screen: Pygame surface to render to
            screen_x: Screen X position
            screen_y: Screen Y position
        """
        import math
        
        # Calculate glow intensity
        if self.is_unlocking:
            # Pulsing glow during unlock animation
            progress = self.unlock_animation_time / self.unlock_animation_duration
            intensity = int(100 * (1.0 + math.sin(progress * math.pi * 8)) / 2)
        else:
            # Gentle glow for unlocked doors
            intensity = int(50 * (1.0 + math.sin(self.glow_time)) / 2)
        
        if intensity > 0:
            glow_surface = pygame.Surface((self.width + 8, self.height + 8))
            glow_surface.set_alpha(intensity)
            
            if self.is_unlocking:
                glow_surface.fill((255, 255, 0))  # Yellow glow during unlock
            else:
                glow_surface.fill((0, 255, 0))    # Green glow when unlocked
            
            screen.blit(glow_surface, (screen_x - 4, screen_y - 4))
    
    def _render_interaction_indicator(self, screen: pygame.Surface, screen_x: int, screen_y: int) -> None:
        """
        Render interaction indicator above the door.
        
        Args:
            screen: Pygame surface to render to
            screen_x: Screen X position
            screen_y: Screen Y position
        """
        # Draw "E" key indicator
        try:
            font = pygame.font.Font(None, 24)
            text = font.render("E", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen_x + self.width // 2, screen_y - 20))
            
            # Background circle
            pygame.draw.circle(screen, (0, 0, 0), text_rect.center, 12)
            pygame.draw.circle(screen, (255, 255, 255), text_rect.center, 12, 2)
            
            screen.blit(text, text_rect)
        except pygame.error:
            # Fallback if font fails
            pygame.draw.circle(screen, (255, 255, 255), (screen_x + self.width // 2, screen_y - 20), 8)
    
    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.
        
        Returns:
            Pygame Rect representing the door's bounds
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def get_info(self) -> dict:
        """
        Get door information.
        
        Returns:
            Dictionary containing door information
        """
        return {
            'door_id': self.door_id,
            'position': (self.x, self.y),
            'size': (self.width, self.height),
            'is_locked': self.is_locked,
            'is_open': self.is_open,
            'target_map': self.target_map,
            'target_position': self.target_position,
            'can_interact': self.can_interact,
            'unlock_condition': self.unlock_condition
        }