"""
Inventory UI system for displaying and managing player inventory.
Provides inventory window, item slots, and item information display.
"""
import pygame
import math
from typing import List, Optional, Tuple, Callable
from .ui_system import UIElement, UIManager, TextRenderer
from .inventory_system import Inventory
from ..objects.item import Item


class ItemSlot(UIElement):
    """
    Individual item slot in the inventory grid.
    """
    
    def __init__(self, x: int, y: int, size: int = 48, slot_index: int = 0, layer: int = 0):
        """
        Initialize item slot.
        
        Args:
            x: X position
            y: Y position
            size: Size of the slot (square)
            slot_index: Index of this slot in the inventory
            layer: Rendering layer
        """
        super().__init__(x, y, size, size, layer)
        
        self.slot_index = slot_index
        self.item: Optional[Item] = None
        self.is_selected = False
        self.is_hovered = False
        
        # Visual properties
        self.bg_color = (60, 60, 60)
        self.border_color = (120, 120, 120)
        self.selected_color = (255, 255, 0)
        self.hover_color = (200, 200, 200)
        self.border_width = 2
        
        # Item display properties
        self.item_padding = 4
        self.show_quantity = True
        
        # Animation properties
        self.hover_animation_time = 0.0
        self.hover_animation_speed = 4.0
    
    def set_item(self, item: Optional[Item]) -> None:
        """
        Set the item in this slot.
        
        Args:
            item: Item to place in slot, or None for empty slot
        """
        self.item = item
    
    def set_selected(self, selected: bool) -> None:
        """
        Set the selected state of this slot.
        
        Args:
            selected: Whether slot is selected
        """
        self.is_selected = selected
    
    def set_hovered(self, hovered: bool) -> None:
        """
        Set the hover state of this slot.
        
        Args:
            hovered: Whether slot is being hovered
        """
        self.is_hovered = hovered
    
    def update(self, dt: float) -> None:
        """
        Update slot animations.
        
        Args:
            dt: Delta time since last frame
        """
        if self.is_hovered:
            self.hover_animation_time += dt * self.hover_animation_speed
        else:
            self.hover_animation_time = max(0, self.hover_animation_time - dt * self.hover_animation_speed * 2)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the item slot.
        
        Args:
            screen: Pygame surface to render to
        """
        if not self.visible:
            return
        
        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, bg_rect)
        
        # Draw item if present
        if self.item:
            self._render_item(screen)
        
        # Draw border with appropriate color
        border_color = self.border_color
        if self.is_selected:
            border_color = self.selected_color
        elif self.is_hovered:
            # Animate hover effect
            hover_intensity = (math.sin(self.hover_animation_time) + 1) / 2
            base_color = self.hover_color
            border_color = (
                int(self.border_color[0] + (base_color[0] - self.border_color[0]) * hover_intensity),
                int(self.border_color[1] + (base_color[1] - self.border_color[1]) * hover_intensity),
                int(self.border_color[2] + (base_color[2] - self.border_color[2]) * hover_intensity)
            )
        
        pygame.draw.rect(screen, border_color, bg_rect, self.border_width)
    
    def _render_item(self, screen: pygame.Surface) -> None:
        """
        Render the item within the slot.
        
        Args:
            screen: Pygame surface to render to
        """
        if not self.item:
            return
        
        # Calculate item display area
        item_size = self.width - (self.item_padding * 2)
        item_x = self.x + self.item_padding
        item_y = self.y + self.item_padding
        
        # Draw item background with item color
        item_rect = pygame.Rect(item_x, item_y, item_size, item_size)
        pygame.draw.rect(screen, self.item.color, item_rect)
        
        # Draw item icon/sprite if available
        if hasattr(self.item, 'sprite') and self.item.sprite:
            # Scale sprite to fit slot
            scaled_sprite = pygame.transform.scale(self.item.sprite, (item_size, item_size))
            screen.blit(scaled_sprite, (item_x, item_y))
        else:
            # Draw simple colored rectangle with category indicator
            self._render_item_icon(screen, item_rect)
    
    def _render_item_icon(self, screen: pygame.Surface, rect: pygame.Rect) -> None:
        """
        Render a simple icon for the item.
        
        Args:
            screen: Pygame surface to render to
            rect: Rectangle to draw icon in
        """
        # Draw category-specific icon
        center_x = rect.centerx
        center_y = rect.centery
        
        if self.item.category == 'consumable':
            # Draw potion bottle shape
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 8)
            pygame.draw.rect(screen, (100, 100, 100), (center_x - 2, center_y - 12, 4, 6))
        elif self.item.category == 'weapon':
            # Draw sword shape
            pygame.draw.line(screen, (255, 255, 255), 
                           (center_x, center_y - 10), (center_x, center_y + 10), 3)
            pygame.draw.line(screen, (255, 255, 255), 
                           (center_x - 6, center_y - 6), (center_x + 6, center_y - 6), 2)
        elif self.item.category == 'armor':
            # Draw shield shape
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 10, 2)
            pygame.draw.line(screen, (255, 255, 255), 
                           (center_x - 6, center_y - 6), (center_x + 6, center_y + 6), 2)
        elif self.item.category == 'equipment':
            # Draw gear shape
            pygame.draw.circle(screen, (255, 255, 255), (center_x, center_y), 6, 2)
            for i in range(8):
                angle = i * math.pi / 4
                start_x = center_x + math.cos(angle) * 8
                start_y = center_y + math.sin(angle) * 8
                end_x = center_x + math.cos(angle) * 12
                end_y = center_y + math.sin(angle) * 12
                pygame.draw.line(screen, (255, 255, 255), (start_x, start_y), (end_x, end_y), 1)


class ItemTooltip(UIElement):
    """
    Tooltip that displays item information when hovering over items.
    """
    
    def __init__(self, layer: int = 10):
        """
        Initialize item tooltip.
        
        Args:
            layer: Rendering layer (should be high to appear on top)
        """
        super().__init__(0, 0, 200, 100, layer)
        
        self.item: Optional[Item] = None
        self.text_renderer = TextRenderer()
        self.padding = 8
        self.line_spacing = 2
        self.visible = False  # Start invisible
        
        # Visual properties
        self.bg_color = (40, 40, 40)
        self.border_color = (200, 200, 200)
        self.text_color = (255, 255, 255)
        self.title_color = (255, 255, 0)
        self.border_width = 1
        
        # Auto-hide properties
        self.auto_hide_time = 0.0
        self.auto_hide_delay = 0.1  # Hide after 0.1 seconds of no updates
    
    def show_item(self, item: Item, x: int, y: int) -> None:
        """
        Show tooltip for an item at specified position.
        
        Args:
            item: Item to show tooltip for
            x: X position for tooltip
            y: Y position for tooltip
        """
        self.item = item
        self.auto_hide_time = 0.0
        
        # Calculate tooltip size based on content
        self._calculate_size()
        
        # Position tooltip (adjust if it would go off screen)
        self.x = x
        self.y = y
        self.visible = True
    
    def hide(self) -> None:
        """Hide the tooltip."""
        self.visible = False
        self.item = None
    
    def update(self, dt: float) -> None:
        """
        Update tooltip auto-hide timer.
        
        Args:
            dt: Delta time since last frame
        """
        if self.visible and self.item:
            self.auto_hide_time += dt
            if self.auto_hide_time >= self.auto_hide_delay:
                self.hide()
    
    def _calculate_size(self) -> None:
        """Calculate tooltip size based on item content."""
        if not self.item:
            return
        
        # Calculate text dimensions
        title_size = self.text_renderer.get_text_size(self.item.name, size=16)
        desc_lines = self._wrap_text(self.item.description, 180)
        
        max_width = max(title_size[0], max(self.text_renderer.get_text_size(line, size=12)[0] for line in desc_lines))
        
        # Calculate height
        height = title_size[1] + 4  # Title height + spacing
        height += len(desc_lines) * (12 + self.line_spacing)  # Description lines
        
        # Add effects info if present
        if self.item.effect:
            height += 16 + len(self.item.effect) * 14  # Effects section
        
        self.width = max_width + self.padding * 2
        self.height = height + self.padding * 2
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """
        Wrap text to fit within specified width.
        
        Args:
            text: Text to wrap
            max_width: Maximum width in pixels
            
        Returns:
            List of wrapped text lines
        """
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_width = self.text_renderer.get_text_size(test_line, size=12)[0]
            
            if test_width <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    lines.append(word)  # Word is too long, add anyway
        
        if current_line:
            lines.append(' '.join(current_line))
        
        return lines
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the tooltip.
        
        Args:
            screen: Pygame surface to render to
        """
        if not self.visible or not self.item:
            return
        
        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, bg_rect)
        pygame.draw.rect(screen, self.border_color, bg_rect, self.border_width)
        
        # Render content
        y_offset = self.y + self.padding
        
        # Render title
        title_surface = self.text_renderer.render_text(self.item.name, size=16, color=self.title_color)
        screen.blit(title_surface, (self.x + self.padding, y_offset))
        y_offset += title_surface.get_height() + 4
        
        # Render description
        desc_lines = self._wrap_text(self.item.description, self.width - self.padding * 2)
        for line in desc_lines:
            line_surface = self.text_renderer.render_text(line, size=12, color=self.text_color)
            screen.blit(line_surface, (self.x + self.padding, y_offset))
            y_offset += line_surface.get_height() + self.line_spacing
        
        # Render effects
        if self.item.effect:
            y_offset += 4
            effects_title = self.text_renderer.render_text("Effects:", size=12, color=self.title_color)
            screen.blit(effects_title, (self.x + self.padding, y_offset))
            y_offset += effects_title.get_height() + 2
            
            for effect_name, effect_value in self.item.effect.items():
                effect_text = f"  {effect_name.replace('_', ' ').title()}: +{effect_value}"
                effect_surface = self.text_renderer.render_text(effect_text, size=11, color=self.text_color)
                screen.blit(effect_surface, (self.x + self.padding, y_offset))
                y_offset += effect_surface.get_height() + 1


class InventoryWindow(UIElement):
    """
    Main inventory window that contains item slots and controls.
    """
    
    def __init__(self, x: int, y: int, inventory: Inventory, layer: int = 5):
        """
        Initialize inventory window.
        
        Args:
            x: X position
            y: Y position
            inventory: Inventory system to display
            layer: Rendering layer
        """
        # Calculate window size based on inventory
        self.slots_per_row = 8
        self.slot_size = 48
        self.slot_spacing = 4
        self.padding = 16
        
        rows = (inventory.max_size + self.slots_per_row - 1) // self.slots_per_row
        
        width = (self.slots_per_row * self.slot_size + 
                (self.slots_per_row - 1) * self.slot_spacing + 
                self.padding * 2)
        height = (rows * self.slot_size + 
                 (rows - 1) * self.slot_spacing + 
                 self.padding * 2 + 40)  # Extra space for title and controls
        
        super().__init__(x, y, width, height, layer)
        
        self.inventory = inventory
        self.slots: List[ItemSlot] = []
        self.selected_slot = 0
        self.tooltip = ItemTooltip(layer + 1)
        
        # Visual properties
        self.bg_color = (50, 50, 50)
        self.border_color = (150, 150, 150)
        self.title_color = (255, 255, 255)
        self.border_width = 2
        
        # Input handling
        self.mouse_pos = (0, 0)
        self.last_mouse_pos = (0, 0)
        
        # Callbacks
        self.on_item_selected: Optional[Callable[[Item, int], None]] = None
        self.on_item_used: Optional[Callable[[Item, int], None]] = None
        self.on_item_dropped: Optional[Callable[[Item, int], None]] = None
        
        self._create_slots()
        self._update_slot_items()  # Initialize slot items
    
    def _create_slots(self) -> None:
        """Create item slots for the inventory."""
        self.slots.clear()
        
        for i in range(self.inventory.max_size):
            row = i // self.slots_per_row
            col = i % self.slots_per_row
            
            slot_x = (self.x + self.padding + 
                     col * (self.slot_size + self.slot_spacing))
            slot_y = (self.y + self.padding + 30 +  # 30 for title space
                     row * (self.slot_size + self.slot_spacing))
            
            slot = ItemSlot(slot_x, slot_y, self.slot_size, i, self.layer)
            self.slots.append(slot)
    
    def update(self, dt: float) -> None:
        """
        Update inventory window and slots.
        
        Args:
            dt: Delta time since last frame
        """
        if not self.active:
            return
        
        # Update inventory data in slots
        self._update_slot_items()
        
        # Update slots
        for slot in self.slots:
            slot.update(dt)
        
        # Update tooltip
        self.tooltip.update(dt)
        
        # Handle mouse hover
        self._handle_mouse_hover()
    
    def _update_slot_items(self) -> None:
        """Update items in slots based on inventory state."""
        items = self.inventory.get_items_list()
        
        for i, slot in enumerate(self.slots):
            if i < len(items):
                slot.set_item(items[i])
            else:
                slot.set_item(None)
            
            slot.set_selected(i == self.selected_slot)
    
    def _handle_mouse_hover(self) -> None:
        """Handle mouse hover over slots."""
        # Reset hover state for all slots
        for slot in self.slots:
            slot.set_hovered(False)
        
        # Check which slot is being hovered
        for slot in self.slots:
            if slot.contains_point(self.mouse_pos[0], self.mouse_pos[1]):
                slot.set_hovered(True)
                
                # Show tooltip if slot has item
                if slot.item and self.mouse_pos != self.last_mouse_pos:
                    self.tooltip.show_item(slot.item, 
                                         self.mouse_pos[0] + 10, 
                                         self.mouse_pos[1] + 10)
                    self.tooltip.auto_hide_time = 0.0  # Reset auto-hide timer
                break
        else:
            # No slot is hovered, hide tooltip
            if self.tooltip.visible:
                self.tooltip.hide()
        
        self.last_mouse_pos = self.mouse_pos
    
    def handle_mouse_motion(self, x: int, y: int) -> None:
        """
        Handle mouse motion events.
        
        Args:
            x: Mouse X position
            y: Mouse Y position
        """
        self.mouse_pos = (x, y)
    
    def handle_mouse_click(self, x: int, y: int, button: int) -> bool:
        """
        Handle mouse click events.
        
        Args:
            x: Mouse X position
            y: Mouse Y position
            button: Mouse button (1=left, 2=middle, 3=right)
            
        Returns:
            True if click was handled, False otherwise
        """
        if not self.visible or not self.active:
            return False
        
        # Check if click is within window
        if not self.contains_point(x, y):
            return False
        
        # Check which slot was clicked
        for slot in self.slots:
            if slot.contains_point(x, y):
                self.selected_slot = slot.slot_index
                
                if slot.item:
                    if button == 1:  # Left click - select item
                        if self.on_item_selected:
                            self.on_item_selected(slot.item, slot.slot_index)
                    elif button == 2:  # Middle click - use item
                        if self.on_item_used:
                            self.on_item_used(slot.item, slot.slot_index)
                    elif button == 3:  # Right click - drop item
                        if self.on_item_dropped:
                            self.on_item_dropped(slot.item, slot.slot_index)
                
                return True
        
        return False
    
    def handle_key_press(self, key: int) -> bool:
        """
        Handle keyboard input for inventory navigation.
        
        Args:
            key: Pygame key constant
            
        Returns:
            True if key was handled, False otherwise
        """
        if not self.visible or not self.active:
            return False
        
        if key == pygame.K_LEFT:
            self.selected_slot = max(0, self.selected_slot - 1)
            return True
        elif key == pygame.K_RIGHT:
            self.selected_slot = min(len(self.slots) - 1, self.selected_slot + 1)
            return True
        elif key == pygame.K_UP:
            self.selected_slot = max(0, self.selected_slot - self.slots_per_row)
            return True
        elif key == pygame.K_DOWN:
            self.selected_slot = min(len(self.slots) - 1, self.selected_slot + self.slots_per_row)
            return True
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            # Use selected item
            slot = self.slots[self.selected_slot]
            if slot.item and self.on_item_used:
                self.on_item_used(slot.item, slot.slot_index)
            return True
        
        return False
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the inventory window.
        
        Args:
            screen: Pygame surface to render to
        """
        if not self.visible:
            return
        
        # Draw window background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, bg_rect)
        pygame.draw.rect(screen, self.border_color, bg_rect, self.border_width)
        
        # Draw title
        self._render_title(screen)
        
        # Draw slots
        for slot in self.slots:
            slot.render(screen)
        
        # Draw inventory info
        self._render_inventory_info(screen)
        
        # Draw tooltip
        self.tooltip.render(screen)
    
    def _render_title(self, screen: pygame.Surface) -> None:
        """
        Render window title.
        
        Args:
            screen: Pygame surface to render to
        """
        try:
            font = pygame.font.Font(None, 24)
            title_text = font.render("Inventory", True, self.title_color)
            title_rect = title_text.get_rect()
            title_rect.centerx = self.x + self.width // 2
            title_rect.y = self.y + 8
            screen.blit(title_text, title_rect)
        except pygame.error:
            pass
    
    def _render_inventory_info(self, screen: pygame.Surface) -> None:
        """
        Render inventory information (item count, etc.).
        
        Args:
            screen: Pygame surface to render to
        """
        try:
            font = pygame.font.Font(None, 18)
            info_text = f"{self.inventory.get_item_count()}/{self.inventory.max_size}"
            text_surface = font.render(info_text, True, self.title_color)
            
            # Position at bottom right of window
            text_rect = text_surface.get_rect()
            text_rect.right = self.x + self.width - self.padding
            text_rect.bottom = self.y + self.height - 8
            
            screen.blit(text_surface, text_rect)
        except pygame.error:
            pass
    
    def set_callbacks(self, on_item_selected: Callable = None, 
                     on_item_used: Callable = None, 
                     on_item_dropped: Callable = None) -> None:
        """
        Set callback functions for inventory events.
        
        Args:
            on_item_selected: Called when item is selected
            on_item_used: Called when item is used
            on_item_dropped: Called when item is dropped
        """
        self.on_item_selected = on_item_selected
        self.on_item_used = on_item_used
        self.on_item_dropped = on_item_dropped
    
    def get_selected_item(self) -> Optional[Item]:
        """
        Get the currently selected item.
        
        Returns:
            Selected item or None if no item selected
        """
        if 0 <= self.selected_slot < len(self.slots):
            return self.slots[self.selected_slot].item
        return None
    
    def refresh(self) -> None:
        """Refresh the inventory display."""
        self._update_slot_items()


class InventoryManager:
    """
    Manager for inventory UI that integrates with the game's UI system.
    """
    
    def __init__(self, ui_manager: UIManager, inventory: Inventory):
        """
        Initialize inventory manager.
        
        Args:
            ui_manager: UI manager to add inventory to
            inventory: Inventory system to manage
        """
        self.ui_manager = ui_manager
        self.inventory = inventory
        self.inventory_window: Optional[InventoryWindow] = None
        self.is_open = False
        
        # Create inventory layer
        self.inventory_layer = ui_manager.create_layer("inventory", 10)
        self.inventory_layer.set_visible(False)
    
    def toggle_inventory(self) -> None:
        """Toggle inventory window open/closed."""
        if self.is_open:
            self.close_inventory()
        else:
            self.open_inventory()
    
    def open_inventory(self) -> None:
        """Open the inventory window."""
        if not self.is_open:
            # Calculate center position
            screen_width = self.ui_manager.screen_width
            screen_height = self.ui_manager.screen_height
            
            # Create inventory window
            self.inventory_window = InventoryWindow(
                (screen_width - 400) // 2,  # Center horizontally
                (screen_height - 300) // 2,  # Center vertically
                self.inventory,
                layer=0
            )
            
            # Set up callbacks
            self.inventory_window.set_callbacks(
                on_item_selected=self._on_item_selected,
                on_item_used=self._on_item_used,
                on_item_dropped=self._on_item_dropped
            )
            
            # Add to layer
            self.inventory_layer.add_element(self.inventory_window)
            self.inventory_layer.set_visible(True)
            self.inventory_layer.set_active(True)
            
            self.is_open = True
    
    def close_inventory(self) -> None:
        """Close the inventory window."""
        if self.is_open:
            self.inventory_layer.set_visible(False)
            self.inventory_layer.set_active(False)
            self.inventory_layer.clear_elements()
            self.inventory_window = None
            self.is_open = False
    
    def handle_mouse_motion(self, x: int, y: int) -> None:
        """
        Handle mouse motion events.
        
        Args:
            x: Mouse X position
            y: Mouse Y position
        """
        if self.is_open and self.inventory_window:
            self.inventory_window.handle_mouse_motion(x, y)
    
    def handle_mouse_click(self, x: int, y: int, button: int) -> bool:
        """
        Handle mouse click events.
        
        Args:
            x: Mouse X position
            y: Mouse Y position
            button: Mouse button
            
        Returns:
            True if click was handled, False otherwise
        """
        if self.is_open and self.inventory_window:
            return self.inventory_window.handle_mouse_click(x, y, button)
        return False
    
    def handle_key_press(self, key: int) -> bool:
        """
        Handle keyboard input.
        
        Args:
            key: Pygame key constant
            
        Returns:
            True if key was handled, False otherwise
        """
        if key == pygame.K_i or key == pygame.K_TAB:
            self.toggle_inventory()
            return True
        
        if self.is_open and self.inventory_window:
            return self.inventory_window.handle_key_press(key)
        
        return False
    
    def _on_item_selected(self, item: Item, slot_index: int) -> None:
        """
        Handle item selection.
        
        Args:
            item: Selected item
            slot_index: Slot index of selected item
        """
        print(f"Selected item: {item.name} at slot {slot_index}")
    
    def _on_item_used(self, item: Item, slot_index: int) -> None:
        """
        Handle item usage.
        
        Args:
            item: Item to use
            slot_index: Slot index of item
        """
        print(f"Using item: {item.name}")
        # The actual item usage should be handled by the game/player system
        # This is just for UI feedback
    
    def _on_item_dropped(self, item: Item, slot_index: int) -> None:
        """
        Handle item dropping.
        
        Args:
            item: Item to drop
            slot_index: Slot index of item
        """
        print(f"Dropping item: {item.name}")
        # The actual item dropping should be handled by the game system
    
    def refresh(self) -> None:
        """Refresh the inventory display."""
        if self.is_open and self.inventory_window:
            self.inventory_window.refresh()
    
    def update(self, dt: float) -> None:
        """
        Update inventory UI.
        
        Args:
            dt: Delta time since last frame
        """
        # UI manager handles the actual updates
        pass