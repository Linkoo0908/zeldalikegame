"""
Unit tests for MapSystem class.
"""
import unittest
import json
import os
import sys
import tempfile

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from systems.map_system import MapSystem


class TestMapSystem(unittest.TestCase):
    """Test cases for MapSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.map_system = MapSystem()
        
        # Create a temporary test map
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
                ],
                "collision": [
                    [1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 1],
                    [1, 0, 1, 0, 1],
                    [1, 1, 1, 1, 1]
                ],
                "objects": [
                    {"type": "enemy", "x": 64, "y": 64, "enemy_type": "goblin"},
                    {"type": "item", "x": 96, "y": 64, "item_type": "potion"}
                ]
            }
        }
        
        # Create temporary file
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_map_data, self.temp_file)
        self.temp_file.close()
        
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_load_map_success(self):
        """Test successful map loading."""
        loaded_map = self.map_system.load_map(self.temp_file.name)
        
        self.assertEqual(loaded_map['width'], 5)
        self.assertEqual(loaded_map['height'], 4)
        self.assertEqual(loaded_map['tile_size'], 32)
        self.assertIn('background', loaded_map['layers'])
        self.assertIn('collision', loaded_map['layers'])
        
    def test_load_map_file_not_found(self):
        """Test loading non-existent map file."""
        with self.assertRaises(FileNotFoundError):
            self.map_system.load_map("nonexistent_map.json")
    
    def test_load_map_invalid_json(self):
        """Test loading invalid JSON file."""
        # Create invalid JSON file
        invalid_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        invalid_file.write("{ invalid json }")
        invalid_file.close()
        
        try:
            with self.assertRaises(ValueError):
                self.map_system.load_map(invalid_file.name)
        finally:
            os.unlink(invalid_file.name)
    
    def test_validate_map_data_missing_fields(self):
        """Test map validation with missing required fields."""
        invalid_map = {"width": 5, "height": 4}  # Missing tile_size and layers
        
        with self.assertRaises(ValueError):
            self.map_system._validate_map_data(invalid_map)
    
    def test_validate_map_data_missing_layers(self):
        """Test map validation with missing required layers."""
        invalid_map = {
            "width": 5,
            "height": 4,
            "tile_size": 32,
            "layers": {
                "background": [[1, 2, 3, 4, 5]]  # Missing collision layer
            }
        }
        
        with self.assertRaises(ValueError):
            self.map_system._validate_map_data(invalid_map)
    
    def test_validate_map_data_dimension_mismatch(self):
        """Test map validation with dimension mismatch."""
        invalid_map = {
            "width": 3,
            "height": 2,
            "tile_size": 32,
            "layers": {
                "background": [
                    [1, 2, 3, 4, 5],  # Width doesn't match
                    [1, 2, 3]
                ],
                "collision": [
                    [0, 0, 0],
                    [0, 0, 0]
                ]
            }
        }
        
        with self.assertRaises(ValueError):
            self.map_system._validate_map_data(invalid_map)
    
    def test_set_and_get_current_map(self):
        """Test setting and getting current map."""
        self.map_system.set_current_map(self.test_map_data)
        current_map = self.map_system.get_current_map()
        
        self.assertEqual(current_map, self.test_map_data)
    
    def test_get_tile_at(self):
        """Test getting tile at specific coordinates."""
        self.map_system.set_current_map(self.test_map_data)
        
        # Test valid coordinates
        self.assertEqual(self.map_system.get_tile_at(0, 0, 'background'), 1)
        self.assertEqual(self.map_system.get_tile_at(2, 2, 'background'), 3)
        self.assertEqual(self.map_system.get_tile_at(1, 1, 'collision'), 0)
        
        # Test out of bounds
        self.assertEqual(self.map_system.get_tile_at(-1, 0, 'background'), 0)
        self.assertEqual(self.map_system.get_tile_at(10, 10, 'background'), 0)
        
        # Test invalid layer
        self.assertEqual(self.map_system.get_tile_at(0, 0, 'invalid_layer'), 0)
    
    def test_is_tile_solid(self):
        """Test checking if tile is solid."""
        self.map_system.set_current_map(self.test_map_data)
        
        # Test solid tile
        self.assertTrue(self.map_system.is_tile_solid(0, 0))
        self.assertTrue(self.map_system.is_tile_solid(2, 2))
        
        # Test non-solid tile
        self.assertFalse(self.map_system.is_tile_solid(1, 1))
        self.assertFalse(self.map_system.is_tile_solid(3, 1))
        
        # Test out of bounds (should be solid)
        self.assertFalse(self.map_system.is_tile_solid(-1, 0))
    
    def test_world_to_tile_conversion(self):
        """Test world to tile coordinate conversion."""
        self.map_system.set_current_map(self.test_map_data)
        
        # Test conversion
        tile_x, tile_y = self.map_system.world_to_tile(64, 96)
        self.assertEqual(tile_x, 2)
        self.assertEqual(tile_y, 3)
        
        # Test edge case
        tile_x, tile_y = self.map_system.world_to_tile(31, 31)
        self.assertEqual(tile_x, 0)
        self.assertEqual(tile_y, 0)
    
    def test_tile_to_world_conversion(self):
        """Test tile to world coordinate conversion."""
        self.map_system.set_current_map(self.test_map_data)
        
        # Test conversion
        world_x, world_y = self.map_system.tile_to_world(2, 3)
        self.assertEqual(world_x, 64)
        self.assertEqual(world_y, 96)
        
        # Test origin
        world_x, world_y = self.map_system.tile_to_world(0, 0)
        self.assertEqual(world_x, 0)
        self.assertEqual(world_y, 0)
    
    def test_get_map_objects(self):
        """Test getting map objects."""
        self.map_system.set_current_map(self.test_map_data)
        
        objects = self.map_system.get_map_objects()
        self.assertEqual(len(objects), 2)
        
        # Check first object
        enemy = objects[0]
        self.assertEqual(enemy['type'], 'enemy')
        self.assertEqual(enemy['x'], 64)
        self.assertEqual(enemy['y'], 64)
        self.assertEqual(enemy['enemy_type'], 'goblin')
        
        # Check second object
        item = objects[1]
        self.assertEqual(item['type'], 'item')
        self.assertEqual(item['x'], 96)
        self.assertEqual(item['y'], 64)
        self.assertEqual(item['item_type'], 'potion')
    
    def test_get_map_size_pixels(self):
        """Test getting map size in pixels."""
        self.map_system.set_current_map(self.test_map_data)
        
        width, height = self.map_system.get_map_size_pixels()
        self.assertEqual(width, 5 * 32)  # 5 tiles * 32 pixels
        self.assertEqual(height, 4 * 32)  # 4 tiles * 32 pixels
    
    def test_map_caching(self):
        """Test that maps are cached after loading."""
        # Load map first time
        map1 = self.map_system.load_map(self.temp_file.name)
        
        # Load same map again
        map2 = self.map_system.load_map(self.temp_file.name)
        
        # Should be the same object (cached)
        self.assertIs(map1, map2)
        
        # Check cache
        self.assertIn(self.temp_file.name, self.map_system.maps_cache)


if __name__ == '__main__':
    unittest.main()