"""
Unit tests for ResourceManager class.
Tests image loading, caching, error handling, and resource management functionality.
"""
import unittest
import pygame
import json
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add src to path for imports
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from core.resource_manager import ResourceManager, ResourceLoadError


class TestResourceManager(unittest.TestCase):
    """Test cases for ResourceManager class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Initialize pygame for testing
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        # Create temporary directory for test assets
        self.temp_dir = tempfile.mkdtemp()
        self.assets_path = Path(self.temp_dir)
        
        # Create asset subdirectories
        (self.assets_path / "images").mkdir(exist_ok=True)
        (self.assets_path / "sounds").mkdir(exist_ok=True)
        (self.assets_path / "maps").mkdir(exist_ok=True)
        
        # Create ResourceManager instance
        self.resource_manager = ResourceManager(str(self.assets_path))
    
    def tearDown(self):
        """Clean up after each test method."""
        # Clean up temporary directory
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
        pygame.quit()
    
    def create_test_image(self, filename: str, size: tuple = (32, 32)) -> Path:
        """Create a test image file."""
        image_path = self.assets_path / "images" / filename
        surface = pygame.Surface(size)
        surface.fill((255, 0, 0))  # Red color
        pygame.image.save(surface, str(image_path))
        return image_path
    
    def create_test_map(self, filename: str, width: int = 5, height: int = 5) -> Path:
        """Create a test map JSON file."""
        map_path = self.assets_path / "maps" / filename
        map_data = {
            "width": width,
            "height": height,
            "tile_size": 32,
            "layers": {
                "background": [[0 for _ in range(width)] for _ in range(height)],
                "collision": [[0 for _ in range(width)] for _ in range(height)],
                "objects": []
            }
        }
        with open(map_path, 'w') as f:
            json.dump(map_data, f)
        return map_path
    
    def test_initialization(self):
        """Test ResourceManager initialization."""
        self.assertIsInstance(self.resource_manager.image_cache, dict)
        self.assertIsInstance(self.resource_manager.sound_cache, dict)
        self.assertIsInstance(self.resource_manager.map_cache, dict)
        
        # Check default image exists
        self.assertIn("__default__", self.resource_manager.image_cache)
        default_img = self.resource_manager.image_cache["__default__"]
        self.assertIsInstance(default_img, pygame.Surface)
        self.assertEqual(default_img.get_size(), (32, 32))
    
    def test_load_image_success(self):
        """Test successful image loading."""
        # Create test image
        test_image_path = self.create_test_image("test.png")
        
        # Load image
        loaded_image = self.resource_manager.load_image("test.png")
        
        # Verify image loaded correctly
        self.assertIsInstance(loaded_image, pygame.Surface)
        self.assertEqual(loaded_image.get_size(), (32, 32))
        
        # Verify image is cached
        self.assertIn("test.png", self.resource_manager.image_cache)
    
    def test_load_image_with_colorkey(self):
        """Test image loading with colorkey transparency."""
        # Create test image
        self.create_test_image("test_colorkey.png")
        
        # Load image with colorkey
        loaded_image = self.resource_manager.load_image("test_colorkey.png", colorkey=(255, 0, 255))
        
        # Verify image loaded
        self.assertIsInstance(loaded_image, pygame.Surface)
        
        # Verify cached with colorkey
        cache_key = "test_colorkey.png_(255, 0, 255)"
        self.assertIn(cache_key, self.resource_manager.image_cache)
    
    def test_load_image_file_not_found(self):
        """Test image loading when file doesn't exist."""
        # Try to load non-existent image
        loaded_image = self.resource_manager.load_image("nonexistent.png")
        
        # Should return default image
        self.assertEqual(loaded_image, self.resource_manager.default_image)
        
        # Should be cached
        self.assertIn("nonexistent.png", self.resource_manager.image_cache)
    
    def test_load_image_caching(self):
        """Test that images are properly cached."""
        # Create test image
        self.create_test_image("cached_test.png")
        
        # Load image twice
        image1 = self.resource_manager.load_image("cached_test.png")
        image2 = self.resource_manager.load_image("cached_test.png")
        
        # Should be the same object (cached)
        self.assertIs(image1, image2)
    
    def test_load_map_success(self):
        """Test successful map loading."""
        # Create test map
        self.create_test_map("test_map.json", 10, 8)
        
        # Load map
        loaded_map = self.resource_manager.load_map("test_map.json")
        
        # Verify map data
        self.assertIsInstance(loaded_map, dict)
        self.assertEqual(loaded_map["width"], 10)
        self.assertEqual(loaded_map["height"], 8)
        self.assertEqual(loaded_map["tile_size"], 32)
        self.assertIn("layers", loaded_map)
        
        # Verify map is cached
        self.assertIn("test_map.json", self.resource_manager.map_cache)
    
    def test_load_map_file_not_found(self):
        """Test map loading when file doesn't exist."""
        # Try to load non-existent map
        loaded_map = self.resource_manager.load_map("nonexistent.json")
        
        # Should return default map
        self.assertIsInstance(loaded_map, dict)
        self.assertEqual(loaded_map["width"], 10)
        self.assertEqual(loaded_map["height"], 10)
        self.assertIn("layers", loaded_map)
        
        # Should be cached
        self.assertIn("nonexistent.json", self.resource_manager.map_cache)
    
    def test_load_map_invalid_json(self):
        """Test map loading with invalid JSON."""
        # Create invalid JSON file
        invalid_map_path = self.assets_path / "maps" / "invalid.json"
        with open(invalid_map_path, 'w') as f:
            f.write("{ invalid json }")
        
        # Try to load invalid map
        loaded_map = self.resource_manager.load_map("invalid.json")
        
        # Should return default map
        self.assertIsInstance(loaded_map, dict)
        self.assertEqual(loaded_map["width"], 10)
        self.assertEqual(loaded_map["height"], 10)
    
    def test_load_sound_file_not_found(self):
        """Test sound loading when file doesn't exist."""
        # Try to load non-existent sound
        loaded_sound = self.resource_manager.load_sound("nonexistent.wav")
        
        # Should return None
        self.assertIsNone(loaded_sound)
        
        # Should be cached as None
        self.assertIn("nonexistent.wav", self.resource_manager.sound_cache)
        self.assertIsNone(self.resource_manager.sound_cache["nonexistent.wav"])
    
    def test_get_resource_image(self):
        """Test generic resource getter for images."""
        self.create_test_image("generic_test.png")
        
        # Get image resource
        image = self.resource_manager.get_resource("image", "generic_test.png")
        
        self.assertIsInstance(image, pygame.Surface)
    
    def test_get_resource_map(self):
        """Test generic resource getter for maps."""
        self.create_test_map("generic_test.json")
        
        # Get map resource
        map_data = self.resource_manager.get_resource("map", "generic_test.json")
        
        self.assertIsInstance(map_data, dict)
        self.assertIn("width", map_data)
    
    def test_get_resource_invalid_type(self):
        """Test generic resource getter with invalid type."""
        with self.assertRaises(ValueError):
            self.resource_manager.get_resource("invalid_type", "test.file")
    
    def test_preload_resources(self):
        """Test preloading multiple resources."""
        # Create test resources
        self.create_test_image("preload1.png")
        self.create_test_image("preload2.png")
        self.create_test_map("preload_map.json")
        
        # Define resources to preload
        resources = [
            {"type": "image", "path": "preload1.png"},
            {"type": "image", "path": "preload2.png"},
            {"type": "map", "path": "preload_map.json"},
            {"type": "image", "path": "nonexistent.png"}  # This should fail gracefully
        ]
        
        # Preload resources
        self.resource_manager.preload_resources(resources)
        
        # Verify resources are cached
        self.assertIn("preload1.png", self.resource_manager.image_cache)
        self.assertIn("preload2.png", self.resource_manager.image_cache)
        self.assertIn("preload_map.json", self.resource_manager.map_cache)
        self.assertIn("nonexistent.png", self.resource_manager.image_cache)
    
    def test_clear_cache(self):
        """Test cache clearing functionality."""
        # Load some resources
        self.create_test_image("cache_test.png")
        self.create_test_map("cache_test.json")
        
        self.resource_manager.load_image("cache_test.png")
        self.resource_manager.load_map("cache_test.json")
        
        # Verify resources are cached
        self.assertIn("cache_test.png", self.resource_manager.image_cache)
        self.assertIn("cache_test.json", self.resource_manager.map_cache)
        
        # Clear image cache
        self.resource_manager.clear_cache("image")
        
        # Image cache should be cleared (except default)
        self.assertNotIn("cache_test.png", self.resource_manager.image_cache)
        self.assertIn("__default__", self.resource_manager.image_cache)  # Default should remain
        
        # Map cache should still have data
        self.assertIn("cache_test.json", self.resource_manager.map_cache)
        
        # Clear all caches
        self.resource_manager.clear_cache()
        
        # All caches should be cleared (except default image)
        self.assertNotIn("cache_test.json", self.resource_manager.map_cache)
        self.assertIn("__default__", self.resource_manager.image_cache)
    
    def test_get_cache_info(self):
        """Test cache information retrieval."""
        # Initially should have just default image
        cache_info = self.resource_manager.get_cache_info()
        self.assertEqual(cache_info["images"], 1)  # Default image
        self.assertEqual(cache_info["sounds"], 0)
        self.assertEqual(cache_info["maps"], 0)
        
        # Load some resources
        self.create_test_image("info_test.png")
        self.create_test_map("info_test.json")
        
        self.resource_manager.load_image("info_test.png")
        self.resource_manager.load_map("info_test.json")
        
        # Check updated cache info
        cache_info = self.resource_manager.get_cache_info()
        self.assertEqual(cache_info["images"], 2)  # Default + loaded image
        self.assertEqual(cache_info["sounds"], 0)
        self.assertEqual(cache_info["maps"], 1)


if __name__ == '__main__':
    unittest.main()