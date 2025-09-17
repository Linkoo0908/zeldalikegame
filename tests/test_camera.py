"""
Unit tests for Camera class.
"""
import unittest
from src.systems.camera import Camera


class TestCamera(unittest.TestCase):
    """Test cases for Camera class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.camera = Camera(800, 600)
    
    def test_initialization(self):
        """Test camera initialization."""
        self.assertEqual(self.camera.screen_width, 800)
        self.assertEqual(self.camera.screen_height, 600)
        self.assertEqual(self.camera.x, 0.0)
        self.assertEqual(self.camera.y, 0.0)
        self.assertEqual(self.camera.target_x, 0.0)
        self.assertEqual(self.camera.target_y, 0.0)
    
    def test_set_position(self):
        """Test setting camera position directly."""
        self.camera.set_position(100, 200)
        
        self.assertEqual(self.camera.x, 100)
        self.assertEqual(self.camera.y, 200)
        self.assertEqual(self.camera.target_x, 100)
        self.assertEqual(self.camera.target_y, 200)
    
    def test_set_target(self):
        """Test setting camera target."""
        self.camera.set_target(150, 250)
        
        self.assertEqual(self.camera.target_x, 150)
        self.assertEqual(self.camera.target_y, 250)
        # Position should not change immediately
        self.assertEqual(self.camera.x, 0.0)
        self.assertEqual(self.camera.y, 0.0)
    
    def test_follow_target(self):
        """Test camera following a target."""
        # Set initial position
        self.camera.set_position(0, 0)
        
        # Follow target at (400, 300) - should center camera
        self.camera.follow_target(400, 300, 1.0)
        
        # Camera should be centered on target
        expected_x = 400 - 800 // 2  # 400 - 400 = 0
        expected_y = 300 - 600 // 2  # 300 - 300 = 0
        
        self.assertAlmostEqual(self.camera.x, expected_x, places=1)
        self.assertAlmostEqual(self.camera.y, expected_y, places=1)
    
    def test_world_to_screen_conversion(self):
        """Test world to screen coordinate conversion."""
        self.camera.set_position(100, 50)
        
        screen_x, screen_y = self.camera.world_to_screen(200, 150)
        
        self.assertEqual(screen_x, 100)  # 200 - 100
        self.assertEqual(screen_y, 100)  # 150 - 50
    
    def test_screen_to_world_conversion(self):
        """Test screen to world coordinate conversion."""
        self.camera.set_position(100, 50)
        
        world_x, world_y = self.camera.screen_to_world(100, 100)
        
        self.assertEqual(world_x, 200)  # 100 + 100
        self.assertEqual(world_y, 150)  # 100 + 50
    
    def test_get_visible_area(self):
        """Test getting visible area."""
        self.camera.set_position(100, 50)
        
        left, top, right, bottom = self.camera.get_visible_area()
        
        self.assertEqual(left, 100)
        self.assertEqual(top, 50)
        self.assertEqual(right, 900)   # 100 + 800
        self.assertEqual(bottom, 650)  # 50 + 600
    
    def test_is_visible(self):
        """Test visibility checking."""
        self.camera.set_position(100, 50)
        
        # Object completely inside view
        self.assertTrue(self.camera.is_visible(200, 100, 50, 50))
        
        # Object completely outside view (left)
        self.assertFalse(self.camera.is_visible(0, 100, 50, 50))
        
        # Object completely outside view (right)
        self.assertFalse(self.camera.is_visible(1000, 100, 50, 50))
        
        # Object partially visible
        self.assertTrue(self.camera.is_visible(80, 100, 50, 50))
    
    def test_bounds_constraint(self):
        """Test camera bounds constraints."""
        # Set bounds: camera can move from (0,0) to (1000,800)
        self.camera.set_bounds(0, 0, 1000, 800)
        
        # Try to move beyond bounds
        self.camera.set_position(-100, -50)
        
        # Should be constrained to bounds
        self.assertEqual(self.camera.x, 0)
        self.assertEqual(self.camera.y, 0)
        
        # Try to move beyond right/bottom bounds
        self.camera.set_position(1500, 1000)
        
        # Should be constrained (max_x - screen_width, max_y - screen_height)
        self.assertEqual(self.camera.x, 200)  # 1000 - 800
        self.assertEqual(self.camera.y, 200)  # 800 - 600
    
    def test_get_offset(self):
        """Test getting camera offset as integers."""
        self.camera.set_position(123.7, 456.9)
        
        offset_x, offset_y = self.camera.get_offset()
        
        self.assertEqual(offset_x, 123)
        self.assertEqual(offset_y, 456)


if __name__ == '__main__':
    unittest.main()