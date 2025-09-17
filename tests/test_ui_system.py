"""
Unit tests for the UI system.
Tests UI elements, text rendering, and layer management.
"""
import unittest
import pygame
from unittest.mock import Mock, patch
from src.systems.ui_system import UIElement, TextRenderer, UILayer, UIManager


class TestUIElement(UIElement):
    """Test implementation of UIElement for testing purposes."""
    
    def __init__(self, x, y, width, height, layer=0):
        super().__init__(x, y, width, height, layer)
        self.render_called = False
        self.update_called = False
    
    def render(self, screen):
        self.render_called = True
    
    def update(self, dt):
        self.update_called = True


class TestUISystem(unittest.TestCase):
    """Test cases for UI system components."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.font.init()
        self.screen = pygame.Surface((800, 600))
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_ui_element_initialization(self):
        """Test UIElement initialization."""
        element = TestUIElement(10, 20, 100, 50, layer=1)
        
        self.assertEqual(element.x, 10)
        self.assertEqual(element.y, 20)
        self.assertEqual(element.width, 100)
        self.assertEqual(element.height, 50)
        self.assertEqual(element.layer, 1)
        self.assertTrue(element.visible)
        self.assertTrue(element.active)
        self.assertEqual(element.rect, pygame.Rect(10, 20, 100, 50))
    
    def test_ui_element_set_position(self):
        """Test UIElement position setting."""
        element = TestUIElement(0, 0, 50, 50)
        element.set_position(100, 200)
        
        self.assertEqual(element.x, 100)
        self.assertEqual(element.y, 200)
        self.assertEqual(element.rect.x, 100)
        self.assertEqual(element.rect.y, 200)
    
    def test_ui_element_set_size(self):
        """Test UIElement size setting."""
        element = TestUIElement(0, 0, 50, 50)
        element.set_size(150, 100)
        
        self.assertEqual(element.width, 150)
        self.assertEqual(element.height, 100)
        self.assertEqual(element.rect.width, 150)
        self.assertEqual(element.rect.height, 100)
    
    def test_ui_element_contains_point(self):
        """Test UIElement point containment."""
        element = TestUIElement(10, 10, 50, 50)
        
        self.assertTrue(element.contains_point(30, 30))
        self.assertTrue(element.contains_point(10, 10))  # Top-left corner
        self.assertTrue(element.contains_point(59, 59))  # Bottom-right corner
        self.assertFalse(element.contains_point(5, 30))  # Left of element
        self.assertFalse(element.contains_point(70, 30))  # Right of element
        self.assertFalse(element.contains_point(30, 5))  # Above element
        self.assertFalse(element.contains_point(30, 70))  # Below element
    
    def test_ui_element_visibility(self):
        """Test UIElement visibility control."""
        element = TestUIElement(0, 0, 50, 50)
        
        self.assertTrue(element.visible)
        element.set_visible(False)
        self.assertFalse(element.visible)
        element.set_visible(True)
        self.assertTrue(element.visible)
    
    def test_ui_element_active_state(self):
        """Test UIElement active state control."""
        element = TestUIElement(0, 0, 50, 50)
        
        self.assertTrue(element.active)
        element.set_active(False)
        self.assertFalse(element.active)
        element.set_active(True)
        self.assertTrue(element.active)
    
    def test_text_renderer_initialization(self):
        """Test TextRenderer initialization."""
        renderer = TextRenderer()
        
        self.assertEqual(renderer.default_font_size, 16)
        self.assertEqual(renderer.default_color, (255, 255, 255))
        self.assertEqual(len(renderer.font_cache), 0)
    
    def test_text_renderer_get_font(self):
        """Test TextRenderer font retrieval and caching."""
        renderer = TextRenderer()
        
        # Test default font
        font1 = renderer.get_font()
        self.assertIsInstance(font1, pygame.font.Font)
        self.assertEqual(len(renderer.font_cache), 1)
        
        # Test same font retrieval (should use cache)
        font2 = renderer.get_font()
        self.assertIs(font1, font2)
        self.assertEqual(len(renderer.font_cache), 1)
        
        # Test different size
        font3 = renderer.get_font(size=24)
        self.assertIsInstance(font3, pygame.font.Font)
        self.assertIsNot(font1, font3)
        self.assertEqual(len(renderer.font_cache), 2)
    
    def test_text_renderer_render_text(self):
        """Test TextRenderer text rendering."""
        renderer = TextRenderer()
        
        surface = renderer.render_text("Hello World")
        self.assertIsInstance(surface, pygame.Surface)
        self.assertGreater(surface.get_width(), 0)
        self.assertGreater(surface.get_height(), 0)
        
        # Test with custom parameters
        surface2 = renderer.render_text("Test", size=24, color=(255, 0, 0))
        self.assertIsInstance(surface2, pygame.Surface)
        self.assertNotEqual(surface.get_size(), surface2.get_size())
    
    def test_text_renderer_get_text_size(self):
        """Test TextRenderer text size calculation."""
        renderer = TextRenderer()
        
        width, height = renderer.get_text_size("Hello")
        self.assertGreater(width, 0)
        self.assertGreater(height, 0)
        
        # Longer text should be wider
        width2, height2 = renderer.get_text_size("Hello World")
        self.assertGreater(width2, width)
        self.assertEqual(height2, height)  # Same height for same font size
    
    def test_text_renderer_multiline(self):
        """Test TextRenderer multiline text rendering."""
        renderer = TextRenderer()
        
        text = "This is a long line that should wrap to multiple lines"
        surface = renderer.render_text_multiline(text, max_width=100)
        
        self.assertIsInstance(surface, pygame.Surface)
        self.assertLessEqual(surface.get_width(), 100)
        self.assertGreater(surface.get_height(), renderer.get_font().get_height())
    
    def test_text_renderer_clear_cache(self):
        """Test TextRenderer cache clearing."""
        renderer = TextRenderer()
        
        # Add some fonts to cache
        renderer.get_font()
        renderer.get_font(size=24)
        self.assertEqual(len(renderer.font_cache), 2)
        
        # Clear cache
        renderer.clear_cache()
        self.assertEqual(len(renderer.font_cache), 0)
    
    def test_ui_layer_initialization(self):
        """Test UILayer initialization."""
        layer = UILayer("test_layer", 5)
        
        self.assertEqual(layer.name, "test_layer")
        self.assertEqual(layer.layer_index, 5)
        self.assertEqual(len(layer.elements), 0)
        self.assertTrue(layer.visible)
        self.assertTrue(layer.active)
    
    def test_ui_layer_add_remove_elements(self):
        """Test UILayer element management."""
        layer = UILayer("test_layer")
        element1 = TestUIElement(0, 0, 50, 50, layer=1)
        element2 = TestUIElement(50, 50, 50, 50, layer=0)
        
        # Add elements
        layer.add_element(element1)
        layer.add_element(element2)
        self.assertEqual(len(layer.elements), 2)
        
        # Elements should be sorted by layer
        self.assertEqual(layer.elements[0], element2)  # layer 0 first
        self.assertEqual(layer.elements[1], element1)  # layer 1 second
        
        # Remove element
        layer.remove_element(element1)
        self.assertEqual(len(layer.elements), 1)
        self.assertEqual(layer.elements[0], element2)
    
    def test_ui_layer_clear_elements(self):
        """Test UILayer element clearing."""
        layer = UILayer("test_layer")
        element1 = TestUIElement(0, 0, 50, 50)
        element2 = TestUIElement(50, 50, 50, 50)
        
        layer.add_element(element1)
        layer.add_element(element2)
        self.assertEqual(len(layer.elements), 2)
        
        layer.clear_elements()
        self.assertEqual(len(layer.elements), 0)
    
    def test_ui_layer_update(self):
        """Test UILayer update functionality."""
        layer = UILayer("test_layer")
        element1 = TestUIElement(0, 0, 50, 50)
        element2 = TestUIElement(50, 50, 50, 50)
        
        layer.add_element(element1)
        layer.add_element(element2)
        
        # Test normal update
        layer.update(0.016)
        self.assertTrue(element1.update_called)
        self.assertTrue(element2.update_called)
        
        # Reset flags
        element1.update_called = False
        element2.update_called = False
        
        # Test inactive layer
        layer.set_active(False)
        layer.update(0.016)
        self.assertFalse(element1.update_called)
        self.assertFalse(element2.update_called)
    
    def test_ui_layer_render(self):
        """Test UILayer render functionality."""
        layer = UILayer("test_layer")
        element1 = TestUIElement(0, 0, 50, 50)
        element2 = TestUIElement(50, 50, 50, 50)
        
        layer.add_element(element1)
        layer.add_element(element2)
        
        # Test normal render
        layer.render(self.screen)
        self.assertTrue(element1.render_called)
        self.assertTrue(element2.render_called)
        
        # Reset flags
        element1.render_called = False
        element2.render_called = False
        
        # Test invisible layer
        layer.set_visible(False)
        layer.render(self.screen)
        self.assertFalse(element1.render_called)
        self.assertFalse(element2.render_called)
    
    def test_ui_manager_initialization(self):
        """Test UIManager initialization."""
        manager = UIManager()
        
        self.assertEqual(len(manager.layers), 0)
        self.assertEqual(len(manager.layer_order), 0)
        self.assertIsInstance(manager.text_renderer, TextRenderer)
        self.assertEqual(manager.screen_width, 800)
        self.assertEqual(manager.screen_height, 600)
    
    def test_ui_manager_create_layer(self):
        """Test UIManager layer creation."""
        manager = UIManager()
        
        layer1 = manager.create_layer("layer1", 1)
        layer2 = manager.create_layer("layer2", 0)
        layer3 = manager.create_layer("layer3", 2)
        
        self.assertEqual(len(manager.layers), 3)
        self.assertEqual(len(manager.layer_order), 3)
        
        # Layers should be ordered by layer_index
        self.assertEqual(manager.layer_order, ["layer2", "layer1", "layer3"])
        
        self.assertIs(manager.get_layer("layer1"), layer1)
        self.assertIs(manager.get_layer("layer2"), layer2)
        self.assertIs(manager.get_layer("layer3"), layer3)
    
    def test_ui_manager_remove_layer(self):
        """Test UIManager layer removal."""
        manager = UIManager()
        
        layer1 = manager.create_layer("layer1", 1)
        layer2 = manager.create_layer("layer2", 0)
        
        self.assertEqual(len(manager.layers), 2)
        self.assertEqual(len(manager.layer_order), 2)
        
        manager.remove_layer("layer1")
        
        self.assertEqual(len(manager.layers), 1)
        self.assertEqual(len(manager.layer_order), 1)
        self.assertIsNone(manager.get_layer("layer1"))
        self.assertIs(manager.get_layer("layer2"), layer2)
    
    def test_ui_manager_add_element_to_layer(self):
        """Test UIManager element addition to layers."""
        manager = UIManager()
        layer = manager.create_layer("test_layer")
        element = TestUIElement(0, 0, 50, 50)
        
        manager.add_element_to_layer("test_layer", element)
        
        self.assertEqual(len(layer.elements), 1)
        self.assertIs(layer.elements[0], element)
        
        # Test adding to non-existent layer
        manager.add_element_to_layer("non_existent", element)
        # Should not crash, just do nothing
    
    def test_ui_manager_update(self):
        """Test UIManager update functionality."""
        manager = UIManager()
        layer1 = manager.create_layer("layer1", 0)
        layer2 = manager.create_layer("layer2", 1)
        
        element1 = TestUIElement(0, 0, 50, 50)
        element2 = TestUIElement(50, 50, 50, 50)
        
        layer1.add_element(element1)
        layer2.add_element(element2)
        
        manager.update(0.016)
        
        self.assertTrue(element1.update_called)
        self.assertTrue(element2.update_called)
    
    def test_ui_manager_render(self):
        """Test UIManager render functionality."""
        manager = UIManager()
        layer1 = manager.create_layer("layer1", 0)
        layer2 = manager.create_layer("layer2", 1)
        
        element1 = TestUIElement(0, 0, 50, 50)
        element2 = TestUIElement(50, 50, 50, 50)
        
        layer1.add_element(element1)
        layer2.add_element(element2)
        
        manager.render(self.screen)
        
        self.assertTrue(element1.render_called)
        self.assertTrue(element2.render_called)
    
    def test_ui_manager_text_rendering(self):
        """Test UIManager text rendering convenience methods."""
        manager = UIManager()
        
        # Test direct text rendering (should not crash)
        manager.render_text(self.screen, "Hello", 10, 10)
        manager.render_text_centered(self.screen, "Centered", 400, 300)
        
        # These methods should work without throwing exceptions
        # Actual visual verification would require manual testing
    
    def test_ui_manager_layer_visibility_control(self):
        """Test UIManager layer visibility control."""
        manager = UIManager()
        layer = manager.create_layer("test_layer")
        
        self.assertTrue(layer.visible)
        
        manager.set_layer_visible("test_layer", False)
        self.assertFalse(layer.visible)
        
        manager.set_layer_visible("test_layer", True)
        self.assertTrue(layer.visible)
        
        # Test non-existent layer
        manager.set_layer_visible("non_existent", False)
        # Should not crash
    
    def test_ui_manager_layer_active_control(self):
        """Test UIManager layer active state control."""
        manager = UIManager()
        layer = manager.create_layer("test_layer")
        
        self.assertTrue(layer.active)
        
        manager.set_layer_active("test_layer", False)
        self.assertFalse(layer.active)
        
        manager.set_layer_active("test_layer", True)
        self.assertTrue(layer.active)
        
        # Test non-existent layer
        manager.set_layer_active("non_existent", False)
        # Should not crash
    
    def test_ui_manager_clear_all_layers(self):
        """Test UIManager clearing all layers."""
        manager = UIManager()
        
        manager.create_layer("layer1")
        manager.create_layer("layer2")
        
        self.assertEqual(len(manager.layers), 2)
        self.assertEqual(len(manager.layer_order), 2)
        
        manager.clear_all_layers()
        
        self.assertEqual(len(manager.layers), 0)
        self.assertEqual(len(manager.layer_order), 0)
    
    def test_ui_manager_screen_size(self):
        """Test UIManager screen size management."""
        manager = UIManager()
        
        self.assertEqual(manager.screen_width, 800)
        self.assertEqual(manager.screen_height, 600)
        
        manager.set_screen_size(1024, 768)
        
        self.assertEqual(manager.screen_width, 1024)
        self.assertEqual(manager.screen_height, 768)


if __name__ == '__main__':
    unittest.main()