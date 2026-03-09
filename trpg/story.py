
import random
import logging
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field

logger = logging.getLogger('StoryManager')


@dataclass
class StartingPoint:
    id: int
    name: str
    description: str
    initial_scene: str
    choices: List[str]
    starting_gold: int = 0
    starting_items: List[str] = field(default_factory=list)
    difficulty_modifier: float = 1.0


STARTING_POINTS = [
    StartingPoint(
        id=1,
        name="Kerajaan Majapahit",
        description="The glorious Majapahit Empire at its height",
        initial_scene="""Year 1350 CE. You stand in the alun-alun (royal square) of Majapahit Palace. Merchants from China, India, and Arabia trade spices and gold around you.

A royal messenger approaches with urgent news. Three trade caravans have vanished on the northern route. Soldiers whisper about shadows moving near the border.

Patih Gajah Mada summons you. His expression is grave.""",
        choices=[
            "Report to Patih Gajah Mada immediately",
            "Question merchants at the market",
            "Visit the northern gate guards"
        ],
        starting_gold=25,
        starting_items=["keris kecil", "nasi bungkus"]
    ),

    StartingPoint(
        id=2,
        name="Misteri Gunung Merapi",
        description="Strange omens from the sacred volcano",
        initial_scene="""Year 1400 CE. The village of Kademangan sits on Mount Merapi's slopes. Usually calm, the volcano now glows green at night.

Three villagers vanished this week. Only green trails remain, leading into the forest.

The village elders gather around you. You completed your pawang training yesterday.""",
        choices=[
            "Examine the green trails",
            "Speak with the village elders",
            "Climb toward the glowing peak"
        ],
        starting_gold=15,
        starting_items=["tombak", "jamu", "kemenyan"]
    ),

    StartingPoint(
        id=3,
        name="Hilangnya Pusaka Kerajaan",
        description="The sacred heirlooms have been stolen",
        initial_scene="""Year 1550 CE. The Pajajaran palace is in chaos. Prabu Siliwangi lies ill, growing weaker each day.

Last night, someone entered the sacred treasury. The guards found only an empty pedestal and a strange symbol carved in stone.

The royal advisor beckons you. The King requests your presence.""",
        choices=[
            "Enter the King's chamber",
            "Inspect the treasury",
            "Question the night guards"
        ],
        starting_gold=40,
        starting_items=["keris kecil", "jimat perlindungan", "emas batangan"]
    ),

    StartingPoint(
        id=4,
        name="Kutukan Ratu Pantai Selatan",
        description="Fishermen report terrifying sightings",
        initial_scene="""Year 1480 CE. The southern coast fishing village is empty during daylight. Boats sit unused at the harbor.

Seven fishermen disappeared last week. One survivor babbles about green scales and a queen beneath the waves.

The village elder approaches you. Your father was among the missing.""",
        choices=[
            "Examine the abandoned boats",
            "Find the survivor",
            "Walk along the shoreline"
        ],
        starting_gold=10,
        starting_items=["parang", "jamu", "gelang emas"]
    ),

    StartingPoint(
        id=5,
        name="Perang Bubat",
        description="The tragic battle between Majapahit and Pajajaran",
        initial_scene="""Year 1357 CE. You escort Princess Dyah Pitaloka's procession to Bubat. Marriage to Prabu Hayam Wuruk should unite two kingdoms.

But the atmosphere is wrong. Majapahit soldiers surround the camp. Their numbers grow each hour.

Your captain calls you aside. His face is pale.""",
        choices=[
            "Speak with your captain",
            "Observe the Majapahit positions",
            "Check on the Princess"
        ],
        starting_gold=30,
        starting_items=["tombak panjang", "perisai kayu", "ikat kepala"]
    ),

    StartingPoint(
        id=6,
        name="Kerajaan Sriwijaya",
        description="The ancient Buddhist kingdom faces a new threat",
        initial_scene="""Year 1000 CE. Palembang harbor bustles with ships from China, India, and Arabia. Sriwijaya controls the spice trade.

But three merchant vessels failed to arrive this month. Sailors speak of warships near the northern strait.

The harbor master hands you a sealed order from the admiral.""",
        choices=[
            "Read the admiral's order",
            "Question arriving sailors",
            "Inspect the naval shipyard"
        ],
        starting_gold=50,
        starting_items=["pedang lengkung", "jamu", "mutiara"]
    ),

    StartingPoint(
        id=7,
        name="Asal Usul Roro Jonggrang",
        description="The legend of the thousand temples",
        initial_scene="""10th Century CE. Prince Bandung Bondowoso defeated Prabu Baka of Prambanan. Now he demands the princess's hand in marriage.

She agrees on one condition: build a thousand temples in one night.

You are the court architect. The Prince accepts. Construction begins at sunset.""",
        choices=[
            "Survey the construction site",
            "Gather building materials",
            "Watch the Prince closely"
        ],
        starting_gold=20,
        starting_items=["jamu", "buah-buahan", "batu akik"]
    ),

    StartingPoint(
        id=8,
        name="Kerajaan Demak",
        description="The rise of Islam in Java brings new challenges",
        initial_scene="""Year 1500 CE. Demak Sultanate flourishes. The Great Mosque echoes with prayers. Sunan Kalijaga teaches in the courtyard.

But traders bring troubling rumors. Inland courts hold secret meetings. Caravans vanish on the mountain roads.

Sunan Kudus gestures for you to approach.""",
        choices=[
            "Approach Sunan Kudus",
            "Visit the harbor market",
            "Speak with traveling merchants"
        ],
        starting_gold=25,
        starting_items=["kris", "jubah santri", "kemenyan"]
    ),

    StartingPoint(
        id=9,
        name="Tragedi Tanjung Pura",
        description="A kingdom falls to supernatural forces",
        initial_scene="""Year 1600 CE. You approach Tanjung Pura at dusk. The city should be bustling. Instead, silence.

No guards at the gates. No smoke from chimneys. Food sits on tables, still warm.

Your royal orders are clear: investigate and report. You enter alone.""",
        choices=[
            "Search the nearest building",
            "Call out for survivors",
            "Examine the central square"
        ],
        starting_gold=35,
        starting_items=["tombak", "jamu", "minyak kelapa"]
    ),

    StartingPoint(
        id=10,
        name="Pemberontakan Trunajaya",
        description="The great rebellion against Mataram Sultanate",
        initial_scene="""Year 1675 CE. Trunajaya's rebellion spreads across Mataram. Villages burn. Refugees flood the roads.

You intercept a captured messenger. His documents mention a "dark ally" who can raise the dead.

The Sultan's seal marks the papers as urgent.""",
        choices=[
            "Read the captured documents",
            "Question the messenger",
            "Report to headquarters"
        ],
        starting_gold=45,
        starting_items=["keris naga", "jimat perlindungan", "jamu kuat"]
    )
]


class StoryManager:

    MIN_TURNS = 500
    MAX_TURNS = 700
    ENDING_PHASE_TURNS = 50

    def __init__(self):
        self.starting_point: Optional[StartingPoint] = None
        self.turn_count = 0
        self.end_turn = 0
        self.game_ended = False
        self.ending_type = ""
        self.in_ending_phase = False

        self.major_choices: List[Dict[str, Any]] = []
        self.locations_visited: List[str] = []
        self.npcs_met: List[str] = []
        self.quests_completed: List[str] = []
        self.enemies_defeated: int = 0
        self.allies_gained: int = 0

        self.last_encounter_turn = -10
        self.encounters_in_area = 0
        self.current_area = "unknown"

        self.villain_points = 0
        self.villainous_acts: List[Dict[str, Any]] = []
        self.betrayals = 0
        self.innocents_harmed = 0
        self.dark_artifacts_claimed = 0

    def select_starting_point(self) -> StartingPoint:
        self.starting_point = random.choice(STARTING_POINTS)
        return self.starting_point

    def get_starting_point_by_id(self, point_id: int) -> Optional[StartingPoint]:
        for sp in STARTING_POINTS:
            if sp.id == point_id:
                return sp
        return None

    def initialize_game(self) -> Tuple[StartingPoint, int]:
        self.starting_point = self.select_starting_point()
        self.end_turn = random.randint(self.MIN_TURNS, self.MAX_TURNS)
        self.turn_count = 0
        self.game_ended = False
        self.major_choices = []
        self.locations_visited = [self.starting_point.name]
        self.enemies_defeated = 0
        self.allies_gained = 0
        self.villain_points = 0
        self.villainous_acts = []
        self.betrayals = 0
        self.innocents_harmed = 0
        self.dark_artifacts_claimed = 0
        logger.info(f"Game initialized: end_turn={self.end_turn}, MIN={self.MIN_TURNS}, MAX={self.MAX_TURNS}")
        return self.starting_point, self.end_turn

    def increment_turn(self) -> bool:
        self.turn_count += 1
        logger.info(f"Turn {self.turn_count}/{self.end_turn}, game_ended={self.game_ended}, in_ending_phase={self.in_ending_phase}")

        turns_remaining = self.end_turn - self.turn_count

        if turns_remaining == 50 and not self.in_ending_phase:
            self.in_ending_phase = True
            logger.info(f"ENDING PHASE STARTED: {self.ENDING_PHASE_TURNS} turns remaining")

        if turns_remaining == 30:
            logger.info("ENDING PHASE: Building tension at 30 turns remaining")

        if turns_remaining == 10:
            logger.info("ENDING PHASE: Climax approaching at 10 turns remaining")

        if turns_remaining == 3:
            logger.info("ENDING PHASE: Final 3 turns - prepare conclusion")

        if self.turn_count >= self.end_turn and not self.game_ended:
            self.game_ended = True
            logger.info(f"Game ending triggered at turn {self.turn_count}")
            return True

        return False

    def is_in_ending_phase(self) -> bool:
        return self.in_ending_phase

    def get_turns_remaining(self) -> int:
        return max(0, self.end_turn - self.turn_count)

    def record_choice(self, choice: str, context: str = "", consequence: str = "") -> None:
        self.major_choices.append({
            "turn": self.turn_count,
            "choice": choice,
            "context": context,
            "consequence": consequence
        })

    def record_location(self, location: str) -> None:
        if location not in self.locations_visited:
            self.locations_visited.append(location)

    def record_npc(self, npc_name: str, relationship: str = "neutral") -> None:
        if npc_name not in self.npcs_met:
            self.npcs_met.append(npc_name)
            if relationship in ["ally", "friend", "companion"]:
                self.allies_gained += 1

    def record_quest_completed(self, quest_name: str) -> None:
        self.quests_completed.append(quest_name)

    def record_enemy_defeated(self) -> None:
        self.enemies_defeated += 1

    def record_villainous_act(self, act: str, description: str) -> None:
        self.villainous_acts.append({
            "turn": self.turn_count,
            "act": act,
            "description": description
        })
        self.villain_points += 10

    def record_betrayal(self, who: str) -> None:
        self.betrayals += 1
        self.villain_points += 25
        self.villainous_acts.append({
            "turn": self.turn_count,
            "act": "betrayal",
            "description": f"Betrayed {who}"
        })

    def record_innocent_harmed(self, description: str) -> None:
        self.innocents_harmed += 1
        self.villain_points += 15
        self.villainous_acts.append({
            "turn": self.turn_count,
            "act": "harm_innocents",
            "description": description
        })

    def record_dark_artifact(self, artifact_name: str) -> None:
        self.dark_artifacts_claimed += 1
        self.villain_points += 20
        self.villainous_acts.append({
            "turn": self.turn_count,
            "act": "dark_artifact",
            "description": f"Claimed {artifact_name}"
        })

    def record_selfish_choice(self, description: str) -> None:
        self.villain_points += 5
        self.villainous_acts.append({
            "turn": self.turn_count,
            "act": "selfish",
            "description": description
        })

    def is_villain_path(self) -> bool:
        return (
            self.villain_points >= 50 or
            self.betrayals >= 3 or
            self.innocents_harmed >= 5 or
            self.dark_artifacts_claimed >= 2
        )

    def should_trigger_encounter(self, scene_text: str, location: str) -> Tuple[bool, str]:
        scene_lower = scene_text.lower()

        explicit_combat_keywords = [
            "attacks", "lunges", "charges", "appears", "emerges", "blocks",
            "enemy", "monster", "creature", "beast", "hostile", "ambush",
            "combat", "battle begins", "fight", "draws weapon", "hostile"
        ]

        for keyword in explicit_combat_keywords:
            if keyword in scene_lower:
                return True, f"Explicit trigger: '{keyword}' in scene"

        turns_since_encounter = self.turn_count - self.last_encounter_turn
        if turns_since_encounter < 3:
            return False, f"Too soon: only {turns_since_encounter} turns since last encounter"

        dangerous_keywords = ["forest", "dungeon", "cave", "ruins", "wilderness",
                             "dark", "dangerous", "enemy territory", "battlefield",
                             "mountain", "swamp", "wasteland", "tomb"]
        safe_keywords = ["village", "town", "city", "temple", "shrine", "safe",
                        "sanctuary", "inn", "castle", "friendly"]

        danger_level = 0.25

        for keyword in dangerous_keywords:
            if keyword in scene_lower or keyword in location.lower():
                danger_level += 0.15
                break

        for keyword in safe_keywords:
            if keyword in scene_lower or keyword in location.lower():
                danger_level -= 0.15
                break

        roll = random.random()

        if roll < danger_level:
            self.last_encounter_turn = self.turn_count
            return True, f"Random encounter (roll: {roll:.2f} < {danger_level:.2f})"

        return False, f"No encounter (roll: {roll:.2f} >= {danger_level:.2f})"

    def get_ending_type(self) -> str:
        if self.is_villain_path():
            return "villain"

        hero_score = 0
        hero_score += len(self.quests_completed) * 10

        if self.enemies_defeated >= 50:
            hero_score += 30
        elif self.enemies_defeated >= 20:
            hero_score += 20
        elif self.enemies_defeated >= 10:
            hero_score += 10

        hero_score += self.allies_gained * 5
        hero_score += len(self.locations_visited) * 2

        if hero_score >= 100:
            return "legendary_hero"
        elif hero_score >= 70:
            return "hero"
        elif hero_score >= 40:
            return "survivor"
        elif hero_score >= 20:
            return "wanderer"
        else:
            return "forgotten"

    def generate_ending_prompt(self) -> Tuple[str, str]:
        ending_type = self.get_ending_type()

        ending_descriptions = {
            "legendary_hero": "a legendary hero whose deeds will be remembered for ages",
            "hero": "a true hero who saved the realm",
            "survivor": "a survivor who endured against all odds",
            "wanderer": "a wanderer whose story remains untold",
            "forgotten": "one whose potential was never fully realized",
            "villain": "the villain of the story, feared and remembered for dark deeds"
        }

        journey_context = f"""
YOUR JOURNEY BEGAN: {self.starting_point.name if self.starting_point else 'Unknown'}
- {self.starting_point.description if self.starting_point else ''}

THE PATH YOU WALKED:
- Turns Survived: {self.turn_count}
- Kingdoms & Locations Visited: {len(self.locations_visited)}
- Enemies Defeated: {self.enemies_defeated}
- Allies Made: {self.allies_gained}
"""

        choice_summary = ""
        if self.major_choices:
            choice_summary = "\nPIVOTAL MOMENTS:\n"
            for i, choice in enumerate(self.major_choices[-8:], 1):
                choice_summary += f"  {i}. {choice['choice'][:80]}...\n"

        villain_summary = ""
        if ending_type == "villain" and self.villainous_acts:
            villain_summary = "\nDARK DEEDS:\n"
            for act in self.villainous_acts[-8:]:
                villain_summary += f"  • {act['description'][:60]}...\n"

        if ending_type == "villain":
            stats = f"""{journey_context}{choice_summary}{villain_summary}
ENDING: THE VILLAIN'S LEGACY
"""
        else:
            stats = f"""{journey_context}{choice_summary}
ENDING: {ending_type.replace('_', ' ').title()}
"""

        if ending_type == "villain":
            return f"""The adventure has reached its natural conclusion. Through darkness and corruption, the player has become {ending_descriptions[ending_type]}.{stats}

Write a DARK and DRAMATIC ending (150-200 words) that:
1. SHOWS the transformation through narrative, not telling
2. References specific dark choices from the journey above
3. Describes the consequences unleashed upon the Indonesian kingdoms
4. Connects back to the starting point (how far they've fallen)
5. Ends with an ominous epilogue about their dark legacy

Make it feel like a natural conclusion to THIS specific journey, not a generic villain ending.""", stats

        return f"""The adventure has reached its natural conclusion. The player has become {ending_descriptions[ending_type]}.{stats}

Write a conclusive ending (150-200 words) that:
1. REFLECTS on the specific journey described above
2. REFERENCES 2-3 pivotal choices from their path
3. SHOWS consequences through narrative (not just telling)
4. CONNECTS back to where they started ({self.starting_point.name if self.starting_point else 'their beginning'})
5. PROVIDES closure that feels earned by THIS player's actions
6. ENDS with an epilogue about their legacy in the Indonesian kingdoms

Make it feel like THE ONLY ending that could follow THIS specific journey.""", stats

    def to_dict(self) -> dict:
        return {
            "starting_point_id": self.starting_point.id if self.starting_point else None,
            "turn_count": self.turn_count,
            "end_turn": self.end_turn,
            "game_ended": self.game_ended,
            "major_choices": self.major_choices,
            "locations_visited": self.locations_visited,
            "npcs_met": self.npcs_met,
            "quests_completed": self.quests_completed,
            "enemies_defeated": self.enemies_defeated,
            "allies_gained": self.allies_gained,
            "last_encounter_turn": self.last_encounter_turn,
            "villain_points": self.villain_points,
            "villainous_acts": self.villainous_acts,
            "betrayals": self.betrayals,
            "innocents_harmed": self.innocents_harmed,
            "dark_artifacts_claimed": self.dark_artifacts_claimed
        }

    def from_dict(self, data: dict) -> None:
        sp_id = data.get("starting_point_id")
        if sp_id:
            self.starting_point = self.get_starting_point_by_id(sp_id)

        self.turn_count = data.get("turn_count", 0)
        self.end_turn = data.get("end_turn", 0)
        self.game_ended = data.get("game_ended", False)
        self.major_choices = data.get("major_choices", [])
        self.locations_visited = data.get("locations_visited", [])
        self.npcs_met = data.get("npcs_met", [])
        self.quests_completed = data.get("quests_completed", [])
        self.enemies_defeated = data.get("enemies_defeated", 0)
        self.allies_gained = data.get("allies_gained", 0)
        self.last_encounter_turn = data.get("last_encounter_turn", -10)
        self.villain_points = data.get("villain_points", 0)
        self.villainous_acts = data.get("villainous_acts", [])
        self.betrayals = data.get("betrayals", 0)
        self.innocents_harmed = data.get("innocents_harmed", 0)
        self.dark_artifacts_claimed = data.get("dark_artifacts_claimed", 0)
