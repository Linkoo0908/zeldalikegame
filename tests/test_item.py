"""
Unit tests for the Item class.
"""
import unittest
import pygame
from src.objects.item import Item
from src.objects.player import Player


class TestItem(unittest.TestCase):
    """Test cases for Item class."""
    
    def setUp(self):
        """Set up test fixtures."""
        import os
        os.environ['SDL_VIDEODRIVER'] = 'dummy'
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        self.test_x = 100
        self.test_y = 200
        self.player = Player(50, 50)
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_item_creation(self):
        """Test basic item creation."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        self.assertEqual(item.x, self.test_x)
        self.assertEqual(item.y, self.test_y)
        self.assertEqual(item.item_type, 'health_potion')
        self.assertEqual(item.name, 'Health Potion')
        self.assertEqual(item.category, 'consumable')
        self.assertFalse(item.collected)
        self.assertTrue(item.active)
    
    def test_invalid_item_type(self):
        """Test creation with invalid item type."""
        with self.assertRaises(ValueError):
            Item(self.test_x, self.test_y, 'invalid_item')
    
    def test_item_types(self):
        """Test all predefined item types."""
        for item_type in Item.ITEM_TYPES.keys():
            item = Item(self.test_x, self.test_y, item_type)
            self.assertEqual(item.item_type, item_type)
            self.assertIsNotNone(item.name)
            self.assertIsNotNone(item.category)
            self.assertIsNotNone(item.effect)
    
    def test_health_potion_properties(self):
        """Test health potion specific properties."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        self.assertEqual(item.category, 'consumable')
        self.assertIn('health', item.effect)
        self.assertEqual(item.effect['health'], 50)
        self.assertEqual(item.color, (255, 100, 100))
    
    def test_weapon_properties(self):
        """Test weapon item properties."""
        item = Item(self.test_x, self.test_y, 'iron_sword')
        
        self.assertEqual(item.category, 'weapon')
        self.assertIn('attack', item.effect)
        self.assertEqual(item.effect['attack'], 15)
        self.assertEqual(item.color, (150, 150, 150))
    
    def test_item_bounds(self):
        """Test item bounding rectangle."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        bounds = item.get_bounds()
        
        self.assertEqual(bounds.x, self.test_x)
        self.assertEqual(bounds.y, self.test_y)
        self.assertEqual(bounds.width, 24)
        self.assertEqual(bounds.height, 24)
    
    def test_item_center(self):
        """Test item center calculation."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        center = item.get_center()
        
        expected_x = self.test_x + 12  # width / 2
        expected_y = self.test_y + 12  # height / 2
        
        self.assertEqual(center, (expected_x, expected_y))
    
    def test_item_update(self):
        """Test item update method."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        original_y = item.y
        
        # Update should cause bobbing animation
        item.update(0.1)
        
        # Y position should change due to bobbing
        self.assertNotEqual(item.y, original_y)
    
    def test_collected_item_no_update(self):
        """Test that collected items don't update."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        item.collected = True
        original_y = item.y
        
        item.update(0.1)
        
        # Y position should not change for collected items
        self.assertEqual(item.y, original_y)
    
    def test_can_be_collected_by_close_player(self):
        """Test collection detection when player is close."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        # Place player close to item
        self.player.x = self.test_x
        self.player.y = self.test_y
        
        self.assertTrue(item.can_be_collected_by(self.player))
    
    def test_cannot_be_collected_by_far_player(self):
        """Test collection detection when player is far."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        # Place player far from item
        self.player.x = self.test_x + 100
        self.player.y = self.test_y + 100
        
        self.assertFalse(item.can_be_collected_by(self.player))
    
    def test_cannot_collect_already_collected_item(self):
        """Test that already collected items cannot be collected again."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        item.collected = True
        
        # Place player close to item
        self.player.x = self.test_x
        self.player.y = self.test_y
        
        self.assertFalse(item.can_be_collected_by(self.player))
    
    def test_health_potion_collection_heals_player(self):
        """Test that collecting health potion heals player."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        # Damage player first
        self.player.current_health = 50
        
        # Place player close to item
        self.player.x = self.test_x
        self.player.y = self.test_y
        
        # Collect item
        success = item.collect(self.player)
        
        self.assertTrue(success)
        self.assertTrue(item.collected)
        self.assertFalse(item.active)
        self.assertEqual(self.player.current_health, 100)  # 50 + 50 healing
    
    def test_health_potion_full_health_goes_to_inventory(self):
        """Test that health potion goes to inventory when player has full health."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        # Player has full health
        self.player.current_health = self.player.max_health
        
        # Place player close to item
        self.player.x = self.test_x
        self.player.y = self.test_y
        
        # Collect item
        success = item.collect(self.player)
        
        self.assertTrue(success)
        self.assertTrue(item.collected)
        self.assertFalse(item.active)
        self.assertTrue(self.player.inventory.has_item(item))
    
    def test_weapon_collection_goes_to_inventory(self):
        """Test that weapons go to inventory when collected."""
        item = Item(self.test_x, self.test_y, 'iron_sword')
        
        # Place player close to item
        self.player.x = self.test_x
        self.player.y = self.test_y
        
        # Collect item
        success = item.collect(self.player)
        
        self.assertTrue(success)
        self.assertTrue(item.collected)
        self.assertFalse(item.active)
        self.assertTrue(self.player.inventory.has_item(item))
    
    def test_experience_gem_collection(self):
        """Test that experience gems give experience."""
        item = Item(self.test_x, self.test_y, 'experience_gem')
        initial_exp = self.player.experience
        
        # Place player close to item
        self.player.x = self.test_x
        self.player.y = self.test_y
        
        # Collect item
        success = item.collect(self.player)
        
        self.assertTrue(success)
        self.assertTrue(item.collected)
        self.assertFalse(item.active)
        self.assertEqual(self.player.experience, initial_exp + 25)
    
    def test_item_use_consumable(self):
        """Test using a consumable item."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        
        # Damage player
        self.player.current_health = 50
        
        # Use item
        success = item.use_on_player(self.player)
        
        self.assertTrue(success)
        self.assertEqual(self.player.current_health, 100)
    
    def test_item_use_equipment(self):
        """Test using an equipment item."""
        item = Item(self.test_x, self.test_y, 'iron_sword')
        
        # Add item to inventory first (since use_on_player for equipment requires it to be in inventory)
        self.player.add_item(item)
        original_attack = self.player.attack_damage
        
        # Use item (equip)
        success = item.use_on_player(self.player)
        
        self.assertTrue(success)
        self.assertEqual(self.player.attack_damage, original_attack + 15)
    
    def test_get_item_info(self):
        """Test getting item information."""
        item = Item(self.test_x, self.test_y, 'health_potion')
        info = item.get_info()
        
        self.assertEqual(info['name'], 'Health Potion')
        self.assertEqual(info['type'], 'health_potion')
        self.assertEqual(info['category'], 'consumable')
        self.assertEqual(info['effect'], {'health': 50})
        self.assertEqual(info['position'], (self.test_x, self.test_y))
        self.assertFalse(info['collected'])
        self.assertTrue(info['active'])
    
    def test_create_random_item(self):
        """Test creating random items."""
        item = Item.create_random_item(self.test_x, self.test_y)
        
        self.assertEqual(item.x, self.test_x)
        self.assertEqual(item.y, self.test_y)
        self.assertIn(item.item_type, Item.ITEM_TYPES.keys())
    
    def test_get_item_types(self):
        """Test getting all item types."""
        item_types = Item.get_item_types()
        
        self.assertIsInstance(item_types, dict)
        self.assertIn('health_potion', item_types)
        self.assertIn('iron_sword', item_types)
        
        # Ensure it's a copy, not the original
        item_types['test'] = {}
        self.assertNotIn('test', Item.ITEM_TYPES)
    
    def test_item_sprite_creation(self):
        """Test that item sprites are created properly."""
        for item_type in Item.ITEM_TYPES.keys():
            item = Item(self.test_x, self.test_y, item_type)
            self.assertIsNotNone(item.sprite)
            self.assertEqual(item.sprite.get_width(), 24)
            self.assertEqual(item.sprite.get_height(), 24)


if __name__ == '__main__':
    unittest.main()