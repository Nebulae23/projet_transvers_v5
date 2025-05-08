#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Camera Controller for Nightfall Defenders
Manages the camera movement and behavior
"""

import math
from panda3d.core import Vec3, Point3, LVector3

# Import local modules - we need to handle the case when it's run directly
import os
import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.abspath(os.path.join(current_dir, '..'))
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from engine.entity import TransformComponent

class CameraController:
    """
    Controls the game camera
    
    Supports different camera modes:
    - Follow: Camera follows a target entity
    - Free: Camera can be moved freely by the player
    - Fixed: Camera is fixed at a position looking at a target
    """
    
    def __init__(self, game):
        """
        Initialize the camera controller
        
        Args:
            game: The main game instance
        """
        self.game = game
        self.camera = game.camera
        
        # Camera settings
        self.default_distance = 10.0  # Distance from target
        self.min_distance = 5.0
        self.max_distance = 20.0
        self.height = 8.0  # Camera height above ground
        self.pitch = -45  # Camera pitch in degrees (negative = looking down)
        self.follow_speed = 2.0  # Camera follow smoothing
        self.move_speed = 10.0  # Free camera move speed
        
        # Camera mode
        self.modes = ["follow", "free", "fixed"]
        self.current_mode = "free"  # Default to free camera for testing
        
        # Camera targets
        self.target = None  # Entity or node to follow/look at
        
        # Camera state
        self.distance = self.default_distance
        self.position = Vec3(0, 0, self.height)
        self.desired_position = Vec3(0, 0, self.height)
        
        # Initialize the camera position
        self.reset_camera()
    
    def reset_camera(self):
        """Reset the camera to default position and orientation"""
        # Set initial camera position
        self.camera.setPos(0, -self.distance, self.height)
        self.camera.lookAt(0, 0, 0)
        self.camera.setP(self.pitch)
        
        self.position = self.camera.getPos()
        self.desired_position = self.position
    
    def set_mode(self, mode):
        """
        Set the camera mode
        
        Args:
            mode (str): The camera mode to set ('follow', 'free', or 'fixed')
        """
        if mode in self.modes:
            self.current_mode = mode
            print(f"Camera mode set to: {mode}")
        else:
            print(f"Invalid camera mode: {mode}")
    
    def set_target(self, target):
        """
        Set the target for the camera to follow or look at
        
        Args:
            target: The entity or node to follow/look at
        """
        self.target = target
        
        # If we're setting a target, switch to follow mode
        if target and self.current_mode != "follow":
            self.set_mode("follow")
    
    def set_follow_target(self, target):
        """
        Set the entity for the camera to follow (legacy method)
        
        Args:
            target: The entity to follow
        """
        self.set_target(target)
    
    def set_look_target(self, target):
        """
        Set the point or entity for the camera to look at (legacy method)
        
        Args:
            target: The point or entity to look at
        """
        self.set_target(target)
    
    def move_camera(self, direction, dt):
        """
        Move the camera in a direction (used in free mode)
        
        Args:
            direction (str): Direction to move ('forward', 'backward', 'left', 'right')
            dt (float): Delta time since last update
        """
        if self.current_mode != "free":
            return
        
        move_vec = Vec3(0, 0, 0)
        
        # Calculate movement vector relative to camera orientation
        heading = self.camera.getH() % 360
        
        # Forward/backward movement
        if direction in ["forward", "backward"]:
            # Forward vector is along Y axis at heading angle
            forwardVec = LVector3(
                -math.sin(math.radians(heading)), 
                math.cos(math.radians(heading)), 
                0
            )
            
            if direction == "forward":
                move_vec += forwardVec
            else:  # backward
                move_vec -= forwardVec
        
        # Left/right movement
        if direction in ["left", "right"]:
            # Right vector is perpendicular to forward
            rightVec = LVector3(
                math.cos(math.radians(heading)),
                math.sin(math.radians(heading)),
                0
            )
            
            if direction == "right":
                move_vec += rightVec
            else:  # left
                move_vec -= rightVec
        
        # Apply movement with speed
        move_vec.normalize()
        move_distance = self.move_speed * dt
        self.desired_position += move_vec * move_distance
    
    def zoom_camera(self, amount):
        """
        Zoom the camera in or out
        
        Args:
            amount (float): Amount to zoom (positive = zoom in, negative = zoom out)
        """
        self.distance = max(self.min_distance, min(self.max_distance, self.distance - amount))
        
        if self.current_mode == "free":
            # In free mode, move camera forward/backward along its forward axis
            forward = self.camera.getMat().getRow3(1)
            self.desired_position += forward * amount
    
    def update(self, dt):
        """
        Update the camera
        
        Args:
            dt (float): Delta time since last update
        """
        if self.current_mode == "follow" and self.target:
            # Get target position
            target_pos = None
            
            # First check if it's a NodePath
            if hasattr(self.target, "getPos"):
                target_pos = self.target.getPos()
            # Then check if it's an entity with a position attribute
            elif hasattr(self.target, "position"):
                target_pos = self.target.position
            # Otherwise try to get root node from entity
            elif hasattr(self.target, "root") and hasattr(self.target.root, "getPos"):
                target_pos = self.target.root.getPos()
                
            if target_pos is None:
                # No valid position found, use origin as fallback
                target_pos = Point3(0, 0, 0)
                
            # Calculate desired camera position behind the target
            offset = Vec3(0, -self.distance, self.height)
            
            # If the entity/node has a heading, position camera behind it
            heading = 0
            if hasattr(self.target, "getH"):
                heading = self.target.getH()
            elif hasattr(self.target, "facing_angle"):
                heading = self.target.facing_angle
            elif hasattr(self.target, "root") and hasattr(self.target.root, "getH"):
                heading = self.target.root.getH()
            
            # Convert heading to radians
            heading_rad = math.radians(heading)
            
            # Calculate offset based on heading
            offset = Vec3(
                -math.sin(heading_rad) * self.distance,
                -math.cos(heading_rad) * self.distance,
                self.height
            )
            
            # Set the desired position behind the target
            self.desired_position = target_pos + offset
            
            # Look at the target
            look_at_pos = Point3(target_pos)
            
            # Smoothly interpolate to the desired position
            self.position = self.position + (self.desired_position - self.position) * min(dt * self.follow_speed, 1.0)
            
            # Update camera position and orientation
            self.camera.setPos(self.position)
            self.camera.lookAt(look_at_pos)
            self.camera.setP(self.pitch)
        
        elif self.current_mode == "free":
            # In free mode, smoothly move to desired position
            self.position = self.position + (self.desired_position - self.position) * min(dt * self.follow_speed, 1.0)
            self.camera.setPos(self.position)
            
            # If we have a target, look at it
            if self.target:
                if hasattr(self.target, "getPos"):
                    # It's a NodePath or similar
                    self.camera.lookAt(self.target)
                elif hasattr(self.target, "position"):
                    # It's an entity with position
                    self.camera.lookAt(self.target.position)
                elif hasattr(self.target, "root") and hasattr(self.target.root, "getPos"):
                    # It has a root node
                    self.camera.lookAt(self.target.root)
            
            # Always maintain the pitch
            self.camera.setP(self.pitch)
        
        elif self.current_mode == "fixed":
            # Fixed mode - camera stays at a specific position
            # Useful for cutscenes or specific game areas
            if self.target:
                if hasattr(self.target, "getPos"):
                    self.camera.lookAt(self.target)
                elif hasattr(self.target, "position"):
                    self.camera.lookAt(self.target.position)
                elif hasattr(self.target, "root") and hasattr(self.target.root, "getPos"):
                    self.camera.lookAt(self.target.root)
    
    def process_input(self, input_manager, dt):
        """
        Process input for camera control
        
        Args:
            input_manager: The game's input manager
            dt (float): Delta time since last update
        """
        # Only process input in free mode
        if self.current_mode != "free":
            return
        
        # Get movement vector from input manager
        move_vector = input_manager.get_movement_vector()
        
        # Apply movement
        if move_vector[1] > 0:  # Forward
            self.move_camera("forward", dt)
        elif move_vector[1] < 0:  # Backward
            self.move_camera("backward", dt)
            
        if move_vector[0] < 0:  # Left
            self.move_camera("left", dt)
        elif move_vector[0] > 0:  # Right
            self.move_camera("right", dt)
        
        # Mouse movement for rotation is handled in the game's task
        # Zoom is typically handled via mouse wheel elsewhere 