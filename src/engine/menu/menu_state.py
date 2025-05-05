# src/engine/menu/menu_state.py
from enum import Enum, auto
from dataclasses import dataclass
from typing import Optional, Dict, Any

class MenuStateType(Enum):
    MAIN = auto()
    OPTIONS = auto()
    LOAD_GAME = auto()
    NEW_GAME = auto()
    CREDITS = auto()
    TRANSITIONING = auto()

@dataclass
class TransitionData:
    source: MenuStateType
    target: MenuStateType
    progress: float = 0.0
    duration: float = 0.5

class MenuState:
    def __init__(self):
        self.current = MenuStateType.MAIN
        self.previous = MenuStateType.MAIN
        self.transition: Optional[TransitionData] = None
        
        # State-specific data
        self.state_data: Dict[MenuStateType, Dict[str, Any]] = {
            MenuStateType.MAIN: {},
            MenuStateType.OPTIONS: {
                "selected_tab": "graphics",
                "settings": {
                    "graphics": {
                        "resolution": "1920x1080",
                        "quality": "high",
                        "vsync": True
                    },
                    "audio": {
                        "master": 0.8,
                        "music": 0.7,
                        "effects": 0.9
                    },
                    "gameplay": {
                        "difficulty": "normal",
                        "tutorials": True,
                        "auto_save": True
                    }
                }
            },
            MenuStateType.LOAD_GAME: {
                "selected_save": None,
                "save_list": []
            },
            MenuStateType.NEW_GAME: {
                "character_class": None,
                "difficulty": "normal",
                "world_seed": None
            },
            MenuStateType.CREDITS: {
                "scroll_position": 0.0
            }
        }
        
    def transition_to(self, target: MenuStateType,
                     duration: float = 0.5) -> None:
        if self.transition is None:
            self.previous = self.current
            self.transition = TransitionData(
                source=self.current,
                target=target,
                duration=duration
            )
            
    def update(self, delta_time: float) -> None:
        if self.transition:
            self.transition.progress += delta_time / self.transition.duration
            
            if self.transition.progress >= 1.0:
                self.current = self.transition.target
                self.transition = None
                
    def get_transition_alpha(self) -> float:
        if not self.transition:
            return 0.0
            
        # Smooth step function for transition
        t = self.transition.progress
        return t * t * (3 - 2 * t)
        
    def get_current_data(self) -> Dict[str, Any]:
        return self.state_data[self.current]
        
    def set_state_data(self, state: MenuStateType,
                      key: str, value: Any) -> None:
        if state in self.state_data:
            self.state_data[state][key] = value
            
    def get_state_data(self, state: MenuStateType,
                      key: str) -> Optional[Any]:
        if state in self.state_data and key in self.state_data[state]:
            return self.state_data[state][key]
        return None