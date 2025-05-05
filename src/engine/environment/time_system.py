# src/engine/environment/time_system.py
from enum import Enum
from engine.ecs.system import System

class TimePhase(Enum):
    DAWN = 0    # 6:00  - 8:00
    DAY = 1     # 8:00  - 18:00
    DUSK = 2    # 18:00 - 20:00
    NIGHT = 3   # 20:00 - 6:00

class TimeSystem(System):
    MINUTES_PER_TICK = 1  # Each tick represents 1 minute
    
    def __init__(self, start_hour=6):
        self.minutes = start_hour * 60
        self.day_count = 1
        self.subscribers = []  # Systems that need time updates
        
    def get_current_hour(self):
        return (self.minutes // 60) % 24
    
    def get_current_phase(self):
        hour = self.get_current_hour()
        if 6 <= hour < 8:
            return TimePhase.DAWN
        elif 8 <= hour < 18:
            return TimePhase.DAY
        elif 18 <= hour < 20:
            return TimePhase.DUSK
        else:
            return TimePhase.NIGHT
            
    def subscribe(self, system):
        if system not in self.subscribers:
            self.subscribers.append(system)
            
    def update(self, dt, entities):
        # Advance time (assume dt is in seconds)
        real_minutes = (dt / 3600.0) * 1440  # Convert game time to minutes
        self.minutes += real_minutes * self.MINUTES_PER_TICK
        
        # Handle day rollover
        if self.minutes >= 1440:  # 24 hours * 60 minutes
            self.minutes %= 1440
            self.day_count += 1
            
        # Notify subscribers of time change
        current_phase = self.get_current_phase()
        for system in self.subscribers:
            system.on_time_update(current_phase, self.get_current_hour(), self.minutes)