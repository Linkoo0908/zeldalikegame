"""
Unit tests for Player class.
"""
import unittest
from unittest.mock import patch, mock_open, MagicMock
import pygame
import json
import sys
import os

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from objects.player import Player
from systems.input_system import InputSystem


class TestPlayer(unittest.TestCase):
    """Test cases for Player class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock pygame
        pygame.init = MagicMock()
        pygame.Surface = MagicMock()
        pygame.draw = MagicMock()
        
        # Sample settings
        self.sample_settings = {
            "game": {
                "player_speed": 150,
                "tile_size": 32
            }
        }
    
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_init_loads_settings(self, mock_json_load, mock_file):
        """Test that Player loads settings from file."""
        mock_json_load.return_value = self.sample_settings
        
        player = Player(100, 200, "test_settings.json")
        
        mock_file.assert_called_once_with("test_settings.json", 'r', encoding='utf-8')
        self.assertEqual(player.speed, 150)
        self.assertEqual(player.x, 100)
        self.assertEqual(player.y, 200)
    
    @patch('builtins.open', side_effect=FileNotFoundError)
    def test_init_handles_missing_settings(self, mock_file):
        """Test that Player handles missing settings file gracefully."""
        player = Player(50, 75)
        
        # Should have default speed
        self.assertEqual(player.speed, 100)
        self.assertEqual(player.x, 50)
        self.assertEqual(player.y, 75)
    
    def test_initial_stats(self):
        """Test that player has correct initial stats."""
        player = Player(0, 0)
        
        self.assertEqual(player.max_health, 100)
        self.assertEqual(player.current_health, 100)
        self.assertEqual(player.level, 1)
        self.assertEqual(player.experience, 0)
        self.assertEqual(player.facing_direction, 'down')
        self.assertFalse(player.is_moving)
        self.assertEqual(len(player.inventory), 0)
    
    def test_handle_input_movement(self):
        """Test that player handles movement input correctly."""
        player = Player(100, 100)
        input_system = MagicMock()
        
        # Mock input system to return movement
        input_system.get_movement_vector.return_value = (1.0, 0.0)  # Moving right
        input_system.get_movement_direction.return_value = 'right'
        input_system.is_action_just_pressed.return_value = False
        
        player.handle_input(input_system)
        
        self.assertEqual(player.velocity_x, player.speed)
        self.assertEqual(player.velocity_y, 0.0)
        self.assertTrue(player.is_moving)
        self.assertEqual(player.facing_direction, 'right')
    
    def test_handle_input_no_movement(self):
        """Test that player handles no movement input correctly."""
        player = Player(100, 100)
        input_system = MagicMock()
        
        # Mock input system to return no movement
        input_system.get_movement_vector.return_value = (0.0, 0.0)
        input_system.is_action_just_pressed.return_value = False
        
        player.handle_input(input_system)
        
        self.assertEqual(player.velocity_x, 0.0)
        self.assertEqual(player.velocity_y, 0.0)
        self.assertFalse(player.is_moving)
    
    def test_handle_input_attack(self):
        """Test that player handles attack input."""
        player = Player(100, 100)
        input_system = MagicMock()
        
        input_system.get_movement_vector.return_value = (0.0, 0.0)
        input_system.is_action_just_pressed.side_effect = lambda action: action == 'attack'
        
        with patch('builtins.print') as mock_print:
            player.handle_input(input_system)
            mock_print.assert_called_with("Player attacks in direction: down")
    
    def test_handle_input_interact(self):
        """Test that player handles interact input."""
        player = Player(100, 100)
        input_system = MagicMock()
        
        input_system.get_movement_vector.return_value = (0.0, 0.0)
        input_system.is_action_just_pressed.side_effect = lambda action: action == 'interact'
        
        with patch('builtins.print') as mock_print:
            player.handle_input(input_system)
            mock_print.assert_called_with("Player interacts")
    
    def test_update_position(self):
        """Test that player position updates based on velocity."""
        player = Player(100, 100)
        player.velocity_x = 50.0  # 50 pixels per second
        player.velocity_y = -30.0  # -30 pixels per second
        
        dt = 0.1  # 0.1 seconds
        player.update(dt)
        
        self.assertEqual(player.x, 105.0)  # 100 + 50 * 0.1
        self.assertEqual(player.y, 97.0)   # 100 + (-30) * 0.1
    
    def test_update_animation_moving(self):
        """Test that animation updates when moving."""
        player = Player(100, 100)
        player.is_moving = True
        
        # Update multiple times to test animation frame changes
        for _ in range(5):
            player.update(0.05)  # 0.05 seconds each
        
        # After 0.25 seconds (5 * 0.05), animation should have advanced
        # (0.2 seconds per frame, so should be on frame 1)
        self.assertEqual(player.animation_frame, 1)
    
    def test_update_animation_not_moving(self):
        """Test that animation resets when not moving."""
        player = Player(100, 100)
        player.is_moving = False
        player.animation_frame = 2  # Set to non-zero frame
        
        player.update(0.1)
        
        self.assertEqual(player.animation_frame, 0)
        self.assertEqual(player.animation_time, 0.0)
    
    def test_take_damage(self):
        """Test that player takes damage correctly."""
        player = Player(100, 100)
        
        with patch('builtins.print') as mock_print:
            player.take_damage(25)
            
            self.assertEqual(player.current_health, 75)
            mock_print.assert_called_with("Player takes 25 damage. Health: 75/100")
    
    def test_take_damage_death(self):
        """Test that player dies when health reaches 0."""
        player = Player(100, 100)
        player.current_health = 10
        
        with patch('builtins.print') as mock_print:
            player.take_damage(15)
            
            self.assertEqual(player.current_health, 0)
            # Should print both damage and death messages
            self.assertEqual(mock_print.call_count, 2)
    
    def test_heal(self):
        """Test that player heals correctly."""
        player = Player(100, 100)
        player.current_health = 50
        
        with patch('builtins.print') as mock_print:
            player.heal(30)
            
            self.assertEqual(player.current_health, 80)
            mock_print.assert_called_with("Player healed for 30. Health: 80/100")
    
    def test_heal_max_health(self):
        """Test that healing doesn't exceed max health."""
        player = Player(100, 100)
        player.current_health = 90
        
        with patch('builtins.print') as mock_print:
            player.heal(20)
            
            self.assertEqual(player.current_health, 100)
            mock_print.assert_called_with("Player healed for 10. Health: 100/100")
    
    def test_add_experience(self):
        """Test that player gains experience correctly."""
        player = Player(100, 100)
        
        with patch('builtins.print') as mock_print:
            player.add_experience(50)
            
            self.assertEqual(player.experience, 50)
            mock_print.assert_called_with("Player gains 50 experience. Total: 50")
    
    def test_level_up(self):
        """Test that player levels up correctly."""
        player = Player(100, 100)
        
        with patch('builtins.print') as mock_print:
            player.add_experience(100)  # Should trigger level up
            
            self.assertEqual(player.level, 2)
            self.assertEqual(player.max_health, 110)
            self.assertEqual(player.current_health, 110)
    
    def test_add_item(self):
        """Test that items are added to inventory correctly."""
        player = Player(100, 100)
        
        with patch('builtins.print') as mock_print:
            result = player.add_item("Health Potion")
            
            self.assertTrue(result)
            self.assertIn("Health Potion", player.inventory)
            mock_print.assert_called_with("Added Health Potion to inventory")
    
    def test_add_item_full_inventory(self):
        """Test that items are rejected when inventory is full."""
        player = Player(100, 100)
        
        # Fill inventory
        player.inventory = ["Item"] * player.max_inventory_size
        
        with patch('builtins.print') as mock_print:
            result = player.add_item("New Item")
            
            self.assertFalse(result)
            mock_print.assert_called_with("Inventory is full!")
    
    def test_remove_item(self):
        """Test that items are removed from inventory correctly."""
        player = Player(100, 100)
        player.inventory = ["Health Potion", "Sword"]
        
        with patch('builtins.print') as mock_print:
            result = player.remove_item("Health Potion")
            
            self.assertTrue(result)
            self.assertNotIn("Health Potion", player.inventory)
            mock_print.assert_called_with("Removed Health Potion from inventory")
    
    def test_remove_item_not_found(self):
        """Test removing item that doesn't exist in inventory."""
        player = Player(100, 100)
        player.inventory = ["Sword"]
        
        with patch('builtins.print') as mock_print:
            result = player.remove_item("Health Potion")
            
            self.assertFalse(result)
            mock_print.assert_called_with("Health Potion not found in inventory")
    
    def test_get_health_percentage(self):
        """Test health percentage calculation."""
        player = Player(100, 100)
        
        # Full health
        self.assertEqual(player.get_health_percentage(), 1.0)
        
        # Half health
        player.current_health = 50
        self.assertEqual(player.get_health_percentage(), 0.5)
        
        # No health
        player.current_health = 0
        self.assertEqual(player.get_health_percentage(), 0.0)
    
    def test_get_stats(self):
        """Test that player stats are returned correctly."""
        player = Player(100, 200)
        player.level = 2
        player.current_health = 80
        player.experience = 150
        player.facing_direction = 'right'
        player.inventory = ["Item1", "Item2"]
        
        stats = player.get_stats()
        
        expected_stats = {
            'level': 2,
            'health': 80,
            'max_health': 100,
            'experience': 150,
            'speed': 100,
            'base_speed': 100,
            'position': (100, 200),
            'facing_direction': 'right',
            'inventory_count': 2,
            'is_moving': False,
            'animation_frame': 0,
            'is_attacking': False,
            'attack_damage': 20,
            'attack_range': 40
        }
        
        self.assertEqual(stats, expected_stats)


    def test_set_boundaries(self):
        """Test setting movement boundaries."""
        player = Player(100, 100)
        
        player.set_boundaries(10, 20, 300, 400)
        
        self.assertEqual(player.boundary_left, 10)
        self.assertEqual(player.boundary_top, 20)
        self.assertEqual(player.boundary_right, 300)
        self.assertEqual(player.boundary_bottom, 400)
    
    def test_boundary_constraints_x(self):
        """Test that player is constrained by X boundaries."""
        player = Player(100, 100)
        player.set_boundaries(50, 50, 200, 200)
        
        # Test left boundary
        constrained_x, constrained_y = player._apply_boundary_constraints(30, 100)
        self.assertEqual(constrained_x, 50)  # Should be clamped to left boundary
        self.assertEqual(constrained_y, 100)
        
        # Test right boundary (account for player width)
        constrained_x, constrained_y = player._apply_boundary_constraints(180, 100)
        self.assertEqual(constrained_x, 168)  # 200 - 32 (player width)
        self.assertEqual(constrained_y, 100)
    
    def test_boundary_constraints_y(self):
        """Test that player is constrained by Y boundaries."""
        player = Player(100, 100)
        player.set_boundaries(50, 50, 200, 200)
        
        # Test top boundary
        constrained_x, constrained_y = player._apply_boundary_constraints(100, 30)
        self.assertEqual(constrained_x, 100)
        self.assertEqual(constrained_y, 50)  # Should be clamped to top boundary
        
        # Test bottom boundary (account for player height)
        constrained_x, constrained_y = player._apply_boundary_constraints(100, 180)
        self.assertEqual(constrained_x, 100)
        self.assertEqual(constrained_y, 168)  # 200 - 32 (player height)
    
    def test_is_at_boundary(self):
        """Test boundary detection."""
        player = Player(50, 50)  # At left and top boundaries
        player.set_boundaries(50, 50, 200, 200)
        
        boundaries = player.is_at_boundary()
        
        self.assertTrue(boundaries['left'])
        self.assertTrue(boundaries['top'])
        self.assertFalse(boundaries['right'])
        self.assertFalse(boundaries['bottom'])
    
    def test_can_move_in_direction(self):
        """Test movement direction checking."""
        player = Player(50, 50)  # At left and top boundaries
        player.set_boundaries(50, 50, 200, 200)
        
        # Should not be able to move left or up (at boundaries)
        self.assertFalse(player.can_move_in_direction('left'))
        self.assertFalse(player.can_move_in_direction('up'))
        
        # Should be able to move right and down
        self.assertTrue(player.can_move_in_direction('right'))
        self.assertTrue(player.can_move_in_direction('down'))
    
    def test_speed_modifier(self):
        """Test speed modification."""
        player = Player(100, 100)
        original_speed = player.base_speed
        
        # Test speed boost
        player.set_speed_modifier(1.5)
        self.assertEqual(player.speed, original_speed * 1.5)
        
        # Test speed reduction
        player.set_speed_modifier(0.5)
        self.assertEqual(player.speed, original_speed * 0.5)
        
        # Test reset
        player.reset_speed()
        self.assertEqual(player.speed, original_speed)
    
    def test_animation_speed_control(self):
        """Test that animation speed can be controlled."""
        player = Player(100, 100)
        player.is_moving = True
        
        # Set custom animation speed
        player.animation_speed = 0.1
        
        # Update with time less than animation speed
        player._update_animation(0.05)
        self.assertEqual(player.animation_frame, 0)
        
        # Update with time equal to animation speed
        player._update_animation(0.05)  # Total 0.1
        self.assertEqual(player.animation_frame, 1)
    
    def test_direction_sprites_creation(self):
        """Test that direction-specific sprites are created."""
        player = Player(100, 100)
        
        # Should have sprites for all directions
        expected_directions = ['up', 'down', 'left', 'right']
        for direction in expected_directions:
            self.assertIn(direction, player.direction_sprites)
    
    def test_facing_direction_persistence(self):
        """Test that facing direction persists when not moving."""
        player = Player(100, 100)
        input_system = MagicMock()
        
        # Move right
        input_system.get_movement_vector.return_value = (1.0, 0.0)
        input_system.get_movement_direction.return_value = 'right'
        input_system.is_action_just_pressed.return_value = False
        player.handle_input(input_system)
        
        self.assertEqual(player.facing_direction, 'right')
        self.assertEqual(player.last_facing_direction, 'right')
        
        # Stop moving
        input_system.get_movement_vector.return_value = (0.0, 0.0)
        input_system.get_movement_direction.return_value = 'idle'
        player.handle_input(input_system)
        
        # Should still be facing right
        self.assertEqual(player.last_facing_direction, 'right')
    
    def test_get_movement_info(self):
        """Test movement information retrieval."""
        player = Player(100, 200)
        player.velocity_x = 50.0
        player.velocity_y = -30.0
        player.is_moving = True
        player.facing_direction = 'up'
        player.animation_frame = 2
        
        info = player.get_movement_info()
        
        expected_info = {
            'position': (100, 200),
            'velocity': (50.0, -30.0),
            'is_moving': True,
            'facing_direction': 'up',
            'last_facing_direction': 'down',  # Default
            'animation_frame': 2,
            'speed': 100,  # Default speed
            'at_boundaries': {
                'left': False,
                'right': False,
                'top': False,
                'bottom': False
            }
        }
        
        self.assertEqual(info, expected_info)
    
    def test_animation_offset_calculation(self):
        """Test animation offset calculation."""
        player = Player(100, 100)
        player.is_moving = True
        
        # Test different animation frames
        player.animation_frame = 0
        offset = player._get_animation_offset()
        self.assertEqual(offset, (0, 0))
        
        player.animation_frame = 1
        offset = player._get_animation_offset()
        self.assertEqual(offset, (0, -1))  # Step frame
        
        player.animation_frame = 2
        player.facing_direction = 'right'
        offset = player._get_animation_offset()
        self.assertEqual(offset, (1, 0))  # Horizontal movement
    
    def test_update_with_boundaries(self):
        """Test that update respects boundaries."""
        player = Player(100, 100)
        player.set_boundaries(50, 50, 200, 200)
        
        # Try to move beyond left boundary
        player.velocity_x = -200  # Large negative velocity
        player.velocity_y = 0
        
        player.update(1.0)  # 1 second
        
        # Should be clamped to left boundary
        self.assertEqual(player.x, 50)
        self.assertEqual(player.y, 100)
    
    def test_attack_basic(self):
        """Test basic attack functionality."""
        player = Player(100, 100)
        
        with patch('time.time', return_value=1.0):
            with patch('builtins.print') as mock_print:
                player.attack()
                
                self.assertTrue(player.is_attacking)
                self.assertEqual(player.attack_time, 0.0)
                self.assertEqual(player.last_attack_time, 1.0)
                mock_print.assert_called_with("Player attacks in direction: down")
    
    def test_attack_cooldown(self):
        """Test that attack has cooldown."""
        player = Player(100, 100)
        
        with patch('time.time', side_effect=[1.0, 1.2]):  # 0.2 seconds later
            player.attack()  # First attack
            self.assertTrue(player.is_attacking)
            
            player.attack()  # Second attack (should be blocked by cooldown)
            # Should still be in first attack state
            self.assertTrue(player.is_attacking)
    
    def test_attack_after_cooldown(self):
        """Test that attack works after cooldown period."""
        player = Player(100, 100)
        
        with patch('time.time', side_effect=[1.0, 2.0]):  # 1 second later (> cooldown)
            player.attack()  # First attack
            player.is_attacking = False  # Simulate attack finishing
            
            player.attack()  # Second attack (should work)
            self.assertTrue(player.is_attacking)
    
    def test_attack_state_update(self):
        """Test that attack state updates correctly over time."""
        player = Player(100, 100)
        player.is_attacking = True
        player.attack_time = 0.0
        
        # Update for half the attack duration
        player._update_attack_state(0.15)  # Half of 0.3 seconds
        self.assertTrue(player.is_attacking)
        self.assertEqual(player.attack_time, 0.15)
        
        # Update to complete the attack
        player._update_attack_state(0.15)  # Total 0.3 seconds
        self.assertFalse(player.is_attacking)
        self.assertEqual(player.attack_time, 0.0)
    
    def test_get_attack_rect_down(self):
        """Test attack rectangle calculation for down direction."""
        player = Player(100, 100)
        player.facing_direction = 'down'
        
        attack_rect = player.get_attack_rect()
        
        # Attack should be below the player
        expected_x = 100 - (40 - 32) // 2  # Centered horizontally
        expected_y = 100 + 32  # Below player
        
        self.assertEqual(attack_rect.x, expected_x)
        self.assertEqual(attack_rect.y, expected_y)
        self.assertEqual(attack_rect.width, 40)
        self.assertEqual(attack_rect.height, 40)
    
    def test_get_attack_rect_up(self):
        """Test attack rectangle calculation for up direction."""
        player = Player(100, 100)
        player.facing_direction = 'up'
        
        attack_rect = player.get_attack_rect()
        
        # Attack should be above the player
        expected_x = 100 - (40 - 32) // 2  # Centered horizontally
        expected_y = 100 - 40  # Above player
        
        self.assertEqual(attack_rect.x, expected_x)
        self.assertEqual(attack_rect.y, expected_y)
    
    def test_get_attack_rect_left(self):
        """Test attack rectangle calculation for left direction."""
        player = Player(100, 100)
        player.facing_direction = 'left'
        
        attack_rect = player.get_attack_rect()
        
        # Attack should be to the left of the player
        expected_x = 100 - 40  # Left of player
        expected_y = 100 - (40 - 32) // 2  # Centered vertically
        
        self.assertEqual(attack_rect.x, expected_x)
        self.assertEqual(attack_rect.y, expected_y)
    
    def test_get_attack_rect_right(self):
        """Test attack rectangle calculation for right direction."""
        player = Player(100, 100)
        player.facing_direction = 'right'
        
        attack_rect = player.get_attack_rect()
        
        # Attack should be to the right of the player
        expected_x = 100 + 32  # Right of player
        expected_y = 100 - (40 - 32) // 2  # Centered vertically
        
        self.assertEqual(attack_rect.x, expected_x)
        self.assertEqual(attack_rect.y, expected_y)
    
    def test_is_attack_active(self):
        """Test attack active state during animation."""
        player = Player(100, 100)
        
        # Not attacking
        self.assertFalse(player.is_attack_active())
        
        # Start attacking
        player.is_attacking = True
        player.attack_time = 0.1  # Early in attack
        self.assertTrue(player.is_attack_active())
        
        # Later in attack (past damage window)
        player.attack_time = 0.25  # Past 60% of 0.3 seconds
        self.assertFalse(player.is_attack_active())
    
    def test_get_attack_damage(self):
        """Test attack damage calculation."""
        player = Player(100, 100)
        
        damage = player.get_attack_damage()
        self.assertEqual(damage, 20)  # Base attack damage
    
    def test_update_prevents_movement_during_attack(self):
        """Test that player cannot move while attacking."""
        player = Player(100, 100)
        player.velocity_x = 50.0
        player.velocity_y = 30.0
        player.is_attacking = True
        
        original_x = player.x
        original_y = player.y
        
        player.update(0.1)
        
        # Position should not change during attack
        self.assertEqual(player.x, original_x)
        self.assertEqual(player.y, original_y)


if __name__ == '__main__':
    unittest.main()