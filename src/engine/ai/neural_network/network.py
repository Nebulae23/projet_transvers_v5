# src/engine/ai/neural_network/network.py
import numpy as np
from typing import List, Tuple
from .layer import Layer

class NeuralNetwork:
    def __init__(self, layer_sizes: List[int]):
        self.layers = []
        self.learning_rate = 0.01
        
        # Initialize layers
        for i in range(len(layer_sizes) - 1):
            layer = Layer(
                input_size=layer_sizes[i],
                output_size=layer_sizes[i + 1]
            )
            self.layers.append(layer)
            
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        current_input = inputs
        
        for layer in self.layers:
            current_input = layer.forward(current_input)
            
        return current_input
        
    def backward(self, gradient: np.ndarray) -> None:
        current_gradient = gradient
        
        for layer in reversed(self.layers):
            current_gradient = layer.backward(
                current_gradient,
                self.learning_rate
            )
            
    def train(self, inputs: np.ndarray, targets: np.ndarray,
             epochs: int = 1000) -> List[float]:
        losses = []
        
        for epoch in range(epochs):
            # Forward pass
            outputs = self.forward(inputs)
            
            # Calculate loss
            loss = np.mean((outputs - targets) ** 2)
            losses.append(loss)
            
            # Backward pass
            gradient = 2 * (outputs - targets) / targets.shape[0]
            self.backward(gradient)
            
        return losses
        
    def predict(self, inputs: np.ndarray) -> np.ndarray:
        return self.forward(inputs)
        
    def save_weights(self, filename: str) -> None:
        weights = [layer.weights for layer in self.layers]
        biases = [layer.biases for layer in self.layers]
        np.savez(filename, weights=weights, biases=biases)
        
    def load_weights(self, filename: str) -> None:
        data = np.load(filename)
        weights = data['weights']
        biases = data['biases']
        
        for layer, w, b in zip(self.layers, weights, biases):
            layer.weights = w
            layer.biases = b