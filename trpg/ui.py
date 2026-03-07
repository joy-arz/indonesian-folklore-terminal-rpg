
import os
import sys
from typing import List, Optional, Dict, Any

from colorama import init, Fore, Back, Style

init(autoreset=True)


class Colors:
    NARRATION = Fore.GREEN
    CHOICES = Fore.YELLOW
    ENEMY = Fore.RED
    STATS = Fore.CYAN
    COMBAT = Fore.MAGENTA
    INFO = Fore.WHITE
    ERROR = Fore.RED
    SUCCESS = Fore.GREEN
    WARNING = Fore.YELLOW
    SHOP = Fore.BLUE
    EQUIPMENT = Fore.MAGENTA

    BOLD = Style.BRIGHT
    RESET = Style.RESET_ALL


class UI:

    WIDTH = 70
    SEPARATOR = "=" * WIDTH
    THIN_SEPARATOR = "-" * WIDTH

    QUICK_KEYS = {
        "inventory": ["i", "inv", "inventory"],
        "equipment": ["e", "equip", "equipment"],
        "stats": ["s", "stats", "status"],
        "help": ["h", "help", "?"],
        "quit": ["q", "quit", "exit"],
        "save": ["save"],
        "shop": ["shop", "buy", "sell"],
        "attack": ["attack", "a"],
        "defend": ["defend", "d"],
        "run": ["run", "r", "flee", "escape"],
        "use": ["use", "u"],
    }

    def __init__(self):
        pass

    def clear_screen(self) -> None:
        os.system('cls' if os.name == 'nt' else 'clear')

    def print_header(self, title: str = "AI TERMINAL RPG") -> None:
        print(f"\n{Colors.BOLD}{Colors.STATS}{self.SEPARATOR}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.STATS}{title.center(self.WIDTH)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.STATS}{self.SEPARATOR}{Colors.RESET}\n")

    def print_stats_bar(self, hp: int, max_hp: int, xp: int = 0,
                        max_xp: int = 100, level: int = 1) -> None:
        hp_bar = self._create_hp_bar(hp, max_hp, width=20)
        xp_bar = self._create_hp_bar(xp, max_xp, width=10)

        stats_line = (
            f"{Colors.BOLD}HP: {hp_bar} {hp}/{max_hp}  "
            f"XP: {xp_bar} {xp}/{max_xp}  "
            f"LVL: {level}{Colors.RESET}"
        )
        print(stats_line)
        print()

    def print_full_stats(self, player) -> None:
        equip_bonus = player.get_equipment_stats()

        print(f"{Colors.STATS}╔{'═' * 66}╗{Colors.RESET}")
        print(f"{Colors.STATS}║{Colors.BOLD} CHARACTER STATS {Colors.RESET}".ljust(68) + f"{Colors.STATS}║{Colors.RESET}")
        print(f"{Colors.STATS}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.STATS}║{Colors.RESET}  HP: {player.hp}/{player.max_hp}".ljust(67) + f"{Colors.STATS}║{Colors.RESET}")
        print(f"{Colors.STATS}║{Colors.RESET}  Attack: {player.attack} (base: {player.base_attack}, equip: +{equip_bonus['attack']})".ljust(67) + f"{Colors.STATS}║{Colors.RESET}")
        print(f"{Colors.STATS}║{Colors.RESET}  Defense: {player.defense} (base: {player.base_defense}, equip: +{equip_bonus['defense']})".ljust(67) + f"{Colors.STATS}║{Colors.RESET}")
        print(f"{Colors.STATS}║{Colors.RESET}  Gold: {player.gold}".ljust(67) + f"{Colors.STATS}║{Colors.RESET}")
        print(f"{Colors.STATS}║{Colors.RESET}  Level: {player.level} | XP: {player.xp}/{player.xp_to_level}".ljust(67) + f"{Colors.STATS}║{Colors.RESET}")
        print(f"{Colors.STATS}╚{'═' * 66}╝{Colors.RESET}")
        print()

    def print_scene(self, scene: str) -> None:
        wrapped = self._wrap_text(scene, self.WIDTH - 2)
        print(f"{Colors.NARRATION}  {wrapped}{Colors.RESET}\n")

    def print_choices(self, choices: List[str]) -> None:
        print(f"{Colors.CHOICES}  ┌─ Choices ─────────────────────────────────────────────────────┐{Colors.RESET}")
        for i, choice in enumerate(choices, 1):
            print(f"{Colors.CHOICES}  │  {i}. {choice:<60} │{Colors.RESET}")
        print(f"{Colors.CHOICES}  └{'─' * 65}┘{Colors.RESET}")
        print()

    def print_equipment(self, player) -> None:
        print(f"{Colors.EQUIPMENT}╔{'═' * 66}╗{Colors.RESET}")
        print(f"{Colors.EQUIPMENT}║{Colors.BOLD} EQUIPMENT {Colors.RESET}".ljust(68) + f"{Colors.EQUIPMENT}║{Colors.RESET}")
        print(f"{Colors.EQUIPMENT}╠{'═' * 66}╣{Colors.RESET}")

        for slot in ["weapon", "armor", "accessory"]:
            item = player.get_equipped(slot)
            if item:
                stats = f"+{item.attack} ATK, +{item.defense} DEF"
                line = f"  {slot.capitalize():12}: {item.name:<35} [{stats}]"
            else:
                line = f"  {slot.capitalize():12}: (empty)"
            print(f"{Colors.EQUIPMENT}║{Colors.RESET}  {line}".ljust(68) + f"{Colors.EQUIPMENT}║{Colors.RESET}")

        print(f"{Colors.EQUIPMENT}╚{'═' * 66}╝{Colors.RESET}")
        print()

    def print_inventory_detailed(self, player) -> None:
        print(f"{Colors.INFO}╔{'═' * 66}╗{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.BOLD} INVENTORY {Colors.RESET}".ljust(68) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")

        if not player.inventory:
            print(f"{Colors.INFO}║{Colors.RESET}  Your inventory is empty.".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        else:
            by_category = {}
            for item in player.inventory:
                cat = item.category.value
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(item)

            for category, items in sorted(by_category.items()):
                cat_line = f"  ┌─ {category.upper()} {'─' * 50}"
                print(f"{Colors.INFO}║{Colors.RESET}{cat_line}".ljust(68) + f"{Colors.INFO}║{Colors.RESET}")

                for item in items:
                    stats = ""
                    if item.attack > 0:
                        stats += f" +{item.attack} ATK"
                    if item.defense > 0:
                        stats += f" +{item.defense} DEF"
                    if item.heal > 0:
                        stats += f" +{item.heal} HP"

                    item_line = f"  │  • {item.name} x{item.quantity}{stats}"
                    print(f"{Colors.INFO}║{Colors.RESET}{item_line}".ljust(68) + f"{Colors.INFO}║{Colors.RESET}")

                print(f"{Colors.INFO}║{Colors.RESET}  └{'─' * 55}".ljust(68) + f"{Colors.INFO}║{Colors.RESET}")

        print(f"{Colors.INFO}╚{'═' * 66}╝{Colors.RESET}")
        print()

    def print_combat_actions(self) -> None:
        print(f"{Colors.COMBAT}  ┌─ Combat Actions ──────────────────────────────────────────────┐{Colors.RESET}")
        print(f"{Colors.COMBAT}  │  [A] Attack    - Attack the enemy                            │{Colors.RESET}")
        print(f"{Colors.COMBAT}  │  [D] Defend    - Reduce damage taken (50%)                   │{Colors.RESET}")
        print(f"{Colors.COMBAT}  │  [U] Use <item>- Use an item (e.g., 'use potion')            │{Colors.RESET}")
        print(f"{Colors.COMBAT}  │  [R] Run       - Attempt to flee                             │{Colors.RESET}")
        print(f"{Colors.COMBAT}  └{'─' * 65}┘{Colors.RESET}")
        print()

    def print_enemy(self, name: str, hp: int, max_hp: int, level: int = 1) -> None:
        hp_bar = self._create_hp_bar(hp, max_hp, width=25)
        print(f"{Colors.ENEMY}{Colors.BOLD}  ╔════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.ENEMY}{Colors.BOLD}  ║ ENEMY: {name:<55} ║{Colors.RESET}")
        print(f"{Colors.ENEMY}{Colors.BOLD}  ║ HP: {hp_bar} {hp}/{max_hp}{' ' * 10}║{Colors.RESET}")
        print(f"{Colors.ENEMY}{Colors.BOLD}  ╚════════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()

    def _create_hp_bar(self, current: int, maximum: int, width: int = 20) -> str:
        if maximum <= 0:
            return "[" + " " * width + "]"

        filled = int((current / maximum) * width)
        empty = width - filled

        if current > maximum * 0.6:
            color = Fore.GREEN
        elif current > maximum * 0.3:
            color = Fore.YELLOW
        else:
            color = Fore.RED

        return f"[{color}{'█' * filled}{Style.RESET_ALL}{' ' * empty}]"

    def _wrap_text(self, text: str, width: int) -> str:
        words = text.split()
        lines = []
        current_line = ""

        for word in words:
            if len(current_line) + len(word) + 1 <= width:
                if current_line:
                    current_line += " " + word
                else:
                    current_line = word
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word

        if current_line:
            lines.append(current_line)

        return "\n  ".join(lines)

    def print_message(self, message: str, color: str = Colors.INFO) -> None:
        print(f"{color}{message}{Colors.RESET}")

    def print_error(self, message: str) -> None:
        print(f"{Colors.ERROR}  ✗ Error: {message}{Colors.RESET}\n")

    def print_success(self, message: str) -> None:
        print(f"{Colors.SUCCESS}  ✓ {message}{Colors.RESET}\n")

    def print_warning(self, message: str) -> None:
        print(f"{Colors.WARNING}  ⚠ {message}{Colors.RESET}\n")

    def print_separator(self, thick: bool = True) -> None:
        if thick:
            print(Colors.INFO + self.SEPARATOR + Colors.RESET)
        else:
            print(Colors.INFO + self.THIN_SEPARATOR + Colors.RESET)

    def get_input(self, prompt: str = "Your choice: ") -> str:
        try:
            user_input = input(f"{Colors.CHOICES}  {prompt}{Colors.RESET}")
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return "quit"

    def get_numbered_choice(self, max_choice: int) -> Optional[int]:
        while True:
            user_input = self.get_input(f"Your choice (1-{max_choice}): ")

            if user_input.lower() in ["quit", "exit", "q"]:
                return None

            try:
                choice = int(user_input)
                if 1 <= choice <= max_choice:
                    return choice
                else:
                    self.print_error(f"Please enter a number between 1 and {max_choice}")
            except ValueError:
                self.print_error("Please enter a valid number")

    def get_command(self) -> str:
        return self.get_input("Command: ").lower()

    def confirm(self, message: str) -> bool:
        while True:
            response = self.get_input(f"{message} (y/n): ").lower()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            else:
                self.print_error("Please enter 'y' or 'n'")

    def print_inventory(self, items: List) -> None:
        print(f"{Colors.INFO}  === Inventory ==={Colors.RESET}")
        if not items:
            print(f"{Colors.INFO}  Your inventory is empty.{Colors.RESET}")
        else:
            for item in items:
                print(f"{Colors.INFO}    • {item}{Colors.RESET}")
        print()

    def print_help(self) -> None:
        print(f"{Colors.INFO}╔{'═' * 66}╗{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.BOLD} HELP - Available Commands                          {Colors.RESET}".ljust(68) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [I] Inventory  - View your items                 {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [E] Equipment  - View/change equipped items      {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [S] Stats      - View character status           {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [H] Help       - Show this help message          {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [Q] Quit       - Save and quit game              {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.BOLD} CLI TIPS                                           {Colors.RESET}".ljust(68) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  This game teaches command line interface (CLI)   {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  Type commands and press Enter to execute         {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  During Story:                                    {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}    Enter a number (1-3) to make a choice          {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  During Combat:                                   {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}    [A] Attack, [D] Defend, [U] Use item, [R] Run  {Colors.RESET}".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╚{'═' * 66}╝{Colors.RESET}")
        print()

    def print_shop(self, shop) -> None:
        print(f"{Colors.SHOP}╔{'═' * 66}╗{Colors.RESET}")
        print(f"{Colors.SHOP}║{Colors.BOLD} {shop.name:^64} ║{Colors.RESET}")
        print(f"{Colors.SHOP}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.SHOP}║{Colors.RESET}  Shop Gold Available: {shop.gold}g".ljust(67) + f"{Colors.SHOP}║{Colors.RESET}")
        print(f"{Colors.SHOP}╠{'═' * 66}╣{Colors.RESET}")

        for item_name, qty in sorted(shop.inventory.items()):
            if qty <= 0:
                continue
            price = shop.get_buy_price(item_name)
            print(f"{Colors.SHOP}║{Colors.RESET}  • {item_name} (x{qty}) - {price}g".ljust(67) + f"{Colors.SHOP}║{Colors.RESET}")

        print(f"{Colors.SHOP}╚{'═' * 66}╝{Colors.RESET}")
        print()

    def print_level_up(self, player) -> None:
        self.clear_screen()
        self.print_header()
        print(f"\n{Colors.SUCCESS}{Colors.BOLD}{'╔' + '═' * 66 + '╗'}{Colors.RESET}")
        print(f"{Colors.SUCCESS}{Colors.BOLD}{'║' + 'LEVEL UP!'.center(66) + '║'}{Colors.RESET}")
        print(f"{Colors.SUCCESS}{Colors.BOLD}{'╠' + '═' * 66 + '╣'}{Colors.RESET}")
        print(f"{Colors.SUCCESS}{'║' + f'You reached Level {player.level}!'.center(66) + '║'}{Colors.RESET}")
        print(f"{Colors.SUCCESS}{'║' + f'HP: +5 | Attack: +2 | Defense: +1'.center(66) + '║'}{Colors.RESET}")
        print(f"{Colors.SUCCESS}{Colors.BOLD}{'╚' + '═' * 66 + '╝'}{Colors.RESET}\n")
        self.wait_for_enter()

    def print_game_over(self, victory: bool = False) -> None:
        self.clear_screen()
        self.print_header()

        if victory:
            print(f"\n{Colors.SUCCESS}{Colors.BOLD}{'VICTORY!':^70}{Colors.RESET}\n")
            print(f"{Colors.SUCCESS}You have triumphed over your foes!{Colors.RESET}\n")
        else:
            print(f"\n{Colors.ENEMY}{Colors.BOLD}{'GAME OVER':^70}{Colors.RESET}\n")
            print(f"{Colors.ENEMY}Your adventure has come to an end...{Colors.RESET}\n")

        self.print_separator()

    def print_loading(self, message: str = "Loading") -> None:
        print(f"{Colors.INFO}{message}...{Colors.RESET}")

    def wait_for_enter(self, message: str = "Press Enter to continue") -> None:
        input(f"{Colors.INFO}  {message}{Colors.RESET}")

    def print_status_effects(self, effects: List) -> None:
        if not effects:
            return

        print(f"{Colors.COMBAT}  Status Effects:{Colors.RESET}")
        for effect in effects:
            if effect.effect_type == "buff":
                print(f"{Colors.SUCCESS}    + {effect.name} ({effect.duration} turns){Colors.RESET}")
            else:
                print(f"{Colors.ERROR}    - {effect.name} ({effect.duration} turns){Colors.RESET}")
        print()
