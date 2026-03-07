
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
        description="The glorious Majapahit Empire at its height under Gajah Mada",
        initial_scene="""Tahun 1350 Masehi. Kau berdiri di alun-alun Keraton Majapahit, ibu kota kerajaan terbesar di Nusantara. Di sekelilingmu, pedagang dari Cina, India, dan Arab berdagang rempah-rempah, kain, dan emas.

Patih Gajah Mada baru saja membacakan Sumpah Palapa di hadapan Prabu Hayam Wuruk. Seluruh Nusantara akan disatukan di bawah panji Majapahit.

Sebagai seorang prajurit muda yang menunjukkan keberanian luar biasa, kau dipanggil ke istana. Para pembisik berkata ada misi penting menantimu—misi yang akan menentukan nasib ribuan jiwa.""",
        choices=[
            "Masuki istana dan temui Patih Gajah Mada",
            "Jelajahi pasar dan kumpulkan informasi tentang misi ini",
            "Kunjungi pertapaan untuk meminta restu sebelum bertugas"
        ],
        starting_gold=25,
        starting_items=["keris kecil", "nasi bungkus"]
    ),

    StartingPoint(
        id=2,
        name="Misteri Gunung Merapi",
        description="Strange omens from the sacred volcano",
        initial_scene="""Tahun 1400 Masehi. Desa Kademangan di lereng Gunung Merapi gempar. Semalam, gunung berapi yang biasanya tenang mengeluarkan cahaya hijau misterius dari puncaknya.

Para sesepuh berkata ini adalah tanda bahwa Nyai Roro Kidul, Ratu Laut Selatan, sedang murka. Beberapa penduduk desa menghilang tanpa jejak, hanya meninggalkan jejak cahaya hijau yang mengarah ke dalam hutan.

Kau adalah seorang pawang muda yang baru saja menyelesaikan pelatihan. Masyarakat memandangmu untuk mengungkap misteri ini.""",
        choices=[
            "Naik ke puncak Merapi untuk menyelidiki cahaya hijau",
            "Masuk ke hutan mengikuti jejak cahaya",
            "Temui dukun desa untuk meminta nasihat spiritual"
        ],
        starting_gold=15,
        starting_items=["tombak", "jamu", "kemenyan"]
    ),

    StartingPoint(
        id=3,
        name="Hilangnya Pusaka Kerajaan",
        description="The sacred heirlooms of Pajajaran Kingdom have been stolen",
        initial_scene="""Tahun 1550 Masehi. Kerajaan Pajajaran dalam keadaan darurat. Malam tadi, pencuri misterius telah menembus keraton dan mencuri dua pusaka suci: Keris Ciung Wanara dan Perisai Sakti.

Tanpa pusaka tersebut, kerajaan kehilangan perlindungan spiritual. Prabu Siliwangi yang bijak mulai sakit, dan para menteri saling tuduh.

Kau adalah seorang mata-mata kerajaan yang baru kembali dari misi. Sang Prabu mempercayaimu untuk mengungkap pengkhianat ini.""",
        choices=[
            "Periksa tempat penyimpanan pusaka untuk mencari petunjuk",
            "Wawancarai para penjaga yang bertugas malam itu",
            "Menyamar sebagai pedagang dan cari informasi di pasar gelap"
        ],
        starting_gold=40,
        starting_items=["keris", "surat kepercayaan", "uang emas"]
    ),

    StartingPoint(
        id=4,
        name="Kutukan Ratu Pantai Selatan",
        description="Fishermen report terrifying sea creatures",
        initial_scene="""Tahun 1480 Masehi. Para nelayan di pantai selatan Jawa melaporkan hal yang mengerikan. Ikan-ikan menghilang, dan beberapa nelayan yang pulang bercerita tentang makhluk raksasa dengan sisik hijau dan mata menyala.

Seorang nelayan tua berkata ini adalah tanda bahwa Ratu Nyai Roro Kidul sedang mengumpulkan bala tentara. Dia membutuhkan tumbal manusia untuk memperkuat kerajaannya di dasar laut.

Kau adalah anak seorang nelayan yang hilang dalam kejadian ini. Kau bersumpah akan menemukan ayahmu, hidup atau mati.""",
        choices=[
            "Berlayar ke tengah laut untuk mencari makhluk tersebut",
            "Temui dukun pantai untuk ritual pemanggilan Ratu",
            "Kumpulkan para nelayan untuk berlayar bersama"
        ],
        starting_gold=10,
        starting_items=["jaring ikan", "parang", "mantra perlindungan"]
    ),

    StartingPoint(
        id=5,
        name="Perang Bubat",
        description="The tragic battle between Majapahit and Pajajaran",
        initial_scene="""Tahun 1357 Masehi. Kau adalah seorang prajurit Pajajaran yang mengiringi Putri Dyah Pitaloka ke Bubat untuk pernikahan dengan Prabu Hayam Wuruk.

Namun sesuatu yang tidak beres terjadi. Patih Gajah Mada menuntut Pajajaran tunduk pada Majapahit, bukan mengadakan pernikahan setara. Suasana tegang, dan kedua pasukan mulai bersiap untuk pertempuran.

Kau berdiri di persimpangan sejarah. Pilihanmu akan menentukan nasib ribuan nyawa dan masa depan Nusantara.""",
        choices=[
            "Lindungi Putri Dyah Pitaloka dengan nyawamu",
            "Coba bernegosiasi dengan utusan Majapahit",
            "Siapkan pasukan untuk pertempuran yang tak terhindarkan"
        ],
        starting_gold=30,
        starting_items=["tombak panjang", "perisai kayu", "bendera Pajajaran"]
    ),

    StartingPoint(
        id=6,
        name="Kerajaan Sriwijaya",
        description="The ancient Buddhist kingdom faces a new threat",
        initial_scene="""Tahun 900 Masehi. Sriwijaya, kerajaan maritim terbesar di Asia Tenggara, sedang dalam kejayaan. Kapal-kapal dagang dari seluruh dunia berlabuh di Palembang.

Namun kabar buruk datang dari utara. Kerajaan Chola dari India mulai membangun armada perang besar. Mereka mengincar jalur perdagangan rempah-rempah yang menjadi sumber kekayaan Sriwijaya.

Sebagai seorang laksamana muda, kau mendapat perintah untuk memperkuat pertahanan laut.""",
        choices=[
            "Kunjungi galangan kapal untuk memeriksa kekuatan armada",
            "Temui para biksu untuk meminta restu spiritual",
            "Kirim mata-mata ke wilayah Chola untuk intelijen"
        ],
        starting_gold=50,
        starting_items=["pedang lengkung", "peta laut", "surat perintah"]
    ),

    StartingPoint(
        id=7,
        name="Asal Usul Roro Jonggrang",
        description="The legend of the thousand temples",
        initial_scene="""Tahun 900 Masehi. Pangeran Bandung Bondowoso baru saja mengalahkan Prabu Baka, raja Prambanan. Namun ada harga yang harus dibayar.

Dia mencintai Putri Roro Jonggrang, putri Prabu Baka. Sang putri menolak dengan syarat: Bandung Bondowoso harus membangun seribu candi dalam satu malam.

Kau adalah seorang arsitek istana yang diperintahkan membantu pembangunan ini. Tapi kau tahu ada sesuatu yang ganjil—Bandung Bondowoso memiliki kekuatan gaib.""",
        choices=[
            "Mulai mengumpulkan bahan bangunan untuk candi",
            "Pantau Bandung Bondowoso untuk mengungkap rahasianya",
            "Bantu Roro Jonggrang mencari cara menggagalkan pembangunan"
        ],
        starting_gold=20,
        starting_items=["pahat", "gulungan desain", "obor"]
    ),

    StartingPoint(
        id=8,
        name="Kerajaan Demak",
        description="The rise of Islam in Java brings new challenges",
        initial_scene="""Tahun 1500 Masehi. Kesultanan Demak, kerajaan Islam pertama di Jawa, sedang berkembang pesat. Sunan Kalijaga dan para wali lainnya menyebarkan agama dengan bijak.

Namun kerajaan-kerajaan Hindu di pedalaman merasa terancam. Mereka membentuk aliansi rahasia untuk menyerang Demak sebelum terlalu kuat.

Kau adalah seorang santri yang juga ahli bela diri. Kau mendapat tugas khusus dari Sunan Kudus untuk mengungkap konspirasi ini.""",
        choices=[
            "Menyamar sebagai pedagang dan infiltrasi aliansi",
            "Kunjungi setiap kerajaan untuk merasakan suasana",
            "Minta bantuan para wali dengan ritual khusus"
        ],
        starting_gold=25,
        starting_items=["kris", "kitab suci", "jubah santri"]
    ),

    StartingPoint(
        id=9,
        name="Tragedi Tanjung Pura",
        description="A kingdom falls to supernatural forces",
        initial_scene="""Tahun 1600 Masehi. Kerajaan Tanjung Pura di Kalimantan hancur dalam semalam. Tidak ada serangan musuh, tidak ada pemberontakan. Seluruh penduduk menghilang, meninggalkan kota kosong dengan makanan masih hangat di atas meja.

Para pedagang yang lewat melaporkan melihat bayangan-bayangan hitam dan mendengar tangisan di malam hari. Beberapa berkata ini adalah kutukan dari kerajaan laut.

Kau adalah seorang investigator kerajaan yang dikirim untuk mengungkap kebenaran.""",
        choices=[
            "Masuki kota kosong dan cari petunjuk",
            "Wawancarai pedagang yang selamat",
            "Lakukan ritual pemanggilan arwah untuk bertanya"
        ],
        starting_gold=35,
        starting_items=["lentera", "kitab mantra", "tombak besi"]
    ),

    StartingPoint(
        id=10,
        name="Pemberontakan Trunajaya",
        description="The great rebellion against Mataram Sultanate",
        initial_scene="""Tahun 1675 Masehi. Raden Trunajaya dari Madura memimpin pemberontakan besar terhadap Kesultanan Mataram. Pasukannya yang kuat, dibantu oleh bajak laut Makasar, berhasil merebut banyak wilayah.

Kau adalah seorang prajurit Mataram yang menemukan dokumen rahasia: Trunajaya memiliki sekutu gaib—seorang dukun sakti yang bisa menghidupkan arwah prajurit yang gugur.

Sultan Amangkurat I mempercayaimu untuk menghentikan ritual gelap ini.""",
        choices=[
            "Menyusup ke kamp Trunajaya untuk cari dukun tersebut",
            "Kunjungi makam leluhur untuk minta perlindungan",
            "Kumpulkan prajurit setia untuk serangan mendadak"
        ],
        starting_gold=45,
        starting_items=["keris naga", "jimat perlindungan", "surat sultan"]
    )
]


class StoryManager:

    MIN_TURNS = 500
    MAX_TURNS = 700

    def __init__(self):
        self.starting_point: Optional[StartingPoint] = None
        self.turn_count = 0
        self.end_turn = 0
        self.game_ended = False
        self.ending_type = ""

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
        logger.info(f"Turn {self.turn_count}/{self.end_turn}, game_ended={self.game_ended}")

        if self.turn_count >= self.end_turn and not self.game_ended:
            self.game_ended = True
            logger.info(f"Game ending triggered at turn {self.turn_count}")
            return True

        return False

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

    def generate_ending_prompt(self) -> str:
        ending_type = self.get_ending_type()

        ending_descriptions = {
            "legendary_hero": "a legendary hero whose deeds will be remembered for ages",
            "hero": "a true hero who saved the realm",
            "survivor": "a survivor who endured against all odds",
            "wanderer": "a wanderer whose story remains untold",
            "forgotten": "one whose potential was never fully realized",
            "villain": "the villain of the story, feared and remembered for dark deeds"
        }

        choice_summary = ""
        if self.major_choices:
            choice_summary = "\n\nMAJOR CHOICES MADE:\n"
            for i, choice in enumerate(self.major_choices[-10:], 1):
                choice_summary += f"  {i}. Turn {choice['turn']}: {choice['choice']}\n"

        villain_summary = ""
        if ending_type == "villain" and self.villainous_acts:
            villain_summary = "\n\nVILLAINOUS ACTS:\n"
            for act in self.villainous_acts[-10:]:
                villain_summary += f"  • Turn {act['turn']}: {act['act']} - {act['description']}\n"

        if ending_type == "villain":
            stats = f"""
FINAL STATS:
- Turns Survived: {self.turn_count}
- Locations Visited: {len(self.locations_visited)}
- Enemies Defeated: {self.enemies_defeated}
- Betrayals: {self.betrayals}
- Innocents Harmed: {self.innocents_harmed}
- Dark Artifacts Claimed: {self.dark_artifacts_claimed}
- Villain Points: {self.villain_points}
- Ending Type: THE VILLAIN
"""
        else:
            stats = f"""
FINAL STATS:
- Turns Survived: {self.turn_count}
- Locations Visited: {len(self.locations_visited)}
- Enemies Defeated: {self.enemies_defeated}
- Allies Gained: {self.allies_gained}
- Quests Completed: {len(self.quests_completed)}
- Ending Type: {ending_type.replace('_', ' ').title()}
"""

        if ending_type == "villain":
            return f"""The adventure has reached its conclusion. The player has become {ending_descriptions[ending_type]}.{choice_summary}{villain_summary}{stats}

Write a DARK and DRAMATIC ending to this story (150-200 words) that:
1. Shows the player's transformation into a true villain
2. Describes the terror and chaos they unleashed upon the realm
3. Shows how their villainous choices led to this dark conclusion
4. Makes the player feel powerful but corrupted/feared
5. Ends with an ominous epilogue about their dark legacy

The tone should be menacing, epic, and show that the villain has triumphed (or been sealed away, but still feared).""", stats

        return f"""The adventure has reached its conclusion. The player has become {ending_descriptions[ending_type]}.{choice_summary}{stats}

Write a conclusive ending to this story (150-200 words) that:
1. Reflects on the player's journey and major choices
2. Shows the consequences of their actions
3. Provides closure to their story
4. Matches the ending type: {ending_type.replace('_', ' ')}

End with a final epilogue-style statement about their legacy.""", stats

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
