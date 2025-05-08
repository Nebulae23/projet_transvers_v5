#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Verlet Integration Physics System for Nightfall Defenders
Implements physics-based animation for organic character movement
"""

import math
from typing import List, Tuple, Dict, Set, Optional
from panda3d.core import Vec3, Point3, LineSegs, NodePath

class VerletPoint:
    """A point in a Verlet physics system"""
    
    def __init__(self, position: Vec3, mass: float = 1.0, fixed: bool = False):
        """
        Initialize a Verlet point
        
        Args:
            position: Initial position
            mass: Point mass (affects force response)
            fixed: Whether this point is fixed in place
        """
        self.position = Vec3(position)
        self.old_position = Vec3(position)  # Previous position, used for velocity
        self.acceleration = Vec3(0, 0, 0)
        self.mass = max(0.01, mass)  # Minimum mass to avoid division by zero
        self.fixed = fixed
        self.accumulated_force = Vec3(0, 0, 0)
        
        # Constraints
        self.min_bounds = None  # Optional position constraints
        self.max_bounds = None
    
    def update(self, dt: float):
        """
        Update the point's position using Verlet integration
        
        Args:
            dt: Delta time in seconds
        """
        if self.fixed:
            return
            
        # Calculate velocity from current and previous position
        velocity = self.position - self.old_position
        
        # Save current position before updating
        self.old_position = Vec3(self.position)
        
        # Calculate acceleration from accumulated forces
        self.acceleration = self.accumulated_force / self.mass
        
        # Reset accumulated force for next frame
        self.accumulated_force = Vec3(0, 0, 0)
        
        # Update position using Verlet integration
        # x = x + v + a*dt²
        self.position = self.position + velocity + self.acceleration * dt * dt
        
        # Apply bounds constraints if set
        if self.min_bounds and self.max_bounds:
            self.position.x = max(self.min_bounds.x, min(self.max_bounds.x, self.position.x))
            self.position.y = max(self.min_bounds.y, min(self.max_bounds.y, self.position.y))
            self.position.z = max(self.min_bounds.z, min(self.max_bounds.z, self.position.z))
    
    def apply_force(self, force: Vec3):
        """
        Apply a force to the point
        
        Args:
            force: Force vector to apply
        """
        if self.fixed:
            return
            
        self.accumulated_force += force
    
    def set_position(self, position: Vec3, update_old: bool = True):
        """
        Set the point's position directly
        
        Args:
            position: New position
            update_old: Whether to update old_position (affects velocity)
        """
        self.position = Vec3(position)
        
        if update_old:
            self.old_position = Vec3(position)
    
    def get_velocity(self) -> Vec3:
        """
        Get the current velocity
        
        Returns:
            Velocity vector
        """
        return self.position - self.old_position
    
    def set_bounds(self, min_bounds: Vec3, max_bounds: Vec3):
        """
        Set movement bounds for this point
        
        Args:
            min_bounds: Minimum position
            max_bounds: Maximum position
        """
        self.min_bounds = min_bounds
        self.max_bounds = max_bounds


class VerletConstraint:
    """Base class for constraints between Verlet points"""
    
    def __init__(self, point_a: VerletPoint, point_b: VerletPoint):
        """
        Initialize a constraint between two points
        
        Args:
            point_a: First point
            point_b: Second point
        """
        self.point_a = point_a
        self.point_b = point_b
    
    def solve(self):
        """Solve the constraint (apply corrections to points)"""
        pass


class DistanceConstraint(VerletConstraint):
    """Maintains a specified distance between two points"""
    
    def __init__(self, point_a: VerletPoint, point_b: VerletPoint, 
                 length: float = None, stiffness: float = 1.0):
        """
        Initialize a distance constraint
        
        Args:
            point_a: First point
            point_b: Second point
            length: Target distance (if None, use current distance)
            stiffness: Constraint stiffness (0-1)
        """
        super().__init__(point_a, point_b)
        
        # If length not specified, use current distance
        if length is None:
            self.length = (point_a.position - point_b.position).length()
        else:
            self.length = length
            
        # Stiffness affects how strongly the constraint is enforced
        self.stiffness = max(0.0, min(1.0, stiffness))
    
    def solve(self):
        """Solve the distance constraint"""
        # Calculate current vector between points
        delta = self.point_b.position - self.point_a.position
        current_length = delta.length()
        
        # Avoid division by zero
        if current_length < 0.0001:
            # Points are too close, push them apart slightly
            direction = Vec3(1, 0, 0)  # Arbitrary direction
            current_length = 0.0001
        else:
            # Normalize the vector
            direction = delta / current_length
        
        # Calculate how much the constraint is violated
        error = current_length - self.length
        
        # Skip if constraint is satisfied
        if abs(error) < 0.0001:
            return
            
        # Calculate correction factor based on mass
        if self.point_a.fixed and self.point_b.fixed:
            # Both points fixed, can't correct
            return
        elif self.point_a.fixed:
            # Only point A is fixed
            correction_factor = 1.0
        elif self.point_b.fixed:
            # Only point B is fixed
            correction_factor = 1.0
        else:
            # Both points movable, distribute based on mass ratio
            mass_sum = self.point_a.mass + self.point_b.mass
            correction_factor = self.point_a.mass / mass_sum
        
        # Calculate correction vectors
        correction = direction * error * self.stiffness
        
        # Apply corrections
        if not self.point_a.fixed:
            self.point_a.position += correction * (1.0 - correction_factor)
        
        if not self.point_b.fixed:
            self.point_b.position -= correction * correction_factor


class AngleConstraint(VerletConstraint):
    """Maintains a specified angle between three points"""
    
    def __init__(self, point_a: VerletPoint, point_b: VerletPoint, point_c: VerletPoint,
                 angle: float = None, stiffness: float = 0.5):
        """
        Initialize an angle constraint
        
        Args:
            point_a: First point
            point_b: Middle point (pivot)
            point_c: Third point
            angle: Target angle in radians (if None, use current angle)
            stiffness: Constraint stiffness (0-1)
        """
        super().__init__(point_a, point_b)
        self.point_c = point_c
        
        # If angle not specified, use current angle
        if angle is None:
            vec1 = point_a.position - point_b.position
            vec2 = point_c.position - point_b.position
            self.angle = self._calculate_angle(vec1, vec2)
        else:
            self.angle = angle
            
        self.stiffness = max(0.0, min(1.0, stiffness))
    
    def _calculate_angle(self, vec1: Vec3, vec2: Vec3) -> float:
        """
        Calculate angle between two vectors
        
        Args:
            vec1: First vector
            vec2: Second vector
            
        Returns:
            Angle in radians
        """
        len1 = vec1.length()
        len2 = vec2.length()
        
        if len1 < 0.0001 or len2 < 0.0001:
            return 0.0
            
        dot = vec1.dot(vec2) / (len1 * len2)
        # Clamp dot product to [-1, 1] to avoid precision errors
        dot = max(-1.0, min(1.0, dot))
        return math.acos(dot)
    
    def solve(self):
        """Solve the angle constraint"""
        # Get vectors from pivot to end points
        vec1 = self.point_a.position - self.point_b.position
        vec2 = self.point_c.position - self.point_b.position
        
        # Check if vectors are valid
        len1 = vec1.length()
        len2 = vec2.length()
        
        if len1 < 0.0001 or len2 < 0.0001:
            return
        
        # Normalize vectors
        vec1_norm = vec1 / len1
        vec2_norm = vec2 / len2
        
        # Calculate current angle
        current_angle = self._calculate_angle(vec1, vec2)
        
        # Calculate how much the constraint is violated
        angle_error = current_angle - self.angle
        
        # Skip if constraint is satisfied
        if abs(angle_error) < 0.0001:
            return
        
        # Determine rotation direction using cross product
        cross = vec1.cross(vec2)
        cross_length = cross.length()
        
        if cross_length < 0.0001:
            # Vectors are collinear, choose arbitrary rotation axis
            if abs(vec1.z) < 0.9:
                rotation_axis = vec1.cross(Vec3(0, 0, 1)).normalized()
            else:
                rotation_axis = vec1.cross(Vec3(1, 0, 0)).normalized()
        else:
            rotation_axis = cross / cross_length
        
        # Calculate rotation amount
        correction_angle = angle_error * self.stiffness
        
        # Apply correction to each point if not fixed
        if not self.point_a.fixed and not self.point_b.fixed:
            # Rotate both points around midpoint
            self.point_a.position = self._rotate_point(
                self.point_a.position, 
                self.point_b.position, 
                rotation_axis, 
                correction_angle * 0.5
            )
            
            self.point_c.position = self._rotate_point(
                self.point_c.position, 
                self.point_b.position, 
                rotation_axis, 
                -correction_angle * 0.5
            )
        elif not self.point_a.fixed:
            # Only point A can move
            self.point_a.position = self._rotate_point(
                self.point_a.position, 
                self.point_b.position, 
                rotation_axis, 
                correction_angle
            )
        elif not self.point_c.fixed:
            # Only point C can move
            self.point_c.position = self._rotate_point(
                self.point_c.position, 
                self.point_b.position, 
                rotation_axis, 
                -correction_angle
            )
    
    def _rotate_point(self, point: Vec3, pivot: Vec3, axis: Vec3, angle: float) -> Vec3:
        """
        Rotate a point around a pivot along an axis by an angle
        
        Args:
            point: Point to rotate
            pivot: Pivot point
            axis: Rotation axis (normalized)
            angle: Angle in radians
            
        Returns:
            Rotated point
        """
        # Translate to origin
        translated = point - pivot
        
        # Calculate rotation
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        
        # Rotate using Rodrigues' rotation formula
        rotated = (translated * cos_angle + 
                  axis.cross(translated) * sin_angle + 
                  axis * axis.dot(translated) * (1 - cos_angle))
        
        # Translate back
        return rotated + pivot


class VerletSystem:
    """Manages a collection of Verlet points and constraints"""
    
    def __init__(self):
        """Initialize the Verlet physics system"""
        self.points = []
        self.constraints = []
        self.gravity = Vec3(0, 0, -9.8)  # Default gravity
        self.global_damping = 0.01  # Velocity damping
        
        # Debug visualization
        self.debug_node = None
        self.debug_lines = None
        self.show_debug = False
    
    def add_point(self, position: Vec3, mass: float = 1.0, fixed: bool = False) -> VerletPoint:
        """
        Add a point to the system
        
        Args:
            position: Initial position
            mass: Point mass
            fixed: Whether this point is fixed in place
            
        Returns:
            The created VerletPoint
        """
        point = VerletPoint(position, mass, fixed)
        self.points.append(point)
        return point
    
    def add_distance_constraint(self, point_a: VerletPoint, point_b: VerletPoint, 
                               length: float = None, stiffness: float = 1.0) -> DistanceConstraint:
        """
        Add a distance constraint between two points
        
        Args:
            point_a: First point
            point_b: Second point
            length: Target distance (if None, use current distance)
            stiffness: Constraint stiffness (0-1)
            
        Returns:
            The created DistanceConstraint
        """
        constraint = DistanceConstraint(point_a, point_b, length, stiffness)
        self.constraints.append(constraint)
        return constraint
    
    def add_angle_constraint(self, point_a: VerletPoint, point_b: VerletPoint, point_c: VerletPoint,
                             angle: float = None, stiffness: float = 0.5) -> AngleConstraint:
        """
        Add an angle constraint between three points
        
        Args:
            point_a: First point
            point_b: Middle point (pivot)
            point_c: Third point
            angle: Target angle in radians (if None, use current angle)
            stiffness: Constraint stiffness (0-1)
            
        Returns:
            The created AngleConstraint
        """
        constraint = AngleConstraint(point_a, point_b, point_c, angle, stiffness)
        self.constraints.append(constraint)
        return constraint
    
    def update(self, dt: float, constraint_iterations: int = 3):
        """
        Update the physics system
        
        Args:
            dt: Delta time in seconds
            constraint_iterations: Number of iterations for constraint solving
        """
        # Apply gravity and other global forces to all points
        for point in self.points:
            # Apply gravity
            point.apply_force(self.gravity * point.mass)
            
            # Update point position using Verlet integration
            point.update(dt)
            
            # Apply damping to prevent oscillation
            if not point.fixed and self.global_damping > 0:
                velocity = point.get_velocity()
                if velocity.length_squared() > 0.0001:
                    damping_factor = 1.0 - self.global_damping
                    point.old_position = point.position - (velocity * damping_factor)
        
        # Solve constraints multiple times for stability
        for _ in range(constraint_iterations):
            for constraint in self.constraints:
                constraint.solve()
        
        # Update debug visualization if enabled
        if self.show_debug:
            self.update_debug_visualization()
    
    def apply_force_to_all(self, force: Vec3):
        """
        Apply a force to all points in the system
        
        Args:
            force: Force vector to apply
        """
        for point in self.points:
            point.apply_force(force)
    
    def set_gravity(self, gravity: Vec3):
        """
        Set global gravity
        
        Args:
            gravity: Gravity vector
        """
        self.gravity = Vec3(gravity)
    
    def enable_debug_visualization(self, render_node: NodePath):
        """
        Enable debug visualization
        
        Args:
            render_node: Node to attach visualization to
        """
        if self.debug_node is None:
            self.debug_node = render_node.attach_new_node("verlet_debug")
            self.show_debug = True
    
    def update_debug_visualization(self):
        """Update the debug visualization of points and constraints"""
        if not self.debug_node:
            return
            
        # Clear previous visualization
        self.debug_node.remove_node()
        self.debug_node = self.debug_node.getParent().attach_new_node("verlet_debug")
        
        # Create lines for constraints
        lines = LineSegs()
        lines.setThickness(2.0)
        lines.setColor(1, 1, 0, 1)  # Yellow lines
        
        for constraint in self.constraints:
            if isinstance(constraint, DistanceConstraint):
                lines.moveTo(constraint.point_a.position)
                lines.drawTo(constraint.point_b.position)
        
        # Create the line node and attach it
        line_node = lines.create()
        self.debug_node.attach_new_node(line_node)
        
        # Create markers for points (could use visible geometry here)
        from panda3d.core import GeomNode, GeomVertexData, GeomVertexFormat
        from panda3d.core import Geom, GeomTriangles, GeomVertexWriter
        
        for i, point in enumerate(self.points):
            # Create a small sphere for each point
            from panda3d.core import load_model
            sphere = self.debug_node.attach_new_node(f"point_{i}")
            # Load a sphere model (assuming it exists, or you could use a primitive)
            model = loader.load_model("models/misc/sphere")
            model.set_scale(0.1)  # Small size
            
            # Set color based on fixed status
            if point.fixed:
                model.set_color(1, 0, 0, 1)  # Red for fixed points
            else:
                model.set_color(0, 1, 0, 1)  # Green for movable points
                
            model.reparent_to(sphere)
            sphere.set_pos(point.position)
    
    def create_character_rig(self, base_position: Vec3, height: float = 2.0, character_type: str = "humanoid") -> Dict[str, VerletPoint]:
        """
        Create a character rig for organic animation
        
        Args:
            base_position: Base position for the character
            height: Character height
            character_type: Type of character rig to create (humanoid, quadruped, etc.)
            
        Returns:
            Dictionary mapping joint names to VerletPoints
        """
        # Scale all dimensions based on height
        scale = height / 2.0
        
        # Result dictionary
        points = {}
        
        if character_type == "humanoid":
            # Create a humanoid character rig
            
            # Torso points
            pelvis = self.add_point(base_position + Vec3(0, 0, scale * 0.8), mass=10.0)
            chest = self.add_point(base_position + Vec3(0, 0, scale * 1.2), mass=10.0)
            neck = self.add_point(base_position + Vec3(0, 0, scale * 1.5), mass=3.0)
            head = self.add_point(base_position + Vec3(0, 0, scale * 1.7), mass=5.0)
            
            # Shoulders
            l_shoulder = self.add_point(base_position + Vec3(-scale * 0.3, 0, scale * 1.4), mass=5.0)
            r_shoulder = self.add_point(base_position + Vec3(scale * 0.3, 0, scale * 1.4), mass=5.0)
        
        # Arms
            l_elbow = self.add_point(base_position + Vec3(-scale * 0.6, 0, scale * 1.2), mass=3.0)
            r_elbow = self.add_point(base_position + Vec3(scale * 0.6, 0, scale * 1.2), mass=3.0)
            l_hand = self.add_point(base_position + Vec3(-scale * 0.8, 0, scale * 0.9), mass=2.0)
            r_hand = self.add_point(base_position + Vec3(scale * 0.8, 0, scale * 0.9), mass=2.0)
            
            # Hips
            l_hip = self.add_point(base_position + Vec3(-scale * 0.2, 0, scale * 0.7), mass=5.0)
            r_hip = self.add_point(base_position + Vec3(scale * 0.2, 0, scale * 0.7), mass=5.0)
            
            # Legs
            l_knee = self.add_point(base_position + Vec3(-scale * 0.25, 0, scale * 0.4), mass=3.0)
            r_knee = self.add_point(base_position + Vec3(scale * 0.25, 0, scale * 0.4), mass=3.0)
            l_foot = self.add_point(base_position + Vec3(-scale * 0.3, 0, scale * 0.05), mass=2.0, fixed=True)
            r_foot = self.add_point(base_position + Vec3(scale * 0.3, 0, scale * 0.05), mass=2.0, fixed=True)
            
            # Add connections (torso)
            self.add_distance_constraint(pelvis, chest)
            self.add_distance_constraint(chest, neck)
            self.add_distance_constraint(neck, head)
            
            # Shoulders and arms
            self.add_distance_constraint(chest, l_shoulder)
            self.add_distance_constraint(chest, r_shoulder)
            self.add_distance_constraint(l_shoulder, l_elbow)
            self.add_distance_constraint(r_shoulder, r_elbow)
            self.add_distance_constraint(l_elbow, l_hand)
            self.add_distance_constraint(r_elbow, r_hand)
            
            # Additional arm constraints for stability
            self.add_distance_constraint(l_shoulder, neck)
            self.add_distance_constraint(r_shoulder, neck)
            
            # Hips and legs
            self.add_distance_constraint(pelvis, l_hip)
            self.add_distance_constraint(pelvis, r_hip)
            self.add_distance_constraint(l_hip, l_knee)
            self.add_distance_constraint(r_hip, r_knee)
            self.add_distance_constraint(l_knee, l_foot)
            self.add_distance_constraint(r_knee, r_foot)
            
            # Additional leg constraints for stability
            self.add_distance_constraint(l_hip, r_hip)
            
            # Angle constraints for natural joint rotation
            # Elbows
            self.add_angle_constraint(l_shoulder, l_elbow, l_hand)
            self.add_angle_constraint(r_shoulder, r_elbow, r_hand)
            
            # Knees
            self.add_angle_constraint(l_hip, l_knee, l_foot)
            self.add_angle_constraint(r_hip, r_knee, r_foot)
            
            # Spine
            self.add_angle_constraint(pelvis, chest, neck)
            
            # Assign to result dictionary
            points = {
                "pelvis": pelvis,
                "chest": chest,
                "neck": neck,
                "head": head,
                "l_shoulder": l_shoulder,
                "r_shoulder": r_shoulder,
                "l_elbow": l_elbow,
                "r_elbow": r_elbow,
                "l_hand": l_hand,
                "r_hand": r_hand,
                "l_hip": l_hip,
                "r_hip": r_hip,
                "l_knee": l_knee,
                "r_knee": r_knee,
                "l_foot": l_foot,
                "r_foot": r_foot
            }
            
        elif character_type == "quadruped":
            # Create a quadruped character rig (for animals/monsters)
            
            # Main body points
            rear = self.add_point(base_position + Vec3(-scale * 0.5, 0, scale * 0.7), mass=10.0)
            mid = self.add_point(base_position + Vec3(0, 0, scale * 0.7), mass=10.0)
            front = self.add_point(base_position + Vec3(scale * 0.5, 0, scale * 0.7), mass=10.0)
            neck = self.add_point(base_position + Vec3(scale * 0.7, 0, scale * 0.9), mass=5.0)
            head = self.add_point(base_position + Vec3(scale * 1.0, 0, scale * 1.0), mass=5.0)
            
            # Tail (for some creatures)
            tail_base = self.add_point(base_position + Vec3(-scale * 0.7, 0, scale * 0.7), mass=2.0)
            tail_mid = self.add_point(base_position + Vec3(-scale * 0.9, 0, scale * 0.8), mass=1.0)
            tail_tip = self.add_point(base_position + Vec3(-scale * 1.1, 0, scale * 0.9), mass=0.5)
            
            # Legs - front left
            fl_shoulder = self.add_point(base_position + Vec3(scale * 0.4, scale * 0.2, scale * 0.6), mass=4.0)
            fl_knee = self.add_point(base_position + Vec3(scale * 0.4, scale * 0.2, scale * 0.4), mass=2.0)
            fl_foot = self.add_point(base_position + Vec3(scale * 0.4, scale * 0.2, scale * 0.05), mass=1.0, fixed=True)
            
            # Front right
            fr_shoulder = self.add_point(base_position + Vec3(scale * 0.4, -scale * 0.2, scale * 0.6), mass=4.0)
            fr_knee = self.add_point(base_position + Vec3(scale * 0.4, -scale * 0.2, scale * 0.4), mass=2.0)
            fr_foot = self.add_point(base_position + Vec3(scale * 0.4, -scale * 0.2, scale * 0.05), mass=1.0, fixed=True)
            
            # Rear left
            rl_hip = self.add_point(base_position + Vec3(-scale * 0.4, scale * 0.2, scale * 0.6), mass=4.0)
            rl_knee = self.add_point(base_position + Vec3(-scale * 0.4, scale * 0.2, scale * 0.4), mass=2.0)
            rl_foot = self.add_point(base_position + Vec3(-scale * 0.4, scale * 0.2, scale * 0.05), mass=1.0, fixed=True)
            
            # Rear right
            rr_hip = self.add_point(base_position + Vec3(-scale * 0.4, -scale * 0.2, scale * 0.6), mass=4.0)
            rr_knee = self.add_point(base_position + Vec3(-scale * 0.4, -scale * 0.2, scale * 0.4), mass=2.0)
            rr_foot = self.add_point(base_position + Vec3(-scale * 0.4, -scale * 0.2, scale * 0.05), mass=1.0, fixed=True)
            
            # Body constraints
            self.add_distance_constraint(rear, mid)
            self.add_distance_constraint(mid, front)
            self.add_distance_constraint(front, neck)
            self.add_distance_constraint(neck, head)
            
            # Tail constraints
            self.add_distance_constraint(rear, tail_base)
            self.add_distance_constraint(tail_base, tail_mid)
            self.add_distance_constraint(tail_mid, tail_tip)
            
            # Front leg constraints
            self.add_distance_constraint(front, fl_shoulder)
            self.add_distance_constraint(front, fr_shoulder)
            self.add_distance_constraint(fl_shoulder, fl_knee)
            self.add_distance_constraint(fr_shoulder, fr_knee)
            self.add_distance_constraint(fl_knee, fl_foot)
            self.add_distance_constraint(fr_knee, fr_foot)
            
            # Rear leg constraints
            self.add_distance_constraint(rear, rl_hip)
            self.add_distance_constraint(rear, rr_hip)
            self.add_distance_constraint(rl_hip, rl_knee)
            self.add_distance_constraint(rr_hip, rr_knee)
            self.add_distance_constraint(rl_knee, rl_foot)
            self.add_distance_constraint(rr_knee, rr_foot)
            
            # Lateral stability (width)
            self.add_distance_constraint(fl_shoulder, fr_shoulder)
            self.add_distance_constraint(rl_hip, rr_hip)
            
            # Angle constraints
            self.add_angle_constraint(fl_shoulder, fl_knee, fl_foot)
            self.add_angle_constraint(fr_shoulder, fr_knee, fr_foot)
            self.add_angle_constraint(rl_hip, rl_knee, rl_foot)
            self.add_angle_constraint(rr_hip, rr_knee, rr_foot)
            
            # Spine angle
            self.add_angle_constraint(rear, mid, front)
            self.add_angle_constraint(mid, front, neck)
            
            # Tail angle
            self.add_angle_constraint(rear, tail_base, tail_mid)
            self.add_angle_constraint(tail_base, tail_mid, tail_tip)
            
            # Assign to result dictionary
            points = {
                "rear": rear,
                "mid": mid,
                "front": front,
                "neck": neck,
                "head": head,
                "tail_base": tail_base,
                "tail_mid": tail_mid,
                "tail_tip": tail_tip,
                "fl_shoulder": fl_shoulder,
                "fl_knee": fl_knee,
                "fl_foot": fl_foot,
                "fr_shoulder": fr_shoulder,
                "fr_knee": fr_knee,
                "fr_foot": fr_foot,
                "rl_hip": rl_hip,
                "rl_knee": rl_knee,
                "rl_foot": rl_foot,
                "rr_hip": rr_hip,
                "rr_knee": rr_knee,
                "rr_foot": rr_foot
            }
            
        else:
            # Simple fallback rig for unknown types
            pelvis = self.add_point(base_position + Vec3(0, 0, scale * 0.5), mass=10.0)
            chest = self.add_point(base_position + Vec3(0, 0, scale * 1.0), mass=10.0)
            head = self.add_point(base_position + Vec3(0, 0, scale * 1.5), mass=5.0)
            
            l_hand = self.add_point(base_position + Vec3(-scale * 0.5, 0, scale * 0.8), mass=3.0)
            r_hand = self.add_point(base_position + Vec3(scale * 0.5, 0, scale * 0.8), mass=3.0)
            l_foot = self.add_point(base_position + Vec3(-scale * 0.3, 0, scale * 0.1), mass=3.0, fixed=True)
            r_foot = self.add_point(base_position + Vec3(scale * 0.3, 0, scale * 0.1), mass=3.0, fixed=True)
            
            self.add_distance_constraint(pelvis, chest)
            self.add_distance_constraint(chest, head)
            self.add_distance_constraint(chest, l_hand)
            self.add_distance_constraint(chest, r_hand)
            self.add_distance_constraint(pelvis, l_foot)
            self.add_distance_constraint(pelvis, r_foot)
            
            points = {
                "pelvis": pelvis,
                "chest": chest,
                "head": head,
                "l_hand": l_hand,
                "r_hand": r_hand,
                "l_foot": l_foot,
                "r_foot": r_foot
            }
            
        return points 