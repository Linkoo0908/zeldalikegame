"""
Unit tests for CollisionSystem class.
"""
import unittest
import pygame
from unittest.mock import Mock, MagicMock
from src.systems.collision_system import CollisionSystem
from src.systems.map_system import MapSystem
from src.objects.game_object import GameObject


class TestCollisionSystem(unittest.TestCase):
    """Test cases for CollisionSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        # Create mock map system
        self.mock_map_system = Mock(spec=MapSystem)
        self.collision_system = CollisionSystem(self.mock_map_system)
        
        # Create test game objects
        self.obj1 = GameObject(10, 10)
        self.obj1.width = 20
        self.obj1.height = 20
        
        self.obj2 = GameObject(25, 25)
        self.obj2.width = 20
        self.obj2.height = 20
        
        self.obj3 = GameObject(100, 100)
        self.obj3.width = 20
        self.obj3.height = 20
    
    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()
    
    def test_initialization(self):
        """Test collision system initialization."""
        self.assertEqual(self.collision_system.map_system, self.mock_map_system)
    
    def test_check_aabb_collision_overlapping(self):
        """Test AABB collision detection with overlapping objects."""
        # obj1 (10,10,20,20) and obj2 (25,25,20,20) should overlap
        result = self.collision_system.check_aabb_collision(self.obj1, self.obj2)
        self.assertTrue(result)
    
    def test_check_aabb_collision_non_overlapping(self):
        """Test AABB collision detection with non-overlapping objects."""
        # obj1 (10,10,20,20) and obj3 (100,100,20,20) should not overlap
        result = self.collision_system.check_aabb_collision(self.obj1, self.obj3)
        self.assertFalse(result)
    
    def test_check_aabb_collision_touching(self):
        """Test AABB collision detection with touching objects."""
        # Create objects that just touch
        touching_obj = GameObject(30, 10)  # Right next to obj1
        touching_obj.width = 20
        touching_obj.height = 20
        
        result = self.collision_system.check_aabb_collision(self.obj1, touching_obj)
        self.assertFalse(result)  # Just touching should not be collision
    
    def test_check_point_collision_inside(self):
        """Test point collision when point is inside object."""
        # Point (15, 15) should be inside obj1 (10,10,20,20)
        result = self.collision_system.check_point_collision(15, 15, self.obj1)
        self.assertTrue(result)
    
    def test_check_point_collision_outside(self):
        """Test point collision when point is outside object."""
        # Point (50, 50) should be outside obj1 (10,10,20,20)
        result = self.collision_system.check_point_collision(50, 50, self.obj1)
        self.assertFalse(result)
    
    def test_check_point_collision_on_edge(self):
        """Test point collision when point is on object edge."""
        # Point on edge should be considered inside
        result = self.collision_system.check_point_collision(10, 10, self.obj1)
        self.assertTrue(result)
        
        result = self.collision_system.check_point_collision(30, 30, self.obj1)
        self.assertTrue(result)
    
    def test_check_map_collision_no_map(self):
        """Test map collision when no map is loaded."""
        self.mock_map_system.get_current_map.return_value = None
        
        result = self.collision_system.check_map_collision(self.obj1, 50, 50)
        self.assertFalse(result)
    
    def test_check_map_collision_solid_tile(self):
        """Test map collision with solid tiles."""
        # Mock map system responses
        self.mock_map_system.get_current_map.return_value = {"some": "data"}
        self.mock_map_system.world_to_tile.return_value = (1, 1)
        self.mock_map_system.is_tile_solid.return_value = True
        
        result = self.collision_system.check_map_collision(self.obj1, 32, 32)
        self.assertTrue(result)
    
    def test_check_map_collision_non_solid_tile(self):
        """Test map collision with non-solid tiles."""
        # Mock map system responses
        self.mock_map_system.get_current_map.return_value = {"some": "data"}
        self.mock_map_system.world_to_tile.return_value = (1, 1)
        self.mock_map_system.is_tile_solid.return_value = False
        
        result = self.collision_system.check_map_collision(self.obj1, 32, 32)
        self.assertFalse(result)
    
    def test_resolve_map_collision_both_valid(self):
        """Test map collision resolution when both X and Y movements are valid."""
        # Mock no collision
        self.mock_map_system.get_current_map.return_value = {"some": "data"}
        self.collision_system.check_map_collision = Mock(return_value=False)
        
        resolved_x, resolved_y = self.collision_system.resolve_map_collision(
            self.obj1, 10, 10, 50, 50)
        
        self.assertEqual(resolved_x, 50)
        self.assertEqual(resolved_y, 50)
    
    def test_resolve_map_collision_x_only_valid(self):
        """Test map collision resolution when only X movement is valid."""
        def mock_collision(obj, x, y):
            # Collision occurs when Y changes
            return y != 10
        
        self.mock_map_system.get_current_map.return_value = {"some": "data"}
        self.collision_system.check_map_collision = mock_collision
        
        resolved_x, resolved_y = self.collision_system.resolve_map_collision(
            self.obj1, 10, 10, 50, 50)
        
        self.assertEqual(resolved_x, 50)
        self.assertEqual(resolved_y, 10)  # Y should stay at old position
    
    def test_resolve_map_collision_y_only_valid(self):
        """Test map collision resolution when only Y movement is valid."""
        def mock_collision(obj, x, y):
            # Collision occurs when X changes
            return x != 10
        
        self.mock_map_system.get_current_map.return_value = {"some": "data"}
        self.collision_system.check_map_collision = mock_collision
        
        resolved_x, resolved_y = self.collision_system.resolve_map_collision(
            self.obj1, 10, 10, 50, 50)
        
        self.assertEqual(resolved_x, 10)  # X should stay at old position
        self.assertEqual(resolved_y, 50)
    
    def test_resolve_map_collision_no_movement_valid(self):
        """Test map collision resolution when no movement is valid."""
        # Mock collision for any movement
        self.mock_map_system.get_current_map.return_value = {"some": "data"}
        self.collision_system.check_map_collision = Mock(return_value=True)
        
        resolved_x, resolved_y = self.collision_system.resolve_map_collision(
            self.obj1, 10, 10, 50, 50)
        
        self.assertEqual(resolved_x, 10)  # Should stay at old position
        self.assertEqual(resolved_y, 10)
    
    def test_get_collision_objects(self):
        """Test getting colliding objects."""
        objects = [self.obj1, self.obj2, self.obj3]
        
        # obj1 and obj2 should collide, obj3 should not
        colliding = self.collision_system.get_collision_objects(self.obj1, objects)
        
        self.assertEqual(len(colliding), 1)
        self.assertIn(self.obj2, colliding)
        self.assertNotIn(self.obj3, colliding)
        self.assertNotIn(self.obj1, colliding)  # Should not include self
    
    def test_separate_objects_horizontal(self):
        """Test separating objects horizontally."""
        # Position objects so they overlap horizontally more than vertically
        self.obj1.x = 10
        self.obj1.y = 10
        self.obj2.x = 20  # Overlapping horizontally
        self.obj2.y = 10  # Same Y position
        
        original_x1, original_x2 = self.obj1.x, self.obj2.x
        
        self.collision_system.separate_objects(self.obj1, self.obj2)
        
        # Objects should be separated horizontally
        self.assertNotEqual(self.obj1.x, original_x1)
        self.assertNotEqual(self.obj2.x, original_x2)
        self.assertLess(self.obj1.x, self.obj2.x)  # obj1 should be to the left
    
    def test_separate_objects_vertical(self):
        """Test separating objects vertically."""
        # Position objects so they overlap vertically more than horizontally
        self.obj1.x = 10
        self.obj1.y = 10
        self.obj2.x = 10  # Same X position
        self.obj2.y = 20  # Overlapping vertically
        
        original_y1, original_y2 = self.obj1.y, self.obj2.y
        
        self.collision_system.separate_objects(self.obj1, self.obj2)
        
        # Objects should be separated vertically
        self.assertNotEqual(self.obj1.y, original_y1)
        self.assertNotEqual(self.obj2.y, original_y2)
        self.assertLess(self.obj1.y, self.obj2.y)  # obj1 should be above
    
    def test_get_collision_direction_right(self):
        """Test collision direction detection - right collision."""
        # obj1 hits obj2 from the left
        self.obj1.x = 10
        self.obj1.y = 10
        self.obj2.x = 20
        self.obj2.y = 10
        
        direction = self.collision_system.get_collision_direction(self.obj1, self.obj2)
        self.assertEqual(direction, 'right')
    
    def test_get_collision_direction_left(self):
        """Test collision direction detection - left collision."""
        # obj1 hits obj2 from the right
        self.obj1.x = 30
        self.obj1.y = 10
        self.obj2.x = 20
        self.obj2.y = 10
        
        direction = self.collision_system.get_collision_direction(self.obj1, self.obj2)
        self.assertEqual(direction, 'left')
    
    def test_get_collision_direction_bottom(self):
        """Test collision direction detection - bottom collision."""
        # obj1 hits obj2 from above
        self.obj1.x = 10
        self.obj1.y = 10
        self.obj2.x = 10
        self.obj2.y = 20
        
        direction = self.collision_system.get_collision_direction(self.obj1, self.obj2)
        self.assertEqual(direction, 'bottom')
    
    def test_get_collision_direction_top(self):
        """Test collision direction detection - top collision."""
        # obj1 hits obj2 from below
        self.obj1.x = 10
        self.obj1.y = 30
        self.obj2.x = 10
        self.obj2.y = 20
        
        direction = self.collision_system.get_collision_direction(self.obj1, self.obj2)
        self.assertEqual(direction, 'top')
    
    def test_check_circle_collision_overlapping(self):
        """Test circle collision detection with overlapping circles."""
        result = self.collision_system.check_circle_collision(0, 0, 10, 5, 5, 10)
        self.assertTrue(result)
    
    def test_check_circle_collision_non_overlapping(self):
        """Test circle collision detection with non-overlapping circles."""
        result = self.collision_system.check_circle_collision(0, 0, 5, 20, 20, 5)
        self.assertFalse(result)
    
    def test_check_circle_collision_touching(self):
        """Test circle collision detection with touching circles."""
        result = self.collision_system.check_circle_collision(0, 0, 5, 10, 0, 5)
        self.assertTrue(result)  # Touching circles should collide
    
    def test_get_nearest_non_colliding_position_valid_target(self):
        """Test finding nearest position when target is already valid."""
        # Mock no collision at target
        self.collision_system.check_map_collision = Mock(return_value=False)
        
        result_x, result_y = self.collision_system.get_nearest_non_colliding_position(
            self.obj1, 50, 50)
        
        self.assertEqual(result_x, 50)
        self.assertEqual(result_y, 50)
    
    def test_get_nearest_non_colliding_position_search_needed(self):
        """Test finding nearest position when search is needed."""
        call_count = 0
        
        def mock_collision(obj, x, y):
            nonlocal call_count
            call_count += 1
            # First call (target position) has collision, second call doesn't
            return call_count == 1
        
        self.collision_system.check_map_collision = mock_collision
        
        result_x, result_y = self.collision_system.get_nearest_non_colliding_position(
            self.obj1, 50, 50)
        
        # Should find a different position than the target
        self.assertTrue(result_x != 50 or result_y != 50)


if __name__ == '__main__':
    unittest.main()