"""
Tests for the map transition system.
"""
import unittest
import pygame
from unittest.mock import Mock, patch
import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from systems.map_transition_system import (
    MapTransitionSystem, MapTransition, TransitionType, TransitionDirection
)


class TestMapTransitionSystem(unittest.TestCase):
    """Test cases for MapTransitionSystem."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        self.transition_system = MapTransitionSystem()
        
        # Sample map data
        self.map_data = {
            'width': 20,
            'height': 15,
            'tile_size': 32
        }
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_initialization(self):
        """Test system initialization."""
        self.assertFalse(self.transition_system.is_transitioning)
        self.assertEqual(len(self.transition_system.transitions), 0)
        self.assertIsNone(self.transition_system.current_map_path)
        self.assertEqual(self.transition_system.transition_state, "idle")
    
    def test_set_current_map(self):
        """Test setting current map."""
        map_path = "assets/maps/test_map.json"
        self.transition_system.set_current_map(map_path)
        self.assertEqual(self.transition_system.current_map_path, map_path)
    
    def test_add_boundary_transition(self):
        """Test adding boundary transitions."""
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/north_map.json",
            (400, 450)
        )
        
        self.assertEqual(len(self.transition_system.transitions), 1)
        transition = self.transition_system.transitions["boundary_north"]
        self.assertEqual(transition.transition_type, TransitionType.BOUNDARY)
        self.assertEqual(transition.target_map, "assets/maps/north_map.json")
        self.assertEqual(transition.target_position, (400, 450))
        self.assertEqual(transition.direction, TransitionDirection.NORTH)
    
    def test_add_trigger_zone_transition(self):
        """Test adding trigger zone transitions."""
        trigger_area = pygame.Rect(100, 100, 64, 64)
        self.transition_system.add_trigger_zone_transition(
            "portal1",
            trigger_area,
            "assets/maps/dungeon.json",
            (200, 200)
        )
        
        self.assertEqual(len(self.transition_system.transitions), 1)
        transition = self.transition_system.transitions["zone_portal1"]
        self.assertEqual(transition.transition_type, TransitionType.TRIGGER_ZONE)
        self.assertEqual(transition.trigger_area, trigger_area)
    
    def test_add_door_transition(self):
        """Test adding door transitions."""
        self.transition_system.add_door_transition(
            "house_door",
            (150, 200),
            "assets/maps/house_interior.json",
            (300, 350)
        )
        
        self.assertEqual(len(self.transition_system.transitions), 1)
        transition = self.transition_system.transitions["door_house_door"]
        self.assertEqual(transition.transition_type, TransitionType.DOOR)
        self.assertIsNotNone(transition.trigger_area)
        self.assertEqual(transition.trigger_area.x, 150)
        self.assertEqual(transition.trigger_area.y, 200)
    
    def test_check_boundary_transitions(self):
        """Test boundary transition detection."""
        # Add north boundary transition
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/north_map.json",
            (400, 450)
        )
        
        # Player at north boundary should trigger transition
        transition = self.transition_system.check_transitions(400, 10, self.map_data)
        self.assertIsNotNone(transition)
        self.assertEqual(transition.direction, TransitionDirection.NORTH)
        
        # Player in middle should not trigger transition
        transition = self.transition_system.check_transitions(400, 200, self.map_data)
        self.assertIsNone(transition)
    
    def test_check_trigger_zone_transitions(self):
        """Test trigger zone transition detection."""
        trigger_area = pygame.Rect(100, 100, 64, 64)
        self.transition_system.add_trigger_zone_transition(
            "portal1",
            trigger_area,
            "assets/maps/dungeon.json",
            (200, 200)
        )
        
        # Player in trigger zone should trigger transition
        transition = self.transition_system.check_transitions(120, 120, self.map_data)
        self.assertIsNotNone(transition)
        self.assertEqual(transition.transition_type, TransitionType.TRIGGER_ZONE)
        
        # Player outside trigger zone should not trigger transition
        transition = self.transition_system.check_transitions(50, 50, self.map_data)
        self.assertIsNone(transition)
    
    def test_check_door_transitions(self):
        """Test door transition detection."""
        self.transition_system.add_door_transition(
            "house_door",
            (150, 200),
            "assets/maps/house_interior.json",
            (300, 350)
        )
        
        # Player at door should trigger transition
        transition = self.transition_system.check_transitions(160, 210, self.map_data)
        self.assertIsNotNone(transition)
        self.assertEqual(transition.transition_type, TransitionType.DOOR)
        
        # Player away from door should not trigger transition
        transition = self.transition_system.check_transitions(300, 300, self.map_data)
        self.assertIsNone(transition)
    
    def test_start_transition(self):
        """Test starting a transition."""
        transition = MapTransition(
            TransitionType.BOUNDARY,
            "assets/maps/test_map2.json",
            (100, 100),
            direction=TransitionDirection.NORTH
        )
        
        callback = Mock()
        self.transition_system.start_transition(transition, callback)
        
        self.assertTrue(self.transition_system.is_transitioning)
        self.assertEqual(self.transition_system.transition_state, "fade_out")
        self.assertEqual(self.transition_system.pending_transition, transition)
        self.assertEqual(self.transition_system.transition_callback, callback)
    
    def test_transition_animation_update(self):
        """Test transition animation updates."""
        transition = MapTransition(
            TransitionType.BOUNDARY,
            "assets/maps/test_map2.json",
            (100, 100)
        )
        
        callback = Mock()
        self.transition_system.start_transition(transition, callback)
        
        # Update fade out (fade speed is 255*2 = 510 per second, so 0.5 seconds to complete)
        self.transition_system.update(0.1)  # 0.1 second
        self.assertGreater(self.transition_system.fade_alpha, 0)
        self.assertEqual(self.transition_system.transition_state, "fade_out")
        
        # Complete fade out (need exactly 0.5 seconds total)
        self.transition_system.update(0.4)  # Another 0.4 seconds to complete fade out
        self.assertEqual(self.transition_system.fade_alpha, 255)
        self.assertEqual(self.transition_system.transition_state, "fade_in")
        callback.assert_called_once()
        
        # Complete fade in
        self.transition_system.update(0.5)  # 0.5 seconds to complete fade in
        self.assertFalse(self.transition_system.is_transitioning)
        self.assertEqual(self.transition_system.transition_state, "idle")
    
    def test_render_transition_overlay(self):
        """Test rendering transition overlay."""
        # Create a test surface
        screen = pygame.Surface((800, 600))
        
        # No overlay when not transitioning
        original_surface = screen.copy()
        self.transition_system.render_transition_overlay(screen)
        # Surface should be unchanged (can't easily test this without pixel comparison)
        
        # Start transition and test overlay
        transition = MapTransition(
            TransitionType.BOUNDARY,
            "assets/maps/test_map2.json",
            (100, 100)
        )
        self.transition_system.start_transition(transition, Mock())
        self.transition_system.fade_alpha = 128
        
        # Should render overlay (can't easily test visual result)
        self.transition_system.render_transition_overlay(screen)
    
    def test_clear_transitions(self):
        """Test clearing all transitions."""
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/north_map.json",
            (400, 450)
        )
        
        self.assertEqual(len(self.transition_system.transitions), 1)
        
        self.transition_system.clear_transitions()
        self.assertEqual(len(self.transition_system.transitions), 0)
    
    def test_remove_transition(self):
        """Test removing specific transitions."""
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/north_map.json",
            (400, 450)
        )
        
        self.assertEqual(len(self.transition_system.transitions), 1)
        
        self.transition_system.remove_transition("boundary_north")
        self.assertEqual(len(self.transition_system.transitions), 0)
        
        # Removing non-existent transition should not error
        self.transition_system.remove_transition("non_existent")
    
    def test_set_transition_active(self):
        """Test enabling/disabling transitions."""
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/north_map.json",
            (400, 450)
        )
        
        # Transition should be active by default
        transition = self.transition_system.transitions["boundary_north"]
        self.assertTrue(transition.active)
        
        # Disable transition
        self.transition_system.set_transition_active("boundary_north", False)
        self.assertFalse(transition.active)
        
        # Re-enable transition
        self.transition_system.set_transition_active("boundary_north", True)
        self.assertTrue(transition.active)
    
    def test_inactive_transitions_not_triggered(self):
        """Test that inactive transitions are not triggered."""
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/north_map.json",
            (400, 450)
        )
        
        # Disable transition
        self.transition_system.set_transition_active("boundary_north", False)
        
        # Player at boundary should not trigger inactive transition
        transition = self.transition_system.check_transitions(400, 10, self.map_data)
        self.assertIsNone(transition)
    
    def test_no_transitions_while_transitioning(self):
        """Test that no new transitions can be triggered while transitioning."""
        self.transition_system.add_boundary_transition(
            TransitionDirection.NORTH,
            "assets/maps/north_map.json",
            (400, 450)
        )
        
        # Start a transition
        transition = MapTransition(
            TransitionType.BOUNDARY,
            "assets/maps/test_map2.json",
            (100, 100)
        )
        self.transition_system.start_transition(transition, Mock())
        
        # Should not trigger new transition while transitioning
        new_transition = self.transition_system.check_transitions(400, 10, self.map_data)
        self.assertIsNone(new_transition)
    
    def test_get_transition_progress(self):
        """Test getting transition progress."""
        # No progress when not transitioning
        self.assertEqual(self.transition_system.get_transition_progress(), 0.0)
        
        # Start transition
        transition = MapTransition(
            TransitionType.BOUNDARY,
            "assets/maps/test_map2.json",
            (100, 100)
        )
        self.transition_system.start_transition(transition, Mock())
        
        # Progress during fade out
        self.transition_system.fade_alpha = 127.5  # Half way
        progress = self.transition_system.get_transition_progress()
        self.assertAlmostEqual(progress, 0.25, places=2)  # 50% of first half = 25%
        
        # Progress during loading
        self.transition_system.transition_state = "loading"
        self.assertEqual(self.transition_system.get_transition_progress(), 0.5)
        
        # Progress during fade in
        self.transition_system.transition_state = "fade_in"
        self.transition_system.fade_alpha = 127.5  # Half way through fade in
        progress = self.transition_system.get_transition_progress()
        self.assertAlmostEqual(progress, 0.75, places=2)  # 50% + 50% of second half = 75%


if __name__ == '__main__':
    unittest.main()