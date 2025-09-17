"""
Unit tests for MapRenderer class.
"""
import unittest
import pygame
from unittest.mock import Mock, MagicMock
from src.systems.map_renderer import MapRenderer
from src.systems.camera import Camera
from src.core.resource_manager import ResourceManager


class TestMapRenderer(unittest.TestCase):
    """Test cases for MapRenderer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        self.mock_resource_manager = Mock(spec=ResourceManager)
        self.map_renderer = MapRenderer(self.mock_resource_manager)
        self.camera = Camera(800, 600)
        
        # Test map data
        self.test_map_data = {
            "width": 5,
            "height": 4,
            "tile_size": 32,
            "layers": {
                "background": [
                    [1, 1, 1, 1, 1],
                    [1, 2, 2, 2, 1],
                    [1, 2, 3, 2, 1],
                    [1, 1, 1, 1, 1]
                ]
            }
        }
        
        # Create test screen
        self.screen = pygame.Surface((800, 600))
    
    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()
    
    def test_initialization(self):
        """Test map renderer initialization."""
        self.assertEqual(self.map_renderer.resource_manager, self.mock_resource_manager)
        self.assertEqual(self.map_renderer.default_tile_size, 32)
        self.assertEqual(len(self.map_renderer.tile_cache), 0)
    
    def test_get_visible_tile_range(self):
        """Test calculating visible tile range."""
        # Set camera position
        self.camera.set_position(32, 32)  # One tile offset
        
        visible_range = self.map_renderer._get_visible_tile_range(self.camera, self.test_map_data)
        
        self.assertIsNotNone(visible_range)
        start_x, start_y, end_x, end_y = visible_range
        
        # Should include tiles around the visible area
        self.assertGreaterEqual(start_x, 0)
        self.assertGreaterEqual(start_y, 0)
        self.assertLessEqual(end_x, 5)  # Map width
        self.assertLessEqual(end_y, 4)  # Map height
    
    def test_get_visible_tile_range_invalid_data(self):
        """Test visible tile range with invalid map data."""
        invalid_map = {"width": 0, "height": 0, "tile_size": 0}
        
        visible_range = self.map_renderer._get_visible_tile_range(self.camera, invalid_map)
        
        self.assertIsNone(visible_range)
    
    def test_generate_tile_surface(self):
        """Test generating tile surfaces."""
        tile_surface = self.map_renderer._generate_tile_surface(1, 32)
        
        self.assertIsInstance(tile_surface, pygame.Surface)
        self.assertEqual(tile_surface.get_width(), 32)
        self.assertEqual(tile_surface.get_height(), 32)
    
    def test_get_tile_surface_cached(self):
        """Test tile surface caching."""
        # First call should create and cache
        surface1 = self.map_renderer._get_tile_surface(1, 32)
        
        # Second call should return cached version
        surface2 = self.map_renderer._get_tile_surface(1, 32)
        
        self.assertIs(surface1, surface2)
        self.assertIn((1, 32), self.map_renderer.tile_cache)
    
    def test_get_tile_surface_with_resource_manager(self):
        """Test tile surface loading from resource manager."""
        # Mock successful image loading
        mock_surface = pygame.Surface((32, 32))
        self.mock_resource_manager.load_image.return_value = mock_surface
        
        surface = self.map_renderer._get_tile_surface(1, 32)
        
        self.assertIs(surface, mock_surface)
        self.mock_resource_manager.load_image.assert_called_with("tiles/tile_1.png")
    
    def test_get_tile_surface_with_scaling(self):
        """Test tile surface scaling when size doesn't match."""
        # Mock image with different size
        mock_surface = pygame.Surface((64, 64))  # Different from requested 32x32
        self.mock_resource_manager.load_image.return_value = mock_surface
        
        surface = self.map_renderer._get_tile_surface(1, 32)
        
        self.assertEqual(surface.get_width(), 32)
        self.assertEqual(surface.get_height(), 32)
    
    def test_get_tile_surface_fallback_to_generated(self):
        """Test fallback to generated tile when resource loading fails."""
        # Mock failed image loading
        self.mock_resource_manager.load_image.side_effect = Exception("File not found")
        
        surface = self.map_renderer._get_tile_surface(1, 32)
        
        self.assertIsInstance(surface, pygame.Surface)
        self.assertEqual(surface.get_width(), 32)
        self.assertEqual(surface.get_height(), 32)
    
    def test_render_map_empty_data(self):
        """Test rendering with empty map data."""
        # Should not crash with empty data
        self.map_renderer.render_map(self.screen, {}, self.camera)
        self.map_renderer.render_map(self.screen, None, self.camera)
        
        # Should not crash with missing layer
        map_data = {"layers": {}}
        self.map_renderer.render_map(self.screen, map_data, self.camera, "nonexistent")
    
    def test_render_map_basic(self):
        """Test basic map rendering."""
        # Mock resource manager to return None (use generated tiles)
        self.mock_resource_manager.load_image.side_effect = Exception("No image")
        
        # Should not crash
        self.map_renderer.render_map(self.screen, self.test_map_data, self.camera)
        
        # Should have cached some tiles
        self.assertGreater(len(self.map_renderer.tile_cache), 0)
    
    def test_clear_tile_cache(self):
        """Test clearing tile cache."""
        # Add something to cache
        self.map_renderer._get_tile_surface(1, 32)
        self.assertGreater(len(self.map_renderer.tile_cache), 0)
        
        # Clear cache
        self.map_renderer.clear_tile_cache()
        self.assertEqual(len(self.map_renderer.tile_cache), 0)
    
    def test_preload_tiles(self):
        """Test preloading tiles."""
        tile_ids = [1, 2, 3]
        
        self.map_renderer.preload_tiles(tile_ids, 32)
        
        # Should have cached all requested tiles
        for tile_id in tile_ids:
            self.assertIn((tile_id, 32), self.map_renderer.tile_cache)


if __name__ == '__main__':
    unittest.main()