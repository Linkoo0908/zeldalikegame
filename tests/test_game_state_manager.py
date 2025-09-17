"""
Tests for the game state manager.
"""
import unittest
import os
import json
import tempfile
from unittest.mock import Mock
import sys

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from systems.game_state_manager import GameStateManager


class TestGameStateManager(unittest.TestCase):
    """Test cases for GameStateManager."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state_manager = GameStateManager()
        
        # Create temporary file for save tests
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        self.temp_file_path = self.temp_file.name
    
    def tearDown(self):
        """Clean up after tests."""
        # Remove temporary file
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)
    
    def test_initialization(self):
        """Test state manager initialization."""
        self.assertEqual(len(self.state_manager.player_state), 0)
        self.assertEqual(len(self.state_manager.global_flags), 0)
        self.assertEqual(len(self.state_manager.map_visit_count), 0)
        self.assertEqual(self.state_manager.total_playtime, 0.0)
    
    def test_save_player_state(self):
        """Test saving player state."""
        # Create mock player
        mock_player = Mock()
        mock_player.x = 100
        mock_player.y = 200
        mock_player.current_health = 80
        mock_player.max_health = 100
        mock_player.experience = 150
        mock_player.level = 2
        mock_player.attack_power = 15
        mock_player.defense = 8
        mock_player.speed = 120
        
        # Save player state
        self.state_manager.save_player_state(mock_player)
        
        # Verify state was saved
        self.assertIn('position', self.state_manager.player_state)
        self.assertEqual(self.state_manager.player_state['position']['x'], 100)
        self.assertEqual(self.state_manager.player_state['position']['y'], 200)
        self.assertEqual(self.state_manager.player_state['health']['current'], 80)
        self.assertEqual(self.state_manager.player_state['health']['max'], 100)
        self.assertEqual(self.state_manager.player_state['experience'], 150)
        self.assertEqual(self.state_manager.player_state['level'], 2)
    
    def test_restore_player_state(self):
        """Test restoring player state."""
        # Set up saved state
        self.state_manager.player_state = {
            'position': {'x': 300, 'y': 400},
            'health': {'current': 60, 'max': 100},
            'experience': 200,
            'level': 3,
            'stats': {'attack': 20, 'defense': 10, 'speed': 110}
        }
        
        # Create mock player
        mock_player = Mock()
        mock_player.x = 0
        mock_player.y = 0
        mock_player.current_health = 100
        mock_player.max_health = 100
        mock_player.experience = 0
        mock_player.level = 1
        mock_player.attack_power = 10
        mock_player.defense = 5
        mock_player.speed = 100
        
        # Restore player state
        self.state_manager.restore_player_state(mock_player)
        
        # Verify state was restored
        self.assertEqual(mock_player.x, 300)
        self.assertEqual(mock_player.y, 400)
        self.assertEqual(mock_player.current_health, 60)
        self.assertEqual(mock_player.max_health, 100)
        self.assertEqual(mock_player.experience, 200)
        self.assertEqual(mock_player.level, 3)
        self.assertEqual(mock_player.attack_power, 20)
        self.assertEqual(mock_player.defense, 10)
        self.assertEqual(mock_player.speed, 110)
    
    def test_global_flags(self):
        """Test global flag management."""
        # Set flags
        self.state_manager.set_global_flag('quest_completed', True)
        self.state_manager.set_global_flag('boss_defeated', False)
        self.state_manager.set_global_flag('secret_found', 'treasure_room')
        
        # Get flags
        self.assertTrue(self.state_manager.get_global_flag('quest_completed'))
        self.assertFalse(self.state_manager.get_global_flag('boss_defeated'))
        self.assertEqual(self.state_manager.get_global_flag('secret_found'), 'treasure_room')
        
        # Test default value
        self.assertIsNone(self.state_manager.get_global_flag('nonexistent'))
        self.assertEqual(self.state_manager.get_global_flag('nonexistent', 'default'), 'default')
    
    def test_map_visit_tracking(self):
        """Test map visit count tracking."""
        map_path = "assets/maps/test_map.json"
        
        # Initial visit count should be 0
        self.assertEqual(self.state_manager.get_map_visit_count(map_path), 0)
        
        # Increment visit count
        count1 = self.state_manager.increment_map_visit(map_path)
        self.assertEqual(count1, 1)
        self.assertEqual(self.state_manager.get_map_visit_count(map_path), 1)
        
        # Increment again
        count2 = self.state_manager.increment_map_visit(map_path)
        self.assertEqual(count2, 2)
        self.assertEqual(self.state_manager.get_map_visit_count(map_path), 2)
    
    def test_playtime_tracking(self):
        """Test playtime tracking."""
        # Initial playtime should be 0
        self.assertEqual(self.state_manager.get_playtime(), 0.0)
        
        # Add playtime
        self.state_manager.add_playtime(60.5)  # 1 minute 0.5 seconds
        self.assertEqual(self.state_manager.get_playtime(), 60.5)
        
        # Add more playtime
        self.state_manager.add_playtime(120.0)  # 2 minutes
        self.assertEqual(self.state_manager.get_playtime(), 180.5)
    
    def test_playtime_formatting(self):
        """Test playtime formatting."""
        # Test seconds only
        self.state_manager.total_playtime = 45.7
        self.assertEqual(self.state_manager.get_playtime_formatted(), "45s")
        
        # Test minutes and seconds
        self.state_manager.total_playtime = 125.3  # 2m 5s
        self.assertEqual(self.state_manager.get_playtime_formatted(), "2m 5s")
        
        # Test hours, minutes, and seconds
        self.state_manager.total_playtime = 3725.8  # 1h 2m 5s
        self.assertEqual(self.state_manager.get_playtime_formatted(), "1h 2m 5s")
    
    def test_create_save_data(self):
        """Test creating save data."""
        # Set up some state
        self.state_manager.player_state = {'level': 5}
        self.state_manager.set_global_flag('test_flag', True)
        self.state_manager.increment_map_visit('test_map.json')
        self.state_manager.add_playtime(100.0)
        
        # Create save data
        save_data = self.state_manager.create_save_data()
        
        # Verify save data structure
        self.assertIn('player_state', save_data)
        self.assertIn('global_flags', save_data)
        self.assertIn('map_visit_count', save_data)
        self.assertIn('total_playtime', save_data)
        self.assertIn('version', save_data)
        
        # Verify content
        self.assertEqual(save_data['player_state']['level'], 5)
        self.assertTrue(save_data['global_flags']['test_flag'])
        self.assertEqual(save_data['map_visit_count']['test_map.json'], 1)
        self.assertEqual(save_data['total_playtime'], 100.0)
    
    def test_load_save_data(self):
        """Test loading save data."""
        save_data = {
            'player_state': {'level': 10},
            'global_flags': {'loaded_flag': True},
            'map_visit_count': {'loaded_map.json': 3},
            'total_playtime': 500.0,
            'version': '1.0'
        }
        
        # Load save data
        self.state_manager.load_save_data(save_data)
        
        # Verify data was loaded
        self.assertEqual(self.state_manager.player_state['level'], 10)
        self.assertTrue(self.state_manager.get_global_flag('loaded_flag'))
        self.assertEqual(self.state_manager.get_map_visit_count('loaded_map.json'), 3)
        self.assertEqual(self.state_manager.get_playtime(), 500.0)
    
    def test_save_to_file(self):
        """Test saving to file."""
        # Set up some state
        self.state_manager.player_state = {'test': 'data'}
        self.state_manager.set_global_flag('file_test', True)
        
        # Save to file
        success = self.state_manager.save_to_file(self.temp_file_path)
        self.assertTrue(success)
        
        # Verify file was created and contains correct data
        self.assertTrue(os.path.exists(self.temp_file_path))
        
        with open(self.temp_file_path, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        self.assertEqual(loaded_data['player_state']['test'], 'data')
        self.assertTrue(loaded_data['global_flags']['file_test'])
    
    def test_load_from_file(self):
        """Test loading from file."""
        # Create test save file
        test_data = {
            'player_state': {'file_level': 7},
            'global_flags': {'file_flag': False},
            'map_visit_count': {},
            'total_playtime': 200.0,
            'version': '1.0'
        }
        
        with open(self.temp_file_path, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Load from file
        success = self.state_manager.load_from_file(self.temp_file_path)
        self.assertTrue(success)
        
        # Verify data was loaded
        self.assertEqual(self.state_manager.player_state['file_level'], 7)
        self.assertFalse(self.state_manager.get_global_flag('file_flag'))
        self.assertEqual(self.state_manager.get_playtime(), 200.0)
    
    def test_load_from_nonexistent_file(self):
        """Test loading from nonexistent file."""
        success = self.state_manager.load_from_file('nonexistent_file.json')
        self.assertFalse(success)
    
    def test_reset_state(self):
        """Test resetting state."""
        # Set up some state
        self.state_manager.player_state = {'level': 5}
        self.state_manager.set_global_flag('test', True)
        self.state_manager.increment_map_visit('test.json')
        self.state_manager.add_playtime(100.0)
        
        # Reset state
        self.state_manager.reset_state()
        
        # Verify everything was reset
        self.assertEqual(len(self.state_manager.player_state), 0)
        self.assertEqual(len(self.state_manager.global_flags), 0)
        self.assertEqual(len(self.state_manager.map_visit_count), 0)
        self.assertEqual(self.state_manager.total_playtime, 0.0)
    
    def test_get_state_summary(self):
        """Test getting state summary."""
        # Set up some state
        self.state_manager.player_state = {
            'level': 8,
            'health': {'current': 75}
        }
        self.state_manager.set_global_flag('flag1', True)
        self.state_manager.set_global_flag('flag2', False)
        self.state_manager.increment_map_visit('map1.json')
        self.state_manager.increment_map_visit('map2.json')
        self.state_manager.add_playtime(3665.0)  # 1h 1m 5s
        
        # Get summary
        summary = self.state_manager.get_state_summary()
        
        # Verify summary
        self.assertTrue(summary['has_player_state'])
        self.assertEqual(summary['global_flags_count'], 2)
        self.assertEqual(summary['maps_visited'], 2)
        self.assertEqual(summary['total_playtime'], '1h 1m 5s')
        self.assertEqual(summary['player_level'], 8)
        self.assertEqual(summary['player_health'], 75)


if __name__ == '__main__':
    unittest.main()