"""
Game Over scene that displays when the player dies.
Provides options to restart the game or return to menu.
"""
import pygame
from typing import Optional
from .scene import Scene


class GameOverScene(Scene):
    """
    Game Over scene displayed when player health reaches 0.
    Provides restart and menu options.
    """
    
    def __init__(self):
        """Initialize the GameOverScene."""
        super().__init__("GameOverScene")
        
        # UI state
        self.selected_option = 0  # 0 = Restart, 1 = Menu
        self.options = ["Restart Game", "Main Menu"]
        
        # Colors
        self.bg_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.selected_color = (255, 255, 0)
        self.title_color = (255, 100, 100)
        
        # Fonts (will be initialized in initialize method)
        self.title_font = None
        self.option_font = None
        self.instruction_font = None
        
        # Screen dimensions
        self.screen_width = 800
        self.screen_height = 600
        
        # Animation
        self.fade_alpha = 0
        self.fade_speed = 200  # Alpha units per second
        self.max_fade = 180
    
    def initialize(self, game) -> None:
        """
        Initialize the scene with game resources.
        
        Args:
            game: Reference to the main Game instance
        """
        if self.initialized:
            return
        
        print("Initializing GameOverScene...")
        
        # Store game reference
        self.game = game
        self.screen_width, self.screen_height = game.get_screen_size()
        
        # Initialize fonts
        try:
            self.title_font = pygame.font.Font(None, 72)
            self.option_font = pygame.font.Font(None, 36)
            self.instruction_font = pygame.font.Font(None, 24)
        except pygame.error:
            # Fallback if font loading fails
            self.title_font = None
            self.option_font = None
            self.instruction_font = None
        
        self.initialized = True
        print("GameOverScene initialized successfully")
    
    def cleanup(self) -> None:
        """Clean up scene resources."""
        print("Cleaning up GameOverScene...")
        # No specific cleanup needed for this scene
        print("GameOverScene cleanup complete")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            True if event was handled
        """
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self.selected_option = (self.selected_option - 1) % len(self.options)
                return True
            
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self.selected_option = (self.selected_option + 1) % len(self.options)
                return True
            
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                self._handle_selection()
                return True
            
            elif event.key == pygame.K_ESCAPE:
                # ESC acts as selecting "Main Menu"
                self.selected_option = 1
                self._handle_selection()
                return True
        
        return False
    
    def _handle_selection(self) -> None:
        """Handle the selected menu option."""
        if self.selected_option == 0:
            # Restart Game
            self._restart_game()
        elif self.selected_option == 1:
            # Main Menu (for now, just quit the game)
            self._return_to_menu()
    
    def _restart_game(self) -> None:
        """Restart the game by creating a new GameScene."""
        print("Restarting game...")
        
        # Get scene manager
        scene_manager = self.game.get_scene_manager()
        if scene_manager:
            # Import GameScene here to avoid circular imports
            from .game_scene import GameScene
            
            # Create new game scene
            new_game_scene = GameScene()
            
            # Replace current scene with new game scene
            scene_manager.change_scene(new_game_scene)
    
    def _return_to_menu(self) -> None:
        """Return to main menu (for now, quit the game)."""
        print("Returning to main menu...")
        
        # For now, just quit the game since we don't have a main menu scene yet
        # In the future, this would switch to a MainMenuScene
        self.game.quit()
    
    def update(self, dt: float) -> None:
        """
        Update the scene state.
        
        Args:
            dt: Delta time since last frame in seconds
        """
        # Update fade-in animation
        if self.fade_alpha < self.max_fade:
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha > self.max_fade:
                self.fade_alpha = self.max_fade
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the scene to the screen.
        
        Args:
            screen: The pygame surface to render to
        """
        # Fill background with black
        screen.fill(self.bg_color)
        
        # Create semi-transparent overlay
        if self.fade_alpha > 0:
            overlay = pygame.Surface(screen.get_size())
            overlay.set_alpha(int(self.fade_alpha))
            overlay.fill((50, 0, 0))  # Dark red tint
            screen.blit(overlay, (0, 0))
        
        # Render title
        self._render_title(screen)
        
        # Render menu options
        self._render_options(screen)
        
        # Render instructions
        self._render_instructions(screen)
    
    def _render_title(self, screen: pygame.Surface) -> None:
        """Render the game over title."""
        if not self.title_font:
            return
        
        try:
            # Main title
            title_text = self.title_font.render("GAME OVER", True, self.title_color)
            title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 100))
            screen.blit(title_text, title_rect)
            
            # Subtitle
            if self.option_font:
                subtitle_text = self.option_font.render("You have fallen in battle", True, self.text_color)
                subtitle_rect = subtitle_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
                screen.blit(subtitle_text, subtitle_rect)
        
        except pygame.error:
            # Skip text rendering if it fails
            pass
    
    def _render_options(self, screen: pygame.Surface) -> None:
        """Render the menu options."""
        if not self.option_font:
            return
        
        try:
            start_y = self.screen_height // 2 + 20
            option_spacing = 50
            
            for i, option in enumerate(self.options):
                # Choose color based on selection
                color = self.selected_color if i == self.selected_option else self.text_color
                
                # Render option text
                option_text = self.option_font.render(option, True, color)
                option_rect = option_text.get_rect(center=(self.screen_width // 2, start_y + i * option_spacing))
                screen.blit(option_text, option_rect)
                
                # Render selection indicator
                if i == self.selected_option:
                    indicator_text = self.option_font.render(">", True, self.selected_color)
                    indicator_rect = indicator_text.get_rect(center=(option_rect.left - 30, option_rect.centery))
                    screen.blit(indicator_text, indicator_rect)
        
        except pygame.error:
            # Skip text rendering if it fails
            pass
    
    def _render_instructions(self, screen: pygame.Surface) -> None:
        """Render control instructions."""
        if not self.instruction_font:
            return
        
        try:
            instructions = [
                "Use UP/DOWN or W/S to navigate",
                "Press ENTER or SPACE to select",
                "Press ESC for Main Menu"
            ]
            
            start_y = self.screen_height - 100
            line_spacing = 25
            
            for i, instruction in enumerate(instructions):
                instruction_text = self.instruction_font.render(instruction, True, self.text_color)
                instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, start_y + i * line_spacing))
                screen.blit(instruction_text, instruction_rect)
        
        except pygame.error:
            # Skip text rendering if it fails
            pass
    
    def on_enter(self) -> None:
        """Called when this scene becomes active."""
        super().on_enter()
        print("Entered GameOverScene")
        
        # Reset animation state
        self.fade_alpha = 0
        self.selected_option = 0
    
    def on_exit(self) -> None:
        """Called when this scene is no longer active."""
        super().on_exit()
        print("Exited GameOverScene")
    
    def get_selected_option(self) -> int:
        """
        Get the currently selected option.
        
        Returns:
            Index of the selected option
        """
        return self.selected_option
    
    def set_selected_option(self, option: int) -> None:
        """
        Set the selected option.
        
        Args:
            option: Index of the option to select
        """
        if 0 <= option < len(self.options):
            self.selected_option = option