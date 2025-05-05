# src/engine/city/city_manager.py
from typing import Dict, List, Optional, Tuple
from .district import District
from .building import Building
from .resources import ResourceManager, ResourceType
from .defense import DefenseManager
from ..physics import CollisionSystem
from ..events import EventSystem

class CityManager:
    def __init__(self):
        self.districts: List[District] = []
        self.resource_manager = None  # Will be initialized by Game
        self.collision_system = CollisionSystem()
        self.defense_manager = DefenseManager(self.collision_system)
        self.event_system = None  # Will be initialized by Game
        
    def initialize(self):
        """Initialize systems that need other game components"""
        from ..time.time_manager import TimeManager
        # These will be passed in by the Game in a real implementation
        time_manager = TimeManager()
        self.resource_manager = ResourceManager(time_manager)
        from ..events.event_system import EventSystem
        self.event_system = EventSystem()
        
    def create_district(self, name: str, position: Tuple[float, float], 
                       size: Tuple[float, float]) -> Optional[District]:
        if self._can_place_district(position, size):
            district = District(name, position, size)
            self.districts.append(district)
            return district
        return None
        
    def add_building(self, district: District, building_type: str,
                    position: Tuple[float, float]) -> Optional[Building]:
        if district in self.districts and self._can_place_building(position):
            building = Building(building_type, position)
            district.buildings.append(building)
            return building
        return None
        
    def add_defense_tower(self, position: Tuple[float, float],
                         tower_type: str) -> bool:
        tower = self.defense_manager.add_tower(position, tower_type)
        return tower is not None
        
    def update(self, dt: float):
        # Update all systems
        if self.resource_manager:
            self.resource_manager.update(dt)
        for district in self.districts:
            district.update(dt)
        self.defense_manager.update(dt, self._get_enemies())
        self.collision_system.update(dt)
        if self.event_system:
            self.event_system.update(dt)
        
    def _can_place_district(self, position: Tuple[float, float],
                          size: Tuple[float, float]) -> bool:
        # Check for overlapping districts
        for district in self.districts:
            if self._check_overlap(position, size, 
                                 district.data.position, 
                                 district.data.size):
                return False
        return True
        
    def _can_place_building(self, position: Tuple[float, float]) -> bool:
        # Check building placement rules
        return True  # Implement actual checks based on game rules
        
    @staticmethod
    def _check_overlap(pos1: Tuple[float, float], size1: Tuple[float, float],
                      pos2: Tuple[float, float], size2: Tuple[float, float]) -> bool:
        return not (pos1[0] + size1[0] < pos2[0] or
                   pos1[0] > pos2[0] + size2[0] or
                   pos1[1] + size1[1] < pos2[1] or
                   pos1[1] > pos2[1] + size2[1])
                   
    def _get_enemies(self) -> List:
        # Get list of active enemies from game state
        return []  # Implement based on game state
        
    def render(self, renderer):
        """Render the city and its components"""
        # Render districts and buildings
        for district in self.districts:
            district.render(renderer)
        
        # Render defensive structures
        self.defense_manager.render(renderer)
        
    def cleanup(self):
        """Clean up any resources used by the city manager"""
        # Cleanup code goes here
        pass