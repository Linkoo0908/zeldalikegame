"""
UI System for rendering user interface elements.
Provides base classes and utilities for UI rendering, text rendering, and UI layer management.
"""
import pygame
from typing import List, Dict, Optional, Tuple, Any
from abc import ABC, abstractmethod


class UIElement(ABC):
    """
    Base class for all UI elements.
    Provides common functionality for positioning, rendering, and interaction.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, layer: int = 0):
        """
        Initialize UI element.
        
        Args:
            x: X position
            y: Y position
            width: Element width
            height: Element height
            layer: Rendering layer (higher values render on top)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.layer = layer
        self.visible = True
        self.active = True
        self.rect = pygame.Rect(x, y, width, height)
    
    @abstractmethod
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the UI element to the screen.
        
        Args:
            screen: Pygame surface to render to
        """
        pass
    
    def update(self, dt: float) -> None:
        """
        Update the UI element.
        
        Args:
            dt: Delta time since last frame
        """
        pass
    
    def set_position(self, x: int, y: int) -> None:
        """
        Set the position of the UI element.
        
        Args:
            x: New X position
            y: New Y position
        """
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
    
    def set_size(self, width: int, height: int) -> None:
        """
        Set the size of the UI element.
        
        Args:
            width: New width
            height: New height
        """
        self.width = width
        self.height = height
        self.rect.width = width
        self.rect.height = height
    
    def contains_point(self, x: int, y: int) -> bool:
        """
        Check if a point is within this UI element.
        
        Args:
            x: X coordinate
            y: Y coordinate
            
        Returns:
            True if point is within element bounds
        """
        return self.rect.collidepoint(x, y)
    
    def set_visible(self, visible: bool) -> None:
        """
        Set visibility of the UI element.
        
        Args:
            visible: Whether element should be visible
        """
        self.visible = visible
    
    def set_active(self, active: bool) -> None:
        """
        Set active state of the UI element.
        
        Args:
            active: Whether element should be active
        """
        self.active = active


class TextRenderer:
    """
    Utility class for rendering text with various styles and options.
    """
    
    def __init__(self):
        """Initialize the text renderer."""
        self.font_cache: Dict[Tuple[str, int], pygame.font.Font] = {}
        self.default_font_size = 16
        self.default_color = (255, 255, 255)
    
    def get_font(self, font_name: Optional[str] = None, size: int = None) -> pygame.font.Font:
        """
        Get a font object, using cache for performance.
        
        Args:
            font_name: Name of font (None for default)
            size: Font size (None for default)
            
        Returns:
            Pygame font object
        """
        if size is None:
            size = self.default_font_size
        
        cache_key = (font_name, size)
        
        if cache_key not in self.font_cache:
            try:
                if font_name is None:
                    font = pygame.font.Font(None, size)
                else:
                    font = pygame.font.Font(font_name, size)
                self.font_cache[cache_key] = font
            except pygame.error:
                # Fallback to default font if specified font fails
                font = pygame.font.Font(None, size)
                self.font_cache[cache_key] = font
        
        return self.font_cache[cache_key]
    
    def render_text(self, text: str, font_name: Optional[str] = None, 
                   size: int = None, color: Tuple[int, int, int] = None,
                   antialias: bool = True) -> pygame.Surface:
        """
        Render text to a surface.
        
        Args:
            text: Text to render
            font_name: Font name (None for default)
            size: Font size (None for default)
            color: Text color (None for default)
            antialias: Whether to use antialiasing
            
        Returns:
            Pygame surface containing rendered text
        """
        if color is None:
            color = self.default_color
        
        font = self.get_font(font_name, size)
        return font.render(text, antialias, color)
    
    def render_text_multiline(self, text: str, max_width: int, 
                             font_name: Optional[str] = None, size: int = None,
                             color: Tuple[int, int, int] = None,
                             line_spacing: int = 2) -> pygame.Surface:
        """
        Render multiline text with word wrapping.
        
        Args:
            text: Text to render
            max_width: Maximum width before wrapping
            font_name: Font name (None for default)
            size: Font size (None for default)
            color: Text color (None for default)
            line_spacing: Extra spacing between lines
            
        Returns:
            Pygame surface containing rendered multiline text
        """
        if color is None:
            color = self.default_color
        
        font = self.get_font(font_name, size)
        words = text.split(' ')
        lines = []
        current_line = []
        
        for word in words:
            test_line = ' '.join(current_line + [word])
            test_surface = font.render(test_line, True, color)
            
            if test_surface.get_width() <= max_width:
                current_line.append(word)
            else:
                if current_line:
                    lines.append(' '.join(current_line))
                    current_line = [word]
                else:
                    # Word is too long, add it anyway
                    lines.append(word)
        
        if current_line:
            lines.append(' '.join(current_line))
        
        # Calculate total height
        line_height = font.get_height()
        total_height = len(lines) * line_height + (len(lines) - 1) * line_spacing
        
        # Create surface for all lines
        surface = pygame.Surface((max_width, total_height), pygame.SRCALPHA)
        
        # Render each line
        y_offset = 0
        for line in lines:
            line_surface = font.render(line, True, color)
            surface.blit(line_surface, (0, y_offset))
            y_offset += line_height + line_spacing
        
        return surface
    
    def get_text_size(self, text: str, font_name: Optional[str] = None, 
                     size: int = None) -> Tuple[int, int]:
        """
        Get the size of rendered text without actually rendering it.
        
        Args:
            text: Text to measure
            font_name: Font name (None for default)
            size: Font size (None for default)
            
        Returns:
            Tuple of (width, height)
        """
        font = self.get_font(font_name, size)
        return font.size(text)
    
    def clear_cache(self) -> None:
        """Clear the font cache."""
        self.font_cache.clear()


class UILayer:
    """
    Represents a layer of UI elements that can be managed together.
    """
    
    def __init__(self, name: str, layer_index: int = 0):
        """
        Initialize UI layer.
        
        Args:
            name: Name of the layer
            layer_index: Layer index for rendering order
        """
        self.name = name
        self.layer_index = layer_index
        self.elements: List[UIElement] = []
        self.visible = True
        self.active = True
    
    def add_element(self, element: UIElement) -> None:
        """
        Add a UI element to this layer.
        
        Args:
            element: UI element to add
        """
        self.elements.append(element)
        # Sort elements by their individual layer values
        self.elements.sort(key=lambda e: e.layer)
    
    def remove_element(self, element: UIElement) -> None:
        """
        Remove a UI element from this layer.
        
        Args:
            element: UI element to remove
        """
        if element in self.elements:
            self.elements.remove(element)
    
    def clear_elements(self) -> None:
        """Clear all elements from this layer."""
        self.elements.clear()
    
    def update(self, dt: float) -> None:
        """
        Update all elements in this layer.
        
        Args:
            dt: Delta time since last frame
        """
        if not self.active:
            return
        
        for element in self.elements:
            if element.active:
                element.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render all elements in this layer.
        
        Args:
            screen: Pygame surface to render to
        """
        if not self.visible:
            return
        
        for element in self.elements:
            if element.visible:
                element.render(screen)
    
    def set_visible(self, visible: bool) -> None:
        """
        Set visibility of the entire layer.
        
        Args:
            visible: Whether layer should be visible
        """
        self.visible = visible
    
    def set_active(self, active: bool) -> None:
        """
        Set active state of the entire layer.
        
        Args:
            active: Whether layer should be active
        """
        self.active = active


class UIManager:
    """
    Main UI system that manages layers and provides rendering utilities.
    """
    
    def __init__(self):
        """Initialize the UI manager."""
        self.layers: Dict[str, UILayer] = {}
        self.layer_order: List[str] = []
        self.text_renderer = TextRenderer()
        self.screen_width = 800
        self.screen_height = 600
    
    def set_screen_size(self, width: int, height: int) -> None:
        """
        Set the screen size for UI calculations.
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.screen_width = width
        self.screen_height = height
    
    def create_layer(self, name: str, layer_index: int = 0) -> UILayer:
        """
        Create a new UI layer.
        
        Args:
            name: Name of the layer
            layer_index: Layer index for rendering order
            
        Returns:
            Created UI layer
        """
        layer = UILayer(name, layer_index)
        self.layers[name] = layer
        
        # Insert layer in correct position based on layer_index
        inserted = False
        for i, existing_name in enumerate(self.layer_order):
            if self.layers[existing_name].layer_index > layer_index:
                self.layer_order.insert(i, name)
                inserted = True
                break
        
        if not inserted:
            self.layer_order.append(name)
        
        return layer
    
    def get_layer(self, name: str) -> Optional[UILayer]:
        """
        Get a UI layer by name.
        
        Args:
            name: Name of the layer
            
        Returns:
            UI layer or None if not found
        """
        return self.layers.get(name)
    
    def remove_layer(self, name: str) -> None:
        """
        Remove a UI layer.
        
        Args:
            name: Name of the layer to remove
        """
        if name in self.layers:
            del self.layers[name]
            if name in self.layer_order:
                self.layer_order.remove(name)
    
    def add_element_to_layer(self, layer_name: str, element: UIElement) -> None:
        """
        Add a UI element to a specific layer.
        
        Args:
            layer_name: Name of the layer
            element: UI element to add
        """
        layer = self.get_layer(layer_name)
        if layer:
            layer.add_element(element)
    
    def update(self, dt: float) -> None:
        """
        Update all UI layers and elements.
        
        Args:
            dt: Delta time since last frame
        """
        for layer_name in self.layer_order:
            layer = self.layers[layer_name]
            layer.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render all UI layers and elements.
        
        Args:
            screen: Pygame surface to render to
        """
        for layer_name in self.layer_order:
            layer = self.layers[layer_name]
            layer.render(screen)
    
    def render_text(self, screen: pygame.Surface, text: str, x: int, y: int,
                   font_name: Optional[str] = None, size: int = None,
                   color: Tuple[int, int, int] = None) -> None:
        """
        Convenience method to render text directly to screen.
        
        Args:
            screen: Pygame surface to render to
            text: Text to render
            x: X position
            y: Y position
            font_name: Font name (None for default)
            size: Font size (None for default)
            color: Text color (None for default)
        """
        text_surface = self.text_renderer.render_text(text, font_name, size, color)
        screen.blit(text_surface, (x, y))
    
    def render_text_centered(self, screen: pygame.Surface, text: str, 
                           center_x: int, center_y: int,
                           font_name: Optional[str] = None, size: int = None,
                           color: Tuple[int, int, int] = None) -> None:
        """
        Render text centered at a specific point.
        
        Args:
            screen: Pygame surface to render to
            text: Text to render
            center_x: Center X position
            center_y: Center Y position
            font_name: Font name (None for default)
            size: Font size (None for default)
            color: Text color (None for default)
        """
        text_surface = self.text_renderer.render_text(text, font_name, size, color)
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        screen.blit(text_surface, text_rect)
    
    def clear_all_layers(self) -> None:
        """Clear all UI layers and elements."""
        for layer in self.layers.values():
            layer.clear_elements()
        self.layers.clear()
        self.layer_order.clear()
    
    def set_layer_visible(self, layer_name: str, visible: bool) -> None:
        """
        Set visibility of a specific layer.
        
        Args:
            layer_name: Name of the layer
            visible: Whether layer should be visible
        """
        layer = self.get_layer(layer_name)
        if layer:
            layer.set_visible(visible)
    
    def set_layer_active(self, layer_name: str, active: bool) -> None:
        """
        Set active state of a specific layer.
        
        Args:
            layer_name: Name of the layer
            active: Whether layer should be active
        """
        layer = self.get_layer(layer_name)
        if layer:
            layer.set_active(active)
    
    def get_text_renderer(self) -> TextRenderer:
        """
        Get the text renderer instance.
        
        Returns:
            TextRenderer instance
        """
        return self.text_renderer