"""
Item class for collectible objects in the game.
"""
import pygame
from typing import Dict, Any, Optional, Callable
from .game_object import GameObject


class Item(GameObject):
    """
    Base class for all collectible items in the game.
    """
    
    # Item type definitions
    ITEM_TYPES = {
        'health_potion': {
            'name': 'Health Potion',
            'type': 'consumable',
            'effect': {'health': 50},
            'color': (255, 100, 100),  # Red
            'description': 'Restores 50 health points'
        },
        'mana_potion': {
            'name': 'Mana Potion',
            'type': 'consumable',
            'effect': {'mana': 30},
            'color': (100, 100, 255),  # Blue
            'description': 'Restores 30 mana points'
        },
        'iron_sword': {
            'name': 'Iron Sword',
            'type': 'weapon',
            'effect': {'attack': 15},
            'color': (150, 150, 150),  # Gray
            'description': 'A sturdy iron sword. +15 attack power'
        },
        'leather_armor': {
            'name': 'Leather Armor',
            'type': 'armor',
            'effect': {'defense': 10},
            'color': (139, 69, 19),  # Brown
            'description': 'Basic leather armor. +10 defense'
        },
        'speed_boots': {
            'name': 'Speed Boots',
            'type': 'equipment',
            'effect': {'speed': 1.5},
            'color': (255, 255, 0),  # Yellow
            'description': 'Increases movement speed by 50%'
        },
        'experience_gem': {
            'name': 'Experience Gem',
            'type': 'consumable',
            'effect': {'experience': 25},
            'color': (0, 255, 0),  # Green
            'description': 'Grants 25 experience points'
        },
        'strength_potion': {
            'name': 'Strength Potion',
            'type': 'consumable',
            'effect': {'attack_boost': 10, 'duration': 30},
            'color': (255, 165, 0),  # Orange
            'description': 'Temporarily increases attack power by 10 for 30 seconds'
        },
        'speed_potion': {
            'name': 'Speed Potion',
            'type': 'consumable',
            'effect': {'speed_boost': 1.5, 'duration': 20},
            'color': (255, 255, 100),  # Light Yellow
            'description': 'Temporarily increases movement speed by 50% for 20 seconds'
        },
        'magic_ring': {
            'name': 'Magic Ring',
            'type': 'equipment',
            'effect': {'health_regen': 2},
            'color': (128, 0, 128),  # Purple
            'description': 'Slowly regenerates health over time'
        }
    }
    
    def __init__(self, x: float, y: float, item_type: str):
        """
        Initialize an Item.
        
        Args:
            x: X position in world coordinates
            y: Y position in world coordinates
            item_type: Type of item (must be in ITEM_TYPES)
        """
        super().__init__(x, y, 24, 24)  # Items are 24x24 pixels
        
        if item_type not in self.ITEM_TYPES:
            raise ValueError(f"Unknown item type: {item_type}")
        
        self.item_type = item_type
        self.item_data = self.ITEM_TYPES[item_type].copy()
        
        # Item properties
        self.name = self.item_data['name']
        self.category = self.item_data['type']
        self.effect = self.item_data['effect'].copy()
        self.description = self.item_data['description']
        
        # Visual properties
        self.color = self.item_data['color']
        self.collected = False
        
        # Animation properties
        self.bob_time = 0.0
        self.bob_speed = 2.0  # Speed of bobbing animation
        self.bob_height = 3.0  # Height of bobbing animation
        self.original_y = y
        
        # Collection properties
        self.collection_radius = 16  # Pixels - how close player needs to be
        self.auto_collect = True  # Whether item is collected automatically on contact
        
        # Create sprite
        self._create_sprite()
    
    def _create_sprite(self) -> None:
        """Create the visual sprite for this item."""
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill(self.color)
        
        # Add visual details based on item type
        if self.category == 'consumable':
            self._create_potion_sprite()
        elif self.category == 'weapon':
            self._create_weapon_sprite()
        elif self.category == 'armor':
            self._create_armor_sprite()
        elif self.category == 'equipment':
            self._create_equipment_sprite()
        else:
            self._create_generic_sprite()
    
    def load_sprite_from_loader(self, sprite_loader) -> None:
        """
        Load item sprite using sprite loader.
        
        Args:
            sprite_loader: SpriteLoader instance
        """
        loaded_sprite = sprite_loader.load_item_sprite(self.item_type, self.width, self.height)
        if loaded_sprite:
            self.sprite = loaded_sprite
    
    def _create_potion_sprite(self) -> None:
        """Create sprite for potion items."""
        # Draw bottle shape
        pygame.draw.rect(self.sprite, self.color, (6, 8, 12, 14))
        # Draw bottle neck
        pygame.draw.rect(self.sprite, (100, 100, 100), (9, 4, 6, 6))
        # Draw cork
        pygame.draw.rect(self.sprite, (139, 69, 19), (8, 2, 8, 4))
        # Add shine effect
        pygame.draw.rect(self.sprite, (255, 255, 255), (8, 10, 2, 8))
    
    def _create_weapon_sprite(self) -> None:
        """Create sprite for weapon items."""
        # Draw sword blade
        pygame.draw.rect(self.sprite, self.color, (10, 2, 4, 16))
        # Draw sword hilt
        pygame.draw.rect(self.sprite, (139, 69, 19), (8, 16, 8, 4))
        # Draw sword guard
        pygame.draw.rect(self.sprite, (100, 100, 100), (6, 14, 12, 2))
        # Add blade shine
        pygame.draw.rect(self.sprite, (255, 255, 255), (11, 4, 1, 12))
    
    def _create_armor_sprite(self) -> None:
        """Create sprite for armor items."""
        # Draw armor chest piece
        pygame.draw.rect(self.sprite, self.color, (4, 6, 16, 12))
        # Draw shoulder pieces
        pygame.draw.rect(self.sprite, self.color, (2, 4, 6, 6))
        pygame.draw.rect(self.sprite, self.color, (16, 4, 6, 6))
        # Add details
        pygame.draw.rect(self.sprite, (200, 200, 200), (6, 8, 12, 2))
        pygame.draw.rect(self.sprite, (200, 200, 200), (6, 12, 12, 2))
    
    def _create_equipment_sprite(self) -> None:
        """Create sprite for equipment items."""
        # Draw boot shape for speed boots
        if 'speed' in self.effect:
            pygame.draw.ellipse(self.sprite, self.color, (2, 8, 20, 12))
            pygame.draw.rect(self.sprite, self.color, (2, 12, 20, 8))
            # Add laces
            pygame.draw.line(self.sprite, (255, 255, 255), (6, 10), (18, 10), 1)
            pygame.draw.line(self.sprite, (255, 255, 255), (6, 14), (18, 14), 1)
        else:
            self._create_generic_sprite()
    
    def _create_generic_sprite(self) -> None:
        """Create generic sprite for unknown item types."""
        # Draw a gem-like shape
        points = [
            (12, 2),   # Top
            (20, 8),   # Right
            (16, 20),  # Bottom right
            (8, 20),   # Bottom left
            (4, 8),    # Left
        ]
        pygame.draw.polygon(self.sprite, self.color, points)
        # Add shine
        pygame.draw.polygon(self.sprite, (255, 255, 255), [
            (12, 4), (16, 8), (12, 12), (8, 8)
        ])
    
    def update(self, dt: float) -> None:
        """
        Update the item state.
        
        Args:
            dt: Delta time since last frame in seconds
        """
        if self.collected:
            return
        
        # Update bobbing animation
        self.bob_time += dt * self.bob_speed
        import math
        bob_offset = pygame.math.Vector2(0, self.bob_height * math.sin(self.bob_time))
        self.y = self.original_y + bob_offset.y
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """
        Render the item to the screen.
        
        Args:
            screen: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if self.collected or not self.active:
            return
        
        # Convert world coordinates to screen coordinates
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Only render if item is visible on screen
        if (screen_x + self.width >= 0 and screen_x < screen.get_width() and
            screen_y + self.height >= 0 and screen_y < screen.get_height()):
            
            # Add glow effect for items
            glow_surface = pygame.Surface((self.width + 4, self.height + 4))
            glow_surface.set_alpha(100)
            glow_surface.fill(self.color)
            screen.blit(glow_surface, (screen_x - 2, screen_y - 2))
            
            # Render the main sprite
            screen.blit(self.sprite, (screen_x, screen_y))
    
    def can_be_collected_by(self, player) -> bool:
        """
        Check if this item can be collected by the given player.
        
        Args:
            player: Player object attempting to collect
            
        Returns:
            True if item can be collected, False otherwise
        """
        if self.collected or not self.active:
            return False
        
        # Check if player is close enough
        player_center = player.get_center()
        item_center = self.get_center()
        
        distance = pygame.math.Vector2(
            player_center[0] - item_center[0],
            player_center[1] - item_center[1]
        ).length()
        
        return distance <= self.collection_radius
    
    def collect(self, player) -> bool:
        """
        Attempt to collect this item.
        
        Args:
            player: Player object collecting the item
            
        Returns:
            True if item was successfully collected, False otherwise
        """
        if not self.can_be_collected_by(player):
            return False
        
        # Try to add item to player's inventory
        if self.category == 'consumable':
            # Consumables are used immediately or added to inventory
            success = self._apply_consumable_effect(player)
        else:
            # Equipment and weapons go to inventory
            success = player.add_item(self)
        
        if success:
            self.collected = True
            self.active = False
            self._on_collected(player)
            return True
        
        return False
    
    def _apply_consumable_effect(self, player) -> bool:
        """
        Apply the effect of a consumable item directly to the player.
        
        Args:
            player: Player to apply effect to
            
        Returns:
            True if effect was applied successfully
        """
        if 'health' in self.effect:
            # Only heal if player is not at full health
            if player.current_health < player.max_health:
                player.heal(self.effect['health'])
                return True
            else:
                # Player is at full health, add to inventory instead
                return player.add_item(self)
        
        elif 'mana' in self.effect:
            # TODO: Implement mana system
            print(f"Player would gain {self.effect['mana']} mana")
            return True
        
        elif 'experience' in self.effect:
            player.add_experience(self.effect['experience'])
            return True
        
        elif 'attack_boost' in self.effect or 'speed_boost' in self.effect:
            # Apply temporary status effect
            effect_name = f"{self.item_type}_effect"
            player.apply_status_effect(effect_name, self.effect)
            return True
        
        else:
            # Unknown consumable effect, add to inventory
            return player.add_item(self)
    
    def _on_collected(self, player) -> None:
        """
        Called when the item is successfully collected.
        
        Args:
            player: Player who collected the item
        """
        print(f"Collected {self.name}: {self.description}")
    
    def use_on_player(self, player) -> bool:
        """
        Use this item on a player (for inventory usage).
        
        Args:
            player: Player to use item on
            
        Returns:
            True if item was used successfully
        """
        if self.category == 'consumable':
            return self._apply_consumable_effect(player)
        elif self.category in ['weapon', 'armor', 'equipment']:
            # For equipment items, use the player's equip method which goes through inventory
            return player.equip_item(self)
        
        return False
    
    def _equip_item(self, player) -> bool:
        """
        Equip this item on the player.
        
        Args:
            player: Player to equip item on
            
        Returns:
            True if item was equipped successfully
        """
        print(f"Equipped {self.name} on player")
        
        # The actual stat application will be handled by the inventory system
        # when the item is equipped, to avoid double application
        return True
    
    def get_info(self) -> Dict[str, Any]:
        """
        Get detailed information about this item.
        
        Returns:
            Dictionary containing item information
        """
        return {
            'name': self.name,
            'type': self.item_type,
            'category': self.category,
            'effect': self.effect.copy(),
            'description': self.description,
            'position': (self.x, self.y),
            'collected': self.collected,
            'active': self.active
        }
    
    @classmethod
    def create_random_item(cls, x: float, y: float) -> 'Item':
        """
        Create a random item at the specified position.
        
        Args:
            x: X position
            y: Y position
            
        Returns:
            Random Item instance
        """
        import random
        item_type = random.choice(list(cls.ITEM_TYPES.keys()))
        return cls(x, y, item_type)
    
    @classmethod
    def get_item_types(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get all available item types.
        
        Returns:
            Dictionary of item type definitions
        """
        return cls.ITEM_TYPES.copy()