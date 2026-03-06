# AI Terminal RPG
[This Readme is AI-Generated cuz I am too lazy to write this stuff]

A terminal-based AI-powered text RPG where the story is generated dynamically by Cerebras AI's Llama model. Set in **Indonesian folklore and historical kingdoms**, the game features deep character customization, turn-based combat, equipment system, shops, and an immersive Aidungeon-style narrative experience in **Bahasa Indonesia**.

## 🎭 Educational Purpose

This game is designed to **educate players about Indonesian folklore and history** through interactive storytelling. Players will experience:

- **10 Historical Starting Points** - From Majapahit Empire to Sriwijaya Kingdom
- **Indonesian Mythology** - Encounter creatures like Genderuwo, Tuyul, Kuntilanak, and Nyai Roro Kidul
- **Cultural Heritage** - Learn about traditional weapons (keris), kingdoms, and legends
- **Bahasa Indonesia** - Immersive narrative in Indonesian language
- **Historical Events** - Experience pivotal moments like Perang Bubat and the rise of Islamic kingdoms

## Features

### Core Gameplay
- **Dynamic Story Generation**: AI generates unique story scenes based on your choices in an immersive Aidungeon style
- **Turn-Based Combat**: Strategic combat with attack, defend, use item, and run options
- **Consistent Encounter System**: Balanced random encounters with minimum turn intervals
- **Multiple Save Slots**: 3 save slots with metadata (playtime, location, level)

### Character Progression
- **XP & Leveling System**: Gain XP from combat, level up to increase stats
- **Equipment System**: Equip weapons, armor, and accessories with stat bonuses
- **Status Effects**: Buffs (strength, defense, regeneration) and debuffs (poison, burn, stun)
- **Base + Equipment Stats**: Separate tracking of base stats and equipment bonuses

### Economy & Items
- **Shop System**: Buy and sell items at various shop types (general, weapon, armor, magic, black market)
- **Item Database**: 40+ items including weapons, armor, accessories, and consumables
- **Item Effects**: Potions heal, equipment boosts stats, special items cure effects
- **Rarity System**: Common, uncommon, rare, and legendary items

### Enhanced UI
- **Visual HP/XP Bars**: Color-coded progress bars
- **Equipment Display**: See currently equipped items with stats
- **Detailed Inventory**: Items grouped by category with quantities
- **Quick Keys**: Single-key commands (A=attack, D=defend, I=inventory, E=equipment)
- **Boxed UI Elements**: Clean bordered displays for stats, combat, and shops

### AI Improvements
- **Aidungeon-Style Prompts**: Immersive second-person narrative
- **Better Context Memory**: AI remembers story events, location, NPCs, and quests
- **Combat Narration**: Cinematic combat descriptions
- **Smart Choice Generation**: Context-aware default choices

### Auto-Update
- **Automatic Update Check**: Notified of new versions on startup
- **One-Command Update**: `trpg update` installs the latest version
- **Automatic Backup**: Saves backup before updating
- **Rollback Support**: Automatic rollback on failure

## Requirements

- **Python 3.8 or higher** (https://www.python.org/downloads/)
- **Cerebras AI API Key** (free at https://cloud.cerebras.ai/)

## Installation

### One-Command Install (Recommended)

**macOS / Linux:**
```bash
sudo python3 install_universal.py
```

**Windows (Run as Administrator):**
```bash
python install_universal.py
```

That's it! The installer will:
- ✓ Install all dependencies automatically
- ✓ Configure PATH (no manual setup needed)
- ✓ Create the `trpg` command
- ✓ Work on any drive (C:, D:, etc.)
- ✓ Create desktop shortcut (optional)

### Alternative Installation

If you prefer the traditional method:

```bash
# Clone the repository
git clone https://github.com/joy-arz/ai-terminal-rpg.git
cd ai-terminal-rpg

# Run platform-specific installer
./install.sh          # macOS/Linux
install.bat           # Windows
install_windows.ps1   # Windows PowerShell
```

### What Gets Installed

| Component | Location |
|-----------|----------|
| Game Package | Python site-packages |
| trpg Command | Python scripts directory |
| Save Files | `~/.trpg_saves/` |
| API Key | `~/.trpg.env` |
| Desktop Shortcut | Your desktop (optional) |

### After Installation

**macOS/Linux:**
```bash
# Restart terminal or run:
source ~/.bashrc  # or source ~/.zshrc

# Play from anywhere:
trpg
```

**Windows:**
```cmd
:: Close and open a new Command Prompt
:: Play from anywhere:
trpg
```

### Manual Installation (Advanced)

```bash
# Clone and install manually
git clone https://github.com/joy-arz/ai-terminal-rpg.git
cd ai-terminal-rpg

# Install dependencies
python -m pip install openai python-dotenv colorama

# Run the game
python -m trpg
```

## Running the Game

After installation, the `trpg` command works from anywhere:

```bash
trpg
```

On first run, you'll be prompted to enter your Cerebras AI API key.
Get one from: https://cloud.cerebras.ai/

### Alternative Launch Methods

```bash
# Python module (always works, no PATH needed)
python -m trpg

# With specific commands
trpg help      # Show help
trpg version   # Show version
trpg update    # Update the game
```

### Desktop Shortcut

The installer can create a desktop shortcut for easy access:
- **Windows**: `AI Terminal RPG.bat` on your desktop
- **macOS/Linux**: `AI Terminal RPG.sh` on your desktop

Just double-click to launch the game!

## Game Commands

### General Commands (Available Anytime)
| Key | Command | Description |
|-----|---------|-------------|
| `I` | `inventory` | View your items with categories |
| `E` | `equipment` | View/change equipped items |
| `S` | `stats` | View full character stats |
| `H` | `help` | Show available commands |
| `Q` | `quit` | Save and exit the game |
| - | `save` | Manual save (auto-save enabled) |
| - | `load` | Load from different save slot |

### Story Commands
- Enter a number (1-3) to make a choice
- Commands work during story (I, E, S, H, Q)

### Combat Commands
| Key | Command | Description |
|-----|---------|-------------|
| `A` | `attack` | Attack the enemy |
| `D` | `defend` | Reduce damage taken by 50% |
| `U` | `use <item>` | Use an item (e.g., `use potion`) |
| `R` | `run` | Attempt to flee from combat |

### Shop Commands
| Key | Command | Description |
|-----|---------|-------------|
| `B` | `buy` | Buy items from shop |
| `S` | `sell` | Sell items to shop |
| `L` | `leave` | Leave the shop |

## How It Works

### AI Story Generation (Aidungeon Style)

The game uses Cerebras AI's Llama 3.1-8B model to generate story content. Each turn:

1. The AI receives context including:
   - Previous story history (last 5 scenes)
   - Current player stats, equipment, and inventory
   - Status effects and location
   - The player's last choice/action

2. The AI generates:
   - An immersive story scene (80-150 words)
   - Exactly 3 numbered choices for the player

3. The player selects a choice, and the cycle continues

### Encounter System

Encounters are triggered through a consistent system:
- **Explicit Triggers**: AI narrative mentions combat keywords
- **Random Encounters**: 25% base chance after 3+ turns
- **Location Modifiers**: Dangerous areas increase chance
- **Minimum Interval**: At least 3 turns between random encounters

### Combat System

Combat is turn-based with enhanced mechanics:

- **Damage Formula**: `damage = (attack - defense) × variance(±20%)`
- **Critical Hits**: 10% chance for 1.5× damage
- **Defense**: Reduces incoming damage (50% reduction when defending)
- **Status Effects**: Poison, burn, stun, freeze, bleed, and buffs
- **Enemy Scaling**: Enemies scale with player level
- **Victory Rewards**: Gold, XP, and random item drops
- **Item Drops**: 30% + (5% × level) drop chance with rarity tiers

### Equipment System

Equipment provides permanent stat bonuses:

| Slot | Examples | Stats |
|------|----------|-------|
| Weapon | Iron Sword, Magic Staff | +Attack |
| Armor | Plate Armor, Magic Robe | +Defense |
| Accessory | Ring of Strength, Dragon Pendant | +Attack/+Defense |

Equip items with the `equipment` command → `equip` → enter item name.

### Leveling System

Gain XP from combat to level up:

- **XP Requirement**: Starts at 100, increases 1.5× per level
- **Stat Increases**: +5 HP, +2 Attack, +1 Defense per level
- **Full Heal**: HP restored on level up
- **Enemy Scaling**: Higher level = stronger enemies

### Save System

- **3 Save Slots**: Choose slot on game start
- **Auto-Save**: Saves after each turn
- **Manual Save**: Use `save` command
- **Backup System**: Automatic backup before overwriting
- **Metadata**: Playtime, location, level, HP status
- **Save Location**: `~/.trpg_saves/`

### Shop System

Visit shops to buy and sell items:

- **Shop Types**: General, Weapon, Armor, Magic, Black Market
- **Dynamic Inventory**: Stock scales with player level
- **Buy Prices**: Base value (with discounts at high reputation)
- **Sell Prices**: 50% of base value
- **Shop Gold**: Shops have limited gold for buying

## 📚 Indonesian Folklore Starting Points

The game features **10 unique starting points** based on Indonesian folklore and historical kingdoms. Each game randomly selects one, providing educational content about Indonesia's rich cultural heritage:

| # | Starting Point | Era | Description |
|---|----------------|-----|-------------|
| 1 | **Kerajaan Majapahit** | 1350 M | The glorious Majapahit Empire under Patih Gajah Mada and Prabu Hayam Wuruk |
| 2 | **Misteri Gunung Merapi** | 1400 M | Investigate mysterious green lights from the sacred volcano |
| 3 | **Hilangnya Pusaka Kerajaan** | 1550 M | Recover stolen sacred heirlooms of Pajajaran Kingdom |
| 4 | **Kutukan Ratu Pantai Selatan** | 1480 M | Face the curse of Nyai Roro Kidul, Queen of the Southern Sea |
| 5 | **Perang Bubat** | 1357 M | Experience the tragic battle between Majapahit and Pajajaran |
| 6 | **Kerajaan Sriwijaya** | 900 M | The ancient Buddhist maritime kingdom faces the Chola threat |
| 7 | **Asal Usul Roro Jonggrang** | 900 M | The legend of the thousand temples (Prambanan) |
| 8 | **Kerajaan Demak** | 1500 M | The rise of Islam in Java under Sunan Kalijaga |
| 9 | **Tragedi Tanjung Pura** | 1600 M | Investigate a kingdom's mysterious disappearance |
| 10 | **Pemberontakan Trunajaya** | 1675 M | The great rebellion against Mataram Sultanate |

### Mythological Creatures & Elements

Throughout your journey, you'll encounter:

- **Genderuwo** - Large, hairy supernatural beings
- **Tuyul** - Mischievous child-like spirits
- **Kuntilanak** - Ghosts of women who died during pregnancy
- **Nyai Roro Kidul** - The legendary Queen of the Southern Sea
- **Pocong** - Ghosts wrapped in burial shrouds
- **Jin and Demons** - Islamic mythological entities
- **Dukun** - Traditional shamans with mystical powers

### Historical Kingdoms Featured

- **Sriwijaya** (7th-14th century) - Buddhist maritime empire
- **Majapahit** (1293-1527) - Hindu-Buddhist golden age
- **Pajajaran** (932-1579) - Sunda Kingdom
- **Demak** (1475-1548) - First Islamic Sultanate in Java
- **Mataram** (1587-1755) - Islamic Javanese kingdom

## Example Gameplay

```
======================================================================
                         AI TERMINAL RPG
======================================================================

HP: [████████████████████] 20/20  XP: [██████████] 0/100  LVL: 1

  You stand at the edge of a dense forest. Ancient trees tower above,
  their leaves whispering secrets in the wind. A narrow path winds
  into the darkness, while to the north, you spot smoke rising from
  what might be a village.

  ┌─ Choices ─────────────────────────────────────────────────────┐
  │  1. Follow the narrow path into the forest                    │
  │  2. Head north toward the smoke                               │
  │  3. Search the forest edge for resources                      │
  └───────────────────────────────────────────────────────────────┘

  [I]nventory [E]quipment [S]tats [H]elp [Q]uit

Your choice: 1
```

## Project Structure

```
ai_terminal_rpg/
├── trpg/
│   ├── __init__.py       # Package initialization
│   ├── game.py           # Main game loop and controller
│   ├── player.py         # Player stats, equipment, inventory, XP
│   ├── combat.py         # Turn-based combat with status effects
│   ├── ai_engine.py      # Cerebras AI API integration
│   ├── save_system.py    # Multi-slot save/load functionality
│   ├── shop.py           # Shop system for buying/selling
│   ├── ui.py             # Terminal UI with colors and boxes
│   └── updater.py        # Auto-update functionality
├── tests/
│   └── test_game.py      # Comprehensive test suite (44 tests)
├── install.py            # Universal installer (all platforms)
├── install.sh            # Shell wrapper (macOS/Linux)
├── install.bat           # Batch wrapper (Windows)
├── requirements.txt      # Python dependencies
├── pyproject.toml        # Package configuration
└── README.md            # This file
```

## Item Database

### Weapons
- Rusty Sword (+2 ATK), Iron Sword (+5 ATK), Steel Sword (+8 ATK)
- Magic Sword (+12 ATK), Dragon Blade (+18 ATK)
- Wooden Staff (+3 ATK), Magic Staff (+10 ATK)
- Dagger (+4 ATK), Assassin Dagger (+9 ATK, +2 DEF)
- Battle Axe (+10 ATK, -1 DEF)

### Armor
- Cloth Armor (+2 DEF), Leather Armor (+4 DEF)
- Chain Mail (+7 DEF), Plate Armor (+10 DEF)
- Dragon Scale Armor (+15 DEF, +2 ATK)
- Robe (+3 DEF, +1 ATK), Magic Robe (+5 DEF, +3 ATK)

### Accessories
- Ring of Strength (+3 ATK), Ring of Protection (+3 DEF)
- Amulet of Power (+5 ATK, +2 DEF)
- Lucky Charm (+1 ATK, +1 DEF)
- Dragon Pendant (+7 ATK, +5 DEF)
- Boots of Speed (+2 ATK, +2 DEF)
- Helm of Wisdom (+2 ATK, +4 DEF)

### Consumables
- Health Potion (+15 HP), Greater Health Potion (+30 HP)
- Super Health Potion (+50 HP), Elixir (+100 HP, cure all)
- Antidote (cure poison), Food (+5 HP), Bread (+8 HP)

## Troubleshooting

### "trpg: command not found"

**Windows:**
```
1. Find Python Scripts path:
   python -c "import sysconfig; print(sysconfig.get_path('scripts'))"

2. Add this path to your system PATH:
   - Right-click "This PC" → Properties
   - Advanced system settings → Environment Variables
   - Add the path to the "Path" variable

3. Open a NEW Command Prompt and try: trpg
```

**macOS/Linux:**
```bash
# Add to your shell config
echo 'export PATH="$(python3 -m site --user-base)/bin:$PATH"' >> ~/.bashrc
source ~/.bashrc

# Or use the Python module directly:
python3 -m trpg
```

### "No API key found"

1. Get your API key from: https://cloud.cerebras.ai/
2. On first run, enter your API key when prompted
3. The key is saved to `~/.trpg.env` or `.env`

### "Module not found"

```bash
# Install dependencies manually
cd ai-terminal-rpg
python -m pip install openai python-dotenv colorama
```

### "Permission denied" (Linux/macOS)

```bash
# Run installer with sudo
sudo ./install.sh

# Or install for current user only
python3 -m pip install --user -e .
```

### Game won't start

Try the Python module directly:
```bash
python -m trpg
```

## Testing

Run the comprehensive test suite:

```bash
cd ai-terminal-rpg
python tests/test_game.py
```

All 44 tests should pass, covering:
- Player stats, equipment, inventory, leveling
- Combat mechanics and rewards
- Shop buying/selling
- Save/load functionality
- UI utilities
- Integration tests

## Version History

### 2.1.0 (Current)
- Universal installer for Windows, Mac, Linux
- Automatic PATH configuration
- Desktop shortcut creation
- No manual pip install required
- Simplified installation process

### 2.0.0
- Added equipment system (weapon, armor, accessory)
- Added XP and leveling system
- Added status effects (buffs and debuffs)
- Added shop system with 5 shop types
- Added multiple save slots (3 slots)
- Improved encounter system (consistent triggering)
- Aidungeon-style narrative prompts
- Enhanced UI with visual bars and boxed elements
- Quick keys for all actions
- 40+ item database
- Comprehensive test suite (44 tests)

### 1.0.0
- Initial release
- Basic combat system
- Simple inventory
- Single save file
- AI story generation

## License

MIT License - Feel free to modify and distribute.

## Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Run tests: `python tests/test_game.py`
4. Submit a pull request

## Acknowledgments

- Inspired by Aidungeon's immersive narrative style
- Built with Cerebras AI's fast Llama models
- Terminal UI inspired by classic text adventures

## Support

For issues, questions, or suggestions:
- GitHub Issues: https://github.com/joy-arz/ai-terminal-rpg/issues
- Documentation: See README.md in the repository
