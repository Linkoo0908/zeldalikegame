"""
Main gameplay scene that integrates all game systems.
Handles the core game loop including player movement, combat, items, and UI.
"""
import pygame
from typing import List, Optional, Dict, Any, Tuple
from .scene import Scene
# Import systems and objects with fallback for testing
try:
    from src.systems.input_system import InputSystem
    from src.systems.map_system import MapSystem
    from src.systems.map_renderer import MapRenderer
    from src.systems.camera import Camera
    from src.systems.collision_system import CollisionSystem
    from src.systems.combat_system import CombatSystem
    from src.systems.item_system import ItemSystem
    from src.systems.inventory_system import Inventory
    from src.systems.ui_system import UIManager
    from src.systems.hud_ui import HealthBar, ExperienceBar
    from src.systems.inventory_ui import InventoryManager
    from src.systems.map_transition_system import MapTransitionSystem
    from src.systems.game_state_manager import GameStateManager
    from src.core.sprite_loader import SpriteLoader
    from src.objects.player import Player
    from src.objects.enemy import Enemy
    from src.objects.item import Item
    from src.objects.door import Door
except ImportError:
    try:
        from systems.input_system import InputSystem
        from systems.map_system import MapSystem
        from systems.map_renderer import MapRenderer
        from systems.camera import Camera
        from systems.collision_system import CollisionSystem
        from systems.combat_system import CombatSystem
        from systems.item_system import ItemSystem
        from systems.inventory_system import Inventory
        from systems.ui_system import UIManager
        from systems.hud_ui import HealthBar, ExperienceBar
        from systems.inventory_ui import InventoryManager
        from systems.map_transition_system import MapTransitionSystem
        from systems.game_state_manager import GameStateManager
        from core.sprite_loader import SpriteLoader
        from objects.player import Player
        from objects.enemy import Enemy
        from objects.item import Item
        from objects.door import Door
    except ImportError:
        # For testing - create placeholder classes
        class InputSystem: pass
        class MapSystem: pass
        class MapRenderer: pass
        class Camera: pass
        class CollisionSystem: pass
        class CombatSystem: pass
        class ItemSystem: pass
        class Inventory: pass
        class UIManager: pass
        class HealthBar: pass
        class ExperienceBar: pass
        class InventoryManager: pass
        class MapTransitionSystem: pass
        class GameStateManager: pass
        class Player: pass
        class Enemy: pass
        class Item: pass
        class Door: pass


class GameScene(Scene):
    """
    Main gameplay scene that manages all game systems and objects.
    """
    
    def __init__(self):
        """Initialize the GameScene."""
        super().__init__("GameScene")
        
        # Core systems
        self.input_system: Optional[InputSystem] = None
        self.map_system: Optional[MapSystem] = None
        self.map_renderer: Optional[MapRenderer] = None
        self.camera: Optional[Camera] = None
        self.collision_system: Optional[CollisionSystem] = None
        self.combat_system: Optional[CombatSystem] = None
        self.item_system: Optional[ItemSystem] = None
        self.ui_system: Optional[UIManager] = None
        self.map_transition_system: Optional[MapTransitionSystem] = None
        self.game_state_manager: Optional[GameStateManager] = None
        
        # Game objects
        self.player: Optional[Player] = None
        self.enemies: List[Enemy] = []
        self.items: List[Item] = []
        self.doors: List[Door] = []
        
        # Player systems
        self.inventory: Optional[Inventory] = None
        
        # UI elements
        self.health_bar: Optional[HealthBar] = None
        self.experience_bar: Optional[ExperienceBar] = None
        self.inventory_ui: Optional[InventoryManager] = None
        
        # Game state
        self.current_map_data: Optional[Dict[str, Any]] = None
        self.current_map_path: Optional[str] = None
        self.paused = False
        self.inventory_open = False
        
        # Game configuration
        self.game_config: Dict[str, Any] = {}
        
        # Stage clear system
        self.stage_cleared = False
        self.initial_enemy_count = 0
        self.doors_unlocked = False
    
    def initialize(self, game) -> None:
        """
        Initialize the scene with game resources.
        
        Args:
            game: Reference to the main Game instance
        """
        if self.initialized:
            return
        
        print("Initializing GameScene...")
        
        # Store game reference and config
        self.game = game
        self.game_config = game.config.get('game', {})
        
        # Initialize core systems
        self._initialize_systems()
        
        # Initialize game objects
        self._initialize_game_objects()
        
        # Initialize UI
        self._initialize_ui()
        
        # Load initial map
        self._load_initial_map()
        
        self.initialized = True
        print("GameScene initialized successfully")
    
    def _initialize_systems(self) -> None:
        """Initialize all game systems."""
        # Input system
        self.input_system = InputSystem()
        
        # Map systems
        self.map_system = MapSystem()
        self.map_renderer = MapRenderer(self.game.resource_manager)
        
        # Camera system
        screen_width, screen_height = self.game.get_screen_size()
        self.camera = Camera(screen_width, screen_height)
        
        # Physics and interaction systems
        self.collision_system = CollisionSystem(self.map_system)
        self.combat_system = CombatSystem()
        self.item_system = ItemSystem(self.collision_system)
        
        # UI system
        self.ui_system = UIManager()
        
        # Map transition system
        self.map_transition_system = MapTransitionSystem()
        
        # Game state manager
        self.game_state_manager = GameStateManager()
        
        # Sprite loader
        self.sprite_loader = SpriteLoader(self.game.resource_manager)
        
        print("Game systems initialized")
    
    def _initialize_game_objects(self) -> None:
        """Initialize game objects like player."""
        # Create player at safe starting position (away from doors and transitions)
        start_x = self.game_config.get('player_start_x', 160)  # Safe position away from walls and doors
        start_y = self.game_config.get('player_start_y', 160)
        self.player = Player(start_x, start_y)
        
        # Load player sprite
        if hasattr(self.player, 'load_sprite_from_loader'):
            self.player.load_sprite_from_loader(self.sprite_loader)
        
        # Initialize player inventory
        max_inventory_size = self.game_config.get('max_inventory_size', 20)
        self.inventory = Inventory(max_inventory_size)
        
        # Set player inventory reference
        if hasattr(self.player, 'set_inventory'):
            self.player.set_inventory(self.inventory)
        
        print("Game objects initialized")
    
    def _initialize_ui(self) -> None:
        """Initialize UI elements."""
        screen_width, screen_height = self.game.get_screen_size()
        
        # Health bar (top-left)
        # Create HUD layer
        hud_layer = self.ui_system.create_layer("hud", 0)
        
        self.health_bar = HealthBar(
            x=20, y=20, width=200, height=20
        )
        # Set the health values after creation
        self.health_bar.set_max_value(self.player.max_health)
        self.health_bar.set_value(self.player.current_health)
        self.ui_system.add_element_to_layer("hud", self.health_bar)
        
        # Experience bar (below health bar)
        self.experience_bar = ExperienceBar(
            x=20, y=50, width=200, height=15
        )
        # Set the experience values after creation
        self.experience_bar.set_max_value(100)  # Will be updated based on level
        self.experience_bar.set_value(self.player.experience)
        self.ui_system.add_element_to_layer("hud", self.experience_bar)
        
        # Inventory UI (initially hidden)
        self.inventory_ui = InventoryManager(
            ui_manager=self.ui_system,
            inventory=self.inventory
        )
        
        print("UI elements initialized")
    
    def _load_initial_map(self) -> None:
        """Load the initial game map."""
        try:
            # Try to load the default map
            default_map = self.game_config.get('default_map', 'assets/maps/test_map.json')
            print(f"Attempting to load map: {default_map}")
            self._load_map(default_map)
            
            print(f"Successfully loaded initial map: {default_map}")
            
        except Exception as e:
            print(f"Warning: Failed to load initial map: {e}")
            import traceback
            traceback.print_exc()
            print("Continuing with empty map")
            self.current_map_data = self._create_default_map()
            self.current_map_path = None
    
    def _create_default_map(self) -> Dict[str, Any]:
        """Create a basic default map if loading fails."""
        return {
            'width': 25,
            'height': 19,
            'tile_size': 32,
            'layers': {
                'background': [[0 for _ in range(25)] for _ in range(19)],
                'collision': [[0 for _ in range(25)] for _ in range(19)],
                'objects': []
            }
        }
    
    def _spawn_map_objects(self) -> None:
        """Spawn enemies and items from map data."""
        if not self.current_map_data:
            return
        
        objects = self.current_map_data.get('layers', {}).get('objects', [])
        
        for obj_data in objects:
            obj_type = obj_data.get('type')
            x = obj_data.get('x', 0)
            y = obj_data.get('y', 0)
            
            if obj_type == 'enemy':
                enemy_type = obj_data.get('enemy_type', 'goblin')
                # Find safe spawn position away from player
                safe_x, safe_y = self._find_safe_spawn_position(x, y)
                enemy = Enemy(safe_x, safe_y, enemy_type)
                # Load enemy sprite
                if hasattr(enemy, 'load_sprite_from_loader'):
                    enemy.load_sprite_from_loader(self.sprite_loader)
                self.enemies.append(enemy)
            
            elif obj_type == 'item':
                item_type = obj_data.get('item_type', 'health_potion')
                item = Item(x, y, item_type)
                # Load item sprite
                if hasattr(item, 'load_sprite_from_loader'):
                    item.load_sprite_from_loader(self.sprite_loader)
                self.items.append(item)
            
            elif obj_type == 'door':
                door_id = obj_data.get('door_id', f'door_{len(self.doors)}')
                target_map = obj_data.get('target_map')
                target_position = obj_data.get('target_position', [x, y])
                width = obj_data.get('width', 32)
                height = obj_data.get('height', 32)
                
                door = Door(x, y, door_id, target_map, tuple(target_position), width, height)
                self.doors.append(door)
        
        # Set initial enemy count for stage clear tracking
        self.initial_enemy_count = len(self.enemies)
        self.stage_cleared = False
        self.doors_unlocked = False
        
        print(f"Spawned {len(self.enemies)} enemies, {len(self.items)} items, and {len(self.doors)} doors")
    
    def _find_safe_spawn_position(self, preferred_x: float, preferred_y: float) -> Tuple[float, float]:
        """
        Find a safe spawn position that doesn't overlap with player.
        
        Args:
            preferred_x: Preferred X position from map data
            preferred_y: Preferred Y position from map data
            
        Returns:
            Tuple of (safe_x, safe_y) coordinates
        """
        import random
        import math
        
        if not self.player:
            return (preferred_x, preferred_y)
        
        player_x = self.player.x + self.player.width / 2
        player_y = self.player.y + self.player.height / 2
        min_distance = 100.0  # Minimum distance from player
        
        # Check if preferred position is safe
        distance = math.sqrt((preferred_x - player_x)**2 + (preferred_y - player_y)**2)
        if distance >= min_distance:
            # Check if position is not in collision
            if not self._is_position_blocked(preferred_x, preferred_y):
                return (preferred_x, preferred_y)
        
        # Find alternative safe position
        map_width = self.current_map_data.get('width', 20) * self.current_map_data.get('tile_size', 32)
        map_height = self.current_map_data.get('height', 15) * self.current_map_data.get('tile_size', 32)
        
        max_attempts = 50
        for _ in range(max_attempts):
            # Generate random position
            x = random.uniform(64, map_width - 64)  # Keep away from edges
            y = random.uniform(64, map_height - 64)
            
            # Check distance from player
            distance = math.sqrt((x - player_x)**2 + (y - player_y)**2)
            if distance >= min_distance:
                # Check if position is not blocked
                if not self._is_position_blocked(x, y):
                    return (x, y)
        
        # Fallback: use preferred position but move it away from player
        angle = math.atan2(preferred_y - player_y, preferred_x - player_x)
        safe_x = player_x + math.cos(angle) * min_distance
        safe_y = player_y + math.sin(angle) * min_distance
        
        # Clamp to map bounds
        safe_x = max(32, min(map_width - 32, safe_x))
        safe_y = max(32, min(map_height - 32, safe_y))
        
        return (safe_x, safe_y)
    
    def _is_position_blocked(self, x: float, y: float) -> bool:
        """
        Check if a position is blocked by collision tiles.
        
        Args:
            x: X coordinate to check
            y: Y coordinate to check
            
        Returns:
            True if position is blocked, False otherwise
        """
        if not self.collision_system or not self.current_map_data:
            return False
        
        # Create temporary object to test collision
        test_rect = pygame.Rect(x, y, 32, 32)
        
        # Check collision with map
        tile_x, tile_y = self.map_system.world_to_tile(x, y)
        return self.map_system.is_tile_solid(tile_x, tile_y)
    
    def _load_map(self, map_path: str) -> None:
        """
        Load a specific map and set up all related systems.
        
        Args:
            map_path: Path to the map file to load
        """
        # Load map data
        self.current_map_data = self.map_system.load_map(map_path)
        self.current_map_path = map_path
        
        # Set current map in systems
        self.map_system.set_current_map(self.current_map_data)
        self.map_transition_system.set_current_map(map_path)
        
        # Map renderer will use map data directly in render calls
        
        # Update camera bounds based on map size
        if self.current_map_data:
            map_width = self.current_map_data.get('width', 20) * self.current_map_data.get('tile_size', 32)
            map_height = self.current_map_data.get('height', 15) * self.current_map_data.get('tile_size', 32)
            self.camera.set_bounds(0, 0, map_width, map_height)
        
        # Clear existing objects
        self.enemies.clear()
        self.items.clear()
        self.doors.clear()
        
        # Spawn new objects from map data
        self._spawn_map_objects()
        
        # Set up map transitions from map data
        self._setup_map_transitions()
    
    def _setup_map_transitions(self) -> None:
        """Set up map transitions based on current map data."""
        if not self.current_map_data:
            return
        
        # Clear existing transitions
        self.map_transition_system.clear_transitions()
        
        # Get transitions from map data
        transitions = self.current_map_data.get('transitions', {})
        
        # Set up boundary transitions
        boundaries = transitions.get('boundaries', {})
        for direction, transition_data in boundaries.items():
            if direction in ['north', 'south', 'east', 'west']:
                try:
                    from src.systems.map_transition_system import TransitionDirection
                except ImportError:
                    from systems.map_transition_system import TransitionDirection
                direction_enum = getattr(TransitionDirection, direction.upper())
                self.map_transition_system.add_boundary_transition(
                    direction_enum,
                    transition_data['target_map'],
                    tuple(transition_data['target_position'])
                )
        
        # Set up trigger zone transitions
        zones = transitions.get('zones', [])
        for zone in zones:
            trigger_area = pygame.Rect(
                zone['area']['x'], zone['area']['y'],
                zone['area']['width'], zone['area']['height']
            )
            self.map_transition_system.add_trigger_zone_transition(
                zone['id'],
                trigger_area,
                zone['target_map'],
                tuple(zone['target_position'])
            )
        
        # Set up door transitions
        doors = transitions.get('doors', [])
        for door in doors:
            self.map_transition_system.add_door_transition(
                door['id'],
                tuple(door['position']),
                door['target_map'],
                tuple(door['target_position']),
                tuple(door.get('size', [32, 32]))
            )
    
    def _handle_map_transition(self, target_map: str, target_position: Tuple[float, float]) -> None:
        """
        Handle a map transition.
        
        Args:
            target_map: Path to the target map
            target_position: Target position for the player
        """
        try:
            print(f"Transitioning to map: {target_map}")
            
            # Save current map state before transitioning
            self._save_current_map_state()
            
            # Load the new map
            self._load_map(target_map)
            
            # Try to restore saved state for the target map
            self._restore_map_state(target_map)
            
            # Move player to target position
            if self.player:
                self.player.x, self.player.y = target_position
                print(f"Player moved to position: {target_position}")
            
            # Update camera to follow player immediately
            if self.camera and self.player:
                self.camera.set_position(self.player.x, self.player.y)
            
            # Track map visit
            if self.game_state_manager:
                visit_count = self.game_state_manager.increment_map_visit(target_map)
                print(f"Map visit count: {visit_count}")
            
        except Exception as e:
            print(f"Error during map transition: {e}")
            # Could implement fallback behavior here
    
    def _save_current_map_state(self) -> None:
        """Save the current map state (enemies, items, player data)."""
        if not self.current_map_path or not self.map_system:
            return
        
        try:
            # Convert enemies to serializable data
            enemy_data = []
            for enemy in self.enemies:
                enemy_data.append({
                    'x': enemy.x,
                    'y': enemy.y,
                    'enemy_type': getattr(enemy, 'enemy_type', 'unknown'),
                    'current_health': getattr(enemy, 'current_health', 100),
                    'max_health': getattr(enemy, 'max_health', 100)
                })
            
            # Convert items to serializable data
            item_data = []
            for item in self.items:
                item_data.append({
                    'x': item.x,
                    'y': item.y,
                    'item_type': getattr(item, 'item_type', 'unknown')
                })
            
            # Save player state
            player_data = None
            if self.player and self.game_state_manager:
                self.game_state_manager.save_player_state(self.player)
                if self.inventory:
                    self.game_state_manager.save_inventory_state(self.inventory)
                player_data = self.game_state_manager.player_state.copy()
            
            # Save to map system
            self.map_system.save_map_state(self.current_map_path, enemy_data, item_data, player_data)
            
            print(f"Saved state for map: {self.current_map_path}")
            print(f"  Enemies: {len(enemy_data)}, Items: {len(item_data)}")
            
        except Exception as e:
            print(f"Error saving map state: {e}")
    
    def _restore_map_state(self, map_path: str) -> None:
        """
        Restore saved state for a map.
        
        Args:
            map_path: Path to the map to restore state for
        """
        if not self.map_system:
            return
        
        try:
            saved_state = self.map_system.load_map_state(map_path)
            if not saved_state:
                print(f"No saved state found for map: {map_path}")
                return
            
            print(f"Restoring state for map: {map_path}")
            
            # Clear current objects
            self.enemies.clear()
            self.items.clear()
            
            # Restore enemies
            enemy_data = saved_state.get('enemies', [])
            for enemy_info in enemy_data:
                try:
                    from src.objects.enemy import Enemy
                    enemy = Enemy(
                        enemy_info['x'], 
                        enemy_info['y'], 
                        enemy_info.get('enemy_type', 'goblin')
                    )
                    # Load enemy sprite
                    if hasattr(enemy, 'load_sprite_from_loader'):
                        enemy.load_sprite_from_loader(self.sprite_loader)
                    if hasattr(enemy, 'current_health'):
                        enemy.current_health = enemy_info.get('current_health', 100)
                    if hasattr(enemy, 'max_health'):
                        enemy.max_health = enemy_info.get('max_health', 100)
                    self.enemies.append(enemy)
                except ImportError:
                    # Fallback for testing
                    pass
            
            # Restore items
            item_data = saved_state.get('items', [])
            for item_info in item_data:
                try:
                    from src.objects.item import Item
                    item = Item(
                        item_info['x'], 
                        item_info['y'], 
                        item_info.get('item_type', 'health_potion')
                    )
                    self.items.append(item)
                except ImportError:
                    # Fallback for testing
                    pass
            
            print(f"Restored {len(self.enemies)} enemies and {len(self.items)} items")
            
            # Note: Player state is handled separately and doesn't need to be restored here
            # since the player object persists across map transitions
            
        except Exception as e:
            print(f"Error restoring map state: {e}")
            # Fall back to spawning from map data
            self._spawn_map_objects()
    
    def cleanup(self) -> None:
        """Clean up scene resources."""
        print("Cleaning up GameScene...")
        
        # Clear object lists
        self.enemies.clear()
        self.items.clear()
        self.doors.clear()
        
        # Clear UI elements
        if self.ui_system:
            self.ui_system.clear_all_layers()
        
        # Clear map cache
        if self.map_system:
            self.map_system.clear_cache()
        
        print("GameScene cleanup complete")
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """
        Handle pygame events.
        
        Args:
            event: The pygame event to handle
            
        Returns:
            True if event was handled
        """
        if event.type == pygame.KEYDOWN:
            # Toggle inventory
            if event.key == pygame.K_i:
                self._toggle_inventory()
                return True
            
            # Pause/unpause game
            elif event.key == pygame.K_p:
                self.paused = not self.paused
                return True
        
        # Pass event to UI system if inventory is open
        if self.inventory_open and self.ui_system:
            return self.ui_system.handle_event(event)
        
        return False
    
    def _toggle_inventory(self) -> None:
        """Toggle inventory UI visibility."""
        self.inventory_open = not self.inventory_open
        if self.inventory_ui:
            self.inventory_ui.visible = self.inventory_open
        
        print(f"Inventory {'opened' if self.inventory_open else 'closed'}")
    
    def _check_stage_clear(self) -> None:
        """Check if stage is cleared (all enemies defeated) and unlock doors."""
        if self.stage_cleared or self.doors_unlocked:
            return
        
        # Check if all enemies are defeated
        if self.initial_enemy_count > 0 and len(self.enemies) == 0:
            self.stage_cleared = True
            self.doors_unlocked = True
            
            print("🎉 Stage Cleared! All enemies defeated!")
            print("🚪 Doors are now unlocked!")
            
            # Unlock all doors
            for door in self.doors:
                door.unlock()
    
    def _handle_door_interactions(self) -> None:
        """Handle player interactions with doors."""
        if not self.player:
            return
        
        # Check for E key press to interact with doors
        keys = pygame.key.get_pressed()
        if keys[pygame.K_e]:
            for door in self.doors:
                if door.can_interact and not door.is_locked:
                    if door.try_interact(self.player):
                        # Door opened, check if we should transition
                        if door.target_map and door.can_pass_through():
                            self._initiate_door_transition(door)
                        break
    
    def _initiate_door_transition(self, door: Door) -> None:
        """
        Initiate transition through a door.
        
        Args:
            door: Door object to transition through
        """
        if not door.target_map:
            return
        
        print(f"🚪 Entering door {door.door_id} to {door.target_map}")
        
        # Use the map transition system for smooth transition
        if self.map_transition_system:
            # Create a temporary transition for the door
            from src.systems.map_transition_system import MapTransition, TransitionType
            door_transition = MapTransition(
                TransitionType.DOOR,
                door.target_map,
                door.target_position
            )
            
            self.map_transition_system.start_transition(
                door_transition,
                self._handle_map_transition
            )
    
    def update(self, dt: float) -> None:
        """
        Update the scene state.
        
        Args:
            dt: Delta time since last frame in seconds
        """
        if self.paused:
            return
        
        # Track playtime
        if self.game_state_manager:
            self.game_state_manager.add_playtime(dt)
        
        # Update input system
        if self.input_system:
            self.input_system.update()
        
        # Update player
        if self.player and self.input_system:
            self.player.handle_input(self.input_system)
            self.player.update(dt)
            
            # Handle map collisions
            if self.collision_system and self.current_map_data:
                # Check if player would collide with map at new position
                old_x, old_y = self.player.x, self.player.y
                if self.collision_system.check_map_collision(self.player, self.player.x, self.player.y):
                    # Resolve collision by moving player back
                    self.player.x, self.player.y = self.collision_system.resolve_map_collision(
                        self.player, old_x, old_y, self.player.x, self.player.y
                    )
        
        # Update camera to follow player
        if self.camera and self.player:
            self.camera.follow_target(self.player.x, self.player.y, dt)
        
        # Check for map transitions
        if self.map_transition_system and self.player and self.current_map_data:
            transition = self.map_transition_system.check_transitions(
                self.player.x, self.player.y, self.current_map_data
            )
            if transition:
                self.map_transition_system.start_transition(
                    transition, 
                    self._handle_map_transition
                )
        
        # Update enemies
        for enemy in self.enemies[:]:  # Use slice to allow removal during iteration
            enemy.update(dt)
            
            # Update enemy AI and movement
            if self.player:
                enemy.update(dt, (self.player.x, self.player.y))
            else:
                enemy.update(dt)
            
            # Handle enemy-map collisions
            if self.collision_system and self.current_map_data:
                # Check if enemy would collide with map at new position
                old_x, old_y = enemy.x, enemy.y
                if self.collision_system.check_map_collision(enemy, enemy.x, enemy.y):
                    # Resolve collision by moving enemy back
                    enemy.x, enemy.y = self.collision_system.resolve_map_collision(
                        enemy, old_x, old_y, enemy.x, enemy.y
                    )
        
        # Update combat system
        if self.combat_system and self.player:
            # Sync enemies with combat system
            self.combat_system.active_enemies = self.enemies[:]
            
            # Update combat system (handles all combat interactions)
            self.combat_system.update(dt, self.player)
            
            # Remove dead enemies
            for enemy in self.enemies[:]:
                if enemy.current_health <= 0:
                    self.enemies.remove(enemy)
                    self.combat_system.remove_enemy(enemy)
                        # Could spawn items or give experience here
            
            # Enemy attacks are handled in combat_system.update() above
        
        # Check for stage clear condition (all enemies defeated)
        self._check_stage_clear()
        
        # Update doors
        player_pos = (self.player.x, self.player.y) if self.player else None
        for door in self.doors:
            door.update(dt, player_pos)
        
        # Handle door interactions
        self._handle_door_interactions()
        
        # Update item system
        if self.item_system and self.player:
            # Sync items with item system
            self.item_system.items = self.items[:]
            
            # Update item system (handles collection)
            self.item_system.update(dt, self.player)
            
            # Remove collected items
            for item in self.items[:]:
                if not item.active:
                    self.items.remove(item)
                    print(f"Collected {item.item_type}")
        
        # Check for game over condition
        if self.player and self.player.current_health <= 0:
            self._trigger_game_over()
            return  # Don't continue updating if game over
        
        # Update map transition system
        if self.map_transition_system:
            self.map_transition_system.update(dt)
        
        # Update UI elements
        if self.ui_system:
            self.ui_system.update(dt)
            
            # Update health bar
            if self.health_bar:
                self.health_bar.set_value(self.player.current_health)
            
            # Update experience bar
            if self.experience_bar:
                self.experience_bar.set_value(self.player.experience)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the scene to the screen.
        
        Args:
            screen: The pygame surface to render to
        """
        # Clear screen with background color
        screen.fill((50, 50, 50))  # Dark gray background
        
        # Render map background layer
        if self.map_renderer and self.camera and self.current_map_data:
            self.map_renderer.render_map(screen, self.current_map_data, self.camera, 'background')
        
        # Get camera offset
        camera_x, camera_y = 0, 0
        if self.camera:
            camera_x, camera_y = self.camera.get_offset()
        
        # Render items
        for item in self.items:
            item.render(screen, camera_x, camera_y)
        
        # Render doors
        for door in self.doors:
            door.render(screen, camera_x, camera_y)
        
        # Render enemies
        for enemy in self.enemies:
            enemy.render(screen, camera_x, camera_y)
        
        # Render player
        if self.player:
            self.player.render(screen, camera_x, camera_y)
        
        # Render map foreground/overlay layers if they exist
        if self.map_renderer and self.camera and self.current_map_data:
            # Check if there are additional layers to render on top
            layers = self.current_map_data.get('layers', {})
            if 'foreground' in layers:
                self.map_renderer.render_map(screen, self.current_map_data, self.camera, 'foreground')
        
        # Render UI
        if self.ui_system:
            self.ui_system.render(screen)
        
        # Render map transition overlay
        if self.map_transition_system:
            self.map_transition_system.render_transition_overlay(screen)
        
        # Render pause overlay
        if self.paused:
            self._render_pause_overlay(screen)
    
    def _render_pause_overlay(self, screen: pygame.Surface) -> None:
        """Render pause overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface(screen.get_size())
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Pause text
        try:
            font = pygame.font.Font(None, 48)
            text = font.render("PAUSED", True, (255, 255, 255))
            text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
            screen.blit(text, text_rect)
            
            # Instructions
            font_small = pygame.font.Font(None, 24)
            instruction = font_small.render("Press P to resume", True, (200, 200, 200))
            instruction_rect = instruction.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 50))
            screen.blit(instruction, instruction_rect)
        except pygame.error:
            pass  # Skip text rendering if font fails
    
    def on_enter(self) -> None:
        """Called when this scene becomes active."""
        super().on_enter()
        print("Entered GameScene")
    
    def on_exit(self) -> None:
        """Called when this scene is no longer active."""
        super().on_exit()
        print("Exited GameScene")
    
    def on_pause(self) -> None:
        """Called when this scene is paused."""
        super().on_pause()
        print("GameScene paused")
    
    def on_resume(self) -> None:
        """Called when this scene is resumed."""
        super().on_resume()
        print("GameScene resumed")
    
    def get_player(self) -> Optional[Player]:
        """Get the player object."""
        return self.player
    
    def get_enemies(self) -> List[Enemy]:
        """Get the list of enemies."""
        return self.enemies.copy()
    
    def get_items(self) -> List[Item]:
        """Get the list of items."""
        return self.items.copy()
    
    def add_enemy(self, enemy: Enemy) -> None:
        """Add an enemy to the scene."""
        self.enemies.append(enemy)
    
    def add_item(self, item: Item) -> None:
        """Add an item to the scene."""
        self.items.append(item)
    
    def remove_enemy(self, enemy: Enemy) -> None:
        """Remove an enemy from the scene."""
        if enemy in self.enemies:
            self.enemies.remove(enemy)
    
    def remove_item(self, item: Item) -> None:
        """Remove an item from the scene."""
        if item in self.items:
            self.items.remove(item)
    
    def _trigger_game_over(self) -> None:
        """Trigger the game over sequence."""
        print("Player has died - triggering game over")
        
        # Get scene manager
        scene_manager = self.game.get_scene_manager()
        if scene_manager:
            # Import GameOverScene here to avoid circular imports
            from .game_over_scene import GameOverScene
            
            # Create and push game over scene
            game_over_scene = GameOverScene()
            scene_manager.push_scene(game_over_scene)