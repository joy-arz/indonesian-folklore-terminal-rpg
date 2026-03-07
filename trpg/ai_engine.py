
import os
import re
import sys
import time
import logging
from typing import Optional, Tuple, List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

log_file = os.path.join(os.path.expanduser("~"), ".trpg.log")
try:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )
except PermissionError:
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
logger = logging.getLogger('AIEngine')

CEREBRAS_BASE_URL = "https://api.cerebras.ai/v1"
MODEL_NAME = "llama3.1-8b"


def validate_api_key(api_key: str) -> bool:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=CEREBRAS_BASE_URL)
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5
        )
        return response is not None
    except Exception as e:
        error_msg = str(e).lower()
        if "authentication" in error_msg or "api key" in error_msg or "unauthorized" in error_msg or "invalid" in error_msg:
            return False
        return True


def setup_api_key(max_retries: int = 3) -> str:
    api_key = os.getenv("CEREBRAS_API_KEY")
    
    if api_key and api_key.strip():
        print("\n=== AI TERMINAL RPG ===")
        print("Validating saved API key...")
        if validate_api_key(api_key):
            print("API key validated successfully!")
            return api_key
        else:
            print("Saved API key is invalid or expired.")
    
    print("\n=== AI TERMINAL RPG ===")
    print("API Key Setup Required")
    print("\nGet your FREE API key from: https://cloud.cerebras.ai/")
    print("(No credit card required)\n")
    
    for attempt in range(1, max_retries + 1):
        print(f"Attempt {attempt} of {max_retries}")
        api_key = input("Enter your Cerebras API key: ").strip()

        if not api_key:
            print("API key cannot be empty.\n")
            continue

        print("Validating API key...")
        if validate_api_key(api_key):
            home_env = os.path.expanduser("~/.trpg.env")
            with open(home_env, "w") as f:
                f.write(f"CEREBRAS_API_KEY={api_key}\n")

            current_env = ".env"
            with open(current_env, "w") as f:
                f.write(f"CEREBRAS_API_KEY={api_key}\n")

            print("\n✓ API key saved successfully!")
            print(f"  Saved to: {home_env}")
            print(f"  Saved to: {current_env}\n")
            
            os.environ["CEREBRAS_API_KEY"] = api_key
            return api_key
        else:
            print("\n✗ Invalid API key. Please check and try again.\n")
            print("Make sure you copied the entire key from https://cloud.cerebras.ai/\n")
    
    print("\n" + "=" * 60)
    print("ERROR: Unable to validate API key after", max_retries, "attempts")
    print("=" * 60)
    print("\nPlease:")
    print("1. Visit https://cloud.cerebras.ai/")
    print("2. Sign up for a free account (no credit card required)")
    print("3. Copy your API key from the dashboard")
    print("4. Run the game again and paste the key\n")
    print("Or contact support if you continue to have issues.\n")
    sys.exit(1)


try:
    from openai import OpenAI
except ImportError:
    print("Error: openai package not installed. Run: pip install -r requirements.txt")
    raise


class AIEngine:

    MAX_WORDS = 150

    SYSTEM_PROMPT = """You are a dalang (traditional Indonesian storyteller) narrating an epic educational adventure set in Indonesian folklore and history.

PRIMARY GOAL: Educate players about Indonesian kingdoms, history, and culture through immersive storytelling.

LANGUAGE: Write in ENGLISH so international audiences can learn about Indonesian culture.

================================================================================
MANDATORY OUTPUT FORMAT (MUST FOLLOW EXACTLY):
================================================================================

1. NARRATIVE SECTION (80-150 words):
   - Start with: "Year [XXX] CE. [Location description]..."
   - Use SECOND PERSON: "You walk...", "You see...", "You hear..."
   - Use PRESENT TENSE for immediacy
   - Engage 2-3 senses (sight, sound, smell, touch)
   - Include 1-2 educational facts naturally woven in

2. CHOICES SECTION (EXACTLY 3 choices):
   Choices:
   1. [Specific action related to the scene]
   2. [Different approach or exploration option]
   3. [Alternative path or social interaction]

CHOICE RULES:
- Each choice must be ONE sentence ONLY (10-25 words)
- NO markdown formatting (no **, *, _, etc.)
- NO extra descriptions after the choice
- NO periods after the choice number, just the text
- Keep choices concise and actionable
- Example GOOD: "Follow the stream through the forest to find a clearing"
- Example BAD: "**Follow the stream**, which winds its way through the forest, leading you to a tranquil clearing surrounded by towering trees. You hear the gentle lapping of water against the shore, and the air is filled with the sweet scent of lotus flowers."

================================================================================
KINGDOM-SPECIFIC REQUIREMENTS:
================================================================================

When the player is in MAJAPAHIT (East Java, 1293-1527):
- Mention: Red brick temples, alun-alun (royal square), pendopo pavilions
- Include: Javanese court culture, gamelan music, wayang kulit shadows
- Reference: Gajah Mada, Prabu Hayam Wuruk, Sumpah Palapa oath
- Terms to use: prajurit (soldier), keris (dagger), batik (fabric)
- Religion: Hindu-Buddhist syncretism (Siwa-Buddha)

When the player is in SRIWIJAYA (South Sumatra, 7th-14th century):
- Mention: Bustling port, ships from China/India, Buddhist stupas
- Include: Maritime trade, multicultural merchants, Buddhist learning
- Reference: Strait of Malacca, Nalanda University connection
- Terms to use: bandar (port), vihara (monastery), nakhoda (ship captain)
- Religion: Mahayana Buddhism

When the player is in PAJAJARAN/SUNDA (West Java, 932-1579):
- Mention: Rice terraces, wooden palaces, Mount Salak backdrop
- Include: Sundanese culture, agricultural traditions, pusaka (heirlooms)
- Reference: Prabu Siliwangi (legendary king with supernatural powers)
- Terms to use: leuit (rice barn), saung (pavilion), kokosan (village)
- Religion: Sunda Wiwitan (ancestral beliefs)

When the player is in DEMAK (North Coast Java, 1475-1548):
- Mention: Great Mosque with tatal roof, Islamic trading posts
- Include: Wali Songo (nine saints), Islamic-Javanese synthesis
- Reference: Sunan Kalijaga (used wayang for dakwah), Raden Patah
- Terms to use: masjid (mosque), santri (student), dakwah (preaching)
- Religion: Islam (Sunni with Javanese traditions)

When the player is in MATARAM ISLAM (Central Java, 1587-1755):
- Mention: Kotagede palace, Javanese-Islamic court ceremonies
- Include: Sultan's court, gamelan sekaten, bedhaya dance
- Reference: Sultan Agung (attacked Dutch Batavia), Amangkurat
- Terms to use: kraton (palace), bupati (regent), abdi dalem (courtier)
- Religion: Islam with Kejawen (Javanese mysticism)

When the player is in TANJUNG PURA (Kalimantan, 14th-17th century):
- Mention: River settlements, stilt houses, diamond/gold trade
- Include: Malay-Dayak culture synthesis, tropical rainforest
- Reference: Mysterious disappearance (historical mystery)
- Terms to use: sungai (river), rumah panjang (longhouse), mandau (sword)
- Religion: Blend of Islam and Dayak animism

================================================================================
MYTHOLOGICAL CREATURES (use appropriately for encounters):
================================================================================

Common (Level 1-3):
- Tuyul: Small child spirit, steals money, mischievous
- Pocong: Ghost wrapped in white burial shroud, hops slowly
- Genderuwo: Large hairy giant, lives in forests, protective

Uncommon (Level 4-6):
- Kuntilanak: Female ghost, long hair, white dress, tragic past
- Leak: Balinese witch, transforms into animals, dark magic
- Harimau Jadi-jadian: Shapeshifting tiger, Sumatran origin
- Ahool: Giant bat, 3m wingspan, lives near waterfalls

Rare (Level 7-9):
- Orang Bati: Winged humanoid, ape-like, from Maluku
- Kuyang: Disembodied head with organs, blood-sucker, Kalimantan
- Nyi Blorong: Mermaid goddess, half-woman half-snake, wealthy

Boss (Level 10+):
- Naga Besukih: Sacred dragon under Mount Agung, Bali
- Garuda Sakti: Sacred bird king, golden feathers, blocks the sun
- Iblis Laut Selatan: Sea demon, serves Nyai Roro Kidul

================================================================================
CHOICE QUALITY REQUIREMENTS:
================================================================================

Each choice must:
1. Be specific and actionable (not vague)
2. Reflect the historical/cultural context
3. Lead to meaningfully different outcomes
4. Use Indonesian terms when appropriate

GOOD EXAMPLES:
✓ "Enter the pendopo pavilion and greet Patih Gajah Mada with a sembah bow"
✓ "Explore the bandar (port) and speak with Gujarati textile merchants"
✓ "Visit the vihara to receive blessings from Buddhist monks"

BAD EXAMPLES:
✗ "Go inside" (too vague)
✗ "Talk to someone" (not specific)
✗ "Look around" (passive, not engaging)

================================================================================
EDUCATIONAL INTEGRATION RULES:
================================================================================

1. NEVER lecture - weave facts into narrative naturally
2. Use Indonesian terms with English explanations in parentheses
3. Reference real historical events and figures accurately
4. Show cultural practices through action, not description
5. Include architectural and geographical details

EXAMPLE (Good Educational Integration):
"The gamelan orchestra plays a slendro scale as you approach the pendopo.
A Javanese courtier explains that the five-tone scale represents the five
elements: earth, water, fire, air, and ether. This is the same music that
was played during Gajah Mada's campaigns to unite the archipelago."

================================================================================
STRICT PROHIBITIONS:
================================================================================

- Do NOT use modern technology or concepts (cars, phones, computers)
- Do NOT break the fourth wall or reference the game itself
- Do NOT control the player's actions or decisions
- Do NOT create choices that are obviously "right" or "wrong"
- Do NOT use anachronistic language or slang
- Do NOT mix kingdoms' cultural elements incorrectly

================================================================================
RESPONSE VALIDATION (Self-Check Before Output):
================================================================================

Before finalizing your response, verify:
□ Exactly 3 choices provided
□ Each choice is 10-25 words
□ Narrative is 80-150 words
□ At least 1 Indonesian term used correctly
□ At least 1 educational fact included
□ Second person POV maintained throughout
□ Present tense used consistently
□ Kingdom-specific details are accurate
"""

    def __init__(self):
        api_key = setup_api_key()

        self.client = OpenAI(api_key=api_key, base_url=CEREBRAS_BASE_URL)
        self.conversation_history: List[dict] = []
        self.story_history: List[str] = []
        self.location = "unknown"
        self.npcs_met: List[str] = []
        self.quests_active: List[str] = []
        self.history_summaries: List[Dict[str, Any]] = []
        self.summary_interval = 10
        self.reference_interval = 50
        self._response_cache: Dict[str, str] = {}
        logger.info("AIEngine initialized")

    def reset(self) -> None:
        self.conversation_history = []
        self.story_history = []
        self.location = "unknown"
        self.npcs_met = []
        self.quests_active = []
        self.history_summaries = []
        self._response_cache = {}
        logger.info("AIEngine reset")

    def _call_with_retry(self, messages: List[dict], max_retries: int = 3) -> str:
        for attempt in range(max_retries):
            try:
                logger.debug(f"API call attempt {attempt + 1}/{max_retries}")
                response = self.client.chat.completions.create(
                    model=MODEL_NAME,
                    messages=messages,
                    max_tokens=600,
                    temperature=0.85,
                    top_p=0.9,
                )
                logger.info(f"API call successful on attempt {attempt + 1}")
                return response.choices[0].message.content

            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt == max_retries - 1:
                    logger.error(f"API call failed after {max_retries} attempts")
                    raise
                
                wait_time = 2 ** attempt
                logger.info(f"Retrying in {wait_time} seconds...")
                time.sleep(wait_time)
        
        raise Exception("API call failed after all retries")

    def _should_reference_summary(self) -> bool:
        """Check if we should reference history summaries."""
        return len(self.story_history) > 0 and len(self.story_history) % self.reference_interval == 0

    def _create_summary(self) -> str:
        """Create a summary of recent story history."""
        if not self.story_history:
            return ""
        
        recent_scenes = self.story_history[-10:] if len(self.story_history) >= 10 else self.story_history
        summary_text = "\n\n".join(recent_scenes)[:2000]
        
        self.history_summaries.append({
            "turn": len(self.story_history),
            "summary": summary_text[:500]
        })
        
        logger.info(f"Created history summary at turn {len(self.story_history)}")
        return summary_text

    def _get_summary_context(self) -> str:
        """Get context from history summaries for AI reference."""
        if not self.history_summaries:
            return ""
        
        recent_summaries = self.history_summaries[-3:]
        context_parts = []
        for i, summary in enumerate(recent_summaries, 1):
            context_parts.append(f"Summary {i} (turn {summary['turn']}): {summary['summary'][:200]}...")
        
        return "\n".join(context_parts)

    def _build_prompt(
        self,
        player_context: str,
        player_choice: Optional[str] = None,
        combat_context: Optional[str] = None,
        shop_context: Optional[Dict[str, Any]] = None,
        force_encounter: bool = False,
        is_ending_phase: bool = False,
        turns_remaining: int = 0
    ) -> str:
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

        if is_ending_phase:
            if turns_remaining > 40:
                prompt_parts.append(f"⚠️  ENDING PHASE (Early): {turns_remaining} turns remain.")
                prompt_parts.append("Subtly hint at approaching destiny or fate.")
                prompt_parts.append("Mention prophecies, omens, or whispers of change in the air.")
                prompt_parts.append("NPCs may speak of 'the end of an era' or 'destiny approaching'.")
                prompt_parts.append("")
            elif turns_remaining > 20:
                prompt_parts.append(f"⚠️  ENDING PHASE (Building): {turns_remaining} turns remain.")
                prompt_parts.append("Build narrative tension toward the conclusion.")
                prompt_parts.append("Unresolved plot threads should start converging.")
                prompt_parts.append("The world feels different - change is coming.")
                prompt_parts.append("")
            elif turns_remaining > 5:
                prompt_parts.append(f"⚠️  ENDING PHASE (Climax): {turns_remaining} turns remain.")
                prompt_parts.append("The climax approaches - major events unfold.")
                prompt_parts.append("Player's past choices echo in present events.")
                prompt_parts.append("Final challenges or revelations emerge.")
                prompt_parts.append("")
            else:
                prompt_parts.append(f"⚠️  ENDING PHASE (Final): {turns_remaining} turns remain.")
                prompt_parts.append("The story reaches its natural conclusion.")
                prompt_parts.append("All threads converge toward destiny.")
                prompt_parts.append("Prepare for the final scene that concludes the journey.")
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
        force_encounter: bool = False,
        is_ending_phase: bool = False,
        turns_remaining: int = 0
    ) -> Tuple[str, List[str]]:
        prompt = self._build_prompt(
            player_context,
            player_choice,
            combat_context,
            shop_context,
            force_encounter,
            is_ending_phase,
            turns_remaining
        )

        messages = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]

        try:
            response_text = self._call_with_retry(messages)
            scene, choices = self._parse_response(response_text)

            if not choices or len(choices) < 3:
                logger.warning(f"AI returned {len(choices) if choices else 0} choices instead of 3")

            self.story_history.append(scene)
            self._extract_location(scene)

            if len(self.story_history) % self.summary_interval == 0:
                self._create_summary()
                logger.info(f"Created story summary at turn {len(self.story_history)}")

            return scene, choices

        except Exception as e:
            logger.error(f"Failed to generate scene: {str(e)}", exc_info=True)
            error_scene = f"The world seems to flicker around you as reality shifts. An error occurred: {str(e)}"
            default_choices = [
                "Try to stabilize your surroundings",
                "Close your eyes and focus",
                "Call out for help"
            ]
            return error_scene, default_choices

    def _extract_location(self, scene: str) -> None:
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
                model=MODEL_NAME,
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
                model=MODEL_NAME,
                messages=messages,
                max_tokens=200,
                temperature=0.8,
            )

            text = response.choices[0].message.content.strip()

            enemy_hint = "enemy"
            enemy_types = ["genderuwo", "kuntilanak", "tuyul", "pocong", "ahool", "orang bati",
                          "naga", "suku mante", "kuda sembrani", "kuyang", "nyi blorong",
                          "leak", "harimau", "raksasa", "dukun", "ular", "prajurit", 
                          "bajak laut", "arwah", "iblis", "garuda", "goblin", "bandit", 
                          "wolf", "skeleton", "orc", "mage", "spider", "troll", "rat", 
                          "ogre", "wraith", "dragon"]

            text_lower = text.lower()
            for enemy_type in enemy_types:
                if enemy_type in text_lower:
                    enemy_hint = enemy_type
                    break

            return text, enemy_hint

        except Exception as e:
            return f"A hostile creature appears before you! (Error: {e})", "enemy"

    def get_story_summary(self) -> str:
        if not self.story_history:
            return "Your adventure begins..."
        return "\n\n".join(self.story_history[-10:])

    def to_dict(self) -> dict:
        return {
            "story_history": self.story_history.copy(),
            "location": self.location,
            "npcs_met": self.npcs_met.copy(),
            "quests_active": self.quests_active.copy()
        }

    def from_dict(self, data: dict) -> None:
        self.story_history = data.get("story_history", [])
        self.location = data.get("location", "unknown")
        self.npcs_met = data.get("npcs_met", [])
        self.quests_active = data.get("quests_active", [])
