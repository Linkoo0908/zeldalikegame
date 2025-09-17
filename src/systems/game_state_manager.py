"""
Game state manager for preserving game state during map transitions.
Handles saving and loading of player data, inventory, and map-specific states.
"""
from typing import Dict, List, Any, Optional
import json
import os


class GameStateManager:
    """Manages game state persistence across map transitions."""
    
    def __init__(self):
        """Initialize the game state manager."""
        self.player_state = {}
        self.global_flags = {}
        self.map_visit_count = {}
        self.total_playtime = 0.0
        self.save_file_path = "save_game.json"
    
    def save_player_state(self, player) -> None:
        """
        Save current player state.
        
        Args:
            player: Player object to save state from
        """
        if not player:
            return
        
        self.player_state = {
            'position': {'x': player.x, 'y': player.y},
            'health': {
                'current': getattr(player, 'current_health', 100),
                'max': getattr(player, 'max_health', 100)
            },
            'experience': getattr(player, 'experience', 0),
            'level': getattr(player, 'level', 1),
            'stats': {
                'attack': getattr(player, 'attack_power', 10),
                'defense': getattr(player, 'defense', 5),
                'speed': getattr(player, 'speed', 100)
            }
        }
    
    def restore_player_state(self, player) -> None:
        """
        Restore player state from saved data.
        
        Args:
            player: Player object to restore state to
        """
        if not player or not self.player_state:
            return
        
        # Restore position
        if 'position' in self.player_state:
            pos = self.player_state['position']
            player.x = pos.get('x', player.x)
            player.y = pos.get('y', player.y)
        
        # Restore health
        if 'health' in self.player_state:
            health = self.player_state['health']
            if hasattr(player, 'current_health'):
                player.current_health = health.get('current', player.current_health)
            if hasattr(player, 'max_health'):
                player.max_health = health.get('max', player.max_health)
        
        # Restore experience and level
        if hasattr(player, 'experience'):
            player.experience = self.player_state.get('experience', player.experience)
        if hasattr(player, 'level'):
            player.level = self.player_state.get('level', player.level)
        
        # Restore stats
        if 'stats' in self.player_state:
            stats = self.player_state['stats']
            if hasattr(player, 'attack_power'):
                player.attack_power = stats.get('attack', player.attack_power)
            if hasattr(player, 'defense'):
                player.defense = stats.get('defense', player.defense)
            if hasattr(player, 'speed'):
                player.speed = stats.get('speed', player.speed)
    
    def save_inventory_state(self, inventory) -> None:
        """
        Save current inventory state.
        
        Args:
            inventory: Inventory object to save state from
        """
        if not inventory:
            return
        
        # Save inventory items
        items = []
        if hasattr(inventory, 'items'):
            for item in inventory.items:
                if hasattr(item, 'item_type'):
                    items.append({
                        'type': item.item_type,
                        'quantity': getattr(item, 'quantity', 1)
                    })
        
        self.player_state['inventory'] = {
            'items': items,
            'max_size': getattr(inventory, 'max_size', 20)
        }
    
    def restore_inventory_state(self, inventory) -> None:
        """
        Restore inventory state from saved data.
        
        Args:
            inventory: Inventory object to restore state to
        """
        if not inventory or 'inventory' not in self.player_state:
            return
        
        inv_data = self.player_state['inventory']
        
        # Clear current inventory
        if hasattr(inventory, 'clear'):
            inventory.clear()
        elif hasattr(inventory, 'items'):
            inventory.items.clear()
        
        # Restore items
        items = inv_data.get('items', [])
        for item_data in items:
            # This would need to be implemented based on your item system
            # For now, we just store the data
            pass
    
    def set_global_flag(self, flag_name: str, value: Any) -> None:
        """
        Set a global game flag.
        
        Args:
            flag_name: Name of the flag
            value: Value to set
        """
        self.global_flags[flag_name] = value
    
    def get_global_flag(self, flag_name: str, default: Any = None) -> Any:
        """
        Get a global game flag.
        
        Args:
            flag_name: Name of the flag
            default: Default value if flag doesn't exist
            
        Returns:
            Flag value or default
        """
        return self.global_flags.get(flag_name, default)
    
    def increment_map_visit(self, map_path: str) -> int:
        """
        Increment visit count for a map.
        
        Args:
            map_path: Path to the map file
            
        Returns:
            New visit count
        """
        self.map_visit_count[map_path] = self.map_visit_count.get(map_path, 0) + 1
        return self.map_visit_count[map_path]
    
    def get_map_visit_count(self, map_path: str) -> int:
        """
        Get visit count for a map.
        
        Args:
            map_path: Path to the map file
            
        Returns:
            Visit count (0 if never visited)
        """
        return self.map_visit_count.get(map_path, 0)
    
    def add_playtime(self, delta_time: float) -> None:
        """
        Add to total playtime.
        
        Args:
            delta_time: Time to add in seconds
        """
        self.total_playtime += delta_time
    
    def get_playtime(self) -> float:
        """
        Get total playtime in seconds.
        
        Returns:
            Total playtime in seconds
        """
        return self.total_playtime
    
    def get_playtime_formatted(self) -> str:
        """
        Get formatted playtime string.
        
        Returns:
            Formatted playtime (e.g., "1h 23m 45s")
        """
        total_seconds = int(self.total_playtime)
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        
        if hours > 0:
            return f"{hours}h {minutes}m {seconds}s"
        elif minutes > 0:
            return f"{minutes}m {seconds}s"
        else:
            return f"{seconds}s"
    
    def create_save_data(self) -> Dict[str, Any]:
        """
        Create a complete save data dictionary.
        
        Returns:
            Dictionary containing all save data
        """
        return {
            'player_state': self.player_state,
            'global_flags': self.global_flags,
            'map_visit_count': self.map_visit_count,
            'total_playtime': self.total_playtime,
            'version': '1.0'
        }
    
    def load_save_data(self, save_data: Dict[str, Any]) -> None:
        """
        Load save data from dictionary.
        
        Args:
            save_data: Dictionary containing save data
        """
        self.player_state = save_data.get('player_state', {})
        self.global_flags = save_data.get('global_flags', {})
        self.map_visit_count = save_data.get('map_visit_count', {})
        self.total_playtime = save_data.get('total_playtime', 0.0)
    
    def save_to_file(self, file_path: str = None) -> bool:
        """
        Save game state to file.
        
        Args:
            file_path: Path to save file (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if file_path:
            self.save_file_path = file_path
        
        try:
            save_data = self.create_save_data()
            with open(self.save_file_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Failed to save game state: {e}")
            return False
    
    def load_from_file(self, file_path: str = None) -> bool:
        """
        Load game state from file.
        
        Args:
            file_path: Path to save file (optional)
            
        Returns:
            True if successful, False otherwise
        """
        if file_path:
            self.save_file_path = file_path
        
        if not os.path.exists(self.save_file_path):
            return False
        
        try:
            with open(self.save_file_path, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            self.load_save_data(save_data)
            return True
        except Exception as e:
            print(f"Failed to load game state: {e}")
            return False
    
    def reset_state(self) -> None:
        """Reset all game state to defaults."""
        self.player_state.clear()
        self.global_flags.clear()
        self.map_visit_count.clear()
        self.total_playtime = 0.0
    
    def get_state_summary(self) -> Dict[str, Any]:
        """
        Get a summary of current game state.
        
        Returns:
            Dictionary with state summary
        """
        return {
            'has_player_state': bool(self.player_state),
            'global_flags_count': len(self.global_flags),
            'maps_visited': len(self.map_visit_count),
            'total_playtime': self.get_playtime_formatted(),
            'player_level': self.player_state.get('level', 1),
            'player_health': self.player_state.get('health', {}).get('current', 0)
        }