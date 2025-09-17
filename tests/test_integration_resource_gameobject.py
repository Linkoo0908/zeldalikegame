"""
Integration test for ResourceManager with GameObject.
Tests that ResourceManager can load sprites for GameObjects.
"""
import unittest
import pygame
import tempfile
import os
from pathlib import Path

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.resource_manager import ResourceManager
from objects.game_object import GameObject


class TestResourceManagerGameObjectIntegration(unittest.TestCase):
    """Integration tests for ResourceManager and GameObject."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize pygame
        pygame.init()
        pygame.display.set_mode((1, 1))
        
        # Create temporary directory for test assets
        self.temp_dir = tempfile.mkdtemp()
        self.assets_path = Path(self.temp_dir)
        (self.assets_path / "images").mkdir(exist_ok=True)
        
        # Create ResourceManager
        self.resource_manager = ResourceManager(str(self.assets_path))
    
    def tearDown(self):
        """Clean up after tests."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        pygame.quit()
    
    def create_test_sprite(self, filename: str, size: tuple = (64, 64)) -> Path:
        """Create a test sprite image."""
        image_path = self.assets_path / "images" / filename
        surface = pygame.Surface(size)
        surface.fill((0, 255, 0))  # Green color
        pygame.image.save(surface, str(image_path))
        return image_path
    
    def test_gameobject_with_loaded_sprite(self):
        """Test that GameObject can use sprites loaded by ResourceManager."""
        # Create test sprite
        self.create_test_sprite("player.png", (32, 32))
        
        # Load sprite using ResourceManager
        sprite = self.resource_manager.load_image("player.png")
        
        # Create GameObject and set sprite
        game_object = GameObject(100, 200)
        game_object.set_sprite(sprite)
        
        # Verify sprite is set correctly
        self.assertIsNotNone(game_object.sprite)
        self.assertEqual(game_object.sprite.get_size(), (32, 32))
        self.assertEqual(game_object.width, 32)
        self.assertEqual(game_object.height, 32)
    
    def test_gameobject_with_default_sprite(self):
        """Test that GameObject can use default sprite when file not found."""
        # Try to load non-existent sprite
        sprite = self.resource_manager.load_image("nonexistent_player.png")
        
        # Create GameObject and set sprite
        game_object = GameObject(50, 75)
        game_object.set_sprite(sprite)
        
        # Should have default sprite
        self.assertIsNotNone(game_object.sprite)
        self.assertEqual(game_object.sprite.get_size(), (32, 32))
        self.assertEqual(game_object.width, 32)
        self.assertEqual(game_object.height, 32)
        
        # Should be the default magenta sprite
        self.assertEqual(game_object.sprite, self.resource_manager.default_image)
    
    def test_multiple_gameobjects_same_sprite(self):
        """Test that multiple GameObjects can share the same cached sprite."""
        # Create test sprite
        self.create_test_sprite("shared_sprite.png", (48, 48))
        
        # Load sprite (will be cached)
        sprite = self.resource_manager.load_image("shared_sprite.png")
        
        # Create multiple GameObjects with same sprite
        obj1 = GameObject(0, 0)
        obj2 = GameObject(100, 100)
        obj3 = GameObject(200, 200)
        
        obj1.set_sprite(sprite)
        obj2.set_sprite(sprite)
        obj3.set_sprite(sprite)
        
        # All should have the same sprite object (cached)
        self.assertIs(obj1.sprite, obj2.sprite)
        self.assertIs(obj2.sprite, obj3.sprite)
        self.assertIs(obj1.sprite, sprite)
        
        # All should have correct dimensions
        for obj in [obj1, obj2, obj3]:
            self.assertEqual(obj.width, 48)
            self.assertEqual(obj.height, 48)


if __name__ == '__main__':
    unittest.main()