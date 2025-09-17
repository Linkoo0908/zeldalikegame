"""
Scene Manager for handling game scene transitions and management.
Manages a stack of scenes and handles transitions between them.
"""
from typing import List, Optional, Dict, Any
import pygame
from .scene import Scene


class SceneManager:
    """
    Manages game scenes using a stack-based approach.
    Handles scene transitions, memory management, and event routing.
    """
    
    def __init__(self, game):
        """
        Initialize the SceneManager.
        
        Args:
            game: Reference to the main Game instance
        """
        self.game = game
        self.scene_stack: List[Scene] = []
        self.pending_operations: List[Dict[str, Any]] = []
        self.transitioning = False
    
    def push_scene(self, scene: Scene) -> None:
        """
        Push a new scene onto the stack.
        The current scene will be paused and the new scene will become active.
        
        Args:
            scene: The scene to push onto the stack
        """
        operation = {
            'type': 'push',
            'scene': scene
        }
        self.pending_operations.append(operation)
    
    def pop_scene(self) -> Optional[Scene]:
        """
        Pop the current scene from the stack.
        The scene will be cleaned up and the previous scene will be resumed.
        
        Returns:
            The popped scene, or None if the stack is empty
        """
        operation = {
            'type': 'pop'
        }
        self.pending_operations.append(operation)
        return None  # Actual scene will be returned after processing
    
    def change_scene(self, scene: Scene) -> None:
        """
        Replace the current scene with a new one.
        The current scene will be cleaned up and removed.
        
        Args:
            scene: The new scene to set as current
        """
        operation = {
            'type': 'change',
            'scene': scene
        }
        self.pending_operations.append(operation)
    
    def clear_all_scenes(self) -> None:
        """
        Clear all scenes from the stack.
        All scenes will be properly cleaned up.
        """
        operation = {
            'type': 'clear'
        }
        self.pending_operations.append(operation)
    
    def _process_pending_operations(self) -> None:
        """
        Process all pending scene operations.
        This is called at the beginning of each frame to ensure safe transitions.
        """
        if not self.pending_operations or self.transitioning:
            return
        
        self.transitioning = True
        
        for operation in self.pending_operations:
            op_type = operation['type']
            
            if op_type == 'push':
                self._execute_push(operation['scene'])
            elif op_type == 'pop':
                self._execute_pop()
            elif op_type == 'change':
                self._execute_change(operation['scene'])
            elif op_type == 'clear':
                self._execute_clear()
        
        self.pending_operations.clear()
        self.transitioning = False
    
    def _execute_push(self, scene: Scene) -> None:
        """
        Execute a push operation.
        
        Args:
            scene: The scene to push
        """
        # Pause the current scene if there is one
        if self.scene_stack:
            current_scene = self.scene_stack[-1]
            current_scene.on_pause()
            current_scene.active = False  # Explicitly set to inactive
        
        # Initialize and activate the new scene
        if not scene.is_initialized():
            scene.initialize(self.game)
            scene.initialized = True
        
        scene.on_enter()
        self.scene_stack.append(scene)
        
        print(f"Pushed scene: {scene.get_name()}")
    
    def _execute_pop(self) -> Optional[Scene]:
        """
        Execute a pop operation.
        
        Returns:
            The popped scene, or None if stack is empty
        """
        if not self.scene_stack:
            return None
        
        # Remove and cleanup the current scene
        current_scene = self.scene_stack.pop()
        current_scene.on_exit()
        current_scene.cleanup()
        
        # Resume the previous scene if there is one
        if self.scene_stack:
            previous_scene = self.scene_stack[-1]
            previous_scene.active = True  # Explicitly set to active
            previous_scene.on_resume()
        
        print(f"Popped scene: {current_scene.get_name()}")
        return current_scene
    
    def _execute_change(self, scene: Scene) -> None:
        """
        Execute a change operation.
        
        Args:
            scene: The new scene to set as current
        """
        # Clean up the current scene if there is one
        if self.scene_stack:
            current_scene = self.scene_stack.pop()
            current_scene.on_exit()
            current_scene.cleanup()
        
        # Initialize and activate the new scene
        if not scene.is_initialized():
            scene.initialize(self.game)
            scene.initialized = True
        
        scene.on_enter()
        self.scene_stack.append(scene)
        
        print(f"Changed to scene: {scene.get_name()}")
    
    def _execute_clear(self) -> None:
        """Execute a clear operation."""
        while self.scene_stack:
            scene = self.scene_stack.pop()
            scene.on_exit()
            scene.cleanup()
        
        print("Cleared all scenes")
    
    def handle_event(self, event: pygame.event.Event) -> None:
        """
        Handle a pygame event by passing it to the current scene.
        
        Args:
            event: The pygame event to handle
        """
        if self.scene_stack and not self.transitioning:
            current_scene = self.scene_stack[-1]
            current_scene.handle_event(event)
    
    def update(self, dt: float) -> None:
        """
        Update the scene manager and current scene.
        
        Args:
            dt: Delta time since last frame in seconds
        """
        # Process any pending scene operations first
        self._process_pending_operations()
        
        # Update the current scene
        if self.scene_stack and not self.transitioning:
            current_scene = self.scene_stack[-1]
            current_scene.update(dt)
    
    def render(self, screen: pygame.Surface) -> None:
        """
        Render the current scene.
        
        Args:
            screen: The pygame surface to render to
        """
        if self.scene_stack and not self.transitioning:
            current_scene = self.scene_stack[-1]
            current_scene.render(screen)
    
    def get_current_scene(self) -> Optional[Scene]:
        """
        Get the currently active scene.
        
        Returns:
            The current scene, or None if no scene is active
        """
        return self.scene_stack[-1] if self.scene_stack else None
    
    def get_scene_count(self) -> int:
        """
        Get the number of scenes in the stack.
        
        Returns:
            The number of scenes currently in the stack
        """
        return len(self.scene_stack)
    
    def has_scenes(self) -> bool:
        """
        Check if there are any scenes in the stack.
        
        Returns:
            True if there are scenes, False otherwise
        """
        return len(self.scene_stack) > 0
    
    def get_scene_names(self) -> List[str]:
        """
        Get the names of all scenes in the stack.
        
        Returns:
            List of scene names from bottom to top of stack
        """
        return [scene.get_name() for scene in self.scene_stack]
    
    def cleanup(self) -> None:
        """
        Clean up the scene manager and all scenes.
        Called when the game is shutting down.
        """
        print("Cleaning up SceneManager...")
        
        # Clear all scenes
        self.clear_all_scenes()
        self._process_pending_operations()
        
        # Clear any remaining references
        self.scene_stack.clear()
        self.pending_operations.clear()
        
        print("SceneManager cleanup complete")