# src/engine/world/npc.py
from typing import Dict, List, Tuple, Optional
from enum import Enum
import numpy as np
from dataclasses import dataclass

class NPCType(Enum):
    VILLAGER = "villager"
    MERCHANT = "merchant"
    QUEST_GIVER = "quest_giver"
    GUARD = "guard"

class NPCState(Enum):
    IDLE = "idle"
    WALKING = "walking"
    TALKING = "talking"
    WORKING = "working"

@dataclass
class DialogueNode:
    text: str
    responses: Dict[str, 'DialogueNode']
    quest_trigger: Optional[str] = None
    trade_trigger: bool = False

class NPC:
    def __init__(self, npc_id: str, npc_type: NPCType, position: Tuple[float, float, float]):
        self.npc_id = npc_id
        self.type = npc_type
        self.position = list(position)
        self.rotation = 0.0
        self.state = NPCState.IDLE
        self.dialogue_tree = self._create_dialogue_tree()
        self.current_dialogue = None
        self.walking_path: List[Tuple[float, float, float]] = []
        self.daily_schedule: Dict[int, Tuple[str, Tuple[float, float, float]]] = {}
        
    def _create_dialogue_tree(self) -> DialogueNode:
        if self.type == NPCType.VILLAGER:
            return DialogueNode(
                "Hello traveler! Welcome to our village.",
                {
                    "How are you?": DialogueNode(
                        "I'm doing well, thank you for asking!",
                        {}
                    ),
                    "Any news?": DialogueNode(
                        "I heard there's been strange activity in the ruins nearby...",
                        {},
                        quest_trigger="explore_ruins"
                    )
                }
            )
        elif self.type == NPCType.MERCHANT:
            return DialogueNode(
                "Welcome! Would you like to see my wares?",
                {
                    "Yes, show me": DialogueNode(
                        "Here's what I have today.",
                        {},
                        trade_trigger=True
                    ),
                    "Not today": DialogueNode(
                        "Come back anytime!",
                        {}
                    )
                }
            )
        # Add more NPC-specific dialogue trees
        return DialogueNode("Hello.", {})
        
    def update(self, dt: float):
        if self.state == NPCState.WALKING and self.walking_path:
            self._update_movement(dt)
        elif self.state == NPCState.IDLE:
            self._update_idle(dt)
            
    def _update_movement(self, dt: float):
        if not self.walking_path:
            self.state = NPCState.IDLE
            return
            
        target = self.walking_path[0]
        dx = target[0] - self.position[0]
        dz = target[2] - self.position[2]
        dist = np.sqrt(dx*dx + dz*dz)
        
        if dist < 0.1:  # Reached waypoint
            self.walking_path.pop(0)
            if not self.walking_path:
                self.state = NPCState.IDLE
                return
                
        # Update position
        speed = 2.0  # units per second
        if dist > 0:
            self.position[0] += dx/dist * speed * dt
            self.position[2] += dz/dist * speed * dt
            self.rotation = np.arctan2(dz, dx)
            
    def _update_idle(self, dt: float):
        # Random chance to start walking
        if np.random.random() < 0.01:  # 1% chance per update
            self._start_random_walk()
            
    def _start_random_walk(self):
        # Generate a random path around current position
        num_points = np.random.randint(2, 5)
        self.walking_path = []
        current = self.position
        
        for _ in range(num_points):
            angle = np.random.random() * 2 * np.pi
            distance = np.random.uniform(5.0, 15.0)
            next_point = [
                current[0] + np.cos(angle) * distance,
                current[1],
                current[2] + np.sin(angle) * distance
            ]
            self.walking_path.append(tuple(next_point))
            current = next_point
            
        self.state = NPCState.WALKING

class NPCManager:
    def __init__(self):
        self.npcs: Dict[str, NPC] = {}
        self.npc_counter = 0
        
    def spawn_npcs_at_location(self, position: Tuple[float, float, float], count: int):
        """Spawn multiple NPCs around a given position"""
        for _ in range(count):
            # Random position within 10 units
            offset_x = np.random.uniform(-10.0, 10.0)
            offset_z = np.random.uniform(-10.0, 10.0)
            npc_pos = (
                position[0] + offset_x,
                position[1],
                position[2] + offset_z
            )
            
            # Random NPC type weighted towards villagers
            npc_type = np.random.choice(
                list(NPCType),
                p=[0.6, 0.2, 0.1, 0.1]  # Probability for each type
            )
            
            self.npc_counter += 1
            npc_id = f"npc_{self.npc_counter}"
            self.npcs[npc_id] = NPC(npc_id, npc_type, npc_pos)
            
    def update(self, dt: float):
        """Update all NPCs"""
        for npc in self.npcs.values():
            npc.update(dt)
            
    def get_nearby_npcs(self, position: Tuple[float, float, float], radius: float) -> List[NPC]:
        """Get all NPCs within radius of position"""
        nearby = []
        for npc in self.npcs.values():
            dx = npc.position[0] - position[0]
            dz = npc.position[2] - position[2]
            if (dx * dx + dz * dz) <= radius * radius:
                nearby.append(npc)
        return nearby