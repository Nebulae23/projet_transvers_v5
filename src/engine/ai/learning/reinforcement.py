# src/engine/ai/learning/reinforcement.py
import numpy as np
from typing import Dict, List, Tuple
from collections import deque
import random

class ReinforcementLearning:
    def __init__(self, state_size: int, action_size: int):
        self.state_size = state_size
        self.action_size = action_size
        
        # Hyperparameters
        self.gamma = 0.95    # discount rate
        self.epsilon = 1.0   # exploration rate
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.995
        self.learning_rate = 0.001
        
        # Memory for experience replay
        self.memory = deque(maxlen=2000)
        
        # Neural network for Q-learning
        self.model = self._build_model()
        
    def _build_model(self):
        from ..neural_network.network import NeuralNetwork
        return NeuralNetwork([
            self.state_size,
            24,
            24,
            self.action_size
        ])
        
    def remember(self, state: np.ndarray, action: int, 
                reward: float, next_state: np.ndarray, done: bool) -> None:
        self.memory.append((state, action, reward, next_state, done))
        
    def act(self, state: np.ndarray) -> int:
        if np.random.rand() <= self.epsilon:
            return random.randrange(self.action_size)
            
        state = np.reshape(state, [1, self.state_size])
        act_values = self.model.predict(state)
        return np.argmax(act_values[0])
        
    def replay(self, batch_size: int) -> float:
        if len(self.memory) < batch_size:
            return 0
            
        minibatch = random.sample(self.memory, batch_size)
        total_loss = 0
        
        for state, action, reward, next_state, done in minibatch:
            target = reward
            if not done:
                next_state = np.reshape(next_state, [1, self.state_size])
                target = reward + self.gamma * np.amax(
                    self.model.predict(next_state)[0]
                )
                
            state = np.reshape(state, [1, self.state_size])
            target_f = self.model.predict(state)
            target_f[0][action] = target
            
            # Train the model
            loss = self.model.train(state, target_f, epochs=1)
            total_loss += loss[0]
            
        # Decay epsilon
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay
            
        return total_loss / batch_size
        
    def save(self, filename: str) -> None:
        self.model.save_weights(filename)
        
    def load(self, filename: str) -> None:
        self.model.load_weights(filename)