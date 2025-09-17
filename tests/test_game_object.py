"""
Unit tests for GameObject base class.
"""
import unittest
import pygame
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from objects.game_object import GameObject


class TestGameObject(unittest.TestCase):
    """Test cases for GameObject class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize pygame for testing (required for Surface operations)
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        self.game_object = GameObject(100, 200, 32, 48)
    
    def tearDown(self):
        """Clean up after each test method."""
        pygame.quit()
    
    def test_initialization(self):
        """Test GameObject initialization."""
        obj = GameObject(10, 20, 30, 40)
        
        self.assertEqual(obj.x, 10)
        self.assertEqual(obj.y, 20)
        self.assertEqual(obj.width, 30)
        self.assertEqual(obj.height, 40)
        self.assertIsNone(obj.sprite)
        self.assertTrue(obj.active)
    
    def test_default_size(self):
        """Test GameObject with default size."""
        obj = GameObject(5, 15)
        
        self.assertEqual(obj.x, 5)
        self.assertEqual(obj.y, 15)
        self.assertEqual(obj.width, 32)
        self.assertEqual(obj.height, 32)
    
    def test_get_bounds(self):
        """Test get_bounds method."""
        bounds = self.game_object.get_bounds()
        
        self.assertIsInstance(bounds, pygame.Rect)
        self.assertEqual(bounds.x, 100)
        self.assertEqual(bounds.y, 200)
        self.assertEqual(bounds.width, 32)
        self.assertEqual(bounds.height, 48)
    
    def test_get_position(self):
        """Test get_position method."""
        pos = self.game_object.get_position()
        
        self.assertEqual(pos, (100, 200))
    
    def test_set_position(self):
        """Test set_position method."""
        self.game_object.set_position(50, 75)
        
        self.assertEqual(self.game_object.x, 50)
        self.assertEqual(self.game_object.y, 75)
        self.assertEqual(self.game_object.get_position(), (50, 75))
    
    def test_get_center(self):
        """Test get_center method."""
        center = self.game_object.get_center()
        
        # Center should be position + half width/height
        expected_x = 100 + 32 / 2
        expected_y = 200 + 48 / 2
        self.assertEqual(center, (expected_x, expected_y))
    
    def test_set_sprite(self):
        """Test set_sprite method."""
        # Create a test sprite
        test_sprite = pygame.Surface((64, 64))
        test_sprite.fill((255, 0, 0))  # Red color
        
        self.game_object.set_sprite(test_sprite)
        
        self.assertEqual(self.game_object.sprite, test_sprite)
        # Size should update to match sprite
        self.assertEqual(self.game_object.width, 64)
        self.assertEqual(self.game_object.height, 64)
    
    def test_destroy(self):
        """Test destroy method."""
        self.assertTrue(self.game_object.is_active())
        
        self.game_object.destroy()
        
        self.assertFalse(self.game_object.is_active())
        self.assertFalse(self.game_object.active)
    
    def test_update_method_exists(self):
        """Test that update method exists and can be called."""
        # Should not raise an exception
        self.game_object.update(0.016)  # ~60 FPS delta time
    
    def test_render_without_sprite(self):
        """Test render method when no sprite is set."""
        screen = pygame.Surface((800, 600))
        
        # Should not raise an exception even without sprite
        self.game_object.render(screen, 0, 0)
    
    def test_render_with_sprite(self):
        """Test render method with sprite."""
        screen = pygame.Surface((800, 600))
        test_sprite = pygame.Surface((32, 32))
        test_sprite.fill((0, 255, 0))  # Green color
        
        self.game_object.set_sprite(test_sprite)
        
        # Should not raise an exception
        self.game_object.render(screen, 0, 0)
    
    def test_render_with_camera_offset(self):
        """Test render method with camera offset."""
        screen = pygame.Surface((800, 600))
        test_sprite = pygame.Surface((32, 32))
        self.game_object.set_sprite(test_sprite)
        
        # Should not raise an exception with camera offset
        self.game_object.render(screen, 50, 100)
    
    def test_render_inactive_object(self):
        """Test that inactive objects don't render."""
        screen = pygame.Surface((800, 600))
        test_sprite = pygame.Surface((32, 32))
        self.game_object.set_sprite(test_sprite)
        
        self.game_object.destroy()  # Make inactive
        
        # Should not render when inactive
        self.game_object.render(screen, 0, 0)


if __name__ == '__main__':
    unittest.main()