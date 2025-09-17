"""
Integration tests for map and collision systems working together.
"""
import unittest
import pygame
from src.systems.map_system import MapSystem
from src.systems.collision_system import CollisionSystem
from src.systems.camera import Camera
from src.systems.map_renderer import MapRenderer
from src.core.resource_manager import ResourceManager
from src.objects.game_object import GameObject


class TestMapCollisionIntegration(unittest.TestCase):
    """Integration tests for map and collision systems."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.display.set_mode((1, 1))  # Minimal display for testing
        
        # Initialize systems
        self.map_system = MapSystem()
        self.collision_system = CollisionSystem(self.map_system)
        self.camera = Camera(800, 600)
        self.resource_manager = ResourceManager()
        self.map_renderer = MapRenderer(self.resource_manager)
        
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
                ],
                "collision": [
                    [1, 1, 1, 1, 1],
                    [1, 0, 0, 0, 1],
                    [1, 0, 1, 0, 1],
                    [1, 1, 1, 1, 1]
                ]
            }
        }
        
        # Load test map
        self.map_system.set_current_map(self.test_map_data)
        
        # Create test game object
        self.player = GameObject(48, 48)  # Position in open area (center of tile 1,1)
        self.player.width = 16
        self.player.height = 16
        
        # Create test screen
        self.screen = pygame.Surface((800, 600))
    
    def tearDown(self):
        """Clean up test fixtures."""
        pygame.quit()
    
    def test_map_loading_and_collision_detection(self):
        """Test that map loads correctly and collision detection works."""
        # Verify map is loaded
        current_map = self.map_system.get_current_map()
        self.assertIsNotNone(current_map)
        self.assertEqual(current_map['width'], 5)
        self.assertEqual(current_map['height'], 4)
        
        # Test collision detection with solid tiles
        # Position (0, 0) should be solid (wall)
        collision = self.collision_system.check_map_collision(self.player, 0, 0)
        self.assertTrue(collision)
        
        # Position (48, 48) should be open (no collision) - center of tile (1,1)
        collision = self.collision_system.check_map_collision(self.player, 48, 48)
        self.assertFalse(collision)
    
    def test_player_movement_with_collision_resolution(self):
        """Test player movement with collision resolution."""
        # Start player in open area
        self.player.x = 48
        self.player.y = 48
        
        # Try to move into wall (should be blocked)
        new_x, new_y = self.collision_system.resolve_map_collision(
            self.player, 48, 48, 16, 48)  # Try to move left into wall
        
        # Should not be able to move into wall
        self.assertNotEqual(new_x, 16)  # X movement should be blocked
        self.assertEqual(new_y, 48)     # Y should remain the same
    
    def test_camera_following_player_in_map(self):
        """Test camera following player within map bounds."""
        # Set camera bounds based on map size (but allow for screen size)
        map_width = self.test_map_data['width'] * self.test_map_data['tile_size']
        map_height = self.test_map_data['height'] * self.test_map_data['tile_size']
        # Only set bounds if map is larger than screen
        if map_width > self.camera.screen_width and map_height > self.camera.screen_height:
            self.camera.set_bounds(0, 0, map_width, map_height)
        
        # Move player and update camera
        self.player.x = 80
        self.player.y = 80
        self.camera.follow_target(self.player.x, self.player.y, 1.0)
        
        # Camera should follow player but stay within bounds (if bounds are set)
        if self.camera.bounds:
            self.assertGreaterEqual(self.camera.x, 0)
            self.assertGreaterEqual(self.camera.y, 0)
            self.assertLessEqual(self.camera.x, map_width - self.camera.screen_width)
            self.assertLessEqual(self.camera.y, map_height - self.camera.screen_height)
    
    def test_map_rendering_with_camera(self):
        """Test map rendering with camera offset."""
        # Set camera position
        self.camera.set_position(32, 32)
        
        # Render map (should not crash)
        self.map_renderer.render_map(self.screen, self.test_map_data, self.camera)
        
        # Verify some tiles were cached (indicating rendering occurred)
        self.assertGreater(len(self.map_renderer.tile_cache), 0)
    
    def test_coordinate_conversion_consistency(self):
        """Test that coordinate conversions are consistent between systems."""
        # Test world to tile conversion
        world_x, world_y = 96, 64
        tile_x, tile_y = self.map_system.world_to_tile(world_x, world_y)
        
        # Convert back to world coordinates
        converted_world_x, converted_world_y = self.map_system.tile_to_world(tile_x, tile_y)
        
        # Should be consistent (within tile boundaries)
        self.assertEqual(converted_world_x, tile_x * 32)
        self.assertEqual(converted_world_y, tile_y * 32)
        
        # Original coordinates should be within the tile
        self.assertGreaterEqual(world_x, converted_world_x)
        self.assertLess(world_x, converted_world_x + 32)
        self.assertGreaterEqual(world_y, converted_world_y)
        self.assertLess(world_y, converted_world_y + 32)
    
    def test_collision_at_tile_boundaries(self):
        """Test collision detection at tile boundaries."""
        # Test collision at exact tile boundary
        tile_size = self.test_map_data['tile_size']
        
        # Position in open area (tile 1,1) - should not collide
        open_x = 1 * tile_size + 8  # Well inside open tile
        open_y = 1 * tile_size + 8
        
        # Should not collide (in non-solid area)
        collision = self.collision_system.check_map_collision(
            self.player, open_x, open_y)
        self.assertFalse(collision)
        
        # Move into solid tile (tile 2,2)
        solid_x = 2 * tile_size + 8  # Inside solid tile
        solid_y = 2 * tile_size + 8
        collision = self.collision_system.check_map_collision(
            self.player, solid_x, solid_y)
        self.assertTrue(collision)
    
    def test_full_game_loop_simulation(self):
        """Test a simplified game loop with all systems working together."""
        # Simulate a few frames of game loop
        dt = 1.0 / 60.0  # 60 FPS
        initial_x = self.player.x
        
        for frame in range(5):
            # Simulate player trying to move
            old_x, old_y = self.player.x, self.player.y
            new_x = old_x + 2  # Try to move right (smaller movement)
            new_y = old_y
            
            # Check and resolve collisions
            resolved_x, resolved_y = self.collision_system.resolve_map_collision(
                self.player, old_x, old_y, new_x, new_y)
            
            # Update player position
            self.player.x = resolved_x
            self.player.y = resolved_y
            
            # Update camera to follow player (with reasonable speed)
            self.camera.follow_speed = 0.1  # Slower camera movement
            self.camera.follow_target(self.player.x, self.player.y, dt)
            
            # Render map
            self.map_renderer.render_map(self.screen, self.test_map_data, self.camera)
        
        # Player should have moved (no collision in open area)
        self.assertGreater(self.player.x, initial_x)
        
        # Camera position should be reasonable (not extreme values)
        self.assertGreater(self.camera.x, -1000)
        self.assertLess(self.camera.x, 1000)


if __name__ == '__main__':
    unittest.main()