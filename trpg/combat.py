"""
Combat module - handles turn-based combat system with consistent encounters.

This module manages combat encounters including:
- Enemy creation and stats with difficulty scaling
- Turn-based combat flow with status effects
- Damage calculation with defense mitigation
- Combat actions (attack, defend, use item, run, special)
- Victory rewards (XP, gold, items)
- Escape mechanics based on stats
"""

import random
from typing import Optional, Tuple, Dict, Any, List
from .player import Player, Item, StatusEffect


class Enemy:
    """
    Represents an enemy in combat.
    
    Attributes:
        name (str): Enemy name/type
        hp (int): Current health points
        max_hp (int): Maximum health points
        attack (int): Attack power
        defense (int): Defense rating
        gold_reward (int): Gold awarded on defeat
        xp_reward (int): Experience awarded on defeat
        level (int): Enemy level for scaling
    """
    
    # Enemy templates - Indonesian mythology creatures
    ENEMY_TEMPLATES = [
        {"name": "Genderuwo", "hp": 15, "attack": 5, "defense": 2, "gold": (5, 10), "xp": 25, "level": 2},
        {"name": "Kuntilanak", "hp": 10, "attack": 6, "defense": 1, "gold": (3, 8), "xp": 20, "level": 2},
        {"name": "Tuyul", "hp": 6, "attack": 3, "defense": 0, "gold": (8, 15), "xp": 15, "level": 1},
        {"name": "Pocong", "hp": 12, "attack": 4, "defense": 1, "gold": (2, 5), "xp": 18, "level": 2},
        {"name": "Prajurit Majapahit", "hp": 18, "attack": 6, "defense": 3, "gold": (10, 20), "xp": 35, "level": 3},
        {"name": "Bajak Laut", "hp": 14, "attack": 5, "defense": 2, "gold": (15, 30), "xp": 30, "level": 3},
        {"name": "Harimau Jadi-jadian", "hp": 20, "attack": 7, "defense": 2, "gold": (8, 15), "xp": 40, "level": 4},
        {"name": "Leak Bali", "hp": 16, "attack": 8, "defense": 2, "gold": (10, 18), "xp": 45, "level": 4},
        {"name": "Raksasa Gunung", "hp": 30, "attack": 8, "defense": 4, "gold": (20, 35), "xp": 60, "level": 6},
        {"name": "Dukun Hitam", "hp": 14, "attack": 10, "defense": 2, "gold": (25, 40), "xp": 55, "level": 5},
        {"name": "Ular Raksasa", "hp": 22, "attack": 7, "defense": 3, "gold": (12, 22), "xp": 50, "level": 5},
        {"name": "Prajurit Pajajaran", "hp": 20, "attack": 6, "defense": 3, "gold": (15, 25), "xp": 45, "level": 4},
        {"name": "Arwah Kesatria", "hp": 25, "attack": 9, "defense": 4, "gold": (20, 30), "xp": 65, "level": 7},
        {"name": "Iblis Laut Selatan", "hp": 35, "attack": 10, "defense": 4, "gold": (30, 50), "xp": 80, "level": 8},
        {"name": "Garuda Sakti", "hp": 40, "attack": 12, "defense": 5, "gold": (40, 70), "xp": 100, "level": 10},
    ]
    
    # Item drop tables by rarity
    DROP_TABLE = {
        "common": ["health potion", "bread", "rusty sword", "cloth armor"],
        "uncommon": ["greater health potion", "iron sword", "leather armor", "ring of strength"],
        "rare": ["super health potion", "steel sword", "chain mail", "magic staff"],
        "legendary": ["elixir", "magic sword", "plate armor", "dragon pendant"],
    }
    
    def __init__(self, name: str, hp: int, attack: int, defense: int, 
                 gold_range: Tuple[int, int], xp: int, level: int):
        """
        Initialize an enemy with given stats.
        
        Args:
            name: Enemy name
            hp: Maximum health points
            attack: Attack power
            defense: Defense rating
            gold_range: Tuple of (min, max) gold reward
            xp: Experience points awarded
            level: Enemy level
        """
        self.name = name
        self.max_hp = hp
        self.hp = hp
        self.attack = attack
        self.defense = defense
        self.gold_range = gold_range
        self.xp_reward = xp
        self.level = level
        self.status_effects: List[StatusEffect] = []
    
    @classmethod
    def create_random(cls, player_level: int = 1) -> "Enemy":
        """
        Create a random enemy scaled to player level.
        
        Args:
            player_level: Player's current level for scaling
            
        Returns:
            Enemy: New enemy instance
        """
        # Filter enemies appropriate for player level
        suitable_enemies = [t for t in cls.ENEMY_TEMPLATES if t["level"] <= player_level + 2]
        
        if not suitable_enemies:
            suitable_enemies = [cls.ENEMY_TEMPLATES[0]]
        
        # Weight by level proximity (prefer closer levels)
        weights = []
        for template in suitable_enemies:
            level_diff = abs(template["level"] - player_level)
            weight = max(1, 5 - level_diff)  # Higher weight for closer levels
            weights.append(weight)
        
        template = random.choices(suitable_enemies, weights=weights)[0]
        
        # Scale stats slightly based on level difference
        scale = 1 + max(0, (player_level - template["level"])) * 0.1
        
        return cls(
            name=template["name"],
            hp=int(template["hp"] * scale),
            attack=int(template["attack"] * scale),
            defense=int(template["defense"] * scale),
            gold_range=template["gold"],
            xp=int(template["xp"] * scale),
            level=max(1, int(template["level"] * scale))
        )
    
    @classmethod
    def create_boss(cls, player_level: int) -> "Enemy":
        """Create a boss enemy for the player."""
        boss_templates = [t for t in cls.ENEMY_TEMPLATES if t["level"] >= 15]
        if not boss_templates:
            return cls.create_random(player_level)
        
        template = random.choice(boss_templates)
        scale = 1 + (player_level * 0.2)
        
        return cls(
            name=f"Boss {template['name']}",
            hp=int(template["hp"] * scale * 1.5),
            attack=int(template["attack"] * scale * 1.3),
            defense=int(template["defense"] * scale * 1.2),
            gold_range=(template["gold"][0] * 2, template["gold"][1] * 2),
            xp=int(template["xp"] * scale * 2),
            level=int(template["level"] * scale)
        )
    
    def take_damage(self, amount: int) -> int:
        """
        Reduce enemy HP by the given amount (after defense).
        
        Args:
            amount: Raw damage amount
            
        Returns:
            int: Actual damage dealt after defense
        """
        actual_damage = max(1, amount - self.defense)
        self.hp = max(0, self.hp - actual_damage)
        return actual_damage
    
    def apply_status_effect(self, effect_name: str, duration: int = 3) -> bool:
        """Apply a status effect to the enemy."""
        # Some enemies are immune to certain effects
        immune_effects = {
            "undead": ["poison", "bleed"],
            "construct": ["poison", "bleed", "stun"],
            "boss": ["stun", "freeze"],
        }
        
        enemy_type = "normal"
        if "skeleton" in self.name.lower() or "wraith" in self.name.lower() or "lich" in self.name.lower():
            enemy_type = "undead"
        elif "golem" in self.name.lower():
            enemy_type = "construct"
        elif "boss" in self.name.lower():
            enemy_type = "boss"
        
        # Check immunity
        if enemy_type in immune_effects and effect_name in immune_effects[enemy_type]:
            return False
        
        effect = StatusEffect(effect_name, duration)
        self.status_effects.append(effect)
        return True
    
    def process_status_effects(self) -> List[str]:
        """Process status effects on the enemy."""
        descriptions = []
        effects_to_remove = []
        
        for effect in self.status_effects:
            if effect.damage > 0:
                self.hp = max(0, self.hp - effect.damage)
                descriptions.append(f"{effect.name.capitalize()} deals {effect.damage} damage to {self.name}.")
            
            effect.duration -= 1
            if effect.duration <= 0:
                effects_to_remove.append(effect)
                descriptions.append(f"{self.name}'s {effect.name} wears off.")
        
        for effect in effects_to_remove:
            self.status_effects.remove(effect)
        
        return descriptions
    
    def is_alive(self) -> bool:
        """Check if enemy is still alive."""
        return self.hp > 0
    
    def get_gold_reward(self) -> int:
        """Get random gold reward within range."""
        return random.randint(self.gold_range[0], self.gold_range[1])
    
    def get_item_drop(self) -> Optional[str]:
        """
        Get a random item drop based on enemy level.
        
        Returns:
            Item name or None if no drop
        """
        # Base 30% drop chance + 5% per player level
        drop_chance = 0.3 + (0.05 * self.level)
        if random.random() > drop_chance:
            return None
        
        # Determine rarity based on level
        if self.level >= 15:
            rarity = random.choices(
                ["common", "uncommon", "rare", "legendary"],
                weights=[20, 40, 30, 10]
            )[0]
        elif self.level >= 8:
            rarity = random.choices(
                ["common", "uncommon", "rare"],
                weights=[30, 50, 20]
            )[0]
        else:
            rarity = random.choices(
                ["common", "uncommon"],
                weights=[70, 30]
            )[0]
        
        items = self.DROP_TABLE.get(rarity, self.DROP_TABLE["common"])
        return random.choice(items)
    
    def to_dict(self) -> dict:
        """Convert enemy to dictionary for saving."""
        return {
            "name": self.name,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "attack": self.attack,
            "defense": self.defense,
            "gold_range": list(self.gold_range),
            "xp_reward": self.xp_reward,
            "level": self.level,
            "status_effects": [e.to_dict() for e in self.status_effects]
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Enemy":
        """Create enemy from saved data."""
        enemy = cls(
            name=data.get("name", "Goblin"),
            hp=data.get("max_hp", 8),
            attack=data.get("attack", 3),
            defense=data.get("defense", 1),
            gold_range=tuple(data.get("gold_range", [2, 5])),
            xp=data.get("xp_reward", 15),
            level=data.get("level", 1)
        )
        enemy.hp = data.get("hp", enemy.max_hp)
        
        # Load status effects
        for effect_data in data.get("status_effects", []):
            enemy.status_effects.append(StatusEffect.from_dict(effect_data))
        
        return enemy


class Combat:
    """
    Manages a combat encounter between player and enemy.
    
    Handles turn-based combat flow, action resolution, and
    determining combat outcomes (victory, defeat, escape).
    """
    
    ACTIONS = ["attack", "defend", "use item", "run", "special"]
    
    def __init__(self, player: Player, enemy: Enemy):
        """
        Initialize a combat encounter.
        
        Args:
            player: The player character
            enemy: The enemy to fight
        """
        self.player = player
        self.enemy = enemy
        self.is_defending = False
        self.turn_count = 0
        self.combat_log: List[str] = []
        self.player_turn = True
    
    def get_combat_context(self) -> dict:
        """Get current combat state for AI context."""
        return {
            "enemy_name": self.enemy.name,
            "enemy_hp": self.enemy.hp,
            "enemy_max_hp": self.enemy.max_hp,
            "player_hp": self.player.hp,
            "player_max_hp": self.player.max_hp,
            "turn": self.turn_count,
            "player_level": self.player.level
        }
    
    def calculate_damage(self, attacker_attack: int, defender_defense: int, 
                        is_critical: bool = False) -> Tuple[int, bool]:
        """
        Calculate damage with critical hit chance.
        
        Args:
            attacker_attack: Attacker's attack stat
            defender_defense: Defender's defense stat
            is_critical: Force critical hit
            
        Returns:
            Tuple of (damage, was_critical)
        """
        # Base damage calculation
        base_damage = max(1, attacker_attack - defender_defense)
        
        # Critical hit check (10% base + 5% per level difference)
        if is_critical or random.random() < 0.1:
            base_damage = int(base_damage * 1.5)
            return base_damage, True
        
        # Damage variance (±20%)
        variance = random.uniform(0.8, 1.2)
        damage = int(base_damage * variance)
        
        return max(1, damage), False
    
    def player_attack(self) -> Tuple[int, str, bool]:
        """
        Execute player attack action.
        
        Returns:
            Tuple of (damage dealt, description, was_critical)
        """
        self.is_defending = False
        
        # Check if player is stunned
        if self.player.should_skip_turn():
            return 0, "You're stunned and can't attack!", False
        
        damage, is_crit = self.calculate_damage(
            self.player.attack,
            self.enemy.defense
        )
        
        # Apply damage to enemy
        actual_damage = self.enemy.take_damage(damage)
        
        if is_crit:
            description = f"CRITICAL HIT! You strike the {self.enemy.name} for {actual_damage} damage!"
        else:
            description = f"You attack the {self.enemy.name} for {actual_damage} damage."
        
        self.combat_log.append(description)
        return actual_damage, description, is_crit
    
    def player_defend(self) -> Tuple[int, str]:
        """
        Execute player defend action.
        
        Returns:
            Tuple of (defense bonus, description)
        """
        self.is_defending = True
        description = "You raise your guard, reducing incoming damage by 50% this turn."
        self.combat_log.append(description)
        return 0, description
    
    def player_use_item(self, item_name: str) -> Tuple[bool, str]:
        """
        Execute player use item action.
        
        Args:
            item_name: Name of item to use
            
        Returns:
            Tuple of (success, description string)
        """
        self.is_defending = False
        
        # Check if player is stunned
        if self.player.should_skip_turn():
            return False, "You're stunned and can't use items!"
        
        item_name = item_name.lower()
        
        if not self.player.has_item(item_name):
            return False, f"You don't have a {item_name}!"
        
        item = None
        for inv_item in self.player.inventory:
            if inv_item.name == item_name:
                item = inv_item
                break
        
        if not item:
            return False, f"You don't have a {item_name}!"
        
        # Handle different item types
        if item.category.name == "CONSUMABLE":
            # Healing potion
            if hasattr(item, 'heal') and item.heal > 0:
                healed = self.player.heal(item.heal)
                self.player.remove_item(item_name)
                description = f"You use {item_name} and recover {healed} HP!"
                self.combat_log.append(description)
                return True, description
            
            # Cure effect
            if hasattr(item, 'cure') and item.cure:
                if item.cure == "all":
                    self.player.clear_status_effects()
                    description = f"You use {item_name} and cure all ailments!"
                else:
                    self.player.cure_effect(item.cure)
                    description = f"You use {item_name} and cure {item.cure}!"
                self.player.remove_item(item_name)
                self.combat_log.append(description)
                return True, description
        
        # Equipment can't be used in combat (must be equipped before)
        return False, f"You can't use {item_name} in combat!"
    
    def player_run(self) -> Tuple[bool, str]:
        """
        Attempt to flee from combat.
        
        Returns:
            Tuple of (success, description string)
        """
        self.is_defending = False
        
        # Check if player is stunned
        if self.player.should_skip_turn():
            return False, "You're stunned and can't escape!"
        
        # Escape chance based on speed/stats and turn count
        base_chance = 0.5
        
        # Higher level = easier to escape from lower level enemies
        level_diff = self.player.level - self.enemy.level
        base_chance += level_diff * 0.1
        
        # Defending increases escape chance
        if self.is_defending:
            base_chance += 0.2
        
        # Boss battles are harder to escape
        if "boss" in self.enemy.name.lower():
            base_chance = 0.2
        
        if random.random() < base_chance:
            description = "You successfully escape from combat!"
            self.combat_log.append(description)
            return True, description
        else:
            description = "You failed to escape! The enemy blocks your path."
            self.combat_log.append(description)
            return False, description
    
    def enemy_turn(self) -> Tuple[int, str]:
        """
        Execute enemy attack turn.
        
        Returns:
            Tuple of (damage dealt, description string)
        """
        if not self.enemy.is_alive():
            return 0, ""
        
        # Process enemy status effects first
        effect_descriptions = self.enemy.process_status_effects()
        
        # Check if enemy is stunned
        for effect in self.enemy.status_effects:
            if hasattr(effect, 'skip_turn_chance') and effect.skip_turn_chance > 0:
                if random.random() < effect.skip_turn_chance:
                    desc = f"The {self.enemy.name} is stunned and can't act!"
                    effect_descriptions.append(desc)
                    return 0, "\n".join(effect_descriptions) if effect_descriptions else desc
        
        # Calculate enemy damage
        base_damage = self.enemy.attack
        
        # Player defending reduces damage by 50%
        if self.is_defending:
            effective_damage = max(1, base_damage // 2)
            actual_damage = max(1, effective_damage - self.player.defense)
            description = f"The {self.enemy.name} attacks! You block and take only {actual_damage} damage."
        else:
            actual_damage = self.player.take_damage(base_damage)
            description = f"The {self.enemy.name} attacks you for {actual_damage} damage!"
        
        self.combat_log.append(description)
        
        if effect_descriptions:
            description = "\n".join(effect_descriptions) + "\n" + description
        
        return actual_damage, description
    
    def execute_turn(self, action: str, item_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a full combat turn (player action + enemy response).
        
        Args:
            action: Player's chosen action
            item_name: Item name if using an item
            
        Returns:
            dict: Turn results including success, descriptions, and combat status
        """
        self.turn_count += 1
        results = {
            "player_action": "",
            "player_description": "",
            "enemy_description": "",
            "combat_ended": False,
            "victory": False,
            "defeat": False,
            "escaped": False,
            "gold_earned": 0,
            "xp_earned": 0,
            "item_dropped": None,
            "player_stunned": False
        }
        
        action_lower = action.lower().strip()
        
        # Check if player is stunned before acting
        if self.player.should_skip_turn():
            results["player_description"] = "You're stunned and can't act this turn!"
            results["player_stunned"] = True
        else:
            # Execute player action
            if action_lower == "attack":
                _, results["player_description"], _ = self.player_attack()
                results["player_action"] = "attack"
                
                if not self.enemy.is_alive():
                    results["combat_ended"] = True
                    results["victory"] = True
                    results["gold_earned"] = self.enemy.get_gold_reward()
                    results["xp_earned"] = self.enemy.xp_reward
                    self.player.add_gold(results["gold_earned"])
                    self.player.add_xp(results["xp_earned"])
                    
                    # Check for item drop
                    dropped_item = self.enemy.get_item_drop()
                    if dropped_item:
                        results["item_dropped"] = dropped_item
                        self.player.add_item(dropped_item)
                    
                    return results
            
            elif action_lower == "defend":
                _, results["player_description"] = self.player_defend()
                results["player_action"] = "defend"
            
            elif action_lower.startswith("use"):
                if not item_name:
                    parts = action_lower.split(None, 1)
                    item_name = parts[1] if len(parts) > 1 else ""
                
                success, results["player_description"] = self.player_use_item(item_name)
                results["player_action"] = f"use {item_name}"
            
            elif action_lower in ["run", "flee", "escape"]:
                success, results["player_description"] = self.player_run()
                results["player_action"] = "run"
                
                if success:
                    results["combat_ended"] = True
                    results["escaped"] = True
                    return results
            else:
                results["player_description"] = "You hesitate, unsure what to do."
                results["player_action"] = "hesitate"
        
        # Enemy turn (if combat hasn't ended and player is alive)
        if not results["combat_ended"] and self.player.is_alive():
            results["enemy_description"] = self.enemy_turn()
            
            if not self.player.is_alive():
                results["combat_ended"] = True
                results["defeat"] = True
        
        return results
    
    def is_over(self) -> bool:
        """Check if combat has ended."""
        return not self.enemy.is_alive() or not self.player.is_alive()
    
    def get_status(self) -> str:
        """Get formatted combat status string."""
        return (
            f"{self.enemy.name}: HP {self.enemy.hp}/{self.enemy.max_hp} | "
            f"You: HP {self.player.hp}/{self.player.max_hp}"
        )
    
    def to_dict(self) -> dict:
        """Convert combat state to dictionary for saving."""
        return {
            "enemy": self.enemy.to_dict(),
            "turn_count": self.turn_count,
            "is_defending": self.is_defending,
            "combat_log": self.combat_log,
            "player_turn": self.player_turn
        }
    
    @classmethod
    def from_dict(cls, data: dict, player: Player) -> "Combat":
        """Create combat from saved data."""
        enemy = Enemy.from_dict(data.get("enemy", {}))
        combat = cls(player, enemy)
        combat.turn_count = data.get("turn_count", 0)
        combat.is_defending = data.get("is_defending", False)
        combat.combat_log = data.get("combat_log", [])
        combat.player_turn = data.get("player_turn", True)
        return combat
