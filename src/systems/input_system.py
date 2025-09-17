"""
Input System for handling keyboard input and converting to game actions.
"""
import pygame
import json
import os
from typing import Dict, List, Tuple


class InputSystem:
    """
    Handles keyboard input state tracking and converts input to game actions.
    """
    
    def __init__(self, controls_file: str = "config/controls.json"):
        """
        Initialize the input system with control mappings.
        
        Args:
            controls_file: Path to the controls configuration file
        """
        self.current_keys = set()
        self.previous_keys = set()
        self.controls = self._load_controls(controls_file)
        
        # Pygame key mapping
        self.key_map = {
            'w': pygame.K_w,
            's': pygame.K_s,
            'a': pygame.K_a,
            'd': pygame.K_d,
            'up': pygame.K_UP,
            'down': pygame.K_DOWN,
            'left': pygame.K_LEFT,
            'right': pygame.K_RIGHT,
            'space': pygame.K_SPACE,
            'z': pygame.K_z,
            'e': pygame.K_e,
            'x': pygame.K_x,
            'i': pygame.K_i,
            'tab': pygame.K_TAB,
            'escape': pygame.K_ESCAPE,
            'p': pygame.K_p,
            'enter': pygame.K_RETURN,
            'backspace': pygame.K_BACKSPACE
        }
    
    def _load_controls(self, controls_file: str) -> Dict:
        """
        Load control mappings from JSON file.
        
        Args:
            controls_file: Path to controls configuration file
            
        Returns:
            Dictionary containing control mappings
        """
        try:
            with open(controls_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Warning: Could not load controls file {controls_file}: {e}")
            # Return default controls
            return {
                "movement": {
                    "up": ["w", "up"],
                    "down": ["s", "down"],
                    "left": ["a", "left"],
                    "right": ["d", "right"]
                },
                "actions": {
                    "attack": ["space", "z"],
                    "interact": ["e", "x"],
                    "inventory": ["i", "tab"],
                    "pause": ["escape", "p"]
                }
            }
    
    def update(self):
        """
        Update input state. Should be called once per frame.
        """
        # Store previous frame's keys
        self.previous_keys = self.current_keys.copy()
        
        # Get current pressed keys
        keys = pygame.key.get_pressed()
        self.current_keys = set()
        
        # Convert pygame keys to our key names
        for key_name, pygame_key in self.key_map.items():
            if pygame_key < len(keys) and keys[pygame_key]:
                self.current_keys.add(key_name)
    
    def is_key_pressed(self, key: str) -> bool:
        """
        Check if a key is currently being pressed.
        
        Args:
            key: Key name to check
            
        Returns:
            True if key is currently pressed
        """
        return key in self.current_keys
    
    def is_key_just_pressed(self, key: str) -> bool:
        """
        Check if a key was just pressed this frame (not pressed last frame).
        
        Args:
            key: Key name to check
            
        Returns:
            True if key was just pressed
        """
        return key in self.current_keys and key not in self.previous_keys
    
    def is_key_just_released(self, key: str) -> bool:
        """
        Check if a key was just released this frame (pressed last frame, not now).
        
        Args:
            key: Key name to check
            
        Returns:
            True if key was just released
        """
        return key not in self.current_keys and key in self.previous_keys
    
    def is_action_pressed(self, action: str) -> bool:
        """
        Check if any key mapped to an action is currently pressed.
        
        Args:
            action: Action name (e.g., 'attack', 'interact')
            
        Returns:
            True if any key for this action is pressed
        """
        if action not in self.controls.get('actions', {}):
            return False
            
        action_keys = self.controls['actions'][action]
        return any(self.is_key_pressed(key) for key in action_keys)
    
    def is_action_just_pressed(self, action: str) -> bool:
        """
        Check if any key mapped to an action was just pressed.
        
        Args:
            action: Action name (e.g., 'attack', 'interact')
            
        Returns:
            True if any key for this action was just pressed
        """
        if action not in self.controls.get('actions', {}):
            return False
            
        action_keys = self.controls['actions'][action]
        return any(self.is_key_just_pressed(key) for key in action_keys)
    
    def get_movement_vector(self) -> Tuple[float, float]:
        """
        Calculate movement vector based on current input state.
        
        Returns:
            Tuple of (x, y) movement vector, normalized for diagonal movement
        """
        movement_x = 0.0
        movement_y = 0.0
        
        movement_controls = self.controls.get('movement', {})
        
        # Check horizontal movement
        if 'left' in movement_controls:
            if any(self.is_key_pressed(key) for key in movement_controls['left']):
                movement_x -= 1.0
        
        if 'right' in movement_controls:
            if any(self.is_key_pressed(key) for key in movement_controls['right']):
                movement_x += 1.0
        
        # Check vertical movement
        if 'up' in movement_controls:
            if any(self.is_key_pressed(key) for key in movement_controls['up']):
                movement_y -= 1.0
        
        if 'down' in movement_controls:
            if any(self.is_key_pressed(key) for key in movement_controls['down']):
                movement_y += 1.0
        
        # Normalize diagonal movement
        if movement_x != 0 and movement_y != 0:
            # Diagonal movement should be normalized to prevent faster diagonal speed
            diagonal_factor = 0.7071067811865476  # 1/sqrt(2)
            movement_x *= diagonal_factor
            movement_y *= diagonal_factor
        
        return (movement_x, movement_y)
    
    def get_movement_direction(self) -> str:
        """
        Get the primary movement direction as a string.
        
        Returns:
            Direction string: 'up', 'down', 'left', 'right', or 'idle'
        """
        movement_x, movement_y = self.get_movement_vector()
        
        # Determine primary direction (prioritize vertical over horizontal)
        if abs(movement_y) > abs(movement_x):
            if movement_y < 0:
                return 'up'
            elif movement_y > 0:
                return 'down'
            else:
                return 'idle'
        elif abs(movement_x) > 0:
            return 'left' if movement_x < 0 else 'right'
        else:
            return 'idle'