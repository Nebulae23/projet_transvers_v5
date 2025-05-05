# src/engine/systems/achievement_system.py
from typing import Dict, List, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import json
from ..audio.sound_manager import SoundManager

class AchievementCategory(Enum):
    COMBAT = "combat"
    EXPLORATION = "exploration"
    CITY = "city"
    PROGRESSION = "progression"
    SPECIAL = "special"

@dataclass
class Achievement:
    id: str
    name: str
    description: str
    category: AchievementCategory
    icon_path: str
    condition: Callable[[], bool]
    reward: dict
    progress_max: int = 1
    secret: bool = False

class AchievementSystem:
    def __init__(self, sound_manager: SoundManager):
        self.sound_manager = sound_manager
        self.achievements: Dict[str, Achievement] = {}
        self.unlocked: Dict[str, bool] = {}
        self.progress: Dict[str, int] = {}
        self._load_achievements()

    def _load_achievements(self):
        # Combat achievements
        self.register_achievement(
            Achievement(
                "first_victory",
                "First Victory",
                "Win your first combat encounter",
                AchievementCategory.COMBAT,
                "assets/icons/achievements/first_victory.png",
                lambda: self._check_combat_victories() >= 1,
                {"exp": 100}
            )
        )
        # Add more achievements...

    def register_achievement(self, achievement: Achievement):
        self.achievements[achievement.id] = achievement
        if achievement.id not in self.progress:
            self.progress[achievement.id] = 0

    def update_progress(self, achievement_id: str, progress: int):
        if achievement_id not in self.achievements:
            return

        achievement = self.achievements[achievement_id]
        self.progress[achievement_id] = min(progress, achievement.progress_max)

        if (self.progress[achievement_id] >= achievement.progress_max and 
            not self.unlocked.get(achievement_id, False)):
            self.unlock_achievement(achievement_id)

    def unlock_achievement(self, achievement_id: str):
        if achievement_id not in self.achievements or self.unlocked.get(achievement_id, False):
            return

        achievement = self.achievements[achievement_id]
        self.unlocked[achievement_id] = True
        self.sound_manager.play_ui_sound("achievement_unlock")
        
        # Grant rewards
        self._grant_reward(achievement.reward)

    def _grant_reward(self, reward: dict):
        # Handle different reward types
        if "exp" in reward:
            self._grant_exp(reward["exp"])
        if "items" in reward:
            self._grant_items(reward["items"])

    def get_achievement_progress(self, achievement_id: str) -> tuple[int, int]:
        if achievement_id not in self.achievements:
            return (0, 0)
        return (self.progress[achievement_id], self.achievements[achievement_id].progress_max)

    def save_state(self) -> dict:
        return {
            "unlocked": self.unlocked,
            "progress": self.progress
        }

    def load_state(self, data: dict):
        self.unlocked = data.get("unlocked", {})
        self.progress = data.get("progress", {})