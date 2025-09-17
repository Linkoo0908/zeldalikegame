"""
Unit tests for CombatSystem class.
"""
import unittest
from unittest.mock import patch, MagicMock
import pygame
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from systems.combat_system import CombatSystem
from objects.player import Player
from objects.enemy import Enemy


class TestCombatSystem(unittest.TestCase):
    """Test cases for CombatSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock pygame
        pygame.init = MagicMock()
        pygame.Surface = MagicMock()
        pygame.draw = MagicMock()
        pygame.Rect = MagicMock()
        
        # Create combat system
        self.combat_system = CombatSystem()
        
        # Create test player and enemy
        with patch('builtins.open'), patch('json.load'):
            self.player = Player(100, 100)
            self.enemy = Enemy(200, 100, "basic")
    
    def test_init(self):
        """Test combat system initialization."""
        combat_system = CombatSystem()
        
        self.assertEqual(len(combat_system.active_enemies), 0)
        self.assertEqual(len(combat_system.combat_events), 0)
        self.assertEqual(combat_system.damage_flash_duration, 0.2)
        self.assertEqual(combat_system.knockback_force, 50.0)
    
    def test_add_enemy(self):
        """Test adding enemy to combat system."""
        self.combat_system.add_enemy(self.enemy)
        
        self.assertIn(self.enemy, self.combat_system.active_enemies)
        self.assertEqual(len(self.combat_system.active_enemies), 1)
    
    def test_add_enemy_duplicate(self):
        """Test that adding same enemy twice doesn't duplicate it."""
        self.combat_system.add_enemy(self.enemy)
        self.combat_system.add_enemy(self.enemy)  # Add again
        
        self.assertEqual(len(self.combat_system.active_enemies), 1)
    
    def test_remove_enemy(self):
        """Test removing enemy from combat system."""
        self.combat_system.add_enemy(self.enemy)
        self.combat_system.remove_enemy(self.enemy)
        
        self.assertNotIn(self.enemy, self.combat_system.active_enemies)
        self.assertEqual(len(self.combat_system.active_enemies), 0)
    
    def test_remove_enemy_not_present(self):
        """Test removing enemy that's not in the system."""
        # Should not raise an error
        self.combat_system.remove_enemy(self.enemy)
        self.assertEqual(len(self.combat_system.active_enemies), 0)
    
    def test_spawn_enemy(self):
        """Test spawning a new enemy."""
        enemy = self.combat_system.spawn_enemy(150, 200, "goblin")
        
        self.assertEqual(enemy.x, 150)
        self.assertEqual(enemy.y, 200)
        self.assertEqual(enemy.enemy_type, "goblin")
        self.assertIn(enemy, self.combat_system.active_enemies)
    
    def test_clear_enemies(self):
        """Test clearing all enemies."""
        self.combat_system.add_enemy(self.enemy)
        enemy2 = Enemy(300, 300, "orc")
        self.combat_system.add_enemy(enemy2)
        
        self.combat_system.clear_enemies()
        
        self.assertEqual(len(self.combat_system.active_enemies), 0)
    
    def test_get_active_enemies(self):
        """Test getting active enemies list."""
        self.combat_system.add_enemy(self.enemy)
        
        active_enemies = self.combat_system.get_active_enemies()
        
        self.assertEqual(len(active_enemies), 1)
        self.assertIn(self.enemy, active_enemies)
        # Should return a copy, not the original list
        self.assertIsNot(active_enemies, self.combat_system.active_enemies)
    
    def test_get_enemies_in_range(self):
        """Test getting enemies within range."""
        # Add enemies at different distances
        close_enemy = Enemy(110, 110, "basic")  # Close to (100, 100)
        far_enemy = Enemy(300, 300, "basic")    # Far from (100, 100)
        
        self.combat_system.add_enemy(close_enemy)
        self.combat_system.add_enemy(far_enemy)
        
        # Get enemies within 50 pixels of (100, 100)
        enemies_in_range = self.combat_system.get_enemies_in_range((100, 100), 50)
        
        self.assertIn(close_enemy, enemies_in_range)
        self.assertNotIn(far_enemy, enemies_in_range)
    
    def test_get_combat_events(self):
        """Test getting combat events."""
        # Add a test event
        self.combat_system.combat_events.append({'type': 'test_event'})
        
        events = self.combat_system.get_combat_events()
        
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'test_event')
        # Should return a copy
        self.assertIsNot(events, self.combat_system.combat_events)
    
    def test_get_stats(self):
        """Test getting combat system statistics."""
        # Add some enemies
        enemy1 = Enemy(100, 100, "basic")
        enemy2 = Enemy(200, 200, "goblin")
        enemy2.current_health = 20  # Damaged enemy
        
        self.combat_system.add_enemy(enemy1)
        self.combat_system.add_enemy(enemy2)
        
        stats = self.combat_system.get_stats()
        
        self.assertEqual(stats['active_enemies'], 2)
        self.assertEqual(stats['total_enemies'], 2)
        self.assertEqual(stats['total_enemy_health'], 50)  # 30 + 20
        self.assertEqual(stats['combat_events_this_frame'], 0)
    
    def test_update_removes_inactive_enemies(self):
        """Test that update removes inactive enemies."""
        self.enemy.active = False
        self.combat_system.add_enemy(self.enemy)
        
        self.combat_system.update(0.1, self.player)
        
        self.assertNotIn(self.enemy, self.combat_system.active_enemies)
    
    @patch('pygame.Rect')
    def test_rects_collide(self, mock_rect_class):
        """Test rectangle collision detection."""
        # Mock pygame.Rect instances
        rect1 = MagicMock()
        rect2 = MagicMock()
        rect1.colliderect.return_value = True
        
        result = self.combat_system._rects_collide(rect1, rect2)
        
        self.assertTrue(result)
        rect1.colliderect.assert_called_once_with(rect2)
    
    def test_apply_knockback(self):
        """Test knockback application."""
        # Set up source and target positions
        source = MagicMock()
        source.x = 100
        source.y = 100
        source.width = 32
        source.height = 32
        
        target = MagicMock()
        target.x = 150
        target.y = 100
        target.width = 32
        target.height = 32
        
        original_x = target.x
        
        self.combat_system._apply_knockback(target, source, 100.0)
        
        # Target should be moved away from source
        self.assertGreater(target.x, original_x)
    
    def test_give_enemy_rewards(self):
        """Test giving rewards when enemy is defeated."""
        original_exp = self.player.experience
        
        with patch('builtins.print'):  # Suppress print output
            self.combat_system._give_enemy_rewards(self.player, self.enemy)
        
        # Player should gain experience
        self.assertEqual(self.player.experience, original_exp + self.enemy.experience_reward)
        
        # Should create a combat event
        events = self.combat_system.get_combat_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'enemy_defeated')
        self.assertEqual(events[0]['enemy'], self.enemy)
    
    @patch('pygame.Rect')
    def test_check_player_attack_enemy_hit(self, mock_rect_class):
        """Test player attack hitting enemy."""
        # Set up player attack
        self.player.is_attacking = True
        self.player.attack_time = 0.1  # Within active window
        
        # Mock rectangles and collision
        attack_rect = MagicMock()
        enemy_rect = MagicMock()
        attack_rect.colliderect.return_value = True
        
        self.player.get_attack_rect = MagicMock(return_value=attack_rect)
        self.enemy.get_bounds = MagicMock(return_value=enemy_rect)
        
        original_health = self.enemy.current_health
        
        with patch('builtins.print'):  # Suppress print output
            self.combat_system._check_player_attack_enemy(self.player, self.enemy)
        
        # Enemy should take damage
        self.assertLess(self.enemy.current_health, original_health)
        
        # Should create combat event
        events = self.combat_system.get_combat_events()
        self.assertTrue(any(event['type'] == 'player_hit_enemy' for event in events))
    
    @patch('pygame.Rect')
    def test_check_player_attack_enemy_miss(self, mock_rect_class):
        """Test player attack missing enemy."""
        # Set up player attack
        self.player.is_attacking = True
        self.player.attack_time = 0.1
        
        # Mock rectangles with no collision
        attack_rect = MagicMock()
        enemy_rect = MagicMock()
        attack_rect.colliderect.return_value = False
        
        self.player.get_attack_rect = MagicMock(return_value=attack_rect)
        self.enemy.get_bounds = MagicMock(return_value=enemy_rect)
        
        original_health = self.enemy.current_health
        
        self.combat_system._check_player_attack_enemy(self.player, self.enemy)
        
        # Enemy should not take damage
        self.assertEqual(self.enemy.current_health, original_health)
        
        # Should not create combat event
        events = self.combat_system.get_combat_events()
        self.assertFalse(any(event['type'] == 'player_hit_enemy' for event in events))
    
    @patch('pygame.Rect')
    def test_check_enemy_attack_player_hit(self, mock_rect_class):
        """Test enemy attack hitting player."""
        # Set up enemy attack
        self.enemy.is_attacking = True
        self.enemy.attack_time = 0.15  # Within active window
        
        # Mock rectangles and collision
        attack_rect = MagicMock()
        player_rect = MagicMock()
        attack_rect.colliderect.return_value = True
        
        self.enemy.get_attack_rect = MagicMock(return_value=attack_rect)
        mock_rect_class.return_value = player_rect
        
        original_health = self.player.current_health
        
        with patch('builtins.print'):  # Suppress print output
            self.combat_system._check_enemy_attack_player(self.enemy, self.player)
        
        # Player should take damage
        self.assertLess(self.player.current_health, original_health)
        
        # Should create combat event
        events = self.combat_system.get_combat_events()
        self.assertTrue(any(event['type'] == 'enemy_hit_player' for event in events))
    
    def test_update_clears_combat_events(self):
        """Test that update clears combat events from previous frame."""
        # Add a test event
        self.combat_system.combat_events.append({'type': 'old_event'})
        
        self.combat_system.update(0.1, self.player)
        
        # Events should be cleared
        self.assertEqual(len(self.combat_system.combat_events), 0)


if __name__ == '__main__':
    unittest.main()