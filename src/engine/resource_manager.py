#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Resource Manager for Nightfall Defenders
"""

import os
import json
from panda3d.core import (
    Texture, TextureStage, 
    PNMImage, Filename, 
    SamplerState, LoaderOptions
)

class ResourceManager:
    """
    Manages loading and caching of game resources
    including textures, models, audio, and config files
    """
    
    def __init__(self, game):
        """Initialize the resource manager"""
        self.game = game
        self.loader = game.loader
        
        # Cache for loaded resources
        self.textures = {}
        self.models = {}
        self.sounds = {}
        self.shaders = {}
        self.config_files = {}
        
        # Asset directories
        self.asset_dir = os.path.join("src", "assets")
        self.generated_dir = os.path.join(self.asset_dir, "generated")
        self.shader_dir = os.path.join(self.asset_dir, "shaders")
        self.config_dir = os.path.join(self.asset_dir, "configs")
        self.sound_dir = os.path.join(self.asset_dir, "sounds")
        
        # Ensure directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = [
            self.asset_dir,
            self.generated_dir,
            self.shader_dir,
            self.config_dir,
            self.sound_dir,
            os.path.join(self.generated_dir, "characters"),
            os.path.join(self.generated_dir, "environment"),
            os.path.join(self.generated_dir, "effects"),
            os.path.join(self.generated_dir, "ui")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def load_texture(self, texture_path, minfilter=SamplerState.FT_linear, magfilter=SamplerState.FT_linear):
        """
        Load a texture from file or cache
        
        Args:
            texture_path (str): Path to the texture file
            minfilter (int): Minification filter
            magfilter (int): Magnification filter
            
        Returns:
            Texture: The loaded texture
        """
        # Check if texture is already loaded
        if texture_path in self.textures:
            return self.textures[texture_path]
        
        # Load the texture
        full_path = os.path.join(self.asset_dir, texture_path)
        texture = self.loader.loadTexture(full_path)
        
        if texture:
            # Configure texture settings
            texture.setMinfilter(minfilter)
            texture.setMagfilter(magfilter)
            
            # Cache the texture
            self.textures[texture_path] = texture
            return texture
        
        print(f"Failed to load texture: {texture_path}")
        return None
    
    def load_model(self, model_path):
        """
        Load a model from file or cache
        
        Args:
            model_path (str): Path to the model file
            
        Returns:
            NodePath: The loaded model
        """
        # Check if model is already loaded
        if model_path in self.models:
            return self.models[model_path].copyTo(self.game.render)
        
        # Load the model
        full_path = os.path.join(self.asset_dir, model_path)
        model = self.loader.loadModel(full_path)
        
        if model:
            # Cache the model
            self.models[model_path] = model
            return model.copyTo(self.game.render)
        
        print(f"Failed to load model: {model_path}")
        return None
    
    def load_shader(self, vertex_path, fragment_path):
        """
        Load a shader program
        
        Args:
            vertex_path (str): Path to the vertex shader
            fragment_path (str): Path to the fragment shader
            
        Returns:
            Shader: The loaded shader
        """
        shader_key = f"{vertex_path}:{fragment_path}"
        
        # Check if shader is already loaded
        if shader_key in self.shaders:
            return self.shaders[shader_key]
        
        # Load the shader
        vertex_path = os.path.join(self.shader_dir, vertex_path)
        fragment_path = os.path.join(self.shader_dir, fragment_path)
        
        shader = self.loader.loadShader(vertex_path, fragment_path)
        
        if shader:
            # Cache the shader
            self.shaders[shader_key] = shader
            return shader
        
        print(f"Failed to load shader: {vertex_path}, {fragment_path}")
        return None
    
    def load_sound(self, sound_path, volume=1.0, looping=False):
        """
        Load a sound from file or cache
        
        Args:
            sound_path (str): Path to the sound file
            volume (float): Volume level (0.0 to 1.0)
            looping (bool): Whether to loop the sound
            
        Returns:
            AudioSound: The loaded sound
        """
        # Check if sound is already loaded
        if sound_path in self.sounds:
            sound = self.sounds[sound_path]
            sound.setVolume(volume)
            sound.setLoop(looping)
            return sound
        
        # Load the sound
        full_path = os.path.join(self.sound_dir, sound_path)
        sound = self.loader.loadSfx(full_path)
        
        if sound:
            sound.setVolume(volume)
            sound.setLoop(looping)
            
            # Cache the sound
            self.sounds[sound_path] = sound
            return sound
        
        print(f"Failed to load sound: {sound_path}")
        return None
    
    def load_config(self, config_path):
        """
        Load a JSON configuration file
        
        Args:
            config_path (str): Path to the config file
            
        Returns:
            dict: The loaded configuration
        """
        # Check if config is already loaded
        if config_path in self.config_files:
            return self.config_files[config_path]
        
        # Load the config
        full_path = os.path.join(self.config_dir, config_path)
        
        try:
            with open(full_path, 'r') as f:
                config = json.load(f)
            
            # Cache the config
            self.config_files[config_path] = config
            return config
        except Exception as e:
            print(f"Failed to load config: {config_path} - {e}")
            return None
    
    def create_empty_texture(self, width, height, color=(1, 1, 1, 1)):
        """
        Create an empty texture with a solid color
        
        Args:
            width (int): Texture width
            height (int): Texture height
            color (tuple): RGBA color values (0.0 to 1.0)
            
        Returns:
            Texture: The created texture
        """
        texture = Texture()
        image = PNMImage(width, height)
        image.fill(color[0], color[1], color[2])
        image.alphaFill(color[3])
        texture.load(image)
        return texture 