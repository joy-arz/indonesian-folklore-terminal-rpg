"""
Player module - handles player stats, inventory, equipment, XP/leveling, and status effects.

This module defines the Player class which manages:
- Character stats (HP, max HP, attack, defense, gold)
- Equipment system (weapon, armor, accessory)
- Inventory system for collecting and using items
- XP and leveling system
- Status effects (buffs and debuffs)
"""

import random
from typing import Dict, List, Optional, Any
from enum import Enum


class ItemCategory(Enum):
    """Categories of items in the game."""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"


class Item:
    """Represents an item in the game."""
    
    ITEM_DATABASE = {
        "keris kecil": {"category": ItemCategory.WEAPON, "attack": 3, "defense": 0, "value": 15, "rarity": "common"},
        "keris naga": {"category": ItemCategory.WEAPON, "attack": 12, "defense": 0, "value": 100, "rarity": "rare"},
        "keris pusaka": {"category": ItemCategory.WEAPON, "attack": 18, "defense": 0, "value": 250, "rarity": "legendary"},
        "tombak": {"category": ItemCategory.WEAPON, "attack": 5, "defense": 0, "value": 25, "rarity": "common"},
        "tombak panjang": {"category": ItemCategory.WEAPON, "attack": 8, "defense": 0, "value": 50, "rarity": "uncommon"},
        "pedang lengkung": {"category": ItemCategory.WEAPON, "attack": 7, "defense": 0, "value": 40, "rarity": "common"},
        "pedang naga": {"category": ItemCategory.WEAPON, "attack": 14, "defense": 0, "value": 150, "rarity": "rare"},
        "parang": {"category": ItemCategory.WEAPON, "attack": 4, "defense": 0, "value": 20, "rarity": "common"},
        "kris": {"category": ItemCategory.WEAPON, "attack": 6, "defense": 0, "value": 35, "rarity": "common"},
        "golok": {"category": ItemCategory.WEAPON, "attack": 5, "defense": 0, "value": 25, "rarity": "common"},
        "baju zirah": {"category": ItemCategory.ARMOR, "attack": 0, "defense": 5, "value": 40, "rarity": "common"},
        "baju besi": {"category": ItemCategory.ARMOR, "attack": 0, "defense": 8, "value": 70, "rarity": "uncommon"},
        "baju perang": {"category": ItemCategory.ARMOR, "attack": 0, "defense": 12, "value": 150, "rarity": "rare"},
        "perisai kayu": {"category": ItemCategory.ARMOR, "attack": 0, "defense": 3, "value": 15, "rarity": "common"},
        "perisai besi": {"category": ItemCategory.ARMOR, "attack": 0, "defense": 6, "value": 35, "rarity": "uncommon"},
        "perisai sakti": {"category": ItemCategory.ARMOR, "attack": 2, "defense": 10, "value": 120, "rarity": "rare"},
        "jubah santri": {"category": ItemCategory.ARMOR, "attack": 1, "defense": 4, "value": 30, "rarity": "common"},
        "jubah dukun": {"category": ItemCategory.ARMOR, "attack": 3, "defense": 5, "value": 60, "rarity": "uncommon"},
        "jimat perlindungan": {"category": ItemCategory.ACCESSORY, "attack": 2, "defense": 3, "value": 50, "rarity": "uncommon"},
        "cincin sakti": {"category": ItemCategory.ACCESSORY, "attack": 4, "defense": 2, "value": 70, "rarity": "rare"},
        "kalung keramat": {"category": ItemCategory.ACCESSORY, "attack": 5, "defense": 4, "value": 100, "rarity": "rare"},
        "gelang emas": {"category": ItemCategory.ACCESSORY, "attack": 1, "defense": 1, "value": 30, "rarity": "common"},
        "ikat kepala": {"category": ItemCategory.ACCESSORY, "attack": 2, "defense": 2, "value": 25, "rarity": "common"},
        "jamu": {"category": ItemCategory.CONSUMABLE, "heal": 10, "value": 15, "rarity": "common"},
        "jamu kuat": {"category": ItemCategory.CONSUMABLE, "heal": 25, "value": 35, "rarity": "uncommon"},
        "jamu sakti": {"category": ItemCategory.CONSUMABLE, "heal": 50, "value": 70, "rarity": "rare"},
        "nasi bungkus": {"category": ItemCategory.CONSUMABLE, "heal": 5, "value": 5, "rarity": "common"},
        "buah-buahan": {"category": ItemCategory.CONSUMABLE, "heal": 8, "value": 8, "rarity": "common"},
        "kemenyan": {"category": ItemCategory.CONSUMABLE, "cure": "poison", "value": 20, "rarity": "common"},
        "minyak kelapa": {"category": ItemCategory.CONSUMABLE, "heal": 15, "value": 18, "rarity": "common"},
        "rempah-rempah": {"category": ItemCategory.MATERIAL, "value": 20, "rarity": "common"},
        "emas batangan": {"category": ItemCategory.MATERIAL, "value": 50, "rarity": "uncommon"},
        "mutiara": {"category": ItemCategory.MATERIAL, "value": 80, "rarity": "rare"},
        "batu akik": {"category": ItemCategory.MATERIAL, "value": 30, "rarity": "common"},
    }
    
    def __init__(self, name: str, quantity: int = 1):
        """
        Initialize an item.
        
        Args:
            name: Item name (must be in ITEM_DATABASE)
            quantity: Stack quantity
        """
        self.name = name.lower()
        self.quantity = quantity
        
        if self.name in Item.ITEM_DATABASE:
            data = Item.ITEM_DATABASE[self.name]
            self.category = data["category"]
            self.attack = data.get("attack", 0)
            self.defense = data.get("defense", 0)
            self.heal = data.get("heal", 0)
            self.mana = data.get("mana", 0)
            self.cure = data.get("cure", None)
            self.value = data.get("value", 1)
            self.rarity = data.get("rarity", "common")
        else:
            self.category = ItemCategory.MATERIAL
            self.attack = 0
            self.defense = 0
            self.heal = 0
            self.mana = 0
            self.cure = None
            self.value = 1
            self.rarity = "common"
    
    def to_dict(self) -> dict:
        """Convert item to dictionary for saving."""
        return {
            "name": self.name,
            "quantity": self.quantity
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        """Create item from saved data."""
        return cls(data["name"], data.get("quantity", 1))
    
    def __repr__(self) -> str:
        return f"Item({self.name}, qty={self.quantity})"


class StatusEffect:
    """Represents a status effect (buff or debuff)."""
    
    EFFECT_TYPES = {
        "poison": {"damage": 3, "duration": 3, "type": "debuff"},
        "burn": {"damage": 2, "duration": 3, "type": "debuff"},
        "freeze": {"damage": 0, "duration": 1, "type": "debuff", "skip_turn_chance": 0.5},
        "stun": {"damage": 0, "duration": 1, "type": "debuff", "skip_turn_chance": 1.0},
        "bleed": {"damage": 2, "duration": 4, "type": "debuff"},
        "strength": {"attack_bonus": 3, "duration": 3, "type": "buff"},
        "defense": {"defense_bonus": 3, "duration": 3, "type": "buff"},
        "haste": {"attack_bonus": 2, "duration": 2, "type": "buff"},
        "shield": {"defense_bonus": 5, "duration": 2, "type": "buff"},
        "regeneration": {"heal": 5, "duration": 5, "type": "buff"},
    }
    
    def __init__(self, name: str, duration: Optional[int] = None):
        """
        Initialize a status effect.
        
        Args:
            name: Effect name
            duration: Override default duration
        """
        self.name = name.lower()
        if self.name in self.EFFECT_TYPES:
            data = self.EFFECT_TYPES[self.name]
            self.effect_type = data["type"]
            self.duration = duration if duration else data["duration"]
            self.damage = data.get("damage", 0)
            self.attack_bonus = data.get("attack_bonus", 0)
            self.defense_bonus = data.get("defense_bonus", 0)
            self.heal = data.get("heal", 0)
            self.skip_turn_chance = data.get("skip_turn_chance", 0)
        else:
            self.effect_type = "debuff"
            self.duration = duration if duration else 3
            self.damage = 0
            self.attack_bonus = 0
            self.defense_bonus = 0
            self.heal = 0
            self.skip_turn_chance = 0
    
    def to_dict(self) -> dict:
        """Convert effect to dictionary for saving."""
        return {
            "name": self.name,
            "duration": self.duration
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "StatusEffect":
        """Create effect from saved data."""
        return cls(data["name"], data.get("duration", 3))


class Player:
    """
    Represents the player character with stats, equipment, and inventory.
    
    Attributes:
        hp (int): Current health points
        max_hp (int): Maximum health points
        attack (int): Base attack power
        defense (int): Base defense rating
        gold (int): Currency collected
        level (int): Current character level
        xp (int): Current experience points
        xp_to_level (int): XP needed for next level
        inventory (List[Item]): Items owned
        equipment (dict): Currently equipped items
        status_effects (List[StatusEffect]): Active buffs/debuffs
    """
    
    def __init__(self):
        """Initialize player with starting stats."""
        self.hp = 20
        self.max_hp = 20
        self.base_attack = 5
        self.base_defense = 3
        self.gold = 0
        self.level = 1
        self.xp = 0
        self.xp_to_level = 100
        self.inventory: List[Item] = []
        self.equipment = {
            "weapon": None,
            "armor": None,
            "accessory": None
        }
        self.status_effects: List[StatusEffect] = []
    
    @property
    def attack(self) -> int:
        """Get total attack (base + equipment + buffs)."""
        total = self.base_attack
        for slot, item in self.equipment.items():
            if item:
                total += item.attack
        for effect in self.status_effects:
            total += effect.attack_bonus
        return max(1, total)
    
    @property
    def defense(self) -> int:
        """Get total defense (base + equipment + buffs)."""
        total = self.base_defense
        for slot, item in self.equipment.items():
            if item:
                total += item.defense
        for effect in self.status_effects:
            total += effect.defense_bonus
        return max(0, total)
    
    def get_equipment_stats(self) -> dict:
        """Get stats bonus from equipment."""
        attack_bonus = sum(i.attack for i in self.equipment.values() if i)
        defense_bonus = sum(i.defense for i in self.equipment.values() if i)
        return {"attack": attack_bonus, "defense": defense_bonus}
    
    def take_damage(self, amount: int) -> int:
        """
        Reduce HP by the given amount (after defense mitigation).
        
        Args:
            amount: Raw damage amount before defense
            
        Returns:
            int: Actual damage taken after defense
        """
        actual_damage = max(1, amount - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def heal(self, amount: int) -> int:
        """
        Restore HP by the given amount.
        
        Args:
            amount: Amount of HP to restore
            
        Returns:
            int: Actual HP restored (may be less if near max)
        """
        old_hp = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - old_hp
    
    def add_xp(self, amount: int) -> bool:
        """
        Add experience points and check for level up.
        
        Args:
            amount: XP to add
            
        Returns:
            bool: True if player leveled up
        """
        self.xp += amount
        if self.xp >= self.xp_to_level:
            self.level_up()
            return True
        return False
    
    def level_up(self):
        """Level up the player and increase stats."""
        self.level += 1
        self.xp -= self.xp_to_level
        self.xp_to_level = int(self.xp_to_level * 1.5)
        
        self.max_hp += 5
        self.base_attack += 2
        self.base_defense += 1
        self.hp = self.max_hp
    
    def is_alive(self) -> bool:
        """Check if player is still alive."""
        return self.hp > 0
    
    def add_item(self, item_name: str, quantity: int = 1) -> bool:
        """
        Add an item to the player's inventory.
        
        Args:
            item_name: Name of the item to add
            quantity: Stack quantity
            
        Returns:
            bool: True if item was added
        """
        item_name = item_name.lower()
        
        for item in self.inventory:
            if item.name == item_name:
                item.quantity += quantity
                return True
        
        self.inventory.append(Item(item_name, quantity))
        return True
    
    def remove_item(self, item_name: str, quantity: int = 1) -> bool:
        """
        Remove an item from the player's inventory.
        
        Args:
            item_name: Name of the item to remove
            quantity: Amount to remove
            
        Returns:
            bool: True if item was removed, False if not found
        """
        item_name = item_name.lower()
        for item in self.inventory:
            if item.name == item_name:
                if item.quantity <= quantity:
                    self.inventory.remove(item)
                else:
                    item.quantity -= quantity
                return True
        return False
    
    def has_item(self, item_name: str) -> bool:
        """Check if player has a specific item."""
        item_name = item_name.lower()
        return any(item.name == item_name for item in self.inventory)
    
    def get_item_quantity(self, item_name: str) -> int:
        """Get quantity of a specific item."""
        item_name = item_name.lower()
        for item in self.inventory:
            if item.name == item_name:
                return item.quantity
        return 0
    
    def get_items_by_category(self, category: ItemCategory) -> List[Item]:
        """Get all items of a specific category."""
        return [item for item in self.inventory if item.category == category]
    
    def equip_item(self, item_name: str) -> tuple[bool, str]:
        """
        Equip an item from inventory.
        
        Args:
            item_name: Name of the item to equip
            
        Returns:
            tuple: (success, message)
        """
        item_name = item_name.lower()
        item = None
        item_index = -1
        
        for i, inv_item in enumerate(self.inventory):
            if inv_item.name == item_name:
                item = inv_item
                item_index = i
                break
        
        if not item:
            return False, f"You don't have a {item_name}."
        
        if item.category == ItemCategory.CONSUMABLE:
            return False, "You can't equip consumables."
        
        if item.category == ItemCategory.MATERIAL:
            return False, "You can't equip materials."
        
        slot = None
        if item.category == ItemCategory.WEAPON:
            slot = "weapon"
        elif item.category == ItemCategory.ARMOR:
            slot = "armor"
        elif item.category == ItemCategory.ACCESSORY:
            slot = "accessory"
        
        if not slot:
            return False, "This item cannot be equipped."
        
        if self.equipment[slot]:
            self.inventory.append(self.equipment[slot])
            self.equipment[slot] = None
        
        self.equipment[slot] = item
        self.inventory.pop(item_index)
        
        return True, f"Equipped {item_name}."
    
    def unequip_item(self, slot: str) -> tuple[bool, str]:
        """
        Unequip an item from a slot.
        
        Args:
            slot: Equipment slot (weapon, armor, accessory)
            
        Returns:
            tuple: (success, message)
        """
        slot = slot.lower()
        if slot not in self.equipment:
            return False, "Invalid equipment slot."
        
        if not self.equipment[slot]:
            return False, f"No item equipped in {slot}."
        
        item = self.equipment[slot]
        self.inventory.append(item)
        self.equipment[slot] = None
        
        return True, f"Unequipped {item.name}."
    
    def get_equipped(self, slot: str) -> Optional[Item]:
        """Get currently equipped item in a slot."""
        return self.equipment.get(slot.lower())
    
    def add_gold(self, amount: int) -> None:
        """Add gold to player's total."""
        self.gold += amount
    
    def remove_gold(self, amount: int) -> bool:
        """Remove gold from player's total."""
        if self.gold >= amount:
            self.gold -= amount
            return True
        return False
    
    def add_status_effect(self, effect_name: str, duration: Optional[int] = None) -> None:
        """Add a status effect to the player."""
        effect = StatusEffect(effect_name, duration)
        
        for existing in self.status_effects:
            if existing.name == effect.name:
                existing.duration = max(existing.duration, effect.duration)
                return
        
        self.status_effects.append(effect)
    
    def remove_status_effect(self, effect_name: str) -> bool:
        """Remove a specific status effect."""
        for i, effect in enumerate(self.status_effects):
            if effect.name == effect_name.lower():
                self.status_effects.pop(i)
                return True
        return False
    
    def clear_status_effects(self) -> None:
        """Remove all status effects."""
        self.status_effects = []
    
    def process_status_effects(self) -> List[str]:
        """
        Process all status effects (healing, damage, duration).
        
        Returns:
            List of effect descriptions
        """
        descriptions = []
        effects_to_remove = []
        
        for effect in self.status_effects:
            if effect.heal > 0:
                healed = self.heal(effect.heal)
                descriptions.append(f"{effect.name.capitalize()} heals you for {healed} HP.")
            
            if effect.damage > 0:
                self.hp = max(0, self.hp - effect.damage)
                descriptions.append(f"{effect.name.capitalize()} deals {effect.damage} damage.")
            
            effect.duration -= 1
            if effect.duration <= 0:
                effects_to_remove.append(effect)
        
        for effect in effects_to_remove:
            self.status_effects.remove(effect)
            descriptions.append(f"{effect.name.capitalize()} wears off.")
        
        return descriptions
    
    def should_skip_turn(self) -> bool:
        """Check if player should skip turn due to status effects."""
        for effect in self.status_effects:
            if hasattr(effect, 'skip_turn_chance') and effect.skip_turn_chance > 0:
                if random.random() < effect.skip_turn_chance:
                    return True
        return False
    
    def cure_effect(self, effect_name: str) -> bool:
        """Cure a specific status effect."""
        return self.remove_status_effect(effect_name)
    
    def cure_all_effects(self) -> bool:
        """Cure all negative status effects."""
        if self.status_effects:
            self.status_effects = []
            return True
        return False
    
    def to_dict(self) -> dict:
        """Convert player data to dictionary for saving."""
        return {
            "hp": self.hp,
            "max_hp": self.max_hp,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "gold": self.gold,
            "level": self.level,
            "xp": self.xp,
            "xp_to_level": self.xp_to_level,
            "inventory": [item.to_dict() for item in self.inventory],
            "equipment": {
                slot: item.to_dict() if item else None
                for slot, item in self.equipment.items()
            },
            "status_effects": [effect.to_dict() for effect in self.status_effects]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Player":
        """Create a Player instance from saved data."""
        player = cls()
        player.hp = data.get("hp", 20)
        player.max_hp = data.get("max_hp", 20)
        player.base_attack = data.get("base_attack", 5)
        player.base_defense = data.get("base_defense", 3)
        player.gold = data.get("gold", 0)
        player.level = data.get("level", 1)
        player.xp = data.get("xp", 0)
        player.xp_to_level = data.get("xp_to_level", 100)
        
        for item_data in data.get("inventory", []):
            player.inventory.append(Item.from_dict(item_data))
        
        equipment_data = data.get("equipment", {})
        for slot in player.equipment:
            if slot in equipment_data and equipment_data[slot]:
                player.equipment[slot] = Item.from_dict(equipment_data[slot])
        
        for effect_data in data.get("status_effects", []):
            player.status_effects.append(StatusEffect.from_dict(effect_data))
        
        return player
    
    def get_stats_string(self) -> str:
        """Get a formatted string of current stats."""
        equip_bonus = self.get_equipment_stats()
        return (
            f"HP: {self.hp}/{self.max_hp} | "
            f"Attack: {self.attack} ({self.base_attack}+{equip_bonus['attack']}) | "
            f"Defense: {self.defense} ({self.base_defense}+{equip_bonus['defense']}) | "
            f"Gold: {self.gold} | "
            f"Level: {self.level} | "
            f"XP: {self.xp}/{self.xp_to_level}"
        )
    
    def get_inventory_string(self) -> str:
        """Get a formatted string of inventory contents."""
        if not self.inventory:
            return "Your inventory is empty."
        
        items_by_category = {}
        for item in self.inventory:
            cat = item.category.value
            if cat not in items_by_category:
                items_by_category[cat] = []
            items_by_category[cat].append(f"{item.name} x{item.quantity}")
        
        lines = []
        for cat, items in items_by_category.items():
            lines.append(f"  {cat.capitalize()}: {', '.join(items)}")
        
        return "\n".join(lines)
    
    def get_equipment_string(self) -> str:
        """Get a formatted string of currently equipped items."""
        lines = ["Equipment:"]
        for slot, item in self.equipment.items():
            if item:
                lines.append(f"  {slot.capitalize()}: {item.name} (+{item.attack} ATK, +{item.defense} DEF)")
            else:
                lines.append(f"  {slot.capitalize()}: (empty)")
        return "\n".join(lines)
    
    def get_context_for_ai(self) -> str:
        """Generate player context string for AI prompts."""
        equip_bonus = self.get_equipment_stats()
        stats = (
            f"Level {self.level}, HP: {self.hp}/{self.max_hp}, "
            f"Attack: {self.attack} (base:{self.base_attack}+equip:{equip_bonus['attack']}), "
            f"Defense: {self.defense} (base:{self.base_defense}+equip:{equip_bonus['defense']}), "
            f"Gold: {self.gold}, XP: {self.xp}/{self.xp_to_level}"
        )
        
        inventory = ", ".join(f"{item.name} x{item.quantity}" for item in self.inventory) if self.inventory else "None"
        
        equipment = []
        for slot, item in self.equipment.items():
            if item:
                equipment.append(f"{slot}:{item.name}")
        equip_str = ", ".join(equipment) if equipment else "None"
        
        effects = ", ".join(e.name for e in self.status_effects) if self.status_effects else "None"
        
        return f"Player: {stats}\nEquipment: {equip_str}\nInventory: {inventory}\nStatus Effects: {effects}"
