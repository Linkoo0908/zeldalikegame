"""
Sprite loader utility for loading game object sprites from image files.
"""
import pygame
from typing import Optional, Dict
from src.core.resource_manager import ResourceManager


class SpriteLoader:
    """
    Utility class for loading sprites for game objects.
    Provides fallback to programmatic sprite creation if images are not found.
    """
    
    def __init__(self, resource_manager: ResourceManager):
        """
        Initialize the sprite loader.
        
        Args:
            resource_manager: Resource manager for loading images
        """
        self.resource_manager = resource_manager
        
        # Sprite mapping for different game objects
        self.sprite_map = {
            'player': 'player.png',
            'goblin': 'goblin.png',
            'orc': 'orc.png',
            'health_potion': 'health_potion.png',
            'mana_potion': 'health_potion.png',  # Reuse health potion for now
            'iron_sword': 'sword.png',
            'sword': 'sword.png',
            'leather_armor': 'sword.png',  # Reuse sword for now
            'speed_boots': 'sword.png',  # Reuse sword for now
        }
    
    def load_player_sprite(self, width: int = 32, height: int = 32) -> pygame.Surface:
        """
        Load player sprite.
        
        Args:
            width: Desired sprite width
            height: Desired sprite height
            
        Returns:
            Pygame surface with player sprite
        """
        sprite_path = self.sprite_map.get('player')
        if sprite_path:
            sprite = self.resource_manager.load_image(sprite_path)
            if sprite and (sprite.get_width() != width or sprite.get_height() != height):
                sprite = pygame.transform.scale(sprite, (width, height))
            if sprite:
                return sprite
        
        # Fallback to programmatic sprite
        return self._create_fallback_player_sprite(width, height)
    
    def load_enemy_sprite(self, enemy_type: str, width: int = 32, height: int = 32) -> pygame.Surface:
        """
        Load enemy sprite based on type.
        
        Args:
            enemy_type: Type of enemy
            width: Desired sprite width
            height: Desired sprite height
            
        Returns:
            Pygame surface with enemy sprite
        """
        sprite_path = self.sprite_map.get(enemy_type)
        if sprite_path:
            sprite = self.resource_manager.load_image(sprite_path)
            if sprite and (sprite.get_width() != width or sprite.get_height() != height):
                sprite = pygame.transform.scale(sprite, (width, height))
            if sprite:
                return sprite
        
        # Fallback to programmatic sprite
        return self._create_fallback_enemy_sprite(enemy_type, width, height)
    
    def load_item_sprite(self, item_type: str, width: int = 24, height: int = 24) -> pygame.Surface:
        """
        Load item sprite based on type.
        
        Args:
            item_type: Type of item
            width: Desired sprite width
            height: Desired sprite height
            
        Returns:
            Pygame surface with item sprite
        """
        sprite_path = self.sprite_map.get(item_type)
        if sprite_path:
            sprite = self.resource_manager.load_image(sprite_path)
            if sprite and (sprite.get_width() != width or sprite.get_height() != height):
                sprite = pygame.transform.scale(sprite, (width, height))
            if sprite:
                return sprite
        
        # Fallback to programmatic sprite
        return self._create_fallback_item_sprite(item_type, width, height)
    
    def _create_fallback_player_sprite(self, width: int, height: int) -> pygame.Surface:
        """Create fallback player sprite programmatically."""
        sprite = pygame.Surface((width, height))
        sprite.fill((0, 100, 200))  # Blue
        
        # Add simple eyes
        pygame.draw.circle(sprite, (255, 255, 255), (8, 8), 3)
        pygame.draw.circle(sprite, (255, 255, 255), (24, 8), 3)
        pygame.draw.circle(sprite, (0, 0, 0), (8, 8), 1)
        pygame.draw.circle(sprite, (0, 0, 0), (24, 8), 1)
        
        return sprite
    
    def _create_fallback_enemy_sprite(self, enemy_type: str, width: int, height: int) -> pygame.Surface:
        """Create fallback enemy sprite programmatically."""
        sprite = pygame.Surface((width, height))
        
        # Different colors for different enemy types
        enemy_colors = {
            "basic": (150, 50, 50),      # Dark red
            "goblin": (50, 150, 50),     # Dark green
            "orc": (100, 50, 100),       # Dark purple
            "skeleton": (200, 200, 200)  # Light gray
        }
        
        color = enemy_colors.get(enemy_type, enemy_colors["basic"])
        sprite.fill(color)
        
        # Add simple visual features
        pygame.draw.circle(sprite, (255, 0, 0), (8, 8), 3)   # Red eyes
        pygame.draw.circle(sprite, (255, 0, 0), (24, 8), 3)
        pygame.draw.rect(sprite, (255, 255, 255), (12, 20, 8, 4))  # Teeth
        
        return sprite
    
    def _create_fallback_item_sprite(self, item_type: str, width: int, height: int) -> pygame.Surface:
        """Create fallback item sprite programmatically."""
        sprite = pygame.Surface((width, height))
        
        # Item colors
        item_colors = {
            'health_potion': (255, 100, 100),  # Red
            'mana_potion': (100, 100, 255),    # Blue
            'iron_sword': (150, 150, 150),     # Gray
            'sword': (200, 200, 100),          # Yellow
            'leather_armor': (139, 69, 19),    # Brown
            'speed_boots': (255, 255, 0),      # Yellow
        }
        
        color = item_colors.get(item_type, (255, 0, 255))  # Default magenta
        sprite.fill(color)
        
        # Add simple details based on type
        if 'potion' in item_type:
            # Add cross symbol for potions
            pygame.draw.rect(sprite, (255, 255, 255), (width//2-1, 4, 2, height-8))
            pygame.draw.rect(sprite, (255, 255, 255), (4, height//2-1, width-8, 2))
        elif 'sword' in item_type:
            # Add simple sword shape
            pygame.draw.rect(sprite, (150, 150, 150), (width//2-1, 2, 2, height-6))  # Blade
            pygame.draw.rect(sprite, (100, 50, 0), (width//2-2, height-4, 4, 2))     # Handle
        
        return sprite