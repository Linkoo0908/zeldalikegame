"""
ResourceManager for loading and caching game resources.
Handles images, sounds, and map data with error handling and caching.
"""
import pygame
import json
import os
from typing import Dict, Optional, Any
from pathlib import Path


class ResourceLoadError(Exception):
    """Exception raised when resource loading fails."""
    pass


class ResourceManager:
    """
    Manages loading and caching of game resources including images, sounds, and map data.
    Provides error handling with fallback to default resources when loading fails.
    """
    
    def __init__(self, assets_path: str = "assets"):
        """
        Initialize the ResourceManager.
        
        Args:
            assets_path: Base path to the assets directory
        """
        self.assets_path = Path(assets_path)
        self.image_cache: Dict[str, pygame.Surface] = {}
        self.sound_cache: Dict[str, pygame.mixer.Sound] = {}
        self.map_cache: Dict[str, Dict[str, Any]] = {}
        
        # Create default resources
        self._create_default_resources()
    
    def _create_default_resources(self) -> None:
        """Create default fallback resources."""
        # Create a default 32x32 pink square for missing images
        self.default_image = pygame.Surface((32, 32))
        self.default_image.fill((255, 0, 255))  # Magenta/pink color
        
        # Store default image in cache
        self.image_cache["__default__"] = self.default_image
    
    def load_image(self, path: str, colorkey: Optional[tuple] = None) -> pygame.Surface:
        """
        Load an image from file with caching and error handling.
        
        Args:
            path: Relative path to the image file from assets/images/
            colorkey: Optional color to treat as transparent
            
        Returns:
            pygame.Surface: Loaded image or default image if loading fails
        """
        # Check cache first
        cache_key = f"{path}_{colorkey}" if colorkey else path
        if cache_key in self.image_cache:
            return self.image_cache[cache_key]
        
        # Try to load the image
        full_path = self.assets_path / "images" / path
        
        try:
            if not full_path.exists():
                raise ResourceLoadError(f"Image file not found: {full_path}")
            
            image = pygame.image.load(str(full_path)).convert()
            
            if colorkey:
                if colorkey == "auto":
                    # Use top-left pixel as colorkey
                    colorkey = image.get_at((0, 0))
                image.set_colorkey(colorkey)
            else:
                # Convert with alpha for transparency support
                image = image.convert_alpha()
            
            # Cache the loaded image
            self.image_cache[cache_key] = image
            return image
            
        except (pygame.error, ResourceLoadError, OSError) as e:
            print(f"Warning: Failed to load image '{path}': {e}")
            print(f"Using default image instead.")
            
            # Return default image and cache it with this path
            self.image_cache[cache_key] = self.default_image
            return self.default_image
    
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """
        Load a sound from file with caching and error handling.
        
        Args:
            path: Relative path to the sound file from assets/sounds/
            
        Returns:
            pygame.mixer.Sound or None if loading fails
        """
        # Check cache first
        if path in self.sound_cache:
            return self.sound_cache[path]
        
        # Try to load the sound
        full_path = self.assets_path / "sounds" / path
        
        try:
            if not full_path.exists():
                raise ResourceLoadError(f"Sound file not found: {full_path}")
            
            sound = pygame.mixer.Sound(str(full_path))
            
            # Cache the loaded sound
            self.sound_cache[path] = sound
            return sound
            
        except (pygame.error, ResourceLoadError, OSError) as e:
            print(f"Warning: Failed to load sound '{path}': {e}")
            
            # Cache None to avoid repeated loading attempts
            self.sound_cache[path] = None
            return None
    
    def load_map(self, path: str) -> Dict[str, Any]:
        """
        Load map data from JSON file with caching and error handling.
        
        Args:
            path: Relative path to the map file from assets/maps/
            
        Returns:
            Dict containing map data or default empty map if loading fails
        """
        # Check cache first
        if path in self.map_cache:
            return self.map_cache[path]
        
        # Try to load the map
        full_path = self.assets_path / "maps" / path
        
        try:
            if not full_path.exists():
                raise ResourceLoadError(f"Map file not found: {full_path}")
            
            with open(full_path, 'r', encoding='utf-8') as f:
                map_data = json.load(f)
            
            # Validate basic map structure
            required_keys = ['width', 'height', 'tile_size']
            for key in required_keys:
                if key not in map_data:
                    raise ResourceLoadError(f"Map missing required key: {key}")
            
            # Cache the loaded map
            self.map_cache[path] = map_data
            return map_data
            
        except (json.JSONDecodeError, ResourceLoadError, OSError) as e:
            print(f"Warning: Failed to load map '{path}': {e}")
            print("Using default empty map instead.")
            
            # Return default empty map
            default_map = {
                "width": 10,
                "height": 10,
                "tile_size": 32,
                "layers": {
                    "background": [[0 for _ in range(10)] for _ in range(10)],
                    "collision": [[0 for _ in range(10)] for _ in range(10)],
                    "objects": []
                }
            }
            
            # Cache the default map
            self.map_cache[path] = default_map
            return default_map
    
    def get_resource(self, resource_type: str, path: str, **kwargs) -> Any:
        """
        Generic resource getter that delegates to appropriate load method.
        
        Args:
            resource_type: Type of resource ('image', 'sound', 'map')
            path: Path to the resource file
            **kwargs: Additional arguments for specific loaders
            
        Returns:
            Loaded resource or None/default if loading fails
        """
        if resource_type == "image":
            return self.load_image(path, kwargs.get('colorkey'))
        elif resource_type == "sound":
            return self.load_sound(path)
        elif resource_type == "map":
            return self.load_map(path)
        else:
            raise ValueError(f"Unknown resource type: {resource_type}")
    
    def preload_resources(self, resource_list: list) -> None:
        """
        Preload a list of resources to cache them in advance.
        
        Args:
            resource_list: List of dicts with 'type', 'path', and optional 'kwargs'
        """
        for resource in resource_list:
            resource_type = resource.get('type')
            path = resource.get('path')
            kwargs = resource.get('kwargs', {})
            
            if resource_type and path:
                try:
                    self.get_resource(resource_type, path, **kwargs)
                    print(f"Preloaded {resource_type}: {path}")
                except Exception as e:
                    print(f"Failed to preload {resource_type} '{path}': {e}")
    
    def clear_cache(self, resource_type: Optional[str] = None) -> None:
        """
        Clear resource cache.
        
        Args:
            resource_type: Specific type to clear ('image', 'sound', 'map') or None for all
        """
        if resource_type == "image" or resource_type is None:
            # Keep default image
            default_img = self.image_cache.get("__default__")
            self.image_cache.clear()
            if default_img:
                self.image_cache["__default__"] = default_img
        
        if resource_type == "sound" or resource_type is None:
            self.sound_cache.clear()
        
        if resource_type == "map" or resource_type is None:
            self.map_cache.clear()
    
    def get_cache_info(self) -> Dict[str, int]:
        """
        Get information about cached resources.
        
        Returns:
            Dict with cache sizes for each resource type
        """
        return {
            "images": len(self.image_cache),
            "sounds": len(self.sound_cache),
            "maps": len(self.map_cache)
        }