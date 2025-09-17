"""
Map transition system for handling transitions between different maps.
Manages transition triggers, player position adjustments, and transition animations.
"""
import pygame
from typing import Dict, Any, Optional, Tuple, Callable
from enum import Enum


class TransitionType(Enum):
    """Types of map transitions."""
    BOUNDARY = "boundary"  # Triggered at map boundaries
    TRIGGER_ZONE = "trigger_zone"  # Triggered at specific zones
    DOOR = "door"  # Triggered at door objects


class TransitionDirection(Enum):
    """Direction of map transition."""
    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class MapTransition:
    """Represents a single map transition."""
    
    def __init__(self, 
                 transition_type: TransitionType,
                 target_map: str,
                 target_position: Tuple[float, float],
                 trigger_area: pygame.Rect = None,
                 direction: TransitionDirection = None):
        """
        Initialize a map transition.
        
        Args:
            transition_type: Type of transition
            target_map: Path to target map file
            target_position: Player position in target map (x, y)
            trigger_area: Area that triggers the transition (for trigger zones)
            direction: Direction of transition (for boundary transitions)
        """
        self.transition_type = transition_type
        self.target_map = target_map
        self.target_position = target_position
        self.trigger_area = trigger_area
        self.direction = direction
        self.active = True


class MapTransitionSystem:
    """Handles map transitions and animations."""
    
    def __init__(self):
        """Initialize the map transition system."""
        self.transitions: Dict[str, MapTransition] = {}
        self.current_map_path: Optional[str] = None
        self.is_transitioning = False
        self.transition_callback: Optional[Callable] = None
        
        # Animation state
        self.fade_alpha = 0
        self.fade_direction = 0  # -1 for fade out, 1 for fade in
        self.fade_speed = 255 * 2  # Fade speed (alpha per second)
        self.transition_state = "idle"  # idle, fade_out, loading, fade_in
        
        # Pending transition data
        self.pending_transition: Optional[MapTransition] = None
        
        # Cooldown to prevent immediate transitions after map load
        self.transition_cooldown = 0.0
        self.cooldown_duration = 1.0  # 1 second cooldown after map load
    
    def set_current_map(self, map_path: str) -> None:
        """
        Set the current map path.
        
        Args:
            map_path: Path to the current map file
        """
        self.current_map_path = map_path
        # Reset cooldown when setting new map
        self.transition_cooldown = self.cooldown_duration
    
    def add_boundary_transition(self, 
                              direction: TransitionDirection,
                              target_map: str,
                              target_position: Tuple[float, float]) -> None:
        """
        Add a boundary transition.
        
        Args:
            direction: Direction of the boundary
            target_map: Path to target map file
            target_position: Player position in target map
        """
        transition_id = f"boundary_{direction.value}"
        transition = MapTransition(
            TransitionType.BOUNDARY,
            target_map,
            target_position,
            direction=direction
        )
        self.transitions[transition_id] = transition
    
    def add_trigger_zone_transition(self,
                                  zone_id: str,
                                  trigger_area: pygame.Rect,
                                  target_map: str,
                                  target_position: Tuple[float, float]) -> None:
        """
        Add a trigger zone transition.
        
        Args:
            zone_id: Unique identifier for the trigger zone
            trigger_area: Rectangle defining the trigger area
            target_map: Path to target map file
            target_position: Player position in target map
        """
        transition_id = f"zone_{zone_id}"
        transition = MapTransition(
            TransitionType.TRIGGER_ZONE,
            target_map,
            target_position,
            trigger_area=trigger_area
        )
        self.transitions[transition_id] = transition
    
    def add_door_transition(self,
                           door_id: str,
                           door_position: Tuple[float, float],
                           target_map: str,
                           target_position: Tuple[float, float],
                           door_size: Tuple[float, float] = (32, 32)) -> None:
        """
        Add a door transition.
        
        Args:
            door_id: Unique identifier for the door
            door_position: Position of the door (x, y)
            target_map: Path to target map file
            target_position: Player position in target map
            door_size: Size of the door trigger area (width, height)
        """
        transition_id = f"door_{door_id}"
        door_rect = pygame.Rect(door_position[0], door_position[1], 
                               door_size[0], door_size[1])
        transition = MapTransition(
            TransitionType.DOOR,
            target_map,
            target_position,
            trigger_area=door_rect
        )
        self.transitions[transition_id] = transition
    
    def check_transitions(self, 
                         player_x: float, 
                         player_y: float,
                         map_data: Dict[str, Any]) -> Optional[MapTransition]:
        """
        Check if player position triggers any transitions.
        
        Args:
            player_x: Player X position
            player_y: Player Y position
            map_data: Current map data
            
        Returns:
            MapTransition if triggered, None otherwise
        """
        if self.is_transitioning or not map_data or self.transition_cooldown > 0:
            return None
        
        player_rect = pygame.Rect(player_x - 16, player_y - 16, 32, 32)
        
        # Check trigger zone and door transitions
        for transition in self.transitions.values():
            if not transition.active:
                continue
                
            if transition.transition_type in [TransitionType.TRIGGER_ZONE, TransitionType.DOOR]:
                if transition.trigger_area and transition.trigger_area.colliderect(player_rect):
                    return transition
        
        # Check boundary transitions
        map_width = map_data.get('width', 0) * map_data.get('tile_size', 32)
        map_height = map_data.get('height', 0) * map_data.get('tile_size', 32)
        boundary_threshold = 16  # Pixels from edge to trigger transition
        
        for transition in self.transitions.values():
            if not transition.active or transition.transition_type != TransitionType.BOUNDARY:
                continue
            
            direction = transition.direction
            if direction == TransitionDirection.NORTH and player_y <= boundary_threshold:
                return transition
            elif direction == TransitionDirection.SOUTH and player_y >= map_height - boundary_threshold:
                return transition
            elif direction == TransitionDirection.WEST and player_x <= boundary_threshold:
                return transition
            elif direction == TransitionDirection.EAST and player_x >= map_width - boundary_threshold:
                return transition
        
        return None
    
    def start_transition(self, transition: MapTransition, callback: Callable = None) -> None:
        """
        Start a map transition.
        
        Args:
            transition: The transition to execute
            callback: Callback function to call when transition completes
        """
        if self.is_transitioning:
            return
        
        print(f"Starting transition to {transition.target_map}")
        
        self.is_transitioning = True
        self.pending_transition = transition
        self.transition_callback = callback
        self.transition_state = "fade_out"
        self.fade_direction = -1
        self.fade_alpha = 0
    
    def update(self, dt: float) -> None:
        """
        Update transition animations.
        
        Args:
            dt: Delta time in seconds
        """
        # Update cooldown
        if self.transition_cooldown > 0:
            self.transition_cooldown -= dt
        
        if not self.is_transitioning:
            return
        
        if self.transition_state == "fade_out":
            self.fade_alpha += self.fade_speed * dt
            if self.fade_alpha >= 255:
                self.fade_alpha = 255
                self.transition_state = "loading"
                self._execute_transition()
        
        elif self.transition_state == "fade_in":
            self.fade_alpha -= self.fade_speed * dt
            if self.fade_alpha <= 0:
                self.fade_alpha = 0
                self.transition_state = "idle"
                self.is_transitioning = False
                self.pending_transition = None
                self.transition_callback = None
    
    def _execute_transition(self) -> None:
        """Execute the actual map transition."""
        if not self.pending_transition or not self.transition_callback:
            return
        
        # Call the callback to handle the actual map loading and player positioning
        self.transition_callback(
            self.pending_transition.target_map,
            self.pending_transition.target_position
        )
        
        # Start fade in
        self.transition_state = "fade_in"
    
    def render_transition_overlay(self, screen: pygame.Surface) -> None:
        """
        Render transition overlay (fade effect).
        
        Args:
            screen: Surface to render to
        """
        if not self.is_transitioning or self.fade_alpha <= 0:
            return
        
        # Create fade overlay
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(int(self.fade_alpha))
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
    
    def clear_transitions(self) -> None:
        """Clear all transitions."""
        self.transitions.clear()
    
    def remove_transition(self, transition_id: str) -> None:
        """
        Remove a specific transition.
        
        Args:
            transition_id: ID of transition to remove
        """
        if transition_id in self.transitions:
            del self.transitions[transition_id]
    
    def set_transition_active(self, transition_id: str, active: bool) -> None:
        """
        Enable or disable a specific transition.
        
        Args:
            transition_id: ID of transition to modify
            active: Whether transition should be active
        """
        if transition_id in self.transitions:
            self.transitions[transition_id].active = active
    
    def is_transition_active(self) -> bool:
        """
        Check if a transition is currently active.
        
        Returns:
            True if transitioning, False otherwise
        """
        return self.is_transitioning
    
    def get_transition_progress(self) -> float:
        """
        Get current transition progress.
        
        Returns:
            Progress from 0.0 to 1.0, or 0.0 if not transitioning
        """
        if not self.is_transitioning:
            return 0.0
        
        if self.transition_state == "fade_out":
            return self.fade_alpha / 255.0 * 0.5  # First half of transition
        elif self.transition_state == "loading":
            return 0.5  # Middle of transition
        elif self.transition_state == "fade_in":
            return 0.5 + (1.0 - self.fade_alpha / 255.0) * 0.5  # Second half
        
        return 0.0