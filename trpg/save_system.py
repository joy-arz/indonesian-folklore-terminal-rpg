
import json
import os
import time
import tempfile
import gzip
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from .player import Player
from .ai_engine import AIEngine
from .combat import Combat, Enemy

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trpg.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('SaveSystem')


class SaveSystem:

    SAVE_DIR = os.path.expanduser("~/.trpg_saves")
    DEFAULT_SLOT = 1
    MAX_SLOTS = 3
    BACKUP_SUFFIX = ".backup"
    COMPRESS_SUFFIX = ".gz"

    def __init__(self, slot: int = DEFAULT_SLOT):
        self.slot = slot
        self.save_file = os.path.join(self.SAVE_DIR, f"save_slot_{slot}.json.gz")
        self.backup_file = self.save_file + self.BACKUP_SUFFIX
        self.save_data: Dict[str, Any] = {}

        os.makedirs(self.SAVE_DIR, exist_ok=True)

    def get_slot_file(self, slot: int) -> str:
        return os.path.join(self.SAVE_DIR, f"save_slot_{slot}.json.gz")

    def list_saves(self) -> List[Dict[str, Any]]:
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
        try:
            if os.path.exists(self.save_file):
                with gzip.open(self.save_file, 'rt', encoding='utf-8') as f:
                    content = f.read()
                with gzip.open(self.backup_file, 'wt', encoding='utf-8') as f:
                    f.write(content)

            self.save_data = self.create_save_data(
                player, ai_engine, combat, turn_count, playtime
            )

            temp_fd, temp_path = tempfile.mkstemp(
                suffix='.json.tmp',
                dir=os.path.dirname(self.save_file)
            )
            
            try:
                with os.fdopen(temp_fd, 'w') as f:
                    json.dump(self.save_data, f, indent=2)
                
                with open(temp_path, 'rb') as f_in:
                    with gzip.open(self.save_file, 'wb') as f_out:
                        f_out.writelines(f_in)
                
                os.unlink(temp_path)
                logger.info(f"Game saved (compressed) to {self.save_file}")
                return True
                
            except Exception:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
                logger.error(f"Failed to save game to {self.save_file}")
                raise

        except Exception as e:
            logger.error(f"Save game error: {str(e)}", exc_info=True)
            return False

    def save_to_slot(self, slot: int, player: Player, ai_engine: AIEngine,
                     combat: Optional[Combat] = None, turn_count: int = 0,
                     playtime: int = 0) -> bool:
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
        if slot is not None:
            load_file = self.get_slot_file(slot)
        else:
            load_file = self.save_file

        if not os.path.exists(load_file):
            return None

        try:
            with gzip.open(load_file, 'rt', encoding='utf-8') as f:
                self.save_data = json.load(f)

            logger.info(f"Game loaded from {load_file}")
            return self.save_data

        except (json.JSONDecodeError, gzip.BadGzipFile) as e:
            logger.error(f"Save file is corrupted: {e}")
            print(f"Error: Save file is corrupted: {e}")

            backup_file = load_file + self.BACKUP_SUFFIX
            if os.path.exists(backup_file):
                print("Attempting to load backup save...")
                logger.info(f"Attempting to load backup from {backup_file}")
                try:
                    with gzip.open(backup_file, 'rt', encoding='utf-8') as f:
                        self.save_data = json.load(f)
                    return self.save_data
                except Exception:
                    pass

            return None
        except Exception as e:
            logger.error(f"Error loading save: {e}", exc_info=True)
            print(f"Error loading save: {e}")
            return None

    def load_from_slot(self, slot: int) -> Optional[Dict[str, Any]]:
        return self.load_game(slot)

    def has_save(self, slot: Optional[int] = None) -> bool:
        if slot is not None:
            return os.path.exists(self.get_slot_file(slot))
        return os.path.exists(self.save_file)

    def delete_save(self, slot: Optional[int] = None) -> bool:
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
        success = True
        for slot in range(1, self.MAX_SLOTS + 1):
            if not self.delete_save(slot):
                success = False
        return success

    def restore_player(self, save_data: dict) -> Player:
        player_data = save_data.get("player", {})
        return Player.from_dict(player_data)

    def restore_ai_engine(self, save_data: dict) -> AIEngine:
        ai_engine = AIEngine()
        ai_data = save_data.get("ai_engine", {})
        ai_engine.from_dict(ai_data)

        ai_engine.location = save_data.get("location", "unknown")

        return ai_engine

    def restore_combat(self, save_data: dict, player: Player) -> Optional[Combat]:
        if not save_data.get("in_combat", False):
            return None

        combat_data = save_data.get("combat")
        if combat_data:
            return Combat.from_dict(combat_data, player)

        return None

    def get_save_info(self, slot: Optional[int] = None) -> Optional[str]:
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
