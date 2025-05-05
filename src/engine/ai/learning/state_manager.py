# src/engine/ai/learning/state_manager.py
from typing import Dict, List, Any
import numpy as np

class StateManager:
    def __init__(self, state_size: int):
        self.state_size = state_size
        self.current_state = np.zeros(state_size)
        self.state_history = []
        self.transition_matrix = {}
        
    def update_state(self, new_state: np.ndarray) -> None:
        self.state_history.append(self.current_state.copy())
        self.current_state = new_state
        
        # Update transition matrix
        state_key = tuple(self.current_state)
        if len(self.state_history) > 0:
            prev_key = tuple(self.state_history[-1])
            if prev_key not in self.transition_matrix:
                self.transition_matrix[prev_key] = {}
            if state_key not in self.transition_matrix[prev_key]:
                self.transition_matrix[prev_key][state_key] = 0
            self.transition_matrix[prev_key][state_key] += 1
            
    def get_state_features(self) -> np.ndarray:
        return np.array([
            self._calculate_state_stability(),
            self._calculate_state_predictability(),
            self._calculate_state_novelty()
        ])
        
    def _calculate_state_stability(self) -> float:
        if len(self.state_history) < 2:
            return 1.0
            
        changes = np.abs(
            self.current_state - self.state_history[-1]
        ).mean()
        return 1.0 - min(changes, 1.0)
        
    def _calculate_state_predictability(self) -> float:
        if len(self.state_history) < 10:
            return 0.5
            
        prev_key = tuple(self.state_history[-1])
        if prev_key not in self.transition_matrix:
            return 0.0
            
        transitions = self.transition_matrix[prev_key]
        total = sum(transitions.values())
        current_key = tuple(self.current_state)
        
        return transitions.get(current_key, 0) / total
        
    def _calculate_state_novelty(self) -> float:
        if len(self.state_history) < 1:
            return 1.0
            
        state_key = tuple(self.current_state)
        times_seen = sum(
            1 for state in self.state_history 
            if tuple(state) == state_key
        )
        
        return 1.0 / (1.0 + times_seen)
        
    def get_transition_probability(self, 
                                 from_state: np.ndarray,
                                 to_state: np.ndarray) -> float:
        from_key = tuple(from_state)
        to_key = tuple(to_state)
        
        if from_key not in self.transition_matrix:
            return 0.0
            
        transitions = self.transition_matrix[from_key]
        total = sum(transitions.values())
        
        return transitions.get(to_key, 0) / total if total > 0 else 0.0