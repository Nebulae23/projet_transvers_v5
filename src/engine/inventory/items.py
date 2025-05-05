# src/engine/inventory/items.py
from enum import Enum
from dataclasses import dataclass
from typing import Dict, Optional

class ItemType(Enum):
    WEAPON = "weapon"
    ARMOR = "armor"
    CONSUMABLE = "consumable"
    MATERIAL = "material"
    QUEST = "quest"

class ItemRarity(Enum):
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

@dataclass
class ItemStats:
    damage: float = 0.0
    defense: float = 0.0
    health: float = 0.0
    speed: float = 0.0

@dataclass
class Item:
    id: str
    name: str
    type: ItemType
    rarity: ItemRarity
    description: str
    stackable: bool
    max_stack: int
    stats: ItemStats
    icon_path: str
    value: int
    
    def __init__(self, 
                 id: str,
                 name: str,
                 type: ItemType,
                 rarity: ItemRarity = ItemRarity.COMMON,
                 description: str = "",
                 stackable: bool = False,
                 max_stack: int = 1,
                 stats: Optional[ItemStats] = None,
                 icon_path: str = "default_item.png",
                 value: int = 0):
        self.id = id
        self.name = name
        self.type = type
        self.rarity = rarity
        self.description = description
        self.stackable = stackable
        self.max_stack = max_stack if stackable else 1
        self.stats = stats or ItemStats()
        self.icon_path = icon_path
        self.value = value

class ItemDatabase:
    def __init__(self):
        self.items: Dict[str, Item] = {}
        self._initialize_items()
        
    def _initialize_items(self):
        # Weapons
        self.register_item(Item(
            id="sword_basic",
            name="Basic Sword",
            type=ItemType.WEAPON,
            description="A simple but reliable sword",
            stats=ItemStats(damage=10.0),
            value=100
        ))
        
        # Armor
        self.register_item(Item(
            id="armor_leather",
            name="Leather Armor",
            type=ItemType.ARMOR,
            description="Basic protective gear",
            stats=ItemStats(defense=5.0),
            value=150
        ))
        
        # Consumables
        self.register_item(Item(
            id="potion_health",
            name="Health Potion",
            type=ItemType.CONSUMABLE,
            description="Restores 50 HP",
            stackable=True,
            max_stack=10,
            stats=ItemStats(health=50.0),
            value=25
        ))
        
    def register_item(self, item: Item):
        self.items[item.id] = item
        
    def get_item(self, item_id: str) -> Optional[Item]:
        return self.items.get(item_id)