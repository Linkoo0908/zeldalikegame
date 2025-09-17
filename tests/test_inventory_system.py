"""
Unit tests for the Inventory system.
"""
import unittest
import pygame
from src.systems.inventory_system import Inventory
from src.objects.item import Item
from src.objects.player import Player


class TestInventory(unittest.TestCase):
    """Test cases for Inventory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        self.inventory = Inventory(max_size=5)  # Small inventory for testing
        self.player = Player(100, 100)
        
        # Create test items
        self.health_potion = Item(0, 0, 'health_potion')
        self.mana_potion = Item(0, 0, 'mana_potion')
        self.iron_sword = Item(0, 0, 'iron_sword')
        self.leather_armor = Item(0, 0, 'leather_armor')
        self.speed_boots = Item(0, 0, 'speed_boots')
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_inventory_creation(self):
        """Test basic inventory creation."""
        self.assertEqual(self.inventory.max_size, 5)
        self.assertEqual(self.inventory.get_item_count(), 0)
        self.assertTrue(self.inventory.is_empty())
        self.assertFalse(self.inventory.is_full())
    
    def test_add_item(self):
        """Test adding items to inventory."""
        success = self.inventory.add_item(self.health_potion)
        
        self.assertTrue(success)
        self.assertEqual(self.inventory.get_item_count(), 1)
        self.assertFalse(self.inventory.is_empty())
        self.assertTrue(self.inventory.has_item(self.health_potion))
    
    def test_add_item_to_full_inventory(self):
        """Test adding item to full inventory."""
        # Fill inventory
        for i in range(5):
            item = Item(0, 0, 'health_potion')
            self.inventory.add_item(item)
        
        self.assertTrue(self.inventory.is_full())
        
        # Try to add one more item
        extra_item = Item(0, 0, 'mana_potion')
        success = self.inventory.add_item(extra_item)
        
        self.assertFalse(success)
        self.assertEqual(self.inventory.get_item_count(), 5)
    
    def test_remove_item(self):
        """Test removing items from inventory."""
        self.inventory.add_item(self.health_potion)
        
        success = self.inventory.remove_item(self.health_potion)
        
        self.assertTrue(success)
        self.assertEqual(self.inventory.get_item_count(), 0)
        self.assertFalse(self.inventory.has_item(self.health_potion))
    
    def test_remove_nonexistent_item(self):
        """Test removing item that doesn't exist."""
        success = self.inventory.remove_item(self.health_potion)
        
        self.assertFalse(success)
        self.assertEqual(self.inventory.get_item_count(), 0)
    
    def test_remove_item_by_index(self):
        """Test removing item by index."""
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(self.mana_potion)
        
        removed_item = self.inventory.remove_item_by_index(0)
        
        self.assertEqual(removed_item, self.health_potion)
        self.assertEqual(self.inventory.get_item_count(), 1)
        self.assertFalse(self.inventory.has_item(self.health_potion))
    
    def test_remove_item_by_invalid_index(self):
        """Test removing item by invalid index."""
        self.inventory.add_item(self.health_potion)
        
        removed_item = self.inventory.remove_item_by_index(5)
        
        self.assertIsNone(removed_item)
        self.assertEqual(self.inventory.get_item_count(), 1)
    
    def test_get_item_by_index(self):
        """Test getting item by index."""
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(self.mana_potion)
        
        item = self.inventory.get_item_by_index(1)
        
        self.assertEqual(item, self.mana_potion)
    
    def test_get_item_by_invalid_index(self):
        """Test getting item by invalid index."""
        item = self.inventory.get_item_by_index(0)
        
        self.assertIsNone(item)
    
    def test_find_items_by_type(self):
        """Test finding items by type."""
        health_potion2 = Item(0, 0, 'health_potion')
        
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(health_potion2)
        self.inventory.add_item(self.iron_sword)
        
        health_potions = self.inventory.find_items_by_type('health_potion')
        
        self.assertEqual(len(health_potions), 2)
        self.assertIn(self.health_potion, health_potions)
        self.assertIn(health_potion2, health_potions)
    
    def test_find_items_by_category(self):
        """Test finding items by category."""
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(self.mana_potion)
        self.inventory.add_item(self.iron_sword)
        
        consumables = self.inventory.find_items_by_category('consumable')
        weapons = self.inventory.find_items_by_category('weapon')
        
        self.assertEqual(len(consumables), 2)
        self.assertIn(self.health_potion, consumables)
        self.assertIn(self.mana_potion, consumables)
        
        self.assertEqual(len(weapons), 1)
        self.assertIn(self.iron_sword, weapons)
    
    def test_get_consumables(self):
        """Test getting consumable items."""
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(self.iron_sword)
        
        consumables = self.inventory.get_consumables()
        
        self.assertEqual(len(consumables), 1)
        self.assertIn(self.health_potion, consumables)
    
    def test_get_weapons(self):
        """Test getting weapon items."""
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(self.iron_sword)
        
        weapons = self.inventory.get_weapons()
        
        self.assertEqual(len(weapons), 1)
        self.assertIn(self.iron_sword, weapons)
    
    def test_get_free_space(self):
        """Test getting free space."""
        self.assertEqual(self.inventory.get_free_space(), 5)
        
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(self.mana_potion)
        
        self.assertEqual(self.inventory.get_free_space(), 3)
    
    def test_clear_inventory(self):
        """Test clearing inventory."""
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(self.iron_sword)
        
        self.inventory.clear()
        
        self.assertEqual(self.inventory.get_item_count(), 0)
        self.assertTrue(self.inventory.is_empty())
        self.assertIsNone(self.inventory.get_equipped_item('weapon'))
    
    def test_equip_weapon(self):
        """Test equipping a weapon."""
        self.inventory.add_item(self.iron_sword)
        
        success = self.inventory.equip_item(self.iron_sword)
        
        self.assertTrue(success)
        self.assertEqual(self.inventory.get_equipped_item('weapon'), self.iron_sword)
        self.assertFalse(self.inventory.has_item(self.iron_sword))
    
    def test_equip_item_not_in_inventory(self):
        """Test equipping item not in inventory."""
        success = self.inventory.equip_item(self.iron_sword)
        
        self.assertFalse(success)
        self.assertIsNone(self.inventory.get_equipped_item('weapon'))
    
    def test_equip_replace_existing(self):
        """Test equipping item when slot already has item."""
        sword2 = Item(0, 0, 'iron_sword')
        
        self.inventory.add_item(self.iron_sword)
        self.inventory.add_item(sword2)
        
        # Equip first sword
        self.inventory.equip_item(self.iron_sword)
        
        # Equip second sword (should replace first)
        success = self.inventory.equip_item(sword2)
        
        self.assertTrue(success)
        self.assertEqual(self.inventory.get_equipped_item('weapon'), sword2)
        self.assertTrue(self.inventory.has_item(self.iron_sword))  # First sword back in inventory
    
    def test_unequip_item(self):
        """Test unequipping an item."""
        self.inventory.add_item(self.iron_sword)
        self.inventory.equip_item(self.iron_sword)
        
        success = self.inventory.unequip_item(self.iron_sword)
        
        self.assertTrue(success)
        self.assertIsNone(self.inventory.get_equipped_item('weapon'))
        self.assertTrue(self.inventory.has_item(self.iron_sword))
    
    def test_unequip_item_full_inventory(self):
        """Test unequipping item when inventory is full."""
        # Fill inventory
        for i in range(5):
            item = Item(0, 0, 'health_potion')
            self.inventory.add_item(item)
        
        # Equip sword (not in inventory)
        self.inventory.equipped_items['weapon'] = self.iron_sword
        
        success = self.inventory.unequip_item(self.iron_sword)
        
        self.assertFalse(success)  # Can't unequip because inventory is full
        self.assertEqual(self.inventory.get_equipped_item('weapon'), self.iron_sword)
    
    def test_is_item_equipped(self):
        """Test checking if item is equipped."""
        self.inventory.add_item(self.iron_sword)
        
        self.assertFalse(self.inventory.is_item_equipped(self.iron_sword))
        
        self.inventory.equip_item(self.iron_sword)
        
        self.assertTrue(self.inventory.is_item_equipped(self.iron_sword))
    
    def test_use_consumable_item(self):
        """Test using a consumable item."""
        self.inventory.add_item(self.health_potion)
        
        # Damage player so health potion will work
        self.player.current_health = 50
        
        success = self.inventory.use_item(self.health_potion, self.player)
        
        self.assertTrue(success)
        self.assertEqual(self.player.current_health, 100)
        self.assertFalse(self.inventory.has_item(self.health_potion))  # Consumed
    
    def test_use_equipment_item(self):
        """Test using an equipment item (should equip it)."""
        self.inventory.add_item(self.iron_sword)
        original_attack = self.player.attack_damage
        
        success = self.inventory.use_item(self.iron_sword, self.player)
        
        self.assertTrue(success)
        self.assertEqual(self.inventory.get_equipped_item('weapon'), self.iron_sword)
        self.assertEqual(self.player.attack_damage, original_attack + 15)
    
    def test_use_item_by_index(self):
        """Test using item by index."""
        self.inventory.add_item(self.health_potion)
        self.player.current_health = 50
        
        success = self.inventory.use_item_by_index(0, self.player)
        
        self.assertTrue(success)
        self.assertEqual(self.player.current_health, 100)
    
    def test_use_item_by_invalid_index(self):
        """Test using item by invalid index."""
        success = self.inventory.use_item_by_index(0, self.player)
        
        self.assertFalse(success)
    
    def test_sort_items_by_category(self):
        """Test sorting items by category."""
        self.inventory.add_item(self.iron_sword)      # weapon
        self.inventory.add_item(self.health_potion)   # consumable
        self.inventory.add_item(self.leather_armor)   # armor
        
        self.inventory.sort_items('category')
        
        items = self.inventory.get_items_list()
        self.assertEqual(items[0].category, 'armor')
        self.assertEqual(items[1].category, 'consumable')
        self.assertEqual(items[2].category, 'weapon')
    
    def test_sort_items_by_name(self):
        """Test sorting items by name."""
        self.inventory.add_item(self.iron_sword)      # Iron Sword
        self.inventory.add_item(self.health_potion)   # Health Potion
        
        self.inventory.sort_items('name')
        
        items = self.inventory.get_items_list()
        self.assertEqual(items[0].name, 'Health Potion')
        self.assertEqual(items[1].name, 'Iron Sword')
    
    def test_has_item_type(self):
        """Test checking if inventory has item type."""
        self.assertFalse(self.inventory.has_item_type('health_potion'))
        
        self.inventory.add_item(self.health_potion)
        
        self.assertTrue(self.inventory.has_item_type('health_potion'))
        self.assertFalse(self.inventory.has_item_type('iron_sword'))
    
    def test_count_item_type(self):
        """Test counting items of specific type."""
        health_potion2 = Item(0, 0, 'health_potion')
        
        self.assertEqual(self.inventory.count_item_type('health_potion'), 0)
        
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(health_potion2)
        
        self.assertEqual(self.inventory.count_item_type('health_potion'), 2)
        self.assertEqual(self.inventory.count_item_type('iron_sword'), 0)
    
    def test_get_inventory_info(self):
        """Test getting inventory information."""
        self.inventory.add_item(self.health_potion)
        self.inventory.add_item(self.iron_sword)
        self.inventory.equip_item(self.iron_sword)
        
        info = self.inventory.get_inventory_info()
        
        self.assertEqual(info['max_size'], 5)
        self.assertEqual(info['current_size'], 1)  # Only health potion left
        self.assertEqual(info['free_space'], 4)
        self.assertFalse(info['is_full'])
        self.assertFalse(info['is_empty'])
        self.assertEqual(len(info['items']), 1)
        self.assertIsNotNone(info['equipped_items']['weapon'])
        self.assertEqual(info['item_counts_by_category']['consumable'], 1)


class TestPlayerInventoryIntegration(unittest.TestCase):
    """Test cases for Player-Inventory integration."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        self.player = Player(100, 100)
        self.health_potion = Item(0, 0, 'health_potion')
        self.iron_sword = Item(0, 0, 'iron_sword')
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_player_add_item(self):
        """Test player adding item to inventory."""
        success = self.player.add_item(self.health_potion)
        
        self.assertTrue(success)
        self.assertTrue(self.player.inventory.has_item(self.health_potion))
    
    def test_player_remove_item(self):
        """Test player removing item from inventory."""
        self.player.add_item(self.health_potion)
        
        success = self.player.remove_item(self.health_potion)
        
        self.assertTrue(success)
        self.assertFalse(self.player.inventory.has_item(self.health_potion))
    
    def test_player_use_item(self):
        """Test player using item."""
        self.player.add_item(self.health_potion)
        self.player.current_health = 50
        
        success = self.player.use_item(self.health_potion)
        
        self.assertTrue(success)
        self.assertEqual(self.player.current_health, 100)
    
    def test_player_equip_item(self):
        """Test player equipping item."""
        self.player.add_item(self.iron_sword)
        original_attack = self.player.attack_damage
        
        success = self.player.equip_item(self.iron_sword)
        
        self.assertTrue(success)
        self.assertEqual(self.player.get_equipped_weapon(), self.iron_sword)
        self.assertEqual(self.player.attack_damage, original_attack + 15)
    
    def test_player_has_item_type(self):
        """Test player checking for item type."""
        self.assertFalse(self.player.has_item_type('health_potion'))
        
        self.player.add_item(self.health_potion)
        
        self.assertTrue(self.player.has_item_type('health_potion'))
    
    def test_player_count_item_type(self):
        """Test player counting item type."""
        health_potion2 = Item(0, 0, 'health_potion')
        
        self.assertEqual(self.player.count_item_type('health_potion'), 0)
        
        self.player.add_item(self.health_potion)
        self.player.add_item(health_potion2)
        
        self.assertEqual(self.player.count_item_type('health_potion'), 2)
    
    def test_player_get_inventory_info(self):
        """Test player getting inventory info."""
        self.player.add_item(self.health_potion)
        
        info = self.player.get_inventory_info()
        
        self.assertIsInstance(info, dict)
        self.assertEqual(info['current_size'], 1)
        self.assertEqual(len(info['items']), 1)


if __name__ == '__main__':
    unittest.main()