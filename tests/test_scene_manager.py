"""
Unit tests for the SceneManager class.
Tests scene management, transitions, and memory management.
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
import pygame
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from scenes.scene import Scene
from scenes.scene_manager import SceneManager


class MockScene(Scene):
    """Mock scene for testing purposes."""
    
    def __init__(self, name: str):
        super().__init__(name)
        self.initialize_called = False
        self.cleanup_called = False
        self.on_enter_called = False
        self.on_exit_called = False
        self.on_pause_called = False
        self.on_resume_called = False
        self.handle_event_called = False
        self.update_called = False
        self.render_called = False
    
    def initialize(self, game) -> None:
        self.initialize_called = True
        self.initialized = True
    
    def cleanup(self) -> None:
        self.cleanup_called = True
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        self.handle_event_called = True
        return True
    
    def update(self, dt: float) -> None:
        self.update_called = True
    
    def render(self, screen: pygame.Surface) -> None:
        self.render_called = True
    
    def on_enter(self) -> None:
        super().on_enter()
        self.on_enter_called = True
    
    def on_exit(self) -> None:
        super().on_exit()
        self.on_exit_called = True
    
    def on_pause(self) -> None:
        super().on_pause()
        self.on_pause_called = True
    
    def on_resume(self) -> None:
        super().on_resume()
        self.on_resume_called = True


class TestSceneManager(unittest.TestCase):
    """Test cases for SceneManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Mock pygame to avoid initialization issues
        pygame.init = Mock()
        pygame.display.set_mode = Mock(return_value=Mock())
        pygame.display.set_caption = Mock()
        pygame.time.Clock = Mock()
        
        # Create mock game instance
        self.mock_game = Mock()
        self.mock_game.screen = Mock()
        
        # Create scene manager
        self.scene_manager = SceneManager(self.mock_game)
        
        # Create test scenes
        self.scene1 = MockScene("TestScene1")
        self.scene2 = MockScene("TestScene2")
        self.scene3 = MockScene("TestScene3")
    
    def tearDown(self):
        """Clean up after each test method."""
        if hasattr(self, 'scene_manager'):
            self.scene_manager.cleanup()
    
    def test_initialization(self):
        """Test SceneManager initialization."""
        self.assertEqual(self.scene_manager.game, self.mock_game)
        self.assertEqual(len(self.scene_manager.scene_stack), 0)
        self.assertEqual(len(self.scene_manager.pending_operations), 0)
        self.assertFalse(self.scene_manager.transitioning)
    
    def test_push_scene(self):
        """Test pushing a scene onto the stack."""
        # Push first scene
        self.scene_manager.push_scene(self.scene1)
        self.assertEqual(len(self.scene_manager.pending_operations), 1)
        
        # Process operations
        self.scene_manager.update(0.016)
        
        # Verify scene was pushed and initialized
        self.assertEqual(self.scene_manager.get_scene_count(), 1)
        self.assertEqual(self.scene_manager.get_current_scene(), self.scene1)
        self.assertTrue(self.scene1.initialize_called)
        self.assertTrue(self.scene1.on_enter_called)
        self.assertTrue(self.scene1.is_active())
    
    def test_push_multiple_scenes(self):
        """Test pushing multiple scenes."""
        # Push first scene
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.update(0.016)
        
        # Push second scene
        self.scene_manager.push_scene(self.scene2)
        self.scene_manager.update(0.016)
        
        # Verify stack state
        self.assertEqual(self.scene_manager.get_scene_count(), 2)
        self.assertEqual(self.scene_manager.get_current_scene(), self.scene2)
        
        # Verify first scene was paused
        self.assertTrue(self.scene1.on_pause_called)
        self.assertFalse(self.scene1.is_active())
        
        # Verify second scene is active
        self.assertTrue(self.scene2.is_active())
        self.assertTrue(self.scene2.on_enter_called)
    
    def test_pop_scene(self):
        """Test popping a scene from the stack."""
        # Push two scenes
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.push_scene(self.scene2)
        self.scene_manager.update(0.016)
        
        # Pop the top scene
        self.scene_manager.pop_scene()
        self.scene_manager.update(0.016)
        
        # Verify scene was popped
        self.assertEqual(self.scene_manager.get_scene_count(), 1)
        self.assertEqual(self.scene_manager.get_current_scene(), self.scene1)
        
        # Verify scene2 was cleaned up
        self.assertTrue(self.scene2.on_exit_called)
        self.assertTrue(self.scene2.cleanup_called)
        self.assertFalse(self.scene2.is_active())
        
        # Verify scene1 was resumed
        self.assertTrue(self.scene1.on_resume_called)
    
    def test_pop_empty_stack(self):
        """Test popping from an empty stack."""
        result = self.scene_manager.pop_scene()
        self.scene_manager.update(0.016)
        
        self.assertIsNone(result)
        self.assertEqual(self.scene_manager.get_scene_count(), 0)
    
    def test_change_scene(self):
        """Test changing the current scene."""
        # Push initial scene
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.update(0.016)
        
        # Change to new scene
        self.scene_manager.change_scene(self.scene2)
        self.scene_manager.update(0.016)
        
        # Verify scene was changed
        self.assertEqual(self.scene_manager.get_scene_count(), 1)
        self.assertEqual(self.scene_manager.get_current_scene(), self.scene2)
        
        # Verify old scene was cleaned up
        self.assertTrue(self.scene1.on_exit_called)
        self.assertTrue(self.scene1.cleanup_called)
        
        # Verify new scene is active
        self.assertTrue(self.scene2.on_enter_called)
        self.assertTrue(self.scene2.is_active())
    
    def test_clear_all_scenes(self):
        """Test clearing all scenes from the stack."""
        # Push multiple scenes
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.push_scene(self.scene2)
        self.scene_manager.push_scene(self.scene3)
        self.scene_manager.update(0.016)
        
        # Clear all scenes
        self.scene_manager.clear_all_scenes()
        self.scene_manager.update(0.016)
        
        # Verify all scenes were cleared
        self.assertEqual(self.scene_manager.get_scene_count(), 0)
        self.assertIsNone(self.scene_manager.get_current_scene())
        
        # Verify all scenes were cleaned up
        self.assertTrue(self.scene1.cleanup_called)
        self.assertTrue(self.scene2.cleanup_called)
        self.assertTrue(self.scene3.cleanup_called)
    
    def test_handle_event(self):
        """Test event handling."""
        # Push a scene
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.update(0.016)
        
        # Create mock event
        mock_event = Mock()
        
        # Handle event
        self.scene_manager.handle_event(mock_event)
        
        # Verify event was passed to current scene
        self.assertTrue(self.scene1.handle_event_called)
    
    def test_handle_event_no_scene(self):
        """Test event handling with no active scene."""
        mock_event = Mock()
        
        # This should not raise an exception
        self.scene_manager.handle_event(mock_event)
    
    def test_update(self):
        """Test scene manager update."""
        # Push a scene
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.update(0.016)
        
        # Update again
        self.scene_manager.update(0.016)
        
        # Verify scene was updated
        self.assertTrue(self.scene1.update_called)
    
    def test_render(self):
        """Test scene manager render."""
        # Push a scene
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.update(0.016)
        
        # Mock screen
        mock_screen = Mock()
        
        # Render
        self.scene_manager.render(mock_screen)
        
        # Verify scene was rendered
        self.assertTrue(self.scene1.render_called)
    
    def test_render_no_scene(self):
        """Test rendering with no active scene."""
        mock_screen = Mock()
        
        # This should not raise an exception
        self.scene_manager.render(mock_screen)
    
    def test_get_scene_names(self):
        """Test getting scene names."""
        # Push multiple scenes
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.push_scene(self.scene2)
        self.scene_manager.update(0.016)
        
        names = self.scene_manager.get_scene_names()
        self.assertEqual(names, ["TestScene1", "TestScene2"])
    
    def test_has_scenes(self):
        """Test checking if scenes exist."""
        # Initially no scenes
        self.assertFalse(self.scene_manager.has_scenes())
        
        # Push a scene
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.update(0.016)
        
        # Now has scenes
        self.assertTrue(self.scene_manager.has_scenes())
    
    def test_pending_operations_during_transition(self):
        """Test that operations are queued during transitions."""
        # Push a scene
        self.scene_manager.push_scene(self.scene1)
        
        # Set transitioning flag manually
        self.scene_manager.transitioning = True
        
        # Try to push another scene
        self.scene_manager.push_scene(self.scene2)
        
        # Operations should be queued
        self.assertEqual(len(self.scene_manager.pending_operations), 2)
        
        # Reset transitioning flag and update
        self.scene_manager.transitioning = False
        self.scene_manager.update(0.016)
        
        # Both operations should be processed
        self.assertEqual(self.scene_manager.get_scene_count(), 2)
    
    def test_cleanup(self):
        """Test scene manager cleanup."""
        # Push multiple scenes
        self.scene_manager.push_scene(self.scene1)
        self.scene_manager.push_scene(self.scene2)
        self.scene_manager.update(0.016)
        
        # Cleanup
        self.scene_manager.cleanup()
        
        # Verify all scenes were cleaned up
        self.assertEqual(self.scene_manager.get_scene_count(), 0)
        self.assertEqual(len(self.scene_manager.pending_operations), 0)
        self.assertTrue(self.scene1.cleanup_called)
        self.assertTrue(self.scene2.cleanup_called)


if __name__ == '__main__':
    unittest.main()