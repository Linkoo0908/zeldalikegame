"""
Integration tests for map transition system.
"""
import unittest
import pygame
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from systems.map_transition_system import MapTransitionSystem, TransitionDirection
from systems.map_system import MapSystem


class TestMapTransitionIntegration(unittest.TestCase):
    """Integration tests for map transition system."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.transition_system = MapTransitionSystem()
        self.map_system = MapSystem()
        
        # Create test map data
        self.test_map_data = {
            'width': 20,
            'height': 15,
            'tile_size': 32,
            'layers': {
                'background': [[1 for _ in range(20)] for _ in range(15)],
                'collision': [[0 for _ in range(20)] for _ in range(15)]
            }
        }
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_boundary_transition_integration(self):
        """Test boundary transition with real map data."""
        # Set up map system
        self.map_system.set_current_map(self.test_map_data)
        self.transition_system.set_current_map("test_map.json")
        
        # Add boundary transition
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/test_map2.json",
            (400, 450)
        )
        
        # Test player at north boundary
        map_width = self.test_map_data['width'] * self.test_map_data['tile_size']
        map_height = self.test_map_data['height'] * self.test_map_data['tile_size']
        
        # Player at north boundary should trigger transition
        transition = self.transition_system.check_transitions(
            map_width // 2, 10, self.test_map_data
        )
        self.assertIsNotNone(transition)
        self.assertEqual(transition.target_map, "assets/maps/test_map2.json")
        self.assertEqual(transition.target_position, (400, 450))
    
    def test_trigger_zone_integration(self):
        """Test trigger zone transition with collision detection."""
        # Set up trigger zone
        trigger_area = pygame.Rect(200, 200, 64, 64)
        self.transition_system.add_trigger_zone_transition(
            "portal1",
            trigger_area,
            "assets/maps/dungeon.json",
            (100, 100)
        )
        
        # Player in trigger zone
        transition = self.transition_system.check_transitions(
            220, 220, self.test_map_data
        )
        self.assertIsNotNone(transition)
        
        # Player outside trigger zone
        transition = self.transition_system.check_transitions(
            100, 100, self.test_map_data
        )
        self.assertIsNone(transition)
    
    def test_transition_animation_cycle(self):
        """Test complete transition animation cycle."""
        transition_completed = False
        target_map = None
        target_position = None
        
        def transition_callback(map_path, position):
            nonlocal transition_completed, target_map, target_position
            transition_completed = True
            target_map = map_path
            target_position = position
        
        # Add and trigger transition
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/test_map2.json",
            (400, 450)
        )
        
        transition = self.transition_system.check_transitions(
            400, 10, self.test_map_data
        )
        self.assertIsNotNone(transition)
        
        # Start transition
        self.transition_system.start_transition(transition, transition_callback)
        self.assertTrue(self.transition_system.is_transition_active())
        
        # Complete fade out (0.5 seconds at 510 alpha/second)
        self.transition_system.update(0.5)
        self.assertTrue(transition_completed)
        self.assertEqual(target_map, "assets/maps/test_map2.json")
        self.assertEqual(target_position, (400, 450))
        
        # Complete fade in
        self.transition_system.update(0.5)
        self.assertFalse(self.transition_system.is_transition_active())
    
    def test_multiple_transition_types(self):
        """Test multiple transition types on same map."""
        # Add different types of transitions
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/north.json",
            (100, 100)
        )
        
        trigger_area = pygame.Rect(300, 300, 32, 32)
        self.transition_system.add_trigger_zone_transition(
            "portal",
            trigger_area,
            "assets/maps/portal.json",
            (200, 200)
        )
        
        self.transition_system.add_door_transition(
            "house",
            (150, 150),
            "assets/maps/house.json",
            (300, 300)
        )
        
        # Test each transition type
        # Boundary
        transition = self.transition_system.check_transitions(400, 10, self.test_map_data)
        self.assertIsNotNone(transition)
        self.assertEqual(transition.target_map, "assets/maps/north.json")
        
        # Trigger zone
        transition = self.transition_system.check_transitions(310, 310, self.test_map_data)
        self.assertIsNotNone(transition)
        self.assertEqual(transition.target_map, "assets/maps/portal.json")
        
        # Door
        transition = self.transition_system.check_transitions(160, 160, self.test_map_data)
        self.assertIsNotNone(transition)
        self.assertEqual(transition.target_map, "assets/maps/house.json")
    
    def test_transition_state_management(self):
        """Test transition state management."""
        # Add transition
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/test_map2.json",
            (400, 450)
        )
        
        # Initially not transitioning
        self.assertFalse(self.transition_system.is_transition_active())
        self.assertEqual(self.transition_system.get_transition_progress(), 0.0)
        
        # Start transition
        transition = self.transition_system.check_transitions(400, 10, self.test_map_data)
        self.transition_system.start_transition(transition, lambda m, p: None)
        
        # Should be transitioning
        self.assertTrue(self.transition_system.is_transition_active())
        
        # Update to get some progress
        self.transition_system.update(0.1)
        self.assertGreater(self.transition_system.get_transition_progress(), 0.0)
        
        # No new transitions should be possible while transitioning
        new_transition = self.transition_system.check_transitions(400, 10, self.test_map_data)
        self.assertIsNone(new_transition)
        
        # Complete transition - need to update in steps
        # First complete fade out (0.4 more seconds after the 0.1 we already did)
        self.transition_system.update(0.4)
        # Then complete fade in
        self.transition_system.update(0.5)
        
        self.assertFalse(self.transition_system.is_transition_active())
        self.assertEqual(self.transition_system.get_transition_progress(), 0.0)


if __name__ == '__main__':
    unittest.main()