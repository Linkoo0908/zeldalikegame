"""
Map rendering system for tile-based maps.
"""
import pygame
from typing import Dict, Any, Optional, Tuple
from src.systems.camera import Camera
from src.core.resource_manager import ResourceManager


class MapRenderer:
    """Handles rendering of tile-based maps with camera support."""
    
    def __init__(self, resource_manager: ResourceManager):
        """
        Initialize map renderer.
        
        Args:
            resource_manager: Resource manager for loading tile images
        """
        self.resource_manager = resource_manager
        self.tile_cache = {}  # Cache for tile surfaces
        self.default_tile_size = 32
        
    def render_map(self, screen: pygame.Surface, map_data: Dict[str, Any], 
                   camera: Camera, layer_name: str = 'background') -> None:
        """
        Render a map layer with camera offset and culling.
        
        Args:
            screen: Pygame surface to render to
            map_data: Map data dictionary
            camera: Camera for viewport calculation
            layer_name: Name of the layer to render
        """
        if not map_data or 'layers' not in map_data:
            return
            
        if layer_name not in map_data['layers']:
            return
            
        layer_data = map_data['layers'][layer_name]
        tile_size = map_data.get('tile_size', self.default_tile_size)
        
        # Get visible tile range for culling
        visible_tiles = self._get_visible_tile_range(camera, map_data)
        if not visible_tiles:
            return
            
        start_x, start_y, end_x, end_y = visible_tiles
        
        # Render only visible tiles
        for y in range(start_y, end_y):
            if y < 0 or y >= len(layer_data):
                continue
                
            row = layer_data[y]
            for x in range(start_x, end_x):
                if x < 0 or x >= len(row):
                    continue
                    
                tile_id = row[x]
                if tile_id == 0:  # Skip empty tiles
                    continue
                    
                # Calculate world position
                world_x = x * tile_size
                world_y = y * tile_size
                
                # Convert to screen coordinates
                screen_x, screen_y = camera.world_to_screen(world_x, world_y)
                
                # Render tile
                self._render_tile(screen, tile_id, int(screen_x), int(screen_y), tile_size)
    
    def _get_visible_tile_range(self, camera: Camera, map_data: Dict[str, Any]) -> Optional[Tuple[int, int, int, int]]:
        """
        Calculate the range of tiles visible in the camera view.
        
        Args:
            camera: Camera for viewport calculation
            map_data: Map data dictionary
            
        Returns:
            Tuple of (start_x, start_y, end_x, end_y) tile coordinates, or None if invalid
        """
        tile_size = map_data.get('tile_size', self.default_tile_size)
        map_width = map_data.get('width', 0)
        map_height = map_data.get('height', 0)
        
        if tile_size <= 0 or map_width <= 0 or map_height <= 0:
            return None
            
        # Get visible area in world coordinates
        left, top, right, bottom = camera.get_visible_area()
        
        # Convert to tile coordinates with padding
        start_x = max(0, int(left // tile_size) - 1)
        start_y = max(0, int(top // tile_size) - 1)
        end_x = min(map_width, int(right // tile_size) + 2)
        end_y = min(map_height, int(bottom // tile_size) + 2)
        
        return (start_x, start_y, end_x, end_y)
    
    def _render_tile(self, screen: pygame.Surface, tile_id: int, x: int, y: int, tile_size: int) -> None:
        """
        Render a single tile.
        
        Args:
            screen: Pygame surface to render to
            tile_id: ID of the tile to render
            x: Screen X position
            y: Screen Y position
            tile_size: Size of the tile in pixels
        """
        # Get or create tile surface
        tile_surface = self._get_tile_surface(tile_id, tile_size)
        
        if tile_surface:
            screen.blit(tile_surface, (x, y))
    
    def _get_tile_surface(self, tile_id: int, tile_size: int) -> Optional[pygame.Surface]:
        """
        Get or create a tile surface for the given tile ID.
        
        Args:
            tile_id: ID of the tile
            tile_size: Size of the tile in pixels
            
        Returns:
            Pygame surface for the tile, or None if not available
        """
        cache_key = (tile_id, tile_size)
        
        if cache_key in self.tile_cache:
            return self.tile_cache[cache_key]
        
        # Map tile IDs to image files
        tile_image_map = {
            1: "tile_wall.png",
            2: "tile_floor.png", 
            3: "tile_stone.png"
        }
        
        # Try to load tile image from resource manager
        if tile_id in tile_image_map:
            tile_image_path = tile_image_map[tile_id]
            try:
                tile_surface = self.resource_manager.load_image(tile_image_path)
                if tile_surface:
                    # Scale to correct tile size if needed
                    if tile_surface.get_width() != tile_size or tile_surface.get_height() != tile_size:
                        tile_surface = pygame.transform.scale(tile_surface, (tile_size, tile_size))
                    
                    self.tile_cache[cache_key] = tile_surface
                    return tile_surface
            except:
                pass  # Fall back to generated tile
        
        # Generate a simple colored tile if image not found
        tile_surface = self._generate_tile_surface(tile_id, tile_size)
        self.tile_cache[cache_key] = tile_surface
        return tile_surface
    
    def _generate_tile_surface(self, tile_id: int, tile_size: int) -> pygame.Surface:
        """
        Generate a simple colored tile surface for testing.
        
        Args:
            tile_id: ID of the tile
            tile_size: Size of the tile in pixels
            
        Returns:
            Generated pygame surface
        """
        surface = pygame.Surface((tile_size, tile_size))
        
        # Simple color mapping for different tile IDs
        colors = {
            1: (100, 100, 100),  # Gray - walls
            2: (50, 150, 50),    # Green - grass
            3: (139, 69, 19),    # Brown - dirt/stone
            4: (0, 100, 200),    # Blue - water
            5: (200, 200, 0),    # Yellow - sand
        }
        
        color = colors.get(tile_id, (200, 0, 200))  # Default magenta for unknown tiles
        surface.fill(color)
        
        # Add a simple border for visibility
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 1)
        
        return surface
    
    def clear_tile_cache(self) -> None:
        """Clear the tile cache to free memory."""
        self.tile_cache.clear()
    
    def preload_tiles(self, tile_ids: list, tile_size: int) -> None:
        """
        Preload tiles into cache.
        
        Args:
            tile_ids: List of tile IDs to preload
            tile_size: Size of tiles in pixels
        """
        for tile_id in tile_ids:
            self._get_tile_surface(tile_id, tile_size)