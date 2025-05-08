#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Character Physics System for Nightfall Defenders
Implements physics-based character animation with muscle system
"""

import math
from enum import Enum
from typing import Dict, List, Tuple, Optional

from panda3d.core import Vec3, Point3, NodePath, LineSegs

from src.engine.physics.verlet import VerletSystem, VerletPoint, DistanceConstraint

class MovementState(Enum):
    """Character movement states"""
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"
    JUMPING = "jumping"
    FALLING = "falling"
    ATTACKING = "attacking"
    DODGING = "dodging"
    CLIMBING = "climbing"
    HURT = "hurt"

class MuscleType(Enum):
    """Types of muscles that can be activated"""
    NECK = "neck"
    SHOULDER_LEFT = "shoulder_left"
    SHOULDER_RIGHT = "shoulder_right"
    ELBOW_LEFT = "elbow_left"
    ELBOW_RIGHT = "elbow_right"
    HIP_LEFT = "hip_left"
    HIP_RIGHT = "hip_right"
    KNEE_LEFT = "knee_left"
    KNEE_RIGHT = "knee_right"
    TORSO = "torso"
    SPINE = "spine"

class CharacterPhysics:
    """
    Manages physics-based character animation using a muscle system
    that controls a Verlet-based physics skeleton
    """
    
    def __init__(self, verlet_system: VerletSystem):
        """
        Initialize the character physics system
        
        Args:
            verlet_system: The Verlet physics system
        """
        self.verlet_system = verlet_system
        
        # Character data
        self.points = {}  # VerletPoint references
        self.constraints = []  # Constraint references
        self.angle_constraints = []  # Angle constraint references
        
        # Muscles
        self.muscles = {}  # Named muscles with target points
        self.muscle_forces = {}  # Current force for each muscle
        self.balance_target = Vec3(0, 0, 0)  # Target for balance system
        
        # Environment
        self.ground_height = 0.0
        self.on_ground = False
        self.climbing = False
        self.climbing_surface = None
        
        # State
        self.movement_state = MovementState.IDLE
        self.facing_direction = 1  # 1 for right, -1 for left
        self.tension = 0.5  # Overall body tension (0-1)
        
        # Movement targets
        self.movement_target = Vec3(0, 0, 0)
        self.target_velocity = Vec3(0, 0, 0)
        
        # Debug
        self.debug_node = None
    
    def initialize_from_model(self, character_model: Dict, position: Vec3, facing_right: bool = True):
        """
        Initialize physics character from a character model
        
        Args:
            character_model: Character model from BodyPartGenerator
            position: Character position
            facing_right: Whether the character is facing right
        """
        # Clear any existing data
        self.points.clear()
        self.constraints.clear()
        self.angle_constraints.clear()
        self.muscles.clear()
        
        # Set facing direction
        self.facing_direction = 1 if facing_right else -1
        
        # Extract model data
        model_points = character_model["points"]
        model_constraints = character_model["constraints"]
        model_angle_constraints = character_model.get("angle_constraints", [])
        
        # Create all points
        for point_name, point_data in model_points.items():
            pos = point_data["pos"]
            x_pos = position.x + pos[0] * self.facing_direction
            y_pos = position.y
            z_pos = position.z + pos[1]
            
            # Create the point
            verlet_point = self.verlet_system.add_point(
                Vec3(x_pos, y_pos, z_pos),
                point_data.get("mass", 1.0),
                point_data.get("fixed", False)
            )
            
            # Store reference
            self.points[point_name] = verlet_point
        
        # Create constraints
        for constraint_data in model_constraints:
            p1 = constraint_data["p1"]
            p2 = constraint_data["p2"]
            
            if p1 in self.points and p2 in self.points:
                constraint = self.verlet_system.add_distance_constraint(
                    self.points[p1],
                    self.points[p2],
                    None,  # Use current distance
                    constraint_data.get("stiffness", 0.8)
                )
                
                self.constraints.append(constraint)
        
        # Create angle constraints
        for angle_constraint in model_angle_constraints:
            p1 = angle_constraint["p1"]
            p2 = angle_constraint["p2"]
            p3 = angle_constraint["p3"]
            
            if p1 in self.points and p2 in self.points and p3 in self.points:
                constraint = self.verlet_system.add_angle_constraint(
                    self.points[p1],
                    self.points[p2],
                    self.points[p3],
                    None,  # Use current angle
                    angle_constraint.get("stiffness", 0.5)
                )
                
                # Set min/max angles if provided
                if "min_angle" in angle_constraint:
                    constraint.min_angle = angle_constraint["min_angle"]
                if "max_angle" in angle_constraint:
                    constraint.max_angle = angle_constraint["max_angle"]
                
                self.angle_constraints.append(constraint)
        
        # Create muscle definitions
        self._setup_muscles()
    
    def _setup_muscles(self):
        """Set up muscle definitions based on character skeleton"""
        # Check if we have the necessary points
        required_points = ["neck", "torso_mid", "hip_left", "hip_right", 
                          "shoulder_left", "shoulder_right", "knee_left", "knee_right"]
        
        if not all(point in self.points for point in required_points):
            print("Warning: Not all required points exist for muscles")
            return
        
        # Create muscles with target points and rest positions
        self.muscles = {
            MuscleType.NECK: {
                "anchor": self.points["neck"],
                "target": self.points["head"],
                "rest_offset": Vec3(0, 0, 0),
                "strength": 0.8
            },
            MuscleType.SHOULDER_LEFT: {
                "anchor": self.points["torso_mid"],
                "target": self.points["shoulder_left"],
                "rest_offset": Vec3(-0.1 * self.facing_direction, 0, 0.05),
                "strength": 0.7
            },
            MuscleType.SHOULDER_RIGHT: {
                "anchor": self.points["torso_mid"],
                "target": self.points["shoulder_right"],
                "rest_offset": Vec3(0.1 * self.facing_direction, 0, 0.05),
                "strength": 0.7
            },
            MuscleType.HIP_LEFT: {
                "anchor": self.points["torso_mid"],
                "target": self.points["hip_left"],
                "rest_offset": Vec3(-0.05 * self.facing_direction, 0, -0.1),
                "strength": 0.7
            },
            MuscleType.HIP_RIGHT: {
                "anchor": self.points["torso_mid"],
                "target": self.points["hip_right"],
                "rest_offset": Vec3(0.05 * self.facing_direction, 0, -0.1),
                "strength": 0.7
            },
            MuscleType.KNEE_LEFT: {
                "anchor": self.points["hip_left"],
                "target": self.points["knee_left"],
                "rest_offset": Vec3(0, 0, -0.1),
                "strength": 0.6
            },
            MuscleType.KNEE_RIGHT: {
                "anchor": self.points["hip_right"],
                "target": self.points["knee_right"],
                "rest_offset": Vec3(0, 0, -0.1),
                "strength": 0.6
            },
            MuscleType.SPINE: {
                "anchor": self.points["hip_left"],  # Actually uses both hips
                "target": self.points["torso_mid"],
                "rest_offset": Vec3(0, 0, 0.1),
                "strength": 0.9
            }
        }
        
        # Add arm muscles if we have elbow points
        if "elbow_left" in self.points and "wrist_left" in self.points:
            self.muscles[MuscleType.ELBOW_LEFT] = {
                "anchor": self.points["shoulder_left"],
                "target": self.points["elbow_left"],
                "rest_offset": Vec3(-0.05 * self.facing_direction, 0, -0.05),
                "strength": 0.6
            }
        
        if "elbow_right" in self.points and "wrist_right" in self.points:
            self.muscles[MuscleType.ELBOW_RIGHT] = {
                "anchor": self.points["shoulder_right"],
                "target": self.points["elbow_right"],
                "rest_offset": Vec3(0.05 * self.facing_direction, 0, -0.05),
                "strength": 0.6
            }
        
        # Initialize muscle forces
        self.muscle_forces = {muscle_type: Vec3(0, 0, 0) for muscle_type in self.muscles}
    
    def update(self, dt: float):
        """
        Update character physics
        
        Args:
            dt: Delta time in seconds
        """
        # Check ground contact
        self._check_ground_contact()
        
        # Update muscles based on current movement state
        self._update_muscles(dt)
        
        # Apply muscle forces
        self._apply_muscle_forces()
        
        # Apply balance control
        self._apply_balance_forces(dt)
    
    def _check_ground_contact(self):
        """Check if character is in contact with the ground"""
        # Find the lowest point of the character (usually feet)
        lowest_point = float('inf')
        for point_name, point in self.points.items():
            if "ankle" in point_name or "foot" in point_name:
                if point.position.z < lowest_point:
                    lowest_point = point.position.z
        
        # Check if lowest point is near ground
        ground_threshold = 0.1  # How close to ground to consider "on ground"
        self.on_ground = abs(lowest_point - self.ground_height) < ground_threshold
    
    def _update_muscles(self, dt: float):
        """
        Update muscle targets based on current movement state
        
        Args:
            dt: Delta time in seconds
        """
        # Get the base character center position
        center = self._get_character_center()
        
        # Reset muscle forces
        for muscle_type in self.muscle_forces:
            self.muscle_forces[muscle_type] = Vec3(0, 0, 0)
        
        # Different behaviors based on movement state
        if self.movement_state == MovementState.IDLE:
            self._idle_pose(dt)
        elif self.movement_state == MovementState.WALKING:
            self._walking_pose(dt)
        elif self.movement_state == MovementState.RUNNING:
            self._running_pose(dt)
        elif self.movement_state == MovementState.JUMPING:
            self._jumping_pose(dt)
        elif self.movement_state == MovementState.FALLING:
            self._falling_pose(dt)
        elif self.movement_state == MovementState.ATTACKING:
            self._attacking_pose(dt)
        elif self.movement_state == MovementState.CLIMBING:
            self._climbing_pose(dt)
        else:
            # Default to idle
            self._idle_pose(dt)
    
    def _idle_pose(self, dt: float):
        """Set muscles for idle pose"""
        # Slight relaxed posture
        tension = 0.4 * self.tension
        
        # Apply small breathing motion
        breathing = math.sin(self.verlet_system.time_accumulator * 1.0) * 0.02
        
        # Neck slightly forward
        self.muscle_forces[MuscleType.NECK] = Vec3(0.1 * self.facing_direction, 0, 0.05 + breathing) * tension
        
        # Shoulders relaxed
        self.muscle_forces[MuscleType.SHOULDER_LEFT] = Vec3(-0.05 * self.facing_direction, 0, breathing) * tension
        self.muscle_forces[MuscleType.SHOULDER_RIGHT] = Vec3(0.05 * self.facing_direction, 0, breathing) * tension
        
        # Relaxed elbows
        if MuscleType.ELBOW_LEFT in self.muscles:
            self.muscle_forces[MuscleType.ELBOW_LEFT] = Vec3(-0.02 * self.facing_direction, 0, -0.03) * tension
        
        if MuscleType.ELBOW_RIGHT in self.muscles:
            self.muscle_forces[MuscleType.ELBOW_RIGHT] = Vec3(0.02 * self.facing_direction, 0, -0.03) * tension
        
        # Hips and knees relaxed
        self.muscle_forces[MuscleType.HIP_LEFT] = Vec3(-0.02 * self.facing_direction, 0, -0.03) * tension
        self.muscle_forces[MuscleType.HIP_RIGHT] = Vec3(0.02 * self.facing_direction, 0, -0.03) * tension
        self.muscle_forces[MuscleType.KNEE_LEFT] = Vec3(0, 0, -0.05) * tension
        self.muscle_forces[MuscleType.KNEE_RIGHT] = Vec3(0, 0, -0.05) * tension
        
        # Spine slightly upright
        self.muscle_forces[MuscleType.SPINE] = Vec3(0, 0, 0.05 + breathing) * tension
    
    def _walking_pose(self, dt: float):
        """Set muscles for walking pose with leg cycle"""
        # Higher tension during walking
        tension = 0.7 * self.tension
        
        # Walking cycle
        cycle_speed = 3.0  # Speed of the walking cycle
        t = self.verlet_system.time_accumulator * cycle_speed
        
        # Alternating leg movement
        leg_left_forward = math.sin(t) > 0
        leg_right_forward = not leg_left_forward
        
        # Neck forward
        self.muscle_forces[MuscleType.NECK] = Vec3(0.15 * self.facing_direction, 0, 0.1) * tension
        
        # Shoulders counter-motion to legs
        self.muscle_forces[MuscleType.SHOULDER_LEFT] = Vec3(
            (-0.1 if leg_left_forward else 0.1) * self.facing_direction, 0, 0.05
        ) * tension
        
        self.muscle_forces[MuscleType.SHOULDER_RIGHT] = Vec3(
            (-0.1 if leg_right_forward else 0.1) * self.facing_direction, 0, 0.05
        ) * tension
        
        # Arms swing opposite to legs
        if MuscleType.ELBOW_LEFT in self.muscles:
            self.muscle_forces[MuscleType.ELBOW_LEFT] = Vec3(
                (-0.15 if leg_right_forward else 0.05) * self.facing_direction, 0, -0.05
            ) * tension
        
        if MuscleType.ELBOW_RIGHT in self.muscles:
            self.muscle_forces[MuscleType.ELBOW_RIGHT] = Vec3(
                (-0.15 if leg_left_forward else 0.05) * self.facing_direction, 0, -0.05
            ) * tension
        
        # Hips and knees
        hip_forward_force = 0.12
        hip_backward_force = -0.05
        knee_up_force = 0.12
        knee_down_force = -0.15
        
        self.muscle_forces[MuscleType.HIP_LEFT] = Vec3(
            (hip_forward_force if leg_left_forward else hip_backward_force) * self.facing_direction, 
            0, 0
        ) * tension
        
        self.muscle_forces[MuscleType.HIP_RIGHT] = Vec3(
            (hip_forward_force if leg_right_forward else hip_backward_force) * self.facing_direction, 
            0, 0
        ) * tension
        
        self.muscle_forces[MuscleType.KNEE_LEFT] = Vec3(
            0, 0, knee_up_force if leg_left_forward else knee_down_force
        ) * tension
        
        self.muscle_forces[MuscleType.KNEE_RIGHT] = Vec3(
            0, 0, knee_up_force if leg_right_forward else knee_down_force
        ) * tension
        
        # Spine slightly tilted forward
        self.muscle_forces[MuscleType.SPINE] = Vec3(0.05 * self.facing_direction, 0, 0.08) * tension
    
    def _running_pose(self, dt: float):
        """Set muscles for running pose with leg cycle"""
        # More intense version of walking cycle
        self._walking_pose(dt)
        
        # Then scale up all forces
        for muscle_type in self.muscle_forces:
            self.muscle_forces[muscle_type] *= 1.5
    
    def _jumping_pose(self, dt: float):
        """Set muscles for jumping pose"""
        # High tension during jump
        tension = 0.9 * self.tension
        
        # Arms up and forward
        if MuscleType.ELBOW_LEFT in self.muscles:
            self.muscle_forces[MuscleType.ELBOW_LEFT] = Vec3(0.1 * self.facing_direction, 0, 0.2) * tension
        
        if MuscleType.ELBOW_RIGHT in self.muscles:
            self.muscle_forces[MuscleType.ELBOW_RIGHT] = Vec3(0.1 * self.facing_direction, 0, 0.2) * tension
        
        # Legs extended
        self.muscle_forces[MuscleType.KNEE_LEFT] = Vec3(0, 0, -0.3) * tension
        self.muscle_forces[MuscleType.KNEE_RIGHT] = Vec3(0, 0, -0.3) * tension
        
        # Spine arched
        self.muscle_forces[MuscleType.SPINE] = Vec3(0.1 * self.facing_direction, 0, 0.2) * tension
    
    def _falling_pose(self, dt: float):
        """Set muscles for falling pose"""
        # Medium tension while falling
        tension = 0.6 * self.tension
        
        # Arms extended outward for balance
        self.muscle_forces[MuscleType.SHOULDER_LEFT] = Vec3(-0.2 * self.facing_direction, 0, 0.1) * tension
        self.muscle_forces[MuscleType.SHOULDER_RIGHT] = Vec3(0.2 * self.facing_direction, 0, 0.1) * tension
        
        # Legs bent for landing
        self.muscle_forces[MuscleType.KNEE_LEFT] = Vec3(0, 0, 0.1) * tension
        self.muscle_forces[MuscleType.KNEE_RIGHT] = Vec3(0, 0, 0.1) * tension
    
    def _attacking_pose(self, dt: float):
        """Set muscles for attacking pose"""
        # Very high tension during attack
        tension = 1.0 * self.tension
        
        # Check which point is the "weapon arm"
        weapon_arm = MuscleType.ELBOW_RIGHT if self.facing_direction > 0 else MuscleType.ELBOW_LEFT
        off_arm = MuscleType.ELBOW_LEFT if self.facing_direction > 0 else MuscleType.ELBOW_RIGHT
        
        # Weapon arm extends forward
        if weapon_arm in self.muscles:
            self.muscle_forces[weapon_arm] = Vec3(0.3 * self.facing_direction, 0, 0.1) * tension
        
        # Off-arm back for balance
        if off_arm in self.muscles:
            self.muscle_forces[off_arm] = Vec3(-0.2 * self.facing_direction, 0, 0.1) * tension
        
        # Torso rotates into attack
        self.muscle_forces[MuscleType.SHOULDER_RIGHT] = Vec3(0.15 * self.facing_direction, 0, 0.1) * tension
        self.muscle_forces[MuscleType.SHOULDER_LEFT] = Vec3(-0.15 * self.facing_direction, 0, 0.1) * tension
        
        # Stance widens
        self.muscle_forces[MuscleType.HIP_LEFT] = Vec3(-0.15 * self.facing_direction, 0, 0) * tension
        self.muscle_forces[MuscleType.HIP_RIGHT] = Vec3(0.15 * self.facing_direction, 0, 0) * tension
    
    def _climbing_pose(self, dt: float):
        """Set muscles for climbing pose"""
        # High tension during climbing
        tension = 0.85 * self.tension
        
        # Climbing cycle
        cycle_speed = 2.0
        t = self.verlet_system.time_accumulator * cycle_speed
        
        # Alternating arm/leg movement
        left_up = math.sin(t) > 0
        right_up = not left_up
        
        # Arms reach up
        if MuscleType.SHOULDER_LEFT in self.muscles:
            self.muscle_forces[MuscleType.SHOULDER_LEFT] = Vec3(
                0, 0, 0.2 if left_up else 0.05
            ) * tension
        
        if MuscleType.SHOULDER_RIGHT in self.muscles:
            self.muscle_forces[MuscleType.SHOULDER_RIGHT] = Vec3(
                0, 0, 0.2 if right_up else 0.05
            ) * tension
        
        # Legs brace against wall
        self.muscle_forces[MuscleType.KNEE_LEFT] = Vec3(
            0, 0, 0.15 if left_up else -0.1
        ) * tension
        
        self.muscle_forces[MuscleType.KNEE_RIGHT] = Vec3(
            0, 0, 0.15 if right_up else -0.1
        ) * tension
        
        # Torso close to wall
        self.muscle_forces[MuscleType.SPINE] = Vec3(0, -0.2, 0.1) * tension
    
    def _apply_muscle_forces(self):
        """Apply current muscle forces to the physics points"""
        for muscle_type, force in self.muscle_forces.items():
            if muscle_type not in self.muscles:
                continue
                
            muscle = self.muscles[muscle_type]
            target = muscle["target"]
            anchor = muscle["anchor"]
            strength = muscle["strength"]
            
            # Skip if either point is fixed
            if target.fixed or anchor.fixed:
                continue
            
            # Calculate direction from anchor to target
            direction = (target.position - anchor.position).normalized()
            
            # Apply force to target
            target.apply_force(force * strength)
            
            # Apply opposite force to anchor (smaller)
            anchor.apply_force(-force * strength * 0.5)
    
    def _apply_balance_forces(self, dt: float):
        """Apply balancing forces to keep character upright"""
        # Only apply balance when on ground
        if not self.on_ground:
            return
            
        # For simplicity, we'll just apply upward force to torso
        if "torso_mid" in self.points:
            torso = self.points["torso_mid"]
            # Apply upward force with some forward lean
            balance_force = Vec3(0.05 * self.facing_direction, 0, 0.5 * self.tension)
            torso.apply_force(balance_force)
    
    def _get_character_center(self) -> Vec3:
        """Get the character's center position"""
        if "torso_mid" in self.points:
            return self.points["torso_mid"].position
        
        # Fall back to calculating average of all points
        total = Vec3(0, 0, 0)
        count = 0
        
        for point in self.points.values():
            total += point.position
            count += 1
            
        if count > 0:
            return total / count
        
        return Vec3(0, 0, 0)
    
    def set_movement_state(self, state: MovementState, target_velocity: Optional[Vec3] = None):
        """
        Set the character's movement state
        
        Args:
            state: New movement state
            target_velocity: Target velocity vector (if applicable)
        """
        self.movement_state = state
        
        if target_velocity:
            self.target_velocity = target_velocity
            
            # Update facing direction based on velocity
            if abs(target_velocity.x) > 0.01:
                self.facing_direction = 1 if target_velocity.x > 0 else -1
    
    def set_ground_height(self, height: float):
        """Set the ground height for the character"""
        self.ground_height = height
    
    def set_tension(self, tension: float):
        """
        Set overall body tension (0-1)
        
        Args:
            tension: Tension level (0-1)
        """
        self.tension = max(0.1, min(1.0, tension))
    
    def set_climbing(self, climbing: bool, surface: Optional[Vec3] = None):
        """
        Set climbing state
        
        Args:
            climbing: Whether character is climbing
            surface: Surface normal vector
        """
        self.climbing = climbing
        self.climbing_surface = surface
        
        if climbing:
            self.set_movement_state(MovementState.CLIMBING)
    
    def enable_debug_visualization(self, render_node: NodePath):
        """
        Enable debug visualization
        
        Args:
            render_node: Node to attach visualization to
        """
        if self.debug_node:
            self.debug_node.removeNode()
            
        self.debug_node = render_node.attachNewNode("character_physics_debug")
        
    def update_debug_visualization(self):
        """Update the debug visualization if enabled"""
        if not self.debug_node:
            return
            
        # Clear existing visualization
        self.debug_node.removeNode()
        self.debug_node = self.debug_node.getParent().attachNewNode("character_physics_debug")
        
        # Draw muscle forces
        segs = LineSegs()
        segs.setThickness(2.0)
        segs.setColor(1.0, 0.0, 0.0, 1.0)  # Red
        
        for muscle_type, muscle in self.muscles.items():
            if muscle_type not in self.muscle_forces:
                continue
                
            force = self.muscle_forces[muscle_type]
            if force.length() < 0.01:
                continue
                
            target = muscle["target"]
            
            # Draw force vector
            segs.moveTo(target.position)
            segs.drawTo(target.position + force * 2.0)  # Scale for visibility
            
        # Create the visualization
        self.debug_node.attachNewNode(segs.create()) 