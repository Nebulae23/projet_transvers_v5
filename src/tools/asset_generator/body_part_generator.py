#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Body Part Generator for Nightfall Defenders
Procedurally generates character body parts for physics-based animation
"""

import random
import math
from enum import Enum
from typing import Dict, List, Tuple, Optional

class CharacterClass(Enum):
    """Available character classes"""
    WARRIOR = "warrior"
    MAGE = "mage"
    CLERIC = "cleric"
    ALCHEMIST = "alchemist"
    RANGER = "ranger"
    SUMMONER = "summoner"

class BodyPartType(Enum):
    """Types of body parts that can be generated"""
    HEAD = "head"
    TORSO = "torso"
    UPPER_ARM = "upper_arm"
    LOWER_ARM = "lower_arm"
    HAND = "hand"
    UPPER_LEG = "upper_leg"
    LOWER_LEG = "lower_leg"
    FOOT = "foot"
    ACCESSORY = "accessory"
    WEAPON = "weapon"

class BodyPartGenerator:
    """Generates procedural body parts for physics-based animation"""
    
    def __init__(self):
        """Initialize the body part generator"""
        # Body proportion templates for different character classes
        self.class_proportions = {
            CharacterClass.WARRIOR: {
                "head_size": 0.15,
                "torso_length": 0.35,
                "arm_length": 0.32,
                "leg_length": 0.45,
                "shoulder_width": 0.25,
                "hip_width": 0.2,
                "muscle_mass": 1.2,
                "joint_stiffness": 0.8
            },
            CharacterClass.MAGE: {
                "head_size": 0.16,
                "torso_length": 0.33,
                "arm_length": 0.3,
                "leg_length": 0.43,
                "shoulder_width": 0.22,
                "hip_width": 0.18,
                "muscle_mass": 0.9,
                "joint_stiffness": 0.7
            },
            CharacterClass.CLERIC: {
                "head_size": 0.16,
                "torso_length": 0.34,
                "arm_length": 0.31,
                "leg_length": 0.44,
                "shoulder_width": 0.23,
                "hip_width": 0.19,
                "muscle_mass": 1.0,
                "joint_stiffness": 0.75
            },
            CharacterClass.ALCHEMIST: {
                "head_size": 0.17,
                "torso_length": 0.32,
                "arm_length": 0.33,
                "leg_length": 0.42,
                "shoulder_width": 0.21,
                "hip_width": 0.18,
                "muscle_mass": 0.9,
                "joint_stiffness": 0.7
            },
            CharacterClass.RANGER: {
                "head_size": 0.15,
                "torso_length": 0.33,
                "arm_length": 0.32,
                "leg_length": 0.46,
                "shoulder_width": 0.22,
                "hip_width": 0.18,
                "muscle_mass": 1.0,
                "joint_stiffness": 0.75
            },
            CharacterClass.SUMMONER: {
                "head_size": 0.16,
                "torso_length": 0.32,
                "arm_length": 0.3,
                "leg_length": 0.43,
                "shoulder_width": 0.21,
                "hip_width": 0.18,
                "muscle_mass": 0.85,
                "joint_stiffness": 0.65
            }
        }
        
        # Visual properties for different character classes
        self.class_visuals = {
            CharacterClass.WARRIOR: {
                "head_color": (180, 150, 120, 255),
                "torso_color": (180, 30, 30, 255),  # Red for warrior
                "limb_color": (50, 50, 50, 255),
                "accessory_color": (150, 120, 50, 255)
            },
            CharacterClass.MAGE: {
                "head_color": (180, 150, 120, 255),
                "torso_color": (50, 50, 180, 255),  # Blue for mage
                "limb_color": (70, 70, 100, 255),
                "accessory_color": (120, 80, 160, 255)
            },
            CharacterClass.CLERIC: {
                "head_color": (180, 150, 120, 255),
                "torso_color": (180, 180, 180, 255),  # White for cleric
                "limb_color": (80, 80, 80, 255),
                "accessory_color": (200, 180, 100, 255)
            },
            CharacterClass.ALCHEMIST: {
                "head_color": (180, 150, 120, 255),
                "torso_color": (80, 140, 80, 255),  # Green for alchemist
                "limb_color": (60, 90, 60, 255),
                "accessory_color": (140, 100, 50, 255)
            },
            CharacterClass.RANGER: {
                "head_color": (180, 150, 120, 255),
                "torso_color": (80, 120, 50, 255),  # Forest green for ranger
                "limb_color": (60, 70, 40, 255),
                "accessory_color": (100, 80, 60, 255)
            },
            CharacterClass.SUMMONER: {
                "head_color": (180, 150, 120, 255),
                "torso_color": (140, 80, 160, 255),  # Purple for summoner
                "limb_color": (80, 60, 100, 255),
                "accessory_color": (160, 140, 180, 255)
            }
        }
    
    def generate_character_model(self, character_class: str, height: float, variation_seed: Optional[int] = None) -> Dict:
        """
        Generate a full character model with all body parts
        
        Args:
            character_class: Character class name
            height: Total character height in units
            variation_seed: Seed for random variations
            
        Returns:
            Dictionary with character model data for verlet simulation
        """
        # Set seed if provided
        if variation_seed is not None:
            random.seed(variation_seed)
        
        # Convert string to enum if needed
        if isinstance(character_class, str):
            try:
                character_class = CharacterClass(character_class)
            except ValueError:
                character_class = CharacterClass.WARRIOR  # Default
        
        # Get class-specific proportions
        proportions = self.class_proportions.get(character_class, self.class_proportions[CharacterClass.WARRIOR])
        visuals = self.class_visuals.get(character_class, self.class_visuals[CharacterClass.WARRIOR])
        
        # Apply small random variations to proportions
        for key in proportions:
            proportions[key] *= random.uniform(0.95, 1.05)
        
        # Calculate actual dimensions based on height
        head_size = height * proportions["head_size"]
        torso_length = height * proportions["torso_length"]
        shoulder_width = height * proportions["shoulder_width"]
        hip_width = height * proportions["hip_width"]
        arm_length = height * proportions["arm_length"]
        leg_length = height * proportions["leg_length"]
        
        # Calculate joint positions
        neck_y = height - head_size  # Top of torso
        shoulder_y = neck_y - torso_length * 0.15  # Shoulder height
        hip_y = neck_y - torso_length  # Bottom of torso
        knee_y = hip_y - leg_length * 0.55
        ankle_y = hip_y - leg_length
        
        elbow_x_offset = shoulder_width * 0.2  # Elbow goes slightly inward
        
        # Create points dictionary
        points = {
            # Head and torso
            "head": {"pos": [0, neck_y + head_size * 0.5], "mass": 1.0, "fixed": False},
            "neck": {"pos": [0, neck_y], "mass": 1.0, "fixed": False},
            "shoulder_left": {"pos": [-shoulder_width/2, shoulder_y], "mass": 1.0, "fixed": False},
            "shoulder_right": {"pos": [shoulder_width/2, shoulder_y], "mass": 1.0, "fixed": False},
            "torso_mid": {"pos": [0, (shoulder_y + hip_y) / 2], "mass": 2.0, "fixed": False},
            "hip_left": {"pos": [-hip_width/2, hip_y], "mass": 1.0, "fixed": False},
            "hip_right": {"pos": [hip_width/2, hip_y], "mass": 1.0, "fixed": False},
            
            # Left arm
            "elbow_left": {
                "pos": [-shoulder_width/2 + elbow_x_offset, shoulder_y - arm_length * 0.45], 
                "mass": 0.7, 
                "fixed": False
            },
            "wrist_left": {
                "pos": [-shoulder_width/2 + elbow_x_offset, shoulder_y - arm_length], 
                "mass": 0.5, 
                "fixed": False
            },
            
            # Right arm
            "elbow_right": {
                "pos": [shoulder_width/2 - elbow_x_offset, shoulder_y - arm_length * 0.45], 
                "mass": 0.7, 
                "fixed": False
            },
            "wrist_right": {
                "pos": [shoulder_width/2 - elbow_x_offset, shoulder_y - arm_length], 
                "mass": 0.5, 
                "fixed": False
            },
            
            # Left leg
            "knee_left": {"pos": [-hip_width/3, knee_y], "mass": 0.8, "fixed": False},
            "ankle_left": {"pos": [-hip_width/3, ankle_y], "mass": 0.6, "fixed": False},
            
            # Right leg
            "knee_right": {"pos": [hip_width/3, knee_y], "mass": 0.8, "fixed": False},
            "ankle_right": {"pos": [hip_width/3, ankle_y], "mass": 0.6, "fixed": False}
        }
        
        # Save old position (for verlet integration)
        for point in points.values():
            point["old_pos"] = list(point["pos"])
        
        # Define constraints (connections between points)
        constraints = [
            # Head and neck
            {"p1": "head", "p2": "neck", "stiffness": 0.9},
            
            # Torso structure
            {"p1": "neck", "p2": "shoulder_left", "stiffness": 0.9},
            {"p1": "neck", "p2": "shoulder_right", "stiffness": 0.9},
            {"p1": "neck", "p2": "torso_mid", "stiffness": 0.9},
            {"p1": "shoulder_left", "p2": "torso_mid", "stiffness": 0.8},
            {"p1": "shoulder_right", "p2": "torso_mid", "stiffness": 0.8},
            {"p1": "torso_mid", "p2": "hip_left", "stiffness": 0.8},
            {"p1": "torso_mid", "p2": "hip_right", "stiffness": 0.8},
            {"p1": "hip_left", "p2": "hip_right", "stiffness": 0.9},
            
            # Left arm
            {"p1": "shoulder_left", "p2": "elbow_left", "stiffness": proportions["joint_stiffness"]},
            {"p1": "elbow_left", "p2": "wrist_left", "stiffness": proportions["joint_stiffness"]},
            
            # Right arm
            {"p1": "shoulder_right", "p2": "elbow_right", "stiffness": proportions["joint_stiffness"]},
            {"p1": "elbow_right", "p2": "wrist_right", "stiffness": proportions["joint_stiffness"]},
            
            # Left leg
            {"p1": "hip_left", "p2": "knee_left", "stiffness": proportions["joint_stiffness"]},
            {"p1": "knee_left", "p2": "ankle_left", "stiffness": proportions["joint_stiffness"]},
            
            # Right leg
            {"p1": "hip_right", "p2": "knee_right", "stiffness": proportions["joint_stiffness"]},
            {"p1": "knee_right", "p2": "ankle_right", "stiffness": proportions["joint_stiffness"]}
        ]
        
        # Add angle constraints to prevent unnatural joint bending
        angle_constraints = [
            # Elbow constraints
            {"p1": "shoulder_left", "p2": "elbow_left", "p3": "wrist_left", 
             "min_angle": math.radians(45), "max_angle": math.radians(175), "stiffness": 0.7},
            
            {"p1": "shoulder_right", "p2": "elbow_right", "p3": "wrist_right", 
             "min_angle": math.radians(45), "max_angle": math.radians(175), "stiffness": 0.7},
            
            # Knee constraints
            {"p1": "hip_left", "p2": "knee_left", "p3": "ankle_left", 
             "min_angle": math.radians(45), "max_angle": math.radians(175), "stiffness": 0.7},
            
            {"p1": "hip_right", "p2": "knee_right", "p3": "ankle_right", 
             "min_angle": math.radians(45), "max_angle": math.radians(175), "stiffness": 0.7}
        ]
        
        # Return the complete character model
        return {
            "points": points,
            "constraints": constraints,
            "angle_constraints": angle_constraints,
            "visual": visuals,
            "character_class": character_class.value,
            "muscle_mass": proportions["muscle_mass"],
            "head_size": head_size,
            "shoulder_width": shoulder_width,
            "hip_width": hip_width
        }
    
    def generate_accessory(self, character_class: str, character_model: Dict) -> Dict:
        """
        Generate class-specific accessories
        
        Args:
            character_class: Character class name
            character_model: Character model to attach accessory to
            
        Returns:
            Dictionary with accessory points and constraints
        """
        # Convert string to enum if needed
        if isinstance(character_class, str):
            try:
                character_class = CharacterClass(character_class)
            except ValueError:
                character_class = CharacterClass.WARRIOR  # Default
        
        accessory_points = {}
        accessory_constraints = []
        
        # Generate accessories based on class
        if character_class == CharacterClass.WARRIOR:
            # Add a shield to the left arm
            shoulder = character_model["points"]["shoulder_left"]["pos"]
            wrist = character_model["points"]["wrist_left"]["pos"]
            
            shield_x = wrist[0] - 0.1
            shield_y = (shoulder[1] + wrist[1]) / 2
            
            accessory_points["shield_center"] = {"pos": [shield_x, shield_y], "mass": 1.2, "fixed": False}
            accessory_points["shield_top"] = {"pos": [shield_x, shield_y + 0.15], "mass": 0.5, "fixed": False}
            accessory_points["shield_bottom"] = {"pos": [shield_x, shield_y - 0.15], "mass": 0.5, "fixed": False}
            
            # Add constraints to arm
            accessory_constraints.append({"p1": "wrist_left", "p2": "shield_center", "stiffness": 0.9})
            accessory_constraints.append({"p1": "shield_center", "p2": "shield_top", "stiffness": 0.9})
            accessory_constraints.append({"p1": "shield_center", "p2": "shield_bottom", "stiffness": 0.9})
            
        elif character_class == CharacterClass.MAGE:
            # Add a staff to the right arm
            wrist = character_model["points"]["wrist_right"]["pos"]
            
            staff_x = wrist[0] + 0.05
            staff_y = wrist[1]
            
            accessory_points["staff_top"] = {"pos": [staff_x, staff_y + 0.3], "mass": 0.5, "fixed": False}
            accessory_points["staff_bottom"] = {"pos": [staff_x, staff_y - 0.2], "mass": 0.7, "fixed": False}
            
            # Add constraints
            accessory_constraints.append({"p1": "wrist_right", "p2": "staff_top", "stiffness": 0.85})
            accessory_constraints.append({"p1": "wrist_right", "p2": "staff_bottom", "stiffness": 0.85})
            accessory_constraints.append({"p1": "staff_top", "p2": "staff_bottom", "stiffness": 0.9})
        
        # Save old position (for verlet integration)
        for point in accessory_points.values():
            point["old_pos"] = list(point["pos"])
        
        return {
            "points": accessory_points,
            "constraints": accessory_constraints
        }
    
    def apply_random_variation(self, model: Dict, variation_amount: float = 0.1) -> Dict:
        """
        Apply random variations to a character model
        
        Args:
            model: Character model to vary
            variation_amount: Amount of variation (0-1)
            
        Returns:
            Modified character model
        """
        varied_model = model.copy()
        points = varied_model["points"].copy()
        
        # Apply small random variations to point positions
        for point_name, point_data in points.items():
            # Don't vary fixed points
            if point_data.get("fixed", False):
                continue
                
            # Vary the position slightly
            pos = point_data["pos"]
            varied_pos = [
                pos[0] + random.uniform(-variation_amount, variation_amount),
                pos[1] + random.uniform(-variation_amount, variation_amount)
            ]
            
            point_data["pos"] = varied_pos
            point_data["old_pos"] = varied_pos.copy()
        
        varied_model["points"] = points
        return varied_model 