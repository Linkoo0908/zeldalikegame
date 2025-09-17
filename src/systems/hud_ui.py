"""
HUD UI components for displaying player status information.
Includes health bars, experience bars, and other status indicators.
"""
import pygame
import math
from typing import Tuple, Optional
from .ui_system import UIElement


class ProgressBar(UIElement):
    """
    Generic progress bar UI element that can be used for health, experience, etc.
    """
    
    def __init__(self, x: int, y: int, width: int, height: int, 
                 max_value: float = 100.0, current_value: float = 100.0,
                 bg_color: Tuple[int, int, int] = (50, 50, 50),
                 fill_color: Tuple[int, int, int] = (0, 255, 0),
                 border_color: Tuple[int, int, int] = (255, 255, 255),
                 border_width: int = 2, layer: int = 0):
        """
        Initialize progress bar.
        
        Args:
            x: X position
            y: Y position
            width: Bar width
            height: Bar height
            max_value: Maximum value for the bar
            current_value: Current value for the bar
            bg_color: Background color
            fill_color: Fill color
            border_color: Border color
            border_width: Border width in pixels
            layer: Rendering layer
        """
        super().__init__(x, y, width, height, layer)
        
        self.max_value = max_value
        self.current_value = current_value
        self.bg_color = bg_color
        self.fill_color = fill_color
        self.border_color = border_color
        self.border_width = border_width
        
        # Animation properties
        self.animated_value = current_value
        self.animation_speed = 50.0  # Units per second for smooth animation
        
        # Visual effects
        self.show_text = True
        self.text_color = (255, 255, 255)
        self.font_size = 14
    
    def set_value(self, value: float) -> None:
        """
        Set the current value of the progress bar.
        
        Args:
            value: New current value
        """
        self.current_value = max(0, min(self.max_value, value))
    
    def set_max_value(self, max_value: float) -> None:
        """
        Set the maximum value of the progress bar.
        
        Args:
            max_value: New maximum value
        """
        self.max_value = max(1, max_value)  # Prevent division by zero
        self.current_value = min(self.current_value, self.max_value)
    
    def get_percentage(self) -> float:
        """
        Get the current value as a percentage.
        
        Returns:
            Percentage (0.0 to 1.0)
        """
        if self.max_value <= 0:
            return 0.0
        return self.current_value / self.max_value
    
    def update(self, dt: float) -> None:
        """
        Update the progress bar animation.
        
        Args:
            dt: Delta time since last frame
        """
        # Animate the displayed value towards the actual value
        if abs(self.animated_value - self.current_value) > 0.1:
            if self.animated_value < self.current_value:
                self.animated_value = min(self.current_value, 
                                        self.animated_value + self.animation_speed * dt)
            else:
                self.animated_value = max(self.current_value, 
                                        self.animated_value - self.animation_speed * dt)
        else:
            self.animated_value = self.current_value
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the progress bar to the screen.
        
        Args:
            screen: Pygame surface to render to
        """
        if not self.visible:
            return
        
        # Draw background
        bg_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, bg_rect)
        
        # Draw fill based on animated value
        fill_percentage = self.animated_value / self.max_value if self.max_value > 0 else 0
        fill_width = int(self.width * fill_percentage)
        
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            pygame.draw.rect(screen, self.fill_color, fill_rect)
        
        # Draw border
        if self.border_width > 0:
            pygame.draw.rect(screen, self.border_color, bg_rect, self.border_width)
        
        # Draw text if enabled
        if self.show_text:
            self._render_text(screen)
    
    def _render_text(self, screen: pygame.Surface) -> None:
        """
        Render text overlay on the progress bar.
        
        Args:
            screen: Pygame surface to render to
        """
        try:
            font = pygame.font.Font(None, self.font_size)
            text = f"{int(self.current_value)}/{int(self.max_value)}"
            text_surface = font.render(text, True, self.text_color)
            
            # Center text on the bar
            text_rect = text_surface.get_rect()
            text_rect.center = (self.x + self.width // 2, self.y + self.height // 2)
            
            screen.blit(text_surface, text_rect)
        except pygame.error:
            # If font rendering fails, just skip text
            pass


class HealthBar(ProgressBar):
    """
    Health bar UI element with health-specific styling and behavior.
    """
    
    def __init__(self, x: int, y: int, width: int = 200, height: int = 20, layer: int = 0):
        """
        Initialize health bar.
        
        Args:
            x: X position
            y: Y position
            width: Bar width
            height: Bar height
            layer: Rendering layer
        """
        super().__init__(
            x, y, width, height,
            max_value=100.0,
            current_value=100.0,
            bg_color=(100, 20, 20),  # Dark red background
            fill_color=(220, 20, 20),  # Bright red fill
            border_color=(255, 255, 255),
            border_width=2,
            layer=layer
        )
        
        # Health-specific properties
        self.low_health_threshold = 0.25  # 25% health
        self.critical_health_threshold = 0.1  # 10% health
        self.low_health_color = (255, 165, 0)  # Orange
        self.critical_health_color = (255, 0, 0)  # Bright red
        
        # Pulsing effect for low health
        self.pulse_time = 0.0
        self.pulse_speed = 3.0
    
    def update(self, dt: float) -> None:
        """
        Update health bar with special effects.
        
        Args:
            dt: Delta time since last frame
        """
        super().update(dt)
        
        # Update pulse effect for low health
        if self.get_percentage() <= self.critical_health_threshold:
            self.pulse_time += dt * self.pulse_speed
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render health bar with health-specific effects.
        
        Args:
            screen: Pygame surface to render to
        """
        if not self.visible:
            return
        
        # Adjust fill color based on health percentage
        health_percentage = self.get_percentage()
        
        if health_percentage <= self.critical_health_threshold:
            # Critical health - pulsing red effect
            pulse_intensity = (math.sin(self.pulse_time) + 1) / 2  # 0 to 1
            base_color = self.critical_health_color
            self.fill_color = (
                int(base_color[0] * (0.5 + 0.5 * pulse_intensity)),
                int(base_color[1] * (0.5 + 0.5 * pulse_intensity)),
                int(base_color[2] * (0.5 + 0.5 * pulse_intensity))
            )
        elif health_percentage <= self.low_health_threshold:
            # Low health - orange color
            self.fill_color = self.low_health_color
        else:
            # Normal health - red color
            self.fill_color = (220, 20, 20)
        
        # Render the progress bar
        super().render(screen)


class ExperienceBar(ProgressBar):
    """
    Experience bar UI element with experience-specific styling and behavior.
    """
    
    def __init__(self, x: int, y: int, width: int = 200, height: int = 16, layer: int = 0):
        """
        Initialize experience bar.
        
        Args:
            x: X position
            y: Y position
            width: Bar width
            height: Bar height
            layer: Rendering layer
        """
        super().__init__(
            x, y, width, height,
            max_value=100.0,
            current_value=0.0,
            bg_color=(20, 20, 100),  # Dark blue background
            fill_color=(50, 150, 255),  # Bright blue fill
            border_color=(255, 255, 255),
            border_width=1,
            layer=layer
        )
        
        # Experience-specific properties
        self.level = 1
        self.show_level = True
        self.level_up_effect_time = 0.0
        self.level_up_effect_duration = 1.0
        self.is_level_up_effect_active = False
        
        # Level up colors
        self.level_up_color = (255, 215, 0)  # Gold
        self.normal_fill_color = (50, 150, 255)
    
    def set_experience(self, current_exp: float, max_exp: float, level: int) -> None:
        """
        Set experience values and level.
        
        Args:
            current_exp: Current experience points
            max_exp: Experience needed for next level
            level: Current level
        """
        old_level = self.level
        self.level = level
        self.set_max_value(max_exp)
        self.set_value(current_exp)
        
        # Trigger level up effect if level increased
        if level > old_level:
            self.trigger_level_up_effect()
    
    def trigger_level_up_effect(self) -> None:
        """Trigger the level up visual effect."""
        self.is_level_up_effect_active = True
        self.level_up_effect_time = 0.0
    
    def update(self, dt: float) -> None:
        """
        Update experience bar with level up effects.
        
        Args:
            dt: Delta time since last frame
        """
        super().update(dt)
        
        # Update level up effect
        if self.is_level_up_effect_active:
            self.level_up_effect_time += dt
            if self.level_up_effect_time >= self.level_up_effect_duration:
                self.is_level_up_effect_active = False
                self.level_up_effect_time = 0.0
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render experience bar with level up effects.
        
        Args:
            screen: Pygame surface to render to
        """
        if not self.visible:
            return
        
        # Apply level up effect
        if self.is_level_up_effect_active:
            effect_progress = self.level_up_effect_time / self.level_up_effect_duration
            # Fade from gold back to normal color
            fade_factor = 1.0 - effect_progress
            
            normal_color = self.normal_fill_color
            gold_color = self.level_up_color
            
            self.fill_color = (
                int(normal_color[0] + (gold_color[0] - normal_color[0]) * fade_factor),
                int(normal_color[1] + (gold_color[1] - normal_color[1]) * fade_factor),
                int(normal_color[2] + (gold_color[2] - normal_color[2]) * fade_factor)
            )
        else:
            self.fill_color = self.normal_fill_color
        
        # Render the progress bar
        super().render(screen)
        
        # Render level text if enabled
        if self.show_level:
            self._render_level_text(screen)
    
    def _render_level_text(self, screen: pygame.Surface) -> None:
        """
        Render level text next to the experience bar.
        
        Args:
            screen: Pygame surface to render to
        """
        try:
            font = pygame.font.Font(None, 18)
            level_text = f"Level {self.level}"
            text_surface = font.render(level_text, True, self.text_color)
            
            # Position text to the left of the bar
            text_rect = text_surface.get_rect()
            text_rect.right = self.x - 5
            text_rect.centery = self.y + self.height // 2
            
            screen.blit(text_surface, text_rect)
        except pygame.error:
            # If font rendering fails, just skip text
            pass


class StatusIndicator(UIElement):
    """
    Status indicator for showing temporary effects, buffs, debuffs, etc.
    """
    
    def __init__(self, x: int, y: int, size: int = 32, layer: int = 0):
        """
        Initialize status indicator.
        
        Args:
            x: X position
            y: Y position
            size: Size of the indicator (square)
            layer: Rendering layer
        """
        super().__init__(x, y, size, size, layer)
        
        self.status_effects = {}  # Dict of effect_name -> effect_data
        self.icon_size = size - 4  # Leave space for border
        self.border_color = (255, 255, 255)
        self.border_width = 2
        
        # Animation properties
        self.pulse_time = 0.0
        self.pulse_speed = 2.0
    
    def add_status_effect(self, name: str, color: Tuple[int, int, int], 
                         duration: float = 0.0, icon_text: str = None) -> None:
        """
        Add a status effect to display.
        
        Args:
            name: Name of the effect
            color: Color to represent the effect
            duration: Duration of the effect (0 for permanent)
            icon_text: Text to display on the icon (optional)
        """
        import time
        
        self.status_effects[name] = {
            'color': color,
            'duration': duration,
            'start_time': time.time(),
            'icon_text': icon_text or name[:2].upper()
        }
    
    def remove_status_effect(self, name: str) -> None:
        """
        Remove a status effect.
        
        Args:
            name: Name of the effect to remove
        """
        if name in self.status_effects:
            del self.status_effects[name]
    
    def clear_status_effects(self) -> None:
        """Clear all status effects."""
        self.status_effects.clear()
    
    def update(self, dt: float) -> None:
        """
        Update status indicator and remove expired effects.
        
        Args:
            dt: Delta time since last frame
        """
        import time
        current_time = time.time()
        
        # Remove expired effects
        expired_effects = []
        for name, effect_data in self.status_effects.items():
            if effect_data['duration'] > 0:
                elapsed = current_time - effect_data['start_time']
                if elapsed >= effect_data['duration']:
                    expired_effects.append(name)
        
        for name in expired_effects:
            self.remove_status_effect(name)
        
        # Update pulse animation
        self.pulse_time += dt * self.pulse_speed
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render status indicators.
        
        Args:
            screen: Pygame surface to render to
        """
        if not self.visible or not self.status_effects:
            return
        
        # Render each status effect as a small icon
        effect_names = list(self.status_effects.keys())
        icons_per_row = 4
        icon_spacing = self.width + 2
        
        for i, name in enumerate(effect_names):
            effect_data = self.status_effects[name]
            
            # Calculate position
            row = i // icons_per_row
            col = i % icons_per_row
            icon_x = self.x + col * icon_spacing
            icon_y = self.y + row * icon_spacing
            
            # Create icon rect
            icon_rect = pygame.Rect(icon_x, icon_y, self.width, self.height)
            
            # Draw background with effect color
            pygame.draw.rect(screen, effect_data['color'], icon_rect)
            
            # Draw border with pulse effect
            pulse_intensity = (math.sin(self.pulse_time) + 1) / 2
            border_alpha = int(128 + 127 * pulse_intensity)
            border_color = (*self.border_color, border_alpha)
            
            # Since pygame.draw.rect doesn't support alpha, we'll use a simpler approach
            pygame.draw.rect(screen, self.border_color, icon_rect, self.border_width)
            
            # Draw icon text
            self._render_icon_text(screen, effect_data['icon_text'], icon_rect)
    
    def _render_icon_text(self, screen: pygame.Surface, text: str, rect: pygame.Rect) -> None:
        """
        Render text on a status icon.
        
        Args:
            screen: Pygame surface to render to
            text: Text to render
            rect: Rectangle to center text in
        """
        try:
            font = pygame.font.Font(None, 16)
            text_surface = font.render(text, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=rect.center)
            screen.blit(text_surface, text_rect)
        except pygame.error:
            # If font rendering fails, just skip text
            pass


class PlayerHUD:
    """
    Complete player HUD that combines health bar, experience bar, and status indicators.
    """
    
    def __init__(self, screen_width: int, screen_height: int):
        """
        Initialize player HUD.
        
        Args:
            screen_width: Screen width for positioning
            screen_height: Screen height for positioning
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Create UI elements
        self.health_bar = HealthBar(20, 20, 200, 24, layer=1)
        self.experience_bar = ExperienceBar(20, 50, 200, 16, layer=1)
        self.status_indicator = StatusIndicator(screen_width - 150, 20, 32, layer=1)
        
        # Labels
        self.show_labels = True
        self.label_color = (255, 255, 255)
        self.label_font_size = 16
    
    def update_player_stats(self, health: float, max_health: float, 
                           experience: float, max_experience: float, level: int) -> None:
        """
        Update HUD with current player stats.
        
        Args:
            health: Current health
            max_health: Maximum health
            experience: Current experience
            max_experience: Experience needed for next level
            level: Current level
        """
        self.health_bar.set_max_value(max_health)
        self.health_bar.set_value(health)
        
        self.experience_bar.set_experience(experience, max_experience, level)
    
    def add_status_effect(self, name: str, color: Tuple[int, int, int], 
                         duration: float = 0.0, icon_text: str = None) -> None:
        """
        Add a status effect to the HUD.
        
        Args:
            name: Name of the effect
            color: Color to represent the effect
            duration: Duration of the effect
            icon_text: Text to display on the icon
        """
        self.status_indicator.add_status_effect(name, color, duration, icon_text)
    
    def remove_status_effect(self, name: str) -> None:
        """
        Remove a status effect from the HUD.
        
        Args:
            name: Name of the effect to remove
        """
        self.status_indicator.remove_status_effect(name)
    
    def update(self, dt: float) -> None:
        """
        Update all HUD elements.
        
        Args:
            dt: Delta time since last frame
        """
        self.health_bar.update(dt)
        self.experience_bar.update(dt)
        self.status_indicator.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the complete HUD.
        
        Args:
            screen: Pygame surface to render to
        """
        # Render labels if enabled
        if self.show_labels:
            self._render_labels(screen)
        
        # Render UI elements
        self.health_bar.render(screen)
        self.experience_bar.render(screen)
        self.status_indicator.render(screen)
    
    def _render_labels(self, screen: pygame.Surface) -> None:
        """
        Render labels for the HUD elements.
        
        Args:
            screen: Pygame surface to render to
        """
        try:
            font = pygame.font.Font(None, self.label_font_size)
            
            # Health label
            health_label = font.render("Health:", True, self.label_color)
            screen.blit(health_label, (self.health_bar.x, self.health_bar.y - 18))
            
            # Experience label
            exp_label = font.render("Experience:", True, self.label_color)
            screen.blit(exp_label, (self.experience_bar.x, self.experience_bar.y - 18))
            
        except pygame.error:
            # If font rendering fails, just skip labels
            pass
    
    def set_position(self, health_x: int, health_y: int, exp_x: int, exp_y: int) -> None:
        """
        Set positions of HUD elements.
        
        Args:
            health_x: Health bar X position
            health_y: Health bar Y position
            exp_x: Experience bar X position
            exp_y: Experience bar Y position
        """
        self.health_bar.set_position(health_x, health_y)
        self.experience_bar.set_position(exp_x, exp_y)
    
    def set_visible(self, visible: bool) -> None:
        """
        Set visibility of all HUD elements.
        
        Args:
            visible: Whether HUD should be visible
        """
        self.health_bar.set_visible(visible)
        self.experience_bar.set_visible(visible)
        self.status_indicator.set_visible(visible)
    
    def resize(self, screen_width: int, screen_height: int) -> None:
        """
        Resize and reposition HUD elements for new screen size.
        
        Args:
            screen_width: New screen width
            screen_height: New screen height
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Reposition status indicator to top-right
        self.status_indicator.set_position(screen_width - 150, 20)