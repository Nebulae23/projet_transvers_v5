# src/engine/ai/neural_network/layer.py
import numpy as np
from typing import Tuple

class Layer:
    def __init__(self, input_size: int, output_size: int):
        self.weights = np.random.randn(input_size, output_size) * 0.01
        self.biases = np.zeros((1, output_size))
        
        self.inputs = None
        self.outputs = None
        
    def forward(self, inputs: np.ndarray) -> np.ndarray:
        self.inputs = inputs
        self.outputs = np.dot(inputs, self.weights) + self.biases
        return self.relu(self.outputs)
        
    def backward(self, gradient: np.ndarray, learning_rate: float) -> np.ndarray:
        # Calculate gradients
        relu_gradient = self.relu_derivative(self.outputs)
        activated_gradient = gradient * relu_gradient
        
        # Calculate weight gradients
        weight_gradients = np.dot(self.inputs.T, activated_gradient)
        bias_gradients = np.sum(activated_gradient, axis=0, keepdims=True)
        
        # Calculate input gradients for next layer
        input_gradients = np.dot(activated_gradient, self.weights.T)
        
        # Update weights and biases
        self.weights -= learning_rate * weight_gradients
        self.biases -= learning_rate * bias_gradients
        
        return input_gradients
        
    @staticmethod
    def relu(x: np.ndarray) -> np.ndarray:
        return np.maximum(0, x)
        
    @staticmethod
    def relu_derivative(x: np.ndarray) -> np.ndarray:
        return np.where(x > 0, 1, 0)