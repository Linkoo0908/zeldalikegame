"""
Item system for managing item collection and interactions.
"""
import pygame
from typing import List, Optional
from src.objects.item import Item
from src.objects.player import Player
from src.systems.collision_system import CollisionSystem


class ItemSystem:
    """
    System for managing items in the game world.
    """
    
    def __init__(self, collision_system: CollisionSystem):
        """
        Initialize the item system.
        
        Args:
            collision_system: Collision system for detecting item collection
        """
        self.collision_system = collision_system
        self.items: List[Item] = []
        self.collected_items: List[Item] = []
    
    def add_item(self, item: Item) -> None:
        """
        Add an item to the game world.
        
        Args:
            item: Item to add
        """
        if item not in self.items:
            self.items.append(item)
    
    def remove_item(self, item: Item) -> None:
        """
        Remove an item from the game world.
        
        Args:
            item: Item to remove
        """
        if item in self.items:
            self.items.remove(item)
    
    def create_item(self, x: float, y: float, item_type: str) -> Item:
        """
        Create and add a new item to the world.
        
        Args:
            x: X position
            y: Y position
            item_type: Type of item to create
            
        Returns:
            Created Item instance
        """
        item = Item(x, y, item_type)
        self.add_item(item)
        return item
    
    def update(self, dt: float, player: Player) -> None:
        """
        Update all items and handle collection.
        
        Args:
            dt: Delta time since last frame
            player: Player object for collection detection
        """
        # Update all active items
        for item in self.items[:]:  # Use slice to avoid modification during iteration
            if item.active:
                item.update(dt)
                
                # Check for collection
                if item.can_be_collected_by(player):
                    if item.collect(player):
                        self.collected_items.append(item)
                        self.remove_item(item)
            else:
                # Remove inactive items
                self.remove_item(item)
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """
        Render all active items.
        
        Args:
            screen: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        for item in self.items:
            if item.active:
                item.render(screen, camera_x, camera_y)
    
    def get_items_near_position(self, x: float, y: float, radius: float) -> List[Item]:
        """
        Get all items within a certain radius of a position.
        
        Args:
            x: X position
            y: Y position
            radius: Search radius
            
        Returns:
            List of items within radius
        """
        nearby_items = []
        
        for item in self.items:
            if not item.active:
                continue
            
            item_center = item.get_center()
            distance = pygame.math.Vector2(
                x - item_center[0],
                y - item_center[1]
            ).length()
            
            if distance <= radius:
                nearby_items.append(item)
        
        return nearby_items
    
    def get_items_by_type(self, item_type: str) -> List[Item]:
        """
        Get all items of a specific type.
        
        Args:
            item_type: Type of items to find
            
        Returns:
            List of items of the specified type
        """
        return [item for item in self.items if item.item_type == item_type and item.active]
    
    def get_items_by_category(self, category: str) -> List[Item]:
        """
        Get all items of a specific category.
        
        Args:
            category: Category of items to find ('consumable', 'weapon', 'armor', 'equipment')
            
        Returns:
            List of items of the specified category
        """
        return [item for item in self.items if item.category == category and item.active]
    
    def clear_all_items(self) -> None:
        """Remove all items from the world."""
        self.items.clear()
        self.collected_items.clear()
    
    def spawn_item_drop(self, x: float, y: float, item_type: Optional[str] = None) -> Item:
        """
        Spawn an item drop at a specific location (e.g., when enemy dies).
        
        Args:
            x: X position
            y: Y position
            item_type: Specific item type to spawn, or None for random
            
        Returns:
            Spawned Item instance
        """
        if item_type is None:
            item = Item.create_random_item(x, y)
        else:
            item = Item(x, y, item_type)
        
        self.add_item(item)
        return item
    
    def get_active_item_count(self) -> int:
        """
        Get the number of active items in the world.
        
        Returns:
            Number of active items
        """
        return len([item for item in self.items if item.active])
    
    def get_collected_item_count(self) -> int:
        """
        Get the number of items that have been collected.
        
        Returns:
            Number of collected items
        """
        return len(self.collected_items)
    
    def get_item_stats(self) -> dict:
        """
        Get statistics about items in the system.
        
        Returns:
            Dictionary containing item statistics
        """
        stats = {
            'total_items': len(self.items),
            'active_items': self.get_active_item_count(),
            'collected_items': self.get_collected_item_count(),
            'items_by_category': {}
        }
        
        # Count items by category
        for category in ['consumable', 'weapon', 'armor', 'equipment']:
            stats['items_by_category'][category] = len(self.get_items_by_category(category))
        
        return stats