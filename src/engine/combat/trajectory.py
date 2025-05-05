# src/engine/combat/trajectory.py
import numpy as np
from typing import Optional
from dataclasses import dataclass

@dataclass
class TrajectoryPattern:
    speed: float
    
    def calculate_velocity(self, current_pos: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        raise NotImplementedError("Subclasses must implement calculate_velocity")
        
    def calculate_initial_velocity(self, distance: float, angle: float) -> np.ndarray:
        raise NotImplementedError("Subclasses must implement calculate_initial_velocity")

class LinearTrajectory(TrajectoryPattern):
    def calculate_velocity(self, current_pos: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        direction = target_pos - current_pos
        if np.all(direction == 0):
            return np.zeros(2)
        return self.speed * direction / np.linalg.norm(direction)
        
    def calculate_initial_velocity(self, distance: float, angle: float) -> np.ndarray:
        return self.speed * np.array([np.cos(angle), np.sin(angle)])

class ArcingTrajectory(TrajectoryPattern):
    def __init__(self, speed: float, gravity: float):
        super().__init__(speed)
        self.gravity = gravity
        
    def calculate_velocity(self, current_pos: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        direction = target_pos - current_pos
        distance = np.linalg.norm(direction)
        angle = np.arctan2(direction[1], direction[0])
        return self.calculate_initial_velocity(distance, angle)
        
    def calculate_initial_velocity(self, distance: float, angle: float) -> np.ndarray:
        # Calculate initial velocity for projectile motion
        v0_x = self.speed * np.cos(angle)
        v0_y = self.speed * np.sin(angle)
        return np.array([v0_x, v0_y])

class HomingTrajectory(TrajectoryPattern):
    def __init__(self, speed: float, turn_rate: float):
        super().__init__(speed)
        self.turn_rate = turn_rate
        
    def calculate_velocity(self, current_pos: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        direction = target_pos - current_pos
        if np.all(direction == 0):
            return np.zeros(2)
            
        current_dir = direction / np.linalg.norm(direction)
        return self.speed * current_dir

class OrbitalTrajectory(TrajectoryPattern):
    def __init__(self, speed: float, radius: float, angular_speed: float):
        super().__init__(speed)
        self.radius = radius
        self.angular_speed = angular_speed
        self.angle = 0.0
        
    def calculate_velocity(self, current_pos: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        self.angle += self.angular_speed
        x = self.radius * np.cos(self.angle)
        y = self.radius * np.sin(self.angle)
        return self.speed * np.array([x, y])

class ZigzagTrajectory(TrajectoryPattern):
    def __init__(self, speed: float, amplitude: float, frequency: float):
        super().__init__(speed)
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0.0
        
    def calculate_velocity(self, current_pos: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        self.time += 0.016  # Assuming 60 FPS
        direction = target_pos - current_pos
        if np.all(direction == 0):
            return np.zeros(2)
            
        base_direction = direction / np.linalg.norm(direction)
        perpendicular = np.array([-base_direction[1], base_direction[0]])
        zigzag = perpendicular * self.amplitude * np.sin(self.time * self.frequency)
        
        return self.speed * (base_direction + zigzag)

class SpiralTrajectory(TrajectoryPattern):
    def __init__(self, speed: float, radius_growth: float, angular_speed: float):
        super().__init__(speed)
        self.radius_growth = radius_growth
        self.angular_speed = angular_speed
        self.time = 0.0
        
    def calculate_velocity(self, current_pos: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        self.time += 0.016
        radius = self.radius_growth * self.time
        angle = self.angular_speed * self.time
        
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        return self.speed * np.array([x, y])

class BouncingTrajectory(TrajectoryPattern):
    def __init__(self, speed: float, bounce_factor: float = 0.8):
        super().__init__(speed)
        self.bounce_factor = bounce_factor
        self.velocity = np.zeros(2)
        
    def calculate_velocity(self, current_pos: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        if np.all(self.velocity == 0):
            direction = target_pos - current_pos
            self.velocity = self.speed * direction / np.linalg.norm(direction)
            
        # Simple boundary check (assuming 1280x720 screen)
        if current_pos[0] <= 0 or current_pos[0] >= 1280:
            self.velocity[0] *= -self.bounce_factor
        if current_pos[1] <= 0 or current_pos[1] >= 720:
            self.velocity[1] *= -self.bounce_factor
            
        return self.velocity

class WaveTrajectory(TrajectoryPattern):
    def __init__(self, speed: float, amplitude: float, frequency: float):
        super().__init__(speed)
        self.amplitude = amplitude
        self.frequency = frequency
        self.time = 0.0
        
    def calculate_velocity(self, current_pos: np.ndarray, target_pos: np.ndarray) -> np.ndarray:
        self.time += 0.016
        direction = target_pos - current_pos
        if np.all(direction == 0):
            return np.zeros(2)
            
        base_direction = direction / np.linalg.norm(direction)
        perpendicular = np.array([-base_direction[1], base_direction[0]])
        wave = perpendicular * self.amplitude * np.sin(self.time * self.frequency)
        
        return self.speed * base_direction + wave