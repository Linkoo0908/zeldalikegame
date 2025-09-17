"""
Unit tests for the ItemSystem class.
"""
import unittest
import pygame
from src.systems.item_system import ItemSystem
from src.systems.collision_system import CollisionSystem
from src.systems.map_system import MapSystem
from src.objects.item import Item
from src.objects.player import Player


class TestItemSystem(unittest.TestCase):
    """Test cases for ItemSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        # Create dependencies
        self.map_system = MapSystem()
        self.collision_system = CollisionSystem(self.map_system)
        self.item_system = ItemSystem(self.collision_system)
        
        self.player = Player(100, 100)
        self.test_x = 200
        self.test_y = 300
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_item_system_creation(self):
        """Test basic item system creation."""
        self.assertIsNotNone(self.item_system)
        self.assertEqual(len(self.item_system.items), 0)
        self.assertEqual(len(self.item_system.collected_items), 0)
    
    def test_add_item(self):
        """Test adding items to the system."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        self.item_system.add_item(item)
        
        self.assertIn(item, self.item_system.items)
        self.assertEqual(len(self.item_system.items), 1)
    
    def test_add_duplicate_item(self):
        """Test that duplicate items are not added."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        self.item_system.add_item(item)
        self.item_system.add_item(item)  # Try to add again
        
        self.assertEqual(len(self.item_system.items), 1)
    
    def test_remove_item(self):
        """Test removing items from the system."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        self.item_system.add_item(item)
        self.item_system.remove_item(item)
        
        self.assertNotIn(item, self.item_system.items)
        self.assertEqual(len(self.item_system.items), 0)
    
    def test_remove_nonexistent_item(self):
        """Test removing item that doesn't exist."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        # Should not raise exception
        self.item_system.remove_item(item)
        self.assertEqual(len(self.item_system.items), 0)
    
    def test_create_item(self):
        """Test creating and adding items through the system."""
        item = self.item_system.create_item(self.test_x, self.test_y, 'health_potion')
        
        self.assertIsInstance(item, Item)
        self.assertEqual(item.x, self.test_x)
        self.assertEqual(item.y, self.test_y)
        self.assertEqual(item.item_type, 'health_potion')
        self.assertIn(item, self.item_system.items)
    
    def test_update_items(self):
        """Test updating items in the system."""
        item = self.item_system.create_item(self.test_x, self.test_y, 'health_potion')
        original_y = item.y
        
        # Update should cause bobbing animation
        self.item_system.update(0.1, self.player)
        
        # Item should have updated (bobbing animation changes Y)
        self.assertNotEqual(item.y, original_y)
    
    def test_item_collection_during_update(self):
        """Test that items are collected during update when player is close."""
        item = self.item_system.create_item(self.test_x, self.test_y, 'health_potion')
        
        # Damage player so health potion will be used
        self.player.current_health = 50
        
        # Place player close to item
        self.player.x = self.test_x
        self.player.y = self.test_y
        
        # Update system
        self.item_system.update(0.1, self.player)
        
        # Item should be collected and removed from active items
        self.assertNotIn(item, self.item_system.items)
        self.assertIn(item, self.item_system.collected_items)
        self.assertTrue(item.collected)
        self.assertEqual(self.player.current_health, 100)
    
    def test_inactive_item_removal(self):
        """Test that inactive items are removed during update."""
        item = self.item_system.create_item(self.test_x, self.test_y, 'health_potion')
        
        # Make item inactive
        item.active = False
        
        # Update system
        self.item_system.update(0.1, self.player)
        
        # Item should be removed
        self.assertNotIn(item, self.item_system.items)
    
    def test_get_items_near_position(self):
        """Test finding items near a position."""
        # Create items at different distances
        close_item = self.item_system.create_item(100, 100, 'health_potion')
        far_item = self.item_system.create_item(200, 200, 'iron_sword')
        
        # Search near the close item
        nearby_items = self.item_system.get_items_near_position(100, 100, 50)
        
        self.assertIn(close_item, nearby_items)
        self.assertNotIn(far_item, nearby_items)
    
    def test_get_items_by_type(self):
        """Test finding items by type."""
        health_potion1 = self.item_system.create_item(100, 100, 'health_potion')
        health_potion2 = self.item_system.create_item(200, 200, 'health_potion')
        sword = self.item_system.create_item(300, 300, 'iron_sword')
        
        health_potions = self.item_system.get_items_by_type('health_potion')
        
        self.assertEqual(len(health_potions), 2)
        self.assertIn(health_potion1, health_potions)
        self.assertIn(health_potion2, health_potions)
        self.assertNotIn(sword, health_potions)
    
    def test_get_items_by_category(self):
        """Test finding items by category."""
        health_potion = self.item_system.create_item(100, 100, 'health_potion')
        mana_potion = self.item_system.create_item(200, 200, 'mana_potion')
        sword = self.item_system.create_item(300, 300, 'iron_sword')
        
        consumables = self.item_system.get_items_by_category('consumable')
        weapons = self.item_system.get_items_by_category('weapon')
        
        self.assertEqual(len(consumables), 2)
        self.assertIn(health_potion, consumables)
        self.assertIn(mana_potion, consumables)
        
        self.assertEqual(len(weapons), 1)
        self.assertIn(sword, weapons)
    
    def test_clear_all_items(self):
        """Test clearing all items."""
        self.item_system.create_item(100, 100, 'health_potion')
        self.item_system.create_item(200, 200, 'iron_sword')
        
        self.assertEqual(len(self.item_system.items), 2)
        
        self.item_system.clear_all_items()
        
        self.assertEqual(len(self.item_system.items), 0)
        self.assertEqual(len(self.item_system.collected_items), 0)
    
    def test_spawn_item_drop_specific(self):
        """Test spawning specific item drops."""
        item = self.item_system.spawn_item_drop(self.test_x, self.test_y, 'health_potion')
        
        self.assertEqual(item.x, self.test_x)
        self.assertEqual(item.y, self.test_y)
        self.assertEqual(item.item_type, 'health_potion')
        self.assertIn(item, self.item_system.items)
    
    def test_spawn_item_drop_random(self):
        """Test spawning random item drops."""
        item = self.item_system.spawn_item_drop(self.test_x, self.test_y)
        
        self.assertEqual(item.x, self.test_x)
        self.assertEqual(item.y, self.test_y)
        self.assertIn(item.item_type, Item.ITEM_TYPES.keys())
        self.assertIn(item, self.item_system.items)
    
    def test_get_active_item_count(self):
        """Test counting active items."""
        item1 = self.item_system.create_item(100, 100, 'health_potion')
        item2 = self.item_system.create_item(200, 200, 'iron_sword')
        
        self.assertEqual(self.item_system.get_active_item_count(), 2)
        
        # Make one item inactive
        item1.active = False
        
        self.assertEqual(self.item_system.get_active_item_count(), 1)
    
    def test_get_collected_item_count(self):
        """Test counting collected items."""
        item = self.item_system.create_item(self.test_x, self.test_y, 'health_potion')
        
        self.assertEqual(self.item_system.get_collected_item_count(), 0)
        
        # Simulate collection
        self.item_system.collected_items.append(item)
        
        self.assertEqual(self.item_system.get_collected_item_count(), 1)
    
    def test_get_item_stats(self):
        """Test getting item statistics."""
        self.item_system.create_item(100, 100, 'health_potion')
        self.item_system.create_item(200, 200, 'mana_potion')
        self.item_system.create_item(300, 300, 'iron_sword')
        
        stats = self.item_system.get_item_stats()
        
        self.assertEqual(stats['total_items'], 3)
        self.assertEqual(stats['active_items'], 3)
        self.assertEqual(stats['collected_items'], 0)
        self.assertEqual(stats['items_by_category']['consumable'], 2)
        self.assertEqual(stats['items_by_category']['weapon'], 1)
        self.assertEqual(stats['items_by_category']['armor'], 0)
    
    def test_render_items(self):
        """Test rendering items (basic test)."""
        # Create a test surface
        screen = pygame.Surface((800, 600))
        
        # Create some items
        self.item_system.create_item(100, 100, 'health_potion')
        self.item_system.create_item(200, 200, 'iron_sword')
        
        # Should not raise exception
        self.item_system.render(screen, 0, 0)
    
    def test_render_with_camera_offset(self):
        """Test rendering items with camera offset."""
        screen = pygame.Surface((800, 600))
        
        self.item_system.create_item(100, 100, 'health_potion')
        
        # Should not raise exception
        self.item_system.render(screen, 50, 50)


if __name__ == '__main__':
    unittest.main()