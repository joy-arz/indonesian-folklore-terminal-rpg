
import random
from typing import Dict, List, Optional, Tuple
from .player import Player, Item, ItemCategory


class Shop:

    SHOP_TYPES = {
        "general": {
            "name": "Pasar Umum",
            "items": ["jamu", "jamu kuat", "nasi bungkus", "buah-buahan", "kemenyan",
                     "keris kecil", "tombak", "baju zirah", "perisai kayu"],
        },
        "weapon": {
            "name": "Empa Keris",
            "items": ["keris kecil", "keris naga", "tombak", "tombak panjang", "pedang lengkung",
                     "pedang naga", "parang", "kris", "golok"],
        },
        "armor": {
            "name": "Tukang Besi",
            "items": ["baju zirah", "baju besi", "baju perang", "perisai kayu", "perisai besi",
                     "perisai sakti", "jubah santri", "jubah dukun"],
        },
        "magic": {
            "name": "Dukun",
            "items": ["jamu", "jamu kuat", "jamu sakti", "kemenyan", "minyak kelapa",
                     "jimat perlindungan", "cincin sakti", "kalung keramat"],
        },
        "black_market": {
            "name": "Pasar Gelap",
            "items": ["keris naga", "keris pusaka", "pedang naga", "baju perang",
                     "cincin sakti", "kalung keramat", "mutiara"],
        },
    }

    def __init__(self, shop_type: str = "general", player_level: int = 1):
        shop_data = self.SHOP_TYPES.get(shop_type, self.SHOP_TYPES["general"])
        self.name = shop_data["name"]
        self.shop_type = shop_type
        self.player_level = player_level

        self.inventory: Dict[str, int] = {}
        base_items = shop_data["items"]

        for item_name in base_items:
            if item_name in Item.ITEM_DATABASE:
                item = Item(item_name)
                if self._is_item_appropriate(item):
                    self.inventory[item_name] = random.randint(3, 10)

        if player_level >= 5:
            rare_items = ["steel sword", "chain mail", "ring of strength", "amulet of power"]
            for item_name in rare_items:
                if item_name not in self.inventory and random.random() < 0.5:
                    self.inventory[item_name] = random.randint(1, 3)

        if player_level >= 10:
            epic_items = ["magic sword", "plate armor", "dragon blade", "dragon pendant"]
            for item_name in epic_items:
                if item_name not in self.inventory and random.random() < 0.3:
                    self.inventory[item_name] = random.randint(1, 2)

        self.gold = 100 + (player_level * 20)

        self.markup = 0.5
        self.player_discount = 0.0

    def _is_item_appropriate(self, item: Item) -> bool:
        max_value = 20 + (self.player_level * 15)
        return item.value <= max_value

    def get_buy_price(self, item_name: str) -> int:
        item_name = item_name.lower()
        if item_name not in self.inventory or self.inventory[item_name] <= 0:
            return 0

        if item_name not in Item.ITEM_DATABASE:
            return 1

        base_value = Item.ITEM_DATABASE[item_name].get("value", 1)
        price = int(base_value * (1 - self.player_discount))
        return max(1, price)

    def get_sell_price(self, item_name: str) -> int:
        item_name = item_name.lower()

        if item_name not in Item.ITEM_DATABASE:
            return 0

        base_value = Item.ITEM_DATABASE[item_name].get("value", 1)
        price = int(base_value * self.markup)
        return max(1, price)

    def buy_item(self, player: Player, item_name: str, quantity: int = 1) -> Tuple[bool, str]:
        item_name = item_name.lower()

        if item_name not in self.inventory or self.inventory[item_name] < quantity:
            return False, f"Sorry, I don't have that item in stock."

        price = self.get_buy_price(item_name) * quantity

        if player.gold < price:
            return False, f"You need {price} gold, but you only have {player.gold}."

        player.remove_gold(price)
        player.add_item(item_name, quantity)
        self.inventory[item_name] -= quantity
        self.gold += price

        return True, f"Bought {quantity}x {item_name} for {price} gold!"

    def sell_item(self, player: Player, item_name: str, quantity: int = 1) -> Tuple[bool, str]:
        item_name = item_name.lower()

        if not player.has_item(item_name):
            return False, f"You don't have any {item_name} to sell."

        player_qty = player.get_item_quantity(item_name)
        if player_qty < quantity:
            return False, f"You only have {player_qty} {item_name}."

        price = self.get_sell_price(item_name) * quantity

        if price <= 0:
            return False, f"I don't buy {item_name}."

        if self.gold < price:
            return False, f"I only have {self.gold} gold, not enough for that."

        player.remove_item(item_name, quantity)
        player.add_gold(price)
        self.gold -= price

        if item_name in self.inventory:
            self.inventory[item_name] += quantity
        else:
            self.inventory[item_name] = quantity

        return True, f"Sold {quantity}x {item_name} for {price} gold!"

    def get_inventory_string(self) -> str:
        if not self.inventory:
            return "This shop has no items for sale."

        lines = [f"=== {self.name} ===", f"Shop Gold: {self.gold}"]
        lines.append("-" * 40)

        by_category: Dict[str, List[Tuple[str, int, int]]] = {}

        for item_name, qty in sorted(self.inventory.items()):
            if qty <= 0:
                continue

            if item_name in Item.ITEM_DATABASE:
                item = Item(item_name)
                cat = item.category.value
                price = self.get_buy_price(item_name)

                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append((item_name, price, qty))

        for category, items in sorted(by_category.items()):
            lines.append(f"\n{category.upper()}:")
            for name, price, qty in items:
                item = Item(name)
                stats = ""
                if item.attack > 0:
                    stats += f" +{item.attack} ATK"
                if item.defense > 0:
                    stats += f" +{item.defense} DEF"
                if item.heal > 0:
                    stats += f" +{item.heal} HP"
                lines.append(f"  • {name} ({qty}x) - {price}g{stats}")

        return "\n".join(lines)

    def restock(self) -> None:
        shop_data = self.SHOP_TYPES.get(self.shop_type, self.SHOP_TYPES["general"])

        for item_name in shop_data["items"]:
            if item_name in self.inventory:
                self.inventory[item_name] = max(
                    self.inventory[item_name],
                    random.randint(3, 10)
                )
            else:
                self.inventory[item_name] = random.randint(3, 10)

        self.gold = 100 + (self.player_level * 20)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "shop_type": self.shop_type,
            "player_level": self.player_level,
            "inventory": self.inventory.copy(),
            "gold": self.gold,
            "markup": self.markup,
            "player_discount": self.player_discount
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Shop":
        shop = cls(
            shop_type=data.get("shop_type", "general"),
            player_level=data.get("player_level", 1)
        )
        shop.name = data.get("name", shop.name)
        shop.inventory = data.get("inventory", {})
        shop.gold = data.get("gold", 100)
        shop.markup = data.get("markup", 0.5)
        shop.player_discount = data.get("player_discount", 0.0)
        return shop


def find_shop(player_level: int = 1) -> Shop:
    if player_level >= 10:
        shop_types = ["general", "weapon", "armor", "magic", "black_market"]
        weights = [20, 25, 25, 20, 10]
    elif player_level >= 5:
        shop_types = ["general", "weapon", "armor", "magic"]
        weights = [30, 25, 25, 20]
    else:
        shop_types = ["general", "weapon", "armor"]
        weights = [50, 30, 20]

    shop_type = random.choices(shop_types, weights=weights)[0]
    return Shop(shop_type, player_level)
