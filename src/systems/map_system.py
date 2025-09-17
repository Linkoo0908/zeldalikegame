"""
Map system for loading and managing game maps.
"""
import json
import os
import pygame
from typing import Dict, List, Any, Optional, Tuple


class MapSystem:
    """Handles loading and managing game maps."""
    
    def __init__(self):
        self.current_map = None
        self.current_map_path = None
        self.maps_cache = {}
        self.map_states = {}  # Store per-map game state (enemies, items, etc.)
        
    def load_map(self, map_path: str) -> Dict[str, Any]:
        """
        Load a map from JSON file.
        
        Args:
            map_path: Path to the map JSON file
            
        Returns:
            Dictionary containing map data
            
        Raises:
            FileNotFoundError: If map file doesn't exist
            json.JSONDecodeError: If map file is invalid JSON
        """
        if map_path in self.maps_cache:
            return self.maps_cache[map_path]
            
        if not os.path.exists(map_path):
            raise FileNotFoundError(f"Map file not found: {map_path}")
            
        try:
            with open(map_path, 'r', encoding='utf-8') as f:
                map_data = json.load(f)
                
            # Validate map data structure
            self._validate_map_data(map_data)
            
            # Cache the loaded map
            self.maps_cache[map_path] = map_data
            
            return map_data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in map file {map_path}: {e}")
    
    def _validate_map_data(self, map_data: Dict[str, Any]) -> None:
        """
        Validate that map data has required structure.
        
        Args:
            map_data: Map data dictionary to validate
            
        Raises:
            ValueError: If map data is missing required fields
        """
        required_fields = ['width', 'height', 'tile_size', 'layers']
        for field in required_fields:
            if field not in map_data:
                raise ValueError(f"Map data missing required field: {field}")
                
        layers = map_data['layers']
        required_layers = ['background', 'collision']
        for layer in required_layers:
            if layer not in layers:
                raise ValueError(f"Map data missing required layer: {layer}")
                
        # Validate layer dimensions
        width, height = map_data['width'], map_data['height']
        
        for layer_name, layer_data in layers.items():
            if layer_name in ['background', 'collision']:
                if len(layer_data) != height:
                    raise ValueError(f"Layer {layer_name} height mismatch")
                for row in layer_data:
                    if len(row) != width:
                        raise ValueError(f"Layer {layer_name} width mismatch")
    
    def get_tile_at(self, x: int, y: int, layer: str = 'background') -> int:
        """
        Get tile ID at specific coordinates.
        
        Args:
            x: X coordinate in tile units
            y: Y coordinate in tile units
            layer: Layer name to check
            
        Returns:
            Tile ID at the specified position, or 0 if out of bounds
        """
        if not self.current_map:
            return 0
            
        if layer not in self.current_map['layers']:
            return 0
            
        if (x < 0 or x >= self.current_map['width'] or 
            y < 0 or y >= self.current_map['height']):
            return 0
            
        return self.current_map['layers'][layer][y][x]
    
    def is_tile_solid(self, x: int, y: int) -> bool:
        """
        Check if tile at coordinates is solid (blocks movement).
        
        Args:
            x: X coordinate in tile units
            y: Y coordinate in tile units
            
        Returns:
            True if tile is solid, False otherwise
        """
        collision_value = self.get_tile_at(x, y, 'collision')
        return collision_value == 1
    
    def world_to_tile(self, world_x: float, world_y: float) -> Tuple[int, int]:
        """
        Convert world coordinates to tile coordinates.
        
        Args:
            world_x: X coordinate in world units (pixels)
            world_y: Y coordinate in world units (pixels)
            
        Returns:
            Tuple of (tile_x, tile_y)
        """
        if not self.current_map:
            return (0, 0)
            
        tile_size = self.current_map['tile_size']
        return (int(world_x // tile_size), int(world_y // tile_size))
    
    def tile_to_world(self, tile_x: int, tile_y: int) -> Tuple[float, float]:
        """
        Convert tile coordinates to world coordinates.
        
        Args:
            tile_x: X coordinate in tile units
            tile_y: Y coordinate in tile units
            
        Returns:
            Tuple of (world_x, world_y)
        """
        if not self.current_map:
            return (0.0, 0.0)
            
        tile_size = self.current_map['tile_size']
        return (tile_x * tile_size, tile_y * tile_size)
    
    def set_current_map(self, map_data: Dict[str, Any], map_path: str = None) -> None:
        """
        Set the currently active map.
        
        Args:
            map_data: Map data dictionary
            map_path: Path to the map file (optional)
        """
        self.current_map = map_data
        if map_path:
            self.current_map_path = map_path
    
    def get_current_map(self) -> Optional[Dict[str, Any]]:
        """
        Get the currently active map.
        
        Returns:
            Current map data or None if no map is loaded
        """
        return self.current_map
    
    def get_map_objects(self) -> List[Dict[str, Any]]:
        """
        Get all objects from the current map.
        
        Returns:
            List of object dictionaries
        """
        if not self.current_map or 'layers' not in self.current_map:
            return []
            
        return self.current_map['layers'].get('objects', [])
    
    def get_map_size_pixels(self) -> Tuple[int, int]:
        """
        Get map size in pixels.
        
        Returns:
            Tuple of (width_pixels, height_pixels)
        """
        if not self.current_map:
            return (0, 0)
            
        width = self.current_map['width'] * self.current_map['tile_size']
        height = self.current_map['height'] * self.current_map['tile_size']
        return (width, height)
    
    def save_map_state(self, map_path: str, enemies: List[Dict], items: List[Dict], 
                      player_data: Dict = None) -> None:
        """
        Save the current state of a map (enemies, items, player data).
        
        Args:
            map_path: Path to the map file
            enemies: List of enemy data dictionaries
            items: List of item data dictionaries
            player_data: Optional player data to save with map
        """
        self.map_states[map_path] = {
            'enemies': enemies.copy() if enemies else [],
            'items': items.copy() if items else [],
            'player_data': player_data.copy() if player_data else None,
            'timestamp': pygame.time.get_ticks()
        }
    
    def load_map_state(self, map_path: str) -> Optional[Dict[str, Any]]:
        """
        Load the saved state of a map.
        
        Args:
            map_path: Path to the map file
            
        Returns:
            Dictionary containing saved map state or None if no state exists
        """
        return self.map_states.get(map_path)
    
    def clear_map_state(self, map_path: str) -> None:
        """
        Clear the saved state of a map.
        
        Args:
            map_path: Path to the map file
        """
        if map_path in self.map_states:
            del self.map_states[map_path]
    
    def clear_all_map_states(self) -> None:
        """Clear all saved map states."""
        self.map_states.clear()
    
    def get_all_loaded_maps(self) -> List[str]:
        """
        Get list of all loaded map paths.
        
        Returns:
            List of map file paths that have been loaded
        """
        return list(self.maps_cache.keys())
    
    def preload_maps(self, map_paths: List[str]) -> Dict[str, bool]:
        """
        Preload multiple maps into cache.
        
        Args:
            map_paths: List of map file paths to preload
            
        Returns:
            Dictionary mapping map paths to success status
        """
        results = {}
        for map_path in map_paths:
            try:
                self.load_map(map_path)
                results[map_path] = True
            except Exception as e:
                print(f"Failed to preload map {map_path}: {e}")
                results[map_path] = False
        return results
    
    def unload_map(self, map_path: str) -> None:
        """
        Unload a map from cache.
        
        Args:
            map_path: Path to the map file to unload
        """
        if map_path in self.maps_cache:
            del self.maps_cache[map_path]
        
        # Also clear any saved state
        self.clear_map_state(map_path)
    
    def clear_cache(self) -> None:
        """Clear the map cache and all saved states."""
        self.maps_cache.clear()
        self.clear_all_map_states()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """
        Get information about the current cache state.
        
        Returns:
            Dictionary with cache statistics
        """
        return {
            'cached_maps': len(self.maps_cache),
            'map_states': len(self.map_states),
            'current_map': self.current_map_path,
            'cached_map_paths': list(self.maps_cache.keys()),
            'state_map_paths': list(self.map_states.keys())
        }