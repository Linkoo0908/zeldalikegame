"""
Unit tests for the HUD UI system.
Tests health bars, experience bars, status indicators, and player HUD.
"""
import unittest
import pygame
import time
from unittest.mock import Mock, patch
from src.systems.hud_ui import ProgressBar, HealthBar, ExperienceBar, StatusIndicator, PlayerHUD


class TestHUDUI(unittest.TestCase):
    """Test cases for HUD UI components."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.font.init()
        self.screen = pygame.Surface((800, 600))
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_progress_bar_initialization(self):
        """Test ProgressBar initialization."""
        bar = ProgressBar(10, 20, 200, 30, max_value=150.0, current_value=75.0)
        
        self.assertEqual(bar.x, 10)
        self.assertEqual(bar.y, 20)
        self.assertEqual(bar.width, 200)
        self.assertEqual(bar.height, 30)
        self.assertEqual(bar.max_value, 150.0)
        self.assertEqual(bar.current_value, 75.0)
        self.assertEqual(bar.animated_value, 75.0)
        self.assertTrue(bar.show_text)
    
    def test_progress_bar_set_value(self):
        """Test ProgressBar value setting."""
        bar = ProgressBar(0, 0, 100, 20, max_value=100.0)
        
        # Normal value
        bar.set_value(50.0)
        self.assertEqual(bar.current_value, 50.0)
        
        # Value above maximum
        bar.set_value(150.0)
        self.assertEqual(bar.current_value, 100.0)
        
        # Negative value
        bar.set_value(-10.0)
        self.assertEqual(bar.current_value, 0.0)
    
    def test_progress_bar_set_max_value(self):
        """Test ProgressBar maximum value setting."""
        bar = ProgressBar(0, 0, 100, 20, max_value=100.0, current_value=80.0)
        
        # Increase max value
        bar.set_max_value(200.0)
        self.assertEqual(bar.max_value, 200.0)
        self.assertEqual(bar.current_value, 80.0)  # Should remain unchanged
        
        # Decrease max value below current
        bar.set_max_value(50.0)
        self.assertEqual(bar.max_value, 50.0)
        self.assertEqual(bar.current_value, 50.0)  # Should be clamped
        
        # Zero or negative max value
        bar.set_max_value(0.0)
        self.assertEqual(bar.max_value, 1.0)  # Should be clamped to minimum
    
    def test_progress_bar_get_percentage(self):
        """Test ProgressBar percentage calculation."""
        bar = ProgressBar(0, 0, 100, 20, max_value=100.0, current_value=25.0)
        
        self.assertAlmostEqual(bar.get_percentage(), 0.25)
        
        bar.set_value(0.0)
        self.assertAlmostEqual(bar.get_percentage(), 0.0)
        
        bar.set_value(100.0)
        self.assertAlmostEqual(bar.get_percentage(), 1.0)
        
        # Test with zero max value
        bar.set_max_value(0.0)  # Will be clamped to 1.0
        self.assertAlmostEqual(bar.get_percentage(), 1.0)
    
    def test_progress_bar_update_animation(self):
        """Test ProgressBar animation update."""
        bar = ProgressBar(0, 0, 100, 20, max_value=100.0, current_value=50.0)
        bar.animated_value = 0.0  # Start animation from 0
        
        # Update should move animated value towards current value
        bar.update(0.1)  # 0.1 seconds
        self.assertGreater(bar.animated_value, 0.0)
        self.assertLess(bar.animated_value, 50.0)
        
        # Continue updating until animation completes
        for _ in range(100):  # Enough iterations to complete animation
            bar.update(0.1)
        
        self.assertAlmostEqual(bar.animated_value, 50.0, places=1)
    
    def test_progress_bar_render(self):
        """Test ProgressBar rendering."""
        bar = ProgressBar(10, 10, 100, 20, max_value=100.0, current_value=50.0)
        
        # Should not crash when rendering
        bar.render(self.screen)
        
        # Test invisible bar
        bar.set_visible(False)
        bar.render(self.screen)  # Should not crash
    
    def test_health_bar_initialization(self):
        """Test HealthBar initialization."""
        health_bar = HealthBar(10, 20, 150, 25)
        
        self.assertEqual(health_bar.x, 10)
        self.assertEqual(health_bar.y, 20)
        self.assertEqual(health_bar.width, 150)
        self.assertEqual(health_bar.height, 25)
        self.assertEqual(health_bar.max_value, 100.0)
        self.assertEqual(health_bar.current_value, 100.0)
        self.assertEqual(health_bar.low_health_threshold, 0.25)
        self.assertEqual(health_bar.critical_health_threshold, 0.1)
    
    def test_health_bar_color_changes(self):
        """Test HealthBar color changes based on health level."""
        health_bar = HealthBar(0, 0, 100, 20)
        
        # Normal health
        health_bar.set_value(100.0)
        health_bar.update(0.016)
        health_bar.render(self.screen)
        
        # Low health
        health_bar.set_value(20.0)  # 20% health
        health_bar.update(0.016)
        health_bar.render(self.screen)
        
        # Critical health
        health_bar.set_value(5.0)  # 5% health
        health_bar.update(0.016)
        health_bar.render(self.screen)
        
        # Should not crash with any health level
    
    def test_health_bar_pulse_effect(self):
        """Test HealthBar pulse effect for critical health."""
        health_bar = HealthBar(0, 0, 100, 20)
        health_bar.set_value(5.0)  # Critical health
        
        initial_pulse_time = health_bar.pulse_time
        health_bar.update(0.1)
        
        # Pulse time should increase when health is critical
        self.assertGreater(health_bar.pulse_time, initial_pulse_time)
    
    def test_experience_bar_initialization(self):
        """Test ExperienceBar initialization."""
        exp_bar = ExperienceBar(10, 20, 180, 18)
        
        self.assertEqual(exp_bar.x, 10)
        self.assertEqual(exp_bar.y, 20)
        self.assertEqual(exp_bar.width, 180)
        self.assertEqual(exp_bar.height, 18)
        self.assertEqual(exp_bar.level, 1)
        self.assertEqual(exp_bar.current_value, 0.0)
        self.assertTrue(exp_bar.show_level)
    
    def test_experience_bar_set_experience(self):
        """Test ExperienceBar experience setting."""
        exp_bar = ExperienceBar(0, 0, 100, 20)
        
        exp_bar.set_experience(50.0, 100.0, 2)
        
        self.assertEqual(exp_bar.current_value, 50.0)
        self.assertEqual(exp_bar.max_value, 100.0)
        self.assertEqual(exp_bar.level, 2)
    
    def test_experience_bar_level_up_effect(self):
        """Test ExperienceBar level up effect."""
        exp_bar = ExperienceBar(0, 0, 100, 20)
        
        # Trigger level up
        exp_bar.set_experience(0.0, 150.0, 3)  # Level up from 1 to 3
        
        self.assertTrue(exp_bar.is_level_up_effect_active)
        self.assertEqual(exp_bar.level_up_effect_time, 0.0)
        
        # Update to progress the effect
        exp_bar.update(0.5)
        self.assertGreater(exp_bar.level_up_effect_time, 0.0)
        self.assertTrue(exp_bar.is_level_up_effect_active)
        
        # Update until effect completes
        exp_bar.update(1.0)  # Total 1.5 seconds, should complete
        self.assertFalse(exp_bar.is_level_up_effect_active)
    
    def test_experience_bar_render(self):
        """Test ExperienceBar rendering."""
        exp_bar = ExperienceBar(10, 10, 100, 20)
        exp_bar.set_experience(75.0, 100.0, 5)
        
        # Should not crash when rendering
        exp_bar.render(self.screen)
        
        # Test with level up effect
        exp_bar.trigger_level_up_effect()
        exp_bar.render(self.screen)  # Should not crash
    
    def test_status_indicator_initialization(self):
        """Test StatusIndicator initialization."""
        indicator = StatusIndicator(50, 50, 32)
        
        self.assertEqual(indicator.x, 50)
        self.assertEqual(indicator.y, 50)
        self.assertEqual(indicator.width, 32)
        self.assertEqual(indicator.height, 32)
        self.assertEqual(len(indicator.status_effects), 0)
    
    def test_status_indicator_add_remove_effects(self):
        """Test StatusIndicator effect management."""
        indicator = StatusIndicator(0, 0, 32)
        
        # Add effect
        indicator.add_status_effect("poison", (0, 255, 0), 5.0, "PO")
        self.assertEqual(len(indicator.status_effects), 1)
        self.assertIn("poison", indicator.status_effects)
        
        # Add another effect
        indicator.add_status_effect("strength", (255, 0, 0), 10.0, "ST")
        self.assertEqual(len(indicator.status_effects), 2)
        
        # Remove effect
        indicator.remove_status_effect("poison")
        self.assertEqual(len(indicator.status_effects), 1)
        self.assertNotIn("poison", indicator.status_effects)
        self.assertIn("strength", indicator.status_effects)
        
        # Clear all effects
        indicator.clear_status_effects()
        self.assertEqual(len(indicator.status_effects), 0)
    
    @patch('time.time')
    def test_status_indicator_effect_expiration(self, mock_time):
        """Test StatusIndicator effect expiration."""
        indicator = StatusIndicator(0, 0, 32)
        
        # Mock time progression
        mock_time.return_value = 1000.0
        
        # Add effect with duration
        indicator.add_status_effect("temp_effect", (255, 255, 0), 2.0)
        self.assertEqual(len(indicator.status_effects), 1)
        
        # Advance time but not enough to expire
        mock_time.return_value = 1001.5
        indicator.update(0.016)
        self.assertEqual(len(indicator.status_effects), 1)
        
        # Advance time to expire the effect
        mock_time.return_value = 1003.0
        indicator.update(0.016)
        self.assertEqual(len(indicator.status_effects), 0)
    
    def test_status_indicator_render(self):
        """Test StatusIndicator rendering."""
        indicator = StatusIndicator(10, 10, 32)
        
        # Empty indicator
        indicator.render(self.screen)  # Should not crash
        
        # With effects
        indicator.add_status_effect("effect1", (255, 0, 0), 0.0, "E1")
        indicator.add_status_effect("effect2", (0, 255, 0), 0.0, "E2")
        indicator.render(self.screen)  # Should not crash
        
        # Invisible indicator
        indicator.set_visible(False)
        indicator.render(self.screen)  # Should not crash
    
    def test_player_hud_initialization(self):
        """Test PlayerHUD initialization."""
        hud = PlayerHUD(800, 600)
        
        self.assertEqual(hud.screen_width, 800)
        self.assertEqual(hud.screen_height, 600)
        self.assertIsInstance(hud.health_bar, HealthBar)
        self.assertIsInstance(hud.experience_bar, ExperienceBar)
        self.assertIsInstance(hud.status_indicator, StatusIndicator)
        self.assertTrue(hud.show_labels)
    
    def test_player_hud_update_stats(self):
        """Test PlayerHUD stats updating."""
        hud = PlayerHUD(800, 600)
        
        hud.update_player_stats(75.0, 100.0, 250.0, 500.0, 3)
        
        self.assertEqual(hud.health_bar.current_value, 75.0)
        self.assertEqual(hud.health_bar.max_value, 100.0)
        self.assertEqual(hud.experience_bar.current_value, 250.0)
        self.assertEqual(hud.experience_bar.max_value, 500.0)
        self.assertEqual(hud.experience_bar.level, 3)
    
    def test_player_hud_status_effects(self):
        """Test PlayerHUD status effect management."""
        hud = PlayerHUD(800, 600)
        
        # Add status effect
        hud.add_status_effect("regeneration", (0, 255, 0), 10.0, "RG")
        self.assertEqual(len(hud.status_indicator.status_effects), 1)
        
        # Remove status effect
        hud.remove_status_effect("regeneration")
        self.assertEqual(len(hud.status_indicator.status_effects), 0)
    
    def test_player_hud_update(self):
        """Test PlayerHUD update functionality."""
        hud = PlayerHUD(800, 600)
        hud.update_player_stats(50.0, 100.0, 75.0, 100.0, 2)
        
        # Should not crash when updating
        hud.update(0.016)
    
    def test_player_hud_render(self):
        """Test PlayerHUD rendering."""
        hud = PlayerHUD(800, 600)
        hud.update_player_stats(80.0, 100.0, 150.0, 200.0, 4)
        hud.add_status_effect("test_effect", (255, 255, 0), 5.0)
        
        # Should not crash when rendering
        hud.render(self.screen)
        
        # Test without labels
        hud.show_labels = False
        hud.render(self.screen)  # Should not crash
    
    def test_player_hud_visibility(self):
        """Test PlayerHUD visibility control."""
        hud = PlayerHUD(800, 600)
        
        # All elements should be visible by default
        self.assertTrue(hud.health_bar.visible)
        self.assertTrue(hud.experience_bar.visible)
        self.assertTrue(hud.status_indicator.visible)
        
        # Hide HUD
        hud.set_visible(False)
        self.assertFalse(hud.health_bar.visible)
        self.assertFalse(hud.experience_bar.visible)
        self.assertFalse(hud.status_indicator.visible)
        
        # Show HUD
        hud.set_visible(True)
        self.assertTrue(hud.health_bar.visible)
        self.assertTrue(hud.experience_bar.visible)
        self.assertTrue(hud.status_indicator.visible)
    
    def test_player_hud_positioning(self):
        """Test PlayerHUD positioning."""
        hud = PlayerHUD(800, 600)
        
        # Set custom positions
        hud.set_position(50, 100, 50, 130)
        
        self.assertEqual(hud.health_bar.x, 50)
        self.assertEqual(hud.health_bar.y, 100)
        self.assertEqual(hud.experience_bar.x, 50)
        self.assertEqual(hud.experience_bar.y, 130)
    
    def test_player_hud_resize(self):
        """Test PlayerHUD resizing."""
        hud = PlayerHUD(800, 600)
        original_status_x = hud.status_indicator.x
        
        # Resize to larger screen
        hud.resize(1024, 768)
        
        self.assertEqual(hud.screen_width, 1024)
        self.assertEqual(hud.screen_height, 768)
        # Status indicator should move to maintain right alignment
        self.assertGreater(hud.status_indicator.x, original_status_x)


if __name__ == '__main__':
    unittest.main()