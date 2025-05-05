# src/engine/ecs/components.py
from dataclasses import dataclass, field
from typing import Optional, List
import numpy as np
from ..physics.verlet_system import VerletPoint

@dataclass
class Component:
    entity: Optional['Entity'] = None

@dataclass
class Transform(Component):
    position: np.ndarray = field(default_factory=lambda: np.zeros(2))
    rotation: float = 0.0
    scale: np.ndarray = field(default_factory=lambda: np.ones(2))

@dataclass
class PhysicsBody(Component):
    verlet_points: List[VerletPoint] = field(default_factory=list)
    mass: float = 1.0
    is_static: bool = False

@dataclass
class Sprite(Component):
    texture_path: str = ""  # Chemin vers la texture
    z_index: int = 0       # Ordre de rendu (plus élevé = au-dessus)
    color: np.ndarray = field(default_factory=lambda: np.array([1.0, 1.0, 1.0, 1.0]))  # RGBA

@dataclass
class Animation(Component):
    frames: List[str] = field(default_factory=list)  # Liste des chemins de texture pour l'animation
    current_frame_index: int = 0
    frame_duration: float = 0.1  # Durée de chaque frame en secondes
    time_since_last_frame: float = 0.0
    is_playing: bool = True
    loop: bool = True

@dataclass
class TrajectoryProjectile(Component):
    velocity: np.ndarray = field(default_factory=lambda: np.zeros(2))
    acceleration: np.ndarray = field(default_factory=lambda: np.zeros(2))
    lifetime: float = 5.0
    damage: float = 1.0
    
@dataclass
class Health(Component):
    max_health: float = 100.0
    current_health: float = 100.0
    
    def take_damage(self, amount: float):
        self.current_health = max(0.0, self.current_health - amount)
        
    def heal(self, amount: float):
        self.current_health = min(self.max_health, self.current_health + amount)

@dataclass
class Attack(Component):
    damage: float = 10.0
    attack_range: float = 1.0
    attack_speed: float = 1.0 # Attaques par seconde
    last_attack_time: float = 0.0

@dataclass
class Defense(Component):
    armor: float = 5.0
    resistance: float = 0.0 # Pourcentage de réduction des dégâts magiques (par exemple)

@dataclass
class AIController(Component):
    state: str = "idle"
    target: Optional['Entity'] = None
    fear_threshold: float = 50.0
    confidence: float = 100.0