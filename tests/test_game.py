"""
Unit tests for the Game class.
Tests initialization, configuration loading, and basic functionality.
"""
import unittest
import pygame
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
import sys

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.game import Game


class TestGame(unittest.TestCase):
    """Test cases for the Game class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file for testing
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        test_config = {
            "display": {
                "width": 640,
                "height": 480,
                "title": "Test Game",
                "fps": 30
            },
            "game": {
                "tile_size": 16,
                "player_speed": 50,
                "debug_mode": True
            }
        }
        json.dump(test_config, self.temp_config)
        self.temp_config.close()
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Remove temporary config file
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
    
    @patch('pygame.init')
    @patch('pygame.mixer.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_game_initialization(self, mock_caption, mock_set_mode, mock_mixer_init, mock_init):
        """Test that Game initializes correctly with custom config."""
        mock_screen = MagicMock()
        mock_set_mode.return_value = mock_screen
        
        game = Game(self.temp_config.name)
        
        # Check that pygame was initialized
        mock_init.assert_called_once()
        mock_mixer_init.assert_called_once()
        
        # Check that display was set up correctly
        mock_set_mode.assert_called_once_with((640, 480))
        mock_caption.assert_called_once_with("Test Game")
        
        # Check configuration was loaded correctly
        self.assertEqual(game.screen_width, 640)
        self.assertEqual(game.screen_height, 480)
        self.assertEqual(game.window_title, "Test Game")
        self.assertEqual(game.target_fps, 30)
        
        # Check that resource manager was created
        self.assertIsNotNone(game.resource_manager)
    
    @patch('pygame.init')
    @patch('pygame.mixer.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_game_default_config(self, mock_caption, mock_set_mode, mock_mixer_init, mock_init):
        """Test that Game uses default config when file doesn't exist."""
        mock_screen = MagicMock()
        mock_set_mode.return_value = mock_screen
        
        game = Game("nonexistent_config.json")
        
        # Check default values are used
        self.assertEqual(game.screen_width, 800)
        self.assertEqual(game.screen_height, 600)
        self.assertEqual(game.window_title, "Zelda-like 2D Game")
        self.assertEqual(game.target_fps, 60)
    
    @patch('pygame.init')
    @patch('pygame.mixer.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    def test_game_properties(self, mock_caption, mock_set_mode, mock_mixer_init, mock_init):
        """Test Game property methods."""
        mock_screen = MagicMock()
        mock_set_mode.return_value = mock_screen
        
        game = Game(self.temp_config.name)
        
        # Test screen size getter
        self.assertEqual(game.get_screen_size(), (640, 480))
        
        # Test initial running state
        self.assertFalse(game.is_running())
        
        # Test delta time (should be 0 initially)
        self.assertEqual(game.get_delta_time(), 0.0)
    
    @patch('pygame.init')
    @patch('pygame.mixer.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.time.Clock')
    def test_quit_functionality(self, mock_clock, mock_caption, mock_set_mode, mock_mixer_init, mock_init):
        """Test that quit method sets running to False."""
        mock_screen = MagicMock()
        mock_set_mode.return_value = mock_screen
        mock_clock_instance = MagicMock()
        mock_clock.return_value = mock_clock_instance
        
        game = Game(self.temp_config.name)
        
        # Initially not running
        self.assertFalse(game.is_running())
        
        # Set running to True (simulating game start)
        game.running = True
        self.assertTrue(game.is_running())
        
        # Call quit
        game.quit()
        self.assertFalse(game.is_running())
    
    @patch('pygame.init')
    @patch('pygame.mixer.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.event.get')
    def test_handle_events_quit(self, mock_get_events, mock_caption, mock_set_mode, mock_mixer_init, mock_init):
        """Test that quit event is handled correctly."""
        mock_screen = MagicMock()
        mock_set_mode.return_value = mock_screen
        
        # Mock quit event
        quit_event = MagicMock()
        quit_event.type = pygame.QUIT
        mock_get_events.return_value = [quit_event]
        
        game = Game(self.temp_config.name)
        game.running = True
        
        # Handle events should set running to False
        game.handle_events()
        self.assertFalse(game.running)
    
    @patch('pygame.init')
    @patch('pygame.mixer.init')
    @patch('pygame.display.set_mode')
    @patch('pygame.display.set_caption')
    @patch('pygame.event.get')
    def test_handle_events_escape(self, mock_get_events, mock_caption, mock_set_mode, mock_mixer_init, mock_init):
        """Test that escape key quits the game."""
        mock_screen = MagicMock()
        mock_set_mode.return_value = mock_screen
        
        # Mock escape key event
        escape_event = MagicMock()
        escape_event.type = pygame.KEYDOWN
        escape_event.key = pygame.K_ESCAPE
        mock_get_events.return_value = [escape_event]
        
        game = Game(self.temp_config.name)
        game.running = True
        
        # Handle events should set running to False
        game.handle_events()
        self.assertFalse(game.running)


if __name__ == '__main__':
    unittest.main()