# src/engine/systems/tutorial_system.py
from typing import Dict, List, Optional
from dataclasses import dataclass
import json
from ..audio.sound_manager import SoundManager
from ..ui.ui_base import UIManager

@dataclass
class TutorialStep:
    step_id: str
    title: str
    description: str
    target_element: str
    completion_condition: str
    next_step: Optional[str]
    is_optional: bool = False

class TutorialSystem:
    def __init__(self, ui_manager: UIManager, sound_manager: SoundManager):
        self.ui_manager = ui_manager
        self.sound_manager = sound_manager
        self.steps: Dict[str, TutorialStep] = {}
        self.current_step: Optional[str] = None
        self.completed_steps: List[str] = []
        self._load_tutorial_data()

    def _load_tutorial_data(self):
        tutorial_data = {
            "city_basics": TutorialStep(
                "city_basics", "City Management",
                "Learn how to build and manage your city",
                "city_panel", "open_city_panel", "combat_basics"
            ),
            "combat_basics": TutorialStep(
                "combat_basics", "Combat System",
                "Master the basics of combat",
                "combat_area", "complete_training_fight", "world_exploration"
            ),
            "world_exploration": TutorialStep(
                "world_exploration", "World Exploration",
                "Discover the world around you",
                "world_map", "visit_first_location", None
            )
        }
        self.steps = tutorial_data

    def start_tutorial(self):
        self.current_step = "city_basics"
        self._show_current_step()

    def _show_current_step(self):
        if not self.current_step or self.current_step not in self.steps:
            return

        step = self.steps[self.current_step]
        self.ui_manager.show_tutorial_popup(
            step.title,
            step.description,
            step.target_element
        )
        self.sound_manager.play_ui_sound("tutorial_new")

    def complete_step(self, step_id: str):
        if step_id not in self.steps or step_id != self.current_step:
            return

        self.completed_steps.append(step_id)
        step = self.steps[step_id]
        
        self.sound_manager.play_ui_sound("tutorial_complete")
        
        if step.next_step:
            self.current_step = step.next_step
            self._show_current_step()
        else:
            self.current_step = None
            self.ui_manager.show_tutorial_completion()

    def is_tutorial_complete(self) -> bool:
        return len(self.completed_steps) == len(self.steps)

    def save_progress(self) -> dict:
        return {
            "completed_steps": self.completed_steps,
            "current_step": self.current_step
        }

    def load_progress(self, data: dict):
        self.completed_steps = data.get("completed_steps", [])
        self.current_step = data.get("current_step", None)
        if self.current_step:
            self._show_current_step()