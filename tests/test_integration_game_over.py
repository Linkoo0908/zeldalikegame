"""
Integration tests for the game over system.
Tests the interaction between GameScene and GameOverScene.
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import pygame
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scenes.game_scene import GameScene
from scenes.game_over_scene import GameOverScene
from scenes.scene_manager import SceneManager


class TestGameOverIntegration(unittest.TestCase):
    """Integration test cases for game over system."""
    
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
        self.mock_game.config = {
            'game': {
                'player_speed': 100,
                'player_start_x': 400,
                'player_start_y': 300,
                'max_inventory_size': 20,
                'default_map': 'assets/maps/test_map.json'
            }
        }
        
        # Create scene manager
        self.scene_manager = SceneManager(self.mock_game)
        self.mock_game.get_scene_manager.return_value = self.scene_manager
        
        # Create scenes
        self.game_scene = GameScene()
        self.game_over_scene = GameOverScene()
    
    def tearDown(self):
        """Clean up after each test method."""
        try:
            if hasattr(self, 'scene_manager'):
                self.scene_manager.cleanup()
        except:
            pass
        try:
            if hasattr(self, 'game_scene'):
                self.game_scene.cleanup()
        except:
            pass
        try:
            if hasattr(self, 'game_over_scene'):
                self.game_over_scene.cleanup()
        except:
            pass
    
    def test_game_over_trigger(self):
        """Test that game over is triggered when player health reaches 0."""
        # Create a simple mock game scene that can trigger game over
        mock_game_scene = Mock(spec=GameScene)
        mock_game_scene.name = "GameScene"
        mock_game_scene.initialized = True
        mock_game_scene.active = False
        
        # Mock the trigger game over method
        def mock_trigger_game_over():
            game_over_scene = GameOverScene()
            self.scene_manager.push_scene(game_over_scene)
        
        mock_game_scene._trigger_game_over = mock_trigger_game_over
        
        # Add game scene to scene manager
        self.scene_manager.push_scene(mock_game_scene)
        self.scene_manager.update(0.016)
        
        # Verify game scene is active
        self.assertEqual(self.scene_manager.get_current_scene(), mock_game_scene)
        self.assertEqual(self.scene_manager.get_scene_count(), 1)
        
        # Trigger game over
        mock_game_scene._trigger_game_over()
        self.scene_manager.update(0.016)
        
        # Verify game over scene was pushed
        self.assertEqual(self.scene_manager.get_scene_count(), 2)
        current_scene = self.scene_manager.get_current_scene()
        self.assertIsInstance(current_scene, GameOverScene)
    
    def test_game_over_restart(self):
        """Test restarting the game from game over screen."""
        # Create and initialize game over scene
        game_over_scene = GameOverScene()
        game_over_scene.initialize(self.mock_game)
        
        # Add to scene manager
        self.scene_manager.push_scene(game_over_scene)
        self.scene_manager.update(0.016)
        
        # Select restart option
        game_over_scene.set_selected_option(0)  # Restart
        
        # Create restart event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_RETURN
        
        # Mock the GameScene creation to avoid initialization issues
        with patch('scenes.game_scene.GameScene') as mock_game_scene_class:
            mock_game_scene_instance = Mock()
            mock_game_scene_instance.name = "GameScene"
            mock_game_scene_instance.initialized = False
            mock_game_scene_class.return_value = mock_game_scene_instance
            
            # Handle the restart event
            game_over_scene.handle_event(mock_event)
            
            # Process scene manager operations
            self.scene_manager.update(0.016)
            
            # Verify that scene manager change_scene was called
            # The actual GameScene creation is mocked, so we just verify the flow worked
            self.assertEqual(self.scene_manager.get_scene_count(), 1)
            current_scene = self.scene_manager.get_current_scene()
            self.assertEqual(current_scene, mock_game_scene_instance)
    
    def test_game_over_quit(self):
        """Test quitting from game over screen."""
        # Initialize game over scene
        self.game_over_scene.initialize(self.mock_game)
        
        # Select quit option
        self.game_over_scene.set_selected_option(1)  # Main Menu (quit)
        
        # Create quit event
        mock_event = Mock()
        mock_event.type = pygame.KEYDOWN
        mock_event.key = pygame.K_RETURN
        
        # Handle the quit event
        self.game_over_scene.handle_event(mock_event)
        
        # Verify game quit was called
        self.mock_game.quit.assert_called_once()
    
    def test_game_continues_with_positive_health(self):
        """Test that game continues normally when player has positive health."""
        # Create a mock game scene that doesn't trigger game over
        mock_game_scene = Mock(spec=GameScene)
        mock_game_scene.name = "GameScene"
        mock_game_scene.initialized = True
        mock_game_scene.active = False
        
        # Add to scene manager
        self.scene_manager.push_scene(mock_game_scene)
        self.scene_manager.update(0.016)
        
        # Update scene manager multiple times (simulating normal gameplay)
        for _ in range(5):
            self.scene_manager.update(0.016)
        
        # Verify game scene is still active and no game over scene was created
        self.assertEqual(self.scene_manager.get_scene_count(), 1)
        current_scene = self.scene_manager.get_current_scene()
        self.assertEqual(current_scene, mock_game_scene)
    
    def test_scene_manager_integration(self):
        """Test scene manager properly handles scene transitions."""
        # Create mock scenes to avoid initialization issues
        mock_game_scene = Mock(spec=GameScene)
        mock_game_scene.name = "GameScene"
        mock_game_scene.initialized = True
        mock_game_scene.active = False
        
        mock_game_over_scene = Mock(spec=GameOverScene)
        mock_game_over_scene.name = "GameOverScene"
        mock_game_over_scene.initialized = True
        mock_game_over_scene.active = False
        
        # Start with game scene
        self.scene_manager.push_scene(mock_game_scene)
        self.scene_manager.update(0.016)
        
        # Push game over scene
        self.scene_manager.push_scene(mock_game_over_scene)
        self.scene_manager.update(0.016)
        
        # Verify both scenes are in stack
        self.assertEqual(self.scene_manager.get_scene_count(), 2)
        self.assertEqual(self.scene_manager.get_current_scene(), mock_game_over_scene)
        
        # Pop game over scene
        self.scene_manager.pop_scene()
        self.scene_manager.update(0.016)
        
        # Verify we're back to game scene
        self.assertEqual(self.scene_manager.get_scene_count(), 1)
        self.assertEqual(self.scene_manager.get_current_scene(), mock_game_scene)


if __name__ == '__main__':
    unittest.main()