"""
Player class for the main character controlled by the user.
"""
import pygame
import json
from typing import Tuple, Optional
from .game_object import GameObject
# InputSystem will be passed as parameter, no need to import


class Player(GameObject):
    """
    Player character class that handles user input and movement.
    """
    
    def __init__(self, x: float, y: float, settings_file: str = "config/settings.json"):
        """
        Initialize the Player.
        
        Args:
            x: Starting X position
            y: Starting Y position
            settings_file: Path to settings configuration file
        """
        super().__init__(x, y, 32, 32)  # Default 32x32 size
        
        # Load settings
        self.settings = self._load_settings(settings_file)
        
        # Player stats
        self.max_health = 100
        self.current_health = self.max_health
        self.base_speed = self.settings.get('game', {}).get('player_speed', 100)
        self.speed = self.base_speed
        self.level = 1
        self.experience = 0
        
        # Movement state
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.facing_direction = 'down'  # Default facing direction
        self.last_facing_direction = 'down'
        
        # Movement boundaries (will be set by game/scene)
        self.boundary_left = 0
        self.boundary_right = 800  # Default screen width
        self.boundary_top = 0
        self.boundary_bottom = 600  # Default screen height
        
        # Animation state
        self.animation_time = 0.0
        self.animation_frame = 0
        self.animation_speed = 0.15  # Time per animation frame
        self.max_animation_frames = 4
        self.is_moving = False
        
        # Attack state
        self.is_attacking = False
        self.attack_time = 0.0
        self.attack_duration = 0.3  # Attack animation duration in seconds
        self.attack_cooldown = 0.5  # Cooldown between attacks
        self.last_attack_time = 0.0
        self.attack_damage = 20  # Base attack damage
        self.attack_range = 40  # Attack range in pixels
        
        # Direction-specific sprites
        self.direction_sprites = {}
        self._create_direction_sprites()
        
        # Inventory
        from src.systems.inventory_system import Inventory
        self.inventory = Inventory(max_size=20)
        
        # Status effects and temporary bonuses
        self.status_effects = {}  # Dictionary of active status effects
        self.temporary_attack_bonus = 0
        self.temporary_speed_multiplier = 1.0
        self.health_regen_rate = 0  # Health regeneration per second
    
    def _load_settings(self, settings_file: str) -> dict:
        """
        Load settings from JSON file.
        
        Args:
            settings_file: Path to settings file
            
        Returns:
            Dictionary containing settings
        """
        try:
            with open(settings_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load settings file {settings_file}: {e}")
            return {
                'game': {
                    'player_speed': 100,
                    'tile_size': 32
                }
            }
    
    def _create_default_sprite(self):
        """Create a default sprite for the player (colored rectangle)."""
        self.sprite = pygame.Surface((self.width, self.height))
        self.sprite.fill((0, 100, 200))  # Blue color for player
        
        # Add a simple face to distinguish direction
        pygame.draw.circle(self.sprite, (255, 255, 255), (8, 8), 3)  # Left eye
        pygame.draw.circle(self.sprite, (255, 255, 255), (24, 8), 3)  # Right eye
        pygame.draw.circle(self.sprite, (255, 255, 255), (16, 20), 5)  # Mouth
    
    def _create_direction_sprites(self):
        """Create sprites for each direction."""
        # Create base sprite
        self._create_default_sprite()
        
        # Create direction-specific sprites
        for direction in ['up', 'down', 'left', 'right']:
            self.direction_sprites[direction] = self._create_directional_sprite(direction)
    
    def load_sprite_from_loader(self, sprite_loader) -> None:
        """
        Load player sprite using sprite loader.
        
        Args:
            sprite_loader: SpriteLoader instance
        """
        loaded_sprite = sprite_loader.load_player_sprite(self.width, self.height)
        if loaded_sprite:
            self.sprite = loaded_sprite
            # Update direction sprites to use the loaded sprite as base
            for direction in ['up', 'down', 'left', 'right']:
                self.direction_sprites[direction] = loaded_sprite.copy()
    
    def _create_directional_sprite(self, direction: str) -> pygame.Surface:
        """
        Create a sprite for a specific direction.
        
        Args:
            direction: Direction to create sprite for
            
        Returns:
            Pygame surface for the direction
        """
        sprite = pygame.Surface((self.width, self.height))
        sprite.fill((0, 100, 200))  # Blue base color
        
        # Draw direction-specific features
        if direction == 'up':
            # Eyes at top, mouth below
            pygame.draw.circle(sprite, (255, 255, 255), (8, 6), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (24, 6), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (16, 16), 3)
        elif direction == 'down':
            # Eyes in middle, mouth at bottom
            pygame.draw.circle(sprite, (255, 255, 255), (8, 8), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (24, 8), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (16, 20), 5)
        elif direction == 'left':
            # Eyes on left side
            pygame.draw.circle(sprite, (255, 255, 255), (6, 8), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (6, 16), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (16, 12), 3)
        elif direction == 'right':
            # Eyes on right side
            pygame.draw.circle(sprite, (255, 255, 255), (26, 8), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (26, 16), 3)
            pygame.draw.circle(sprite, (255, 255, 255), (16, 12), 3)
        
        return sprite
    
    def handle_input(self, input_system) -> None:
        """
        Handle player input and update movement.
        
        Args:
            input_system: InputSystem instance to get input from
        """
        # Get movement vector from input system
        movement_x, movement_y = input_system.get_movement_vector()
        
        # Apply speed modifiers (could be affected by items, status effects, etc.)
        current_speed = self._get_current_speed()
        
        # Update velocity based on input with speed control
        self.velocity_x = movement_x * current_speed
        self.velocity_y = movement_y * current_speed
        
        # Update facing direction and movement state
        if movement_x != 0 or movement_y != 0:
            self.is_moving = True
            new_direction = input_system.get_movement_direction()
            if new_direction != 'idle':
                self.facing_direction = new_direction
                self.last_facing_direction = new_direction
        else:
            self.is_moving = False
        
        # Handle action inputs
        if input_system.is_action_just_pressed('attack'):
            self.attack()
        
        if input_system.is_action_just_pressed('interact'):
            self.interact()
    
    def _get_current_speed(self) -> float:
        """
        Get the current movement speed, accounting for modifiers.
        
        Returns:
            Current movement speed
        """
        # Base speed can be modified by items, status effects, etc.
        speed_modifier = 1.0
        
        # Example: could add speed boosts, slowdowns, etc.
        # if self.has_speed_boost:
        #     speed_modifier *= 1.5
        # if self.is_slowed:
        #     speed_modifier *= 0.5
        
        return self.base_speed * speed_modifier
    
    def update(self, dt: float) -> None:
        """
        Update the player state.
        
        Args:
            dt: Delta time since last frame in seconds
        """
        # Update status effects
        self.update_status_effects(dt)
        
        # Update attack state
        self._update_attack_state(dt)
        
        # Only move if not attacking (or allow movement during attack)
        if not self.is_attacking:
            # Calculate new position
            new_x = self.x + self.velocity_x * dt
            new_y = self.y + self.velocity_y * dt
            
            # Apply boundary checking
            new_x, new_y = self._apply_boundary_constraints(new_x, new_y)
            
            # Update position
            self.x = new_x
            self.y = new_y
        
        # Update animation
        self._update_animation(dt)
    
    def _apply_boundary_constraints(self, new_x: float, new_y: float) -> Tuple[float, float]:
        """
        Apply boundary constraints to prevent player from moving outside allowed area.
        
        Args:
            new_x: Proposed new X position
            new_y: Proposed new Y position
            
        Returns:
            Tuple of constrained (x, y) position
        """
        # Constrain X position
        constrained_x = max(self.boundary_left, 
                           min(new_x, self.boundary_right - self.width))
        
        # Constrain Y position
        constrained_y = max(self.boundary_top, 
                           min(new_y, self.boundary_bottom - self.height))
        
        return (constrained_x, constrained_y)
    
    def _update_animation(self, dt: float) -> None:
        """
        Update animation state.
        
        Args:
            dt: Delta time since last frame
        """
        if self.is_moving:
            self.animation_time += dt
            # Change frame based on animation speed
            if self.animation_time >= self.animation_speed:
                self.animation_frame = (self.animation_frame + 1) % self.max_animation_frames
                self.animation_time = 0.0
        else:
            # Reset animation when not moving
            self.animation_frame = 0
            self.animation_time = 0.0
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """
        Render the player to the screen.
        
        Args:
            screen: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if not self.active or not self.sprite:
            return
        
        # Convert world coordinates to screen coordinates
        screen_x = int(self.x - camera_x)
        screen_y = int(self.y - camera_y)
        
        # Create animated sprite based on movement and attack state
        animated_sprite = self._get_animated_sprite()
        
        # Only render if player is visible on screen
        if (screen_x + self.width >= 0 and screen_x < screen.get_width() and
            screen_y + self.height >= 0 and screen_y < screen.get_height()):
            screen.blit(animated_sprite, (screen_x, screen_y))
            
            # Render attack visualization if attacking
            if self.is_attacking:
                self._render_attack_effect(screen, camera_x, camera_y)
    
    def _render_attack_effect(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """
        Render attack effect visualization.
        
        Args:
            screen: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        attack_rect = self.get_attack_rect()
        
        # Convert attack rect to screen coordinates
        screen_attack_rect = pygame.Rect(
            attack_rect.x - camera_x,
            attack_rect.y - camera_y,
            attack_rect.width,
            attack_rect.height
        )
        
        # Calculate attack effect intensity based on attack time
        attack_progress = self.attack_time / self.attack_duration
        
        # Create attack effect color (red with varying alpha)
        if attack_progress <= 0.6:  # Active damage phase
            alpha = int(255 * (1.0 - attack_progress / 0.6))
            color = (255, 100, 100, alpha)
        else:  # Cooldown phase
            alpha = int(100 * (1.0 - (attack_progress - 0.6) / 0.4))
            color = (255, 200, 200, alpha)
        
        # Create a surface for the attack effect
        attack_surface = pygame.Surface((screen_attack_rect.width, screen_attack_rect.height))
        attack_surface.set_alpha(alpha)
        attack_surface.fill((255, 100, 100))
        
        # Only render if attack area is visible on screen
        if (screen_attack_rect.x < screen.get_width() and 
            screen_attack_rect.x + screen_attack_rect.width > 0 and
            screen_attack_rect.y < screen.get_height() and 
            screen_attack_rect.y + screen_attack_rect.height > 0):
            screen.blit(attack_surface, (screen_attack_rect.x, screen_attack_rect.y))
    
    def _get_animated_sprite(self) -> pygame.Surface:
        """
        Get the current animated sprite based on movement state and direction.
        
        Returns:
            Pygame surface representing current animation frame
        """
        # Get the base sprite for current direction
        direction = self.facing_direction if self.is_moving else self.last_facing_direction
        base_sprite = self.direction_sprites.get(direction, self.sprite)
        
        # Handle attack animation
        if self.is_attacking:
            return self._get_attack_sprite(base_sprite)
        
        if not self.is_moving:
            return base_sprite
        
        # Create animated version based on animation frame
        animated_sprite = base_sprite.copy()
        
        # Apply animation effects based on frame
        animation_offset = self._get_animation_offset()
        
        if animation_offset != (0, 0):
            # Create a new surface for the animated sprite
            new_sprite = pygame.Surface((self.width, self.height))
            new_sprite.fill((0, 100, 200))  # Base color
            
            # Copy the base sprite with offset
            new_sprite.blit(base_sprite, animation_offset)
            animated_sprite = new_sprite
        
        return animated_sprite
    
    def _get_attack_sprite(self, base_sprite: pygame.Surface) -> pygame.Surface:
        """
        Get the attack animation sprite.
        
        Args:
            base_sprite: Base sprite to modify for attack animation
            
        Returns:
            Pygame surface with attack animation effects
        """
        attack_sprite = base_sprite.copy()
        
        # Calculate attack animation progress
        attack_progress = self.attack_time / self.attack_duration
        
        # Add visual effects for attack
        if attack_progress <= 0.3:
            # Wind-up phase - slight color change
            attack_sprite.fill((150, 150, 255), special_flags=pygame.BLEND_ADD)
        elif attack_progress <= 0.6:
            # Active attack phase - bright flash
            attack_sprite.fill((255, 200, 200), special_flags=pygame.BLEND_ADD)
        else:
            # Recovery phase - fade back to normal
            fade_amount = int(100 * (1.0 - (attack_progress - 0.6) / 0.4))
            attack_sprite.fill((fade_amount, fade_amount // 2, fade_amount // 2), special_flags=pygame.BLEND_ADD)
        
        return attack_sprite
    
    def _get_animation_offset(self) -> Tuple[int, int]:
        """
        Get the animation offset based on current frame and direction.
        
        Returns:
            Tuple of (x_offset, y_offset) for animation
        """
        if not self.is_moving:
            return (0, 0)
        
        # Create subtle bobbing effect
        if self.animation_frame in [1, 3]:
            # Slight vertical offset for "step" frames
            return (0, -1)
        elif self.animation_frame == 2:
            # Slight horizontal offset for variety
            if self.facing_direction in ['left', 'right']:
                return (1 if self.facing_direction == 'right' else -1, 0)
            else:
                return (0, 1)
        
        return (0, 0)
    
    def attack(self) -> None:
        """
        Perform an attack action.
        """
        import time
        current_time = time.time()
        
        # Check if attack is on cooldown
        if current_time - self.last_attack_time < self.attack_cooldown:
            return
        
        # Check if already attacking
        if self.is_attacking:
            return
        
        # Start attack
        self.is_attacking = True
        self.attack_time = 0.0
        self.last_attack_time = current_time
        
        print(f"Player attacks in direction: {self.facing_direction}")
    
    def _update_attack_state(self, dt: float) -> None:
        """
        Update attack animation state.
        
        Args:
            dt: Delta time since last frame
        """
        if self.is_attacking:
            self.attack_time += dt
            if self.attack_time >= self.attack_duration:
                self.is_attacking = False
                self.attack_time = 0.0
    
    def get_attack_rect(self) -> pygame.Rect:
        """
        Get the attack rectangle based on player position and facing direction.
        
        Returns:
            Pygame Rect representing the attack area
        """
        attack_width = self.attack_range
        attack_height = self.attack_range
        
        # Calculate attack position based on facing direction
        if self.facing_direction == 'up':
            attack_x = self.x - (attack_width - self.width) // 2
            attack_y = self.y - attack_height
        elif self.facing_direction == 'down':
            attack_x = self.x - (attack_width - self.width) // 2
            attack_y = self.y + self.height
        elif self.facing_direction == 'left':
            attack_x = self.x - attack_width
            attack_y = self.y - (attack_height - self.height) // 2
        elif self.facing_direction == 'right':
            attack_x = self.x + self.width
            attack_y = self.y - (attack_height - self.height) // 2
        else:
            # Default to down direction
            attack_x = self.x - (attack_width - self.width) // 2
            attack_y = self.y + self.height
        
        return pygame.Rect(attack_x, attack_y, attack_width, attack_height)
    
    def is_attack_active(self) -> bool:
        """
        Check if the attack is currently active (can deal damage).
        
        Returns:
            True if attack is active and can deal damage
        """
        # Attack is active during the first half of the attack animation
        return self.is_attacking and self.attack_time <= self.attack_duration * 0.6
    
    def get_attack_damage(self) -> int:
        """
        Get the current attack damage.
        
        Returns:
            Attack damage amount
        """
        # Base damage can be modified by equipment, level, etc.
        damage_modifier = 1.0
        
        # Example: could add weapon bonuses, level bonuses, etc.
        # if self.equipped_weapon:
        #     damage_modifier *= self.equipped_weapon.damage_multiplier
        # damage_modifier *= (1.0 + (self.level - 1) * 0.1)  # 10% per level
        
        return int(self.get_total_attack_damage() * damage_modifier)
    
    def interact(self) -> None:
        """
        Perform an interaction action.
        """
        # TODO: Implement interaction logic
        print("Player interacts")
    
    def collect_item(self, item) -> bool:
        """
        Attempt to collect an item.
        
        Args:
            item: Item object to collect
            
        Returns:
            True if item was collected successfully
        """
        if hasattr(item, 'collect'):
            return item.collect(self)
        return False
    
    def use_item(self, item) -> bool:
        """
        Use an item from inventory.
        
        Args:
            item: Item to use
            
        Returns:
            True if item was used successfully
        """
        return self.inventory.use_item(item, self)
    
    def use_item_by_index(self, index: int) -> bool:
        """
        Use an item by its inventory index.
        
        Args:
            index: Index of item to use
            
        Returns:
            True if item was used successfully
        """
        return self.inventory.use_item_by_index(index, self)
    
    def equip_item(self, item) -> bool:
        """
        Equip an item from inventory.
        
        Args:
            item: Item to equip
            
        Returns:
            True if item was equipped successfully
        """
        return self.inventory.equip_item(item, self)
    
    def unequip_item(self, item) -> bool:
        """
        Unequip an item and return it to inventory.
        
        Args:
            item: Item to unequip
            
        Returns:
            True if item was unequipped successfully
        """
        return self.inventory.unequip_item(item, self)
    
    def get_equipped_weapon(self):
        """
        Get the currently equipped weapon.
        
        Returns:
            Equipped weapon item, or None if no weapon equipped
        """
        return self.inventory.get_equipped_item('weapon')
    
    def get_equipped_armor(self):
        """
        Get the currently equipped armor.
        
        Returns:
            Equipped armor item, or None if no armor equipped
        """
        return self.inventory.get_equipped_item('armor')
    
    def get_equipped_equipment(self):
        """
        Get the currently equipped equipment.
        
        Returns:
            Equipped equipment item, or None if no equipment equipped
        """
        return self.inventory.get_equipped_item('equipment')
    
    def get_inventory_info(self) -> dict:
        """
        Get detailed inventory information.
        
        Returns:
            Dictionary containing inventory information
        """
        return self.inventory.get_inventory_info()
    
    def has_item_type(self, item_type: str) -> bool:
        """
        Check if player has any item of a specific type.
        
        Args:
            item_type: Type of item to check for
            
        Returns:
            True if player has item of this type
        """
        return self.inventory.has_item_type(item_type)
    
    def count_item_type(self, item_type: str) -> int:
        """
        Count how many items of a specific type the player has.
        
        Args:
            item_type: Type of item to count
            
        Returns:
            Number of items of the specified type
        """
        return self.inventory.count_item_type(item_type)
    
    def apply_status_effect(self, effect_name: str, effect_data: dict) -> None:
        """
        Apply a temporary status effect to the player.
        
        Args:
            effect_name: Name of the effect
            effect_data: Dictionary containing effect parameters
        """
        import time
        
        # If effect already exists, remove it first to prevent stacking
        if effect_name in self.status_effects:
            self.remove_status_effect(effect_name)
        
        # Calculate end time for the effect
        duration = effect_data.get('duration', 0)
        end_time = time.time() + duration if duration > 0 else float('inf')
        
        # Store the effect
        self.status_effects[effect_name] = {
            'data': effect_data.copy(),
            'end_time': end_time,
            'start_time': time.time()
        }
        
        # Apply immediate effects
        if 'attack_boost' in effect_data:
            self.temporary_attack_bonus += effect_data['attack_boost']
            print(f"Attack increased by {effect_data['attack_boost']} for {duration} seconds")
        
        if 'speed_boost' in effect_data:
            self.temporary_speed_multiplier *= effect_data['speed_boost']
            self.set_speed_modifier(self.temporary_speed_multiplier)
            print(f"Speed increased by {(effect_data['speed_boost'] - 1) * 100:.0f}% for {duration} seconds")
        
        if 'health_regen' in effect_data:
            self.health_regen_rate += effect_data['health_regen']
            print(f"Health regeneration increased by {effect_data['health_regen']} per second")
    
    def remove_status_effect(self, effect_name: str) -> None:
        """
        Remove a status effect from the player.
        
        Args:
            effect_name: Name of the effect to remove
        """
        if effect_name not in self.status_effects:
            return
        
        effect_data = self.status_effects[effect_name]['data']
        
        # Remove the effects
        if 'attack_boost' in effect_data:
            self.temporary_attack_bonus -= effect_data['attack_boost']
            print(f"Attack boost of {effect_data['attack_boost']} has worn off")
        
        if 'speed_boost' in effect_data:
            self.temporary_speed_multiplier /= effect_data['speed_boost']
            self.set_speed_modifier(self.temporary_speed_multiplier)
            print(f"Speed boost has worn off")
        
        if 'health_regen' in effect_data:
            self.health_regen_rate -= effect_data['health_regen']
            print(f"Health regeneration effect has worn off")
        
        # Remove from active effects
        del self.status_effects[effect_name]
    
    def update_status_effects(self, dt: float) -> None:
        """
        Update all active status effects.
        
        Args:
            dt: Delta time since last frame
        """
        import time
        current_time = time.time()
        
        # Check for expired effects
        expired_effects = []
        for effect_name, effect_info in self.status_effects.items():
            if current_time >= effect_info['end_time']:
                expired_effects.append(effect_name)
        
        # Remove expired effects
        for effect_name in expired_effects:
            self.remove_status_effect(effect_name)
        
        # Apply continuous effects
        if self.health_regen_rate > 0:
            regen_amount = self.health_regen_rate * dt
            if self.current_health < self.max_health:
                old_health = self.current_health
                self.current_health = min(self.max_health, self.current_health + regen_amount)
                if self.current_health > old_health:
                    # Only print if we actually regenerated health
                    pass  # Don't spam the console with regen messages
    
    def get_total_attack_damage(self) -> int:
        """
        Get the total attack damage including temporary bonuses.
        
        Returns:
            Total attack damage
        """
        return self.attack_damage + self.temporary_attack_bonus
    
    def has_status_effect(self, effect_name: str) -> bool:
        """
        Check if the player has a specific status effect active.
        
        Args:
            effect_name: Name of the effect to check
            
        Returns:
            True if effect is active, False otherwise
        """
        return effect_name in self.status_effects
    
    def get_status_effects(self) -> dict:
        """
        Get all active status effects.
        
        Returns:
            Dictionary of active status effects
        """
        return self.status_effects.copy()
    
    def clear_all_status_effects(self) -> None:
        """Clear all active status effects."""
        effect_names = list(self.status_effects.keys())
        for effect_name in effect_names:
            self.remove_status_effect(effect_name)
    
    def take_damage(self, damage: int) -> None:
        """
        Take damage and reduce health.
        
        Args:
            damage: Amount of damage to take
        """
        self.current_health = max(0, self.current_health - damage)
        print(f"Player takes {damage} damage. Health: {self.current_health}/{self.max_health}")
        
        if self.current_health <= 0:
            self.die()
    
    def heal(self, amount: int) -> None:
        """
        Heal the player.
        
        Args:
            amount: Amount of health to restore
        """
        old_health = self.current_health
        self.current_health = min(self.max_health, self.current_health + amount)
        healed = self.current_health - old_health
        if healed > 0:
            print(f"Player healed for {healed}. Health: {self.current_health}/{self.max_health}")
    
    def die(self) -> None:
        """
        Handle player death.
        """
        print("Player has died!")
        # TODO: Implement death logic (game over screen, respawn, etc.)
    
    def add_experience(self, exp: int) -> None:
        """
        Add experience points to the player.
        
        Args:
            exp: Experience points to add
        """
        self.experience += exp
        print(f"Player gains {exp} experience. Total: {self.experience}")
        
        # Simple level up logic (every 100 exp = 1 level)
        new_level = (self.experience // 100) + 1
        if new_level > self.level:
            self.level_up(new_level)
    
    def level_up(self, new_level: int) -> None:
        """
        Level up the player.
        
        Args:
            new_level: New level to set
        """
        old_level = self.level
        self.level = new_level
        
        # Increase stats on level up
        health_increase = 10
        self.max_health += health_increase
        self.current_health += health_increase  # Also heal on level up
        
        print(f"Player leveled up! Level {old_level} -> {new_level}")
        print(f"Max health increased by {health_increase}")
    
    def add_item(self, item) -> bool:
        """
        Add an item to the player's inventory.
        
        Args:
            item: Item to add to inventory
            
        Returns:
            True if item was added, False if inventory is full
        """
        success = self.inventory.add_item(item)
        if success:
            print(f"Added {item.name if hasattr(item, 'name') else item} to inventory")
        else:
            print("Inventory is full!")
        return success
    
    def remove_item(self, item) -> bool:
        """
        Remove an item from the player's inventory.
        
        Args:
            item: Item to remove from inventory
            
        Returns:
            True if item was removed, False if item not found
        """
        success = self.inventory.remove_item(item)
        if success:
            print(f"Removed {item.name if hasattr(item, 'name') else item} from inventory")
        else:
            print(f"{item.name if hasattr(item, 'name') else item} not found in inventory")
        return success
    
    def get_health_percentage(self) -> float:
        """
        Get the player's health as a percentage.
        
        Returns:
            Health percentage (0.0 to 1.0)
        """
        return self.current_health / self.max_health if self.max_health > 0 else 0.0
    
    def set_boundaries(self, left: float, top: float, right: float, bottom: float) -> None:
        """
        Set movement boundaries for the player.
        
        Args:
            left: Left boundary (minimum X)
            top: Top boundary (minimum Y)
            right: Right boundary (maximum X)
            bottom: Bottom boundary (maximum Y)
        """
        self.boundary_left = left
        self.boundary_top = top
        self.boundary_right = right
        self.boundary_bottom = bottom
    
    def set_speed_modifier(self, modifier: float) -> None:
        """
        Set a speed modifier for the player.
        
        Args:
            modifier: Speed multiplier (1.0 = normal speed)
        """
        self.speed = self.base_speed * modifier
    
    def reset_speed(self) -> None:
        """Reset player speed to base speed."""
        self.speed = self.base_speed
    
    def is_at_boundary(self) -> dict:
        """
        Check which boundaries the player is currently touching.
        
        Returns:
            Dictionary indicating which boundaries are being touched
        """
        return {
            'left': self.x <= self.boundary_left,
            'right': self.x >= self.boundary_right - self.width,
            'top': self.y <= self.boundary_top,
            'bottom': self.y >= self.boundary_bottom - self.height
        }
    
    def can_move_in_direction(self, direction: str) -> bool:
        """
        Check if player can move in a specific direction without hitting boundaries.
        
        Args:
            direction: Direction to check ('up', 'down', 'left', 'right')
            
        Returns:
            True if movement is possible, False otherwise
        """
        boundaries = self.is_at_boundary()
        
        if direction == 'up' and boundaries['top']:
            return False
        elif direction == 'down' and boundaries['bottom']:
            return False
        elif direction == 'left' and boundaries['left']:
            return False
        elif direction == 'right' and boundaries['right']:
            return False
        
        return True
    
    def get_movement_info(self) -> dict:
        """
        Get detailed movement information.
        
        Returns:
            Dictionary containing movement state information
        """
        return {
            'position': (self.x, self.y),
            'velocity': (self.velocity_x, self.velocity_y),
            'is_moving': self.is_moving,
            'facing_direction': self.facing_direction,
            'last_facing_direction': self.last_facing_direction,
            'animation_frame': self.animation_frame,
            'speed': self.speed,
            'at_boundaries': self.is_at_boundary()
        }
    
    def get_stats(self) -> dict:
        """
        Get player statistics.
        
        Returns:
            Dictionary containing player stats
        """
        return {
            'level': self.level,
            'health': self.current_health,
            'max_health': self.max_health,
            'experience': self.experience,
            'speed': self.speed,
            'base_speed': self.base_speed,
            'position': (self.x, self.y),
            'facing_direction': self.facing_direction,
            'inventory_count': self.inventory.get_item_count(),
            'is_moving': self.is_moving,
            'animation_frame': self.animation_frame,
            'is_attacking': self.is_attacking,
            'attack_damage': self.get_attack_damage(),
            'attack_range': self.attack_range
        }