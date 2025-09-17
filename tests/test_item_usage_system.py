"""
Unit tests for the Item Usage System.
"""
import unittest
import pygame
import time
from src.objects.item import Item
from src.objects.player import Player


class TestItemUsageSystem(unittest.TestCase):
    """Test cases for Item Usage System."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        self.player = Player(100, 100)
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_health_potion_usage(self):
        """Test using health potion."""
        health_potion = Item(0, 0, 'health_potion')
        self.player.current_health = 50
        
        success = health_potion.use_on_player(self.player)
        
        self.assertTrue(success)
        self.assertEqual(self.player.current_health, 100)
    
    def test_experience_gem_usage(self):
        """Test using experience gem."""
        exp_gem = Item(0, 0, 'experience_gem')
        initial_exp = self.player.experience
        
        success = exp_gem.use_on_player(self.player)
        
        self.assertTrue(success)
        self.assertEqual(self.player.experience, initial_exp + 25)
    
    def test_strength_potion_usage(self):
        """Test using strength potion for temporary attack boost."""
        strength_potion = Item(0, 0, 'strength_potion')
        initial_attack = self.player.attack_damage
        
        success = strength_potion.use_on_player(self.player)
        
        self.assertTrue(success)
        self.assertEqual(self.player.get_total_attack_damage(), initial_attack + 10)
        self.assertTrue(self.player.has_status_effect('strength_potion_effect'))
    
    def test_speed_potion_usage(self):
        """Test using speed potion for temporary speed boost."""
        speed_potion = Item(0, 0, 'speed_potion')
        initial_speed = self.player.speed
        
        success = speed_potion.use_on_player(self.player)
        
        self.assertTrue(success)
        self.assertEqual(self.player.speed, initial_speed * 1.5)
        self.assertTrue(self.player.has_status_effect('speed_potion_effect'))
    
    def test_weapon_equipment(self):
        """Test equipping a weapon."""
        iron_sword = Item(0, 0, 'iron_sword')
        self.player.add_item(iron_sword)
        initial_attack = self.player.attack_damage
        
        success = self.player.equip_item(iron_sword)
        
        self.assertTrue(success)
        self.assertEqual(self.player.attack_damage, initial_attack + 15)
        self.assertEqual(self.player.get_equipped_weapon(), iron_sword)
    
    def test_armor_equipment(self):
        """Test equipping armor."""
        leather_armor = Item(0, 0, 'leather_armor')
        self.player.add_item(leather_armor)
        
        success = self.player.equip_item(leather_armor)
        
        self.assertTrue(success)
        self.assertEqual(self.player.get_equipped_armor(), leather_armor)
    
    def test_magic_ring_equipment(self):
        """Test equipping magic ring with health regeneration."""
        magic_ring = Item(0, 0, 'magic_ring')
        self.player.add_item(magic_ring)
        initial_regen = self.player.health_regen_rate
        
        success = self.player.equip_item(magic_ring)
        
        self.assertTrue(success)
        self.assertEqual(self.player.health_regen_rate, initial_regen + 2)
        self.assertEqual(self.player.get_equipped_equipment(), magic_ring)
    
    def test_health_regeneration_over_time(self):
        """Test health regeneration effect over time."""
        magic_ring = Item(0, 0, 'magic_ring')
        self.player.add_item(magic_ring)
        self.player.equip_item(magic_ring)
        
        # Damage player
        self.player.current_health = 80
        
        # Simulate time passing
        dt = 1.0  # 1 second
        self.player.update(dt)
        
        # Health should have regenerated
        self.assertGreater(self.player.current_health, 80)
        self.assertLessEqual(self.player.current_health, 82)  # 2 health per second
    
    def test_status_effect_expiration(self):
        """Test that status effects expire after their duration."""
        # Create a strength potion with short duration for testing
        strength_potion = Item(0, 0, 'strength_potion')
        # Modify the effect to have a very short duration
        strength_potion.effect['duration'] = 0.1  # 0.1 seconds
        
        initial_attack = self.player.get_total_attack_damage()
        
        # Use the potion
        strength_potion.use_on_player(self.player)
        
        # Effect should be active
        self.assertTrue(self.player.has_status_effect('strength_potion_effect'))
        self.assertEqual(self.player.get_total_attack_damage(), initial_attack + 10)
        
        # Wait for effect to expire
        time.sleep(0.2)
        self.player.update_status_effects(0.1)
        
        # Effect should be gone
        self.assertFalse(self.player.has_status_effect('strength_potion_effect'))
        self.assertEqual(self.player.get_total_attack_damage(), initial_attack)
    
    def test_multiple_status_effects(self):
        """Test having multiple status effects active simultaneously."""
        strength_potion = Item(0, 0, 'strength_potion')
        speed_potion = Item(0, 0, 'speed_potion')
        
        initial_attack = self.player.get_total_attack_damage()
        initial_speed = self.player.speed
        
        # Use both potions
        strength_potion.use_on_player(self.player)
        speed_potion.use_on_player(self.player)
        
        # Both effects should be active
        self.assertTrue(self.player.has_status_effect('strength_potion_effect'))
        self.assertTrue(self.player.has_status_effect('speed_potion_effect'))
        self.assertEqual(self.player.get_total_attack_damage(), initial_attack + 10)
        self.assertEqual(self.player.speed, initial_speed * 1.5)
    
    def test_equipment_replacement(self):
        """Test replacing equipped items."""
        sword1 = Item(0, 0, 'iron_sword')
        sword2 = Item(0, 0, 'iron_sword')
        
        self.player.add_item(sword1)
        self.player.add_item(sword2)
        
        initial_attack = self.player.attack_damage
        
        # Equip first sword
        self.player.equip_item(sword1)
        self.assertEqual(self.player.attack_damage, initial_attack + 15)
        
        # Equip second sword (should replace first)
        self.player.equip_item(sword2)
        self.assertEqual(self.player.attack_damage, initial_attack + 15)  # Still +15, not +30
        self.assertEqual(self.player.get_equipped_weapon(), sword2)
        self.assertTrue(self.player.inventory.has_item(sword1))  # First sword back in inventory
    
    def test_unequip_item_effects(self):
        """Test that unequipping items removes their effects."""
        iron_sword = Item(0, 0, 'iron_sword')
        self.player.add_item(iron_sword)
        
        initial_attack = self.player.attack_damage
        
        # Equip sword
        self.player.equip_item(iron_sword)
        self.assertEqual(self.player.attack_damage, initial_attack + 15)
        
        # Unequip sword
        self.player.unequip_item(iron_sword)
        self.assertEqual(self.player.attack_damage, initial_attack)
        self.assertIsNone(self.player.get_equipped_weapon())
    
    def test_consumable_item_removal_after_use(self):
        """Test that consumable items are removed from inventory after use."""
        health_potion = Item(0, 0, 'health_potion')
        self.player.add_item(health_potion)
        self.player.current_health = 50
        
        # Use item through inventory
        success = self.player.use_item(health_potion)
        
        self.assertTrue(success)
        self.assertEqual(self.player.current_health, 100)
        self.assertFalse(self.player.inventory.has_item(health_potion))
    
    def test_equipment_item_equipping_after_use(self):
        """Test that equipment items are equipped after use."""
        iron_sword = Item(0, 0, 'iron_sword')
        self.player.add_item(iron_sword)
        
        initial_attack = self.player.attack_damage
        
        # Use item through inventory (should equip it)
        success = self.player.use_item(iron_sword)
        
        self.assertTrue(success)
        self.assertEqual(self.player.attack_damage, initial_attack + 15)
        self.assertEqual(self.player.get_equipped_weapon(), iron_sword)
        self.assertFalse(self.player.inventory.has_item(iron_sword))
    
    def test_use_item_by_index(self):
        """Test using items by inventory index."""
        health_potion = Item(0, 0, 'health_potion')
        iron_sword = Item(0, 0, 'iron_sword')
        
        self.player.add_item(health_potion)
        self.player.add_item(iron_sword)
        self.player.current_health = 50
        
        # Use first item (health potion)
        success = self.player.use_item_by_index(0)
        
        self.assertTrue(success)
        self.assertEqual(self.player.current_health, 100)
    
    def test_clear_all_status_effects(self):
        """Test clearing all status effects."""
        strength_potion = Item(0, 0, 'strength_potion')
        speed_potion = Item(0, 0, 'speed_potion')
        
        # Apply multiple effects
        strength_potion.use_on_player(self.player)
        speed_potion.use_on_player(self.player)
        
        self.assertTrue(self.player.has_status_effect('strength_potion_effect'))
        self.assertTrue(self.player.has_status_effect('speed_potion_effect'))
        
        # Clear all effects
        self.player.clear_all_status_effects()
        
        self.assertFalse(self.player.has_status_effect('strength_potion_effect'))
        self.assertFalse(self.player.has_status_effect('speed_potion_effect'))
    
    def test_get_status_effects(self):
        """Test getting all active status effects."""
        strength_potion = Item(0, 0, 'strength_potion')
        strength_potion.use_on_player(self.player)
        
        effects = self.player.get_status_effects()
        
        self.assertIn('strength_potion_effect', effects)
        self.assertIn('data', effects['strength_potion_effect'])
        self.assertIn('end_time', effects['strength_potion_effect'])
        self.assertIn('start_time', effects['strength_potion_effect'])
    
    def test_health_potion_full_health_inventory_behavior(self):
        """Test that health potions go to inventory when player has full health."""
        health_potion = Item(0, 0, 'health_potion')
        
        # Player has full health
        self.player.current_health = self.player.max_health
        
        # Try to use potion directly
        success = health_potion.use_on_player(self.player)
        
        self.assertTrue(success)
        self.assertTrue(self.player.inventory.has_item(health_potion))
    
    def test_item_effect_stacking_prevention(self):
        """Test that same status effects don't stack improperly."""
        strength_potion1 = Item(0, 0, 'strength_potion')
        strength_potion2 = Item(0, 0, 'strength_potion')
        
        initial_attack = self.player.get_total_attack_damage()
        
        # Use first potion
        strength_potion1.use_on_player(self.player)
        attack_after_first = self.player.get_total_attack_damage()
        
        # Use second potion (should replace first, not stack)
        strength_potion2.use_on_player(self.player)
        attack_after_second = self.player.get_total_attack_damage()
        
        self.assertEqual(attack_after_first, initial_attack + 10)
        self.assertEqual(attack_after_second, initial_attack + 10)  # Should still be +10, not +20


if __name__ == '__main__':
    unittest.main()