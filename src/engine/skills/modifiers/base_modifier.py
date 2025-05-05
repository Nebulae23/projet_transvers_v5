# src/engine/skills/modifiers/base_modifier.py
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseModifier(ABC):
    def __init__(self, name: str, power: float):
        self.name = name
        self.power = power
        self.duration = -1  # -1 for permanent
        
    @abstractmethod
    def apply(self, target: Any) -> None:
        pass
        
    @abstractmethod
    def remove(self, target: Any) -> None:
        pass
        
    def to_dict(self) -> Dict:
        return {
            'name': self.name,
            'power': self.power,
            'duration': self.duration,
            'type': self.__class__.__name__
        }
        
class StatModifier(BaseModifier):
    def __init__(self, name: str, stat: str, power: float):
        super().__init__(name, power)
        self.stat = stat
        self.original_value = None
        
    def apply(self, target: Any) -> None:
        if hasattr(target, 'stats'):
            self.original_value = getattr(target.stats, self.stat)
            setattr(target.stats, self.stat, 
                   self.original_value * (1 + self.power))
            
    def remove(self, target: Any) -> None:
        if self.original_value and hasattr(target, 'stats'):
            setattr(target.stats, self.stat, self.original_value)
            self.original_value = None
            
class ConditionalModifier(BaseModifier):
    def __init__(self, name: str, condition: str, power: float):
        super().__init__(name, power)
        self.condition = condition
        self.active = False
        
    def check_condition(self, target: Any) -> bool:
        # Example conditions
        if self.condition == 'low_health':
            return target.stats.health / target.stats.max_health < 0.3
        return False
        
    def apply(self, target: Any) -> None:
        if self.check_condition(target):
            self.active = True
            # Apply conditional buff
            
    def remove(self, target: Any) -> None:
        if self.active:
            self.active = False
            # Remove conditional buff