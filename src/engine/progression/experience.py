# src/engine/progression/experience.py
from typing import Callable, List
from dataclasses import dataclass
from math import floor

@dataclass
class LevelThreshold:
    level: int
    xp_required: int
    rewards: List[str]  # List of reward identifiers

class ExperienceSystem:
    def __init__(self):
        self.current_xp = 0
        self.current_level = 1
        self.level_thresholds: List[LevelThreshold] = []
        self.on_level_up: List[Callable[[int], None]] = []
        self._initialize_thresholds()
        
    def _initialize_thresholds(self):
        """Initialize level thresholds with exponential scaling"""
        base_xp = 100
        scale_factor = 1.5
        
        for level in range(1, 51):  # Max level 50
            xp_required = floor(base_xp * (scale_factor ** (level - 1)))
            rewards = [f"stat_point_{level}", f"skill_point_{level}"]
            
            if level % 5 == 0:  # Special rewards every 5 levels
                rewards.append(f"special_reward_{level}")
                
            self.level_thresholds.append(LevelThreshold(level, xp_required, rewards))
            
    def add_experience(self, amount: int) -> List[LevelThreshold]:
        """Add experience and return list of levels gained"""
        if amount <= 0:
            return []
            
        self.current_xp += amount
        levels_gained = []
        
        while True:
            next_threshold = self._get_next_threshold()
            if not next_threshold or self.current_xp < next_threshold.xp_required:
                break
                
            self.current_level += 1
            levels_gained.append(next_threshold)
            
            # Notify listeners
            for callback in self.on_level_up:
                callback(self.current_level)
                
        return levels_gained
        
    def _get_next_threshold(self) -> LevelThreshold:
        if self.current_level >= len(self.level_thresholds):
            return None
        return self.level_thresholds[self.current_level]
        
    def get_progress_to_next_level(self) -> float:
        """Return progress to next level as percentage (0-1)"""
        next_threshold = self._get_next_threshold()
        if not next_threshold:
            return 1.0
            
        prev_xp = self.level_thresholds[self.current_level - 1].xp_required
        progress = (self.current_xp - prev_xp) / (next_threshold.xp_required - prev_xp)
        return min(1.0, max(0.0, progress))
        
    def register_level_up_callback(self, callback: Callable[[int], None]):
        self.on_level_up.append(callback)