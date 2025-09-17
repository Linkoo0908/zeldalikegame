"""
Main Game class that handles the game loop, initialization, and core systems.
Manages Pygame initialization, event handling, FPS control, and delta time calculation.
"""
import pygame
import sys
import json
from pathlib import Path
from typing import Optional
from .resource_manager import ResourceManager
from scenes.scene_manager import SceneManager


class Game:
    """
    Main Game class that manages the game loop and core systems.
    Handles Pygame initialization, event processing, FPS control, and delta time.
    """
    
    def __init__(self, config_path: str = "config/settings.json"):
        """
        Initialize the Game instance.
        
        Args:
            config_path: Path to the game configuration file
        """
        self.running = False
        self.clock = pygame.time.Clock()
        self.screen: Optional[pygame.Surface] = None
        self.resource_manager: Optional[ResourceManager] = None
        self.scene_manager: Optional[SceneManager] = None
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Display settings
        self.screen_width = self.config.get("display", {}).get("width", 800)
        self.screen_height = self.config.get("display", {}).get("height", 600)
        self.window_title = self.config.get("display", {}).get("title", "Zelda-like 2D Game")
        self.target_fps = self.config.get("display", {}).get("fps", 60)
        
        # Game state
        self.delta_time = 0.0
        self.last_frame_time = 0
        
        # Initialize Pygame and systems
        self._initialize_pygame()
        self._initialize_systems()
    
    def _load_config(self, config_path: str) -> dict:
        """
        Load game configuration from JSON file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dictionary containing configuration data
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Failed to load config from {config_path}: {e}")
            print("Using default configuration.")
            return {
                "display": {
                    "width": 800,
                    "height": 600,
                    "title": "Zelda-like 2D Game",
                    "fps": 60
                },
                "game": {
                    "tile_size": 32,
                    "player_speed": 100,
                    "debug_mode": False
                }
            }
    
    def _initialize_pygame(self) -> None:
        """Initialize Pygame and create the main window."""
        try:
            pygame.init()
            pygame.mixer.init()
            
            # Create the main window
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            pygame.display.set_caption(self.window_title)
            
            print(f"Pygame initialized successfully")
            print(f"Window: {self.screen_width}x{self.screen_height}")
            print(f"Target FPS: {self.target_fps}")
            
        except pygame.error as e:
            print(f"Failed to initialize Pygame: {e}")
            sys.exit(1)
    
    def _initialize_systems(self) -> None:
        """Initialize game systems like resource manager and scene manager."""
        try:
            self.resource_manager = ResourceManager()
            self.scene_manager = SceneManager(self)
            
            # Start with the main game scene
            self._start_initial_scene()
            
            print("Game systems initialized successfully")
        except Exception as e:
            print(f"Failed to initialize game systems: {e}")
            sys.exit(1)
    
    def _start_initial_scene(self) -> None:
        """Start the game with the initial scene."""
        try:
            from scenes.game_scene import GameScene
            initial_scene = GameScene()
            self.scene_manager.push_scene(initial_scene)
            print("Initial game scene started")
        except Exception as e:
            print(f"Failed to start initial scene: {e}")
            # Don't exit here, let the game run without scenes for now
    
    def run(self) -> None:
        """
        Main game loop.
        Handles events, updates game state, and renders everything.
        """
        print("Starting game loop...")
        self.running = True
        self.last_frame_time = pygame.time.get_ticks()
        
        while self.running:
            # Calculate delta time
            current_time = pygame.time.get_ticks()
            self.delta_time = (current_time - self.last_frame_time) / 1000.0  # Convert to seconds
            self.last_frame_time = current_time
            
            # Handle events
            self.handle_events()
            
            # Update game state
            self.update(self.delta_time)
            
            # Render everything
            self.render()
            
            # Control frame rate
            self.clock.tick(self.target_fps)
        
        # Cleanup
        self.cleanup()
    
    def handle_events(self) -> None:
        """
        Handle all pygame events.
        Processes quit events and passes events to scene manager.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                self._handle_keydown(event)
            
            elif event.type == pygame.KEYUP:
                self._handle_keyup(event)
            
            # Pass event to scene manager
            if self.scene_manager:
                self.scene_manager.handle_event(event)
    
    def _handle_keydown(self, event: pygame.event.Event) -> None:
        """
        Handle key press events.
        
        Args:
            event: Pygame keydown event
        """
        if event.key == pygame.K_ESCAPE:
            self.running = False
        
        # Debug information toggle
        elif event.key == pygame.K_F1:
            debug_mode = self.config.get("game", {}).get("debug_mode", False)
            self.config["game"]["debug_mode"] = not debug_mode
            print(f"Debug mode: {'ON' if not debug_mode else 'OFF'}")
    
    def _handle_keyup(self, event: pygame.event.Event) -> None:
        """
        Handle key release events.
        
        Args:
            event: Pygame keyup event
        """
        # Key release handling will be expanded in later tasks
        pass
    
    def update(self, dt: float) -> None:
        """
        Update game state.
        
        Args:
            dt: Delta time since last frame in seconds
        """
        # Update scene manager
        if self.scene_manager:
            self.scene_manager.update(dt)
    
    def render(self) -> None:
        """Render the game to the screen."""
        # Clear screen with black background
        self.screen.fill((0, 0, 0))
        
        # Render current scene
        if self.scene_manager and self.scene_manager.has_scenes():
            self.scene_manager.render(self.screen)
        else:
            # Render placeholder if no scene is active
            self._render_placeholder()
        
        # Render debug information if enabled
        if self.config.get("game", {}).get("debug_mode", False):
            self._render_debug_info()
        
        # Update display
        pygame.display.flip()
    
    def _render_debug_info(self) -> None:
        """Render debug information on screen."""
        try:
            font = pygame.font.Font(None, 24)
            
            # FPS information
            fps = self.clock.get_fps()
            fps_text = font.render(f"FPS: {fps:.1f}", True, (255, 255, 255))
            self.screen.blit(fps_text, (10, 10))
            
            # Delta time information
            dt_text = font.render(f"Delta Time: {self.delta_time:.4f}s", True, (255, 255, 255))
            self.screen.blit(dt_text, (10, 35))
            
            # Resource cache info
            if self.resource_manager:
                cache_info = self.resource_manager.get_cache_info()
                cache_text = font.render(f"Cache: {cache_info}", True, (255, 255, 255))
                self.screen.blit(cache_text, (10, 60))
            
            # Scene info
            if self.scene_manager:
                scene_count = self.scene_manager.get_scene_count()
                current_scene = self.scene_manager.get_current_scene()
                scene_name = current_scene.get_name() if current_scene else "None"
                scene_text = font.render(f"Scene: {scene_name} ({scene_count} total)", True, (255, 255, 255))
                self.screen.blit(scene_text, (10, 85))
            
        except pygame.error:
            # If font rendering fails, just skip debug info
            pass
    
    def _render_placeholder(self) -> None:
        """Render placeholder content while game systems are being developed."""
        try:
            font = pygame.font.Font(None, 48)
            title_text = font.render("Zelda-like 2D Game", True, (255, 255, 255))
            title_rect = title_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 - 50))
            self.screen.blit(title_text, title_rect)
            
            font_small = pygame.font.Font(None, 24)
            instruction_text = font_small.render("Press ESC to quit, F1 for debug info", True, (200, 200, 200))
            instruction_rect = instruction_text.get_rect(center=(self.screen_width // 2, self.screen_height // 2 + 20))
            self.screen.blit(instruction_text, instruction_rect)
            
        except pygame.error:
            # If font rendering fails, just skip placeholder
            pass
    
    def cleanup(self) -> None:
        """Clean up resources and quit pygame."""
        print("Cleaning up and shutting down...")
        
        # Clean up scene manager
        if self.scene_manager:
            self.scene_manager.cleanup()
        
        # Clear resource caches
        if self.resource_manager:
            self.resource_manager.clear_cache()
        
        # Quit pygame
        pygame.quit()
        print("Game shutdown complete.")
    
    def get_screen_size(self) -> tuple:
        """
        Get the current screen dimensions.
        
        Returns:
            Tuple of (width, height)
        """
        return (self.screen_width, self.screen_height)
    
    def get_delta_time(self) -> float:
        """
        Get the current delta time.
        
        Returns:
            Delta time in seconds
        """
        return self.delta_time
    
    def get_fps(self) -> float:
        """
        Get the current FPS.
        
        Returns:
            Current frames per second
        """
        return self.clock.get_fps()
    
    def is_running(self) -> bool:
        """
        Check if the game is currently running.
        
        Returns:
            True if game is running, False otherwise
        """
        return self.running
    
    def quit(self) -> None:
        """Request the game to quit gracefully."""
        self.running = False
    
    def get_scene_manager(self) -> Optional[SceneManager]:
        """
        Get the scene manager instance.
        
        Returns:
            The scene manager, or None if not initialized
        """
        return self.scene_manager
    
    def get_resource_manager(self) -> Optional[ResourceManager]:
        """
        Get the resource manager instance.
        
        Returns:
            The resource manager, or None if not initialized
        """
        return self.resource_manager