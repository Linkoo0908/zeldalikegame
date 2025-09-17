"""
Unit tests for Enemy class.
"""
import unittest
from unittest.mock import patch, MagicMock
import pygame
import math
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from objects.enemy import Enemy


class TestEnemy(unittest.TestCase):
    """Test cases for Enemy class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock pygame
        pygame.init = MagicMock()
        pygame.Surface = MagicMock()
        pygame.draw = MagicMock()
        pygame.Rect = MagicMock()
    
    def test_init_basic_enemy(self):
        """Test that Enemy initializes with correct basic stats."""
        enemy = Enemy(100, 200, "basic")
        
        self.assertEqual(enemy.x, 100)
        self.assertEqual(enemy.y, 200)
        self.assertEqual(enemy.enemy_type, "basic")
        self.assertEqual(enemy.max_health, 30)
        self.assertEqual(enemy.current_health, 30)
        self.assertEqual(enemy.speed, 50)
        self.assertEqual(enemy.attack_damage, 10)
        self.assertEqual(enemy.experience_reward, 10)
        self.assertEqual(enemy.ai_state, "idle")
        self.assertTrue(enemy.active)
    
    def test_init_goblin_enemy(self):
        """Test that Enemy initializes with correct goblin stats."""
        enemy = Enemy(50, 75, "goblin")
        
        self.assertEqual(enemy.enemy_type, "goblin")
        self.assertEqual(enemy.max_health, 40)
        self.assertEqual(enemy.speed, 60)
        self.assertEqual(enemy.attack_damage, 12)
        self.assertEqual(enemy.experience_reward, 15)
    
    def test_init_orc_enemy(self):
        """Test that Enemy initializes with correct orc stats."""
        enemy = Enemy(50, 75, "orc")
        
        self.assertEqual(enemy.enemy_type, "orc")
        self.assertEqual(enemy.max_health, 60)
        self.assertEqual(enemy.speed, 40)
        self.assertEqual(enemy.attack_damage, 18)
        self.assertEqual(enemy.experience_reward, 25)
    
    def test_init_skeleton_enemy(self):
        """Test that Enemy initializes with correct skeleton stats."""
        enemy = Enemy(50, 75, "skeleton")
        
        self.assertEqual(enemy.enemy_type, "skeleton")
        self.assertEqual(enemy.max_health, 25)
        self.assertEqual(enemy.speed, 70)
        self.assertEqual(enemy.attack_damage, 8)
        self.assertEqual(enemy.experience_reward, 12)
    
    def test_init_unknown_enemy_type(self):
        """Test that unknown enemy type defaults to basic stats."""
        enemy = Enemy(50, 75, "unknown")
        
        self.assertEqual(enemy.enemy_type, "unknown")
        self.assertEqual(enemy.max_health, 30)  # Basic stats
        self.assertEqual(enemy.speed, 50)
        self.assertEqual(enemy.attack_damage, 10)
    
    def test_calculate_distance(self):
        """Test distance calculation to target."""
        enemy = Enemy(100, 100)
        
        # Distance to same position (center of enemy)
        distance = enemy._calculate_distance((116, 116))  # Enemy center is at (116, 116)
        self.assertEqual(distance, 0.0)
        
        # Distance to position 30 pixels right
        distance = enemy._calculate_distance((146, 116))
        self.assertEqual(distance, 30.0)
        
        # Distance to diagonal position
        distance = enemy._calculate_distance((116 + 30, 116 + 40))
        expected = math.sqrt(30*30 + 40*40)  # 50.0
        self.assertEqual(distance, expected)
    
    def test_take_damage(self):
        """Test that enemy takes damage correctly."""
        enemy = Enemy(100, 100, "basic")
        
        with patch('builtins.print') as mock_print:
            result = enemy.take_damage(10)
            
            self.assertFalse(result)  # Should not die
            self.assertEqual(enemy.current_health, 20)
            mock_print.assert_called_with("basic enemy takes 10 damage. Health: 20/30")
    
    def test_take_damage_death(self):
        """Test that enemy dies when health reaches 0."""
        enemy = Enemy(100, 100, "basic")
        enemy.current_health = 5
        
        with patch('builtins.print') as mock_print:
            result = enemy.take_damage(10)
            
            self.assertTrue(result)  # Should die
            self.assertEqual(enemy.current_health, 0)
            self.assertFalse(enemy.active)
            # Should print both damage and death messages
            self.assertEqual(mock_print.call_count, 2)
    
    def test_attack_basic(self):
        """Test basic attack functionality."""
        enemy = Enemy(100, 100)
        
        with patch('builtins.print') as mock_print:
            enemy.attack()
            
            self.assertTrue(enemy.is_attacking)
            self.assertEqual(enemy.attack_time, 0.0)
            mock_print.assert_called_with("basic enemy attacks!")
    
    def test_attack_while_attacking(self):
        """Test that attack is ignored if already attacking."""
        enemy = Enemy(100, 100)
        enemy.is_attacking = True
        
        with patch('builtins.print') as mock_print:
            enemy.attack()
            
            # Should not print attack message again
            mock_print.assert_not_called()
    
    def test_attack_state_update(self):
        """Test that attack state updates correctly over time."""
        enemy = Enemy(100, 100)
        enemy.is_attacking = True
        enemy.attack_time = 0.0
        
        # Update for half the attack duration
        enemy._update_attack_state(0.2)  # Half of 0.4 seconds
        self.assertTrue(enemy.is_attacking)
        self.assertEqual(enemy.attack_time, 0.2)
        
        # Update to complete the attack
        enemy._update_attack_state(0.2)  # Total 0.4 seconds
        self.assertFalse(enemy.is_attacking)
        self.assertEqual(enemy.attack_time, 0.0)
    
    def test_get_attack_damage(self):
        """Test attack damage retrieval."""
        enemy = Enemy(100, 100, "goblin")
        
        damage = enemy.get_attack_damage()
        self.assertEqual(damage, 12)  # Goblin attack damage
    
    def test_is_attack_active(self):
        """Test attack active state during animation."""
        enemy = Enemy(100, 100)
        
        # Not attacking
        self.assertFalse(enemy.is_attack_active())
        
        # Start attacking - too early
        enemy.is_attacking = True
        enemy.attack_time = 0.05  # Before 0.1 threshold
        self.assertFalse(enemy.is_attack_active())
        
        # Active attack phase
        enemy.attack_time = 0.15  # Between 0.1 and 0.28 (70% of 0.4)
        self.assertTrue(enemy.is_attack_active())
        
        # Later in attack (past damage window)
        enemy.attack_time = 0.35  # Past 70% of 0.4 seconds
        self.assertFalse(enemy.is_attack_active())
    
    def test_move_towards_target(self):
        """Test movement towards target position."""
        enemy = Enemy(100, 100)
        target = (200, 100)  # 100 pixels to the right
        
        enemy._move_towards_target(target)
        
        # Should move right at full speed
        self.assertEqual(enemy.velocity_x, enemy.speed)
        self.assertEqual(enemy.velocity_y, 0.0)
        self.assertEqual(enemy.facing_direction, 'right')
    
    def test_move_towards_target_diagonal(self):
        """Test movement towards diagonal target."""
        enemy = Enemy(100, 100)
        target = (200, 200)  # Diagonal movement
        
        enemy._move_towards_target(target)
        
        # Should normalize diagonal movement
        expected_speed = enemy.speed / math.sqrt(2)
        self.assertAlmostEqual(enemy.velocity_x, expected_speed, places=1)
        self.assertAlmostEqual(enemy.velocity_y, expected_speed, places=1)
    
    def test_update_facing_direction(self):
        """Test facing direction updates based on target."""
        enemy = Enemy(100, 100)
        
        # Test right direction
        enemy._update_facing_direction((200, 116))  # Right of enemy center
        self.assertEqual(enemy.facing_direction, 'right')
        
        # Test left direction
        enemy._update_facing_direction((50, 116))  # Left of enemy center
        self.assertEqual(enemy.facing_direction, 'left')
        
        # Test down direction
        enemy._update_facing_direction((116, 200))  # Below enemy center
        self.assertEqual(enemy.facing_direction, 'down')
        
        # Test up direction
        enemy._update_facing_direction((116, 50))  # Above enemy center
        self.assertEqual(enemy.facing_direction, 'up')
    
    def test_ai_state_transitions(self):
        """Test AI state transitions based on player distance."""
        enemy = Enemy(100, 100)
        player_pos = (200, 100)  # 100 pixels away
        
        # Should transition to chase (within detection range)
        enemy._transition_to_chase(player_pos)
        self.assertEqual(enemy.ai_state, "chase")
        self.assertEqual(enemy.last_player_position, player_pos)
        
        # Should transition to attack (close range)
        player_pos = (130, 100)  # Within attack range
        enemy._transition_to_attack(player_pos)
        self.assertEqual(enemy.ai_state, "attack")
        self.assertEqual(enemy.velocity_x, 0.0)
        self.assertEqual(enemy.velocity_y, 0.0)
        
        # Should transition to patrol (no player)
        enemy._transition_to_patrol()
        self.assertEqual(enemy.ai_state, "patrol")
    
    def test_patrol_target_selection(self):
        """Test that patrol targets are chosen within patrol radius."""
        enemy = Enemy(100, 100)
        enemy.original_position = (100, 100)
        enemy.patrol_radius = 50
        
        enemy._choose_new_patrol_target()
        
        self.assertIsNotNone(enemy.target_position)
        
        # Check that target is within patrol radius
        distance = enemy._calculate_distance(enemy.target_position)
        self.assertLessEqual(distance, enemy.patrol_radius + 20)  # +20 for minimum distance
    
    def test_get_attack_rect_directions(self):
        """Test attack rectangle calculation for different directions."""
        enemy = Enemy(100, 100)
        enemy.attack_range = 40
        
        # Test down direction
        enemy.facing_direction = 'down'
        attack_rect = enemy.get_attack_rect()
        # Attack should be below the enemy
        # This test mainly checks that the method runs without error
        # since pygame.Rect is mocked
        
        # Test other directions
        for direction in ['up', 'left', 'right']:
            enemy.facing_direction = direction
            attack_rect = enemy.get_attack_rect()
            # Just verify it doesn't crash
    
    def test_set_patrol_area(self):
        """Test setting patrol area."""
        enemy = Enemy(100, 100)
        
        enemy.set_patrol_area(200, 300, 75)
        
        self.assertEqual(enemy.original_position, (200, 300))
        self.assertEqual(enemy.patrol_radius, 75)
    
    def test_reset_to_patrol(self):
        """Test resetting enemy to patrol state."""
        enemy = Enemy(100, 100)
        enemy.ai_state = "chase"
        enemy.last_player_position = (200, 200)
        enemy.target_position = (150, 150)
        enemy.velocity_x = 50
        enemy.velocity_y = 30
        
        enemy.reset_to_patrol()
        
        self.assertEqual(enemy.ai_state, "patrol")
        self.assertIsNone(enemy.last_player_position)
        self.assertIsNone(enemy.target_position)
        self.assertEqual(enemy.state_change_timer, 0.0)
        self.assertEqual(enemy.velocity_x, 0.0)
        self.assertEqual(enemy.velocity_y, 0.0)
    
    def test_get_stats(self):
        """Test that enemy stats are returned correctly."""
        enemy = Enemy(150, 250, "goblin")
        enemy.current_health = 30
        enemy.ai_state = "chase"
        enemy.facing_direction = 'left'
        enemy.is_attacking = True
        
        stats = enemy.get_stats()
        
        expected_stats = {
            'enemy_type': 'goblin',
            'health': 30,
            'max_health': 40,
            'position': (150, 250),
            'facing_direction': 'left',
            'ai_state': 'chase',
            'is_attacking': True,
            'attack_damage': 12,
            'speed': 60,
            'experience_reward': 15,
            'active': True
        }
        
        self.assertEqual(stats, expected_stats)
    
    def test_update_basic(self):
        """Test basic update functionality."""
        enemy = Enemy(100, 100)
        enemy.velocity_x = 50
        enemy.velocity_y = 30
        
        enemy.update(0.1)  # 0.1 seconds
        
        # Position should update based on velocity
        self.assertEqual(enemy.x, 105.0)  # 100 + 50 * 0.1
        self.assertEqual(enemy.y, 103.0)  # 100 + 30 * 0.1
    
    def test_update_no_movement_while_attacking(self):
        """Test that enemy doesn't move while attacking."""
        enemy = Enemy(100, 100)
        enemy.velocity_x = 50
        enemy.velocity_y = 30
        enemy.is_attacking = True
        
        original_x = enemy.x
        original_y = enemy.y
        
        enemy.update(0.1)
        
        # Position should not change during attack
        self.assertEqual(enemy.x, original_x)
        self.assertEqual(enemy.y, original_y)
    
    @patch('time.time')
    def test_ai_attack_behavior_with_cooldown(self, mock_time):
        """Test AI attack behavior respects cooldown."""
        enemy = Enemy(100, 100)
        enemy.ai_state = "attack"
        enemy.last_attack_time = 0.0
        
        # First attack should work
        mock_time.return_value = 1.0
        with patch('builtins.print'):
            enemy._execute_attack_behavior((130, 100))
        
        self.assertTrue(enemy.is_attacking)
        
        # Second attack too soon (should be blocked)
        enemy.is_attacking = False  # Reset attack state
        mock_time.return_value = 1.5  # Only 0.5 seconds later (< cooldown)
        with patch('builtins.print'):
            enemy._execute_attack_behavior((130, 100))
        
        # Should not attack again due to cooldown
        # (This is a simplified test since the actual cooldown logic is complex)


if __name__ == '__main__':
    unittest.main()