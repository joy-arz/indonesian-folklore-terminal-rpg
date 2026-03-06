"""
UI module - terminal user interface with colored output.

This module handles all terminal display using colorama for:
- Colored text output (green narration, yellow choices, red enemies)
- Clean formatting and layout
- User input handling with quick keys
- Screen clearing and formatting
- Equipment display
- Status bars and visual elements
"""

import os
import sys
from typing import List, Optional, Dict, Any

from colorama import init, Fore, Back, Style

init(autoreset=True)


class Colors:
    """Color codes for terminal output."""
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
    """
    Terminal user interface manager.
    
    Provides methods for:
    - Displaying game screens with consistent formatting
    - Showing colored text for different content types
    - Getting and validating user input
    - Clearing and formatting the terminal
    - Visual HP/XP bars
    """
    
    WIDTH = 70
    SEPARATOR = "=" * WIDTH
    THIN_SEPARATOR = "-" * WIDTH
    
    # Quick key mappings
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
        """Initialize the UI."""
        pass
    
    def clear_screen(self) -> None:
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self, title: str = "AI TERMINAL RPG") -> None:
        """Print the game header."""
        print(f"\n{Colors.BOLD}{Colors.STATS}{self.SEPARATOR}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.STATS}{title.center(self.WIDTH)}{Colors.RESET}")
        print(f"{Colors.BOLD}{Colors.STATS}{self.SEPARATOR}{Colors.RESET}\n")
    
    def print_stats_bar(self, hp: int, max_hp: int, xp: int = 0, 
                        max_xp: int = 100, level: int = 1) -> None:
        """
        Print player stats bar with HP and XP.
        
        Args:
            hp: Current HP
            max_hp: Maximum HP
            xp: Current XP
            max_xp: XP needed for next level
            level: Current level
        """
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
        """
        Print complete player stats including equipment bonuses.
        
        Args:
            player: Player object
        """
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
        """Print a story scene with narration coloring."""
        # Word wrap the scene text
        wrapped = self._wrap_text(scene, self.WIDTH - 2)
        print(f"{Colors.NARRATION}  {wrapped}{Colors.RESET}\n")
    
    def print_choices(self, choices: List[str]) -> None:
        """Print numbered choices with choice coloring."""
        print(f"{Colors.CHOICES}  ┌─ Choices ─────────────────────────────────────────────────────┐{Colors.RESET}")
        for i, choice in enumerate(choices, 1):
            print(f"{Colors.CHOICES}  │  {i}. {choice:<60} │{Colors.RESET}")
        print(f"{Colors.CHOICES}  └{'─' * 65}┘{Colors.RESET}")
        print()
    
    def print_equipment(self, player) -> None:
        """
        Print player's equipment.
        
        Args:
            player: Player object
        """
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
        """
        Print detailed inventory with categories.
        
        Args:
            player: Player object
        """
        print(f"{Colors.INFO}╔{'═' * 66}╗{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.BOLD} INVENTORY {Colors.RESET}".ljust(68) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")
        
        if not player.inventory:
            print(f"{Colors.INFO}║{Colors.RESET}  Your inventory is empty.".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        else:
            # Group by category
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
        """Print available combat actions with quick keys."""
        print(f"{Colors.COMBAT}  ┌─ Combat Actions ──────────────────────────────────────────────┐{Colors.RESET}")
        print(f"{Colors.COMBAT}  │  [A] Attack    - Attack the enemy                            │{Colors.RESET}")
        print(f"{Colors.COMBAT}  │  [D] Defend    - Reduce damage taken (50%)                   │{Colors.RESET}")
        print(f"{Colors.COMBAT}  │  [U] Use <item>- Use an item (e.g., 'use potion')            │{Colors.RESET}")
        print(f"{Colors.COMBAT}  │  [R] Run       - Attempt to flee                             │{Colors.RESET}")
        print(f"{Colors.COMBAT}  └{'─' * 65}┘{Colors.RESET}")
        print()
    
    def print_enemy(self, name: str, hp: int, max_hp: int, level: int = 1) -> None:
        """Print enemy status with enemy coloring."""
        hp_bar = self._create_hp_bar(hp, max_hp, width=25)
        print(f"{Colors.ENEMY}{Colors.BOLD}  ╔════════════════════════════════════════════════════════════════╗{Colors.RESET}")
        print(f"{Colors.ENEMY}{Colors.BOLD}  ║ ENEMY: {name:<55} ║{Colors.RESET}")
        print(f"{Colors.ENEMY}{Colors.BOLD}  ║ HP: {hp_bar} {hp}/{max_hp}{' ' * 10}║{Colors.RESET}")
        print(f"{Colors.ENEMY}{Colors.BOLD}  ╚════════════════════════════════════════════════════════════════╝{Colors.RESET}")
        print()
    
    def _create_hp_bar(self, current: int, maximum: int, width: int = 20) -> str:
        """Create a visual HP/XP bar."""
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
        """Wrap text to specified width."""
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
        """Print a colored message."""
        print(f"{color}{message}{Colors.RESET}")
    
    def print_error(self, message: str) -> None:
        """Print an error message."""
        print(f"{Colors.ERROR}  ✗ Error: {message}{Colors.RESET}\n")
    
    def print_success(self, message: str) -> None:
        """Print a success message."""
        print(f"{Colors.SUCCESS}  ✓ {message}{Colors.RESET}\n")
    
    def print_warning(self, message: str) -> None:
        """Print a warning message."""
        print(f"{Colors.WARNING}  ⚠ {message}{Colors.RESET}\n")
    
    def print_separator(self, thick: bool = True) -> None:
        """Print a separator line."""
        if thick:
            print(Colors.INFO + self.SEPARATOR + Colors.RESET)
        else:
            print(Colors.INFO + self.THIN_SEPARATOR + Colors.RESET)
    
    def get_input(self, prompt: str = "Your choice: ") -> str:
        """Get user input with a prompt."""
        try:
            user_input = input(f"{Colors.CHOICES}  {prompt}{Colors.RESET}")
            return user_input.strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return "quit"
    
    def get_numbered_choice(self, max_choice: int) -> Optional[int]:
        """Get a numbered choice from user."""
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
        """Get a command from user."""
        return self.get_input("Command: ").lower()
    
    def confirm(self, message: str) -> bool:
        """Ask for user confirmation."""
        while True:
            response = self.get_input(f"{message} (y/n): ").lower()
            if response in ["y", "yes"]:
                return True
            elif response in ["n", "no"]:
                return False
            else:
                self.print_error("Please enter 'y' or 'n'")
    
    def print_inventory(self, items: List) -> None:
        """Print player inventory (simple version)."""
        print(f"{Colors.INFO}  === Inventory ==={Colors.RESET}")
        if not items:
            print(f"{Colors.INFO}  Your inventory is empty.{Colors.RESET}")
        else:
            for item in items:
                print(f"{Colors.INFO}    • {item}{Colors.RESET}")
        print()
    
    def print_help(self) -> None:
        """Print help information."""
        print(f"{Colors.INFO}╔{'═' * 66}╗{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.BOLD} BANTUAN - Perintah Tersedia {Colors.RESET}".ljust(68) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [I] Inventory  - Lihat item yang dimiliki".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [E] Equipment  - Lihat/ganti item yang dipakai".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [S] Stats      - Lihat status karakter".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [H] Help       - Tampilkan bantuan ini".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  [Q] Quit       - Simpan dan keluar".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.BOLD} 💡 TIPS CLI {Colors.RESET}".ljust(68) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  Game ini mengajarkan command line interface (CLI)".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  Ketik perintah di terminal, tekan Enter untuk eksekusi".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  Saat Cerita:".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}    Masukkan angka (1-3) untuk membuat pilihan".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}  Saat Pertempuran:".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}║{Colors.RESET}    [A] Attack, [D] Defend, [U] Use item, [R] Run".ljust(67) + f"{Colors.INFO}║{Colors.RESET}")
        print(f"{Colors.INFO}╚{'═' * 66}╝{Colors.RESET}")
        print()
    
    def print_shop(self, shop) -> None:
        """Print shop interface."""
        print(f"{Colors.SHOP}╔{'═' * 66}╗{Colors.RESET}")
        print(f"{Colors.SHOP}║{Colors.BOLD} {shop.name:^64} ║{Colors.RESET}")
        print(f"{Colors.SHOP}╠{'═' * 66}╣{Colors.RESET}")
        print(f"{Colors.SHOP}║{Colors.RESET}  Shop Gold Available: {shop.gold}g".ljust(67) + f"{Colors.SHOP}║{Colors.RESET}")
        print(f"{Colors.SHOP}╠{'═' * 66}╣{Colors.RESET}")
        
        # Print items for sale
        for item_name, qty in sorted(shop.inventory.items()):
            if qty <= 0:
                continue
            price = shop.get_buy_price(item_name)
            print(f"{Colors.SHOP}║{Colors.RESET}  • {item_name} (x{qty}) - {price}g".ljust(67) + f"{Colors.SHOP}║{Colors.RESET}")
        
        print(f"{Colors.SHOP}╚{'═' * 66}╝{Colors.RESET}")
        print()
    
    def print_level_up(self, player) -> None:
        """Print level up notification."""
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
        """Print game over screen."""
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
        """Print a loading message."""
        print(f"{Colors.INFO}{message}...{Colors.RESET}")
    
    def wait_for_enter(self, message: str = "Press Enter to continue") -> None:
        """Wait for user to press Enter."""
        input(f"{Colors.INFO}  {message}{Colors.RESET}")
    
    def print_status_effects(self, effects: List) -> None:
        """Print active status effects."""
        if not effects:
            return
        
        print(f"{Colors.COMBAT}  Status Effects:{Colors.RESET}")
        for effect in effects:
            if effect.effect_type == "buff":
                print(f"{Colors.SUCCESS}    + {effect.name} ({effect.duration} turns){Colors.RESET}")
            else:
                print(f"{Colors.ERROR}    - {effect.name} ({effect.duration} turns){Colors.RESET}")
        print()
