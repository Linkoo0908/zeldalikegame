"""
Inventory system for managing player items.
"""
from typing import List, Optional, Dict, Any
from src.objects.item import Item


class Inventory:
    """
    Player inventory management system.
    """
    
    def __init__(self, max_size: int = 20):
        """
        Initialize the inventory.
        
        Args:
            max_size: Maximum number of items the inventory can hold
        """
        self.max_size = max_size
        self.items: List[Item] = []
        self.equipped_items: Dict[str, Item] = {
            'weapon': None,
            'armor': None,
            'equipment': None
        }
    
    def add_item(self, item: Item) -> bool:
        """
        Add an item to the inventory.
        
        Args:
            item: Item to add
            
        Returns:
            True if item was added successfully, False if inventory is full
        """
        if self.is_full():
            return False
        
        # Check if we can stack this item with existing items
        if self._try_stack_item(item):
            return True
        
        # Add as new item
        self.items.append(item)
        return True
    
    def remove_item(self, item: Item) -> bool:
        """
        Remove an item from the inventory.
        
        Args:
            item: Item to remove
            
        Returns:
            True if item was removed, False if item not found
        """
        if item in self.items:
            self.items.remove(item)
            return True
        return False
    
    def remove_item_by_index(self, index: int) -> Optional[Item]:
        """
        Remove an item by its index in the inventory.
        
        Args:
            index: Index of item to remove
            
        Returns:
            Removed item, or None if index is invalid
        """
        if 0 <= index < len(self.items):
            return self.items.pop(index)
        return None
    
    def get_item_by_index(self, index: int) -> Optional[Item]:
        """
        Get an item by its index in the inventory.
        
        Args:
            index: Index of item to get
            
        Returns:
            Item at index, or None if index is invalid
        """
        if 0 <= index < len(self.items):
            return self.items[index]
        return None
    
    def find_items_by_type(self, item_type: str) -> List[Item]:
        """
        Find all items of a specific type.
        
        Args:
            item_type: Type of items to find
            
        Returns:
            List of items of the specified type
        """
        return [item for item in self.items if item.item_type == item_type]
    
    def find_items_by_category(self, category: str) -> List[Item]:
        """
        Find all items of a specific category.
        
        Args:
            category: Category of items to find
            
        Returns:
            List of items of the specified category
        """
        return [item for item in self.items if item.category == category]
    
    def get_consumables(self) -> List[Item]:
        """
        Get all consumable items.
        
        Returns:
            List of consumable items
        """
        return self.find_items_by_category('consumable')
    
    def get_weapons(self) -> List[Item]:
        """
        Get all weapon items.
        
        Returns:
            List of weapon items
        """
        return self.find_items_by_category('weapon')
    
    def get_armor(self) -> List[Item]:
        """
        Get all armor items.
        
        Returns:
            List of armor items
        """
        return self.find_items_by_category('armor')
    
    def get_equipment(self) -> List[Item]:
        """
        Get all equipment items.
        
        Returns:
            List of equipment items
        """
        return self.find_items_by_category('equipment')
    
    def is_full(self) -> bool:
        """
        Check if the inventory is full.
        
        Returns:
            True if inventory is full, False otherwise
        """
        return len(self.items) >= self.max_size
    
    def is_empty(self) -> bool:
        """
        Check if the inventory is empty.
        
        Returns:
            True if inventory is empty, False otherwise
        """
        return len(self.items) == 0
    
    def get_item_count(self) -> int:
        """
        Get the number of items in the inventory.
        
        Returns:
            Number of items in inventory
        """
        return len(self.items)
    
    def get_free_space(self) -> int:
        """
        Get the number of free slots in the inventory.
        
        Returns:
            Number of free slots
        """
        return self.max_size - len(self.items)
    
    def clear(self) -> None:
        """Clear all items from the inventory."""
        self.items.clear()
        for slot in self.equipped_items:
            self.equipped_items[slot] = None
    
    def equip_item(self, item: Item, player=None) -> bool:
        """
        Equip an item from the inventory.
        
        Args:
            item: Item to equip
            player: Player to apply effects to (optional)
            
        Returns:
            True if item was equipped successfully
        """
        if item not in self.items:
            return False
        
        if item.category not in self.equipped_items:
            return False
        
        # Unequip current item if any
        current_equipped = self.equipped_items[item.category]
        if current_equipped:
            self._unapply_item_effects(current_equipped, player)
            # Add the previously equipped item back to inventory
            self.add_item(current_equipped)
        
        # Equip new item
        self.equipped_items[item.category] = item
        self.remove_item(item)
        
        # Apply item effects
        if player:
            self._apply_item_effects(item, player)
        
        return True
    
    def unequip_item(self, item: Item, player=None) -> bool:
        """
        Unequip an item and return it to inventory.
        
        Args:
            item: Item to unequip
            player: Player to remove effects from (optional)
            
        Returns:
            True if item was unequipped successfully
        """
        for slot, equipped_item in self.equipped_items.items():
            if equipped_item == item:
                if self.is_full():
                    return False  # Can't unequip if inventory is full
                
                self.equipped_items[slot] = None
                
                # Remove item effects
                if player:
                    self._unapply_item_effects(item, player)
                
                self.add_item(item)
                return True
        
        return False
    
    def get_equipped_item(self, slot: str) -> Optional[Item]:
        """
        Get the currently equipped item in a slot.
        
        Args:
            slot: Equipment slot ('weapon', 'armor', 'equipment')
            
        Returns:
            Equipped item, or None if slot is empty
        """
        return self.equipped_items.get(slot)
    
    def is_item_equipped(self, item: Item) -> bool:
        """
        Check if an item is currently equipped.
        
        Args:
            item: Item to check
            
        Returns:
            True if item is equipped, False otherwise
        """
        return item in self.equipped_items.values()
    
    def use_item(self, item: Item, player) -> bool:
        """
        Use an item from the inventory.
        
        Args:
            item: Item to use
            player: Player to use item on
            
        Returns:
            True if item was used successfully
        """
        if item not in self.items:
            return False
        
        # Use the item
        success = item.use_on_player(player)
        
        if success and item.category == 'consumable':
            # Remove consumable items after use
            self.remove_item(item)
        elif success and item.category in ['weapon', 'armor', 'equipment']:
            # Equipment items get equipped
            self.equip_item(item, player)
        
        return success
    
    def use_item_by_index(self, index: int, player) -> bool:
        """
        Use an item by its index in the inventory.
        
        Args:
            index: Index of item to use
            player: Player to use item on
            
        Returns:
            True if item was used successfully
        """
        item = self.get_item_by_index(index)
        if item:
            return self.use_item(item, player)
        return False
    
    def _try_stack_item(self, item: Item) -> bool:
        """
        Try to stack an item with existing items (for future stackable items).
        
        Args:
            item: Item to try to stack
            
        Returns:
            True if item was stacked, False otherwise
        """
        # For now, items don't stack
        # This could be extended in the future for stackable consumables
        return False
    
    def get_inventory_info(self) -> Dict[str, Any]:
        """
        Get detailed information about the inventory.
        
        Returns:
            Dictionary containing inventory information
        """
        return {
            'max_size': self.max_size,
            'current_size': len(self.items),
            'free_space': self.get_free_space(),
            'is_full': self.is_full(),
            'is_empty': self.is_empty(),
            'items': [item.get_info() for item in self.items],
            'equipped_items': {
                slot: item.get_info() if item else None 
                for slot, item in self.equipped_items.items()
            },
            'item_counts_by_category': {
                'consumable': len(self.get_consumables()),
                'weapon': len(self.get_weapons()),
                'armor': len(self.get_armor()),
                'equipment': len(self.get_equipment())
            }
        }
    
    def sort_items(self, sort_by: str = 'category') -> None:
        """
        Sort items in the inventory.
        
        Args:
            sort_by: Sorting criteria ('category', 'name', 'type')
        """
        if sort_by == 'category':
            self.items.sort(key=lambda item: item.category)
        elif sort_by == 'name':
            self.items.sort(key=lambda item: item.name)
        elif sort_by == 'type':
            self.items.sort(key=lambda item: item.item_type)
    
    def get_items_list(self) -> List[Item]:
        """
        Get a copy of the items list.
        
        Returns:
            Copy of the items list
        """
        return self.items.copy()
    
    def has_item(self, item: Item) -> bool:
        """
        Check if the inventory contains a specific item.
        
        Args:
            item: Item to check for
            
        Returns:
            True if item is in inventory, False otherwise
        """
        return item in self.items
    
    def has_item_type(self, item_type: str) -> bool:
        """
        Check if the inventory contains any item of a specific type.
        
        Args:
            item_type: Type of item to check for
            
        Returns:
            True if inventory contains item of this type, False otherwise
        """
        return len(self.find_items_by_type(item_type)) > 0
    
    def count_item_type(self, item_type: str) -> int:
        """
        Count how many items of a specific type are in the inventory.
        
        Args:
            item_type: Type of item to count
            
        Returns:
            Number of items of the specified type
        """
        return len(self.find_items_by_type(item_type))
    
    def _apply_item_effects(self, item: Item, player) -> None:
        """
        Apply item effects to the player.
        
        Args:
            item: Item whose effects to apply
            player: Player to apply effects to
        """
        if not player:
            return
        
        if 'attack' in item.effect:
            player.attack_damage += item.effect['attack']
        if 'defense' in item.effect:
            # TODO: Implement defense system
            print(f"Player defense increased by {item.effect['defense']}")
        if 'speed' in item.effect:
            player.set_speed_modifier(item.effect['speed'])
        if 'health_regen' in item.effect:
            player.health_regen_rate += item.effect['health_regen']
            print(f"Health regeneration increased by {item.effect['health_regen']} per second")
    
    def _unapply_item_effects(self, item: Item, player) -> None:
        """
        Remove item effects from the player.
        
        Args:
            item: Item whose effects to remove
            player: Player to remove effects from
        """
        if not player:
            return
        
        if 'attack' in item.effect:
            player.attack_damage -= item.effect['attack']
        if 'defense' in item.effect:
            # TODO: Implement defense system
            print(f"Player defense decreased by {item.effect['defense']}")
        if 'speed' in item.effect:
            player.reset_speed()  # Reset to base speed
        if 'health_regen' in item.effect:
            player.health_regen_rate -= item.effect['health_regen']
            print(f"Health regeneration decreased by {item.effect['health_regen']} per second")