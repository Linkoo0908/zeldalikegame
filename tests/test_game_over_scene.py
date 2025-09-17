"""
Unit tests for the GameOverScene class.
Tests game over functionality, menu navigation, and restart mechanics.
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import pygame
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scenes.game_over_scene import GameOverScene


class TestGameOverScene(unittest.TestCase):
    """Test cases for GameOverScene class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock pygame to avoid initialization issues
        pygame.init = Mock()
        pygame.display.set_mode = Mock(return_value=Mock())
        pygame.display.set_caption = Mock()
        pygame.time.Clock = Mock()
        pygame.font.Font = Mock(return_value=Mock())
        
        # Create mock game instance
        self.mock_game = Mock()
        self.mock_game.get_screen_size.return_value = (800, 600)
        self.mock_game.get_scene_manager.return_value = Mock()
        
        # Create game over scene
        self.game_over_scene = GameOverScene()
    
    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self, 'game_over_scene'):
            self.game_over_scene.cleanup()
    
    def test_initialization(self):
        """Test GameOverScene initialization."""
        self.assertEqual(self.game_over_scene.get_name(), "GameOverScene")
        self.assertFalse(self.game_over_scene.is_initialized())
        self.assertFalse(self.game_over_scene.is_active())
        self.assertEqual(self.game_over_scene.selected_option, 0)
        self.assertEqual(len(self.game_over_scene.options), 2)
    
    def test_scene_initialization(self):
        """Test scene initialization with game reference."""
        self.game_over_scene.initialize(self.mock_game)
        
        self.assertTrue(self.game_over_scene.initialized)
        self.assertEqual(self.game_over_scene.game, self.mock_game)
        self.assertEqual(self.game_over_scene.screen_width, 800)
        self.assertEqual(self.game_over_scene.screen_height, 600)
    
    def test_handle_event_navigation_up(self):
        """Test navigation up event handling."""
        # Set initial selection to 1
        self.game_over_scene.selected_option = 1
        
        # Create mock event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_UP
        
        # Handle event
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertTrue(result)
        self.assertEqual(self.game_over_scene.selected_option, 0)
    
    def test_handle_event_navigation_down(self):
        """Test navigation down event handling."""
        # Set initial selection to 0
        self.game_over_scene.selected_option = 0
        
        # Create mock event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_DOWN
        
        # Handle event
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertTrue(result)
        self.assertEqual(self.game_over_scene.selected_option, 1)
    
    def test_handle_event_navigation_wraparound(self):
        """Test navigation wraparound."""
        # Test wrapping from last to first
        self.game_over_scene.selected_option = 1
        
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_DOWN
        
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertTrue(result)
        self.assertEqual(self.game_over_scene.selected_option, 0)
        
        # Test wrapping from first to last
        mock_event.key = pygame.K_UP
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertTrue(result)
        self.assertEqual(self.game_over_scene.selected_option, 1)
    
    def test_handle_event_wasd_navigation(self):
        """Test WASD navigation."""
        # Test W key (up)
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_w
        
        self.game_over_scene.selected_option = 1
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertTrue(result)
        self.assertEqual(self.game_over_scene.selected_option, 0)
        
        # Test S key (down)
        mock_event.key = pygame.K_s
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertTrue(result)
        self.assertEqual(self.game_over_scene.selected_option, 1)
    
    def test_handle_event_restart_selection(self):
        """Test restart game selection."""
        # Initialize scene
        self.game_over_scene.initialize(self.mock_game)
        
        # Set selection to restart (0)
        self.game_over_scene.selected_option = 0
        
        # Create mock event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_RETURN
        
        # Mock the GameScene import inside the method
        with patch('scenes.game_scene.GameScene') as mock_game_scene_class:
            # Handle event
            result = self.game_over_scene.handle_event(mock_event)
            
            self.assertTrue(result)
            
            # Verify scene manager was called to change scene
            scene_manager = self.mock_game.get_scene_manager.return_value
            scene_manager.change_scene.assert_called_once()
    
    def test_handle_event_menu_selection(self):
        """Test main menu selection."""
        # Initialize scene
        self.game_over_scene.initialize(self.mock_game)
        
        # Set selection to menu (1)
        self.game_over_scene.selected_option = 1
        
        # Create mock event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_RETURN
        
        # Handle event
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertTrue(result)
        
        # Verify game quit was called
        self.mock_game.quit.assert_called_once()
    
    def test_handle_event_escape_key(self):
        """Test escape key handling."""
        # Initialize scene
        self.game_over_scene.initialize(self.mock_game)
        
        # Create mock event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_ESCAPE
        
        # Handle event
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertTrue(result)
        
        # Verify game quit was called (ESC acts as main menu)
        self.mock_game.quit.assert_called_once()
    
    def test_handle_event_space_key(self):
        """Test space key selection."""
        # Initialize scene
        self.game_over_scene.initialize(self.mock_game)
        
        # Set selection to menu
        self.game_over_scene.selected_option = 1
        
        # Create mock event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_SPACE
        
        # Handle event
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertTrue(result)
        
        # Verify game quit was called
        self.mock_game.quit.assert_called_once()
    
    def test_handle_event_unhandled(self):
        """Test unhandled event."""
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_a  # Random key
        
        result = self.game_over_scene.handle_event(mock_event)
        
        self.assertFalse(result)
    
    def test_update_fade_animation(self):
        """Test fade-in animation update."""
        # Initial state
        self.assertEqual(self.game_over_scene.fade_alpha, 0)
        
        # Update with delta time
        self.game_over_scene.update(0.1)  # 100ms
        
        # Should have increased fade alpha
        expected_alpha = 0.1 * self.game_over_scene.fade_speed
        self.assertEqual(self.game_over_scene.fade_alpha, expected_alpha)
        
        # Update until max fade
        while self.game_over_scene.fade_alpha < self.game_over_scene.max_fade:
            self.game_over_scene.update(0.1)
        
        # Should be capped at max fade
        self.assertEqual(self.game_over_scene.fade_alpha, self.game_over_scene.max_fade)
    
    def test_render(self):
        """Test scene rendering."""
        # Initialize scene
        self.game_over_scene.initialize(self.mock_game)
        
        # Mock screen
        mock_screen = Mock()
        mock_screen.get_size.return_value = (800, 600)
        
        # Mock fonts and text rendering
        mock_font = Mock()
        mock_text = Mock()
        mock_rect = Mock()
        mock_rect.left = 100
        mock_rect.centery = 50
        mock_text.get_rect.return_value = mock_rect
        mock_font.render.return_value = mock_text
        
        self.game_over_scene.title_font = mock_font
        self.game_over_scene.option_font = mock_font
        self.game_over_scene.instruction_font = mock_font
        
        # Mock pygame.Surface for overlay
        with patch('pygame.Surface') as mock_surface:
            mock_overlay = Mock()
            mock_surface.return_value = mock_overlay
            
            # Set some fade alpha
            self.game_over_scene.fade_alpha = 100
            
            # Render scene
            self.game_over_scene.render(mock_screen)
            
            # Verify basic rendering calls
            mock_screen.fill.assert_called_with(self.game_over_scene.bg_color)
            
            # Verify overlay was created if fade_alpha > 0
            mock_surface.assert_called_with(mock_screen.get_size())
            mock_overlay.set_alpha.assert_called_with(100)
    
    def test_render_no_fonts(self):
        """Test rendering when fonts are not available."""
        # Initialize scene without fonts
        self.game_over_scene.initialize(self.mock_game)
        self.game_over_scene.title_font = None
        self.game_over_scene.option_font = None
        self.game_over_scene.instruction_font = None
        
        # Mock screen
        mock_screen = Mock()
        mock_screen.get_size.return_value = (800, 600)
        
        # This should not raise an exception
        self.game_over_scene.render(mock_screen)
        
        # Verify basic rendering still happened
        mock_screen.fill.assert_called_with(self.game_over_scene.bg_color)
    
    def test_option_management(self):
        """Test option getter and setter."""
        # Test getter
        self.assertEqual(self.game_over_scene.get_selected_option(), 0)
        
        # Test setter with valid option
        self.game_over_scene.set_selected_option(1)
        self.assertEqual(self.game_over_scene.get_selected_option(), 1)
        
        # Test setter with invalid option (should not change)
        self.game_over_scene.set_selected_option(5)
        self.assertEqual(self.game_over_scene.get_selected_option(), 1)
        
        self.game_over_scene.set_selected_option(-1)
        self.assertEqual(self.game_over_scene.get_selected_option(), 1)
    
    def test_scene_lifecycle(self):
        """Test scene lifecycle methods."""
        # Test on_enter
        self.game_over_scene.on_enter()
        self.assertTrue(self.game_over_scene.is_active())
        self.assertEqual(self.game_over_scene.fade_alpha, 0)
        self.assertEqual(self.game_over_scene.selected_option, 0)
        
        # Test on_exit
        self.game_over_scene.on_exit()
        self.assertFalse(self.game_over_scene.is_active())
    
    def test_cleanup(self):
        """Test scene cleanup."""
        # Cleanup should not raise any exceptions
        self.game_over_scene.cleanup()


if __name__ == '__main__':
    unittest.main()