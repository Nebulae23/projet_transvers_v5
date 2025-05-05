# src/engine/physics.py
import numpy as np
from dataclasses import dataclass, field
from typing import List, Tuple

@dataclass
class VerletPoint:
    current_pos: np.ndarray
    old_pos: np.ndarray
    acceleration: np.ndarray = field(default_factory=lambda: np.zeros(2))
    
    def update(self, dt: float, gravity: np.ndarray = np.array([0, -9.81])):
        velocity = self.current_pos - self.old_pos
        self.old_pos = self.current_pos.copy()
        self.current_pos = self.current_pos + velocity + self.acceleration * dt * dt
        self.acceleration = gravity

class VerletStick:
    def __init__(self, p1: VerletPoint, p2: VerletPoint, length: float):
        self.p1 = p1
        self.p2 = p2
        self.length = length

    def update(self):
        diff = self.p2.current_pos - self.p1.current_pos
        dist = np.linalg.norm(diff)
        if dist == 0:
            return
        
        factor = (self.length - dist) / dist
        offset = diff * factor * 0.5
        
        self.p1.current_pos -= offset
        self.p2.current_pos += offset

class PhysicsSystem:
    def __init__(self):
        self.points: List[VerletPoint] = []
        self.sticks: List[VerletStick] = []
        self.gravity = np.array([0, -9.81])
        self.substeps = 8
        
    def add_point(self, pos: np.ndarray) -> VerletPoint:
        point = VerletPoint(pos.copy(), pos.copy())
        self.points.append(point)
        return point
        
    def add_stick(self, p1: VerletPoint, p2: VerletPoint) -> VerletStick:
        length = np.linalg.norm(p2.current_pos - p1.current_pos)
        stick = VerletStick(p1, p2, length)
        self.sticks.append(stick)
        return stick
        
    def update(self, dt: float):
        sub_dt = dt / self.substeps
        
        for _ in range(self.substeps):
            # Update points
            for point in self.points:
                point.update(sub_dt, self.gravity)
            
            # Update sticks
            for stick in self.sticks:
                stick.update()
                
            # Apply constraints (e.g., screen boundaries)
            self.apply_constraints()
    
    def apply_constraints(self):
        for point in self.points:
            # Example: Keep points within screen bounds
            point.current_pos[0] = np.clip(point.current_pos[0], 0, 1280)
            point.current_pos[1] = np.clip(point.current_pos[1], 0, 720)