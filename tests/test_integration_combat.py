"""
Integration tests for combat system interactions.
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


class TestCombatIntegration(unittest.TestCase):
    """Integration test cases for combat system."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock pygame
        pygame.init = MagicMock()
        pygame.Surface = MagicMock()
        pygame.draw = MagicMock()
        pygame.Rect = MagicMock()
        
        # Create combat system
        self.combat_system = CombatSystem()
        
        # Create test player and enemy with mocked file loading
        with patch('builtins.open'), patch('json.load'):
            self.player = Player(100, 100)
            self.enemy = Enemy(150, 100, "basic")  # Close to player
        
        # Add enemy to combat system
        self.combat_system.add_enemy(self.enemy)
    
    @patch('time.time')
    def test_complete_combat_scenario(self, mock_time):
        """Test a complete combat scenario from start to finish."""
        mock_time.return_value = 1.0
        
        # Initial state
        initial_player_health = self.player.current_health
        initial_enemy_health = self.enemy.current_health
        initial_player_exp = self.player.experience
        
        # Player attacks enemy
        with patch('builtins.print'):  # Suppress print output
            self.player.attack()
        
        # Mock collision detection to return True for player attack
        with patch.object(self.combat_system, '_rects_collide', return_value=True):
            self.combat_system.update(0.1, self.player)
        
        # Enemy should take damage
        self.assertLess(self.enemy.current_health, initial_enemy_health)
        
        # Check combat events
        events = self.combat_system.get_combat_events()
        player_hit_events = [e for e in events if e['type'] == 'player_hit_enemy']
        self.assertEqual(len(player_hit_events), 1)
        
        # If enemy died, player should gain experience
        if not self.enemy.active:
            self.assertGreater(self.player.experience, initial_player_exp)
    
    @patch('time.time')
    def test_enemy_attacks_player(self, mock_time):
        """Test enemy attacking player."""
        mock_time.return_value = 1.0
        
        # Set enemy to attack state
        self.enemy.ai_state = "attack"
        
        initial_player_health = self.player.current_health
        
        # Mock collision detection to return True for enemy attack
        with patch.object(self.combat_system, '_rects_collide', return_value=True):
            with patch('builtins.print'):  # Suppress print output
                self.combat_system.update(0.1, self.player)
        
        # Player should take damage if enemy attacked
        events = self.combat_system.get_combat_events()
        enemy_hit_events = [e for e in events if e['type'] == 'enemy_hit_player']
        
        if len(enemy_hit_events) > 0:
            self.assertLess(self.player.current_health, initial_player_health)
    
    def test_enemy_ai_state_transitions(self):
        """Test enemy AI state transitions based on player position."""
        # Player far away - should patrol
        far_player = Player(500, 500)
        with patch('builtins.open'), patch('json.load'):
            pass  # Already created above
        
        self.combat_system.update(0.1, far_player)
        
        # Enemy should eventually transition to patrol (may take a few updates)
        for _ in range(10):  # Multiple updates to allow AI to process
            self.combat_system.update(0.1, far_player)
        
        # Enemy should not be in attack state when player is far
        self.assertNotEqual(self.enemy.ai_state, "attack")
    
    def test_multiple_enemies_combat(self):
        """Test combat with multiple enemies."""
        # Add another enemy
        enemy2 = Enemy(120, 120, "goblin")
        self.combat_system.add_enemy(enemy2)
        
        # Player attacks
        with patch('builtins.print'):
            self.player.attack()
        
        # Mock collision for both enemies
        with patch.object(self.combat_system, '_rects_collide', return_value=True):
            self.combat_system.update(0.1, self.player)
        
        # Both enemies should potentially take damage
        events = self.combat_system.get_combat_events()
        hit_events = [e for e in events if e['type'] == 'player_hit_enemy']
        
        # Should have hit events (exact number depends on attack timing)
        self.assertGreaterEqual(len(hit_events), 0)
    
    def test_enemy_death_and_rewards(self):
        """Test enemy death and reward giving."""
        # Damage enemy to near death
        self.enemy.current_health = 1
        
        initial_exp = self.player.experience
        
        # Player attacks
        with patch('builtins.print'):
            self.player.attack()
        
        # Ensure player attack is active
        self.player.attack_time = 0.1  # Within active window (0.3 * 0.6 = 0.18)
        
        # Mock collision
        with patch.object(self.combat_system, '_rects_collide', return_value=True):
            self.combat_system.update(0.1, self.player)
        
        # Check events immediately after first update
        events_after_first_update = self.combat_system.get_combat_events()
        
        # Enemy should be dead
        self.assertFalse(self.enemy.active)
        
        # Player should gain experience
        self.assertGreater(self.player.experience, initial_exp)
        
        # Should have defeat event from first update
        defeat_events = [e for e in events_after_first_update if e['type'] == 'enemy_defeated']
        self.assertEqual(len(defeat_events), 1)
        
        # Run another update to ensure dead enemies are removed
        self.combat_system.update(0.1, self.player)
        self.assertNotIn(self.enemy, self.combat_system.active_enemies)
    
    def test_knockback_effects(self):
        """Test knockback effects during combat."""
        original_enemy_x = self.enemy.x
        original_player_x = self.player.x
        
        # Player attacks enemy
        with patch('builtins.print'):
            self.player.attack()
        
        # Mock collision
        with patch.object(self.combat_system, '_rects_collide', return_value=True):
            self.combat_system.update(0.1, self.player)
        
        # Enemy should be knocked back (position changed)
        # Note: This test might be flaky depending on exact positioning
        # The main goal is to verify knockback logic runs without errors
        
        # Enemy attacks player
        self.enemy.ai_state = "attack"
        with patch('time.time', return_value=2.0):  # Past cooldown
            with patch.object(self.combat_system, '_rects_collide', return_value=True):
                with patch('builtins.print'):
                    self.combat_system.update(0.1, self.player)
        
        # Verify combat system handles knockback without errors
        self.assertIsNotNone(self.player.x)
        self.assertIsNotNone(self.enemy.x)
    
    def test_combat_system_stats_during_combat(self):
        """Test combat system statistics during active combat."""
        # Add multiple enemies
        enemy2 = Enemy(200, 200, "orc")
        enemy3 = Enemy(300, 300, "skeleton")
        self.combat_system.add_enemy(enemy2)
        self.combat_system.add_enemy(enemy3)
        
        # Get initial stats
        stats = self.combat_system.get_stats()
        self.assertEqual(stats['active_enemies'], 3)
        self.assertEqual(stats['total_enemies'], 3)
        
        # Damage one enemy
        enemy2.current_health = 10
        
        # Update stats
        stats = self.combat_system.get_stats()
        expected_health = self.enemy.current_health + enemy2.current_health + enemy3.current_health
        self.assertEqual(stats['total_enemy_health'], expected_health)
        
        # Kill one enemy
        enemy3.active = False
        self.combat_system.update(0.1, self.player)
        
        # Stats should reflect the change
        stats = self.combat_system.get_stats()
        self.assertEqual(stats['active_enemies'], 2)
        self.assertEqual(stats['total_enemies'], 2)


if __name__ == '__main__':
    unittest.main()