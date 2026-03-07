
import sys
import os
import time
import random
import logging
from typing import Optional

from .player import Player, Item, ItemCategory, StatusEffect
from .ai_engine import AIEngine
from .combat import Combat, Enemy
from .save_system import SaveSystem
from .shop import Shop, find_shop
from .ui import UI, Colors
from .story import StoryManager
from . import updater

log_file = os.path.join(os.path.expanduser("~"), ".trpg.log")
try:
    handler = logging.FileHandler(log_file)
except PermissionError:
    handler = logging.StreamHandler()

logger = logging.getLogger('Game')
logger.setLevel(logging.INFO)
if not logger.handlers:
    logger.addHandler(handler)


class Game:

    def __init__(self):
        self.ui = UI()
        self.player = Player()
        self.ai_engine = None
        self.save_system = SaveSystem()
        self.combat = None
        self.shop = None
        self.story_manager = StoryManager()
        self.turn_count = 0
        self.playtime = 0
        self.game_over = False
        self.game_ended = False
        self.in_combat = False
        self.in_shop = False
        self._session_start = time.time()
        self.current_chapter = 1
        self.chapter_turn_start = 0
        self.last_autosave_turn = 0
        self.autosave_interval = 5
        logger.info("Game initialized")

    def initialize(self) -> bool:
        try:
            self.ui.clear_screen()
            self.ui.print_header("AI TERMINAL RPG")

            self.ai_engine = AIEngine()

            saves = self.save_system.list_saves()
            has_saves = any(s["exists"] for s in saves)

            if has_saves:
                print(f"\n{Colors.INFO}  Found existing save files:{Colors.RESET}\n")

                for save_info in saves:
                    if save_info["exists"]:
                        slot = save_info["slot"]
                        if "error" in save_info:
                            print(f"{Colors.ERROR}    Slot {slot}: {save_info['error']}{Colors.RESET}")
                        else:
                            location = save_info.get("location", "Unknown")
                            level = save_info.get("player", {}).get("level", 1)
                            hp = save_info.get("player", {}).get("hp", 0)
                            max_hp = save_info.get("player", {}).get("max_hp", 1)
                            saved_at = save_info.get("saved_at", "Unknown")[:16]

                            hp_bar = "█" * int(hp / max(1, max_hp) * 10)
                            print(f"{Colors.SUCCESS}    Slot {slot}: Lvl {level} {location} | HP: [{hp_bar}] {saved_at}{Colors.RESET}")
                    else:
                        print(f"{Colors.INFO}    Slot {slot}: (empty){Colors.RESET}")

                print()

                while True:
                    choice = self.ui.get_input(f"Load save (1-3, or 'n' for new game): ").strip()

                    if choice.lower() in ["n", "no", "new"]:
                        self.save_system = SaveSystem(slot=1)
                        return True

                    if choice.lower() in ["quit", "exit", "q"]:
                        return False

                    try:
                        slot = int(choice)
                        if 1 <= slot <= 3:
                            if self.save_system.has_save(slot):
                                self.save_system = SaveSystem(slot=slot)
                                return self.load_game()
                            else:
                                self.ui.print_error(f"Slot {slot} is empty")
                        else:
                            self.ui.print_error("Please enter 1, 2, or 3")
                    except ValueError:
                        self.ui.print_error("Please enter a number or 'n'")
            else:
                self.save_system = SaveSystem(slot=1)
                print(f"\n{Colors.INFO}  No existing saves found. Starting new game...{Colors.RESET}\n")
                self.ui.wait_for_enter()
                return True

            return True

        except ValueError as e:
            self.ui.print_error(str(e))
            return False
        except Exception as e:
            self.ui.print_error(f"Failed to initialize: {e}")
            return False

    def load_game(self) -> bool:
        save_data = self.save_system.load_game()

        if not save_data:
            self.ui.print_error("Failed to load save file")
            return False

        self.player = self.save_system.restore_player(save_data)
        self.ai_engine = self.save_system.restore_ai_engine(save_data)
        self.combat = self.save_system.restore_combat(save_data, self.player)
        self.turn_count = save_data.get("turn_count", 0)
        self.playtime = save_data.get("playtime", 0)
        self.in_combat = self.combat is not None
        self.in_shop = False

        story_data = save_data.get("story_manager", {})
        if story_data:
            self.story_manager.from_dict(story_data)
        self.turn_count = self.story_manager.turn_count

        self.ui.print_success("Game loaded successfully!")
        self.ui.wait_for_enter()
        return True

    def save_game(self, auto: bool = True) -> bool:
        current_playtime = self.playtime + int(time.time() - self._session_start)

        success = self.save_system.save_game(
            self.player,
            self.ai_engine,
            self.combat if self.in_combat else None,
            self.turn_count,
            current_playtime
        )

        if success:
            if auto:
                self.last_autosave_turn = self.turn_count
                if self.turn_count % self.autosave_interval == 0:
                    self.ui.print_message(f"  [Auto-saved at turn {self.turn_count}]", Colors.INFO)
            else:
                slot = self.save_system.slot
                self.ui.print_success(f"Game saved to Slot {slot}!")
        else:
            self.ui.print_error("Failed to save game")

        return success

    def start_new_game(self) -> None:
        self.player = Player()
        self.ai_engine = AIEngine()
        self.combat = None
        self.shop = None
        self.story_manager = StoryManager()
        self.turn_count = 0
        self.playtime = 0
        self.game_over = False
        self.in_combat = False
        self.in_shop = False
        self._session_start = time.time()
        self.save_system.delete_save()

        self.story_manager.initialize_game()

    def display_game_state(self) -> None:
        self.ui.clear_screen()
        self.ui.print_header()

        self.ui.print_stats_bar(
            self.player.hp,
            self.player.max_hp,
            self.player.xp,
            self.player.xp_to_level,
            self.player.level
        )

        if self.player.status_effects:
            self.ui.print_status_effects(self.player.status_effects)

    def handle_exploration(self) -> None:
        player_context = self.player.get_context_for_ai()

        scene, choices = self.ai_engine.generate_scene(player_context)

        if not choices or len(choices) < 2:
            logger.error(f"AI returned invalid choices: {len(choices) if choices else 0}")
            choices = ["Continue forward", "Look around", "Check inventory"]

        self.display_game_state()
        self.ui.print_scene(scene)
        self.ui.print_choices(choices)

        print(f"{Colors.INFO}  [I]nventory [E]quipment [S]tats [H]elp [Q]uit{Colors.RESET}\n")

        max_attempts = 3
        attempts = 0

        while True:
            user_input = self.ui.get_input("Your choice: ")

            if user_input.lower() in ["escape", "exit_game", "force_quit"]:
                if self.ui.confirm("Force quit without saving?"):
                    self.game_over = True
                    return

            cmd_result = self.handle_commands(user_input)
            if cmd_result is False:
                self.game_over = True
                return
            if cmd_result is True:
                self.display_game_state()
                self.ui.print_scene(scene)
                self.ui.print_choices(choices)
                print(f"{Colors.INFO}  [I]nventory [E]quipment [S]tats [H]elp [Q]uit{Colors.RESET}\n")
                continue

            try:
                choice_num = int(user_input)
                if 1 <= choice_num <= len(choices):
                    selected_choice = choices[choice_num - 1]
                    attempts = 0

                    self.story_manager.record_choice(
                        choice=selected_choice,
                        context=scene[:100] + "..."
                    )

                    self.analyze_choice_for_villainy(selected_choice, scene)

                    should_end = self.story_manager.increment_turn()
                    self.turn_count = self.story_manager.turn_count

                    if should_end and not self.in_combat:
                        self.trigger_game_ending()
                        return

                    player_context = self.player.get_context_for_ai()
                    new_scene, new_choices = self.ai_engine.generate_scene(
                        player_context,
                        player_choice=selected_choice
                    )

                    if not new_choices or len(new_choices) < 2:
                        logger.warning("AI returned invalid choices, using defaults")
                        new_choices = ["Continue forward", "Look around", "Check inventory"]

                    encounter_triggered, reason = self.story_manager.should_trigger_encounter(
                        new_scene,
                        self.ai_engine.location
                    )

                    if encounter_triggered:
                        self.start_combat()
                        return

                    shop_triggered = self._check_for_shop(new_scene, selected_choice)

                    if shop_triggered:
                        self.start_shop()
                        return

                    scene = new_scene
                    choices = new_choices

                    effect_descriptions = self.player.process_status_effects()
                    if effect_descriptions:
                        for desc in effect_descriptions:
                            self.ui.print_message(f"  {desc}", Colors.COMBAT)

                    self.display_game_state()
                    self.ui.print_scene(scene)
                    self.ui.print_choices(choices)
                    print(f"{Colors.INFO}  [I]nventory [E]quipment [S]tats [H]elp [Q]uit{Colors.RESET}\n")

                    self.save_game(auto=True)
                    
                    turns_in_chapter = self.turn_count - self.chapter_turn_start
                    if turns_in_chapter >= 100:
                        self.current_chapter += 1
                        self.chapter_turn_start = self.turn_count
                        self.ui.print_message(f"\n  ═══ CHAPTER {self.current_chapter} BEGINS ═══", Colors.BOLD)
                        self.ui.wait_for_enter()
                else:
                    attempts += 1
                    self.ui.print_error(f"Please enter a number between 1 and {len(choices)}")
                    if attempts >= max_attempts:
                        self.ui.print_error("Too many invalid attempts. Type 'help' for assistance or 'quit' to save and exit.")
                        attempts = 0
            except ValueError:
                attempts += 1
                self.ui.print_error("Please enter a valid number")
                if attempts >= max_attempts:
                    self.ui.print_error("Too many invalid attempts. Type 'help' for assistance or 'quit' to save and exit.")
                    attempts = 0

    def _check_for_shop(self, scene: str, choice: str) -> bool:
        scene_lower = scene.lower()
        choice_lower = choice.lower()

        shop_keywords = [
            "shop", "store", "merchant", "trader", "vendor", "seller",
            "market", "bazaar", "innkeeper offers", "blacksmith",
            "buy", "sell", "trade", "gold"
        ]

        for keyword in shop_keywords:
            if keyword in scene_lower or keyword in choice_lower:
                if "enter" in choice_lower or "visit" in choice_lower or \
                   "shop" in choice_lower or "buy" in choice_lower or \
                   "talk" in choice_lower or "speak" in choice_lower:
                    return True

        return False

    def analyze_choice_for_villainy(self, choice: str, scene: str) -> None:
        choice_lower = choice.lower()
        scene_lower = scene.lower()

        betrayal_keywords = ["betray", "backstab", "abandon ally", "sacrifice",
                           "sell out", "give up", "leave them", "let them die"]
        for keyword in betrayal_keywords:
            if keyword in choice_lower:
                self.story_manager.record_betrayal("NPC/Ally")
                return

        innocent_keywords = ["kill villager", "harm innocent", "attack civilian",
                           "burn village", "plague", "poison well", "hurt them"]
        for keyword in innocent_keywords:
            if keyword in choice_lower:
                self.story_manager.record_innocent_harmed(choice)
                return

        dark_keywords = ["cursed artifact", "dark power", "forbidden magic",
                        "demon weapon", "evil relic", "corrupt", "darkness"]
        for keyword in dark_keywords:
            if keyword in choice_lower or keyword in scene_lower:
                if "take" in choice_lower or "claim" in choice_lower or "use" in choice_lower:
                    self.story_manager.record_dark_artifact("Dark Power/Artifact")
                    return

        selfish_keywords = ["for myself", "my own gain", "abandon them", "let them",
                          "sacrifice them", "my power", "I become"]
        for keyword in selfish_keywords:
            if keyword in choice_lower:
                self.story_manager.record_selfish_choice(choice)
                return

        villain_keywords = ["destroy", "kill all", "wipe out", "enslave", "dominate",
                          "rule", "conquer", "dark lord", "evil"]
        for keyword in villain_keywords:
            if keyword in choice_lower:
                self.story_manager.record_villainous_act("villainous", choice)
                return

    def trigger_game_ending(self) -> None:
        self.ui.clear_screen()
        self.ui.print_header()

        print(f"{Colors.INFO}  Your journey has reached its conclusion...{Colors.RESET}\n")
        print(f"{Colors.STATS}  Turns Survived: {self.story_manager.turn_count}{Colors.RESET}\n")

        ending_prompt = self.story_manager.generate_ending_prompt()

        try:
            messages = [
                {"role": "system", "content": "You are narrating the epic conclusion of a fantasy adventure. Be conclusive and dramatic."},
                {"role": "user", "content": ending_prompt}
            ]

            response = self.ai_engine.client.chat.completions.create(
                model=self.ai_engine.MODEL_NAME,
                messages=messages,
                max_tokens=800,
                temperature=0.9,
            )

            ending_text = response.choices[0].message.content.strip()

            self.ui.print_message("\n" + "=" * 60, Colors.NARRATION)
            self.ui.print_message("                    THE END", Colors.BOLD)
            self.ui.print_message("=" * 60 + "\n", Colors.NARRATION)
            self.ui.print_scene(ending_text)
            self.ui.print_separator()

        except Exception as e:
            ending_type = self.story_manager.get_ending_type()
            self.ui.print_message(f"\n  Ending: {ending_type.replace('_', ' ').title()}", Colors.BOLD)
            self.ui.print_message(f"  You survived {self.story_manager.turn_count} turns.", Colors.NARRATION)
            self.ui.print_message(f"  Enemies defeated: {self.story_manager.enemies_defeated}", Colors.NARRATION)
            self.ui.print_message(f"  Locations visited: {len(self.story_manager.locations_visited)}", Colors.NARRATION)

        self.ui.wait_for_enter()

        self.game_over = True
        self.game_ended = True

        self.ui.print_message("\n  Your adventure has been saved for posterity.", Colors.INFO)
        self.ui.print_message("  Thank you for playing!", Colors.SUCCESS)
        self.ui.wait_for_enter()

    def start_combat(self) -> None:
        self.in_combat = True
        self.in_shop = False

        enemy = Enemy.create_random(self.player.level)
        self.combat = Combat(self.player, enemy)

        self.ui.clear_screen()
        self.ui.print_header()

        encounter_text, enemy_hint = self.ai_engine.generate_encounter(
            self.player.get_context_for_ai(),
            self.ai_engine.location
        )

        self.ui.print_message(f"\n{encounter_text}\n", Colors.ENEMY)
        self.ui.print_enemy(
            self.combat.enemy.name,
            self.combat.enemy.hp,
            self.combat.enemy.max_hp,
            self.combat.enemy.level
        )

        self.ui.wait_for_enter()

    def handle_combat(self) -> None:
        while self.in_combat and self.player.is_alive() and self.combat.enemy.is_alive():
            self.display_game_state()
            self.ui.print_enemy(
                self.combat.enemy.name,
                self.combat.enemy.hp,
                self.combat.enemy.max_hp,
                self.combat.enemy.level
            )
            self.ui.print_combat_actions()

            action = self.ui.get_input("Combat action: ").lower().strip()

            if action in ["inventory", "inv", "i"]:
                self.ui.print_inventory_detailed(self.player)
                self.ui.wait_for_enter()
                continue

            if action in ["equipment", "equip", "e"]:
                self.ui.print_equipment(self.player)
                self.ui.wait_for_enter()
                continue

            if action in ["stats", "s"]:
                self.ui.print_full_stats(self.player)
                self.ui.wait_for_enter()
                continue

            if action in ["help", "h", "?"]:
                self.ui.print_help()
                self.ui.wait_for_enter()
                continue

            if action in ["quit", "exit", "q"]:
                if self.ui.confirm("Save and quit?"):
                    self.save_game()
                    self.game_over = True
                return

            if action == "a":
                action = "attack"
            elif action == "d":
                action = "defend"
            elif action == "r":
                action = "run"
            elif action.startswith("u "):
                action = action

            item_name = None
            if action.startswith("use "):
                parts = action.split(None, 1)
                if len(parts) > 1:
                    item_name = parts[1]

            results = self.combat.execute_turn(action, item_name)

            self.display_game_state()

            if results["player_description"]:
                self.ui.print_message(f"  {results['player_description']}", Colors.COMBAT)

            if results["enemy_description"]:
                self.ui.print_message(f"  {results['enemy_description']}", Colors.ENEMY)

            if results["victory"]:
                self.ui.print_success(f"Victory! Defeated {self.combat.enemy.name}!")
                self.ui.print_success(f"  +{results['gold_earned']} Gold | +{results['xp_earned']} XP")

                if results["item_dropped"]:
                    self.ui.print_success(f"  Found: {results['item_dropped']}!")

                self.story_manager.record_enemy_defeated()

                if self.player.xp >= self.player.xp_to_level:
                    self.ui.print_level_up(self.player)

                self.in_combat = False
                self.combat = None
                self.ui.wait_for_enter()
                return

            if results["defeat"]:
                self.ui.print_error("You have been defeated...")
                self.ui.wait_for_enter()
                self.game_over = True
                return

            if results["escaped"]:
                self.ui.print_warning("You escaped from combat!")
                self.in_combat = False
                self.combat = None
                self.ui.wait_for_enter()
                return

            if self.player.status_effects or self.combat.enemy.status_effects:
                self.ui.print_status_effects(self.player.status_effects)

            if self.combat.enemy.is_alive():
                self.ui.print_enemy(
                    self.combat.enemy.name,
                    self.combat.enemy.hp,
                    self.combat.enemy.max_hp,
                    self.combat.enemy.level
                )

            self.ui.wait_for_enter()

        self.in_combat = False
        self.combat = None

    def start_shop(self) -> None:
        self.in_shop = True
        self.in_combat = False

        self.shop = find_shop(self.player.level)

        self.ui.clear_screen()
        self.ui.print_header()
        self.ui.print_shop(self.shop)
        print(f"{Colors.INFO}  [B]uy [S]ell [L]eave Shop{Colors.RESET}\n")

    def handle_shop(self) -> None:
        while self.in_shop:
            self.display_game_state()
            self.ui.print_shop(self.shop)
            print(f"{Colors.INFO}  [B]uy [S]ell [L]eave Shop{Colors.RESET}\n")

            action = self.ui.get_input("Shop action: ").lower().strip()

            if action in ["b", "buy"]:
                self._handle_buy()
            elif action in ["s", "sell"]:
                self._handle_sell()
            elif action in ["l", "leave", "exit", "q"]:
                self.in_shop = False
                self.shop = None
                return
            elif action in ["i", "inv", "inventory"]:
                self.ui.print_inventory_detailed(self.player)
                self.ui.wait_for_enter()
            elif action in ["e", "equip", "equipment"]:
                self.ui.print_equipment(self.player)
                self.ui.wait_for_enter()
            else:
                self.ui.print_error("Invalid command. Use [B]uy, [S]ell, or [L]eave")

    def _handle_buy(self) -> None:
        item_name = self.ui.get_input("Item to buy: ").strip().lower()

        if not item_name:
            return

        matching_item = None
        for shop_item in self.shop.inventory:
            if item_name in shop_item.lower():
                matching_item = shop_item
                break

        if not matching_item:
            self.ui.print_error("Item not found in shop")
            self.ui.wait_for_enter()
            return

        quantity = 1
        qty_input = self.ui.get_input(f"Quantity (default 1): ").strip()
        if qty_input:
            try:
                quantity = max(1, int(qty_input))
            except ValueError:
                quantity = 1

        success, message = self.shop.buy_item(self.player, matching_item, quantity)

        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)

        self.ui.wait_for_enter()

    def _handle_sell(self) -> None:
        if not self.player.inventory:
            self.ui.print_message("  You have nothing to sell.", Colors.INFO)
            self.ui.wait_for_enter()
            return

        self.ui.print_inventory_detailed(self.player)
        item_name = self.ui.get_input("Item to sell: ").strip().lower()

        if not item_name:
            return

        if not self.player.has_item(item_name):
            self.ui.print_error("You don't have that item")
            self.ui.wait_for_enter()
            return

        quantity = 1
        qty_input = self.ui.get_input(f"Quantity (default 1, have {self.player.get_item_quantity(item_name)}): ").strip()
        if qty_input:
            try:
                quantity = max(1, int(qty_input))
            except ValueError:
                quantity = 1

        success, message = self.shop.sell_item(self.player, item_name, quantity)

        if success:
            self.ui.print_success(message)
        else:
            self.ui.print_error(message)

        self.ui.wait_for_enter()

    def handle_commands(self, user_input: str) -> Optional[bool]:
        cmd = user_input.lower().strip()

        if cmd in ["inventory", "inv", "i"]:
            self.ui.print_inventory_detailed(self.player)
            self.ui.wait_for_enter()
            return True

        if cmd in ["equipment", "equip", "e"]:
            self._handle_equipment()
            return True

        if cmd in ["stats", "status", "s"]:
            self.ui.print_full_stats(self.player)
            self.ui.wait_for_enter()
            return True

        if cmd in ["help", "h", "?"]:
            self.ui.print_help()
            self.ui.wait_for_enter()
            return True

        if cmd in ["quit", "exit", "q"]:
            if self.ui.confirm("Save and quit?"):
                self.save_game()
                return False
            return True

        if cmd in ["save"]:
            self.save_game(auto=False)
            self.ui.wait_for_enter()
            return True

        if cmd in ["load"]:
            return self._handle_load_game()

        return None

    def _handle_equipment(self) -> None:
        while True:
            self.ui.clear_screen()
            self.ui.print_header("EQUIPMENT")
            self.ui.print_equipment(self.player)
            self.ui.print_inventory_detailed(self.player)

            print(f"{Colors.EQUIPMENT}  [E]quip [U]nequip [L]eave{Colors.RESET}\n")

            action = self.ui.get_input("Equipment action: ").lower().strip()

            if action in ["e", "equip"]:
                item_name = self.ui.get_input("Item to equip: ").strip()
                if item_name:
                    success, message = self.player.equip_item(item_name)
                    if success:
                        self.ui.print_success(message)
                    else:
                        self.ui.print_error(message)
                    self.ui.wait_for_enter()

            elif action in ["u", "unequip"]:
                slot = self.ui.get_input("Slot to unequip (weapon/armor/accessory): ").lower().strip()
                if slot:
                    success, message = self.player.unequip_item(slot)
                    if success:
                        self.ui.print_success(message)
                    else:
                        self.ui.print_error(message)
                    self.ui.wait_for_enter()

            elif action in ["l", "leave", "exit", ""]:
                return

    def _handle_load_game(self) -> Optional[bool]:
        saves = self.save_system.list_saves()

        print(f"\n{Colors.INFO}  Available Saves:{Colors.RESET}\n")

        for save_info in saves:
            slot = save_info["slot"]
            if save_info["exists"]:
                if "error" in save_info:
                    print(f"{Colors.ERROR}    Slot {slot}: {save_info['error']}{Colors.RESET}")
                else:
                    info = self.save_system.get_save_info(slot)
                    print(f"{Colors.SUCCESS}    {info}{Colors.RESET}")
            else:
                print(f"{Colors.INFO}    Slot {slot}: (empty){Colors.RESET}")

        print()

        choice = self.ui.get_input("Load slot (1-3, or 'cancel'): ").strip()

        if choice.lower() in ["cancel", "c", ""]:
            return True

        try:
            slot = int(choice)
            if 1 <= slot <= 3:
                if self.save_system.has_save(slot):
                    if self.ui.confirm("Current progress will be lost. Load this save?"):
                        self.save_system = SaveSystem(slot=slot)
                        return self.load_game()
                else:
                    self.ui.print_error(f"Slot {slot} is empty")
                    self.ui.wait_for_enter()
            else:
                self.ui.print_error("Please enter 1, 2, or 3")
                self.ui.wait_for_enter()
        except ValueError:
            self.ui.print_error("Please enter a number")
            self.ui.wait_for_enter()

        return True

    def run(self) -> None:
        if not self.initialize():
            return

        if hasattr(self, 'game_ended') and not self.game_ended and self.story_manager.starting_point:
            self._show_starting_point()

        if self.in_combat:
            self.ui.print_message("  You are still in combat!", Colors.ENEMY)
            self.ui.wait_for_enter()

        while not self.game_over and self.player.is_alive():
            if self.in_combat:
                self.handle_combat()
            elif self.in_shop:
                self.handle_shop()
            else:
                self.handle_exploration()

        if not self.player.is_alive():
            self.ui.print_game_over(victory=False)
            self.save_system.delete_save()
            print(f"\n{Colors.INFO}  Better luck next time!{Colors.RESET}\n")
        elif hasattr(self, 'game_ended') and self.game_ended:
            pass
        else:
            self.ui.print_message("  Thanks for playing!", Colors.SUCCESS)

        self.ui.print_separator()

    def _show_starting_point(self) -> None:
        if not self.story_manager.starting_point:
            return

        sp = self.story_manager.starting_point

        self.ui.clear_screen()
        self.ui.print_header("YOUR ADVENTURE BEGINS")

        print(f"{Colors.NARRATION}  Starting Location: {sp.name}{Colors.RESET}\n")
        print(f"{Colors.NARRATION}  {sp.description}{Colors.RESET}\n")
        print(f"{Colors.NARRATION}  {sp.initial_scene}{Colors.RESET}\n")

        self.ui.print_choices(sp.choices)

        if sp.starting_items:
            for item in sp.starting_items:
                self.player.add_item(item)
            print(f"{Colors.SUCCESS}  Received starting items: {', '.join(sp.starting_items)}{Colors.RESET}\n")

        if sp.starting_gold > 0:
            self.player.add_gold(sp.starting_gold)
            print(f"{Colors.SUCCESS}  Received {sp.starting_gold} gold{Colors.RESET}\n")

        self.story_manager.record_location(sp.name)

        self.ui.wait_for_enter()


def check_update_on_startup() -> None:
    try:
        from .updater import check_for_update

        available, current, latest = check_for_update()
        if available:
            print(f"\n{Colors.WARNING}  ⚡ Update available: v{current} → v{latest}{Colors.RESET}")
            print(f"{Colors.INFO}  Run 'trpg update' to install the latest version!{Colors.RESET}\n")
    except Exception:
        pass


def main():
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()

        if command == "update":
            try:
                from .updater import update_interactive
                update_interactive()
            except Exception as e:
                print(f"\n{Colors.ERROR}Update failed: {e}{Colors.RESET}")
                print(f"\n{Colors.INFO}Try manual update: pip install --upgrade ai-terminal-rpg{Colors.RESET}")
            return

        elif command == "version":
            try:
                from trpg import __version__
                print(f"AI Terminal RPG v{__version__}")
            except ImportError:
                print(f"AI Terminal RPG v{updater.CURRENT_VERSION}")
            return

        elif command in ["help", "-h", "--help"]:
            print(f"""
{Colors.BOLD}AI TERMINAL RPG{Colors.RESET}
A terminal-based AI-powered text RPG

{Colors.BOLD}Usage:{Colors.RESET}
  trpg              Start the game
  trpg update       Check for and install updates
  trpg version      Show current version
  trpg help         Show this help message

{Colors.BOLD}In-Game Commands:{Colors.RESET}
  [I]nventory       View your items
  [E]quipment       View/change equipped items
  [S]tats           View character stats
  [H]elp            Show help
  [Q]uit            Save and quit
  [1-3]             Make story choices
  [A]ttack          Combat attack
  [D]efend          Combat defend
  [R]un             Combat escape
  [U]se <item>      Use item

{Colors.BOLD}Requirements:{Colors.RESET}
  - Python 3.8+
  - Cerebras AI API key (free at https://cloud.cerebras.ai/)
""")
            return

    try:
        check_update_on_startup()

        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
