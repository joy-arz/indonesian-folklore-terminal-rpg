"""
Save System module - handles game save/load functionality with multiple slots.

This module manages:
- Multiple save slots (3 slots)
- Automatic saving after each turn
- Loading saved games on startup
- Save file format and validation
- Backup creation for safety
- Save metadata (playtime, location, level)
"""

import json
import os
import time
from datetime import datetime
from typing import Optional, Dict, Any, List

from .player import Player
from .ai_engine import AIEngine
from .combat import Combat, Enemy


class SaveSystem:
    """
    Manages game state persistence with multiple save slots.
    
    Saves are stored in JSON format and include:
    - Player stats, inventory, and equipment
    - Story history for AI context
    - Active combat state (if in battle)
    - Metadata (save time, turn count, playtime, location)
    """
    
    SAVE_DIR = os.path.expanduser("~/.trpg_saves")
    DEFAULT_SLOT = 1
    MAX_SLOTS = 3
    BACKUP_SUFFIX = ".backup"
    
    def __init__(self, slot: int = DEFAULT_SLOT):
        """
        Initialize save system.
        
        Args:
            slot: Save slot number (1-3)
        """
        self.slot = slot
        self.save_file = os.path.join(self.SAVE_DIR, f"save_slot_{slot}.json")
        self.backup_file = self.save_file + self.BACKUP_SUFFIX
        self.save_data: Dict[str, Any] = {}
        
        # Ensure save directory exists
        os.makedirs(self.SAVE_DIR, exist_ok=True)
    
    def get_slot_file(self, slot: int) -> str:
        """Get the file path for a specific save slot."""
        return os.path.join(self.SAVE_DIR, f"save_slot_{slot}.json")
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """
        List all available save slots with metadata.
        
        Returns:
            List of save info dictionaries
        """
        saves = []
        
        for slot in range(1, self.MAX_SLOTS + 1):
            save_file = self.get_slot_file(slot)
            
            if os.path.exists(save_file):
                try:
                    with open(save_file, 'r') as f:
                        data = json.load(f)
                    
                    saves.append({
                        "slot": slot,
                        "exists": True,
                        "saved_at": data.get("saved_at", "Unknown"),
                        "turn_count": data.get("turn_count", 0),
                        "playtime": data.get("playtime", 0),
                        "player": data.get("player", {}),
                        "location": data.get("location", "Unknown"),
                        "in_combat": data.get("in_combat", False)
                    })
                except Exception:
                    saves.append({
                        "slot": slot,
                        "exists": True,
                        "error": "Corrupted save"
                    })
            else:
                saves.append({
                    "slot": slot,
                    "exists": False
                })
        
        return saves
    
    def create_save_data(
        self,
        player: Player,
        ai_engine: AIEngine,
        combat: Optional[Combat] = None,
        turn_count: int = 0,
        playtime: int = 0
    ) -> dict:
        """
        Create a complete save data dictionary.
        
        Args:
            player: Current player instance
            ai_engine: AI engine instance
            combat: Active combat instance (if any)
            turn_count: Number of turns played
            playtime: Total playtime in seconds
            
        Returns:
            dict: Complete save data
        """
        save_data = {
            "version": "2.0",
            "saved_at": datetime.now().isoformat(),
            "turn_count": turn_count,
            "playtime": playtime + int(time.time() - getattr(self, '_session_start', time.time())),
            "player": player.to_dict(),
            "ai_engine": ai_engine.to_dict(),
            "in_combat": combat is not None,
            "combat": combat.to_dict() if combat else None,
            "location": ai_engine.location,
            "story_summary": ai_engine.get_story_summary()[:500] if ai_engine.story_history else "New game"
        }
        
        return save_data
    
    def save_game(
        self,
        player: Player,
        ai_engine: AIEngine,
        combat: Optional[Combat] = None,
        turn_count: int = 0,
        playtime: int = 0
    ) -> bool:
        """
        Save the current game state.
        
        Creates a backup of existing save before overwriting.
        
        Args:
            player: Current player instance
            ai_engine: AI engine instance
            combat: Active combat instance (if any)
            turn_count: Number of turns played
            playtime: Total playtime in seconds
            
        Returns:
            bool: True if save successful
        """
        try:
            # Create backup if save exists
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    content = f.read()
                with open(self.backup_file, 'w') as f:
                    f.write(content)
            
            # Create save data
            self.save_data = self.create_save_data(
                player, ai_engine, combat, turn_count, playtime
            )
            
            # Write save file
            with open(self.save_file, 'w') as f:
                json.dump(self.save_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def save_to_slot(self, slot: int, player: Player, ai_engine: AIEngine,
                     combat: Optional[Combat] = None, turn_count: int = 0,
                     playtime: int = 0) -> bool:
        """
        Save to a specific slot.
        
        Args:
            slot: Slot number (1-3)
            player: Current player instance
            ai_engine: AI engine instance
            combat: Active combat instance (if any)
            turn_count: Number of turns played
            playtime: Total playtime in seconds
            
        Returns:
            bool: True if save successful
        """
        if slot < 1 or slot > self.MAX_SLOTS:
            return False
        
        old_slot = self.slot
        self.slot = slot
        self.save_file = self.get_slot_file(slot)
        self.backup_file = self.save_file + self.BACKUP_SUFFIX
        
        result = self.save_game(player, ai_engine, combat, turn_count, playtime)
        
        self.slot = old_slot
        self.save_file = self.get_slot_file(old_slot)
        self.backup_file = self.save_file + self.BACKUP_SUFFIX
        
        return result
    
    def load_game(self, slot: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """
        Load saved game data.
        
        Args:
            slot: Slot to load from (uses current slot if None)
            
        Returns:
            dict: Loaded save data, or None if no save exists
        """
        if slot is not None:
            load_file = self.get_slot_file(slot)
        else:
            load_file = self.save_file
        
        if not os.path.exists(load_file):
            return None
        
        try:
            with open(load_file, 'r') as f:
                self.save_data = json.load(f)
            
            return self.save_data
            
        except json.JSONDecodeError as e:
            print(f"Error: Save file is corrupted: {e}")
            
            # Try to load backup
            backup_file = load_file + self.BACKUP_SUFFIX
            if os.path.exists(backup_file):
                print("Attempting to load backup save...")
                try:
                    with open(backup_file, 'r') as f:
                        self.save_data = json.load(f)
                    return self.save_data
                except Exception:
                    pass
            
            return None
        except Exception as e:
            print(f"Error loading save: {e}")
            return None
    
    def load_from_slot(self, slot: int) -> Optional[Dict[str, Any]]:
        """Load from a specific slot."""
        return self.load_game(slot)
    
    def has_save(self, slot: Optional[int] = None) -> bool:
        """Check if a save file exists."""
        if slot is not None:
            return os.path.exists(self.get_slot_file(slot))
        return os.path.exists(self.save_file)
    
    def delete_save(self, slot: Optional[int] = None) -> bool:
        """Delete a save file."""
        if slot is not None:
            save_file = self.get_slot_file(slot)
            backup_file = save_file + self.BACKUP_SUFFIX
        else:
            save_file = self.save_file
            backup_file = self.backup_file
        
        try:
            if os.path.exists(save_file):
                os.remove(save_file)
            if os.path.exists(backup_file):
                os.remove(backup_file)
            return True
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
    
    def delete_all_saves(self) -> bool:
        """Delete all save slots."""
        success = True
        for slot in range(1, self.MAX_SLOTS + 1):
            if not self.delete_save(slot):
                success = False
        return success
    
    def restore_player(self, save_data: dict) -> Player:
        """Restore player from save data."""
        player_data = save_data.get("player", {})
        return Player.from_dict(player_data)
    
    def restore_ai_engine(self, save_data: dict) -> AIEngine:
        """Restore AI engine from save data."""
        ai_engine = AIEngine()
        ai_data = save_data.get("ai_engine", {})
        ai_engine.from_dict(ai_data)
        
        # Restore additional state
        ai_engine.location = save_data.get("location", "unknown")
        
        return ai_engine
    
    def restore_combat(self, save_data: dict, player: Player) -> Optional[Combat]:
        """Restore combat from save data."""
        if not save_data.get("in_combat", False):
            return None
        
        combat_data = save_data.get("combat")
        if combat_data:
            return Combat.from_dict(combat_data, player)
        
        return None
    
    def get_save_info(self, slot: Optional[int] = None) -> Optional[str]:
        """Get human-readable save file info."""
        if slot is not None:
            if not self.has_save(slot):
                return None
            save_data = self.load_game(slot)
        else:
            if not self.has_save():
                return None
            save_data = self.load_game()
        
        if not save_data:
            return None
        
        player = save_data.get("player", {})
        saved_at = save_data.get("saved_at", "Unknown")
        turn_count = save_data.get("turn_count", 0)
        playtime = save_data.get("playtime", 0)
        location = save_data.get("location", "Unknown")
        
        # Format playtime
        hours = playtime // 3600
        minutes = (playtime % 3600) // 60
        
        info = (
            f"Save from: {saved_at}\n"
            f"Location: {location}\n"
            f"Playtime: {hours}h {minutes}m | Turns: {turn_count}\n"
            f"Player: Level {player.get('level', 1)}, "
            f"HP {player.get('hp', 0)}/{player.get('max_hp', 0)}, "
            f"ATK {player.get('base_attack', 0)}, "
            f"DEF {player.get('base_defense', 0)}, "
            f"Gold: {player.get('gold', 0)}"
        )
        
        if save_data.get("in_combat"):
            enemy = save_data.get("combat", {}).get("enemy", {})
            info += f"\n⚔️  In combat with: {enemy.get('name', 'Unknown enemy')}"
        
        return info
    
    def get_save_summary(self, slot: int) -> Optional[str]:
        """Get a short summary for save slot display."""
        if not self.has_save(slot):
            return None
        
        save_data = self.load_game(slot)
        if not save_data:
            return None
        
        player = save_data.get("player", {})
        location = save_data.get("location", "Unknown")
        level = player.get("level", 1)
        hp = player.get("hp", 0)
        max_hp = player.get("max_hp", 1)
        
        hp_status = "✓" if hp > max_hp * 0.5 else "⚠" if hp > max_hp * 0.25 else "✗"
        
        return f"Slot {slot}: Lvl {level} {location} {hp_status}"
