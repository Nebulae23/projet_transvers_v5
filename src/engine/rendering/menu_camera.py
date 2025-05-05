# src/engine/rendering/menu_camera.py
from typing import Optional, Tuple
import math
import numpy as np
from dataclasses import dataclass
from enum import Enum

@dataclass
class POIPoint:
    position: np.ndarray
    target: np.ndarray
    transition_time: float = 2.0
    hold_time: float = 5.0

class CameraState(Enum):
    TRANSITIONING = "transitioning"
    HOLDING = "holding"
    IDLE = "idle"

class MenuCamera:
    def __init__(self, initial_position: Tuple[float, float, float] = (0, 10, 0)):
        self.position = np.array(initial_position, dtype=float)
        self.target = np.array([0, 0, 0], dtype=float)
        self.up = np.array([0, 1, 0], dtype=float)
        
        # Camera movement parameters
        self.transition_state = CameraState.IDLE
        self.transition_timer = 0.0
        self.hold_timer = 0.0
        
        # POI queue for showcase
        self.points_of_interest: list[POIPoint] = []
        self.current_poi: Optional[POIPoint] = None
        
        # Smoothing parameters
        self.position_smoothing = 0.1
        self.target_smoothing = 0.15
        
    def add_poi(self, poi: POIPoint) -> None:
        self.points_of_interest.append(poi)
        
    def update(self, delta_time: float) -> None:
        if self.transition_state == CameraState.IDLE:
            if self.points_of_interest and not self.current_poi:
                self.current_poi = self.points_of_interest.pop(0)
                self.transition_state = CameraState.TRANSITIONING
                self.transition_timer = 0.0
                
        elif self.transition_state == CameraState.TRANSITIONING:
            self.transition_timer += delta_time
            progress = min(1.0, self.transition_timer / self.current_poi.transition_time)
            
            # Smooth interpolation
            self.position = self._smooth_lerp(
                self.position,
                self.current_poi.position,
                progress,
                self.position_smoothing
            )
            
            self.target = self._smooth_lerp(
                self.target,
                self.current_poi.target,
                progress,
                self.target_smoothing
            )
            
            if progress >= 1.0:
                self.transition_state = CameraState.HOLDING
                self.hold_timer = 0.0
                
        elif self.transition_state == CameraState.HOLDING:
            self.hold_timer += delta_time
            
            # Add subtle movement during hold
            self._apply_ambient_movement(delta_time)
            
            if self.hold_timer >= self.current_poi.hold_time:
                self.transition_state = CameraState.IDLE
                self.current_poi = None
                
    def _smooth_lerp(self, start: np.ndarray, end: np.ndarray, 
                    progress: float, smoothing: float) -> np.ndarray:
        # Smooth step function
        progress = progress * progress * (3 - 2 * progress)
        
        # Apply additional smoothing
        smooth_progress = 1.0 - math.exp(-progress / smoothing)
        
        return start + (end - start) * smooth_progress
        
    def _apply_ambient_movement(self, delta_time: float) -> None:
        # Add subtle floating motion
        time_scale = delta_time * 0.5
        self.position[1] += math.sin(self.hold_timer) * 0.01 * time_scale
        self.position[0] += math.cos(self.hold_timer * 0.7) * 0.005 * time_scale
        
    def get_view_matrix(self) -> np.ndarray:
        # Create view matrix
        z_axis = self.target - self.position
        z_axis = z_axis / np.linalg.norm(z_axis)
        
        x_axis = np.cross(self.up, z_axis)
        x_axis = x_axis / np.linalg.norm(x_axis)
        
        y_axis = np.cross(z_axis, x_axis)
        
        view_matrix = np.eye(4)
        view_matrix[:3, 0] = x_axis
        view_matrix[:3, 1] = y_axis
        view_matrix[:3, 2] = z_axis
        view_matrix[:3, 3] = -self.position
        
        return view_matrix