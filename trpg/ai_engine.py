"""
AI Engine module - handles Cerebras AI API integration for story generation.

This module manages communication with Cerebras AI's Llama model to:
- Generate story scenes dynamically in Aidungeon style
- Create player choices based on context
- Maintain story consistency through context passing
- Handle combat narration
- Support shop interactions

The AI prompt system works by sending structured context each turn:
1. System prompt defining the AI's role as dungeon master (Aidungeon style)
2. Story history for continuity
3. Current player state (stats, inventory, equipment)
4. Player's last choice/action
"""

import os
import re
import sys
from typing import Optional, Tuple, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()


def setup_api_key():
    """Prompt user for API key if not set."""
    api_key = os.getenv("CEREBRAS_API_KEY")

    if not api_key or api_key.strip() == "":
        print("\n=== AI TERMINAL RPG ===")
        print("No API key found in .env file")
        print("\nGet your API key from: https://cloud.cerebras.ai/")
        api_key = input("\nEnter your Cerebras API key: ").strip()

        if api_key:
            # Save to home directory for persistence
            home_env = os.path.expanduser("~/.trpg.env")
            with open(home_env, "w") as f:
                f.write(f"CEREBRAS_API_KEY={api_key}\n")
            
            # Also save to current directory
            current_env = ".env"
            with open(current_env, "w") as f:
                f.write(f"CEREBRAS_API_KEY={api_key}\n")
            
            print("API key saved!")
            os.environ["CEREBRAS_API_KEY"] = api_key
            return api_key
        else:
            print("API key required to play")
            sys.exit(1)

    return api_key


try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install -r requirements.txt")
    raise


class AIEngine:
    """
    Handles AI story generation using Cerebras AI's Llama model.
    
    The engine maintains conversation history to ensure story consistency
    and generates both narrative content and player choices.
    
    Style: Aidungeon-inspired immersive second-person narrative
    """
    
    CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1"
    MODEL_NAME = "llama3.1-8b"
    MAX_WORDS = 150
    
    SYSTEM_PROMPT = """Kamu adalah seorang dalang yang menceritakan petualangan epik dalam bahasa Indonesia.

PANDUAN GAYA:
- Tulis dalam BAHASA INDONESIA yang baik
- Gunakan sudut pandang ORANG KEDUA ("Kau berjalan...", "Kau melihat...")
- Deskriptif dan IMERSIF - libatkan semua panca indera
- Gunakan WAKTU SEKARANG untuk immediasi
- Setiap respons 80-150 kata narasi yang kaya
- Berikan TEPAT 3 pilihan bernomor

FORMAT PILIHAN (harus tepat 3):
Choices:
1. [Opsi aksi spesifik]
2. [Opsi pendekatan berbeda]
3. [Opsi jalur alternatif]

ELEMEN CERITA:
- Detail lingkungan yang hidup (pemandangan, suara, bau)
- Dialog NPC bila relevan (dalam tanda kutip)
- Konsekuensi bermakna untuk aksi pemain
- Gunakan makhluk mitologi Nusantara (genderuwo, tuyul, kuntilanak, dll)
- Gunakan nama-nama Indonesia untuk karakter dan tempat

LATAR:
- Kerajaan-kerajaan Nusantara (Majapahit, Sriwijaya, Pajajaran, dll)
- Budaya Indonesia (makanan, pakaian, adat)
- Peristiwa sejarah Indonesia bila relevan

PENTING: Jangan kontrol aksi pemain. Hanya deskripsikan apa yang terjadi."""

    def __init__(self):
        """Initialize the AI engine with Cerebras AI client."""
        api_key = setup_api_key()
        
        self.client = OpenAI(api_key=api_key, base_url=self.CEREBRAS_BASE_URL)
        self.conversation_history: List[dict] = []
        self.story_history: List[str] = []
        self.location = "unknown"
        self.npcs_met: List[str] = []
        self.quests_active: List[str] = []
    
    def reset(self) -> None:
        """Reset conversation and story history for a new game."""
        self.conversation_history = []
        self.story_history = []
        self.location = "unknown"
        self.npcs_met = []
        self.quests_active = []
    
    def _build_prompt(
        self,
        player_context: str,
        player_choice: Optional[str] = None,
        combat_context: Optional[str] = None,
        shop_context: Optional[Dict[str, Any]] = None,
        force_encounter: bool = False
    ) -> str:
        """
        Build the user prompt with all necessary context.
        
        This is the core of the AI memory system - each turn we send:
        - Previous story summary for continuity
        - Current player state (stats, inventory, equipment)
        - The player's last choice/action
        - Combat context if in battle
        - Shop context if shopping
        
        Args:
            player_context: Formatted string of player stats and inventory
            player_choice: The player's last choice (None for first turn)
            combat_context: Optional combat situation description
            shop_context: Optional shop information
            force_encounter: Force an enemy encounter
            
        Returns:
            str: Complete prompt with all context
        """
        recent_history = self.story_history[-5:] if self.story_history else []
        
        prompt_parts = []
        
        if recent_history:
            prompt_parts.append("STORY SO FAR:")
            for i, scene in enumerate(recent_history, 1):
                prompt_parts.append(f"  {i}. {scene}")
            prompt_parts.append("")
        
        prompt_parts.append("CURRENT STATE:")
        prompt_parts.append(f"  {player_context}")
        prompt_parts.append("")
        
        prompt_parts.append(f"LOCATION: {self.location}")
        if self.npcs_met:
            prompt_parts.append(f"NPCs KNOWN: {', '.join(self.npcs_met)}")
        if self.quests_active:
            prompt_parts.append(f"ACTIVE QUESTS: {', '.join(self.quests_active)}")
        prompt_parts.append("")
        
        if combat_context:
            prompt_parts.append(f"COMBAT: {combat_context}")
            prompt_parts.append("Describe this combat action cinematically.")
            prompt_parts.append("")
        
        if shop_context:
            prompt_parts.append(f"SHOP: {shop_context.get('name', 'Unknown Shop')}")
            prompt_parts.append(f"Shop has: {', '.join(shop_context.get('items', [])[:5])}")
            prompt_parts.append("The shopkeeper waits for your business.")
            prompt_parts.append("")
        
        if force_encounter:
            prompt_parts.append("ENCOUNTER: An enemy appears! Describe the encounter dramatically.")
            prompt_parts.append("Include the enemy's appearance and aggressive intent.")
            prompt_parts.append("")
        
        if player_choice:
            prompt_parts.append(f"YOU CHOOSE: {player_choice}")
            prompt_parts.append("")
            prompt_parts.append("Continue the story based on this choice. Describe what happens next.")
            prompt_parts.append("Include consequences, sensory details, and new developments.")
        else:
            prompt_parts.append("BEGIN ADVENTURE:")
            prompt_parts.append("Start the fantasy adventure. Introduce the player to the world.")
            prompt_parts.append("Describe their surroundings vividly and present 3 initial choices.")
            prompt_parts.append("Make the opening engaging and atmospheric.")
        
        return "\n".join(prompt_parts)
    
    def _parse_response(self, response_text: str) -> Tuple[str, List[str]]:
        """
        Parse AI response to extract scene and choices.
        
        The AI should return formatted text with a story scene followed
        by exactly 3 numbered choices. This method extracts both parts.
        
        Args:
            response_text: Raw response from AI
            
        Returns:
            Tuple of (scene_text, list_of_3_choices)
            
        Raises:
            ValueError: If response cannot be parsed properly
        """
        choices_pattern = r"(?:Choices:|CHOICES:|choices:|What do you do:|Options:)\s*\n\s*(\d+[\.:]\s*.+?)\s*\n\s*(\d+[\.:]\s*.+?)\s*\n\s*(\d+[\.:]\s*.+?)(?:\n|$)"
        match = re.search(choices_pattern, response_text, re.IGNORECASE | re.DOTALL)
        
        if match:
            scene = response_text[:match.start()].strip()
            
            choices = []
            for i in range(1, 4):
                choice_text = match.group(i).strip()
                choice_text = re.sub(r'^\d+[\.:]\s*', '', choice_text).strip()
                choices.append(choice_text)
            
            return scene, choices
        
        simple_pattern = r'(\d+[\.:])\s*(.+?)(?=\n\d+[\.:]|$)'
        all_numbered = re.findall(simple_pattern, response_text, re.IGNORECASE | re.DOTALL)
        
        if len(all_numbered) >= 3:
            choices = [text.strip() for _, text in all_numbered[-3:]]
            
            first_choice_text = all_numbered[-3][1].strip()
            first_choice_match = re.search(
                rf'\d+[\.:]\s*{re.escape(first_choice_text)}',
                response_text
            )
            
            if first_choice_match:
                scene = response_text[:first_choice_match.start()].strip()
            else:
                scene = response_text.split('\n')[0]
            
            return scene, choices
        
        scene = response_text.strip()
        
        scene_lower = scene.lower()
        
        if any(word in scene_lower for word in ["enemy", "monster", "attack", "fight", "danger", "hostile"]):
            default_choices = [
                "Prepare for combat and assess the threat",
                "Look for an escape route",
                "Call out to see if it's friendly"
            ]
        elif any(word in scene_lower for word in ["shop", "store", "merchant", "buy", "sell", "gold"]):
            default_choices = [
                "Browse the available items",
                "Ask the shopkeeper about rumors",
                "Leave the shop"
            ]
        elif any(word in scene_lower for word in ["village", "town", "city", "people", "inn", "tavern"]):
            default_choices = [
                "Explore the area and observe",
                "Talk to the locals for information",
                "Find the inn or tavern"
            ]
        elif any(word in scene_lower for word in ["forest", "woods", "trees", "wilderness", "path", "road"]):
            default_choices = [
                "Continue along the path",
                "Search the surroundings for resources",
                "Listen for sounds of danger or civilization"
            ]
        elif any(word in scene_lower for word in ["dungeon", "cave", "ruins", "ancient", "treasure"]):
            default_choices = [
                "Proceed cautiously deeper",
                "Search for traps or hidden dangers",
                "Listen for sounds of movement"
            ]
        else:
            default_choices = [
                "Investigate your surroundings",
                "Continue forward cautiously",
                "Look for resources or points of interest"
            ]
        
        return scene, default_choices
    
    def generate_scene(
        self,
        player_context: str,
        player_choice: Optional[str] = None,
        combat_context: Optional[str] = None,
        shop_context: Optional[Dict[str, Any]] = None,
        force_encounter: bool = False
    ) -> Tuple[str, List[str]]:
        """
        Generate a new story scene from the AI.
        
        This is the main method called each game turn. It:
        1. Builds a prompt with full context (history, stats, choice)
        2. Sends to OpenAI API
        3. Parses the response to extract scene and choices
        4. Stores the scene in history for future context
        
        Args:
            player_context: Formatted player stats and inventory string
            player_choice: Player's last choice (None for game start)
            combat_context: Optional combat situation description
            shop_context: Optional shop information
            force_encounter: Force an enemy encounter
            
        Returns:
            Tuple of (scene_text, list_of_3_choices)
        """
        prompt = self._build_prompt(
            player_context,
            player_choice,
            combat_context,
            shop_context,
            force_encounter
        )
        
        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=messages,
                max_tokens=600,
                temperature=0.85,
                top_p=0.9,
            )
            
            response_text = response.choices[0].message.content
            
            scene, choices = self._parse_response(response_text)
            
            # Store scene in history
            self.story_history.append(scene)
            
            self._extract_location(scene)
            
            return scene, choices
            
        except Exception as e:
            error_scene = f"The world seems to flicker around you as reality shifts. An error occurred: {str(e)}"
            default_choices = [
                "Try to stabilize your surroundings",
                "Close your eyes and focus",
                "Call out for help"
            ]
            return error_scene, default_choices
    
    def _extract_location(self, scene: str) -> None:
        """Try to extract current location from scene text."""
        location_keywords = {
            "forest": ["forest", "woods", "trees", "grove", "clearing"],
            "village": ["village", "town", "city", "settlement", "hamlet"],
            "dungeon": ["dungeon", "cave", "cavern", "tunnel", "underground"],
            "castle": ["castle", "palace", "fortress", "keep", "tower"],
            "inn": ["inn", "tavern", "pub", "alehouse"],
            "shop": ["shop", "store", "market", "bazaar"],
            "ruins": ["ruins", "ancient", "crumbling", "old temple"],
            "mountain": ["mountain", "peak", "cliff", "hillside"],
            "river": ["river", "stream", "lake", "water", "shore"],
        }
        
        scene_lower = scene.lower()
        for location, keywords in location_keywords.items():
            if any(kw in scene_lower for kw in keywords):
                self.location = location
                return
    
    def generate_combat_narration(
        self,
        player_context: str,
        player_action: str,
        combat_state: dict
    ) -> str:
        """
        Generate AI narration for combat situations.
        
        During combat, we need shorter, action-focused responses that
        describe the outcome of player actions and enemy reactions.
        
        Args:
            player_context: Player stats and inventory
            player_action: The action player took (attack, defend, etc.)
            combat_state: Dictionary with enemy info and combat status
            
        Returns:
            str: Description of combat outcome
        """
        enemy_name = combat_state.get("enemy_name", "enemy")
        enemy_hp = combat_state.get("enemy_hp", 0)
        player_hp = combat_state.get("player_hp", 0)
        enemy_max_hp = combat_state.get("enemy_max_hp", 1)
        
        hp_percent = enemy_hp / max(1, enemy_max_hp)
        
        if hp_percent > 0.7:
            enemy_state = "fresh and eager for battle"
        elif hp_percent > 0.4:
            enemy_state = "wounded but still dangerous"
        elif hp_percent > 0.2:
            enemy_state = "badly wounded and desperate"
        else:
            enemy_state = "barely standing, near defeat"
        
        prompt = f"""Combat narration request:

Enemy: {enemy_name} ({enemy_hp} HP) - {enemy_state}
You: {player_hp} HP
{player_context}

Your action: {player_action}

Write 2-3 exciting sentences describing:
- The immediate result of your action
- The enemy's reaction
- The current tension of battle

Make it visceral and cinematic. Use second person."""
        
        try:
            messages = [
                {"role": "system", "content": "You are narrating exciting combat in second person. Be visceral and cinematic."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=messages,
                max_tokens=150,
                temperature=0.7,
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Combat continues! The {enemy_name} glares at you menacingly."
    
    def generate_encounter(
        self,
        player_context: str,
        location: str = "unknown"
    ) -> Tuple[str, str]:
        """
        Generate an enemy encounter description.
        
        Args:
            player_context: Player stats and context
            location: Current location
            
        Returns:
            Tuple of (encounter_description, enemy_name_hint)
        """
        prompt = f"""Generate an enemy encounter.

Location: {location}
{player_context}

Describe:
1. How the enemy appears (suddenly, from shadows, charging, etc.)
2. What the enemy looks like (detailed appearance)
3. The enemy's aggressive intent

Keep it under 80 words. End with the enemy ready to fight.
Also tell me the enemy type (goblin, bandit, wolf, etc.) at the end."""
        
        try:
            messages = [
                {"role": "system", "content": "You create exciting enemy encounters. Be descriptive but concise."},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.MODEL_NAME,
                messages=messages,
                max_tokens=200,
                temperature=0.8,
            )
            
            text = response.choices[0].message.content.strip()
            
            # Try to extract enemy type
            enemy_hint = "enemy"
            enemy_types = ["goblin", "bandit", "wolf", "skeleton", "orc", "mage", 
                          "spider", "troll", "rat", "ogre", "wraith", "dragon"]
            
            text_lower = text.lower()
            for enemy_type in enemy_types:
                if enemy_type in text_lower:
                    enemy_hint = enemy_type
                    break
            
            return text, enemy_hint
            
        except Exception as e:
            return f"A hostile creature appears before you! (Error: {e})", "enemy"
    
    def get_story_summary(self) -> str:
        """Get a summary of the story so far."""
        if not self.story_history:
            return "Your adventure begins..."
        return "\n\n".join(self.story_history[-10:])  # Last 10 scenes
    
    def to_dict(self) -> dict:
        """Convert AI engine state to dictionary for saving."""
        return {
            "story_history": self.story_history.copy(),
            "location": self.location,
            "npcs_met": self.npcs_met.copy(),
            "quests_active": self.quests_active.copy()
        }
    
    def from_dict(self, data: dict) -> None:
        """Load AI engine state from saved data."""
        self.story_history = data.get("story_history", [])
        self.location = data.get("location", "unknown")
        self.npcs_met = data.get("npcs_met", [])
        self.quests_active = data.get("quests_active", [])
