"""
Enemy class for hostile creatures in the game.
"""
import pygame
import math
import random
from typing import Tuple, Optional
from .game_object import GameObject


class Enemy(GameObject):
    """
    Base enemy class that handles AI movement patterns and combat.
    """
    
    def __init__(self, x: float, y: float, enemy_type: str = "basic"):
        """
        Initialize the Enemy.
        
        Args:
            x: Starting X position
            y: Starting Y position
            enemy_type: Type of enemy (affects stats and behavior)
        """
        super().__init__(x, y, 32, 32)  # Default 32x32 size
        
        self.enemy_type = enemy_type
        
        # Enemy stats based on type
        self._initialize_stats(enemy_type)
        
        # AI state
        self.ai_state = "idle"  # idle, patrol, chase, attack
        self.target_position = None
        self.last_player_position = None
        self.detection_range = 80.0  # Range to detect player
        self.attack_range = 35.0  # Range to attack player
        self.patrol_radius = 60.0  # Radius for patrol movement
        self.original_position = (x, y)  # Starting position for patrol
        
        # Movement
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.facing_direction = 'down'
        
        # AI timing
        self.ai_update_timer = 0.0
        self.ai_update_interval = 0.1  # Update AI every 0.1 seconds
        self.state_change_timer = 0.0
        self.patrol_change_interval = 2.0  # Change patrol direction every 2 seconds
        
        # Attack state
        self.is_attacking = False
        self.attack_time = 0.0
        self.attack_duration = 0.4  # Attack animation duration
        self.attack_cooldown = 1.0  # Cooldown between attacks
        self.last_attack_time = 0.0
        
        # Create enemy sprite
        self._create_enemy_sprite()
    
    def _initialize_stats(self, enemy_type: str) -> None:
        """
        Initialize enemy stats based on type.
        
        Args:
            enemy_type: Type of enemy
        """
        enemy_stats = {
            "basic": {
                "max_health": 30,
                "speed": 50,
                "attack_damage": 10,
                "experience_reward": 10
            },
            "goblin": {
                "max_health": 40,
                "speed": 60,
                "attack_damage": 12,
                "experience_reward": 15
            },
            "orc": {
                "max_health": 60,
                "speed": 40,
                "attack_damage": 18,
                "experience_reward": 25
            },
            "skeleton": {
                "max_health": 25,
                "speed": 70,
                "attack_damage": 8,
                "experience_reward": 12
            }
        }
        
        stats = enemy_stats.get(enemy_type, enemy_stats["basic"])
        
        self.max_health = stats["max_health"]
        self.current_health = self.max_health
        self.speed = stats["speed"]
        self.attack_damage = stats["attack_damage"]
        self.experience_reward = stats["experience_reward"]
    
    def _create_enemy_sprite(self) -> None:
        """Create a sprite for the enemy based on type."""
        self.sprite = pygame.Surface((self.width, self.height))
        
        # Different colors for different enemy types
        enemy_colors = {
            "basic": (150, 50, 50),      # Dark red
            "goblin": (50, 150, 50),     # Dark green
            "orc": (100, 50, 100),       # Dark purple
            "skeleton": (200, 200, 200)  # Light gray
        }
        
        color = enemy_colors.get(self.enemy_type, enemy_colors["basic"])
        self.sprite.fill(color)
        
        # Add simple visual features
        # Eyes
        pygame.draw.circle(self.sprite, (255, 0, 0), (8, 8), 3)   # Red eyes
        pygame.draw.circle(self.sprite, (255, 0, 0), (24, 8), 3)
        
        # Mouth/teeth
        pygame.draw.rect(self.sprite, (255, 255, 255), (12, 20, 8, 4))
    
    def load_sprite_from_loader(self, sprite_loader) -> None:
        """
        Load enemy sprite using sprite loader.
        
        Args:
            sprite_loader: SpriteLoader instance
        """
        loaded_sprite = sprite_loader.load_enemy_sprite(self.enemy_type, self.width, self.height)
        if loaded_sprite:
            self.sprite = loaded_sprite
    
    def update(self, dt: float, player_position: Optional[Tuple[float, float]] = None) -> None:
        """
        Update the enemy state including AI and movement.
        
        Args:
            dt: Delta time since last frame in seconds
            player_position: Current player position for AI decisions
        """
        # Update attack state
        self._update_attack_state(dt)
        
        # Update AI
        self._update_ai(dt, player_position)
        
        # Update position based on velocity
        if not self.is_attacking:
            self.x += self.velocity_x * dt
            self.y += self.velocity_y * dt
    
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
    
    def _update_ai(self, dt: float, player_position: Optional[Tuple[float, float]]) -> None:
        """
        Update AI behavior and state machine.
        
        Args:
            dt: Delta time since last frame
            player_position: Current player position
        """
        self.ai_update_timer += dt
        self.state_change_timer += dt
        
        # Only update AI at intervals for performance
        if self.ai_update_timer < self.ai_update_interval:
            return
        
        self.ai_update_timer = 0.0
        
        if player_position:
            distance_to_player = self._calculate_distance(player_position)
            
            # State transitions based on player distance
            if distance_to_player <= self.attack_range and not self.is_attacking:
                self._transition_to_attack(player_position)
            elif distance_to_player <= self.detection_range:
                self._transition_to_chase(player_position)
            else:
                self._transition_to_patrol()
        else:
            self._transition_to_patrol()
        
        # Execute current state behavior
        self._execute_ai_state(dt, player_position)
    
    def _calculate_distance(self, target_position: Tuple[float, float]) -> float:
        """
        Calculate distance to target position.
        
        Args:
            target_position: Target position (x, y)
            
        Returns:
            Distance to target
        """
        dx = target_position[0] - (self.x + self.width / 2)
        dy = target_position[1] - (self.y + self.height / 2)
        return math.sqrt(dx * dx + dy * dy)
    
    def _transition_to_attack(self, player_position: Tuple[float, float]) -> None:
        """
        Transition to attack state.
        
        Args:
            player_position: Player position
        """
        if self.ai_state != "attack":
            self.ai_state = "attack"
            self.velocity_x = 0.0
            self.velocity_y = 0.0
            self._update_facing_direction(player_position)
    
    def _transition_to_chase(self, player_position: Tuple[float, float]) -> None:
        """
        Transition to chase state.
        
        Args:
            player_position: Player position
        """
        if self.ai_state != "chase":
            self.ai_state = "chase"
        
        self.last_player_position = player_position
        self._move_towards_target(player_position)
    
    def _transition_to_patrol(self) -> None:
        """Transition to patrol state."""
        if self.ai_state != "patrol":
            self.ai_state = "patrol"
            self.state_change_timer = 0.0
    
    def _execute_ai_state(self, dt: float, player_position: Optional[Tuple[float, float]]) -> None:
        """
        Execute behavior for current AI state.
        
        Args:
            dt: Delta time
            player_position: Player position
        """
        if self.ai_state == "attack":
            self._execute_attack_behavior(player_position)
        elif self.ai_state == "chase":
            self._execute_chase_behavior(player_position)
        elif self.ai_state == "patrol":
            self._execute_patrol_behavior()
        else:  # idle
            self._execute_idle_behavior()
    
    def _execute_attack_behavior(self, player_position: Optional[Tuple[float, float]]) -> None:
        """
        Execute attack behavior.
        
        Args:
            player_position: Player position
        """
        import time
        current_time = time.time()
        
        # Check if we can attack (cooldown)
        if (current_time - self.last_attack_time >= self.attack_cooldown and 
            not self.is_attacking):
            self.attack()
            self.last_attack_time = current_time
    
    def _execute_chase_behavior(self, player_position: Optional[Tuple[float, float]]) -> None:
        """
        Execute chase behavior.
        
        Args:
            player_position: Player position
        """
        if player_position:
            self._move_towards_target(player_position)
        elif self.last_player_position:
            # Move towards last known player position
            self._move_towards_target(self.last_player_position)
    
    def _execute_patrol_behavior(self) -> None:
        """Execute patrol behavior."""
        # Change patrol direction periodically
        if self.state_change_timer >= self.patrol_change_interval:
            self.state_change_timer = 0.0
            self._choose_new_patrol_target()
        
        # Move towards patrol target
        if self.target_position:
            distance_to_target = self._calculate_distance(self.target_position)
            if distance_to_target < 10.0:  # Close enough to target
                self._choose_new_patrol_target()
            else:
                self._move_towards_target(self.target_position)
    
    def _execute_idle_behavior(self) -> None:
        """Execute idle behavior."""
        self.velocity_x = 0.0
        self.velocity_y = 0.0
    
    def _choose_new_patrol_target(self) -> None:
        """Choose a new random patrol target within patrol radius."""
        angle = random.uniform(0, 2 * math.pi)
        distance = random.uniform(20, self.patrol_radius)
        
        target_x = self.original_position[0] + math.cos(angle) * distance
        target_y = self.original_position[1] + math.sin(angle) * distance
        
        self.target_position = (target_x, target_y)
    
    def _move_towards_target(self, target_position: Tuple[float, float]) -> None:
        """
        Move towards a target position.
        
        Args:
            target_position: Target position (x, y)
        """
        # Calculate direction to target
        dx = target_position[0] - (self.x + self.width / 2)
        dy = target_position[1] - (self.y + self.height / 2)
        
        # Normalize direction
        distance = math.sqrt(dx * dx + dy * dy)
        if distance > 0:
            dx /= distance
            dy /= distance
            
            # Set velocity
            self.velocity_x = dx * self.speed
            self.velocity_y = dy * self.speed
            
            # Update facing direction
            self._update_facing_direction(target_position)
        else:
            self.velocity_x = 0.0
            self.velocity_y = 0.0
    
    def _update_facing_direction(self, target_position: Tuple[float, float]) -> None:
        """
        Update facing direction based on target position.
        
        Args:
            target_position: Target position
        """
        dx = target_position[0] - (self.x + self.width / 2)
        dy = target_position[1] - (self.y + self.height / 2)
        
        # Determine primary direction
        if abs(dx) > abs(dy):
            self.facing_direction = 'right' if dx > 0 else 'left'
        else:
            self.facing_direction = 'down' if dy > 0 else 'up'
    
    def attack(self) -> None:
        """Perform an attack action."""
        if self.is_attacking:
            return
        
        self.is_attacking = True
        self.attack_time = 0.0
        print(f"{self.enemy_type} enemy attacks!")
    
    def take_damage(self, damage: int) -> bool:
        """
        Take damage and reduce health.
        
        Args:
            damage: Amount of damage to take
            
        Returns:
            True if enemy died, False otherwise
        """
        self.current_health = max(0, self.current_health - damage)
        print(f"{self.enemy_type} enemy takes {damage} damage. Health: {self.current_health}/{self.max_health}")
        
        if self.current_health <= 0:
            self.die()
            return True
        
        return False
    
    def die(self) -> None:
        """Handle enemy death."""
        print(f"{self.enemy_type} enemy has died!")
        self.active = False
    
    def get_attack_rect(self) -> pygame.Rect:
        """
        Get the attack rectangle based on enemy position and facing direction.
        
        Returns:
            Pygame Rect representing the attack area
        """
        attack_size = int(self.attack_range)
        
        # Calculate attack position based on facing direction
        if self.facing_direction == 'up':
            attack_x = self.x - (attack_size - self.width) // 2
            attack_y = self.y - attack_size
        elif self.facing_direction == 'down':
            attack_x = self.x - (attack_size - self.width) // 2
            attack_y = self.y + self.height
        elif self.facing_direction == 'left':
            attack_x = self.x - attack_size
            attack_y = self.y - (attack_size - self.height) // 2
        elif self.facing_direction == 'right':
            attack_x = self.x + self.width
            attack_y = self.y - (attack_size - self.height) // 2
        else:
            # Default to down direction
            attack_x = self.x - (attack_size - self.width) // 2
            attack_y = self.y + self.height
        
        return pygame.Rect(attack_x, attack_y, attack_size, attack_size)
    
    def is_attack_active(self) -> bool:
        """
        Check if the attack is currently active (can deal damage).
        
        Returns:
            True if attack is active and can deal damage
        """
        # Attack is active during the middle portion of the attack animation
        return (self.is_attacking and 
                0.1 <= self.attack_time <= self.attack_duration * 0.7)
    
    def get_attack_damage(self) -> int:
        """
        Get the current attack damage.
        
        Returns:
            Attack damage amount
        """
        return self.attack_damage
    
    def render(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """
        Render the enemy to the screen.
        
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
        
        # Get current sprite (with attack effects if attacking)
        current_sprite = self._get_current_sprite()
        
        # Only render if enemy is visible on screen
        if (screen_x + self.width >= 0 and screen_x < screen.get_width() and
            screen_y + self.height >= 0 and screen_y < screen.get_height()):
            screen.blit(current_sprite, (screen_x, screen_y))
            
            # Render health bar
            self._render_health_bar(screen, screen_x, screen_y)
            
            # Render attack effect if attacking
            if self.is_attacking:
                self._render_attack_effect(screen, camera_x, camera_y)
    
    def _get_current_sprite(self) -> pygame.Surface:
        """
        Get the current sprite with any effects applied.
        
        Returns:
            Pygame surface representing current sprite
        """
        if self.is_attacking:
            # Create attack effect sprite
            attack_sprite = self.sprite.copy()
            attack_progress = self.attack_time / self.attack_duration
            
            if attack_progress <= 0.3:
                # Wind-up phase
                attack_sprite.fill((50, 50, 50), special_flags=pygame.BLEND_ADD)
            elif attack_progress <= 0.7:
                # Active attack phase
                attack_sprite.fill((100, 50, 50), special_flags=pygame.BLEND_ADD)
            
            return attack_sprite
        
        return self.sprite
    
    def _render_health_bar(self, screen: pygame.Surface, screen_x: int, screen_y: int) -> None:
        """
        Render enemy health bar above the sprite.
        
        Args:
            screen: Pygame surface to render to
            screen_x: Screen X position
            screen_y: Screen Y position
        """
        if self.current_health >= self.max_health:
            return  # Don't show health bar at full health
        
        bar_width = self.width
        bar_height = 4
        bar_y = screen_y - 8
        
        # Background (red)
        health_bg_rect = pygame.Rect(screen_x, bar_y, bar_width, bar_height)
        pygame.draw.rect(screen, (100, 0, 0), health_bg_rect)
        
        # Foreground (green)
        health_percentage = self.current_health / self.max_health
        health_width = int(bar_width * health_percentage)
        if health_width > 0:
            health_fg_rect = pygame.Rect(screen_x, bar_y, health_width, bar_height)
            pygame.draw.rect(screen, (0, 150, 0), health_fg_rect)
    
    def _render_attack_effect(self, screen: pygame.Surface, camera_x: float, camera_y: float) -> None:
        """
        Render attack effect visualization.
        
        Args:
            screen: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        if not self.is_attack_active():
            return
        
        attack_rect = self.get_attack_rect()
        
        # Convert attack rect to screen coordinates
        screen_attack_rect = pygame.Rect(
            attack_rect.x - camera_x,
            attack_rect.y - camera_y,
            attack_rect.width,
            attack_rect.height
        )
        
        # Create attack effect
        attack_progress = self.attack_time / self.attack_duration
        alpha = int(150 * (1.0 - attack_progress))
        
        attack_surface = pygame.Surface((screen_attack_rect.width, screen_attack_rect.height))
        attack_surface.set_alpha(alpha)
        attack_surface.fill((200, 100, 100))
        
        # Only render if attack area is visible on screen
        if (screen_attack_rect.x < screen.get_width() and 
            screen_attack_rect.x + screen_attack_rect.width > 0 and
            screen_attack_rect.y < screen.get_height() and 
            screen_attack_rect.y + screen_attack_rect.height > 0):
            screen.blit(attack_surface, (screen_attack_rect.x, screen_attack_rect.y))
    
    def get_stats(self) -> dict:
        """
        Get enemy statistics.
        
        Returns:
            Dictionary containing enemy stats
        """
        return {
            'enemy_type': self.enemy_type,
            'health': self.current_health,
            'max_health': self.max_health,
            'position': (self.x, self.y),
            'facing_direction': self.facing_direction,
            'ai_state': self.ai_state,
            'is_attacking': self.is_attacking,
            'attack_damage': self.attack_damage,
            'speed': self.speed,
            'experience_reward': self.experience_reward,
            'active': self.active
        }
    
    def get_bounds(self) -> pygame.Rect:
        """
        Get the bounding rectangle for collision detection.
        
        Returns:
            Pygame Rect representing the enemy's bounds
        """
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def set_patrol_area(self, center_x: float, center_y: float, radius: float) -> None:
        """
        Set the patrol area for this enemy.
        
        Args:
            center_x: Center X of patrol area
            center_y: Center Y of patrol area
            radius: Patrol radius
        """
        self.original_position = (center_x, center_y)
        self.patrol_radius = radius
    
    def reset_to_patrol(self) -> None:
        """Reset enemy to patrol state."""
        self.ai_state = "patrol"
        self.last_player_position = None
        self.target_position = None
        self.state_change_timer = 0.0
        self.velocity_x = 0.0
        self.velocity_y = 0.0