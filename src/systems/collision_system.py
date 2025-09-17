"""
Collision detection and handling system.
"""
import pygame
from typing import Dict, Any, Optional, Tuple, List
from src.objects.game_object import GameObject
from src.systems.map_system import MapSystem


class CollisionSystem:
    """Handles collision detection and resolution."""
    
    def __init__(self, map_system: MapSystem):
        """
        Initialize collision system.
        
        Args:
            map_system: Map system for tile collision detection
        """
        self.map_system = map_system
    
    def check_aabb_collision(self, obj1: GameObject, obj2: GameObject) -> bool:
        """
        Check AABB (Axis-Aligned Bounding Box) collision between two objects.
        
        Args:
            obj1: First game object
            obj2: Second game object
            
        Returns:
            True if objects are colliding, False otherwise
        """
        rect1 = obj1.get_bounds()
        rect2 = obj2.get_bounds()
        
        return self._check_rect_collision(rect1, rect2)
    
    def check_point_collision(self, point_x: float, point_y: float, obj: GameObject) -> bool:
        """
        Check if a point collides with an object.
        
        Args:
            point_x: X coordinate of the point
            point_y: Y coordinate of the point
            obj: Game object to check collision with
            
        Returns:
            True if point is inside object bounds, False otherwise
        """
        bounds = obj.get_bounds()
        return (bounds.left <= point_x <= bounds.right and 
                bounds.top <= point_y <= bounds.bottom)
    
    def check_map_collision(self, obj: GameObject, new_x: float, new_y: float) -> bool:
        """
        Check if an object would collide with solid map tiles at a new position.
        
        Args:
            obj: Game object to check
            new_x: New X position to check
            new_y: New Y position to check
            
        Returns:
            True if collision would occur, False otherwise
        """
        if not self.map_system.get_current_map():
            return False
        
        # Get object bounds at new position
        width = obj.width
        height = obj.height
        
        # Check collision at multiple points around the object
        collision_points = [
            (new_x, new_y),                    # Top-left
            (new_x + width - 1, new_y),        # Top-right
            (new_x, new_y + height - 1),       # Bottom-left
            (new_x + width - 1, new_y + height - 1)  # Bottom-right
        ]
        
        # Also check center points for better collision detection
        collision_points.extend([
            (new_x + width // 2, new_y),       # Top-center
            (new_x + width // 2, new_y + height - 1),  # Bottom-center
            (new_x, new_y + height // 2),      # Left-center
            (new_x + width - 1, new_y + height // 2)   # Right-center
        ])
        
        for point_x, point_y in collision_points:
            tile_x, tile_y = self.map_system.world_to_tile(point_x, point_y)
            if self.map_system.is_tile_solid(tile_x, tile_y):
                return True
        
        return False
    
    def resolve_map_collision(self, obj: GameObject, old_x: float, old_y: float, 
                             new_x: float, new_y: float) -> Tuple[float, float]:
        """
        Resolve collision with map tiles by finding valid position.
        
        Args:
            obj: Game object
            old_x: Previous X position
            old_y: Previous Y position
            new_x: Attempted new X position
            new_y: Attempted new Y position
            
        Returns:
            Tuple of (resolved_x, resolved_y) - valid position
        """
        # Try X movement only
        if not self.check_map_collision(obj, new_x, old_y):
            # X movement is valid, check Y
            if not self.check_map_collision(obj, new_x, new_y):
                return (new_x, new_y)  # Both movements valid
            else:
                return (new_x, old_y)  # Only X movement valid
        
        # Try Y movement only
        if not self.check_map_collision(obj, old_x, new_y):
            return (old_x, new_y)  # Only Y movement valid
        
        # No movement possible
        return (old_x, old_y)
    
    def get_collision_objects(self, obj: GameObject, objects: List[GameObject]) -> List[GameObject]:
        """
        Get all objects that are colliding with the given object.
        
        Args:
            obj: Object to check collisions for
            objects: List of objects to check against
            
        Returns:
            List of objects that are colliding with obj
        """
        colliding_objects = []
        
        for other_obj in objects:
            if other_obj != obj and self.check_aabb_collision(obj, other_obj):
                colliding_objects.append(other_obj)
        
        return colliding_objects
    
    def separate_objects(self, obj1: GameObject, obj2: GameObject) -> None:
        """
        Separate two colliding objects by moving them apart.
        
        Args:
            obj1: First object
            obj2: Second object
        """
        rect1 = obj1.get_bounds()
        rect2 = obj2.get_bounds()
        
        # Calculate overlap
        overlap_x = min(rect1.right - rect2.left, rect2.right - rect1.left)
        overlap_y = min(rect1.bottom - rect2.top, rect2.bottom - rect1.top)
        
        # Separate along the axis with smaller overlap
        if overlap_x < overlap_y:
            # Separate horizontally
            if rect1.centerx < rect2.centerx:
                # obj1 is to the left
                obj1.x -= overlap_x / 2
                obj2.x += overlap_x / 2
            else:
                # obj1 is to the right
                obj1.x += overlap_x / 2
                obj2.x -= overlap_x / 2
        else:
            # Separate vertically
            if rect1.centery < rect2.centery:
                # obj1 is above
                obj1.y -= overlap_y / 2
                obj2.y += overlap_y / 2
            else:
                # obj1 is below
                obj1.y += overlap_y / 2
                obj2.y -= overlap_y / 2
    
    def _check_rect_collision(self, rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        """
        Check collision between two rectangles.
        
        Args:
            rect1: First rectangle
            rect2: Second rectangle
            
        Returns:
            True if rectangles overlap, False otherwise
        """
        return rect1.colliderect(rect2)
    
    def get_collision_direction(self, obj1: GameObject, obj2: GameObject) -> str:
        """
        Get the direction of collision between two objects.
        
        Args:
            obj1: First object (usually the moving object)
            obj2: Second object (usually the stationary object)
            
        Returns:
            String indicating collision direction: 'top', 'bottom', 'left', 'right'
        """
        rect1 = obj1.get_bounds()
        rect2 = obj2.get_bounds()
        
        # Calculate overlap on each axis
        overlap_x = min(rect1.right - rect2.left, rect2.right - rect1.left)
        overlap_y = min(rect1.bottom - rect2.top, rect2.bottom - rect1.top)
        
        # The direction is determined by the smaller overlap
        if overlap_x < overlap_y:
            # Horizontal collision
            if rect1.centerx < rect2.centerx:
                return 'right'  # obj1 hit obj2 from the left
            else:
                return 'left'   # obj1 hit obj2 from the right
        else:
            # Vertical collision
            if rect1.centery < rect2.centery:
                return 'bottom'  # obj1 hit obj2 from above
            else:
                return 'top'     # obj1 hit obj2 from below
    
    def check_circle_collision(self, obj1_x: float, obj1_y: float, obj1_radius: float,
                              obj2_x: float, obj2_y: float, obj2_radius: float) -> bool:
        """
        Check collision between two circles.
        
        Args:
            obj1_x: X position of first circle center
            obj1_y: Y position of first circle center
            obj1_radius: Radius of first circle
            obj2_x: X position of second circle center
            obj2_y: Y position of second circle center
            obj2_radius: Radius of second circle
            
        Returns:
            True if circles overlap, False otherwise
        """
        distance_squared = (obj1_x - obj2_x) ** 2 + (obj1_y - obj2_y) ** 2
        radius_sum_squared = (obj1_radius + obj2_radius) ** 2
        
        return distance_squared <= radius_sum_squared
    
    def get_nearest_non_colliding_position(self, obj: GameObject, target_x: float, target_y: float,
                                         step_size: float = 1.0) -> Tuple[float, float]:
        """
        Find the nearest position to target that doesn't collide with map.
        
        Args:
            obj: Game object
            target_x: Target X position
            target_y: Target Y position
            step_size: Step size for position search
            
        Returns:
            Tuple of (x, y) - nearest valid position
        """
        current_x, current_y = obj.x, obj.y
        
        # If target position is valid, return it
        if not self.check_map_collision(obj, target_x, target_y):
            return (target_x, target_y)
        
        # Search in expanding circles around current position
        max_search_distance = 100  # Maximum search distance
        
        for distance in range(int(step_size), max_search_distance, int(step_size)):
            # Check positions in a circle around current position
            for angle in range(0, 360, 15):  # Check every 15 degrees
                import math
                search_x = current_x + distance * math.cos(math.radians(angle))
                search_y = current_y + distance * math.sin(math.radians(angle))
                
                if not self.check_map_collision(obj, search_x, search_y):
                    return (search_x, search_y)
        
        # If no valid position found, return current position
        return (current_x, current_y)