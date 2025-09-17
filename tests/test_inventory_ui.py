"""
Unit tests for the inventory UI system.
Tests item slots, tooltips, inventory window, and inventory manager.
"""
import unittest
import pygame
from unittest.mock import Mock, patch
from src.systems.inventory_ui import ItemSlot, ItemTooltip, InventoryWindow, InventoryManager
from src.systems.inventory_system import Inventory
from src.systems.ui_system import UIManager
from src.objects.item import Item


class TestInventoryUI(unittest.TestCase):
    """Test cases for inventory UI components."""
    
    def setUp(self):
        """Set up test fixtures."""
        pygame.init()
        pygame.font.init()
        self.screen = pygame.Surface((800, 600))
        
        # Create test inventory with some items
        self.inventory = Inventory(max_size=20)
        self.test_item = Item(0, 0, 'health_potion')
        self.inventory.add_item(self.test_item)
        
        # Create UI manager
        self.ui_manager = UIManager()
        self.ui_manager.set_screen_size(800, 600)
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_item_slot_initialization(self):
        """Test ItemSlot initialization."""
        slot = ItemSlot(10, 20, 48, 5)
        
        self.assertEqual(slot.x, 10)
        self.assertEqual(slot.y, 20)
        self.assertEqual(slot.width, 48)
        self.assertEqual(slot.height, 48)
        self.assertEqual(slot.slot_index, 5)
        self.assertIsNone(slot.item)
        self.assertFalse(slot.is_selected)
        self.assertFalse(slot.is_hovered)
    
    def test_item_slot_set_item(self):
        """Test ItemSlot item setting."""
        slot = ItemSlot(0, 0, 48, 0)
        
        self.assertIsNone(slot.item)
        
        slot.set_item(self.test_item)
        self.assertEqual(slot.item, self.test_item)
        
        slot.set_item(None)
        self.assertIsNone(slot.item)
    
    def test_item_slot_selection_and_hover(self):
        """Test ItemSlot selection and hover states."""
        slot = ItemSlot(0, 0, 48, 0)
        
        # Test selection
        self.assertFalse(slot.is_selected)
        slot.set_selected(True)
        self.assertTrue(slot.is_selected)
        slot.set_selected(False)
        self.assertFalse(slot.is_selected)
        
        # Test hover
        self.assertFalse(slot.is_hovered)
        slot.set_hovered(True)
        self.assertTrue(slot.is_hovered)
        slot.set_hovered(False)
        self.assertFalse(slot.is_hovered)
    
    def test_item_slot_update(self):
        """Test ItemSlot update functionality."""
        slot = ItemSlot(0, 0, 48, 0)
        
        # Test hover animation
        slot.set_hovered(True)
        initial_time = slot.hover_animation_time
        slot.update(0.1)
        self.assertGreater(slot.hover_animation_time, initial_time)
        
        # Test hover animation decay
        slot.set_hovered(False)
        slot.update(0.1)
        self.assertLess(slot.hover_animation_time, 0.1 * slot.hover_animation_speed)
    
    def test_item_slot_render(self):
        """Test ItemSlot rendering."""
        slot = ItemSlot(10, 10, 48, 0)
        
        # Test empty slot rendering
        slot.render(self.screen)  # Should not crash
        
        # Test slot with item
        slot.set_item(self.test_item)
        slot.render(self.screen)  # Should not crash
        
        # Test selected slot
        slot.set_selected(True)
        slot.render(self.screen)  # Should not crash
        
        # Test hovered slot
        slot.set_hovered(True)
        slot.render(self.screen)  # Should not crash
        
        # Test invisible slot
        slot.set_visible(False)
        slot.render(self.screen)  # Should not crash
    
    def test_item_tooltip_initialization(self):
        """Test ItemTooltip initialization."""
        tooltip = ItemTooltip(layer=10)
        
        self.assertEqual(tooltip.layer, 10)
        self.assertIsNone(tooltip.item)
        self.assertFalse(tooltip.visible)
        self.assertEqual(tooltip.auto_hide_time, 0.0)
    
    def test_item_tooltip_show_hide(self):
        """Test ItemTooltip show/hide functionality."""
        tooltip = ItemTooltip()
        
        # Test show
        tooltip.show_item(self.test_item, 100, 200)
        self.assertEqual(tooltip.item, self.test_item)
        self.assertTrue(tooltip.visible)
        self.assertEqual(tooltip.x, 100)
        self.assertEqual(tooltip.y, 200)
        self.assertEqual(tooltip.auto_hide_time, 0.0)
        
        # Test hide
        tooltip.hide()
        self.assertFalse(tooltip.visible)
        self.assertIsNone(tooltip.item)
    
    def test_item_tooltip_auto_hide(self):
        """Test ItemTooltip auto-hide functionality."""
        tooltip = ItemTooltip()
        tooltip.auto_hide_delay = 0.1
        
        tooltip.show_item(self.test_item, 100, 200)
        self.assertTrue(tooltip.visible)
        
        # Update but not enough to trigger auto-hide
        tooltip.update(0.05)
        self.assertTrue(tooltip.visible)
        
        # Update enough to trigger auto-hide
        tooltip.update(0.1)
        self.assertFalse(tooltip.visible)
    
    def test_item_tooltip_render(self):
        """Test ItemTooltip rendering."""
        tooltip = ItemTooltip()
        
        # Test hidden tooltip
        tooltip.render(self.screen)  # Should not crash
        
        # Test visible tooltip with item
        tooltip.show_item(self.test_item, 100, 100)
        tooltip.render(self.screen)  # Should not crash
    
    def test_inventory_window_initialization(self):
        """Test InventoryWindow initialization."""
        window = InventoryWindow(50, 50, self.inventory)
        
        self.assertEqual(window.inventory, self.inventory)
        self.assertEqual(len(window.slots), self.inventory.max_size)
        self.assertEqual(window.selected_slot, 0)
        self.assertIsInstance(window.tooltip, ItemTooltip)
    
    def test_inventory_window_slot_creation(self):
        """Test InventoryWindow slot creation."""
        window = InventoryWindow(0, 0, self.inventory)
        
        # Check that slots are created correctly
        self.assertEqual(len(window.slots), self.inventory.max_size)
        
        for i, slot in enumerate(window.slots):
            self.assertEqual(slot.slot_index, i)
            self.assertIsInstance(slot, ItemSlot)
    
    def test_inventory_window_update(self):
        """Test InventoryWindow update functionality."""
        window = InventoryWindow(0, 0, self.inventory)
        
        # Should not crash when updating
        window.update(0.016)
        
        # Check that first slot has the test item
        self.assertEqual(window.slots[0].item, self.test_item)
        self.assertIsNone(window.slots[1].item)  # Second slot should be empty
    
    def test_inventory_window_mouse_handling(self):
        """Test InventoryWindow mouse event handling."""
        window = InventoryWindow(0, 0, self.inventory)
        
        # Test mouse motion
        window.handle_mouse_motion(100, 100)
        self.assertEqual(window.mouse_pos, (100, 100))
        
        # Test mouse click outside window
        result = window.handle_mouse_click(1000, 1000, 1)
        self.assertFalse(result)
        
        # Test mouse click on first slot (which has an item)
        slot_x = window.slots[0].x + window.slots[0].width // 2
        slot_y = window.slots[0].y + window.slots[0].height // 2
        
        # Mock callback
        window.on_item_selected = Mock()
        
        result = window.handle_mouse_click(slot_x, slot_y, 1)
        self.assertTrue(result)
        self.assertEqual(window.selected_slot, 0)
        window.on_item_selected.assert_called_once_with(self.test_item, 0)
    
    def test_inventory_window_keyboard_handling(self):
        """Test InventoryWindow keyboard event handling."""
        window = InventoryWindow(0, 0, self.inventory)
        
        # Test navigation keys
        self.assertEqual(window.selected_slot, 0)
        
        # Test right arrow
        result = window.handle_key_press(pygame.K_RIGHT)
        self.assertTrue(result)
        self.assertEqual(window.selected_slot, 1)
        
        # Test left arrow
        result = window.handle_key_press(pygame.K_LEFT)
        self.assertTrue(result)
        self.assertEqual(window.selected_slot, 0)
        
        # Test down arrow
        result = window.handle_key_press(pygame.K_DOWN)
        self.assertTrue(result)
        self.assertEqual(window.selected_slot, window.slots_per_row)
        
        # Test up arrow
        result = window.handle_key_press(pygame.K_UP)
        self.assertTrue(result)
        self.assertEqual(window.selected_slot, 0)
        
        # Test item usage key
        window.on_item_used = Mock()
        result = window.handle_key_press(pygame.K_RETURN)
        self.assertTrue(result)
        window.on_item_used.assert_called_once_with(self.test_item, 0)
    
    def test_inventory_window_render(self):
        """Test InventoryWindow rendering."""
        window = InventoryWindow(50, 50, self.inventory)
        
        # Should not crash when rendering
        window.render(self.screen)
        
        # Test invisible window
        window.set_visible(False)
        window.render(self.screen)  # Should not crash
    
    def test_inventory_window_callbacks(self):
        """Test InventoryWindow callback setting."""
        window = InventoryWindow(0, 0, self.inventory)
        
        selected_callback = Mock()
        used_callback = Mock()
        dropped_callback = Mock()
        
        window.set_callbacks(
            on_item_selected=selected_callback,
            on_item_used=used_callback,
            on_item_dropped=dropped_callback
        )
        
        self.assertEqual(window.on_item_selected, selected_callback)
        self.assertEqual(window.on_item_used, used_callback)
        self.assertEqual(window.on_item_dropped, dropped_callback)
    
    def test_inventory_window_get_selected_item(self):
        """Test InventoryWindow selected item retrieval."""
        window = InventoryWindow(0, 0, self.inventory)
        
        # First slot should have the test item
        window.selected_slot = 0
        selected_item = window.get_selected_item()
        self.assertEqual(selected_item, self.test_item)
        
        # Second slot should be empty
        window.selected_slot = 1
        selected_item = window.get_selected_item()
        self.assertIsNone(selected_item)
        
        # Invalid slot index
        window.selected_slot = 999
        selected_item = window.get_selected_item()
        self.assertIsNone(selected_item)
    
    def test_inventory_manager_initialization(self):
        """Test InventoryManager initialization."""
        manager = InventoryManager(self.ui_manager, self.inventory)
        
        self.assertEqual(manager.ui_manager, self.ui_manager)
        self.assertEqual(manager.inventory, self.inventory)
        self.assertIsNone(manager.inventory_window)
        self.assertFalse(manager.is_open)
        self.assertIsNotNone(manager.inventory_layer)
    
    def test_inventory_manager_open_close(self):
        """Test InventoryManager open/close functionality."""
        manager = InventoryManager(self.ui_manager, self.inventory)
        
        # Test open
        self.assertFalse(manager.is_open)
        manager.open_inventory()
        self.assertTrue(manager.is_open)
        self.assertIsNotNone(manager.inventory_window)
        self.assertTrue(manager.inventory_layer.visible)
        self.assertTrue(manager.inventory_layer.active)
        
        # Test close
        manager.close_inventory()
        self.assertFalse(manager.is_open)
        self.assertIsNone(manager.inventory_window)
        self.assertFalse(manager.inventory_layer.visible)
        self.assertFalse(manager.inventory_layer.active)
    
    def test_inventory_manager_toggle(self):
        """Test InventoryManager toggle functionality."""
        manager = InventoryManager(self.ui_manager, self.inventory)
        
        # Test toggle open
        self.assertFalse(manager.is_open)
        manager.toggle_inventory()
        self.assertTrue(manager.is_open)
        
        # Test toggle close
        manager.toggle_inventory()
        self.assertFalse(manager.is_open)
    
    def test_inventory_manager_key_handling(self):
        """Test InventoryManager keyboard handling."""
        manager = InventoryManager(self.ui_manager, self.inventory)
        
        # Test inventory toggle key
        result = manager.handle_key_press(pygame.K_i)
        self.assertTrue(result)
        self.assertTrue(manager.is_open)
        
        # Test inventory toggle key again
        result = manager.handle_key_press(pygame.K_i)
        self.assertTrue(result)
        self.assertFalse(manager.is_open)
        
        # Test TAB key
        result = manager.handle_key_press(pygame.K_TAB)
        self.assertTrue(result)
        self.assertTrue(manager.is_open)
        
        # Test other keys when inventory is open
        result = manager.handle_key_press(pygame.K_RIGHT)
        self.assertTrue(result)  # Should be handled by inventory window
        
        # Test unhandled key
        manager.close_inventory()
        result = manager.handle_key_press(pygame.K_a)
        self.assertFalse(result)
    
    def test_inventory_manager_mouse_handling(self):
        """Test InventoryManager mouse handling."""
        manager = InventoryManager(self.ui_manager, self.inventory)
        
        # Test mouse events when closed
        manager.handle_mouse_motion(100, 100)  # Should not crash
        result = manager.handle_mouse_click(100, 100, 1)
        self.assertFalse(result)
        
        # Test mouse events when open
        manager.open_inventory()
        manager.handle_mouse_motion(100, 100)  # Should not crash
        
        # Mouse click should be handled by inventory window
        result = manager.handle_mouse_click(100, 100, 1)
        # Result depends on whether click hits the window, but should not crash
        self.assertIsInstance(result, bool)
    
    def test_inventory_manager_refresh(self):
        """Test InventoryManager refresh functionality."""
        manager = InventoryManager(self.ui_manager, self.inventory)
        
        # Should not crash when closed
        manager.refresh()
        
        # Should not crash when open
        manager.open_inventory()
        manager.refresh()
    
    def test_inventory_manager_update(self):
        """Test InventoryManager update functionality."""
        manager = InventoryManager(self.ui_manager, self.inventory)
        
        # Should not crash
        manager.update(0.016)


if __name__ == '__main__':
    unittest.main()