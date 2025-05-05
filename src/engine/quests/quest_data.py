from enum import Enum, auto
from dataclasses import dataclass
from typing import Dict, List, Optional
from abc import ABC, abstractmethod

class QuestType(Enum):
    STORY = auto()
    SIDE = auto()
    DAILY = auto()
    CHAIN = auto()
    SPECIAL = auto()

class ObjectiveType(Enum):
    KILL = auto()
    COLLECT = auto()
    DEFEND = auto()
    BUILD = auto()
    EXPLORE = auto()

@dataclass
class Reward:
    resources: Dict[str, int]  # Type de ressource -> quantité
    experience: int
    special_items: List[str]  # IDs des items spéciaux
    unlock_quests: List[str]  # IDs des quêtes débloquées

@dataclass
class Objective:
    id: str # Identifiant unique de l'objectif dans la quête
    type: ObjectiveType
    target: str  # ID de la cible (monstre, ressource, zone...)
    amount: int  # Quantité requise
    current: int = 0  # Progression actuelle
    optional: bool = False
    description: str = "" # Description de l'objectif

@dataclass
class Quest:
    id: str
    type: QuestType
    title: str
    description: str
    objectives: List[Objective]
    rewards: Reward
    prerequisites: List[str]  # IDs des quêtes requises
    time_limit: Optional[float] = None  # En secondes, None = pas de limite