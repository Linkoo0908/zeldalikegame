"""
Combat System for handling player-enemy combat interactions.
"""
import pygame
from typing import List, Optional, Tuple, TYPE_CHECKING

# Use TYPE_CHECKING to avoid circular imports during testing
if TYPE_CHECKING:
    from objects.player import Player
    from objects.enemy import Enemy


class CombatSystem:
    """
    Handles combat interactions between player and enemies.
    Manages damage dealing, collision detection, and combat rewards.
    """
    
    def __init__(self):
        """Initialize the combat system."""
        self.active_enemies: List['Enemy'] = []
        self.combat_events: List[dict] = []  # Store combat events for this frame
        
        # Combat settings
        self.damage_flash_duration = 0.2  # Duration of damage flash effect
        self.knockback_force = 50.0  # Knockback force when hit
        
    def add_enemy(self, enemy: 'Enemy') -> None:
        """
        Add an enemy to the combat system.
        
        Args:
            enemy: Enemy to add
        """
        if enemy not in self.active_enemies:
            self.active_enemies.append(enemy)
    
    def remove_enemy(self, enemy: 'Enemy') -> None:
        """
        Remove an enemy from the combat system.
        
        Args:
            enemy: Enemy to remove
        """
        if enemy in self.active_enemies:
            self.active_enemies.remove(enemy)
    
    def update(self, dt: float, player: 'Player') -> None:
        """
        Update combat system and process all combat interactions.
        
        Args:
            dt: Delta time since last frame
            player: Player object
        """
        self.combat_events.clear()
        
        # Update all enemies with player position for AI
        player_center = (player.x + player.width / 2, player.y + player.height / 2)
        
        for enemy in self.active_enemies[:]:  # Use slice to avoid modification during iteration
            if not enemy.active:
                self.remove_enemy(enemy)
                continue
            
            # Update enemy AI with player position
            enemy.update(dt, player_center)
            
            # Check player attack hitting enemy
            self._check_player_attack_enemy(player, enemy)
            
            # Check enemy attack hitting player
            self._check_enemy_attack_player(enemy, player)
    
    def _check_player_attack_enemy(self, player: 'Player', enemy: 'Enemy') -> None:
        """
        Check if player attack hits enemy.
        
        Args:
            player: Player object
            enemy: Enemy object
        """
        if not player.is_attack_active():
            return
        
        # Get attack and enemy rectangles
        attack_rect = player.get_attack_rect()
        enemy_rect = enemy.get_bounds()
        
        # Check collision
        if self._rects_collide(attack_rect, enemy_rect):
            # Deal damage to enemy
            damage = player.get_attack_damage()
            enemy_died = enemy.take_damage(damage)
            
            # Apply knockback to enemy
            self._apply_knockback(enemy, player, self.knockback_force * 0.5)
            
            # Record combat event
            self.combat_events.append({
                'type': 'player_hit_enemy',
                'damage': damage,
                'enemy': enemy,
                'enemy_died': enemy_died
            })
            
            # If enemy died, give rewards to player
            if enemy_died:
                self._give_enemy_rewards(player, enemy)
    
    def _check_enemy_attack_player(self, enemy: 'Enemy', player: 'Player') -> None:
        """
        Check if enemy attack hits player.
        
        Args:
            enemy: Enemy object
            player: Player object
        """
        if not enemy.is_attack_active():
            return
        
        # Get attack and player rectangles
        attack_rect = enemy.get_attack_rect()
        player_rect = pygame.Rect(player.x, player.y, player.width, player.height)
        
        # Check collision
        if self._rects_collide(attack_rect, player_rect):
            # Deal damage to player
            damage = enemy.get_attack_damage()
            player.take_damage(damage)
            
            # Apply knockback to player
            self._apply_knockback(player, enemy, self.knockback_force)
            
            # Record combat event
            self.combat_events.append({
                'type': 'enemy_hit_player',
                'damage': damage,
                'enemy': enemy
            })
    
    def _rects_collide(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """
        Check if two rectangles collide.
        
        Args:
            rect1: First rectangle
            rect2: Second rectangle
            
        Returns:
            True if rectangles collide
        """
        return rect1.colliderect(rect2)
    
    def _apply_knockback(self, target, source, force: float) -> None:
        """
        Apply knockback force to target away from source.
        
        Args:
            target: Object to apply knockback to
            source: Object causing the knockback
            force: Knockback force magnitude
        """
        # Calculate direction from source to target
        source_center_x = source.x + source.width / 2
        source_center_y = source.y + source.height / 2
        target_center_x = target.x + target.width / 2
        target_center_y = target.y + target.height / 2
        
        dx = target_center_x - source_center_x
        dy = target_center_y - source_center_y
        
        # Normalize direction
        distance = (dx * dx + dy * dy) ** 0.5
        if distance > 0:
            dx /= distance
            dy /= distance
            
            # Apply knockback (simple implementation - just move the target)
            knockback_distance = force * 0.1  # Scale down for reasonable knockback
            target.x += dx * knockback_distance
            target.y += dy * knockback_distance
    
    def _give_enemy_rewards(self, player: 'Player', enemy: 'Enemy') -> None:
        """
        Give rewards to player for defeating enemy.
        
        Args:
            player: Player object
            enemy: Defeated enemy
        """
        # Give experience
        player.add_experience(enemy.experience_reward)
        
        # Record reward event
        self.combat_events.append({
            'type': 'enemy_defeated',
            'enemy': enemy,
            'experience_reward': enemy.experience_reward
        })
        
        # TODO: Add item drops, gold rewards, etc.
    
    def get_combat_events(self) -> List[dict]:
        """
        Get combat events that occurred this frame.
        
        Returns:
            List of combat event dictionaries
        """
        return self.combat_events.copy()
    
    def get_active_enemies(self) -> List['Enemy']:
        """
        Get list of active enemies.
        
        Returns:
            List of active Enemy objects
        """
        return self.active_enemies.copy()
    
    def get_enemies_in_range(self, position: Tuple[float, float], range_distance: float) -> List['Enemy']:
        """
        Get enemies within a certain range of a position.
        
        Args:
            position: Center position (x, y)
            range_distance: Range distance
            
        Returns:
            List of enemies within range
        """
        enemies_in_range = []
        
        for enemy in self.active_enemies:
            if not enemy.active:
                continue
            
            enemy_center = (enemy.x + enemy.width / 2, enemy.y + enemy.height / 2)
            dx = enemy_center[0] - position[0]
            dy = enemy_center[1] - position[1]
            distance = (dx * dx + dy * dy) ** 0.5
            
            if distance <= range_distance:
                enemies_in_range.append(enemy)
        
        return enemies_in_range
    
    def clear_enemies(self) -> None:
        """Clear all enemies from the combat system."""
        self.active_enemies.clear()
    
    def spawn_enemy(self, x: float, y: float, enemy_type: str = "basic") -> 'Enemy':
        """
        Spawn a new enemy at the specified position.
        
        Args:
            x: X position
            y: Y position
            enemy_type: Type of enemy to spawn
            
        Returns:
            The spawned Enemy object
        """
        from objects.enemy import Enemy
        enemy = Enemy(x, y, enemy_type)
        self.add_enemy(enemy)
        return enemy
    
    def get_stats(self) -> dict:
        """
        Get combat system statistics.
        
        Returns:
            Dictionary containing combat stats
        """
        active_count = len([e for e in self.active_enemies if e.active])
        total_health = sum(e.current_health for e in self.active_enemies if e.active)
        
        return {
            'active_enemies': active_count,
            'total_enemies': len(self.active_enemies),
            'total_enemy_health': total_health,
            'combat_events_this_frame': len(self.combat_events)
        }
    
    def render_debug(self, screen: pygame.Surface, camera_x: float = 0, camera_y: float = 0) -> None:
        """
        Render debug information for combat system.
        
        Args:
            screen: Pygame surface to render to
            camera_x: Camera X offset
            camera_y: Camera Y offset
        """
        # Render enemy attack ranges (for debugging)
        for enemy in self.active_enemies:
            if not enemy.active:
                continue
            
            if enemy.is_attacking:
                attack_rect = enemy.get_attack_rect()
                screen_rect = pygame.Rect(
                    attack_rect.x - camera_x,
                    attack_rect.y - camera_y,
                    attack_rect.width,
                    attack_rect.height
                )
                pygame.draw.rect(screen, (255, 0, 0, 100), screen_rect, 2)
            
            # Render detection range
            detection_center_x = enemy.x + enemy.width / 2 - camera_x
            detection_center_y = enemy.y + enemy.height / 2 - camera_y
            pygame.draw.circle(screen, (255, 255, 0, 50), 
                             (int(detection_center_x), int(detection_center_y)), 
                             int(enemy.detection_range), 1)