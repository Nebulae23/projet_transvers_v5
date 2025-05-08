#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Verlet Physics Integration System for Nightfall Defenders
Implements a 3D point-mass physics system with Verlet integration
"""

import math
from typing import List, Tuple, Dict, Optional, Callable
from dataclasses import dataclass

from panda3d.core import Vec3, NodePath, LineSegs

class VerletPoint:
    """A point in the Verlet physics system"""
    
    def __init__(self, position: Vec3, mass: float = 1.0, fixed: bool = False):
        """
        Initialize a Verlet point
        
        Args:
            position: Initial position
            mass: Point mass
            fixed: Whether the point is fixed (immovable)
        """
        self.position = position.copy()
        self.old_position = position.copy()
        self.acceleration = Vec3(0, 0, 0)
        self.mass = max(0.01, mass)  # Avoid zero mass
        self.inv_mass = 1.0 / self.mass if not fixed else 0.0
        self.fixed = fixed
        self.accumulated_force = Vec3(0, 0, 0)
        
        # Environmental interaction properties
        self.friction = 0.95  # Friction coefficient
        self.bounce = 0.4     # Bounce coefficient
        self.colliding = False  # Whether point is colliding with environment
        self.normal = Vec3(0, 0, 1)  # Surface normal at collision point
        
        # User data for custom properties
        self.user_data = {}
    
    def update(self, dt: float, gravity: Vec3):
        """
        Update the point position using Verlet integration
        
        Args:
            dt: Time step
            gravity: Gravity vector
        """
        if self.fixed:
            return
            
        # Apply accumulated forces and gravity
        self.acceleration = self.accumulated_force * self.inv_mass + gravity
        
        # Reset accumulated force
        self.accumulated_force = Vec3(0, 0, 0)
        
        # Save current position
        temp = self.position.copy()
        
        # Verlet integration
        inertia = self.position - self.old_position
        
        # Apply friction to inertia if colliding
        if self.colliding:
            inertia *= self.friction
        
        # Update position
        self.position += inertia + self.acceleration * dt * dt
        
        # Save old position
        self.old_position = temp
    
    def apply_force(self, force: Vec3):
        """
        Apply a force to the point
        
        Args:
            force: Force vector
        """
        if self.fixed:
            return
            
        self.accumulated_force += force
    
    def set_position(self, position: Vec3):
        """
        Set the position of the point
        
        Args:
            position: New position
        """
        self.position = position.copy()
        self.old_position = position.copy()
    
    def move(self, delta: Vec3):
        """
        Move the point by a delta
        
        Args:
            delta: Position delta
        """
        if self.fixed:
            return
            
        self.position += delta

class Constraint:
    """Base class for physics constraints"""
    
    def solve(self) -> bool:
        """
        Solve the constraint
        
        Returns:
            True if constraint was applied, False otherwise
        """
        return False

class DistanceConstraint(Constraint):
    """Maintains a fixed distance between two points"""
    
    def __init__(self, point1: VerletPoint, point2: VerletPoint, 
                 distance: Optional[float] = None, stiffness: float = 1.0):
        """
        Initialize a distance constraint
        
        Args:
            point1: First point
            point2: Second point
            distance: Target distance (if None, use current distance)
            stiffness: Constraint stiffness (0-1)
        """
        self.point1 = point1
        self.point2 = point2
        
        # Use current distance if not specified
        if distance is None:
            distance = (point1.position - point2.position).length()
            
        self.rest_length = distance
        self.stiffness = max(0.01, min(1.0, stiffness))
    
    def solve(self) -> bool:
        """Solve the distance constraint"""
        # Vector from point1 to point2
        delta = self.point2.position - self.point1.position
        
        # Current distance
        current_dist = delta.length()
        
        # Avoid division by zero
        if current_dist < 0.00001:
            delta = Vec3(0.01, 0, 0)  # Arbitrary small vector
            current_dist = 0.01
        
        # Normalized direction
        direction = delta / current_dist
        
        # How far the points need to move
        diff = (current_dist - self.rest_length) * self.stiffness
        
        # Calculate movement based on mass
        total_inv_mass = self.point1.inv_mass + self.point2.inv_mass
        
        # Apply constraint only if at least one point is movable
        if total_inv_mass <= 0:
            return False
            
        # Calculate movement based on relative mass
        p1_move = direction * diff * (self.point1.inv_mass / total_inv_mass)
        p2_move = direction * diff * (self.point2.inv_mass / total_inv_mass) * -1
        
        # Apply movement
        self.point1.move(p1_move)
        self.point2.move(p2_move)
        
        return True

class AngleConstraint(Constraint):
    """Maintains a specific angle between three points"""
    
    def __init__(self, point1: VerletPoint, point2: VerletPoint, point3: VerletPoint,
                 angle: Optional[float] = None, stiffness: float = 0.5):
        """
        Initialize an angle constraint
        
        Args:
            point1: First point
            point2: Middle point (the angle vertex)
            point3: Third point
            angle: Target angle in radians (if None, use current angle)
            stiffness: Constraint stiffness (0-1)
        """
        self.point1 = point1
        self.point2 = point2  # Middle point
        self.point3 = point3
        self.stiffness = max(0.01, min(1.0, stiffness))
        
        # Constraint limits
        self.min_angle = 0.0  # Minimum angle in radians
        self.max_angle = math.pi  # Maximum angle in radians
        
        # Calculate current angle if not specified
        if angle is None:
            v1 = self.point1.position - self.point2.position
            v2 = self.point3.position - self.point2.position
            
            # Normalize vectors
            v1_length = v1.length()
            v2_length = v2.length()
            
            if v1_length > 0.00001 and v2_length > 0.00001:
                v1 = v1 / v1_length
                v2 = v2 / v2_length
                
                # Calculate dot product and clamp to avoid precision errors
                dot = max(-1.0, min(1.0, v1.dot(v2)))
                angle = math.acos(dot)
        
        self.target_angle = angle if angle is not None else math.pi / 2.0  # Default to 90 degrees
    
    def solve(self) -> bool:
        """Solve the angle constraint"""
        # Skip if any point is fixed
        if self.point1.fixed and self.point3.fixed:
            return False
            
        # Get vectors from middle point
        v1 = self.point1.position - self.point2.position
        v2 = self.point3.position - self.point2.position
        
        # Normalize vectors
        v1_length = v1.length()
        v2_length = v2.length()
        
        if v1_length < 0.00001 or v2_length < 0.00001:
            return False
            
        v1_normalized = v1 / v1_length
        v2_normalized = v2 / v2_length
        
        # Calculate current angle
        dot = max(-1.0, min(1.0, v1_normalized.dot(v2_normalized)))
        current_angle = math.acos(dot)
        
        # Clamp to limits
        target = max(self.min_angle, min(self.max_angle, self.target_angle))
        
        # Calculate angle difference
        angle_diff = current_angle - target
        
        # Skip if angle is already close enough
        if abs(angle_diff) < 0.01:
            return False
            
        # Cross product to determine rotation direction
        cross = v1_normalized.cross(v2_normalized)
        
        # Calculate rotation amount
        rotation_amount = angle_diff * self.stiffness
        
        # Calculate rotation axis
        rotation_axis = cross.normalized()
        
        # Apply rotation to points
        if not self.point1.fixed:
            # Rotate around point2
            rotated_v1 = self._rotate_vector(v1_normalized, rotation_axis, rotation_amount)
            self.point1.position = self.point2.position + rotated_v1 * v1_length
            
        if not self.point3.fixed:
            # Rotate in opposite direction
            rotated_v2 = self._rotate_vector(v2_normalized, rotation_axis, -rotation_amount)
            self.point3.position = self.point2.position + rotated_v2 * v2_length
            
        return True
    
    def _rotate_vector(self, vector: Vec3, axis: Vec3, angle: float) -> Vec3:
        """
        Rotate a vector around an axis
        
        Args:
            vector: Vector to rotate
            axis: Rotation axis
            angle: Rotation angle in radians
            
        Returns:
            Rotated vector
        """
        # Rodrigues rotation formula
        cos_angle = math.cos(angle)
        sin_angle = math.sin(angle)
        
        return vector * cos_angle + axis.cross(vector) * sin_angle + axis * axis.dot(vector) * (1 - cos_angle)

class VerletSystem:
    """Manages a collection of Verlet points and constraints"""
    
    def __init__(self):
        """Initialize the Verlet physics system"""
        self.points: List[VerletPoint] = []
        self.constraints: List[Constraint] = []
        self.gravity = Vec3(0, 0, -9.81)
        self.time_accumulator = 0.0
        
        # Collision handling
        self.collision_objects: List[Dict] = []
        
        # Debug visualization
        self.debug_node = None
        self.debug_enabled = False
    
    def add_point(self, position: Vec3, mass: float = 1.0, fixed: bool = False) -> VerletPoint:
        """
        Add a point to the system
        
        Args:
            position: Initial position
            mass: Point mass
            fixed: Whether the point is fixed
            
        Returns:
            Created VerletPoint
        """
        point = VerletPoint(position, mass, fixed)
        self.points.append(point)
        return point
    
    def add_distance_constraint(self, point1: VerletPoint, point2: VerletPoint, 
                              distance: Optional[float] = None, stiffness: float = 1.0) -> DistanceConstraint:
        """
        Add a distance constraint
        
        Args:
            point1: First point
            point2: Second point
            distance: Target distance (if None, use current distance)
            stiffness: Constraint stiffness (0-1)
            
        Returns:
            Created constraint
        """
        constraint = DistanceConstraint(point1, point2, distance, stiffness)
        self.constraints.append(constraint)
        return constraint
    
    def add_angle_constraint(self, point1: VerletPoint, point2: VerletPoint, point3: VerletPoint,
                          angle: Optional[float] = None, stiffness: float = 0.5) -> AngleConstraint:
        """
        Add an angle constraint
        
        Args:
            point1: First point
            point2: Middle point (the angle vertex)
            point3: Third point
            angle: Target angle in radians (if None, use current angle)
            stiffness: Constraint stiffness (0-1)
            
        Returns:
            Created constraint
        """
        constraint = AngleConstraint(point1, point2, point3, angle, stiffness)
        self.constraints.append(constraint)
        return constraint
    
    def add_collision_box(self, min_point: Vec3, max_point: Vec3, friction: float = 0.9, bounce: float = 0.3):
        """
        Add a box collision object
        
        Args:
            min_point: Minimum corner
            max_point: Maximum corner
            friction: Friction coefficient
            bounce: Bounce coefficient
        """
        self.collision_objects.append({
            "type": "box",
            "min": min_point,
            "max": max_point,
            "friction": friction,
            "bounce": bounce
        })
    
    def add_collision_plane(self, normal: Vec3, distance: float, friction: float = 0.9, bounce: float = 0.3):
        """
        Add a plane collision object
        
        Args:
            normal: Plane normal
            distance: Plane distance from origin
            friction: Friction coefficient
            bounce: Bounce coefficient
        """
        self.collision_objects.append({
            "type": "plane",
            "normal": normal.normalized(),
            "distance": distance,
            "friction": friction,
            "bounce": bounce
        })
    
    def update(self, dt: float, substeps: int = 8):
        """
        Update the physics system
        
        Args:
            dt: Time step
            substeps: Number of simulation substeps
        """
        # Update time accumulator for animation cycles
        self.time_accumulator += dt
        
        # Calculate substep time
        substep_dt = dt / substeps
        
        # Run simulation substeps
        for _ in range(substeps):
            # Apply Verlet integration
            for point in self.points:
                point.update(substep_dt, self.gravity)

            # Handle collisions
            self._handle_collisions(substep_dt)
        
        # Solve constraints multiple times for stability
        constraint_iterations = 2
        for _ in range(constraint_iterations):
            for constraint in self.constraints:
                constraint.solve()
    
    def _handle_collisions(self, dt: float):
        """
        Handle collisions with environment
        
        Args:
            dt: Time step
        """
        # Reset collision flags
        for point in self.points:
            point.colliding = False
        
        # Check each point against all collision objects
        for point in self.points:
            if point.fixed:
                continue
                
            for collision_obj in self.collision_objects:
                if collision_obj["type"] == "box":
                    self._handle_box_collision(point, collision_obj, dt)
                elif collision_obj["type"] == "plane":
                    self._handle_plane_collision(point, collision_obj, dt)
    
    def _handle_box_collision(self, point: VerletPoint, box: Dict, dt: float):
        """
        Handle collision with a box
        
        Args:
            point: Verlet point
            box: Box collision object
            dt: Time step
        """
        # Check if point is inside box
        min_point = box["min"]
        max_point = box["max"]
        
        if (point.position.x >= min_point.x and point.position.x <= max_point.x and
            point.position.y >= min_point.y and point.position.y <= max_point.y and
            point.position.z >= min_point.z and point.position.z <= max_point.z):
            
            # Find closest face for collision normal
            distances = [
                (point.position.x - min_point.x, Vec3(-1, 0, 0)),  # Left
                (max_point.x - point.position.x, Vec3(1, 0, 0)),   # Right
                (point.position.y - min_point.y, Vec3(0, -1, 0)),  # Back
                (max_point.y - point.position.y, Vec3(0, 1, 0)),   # Front
                (point.position.z - min_point.z, Vec3(0, 0, -1)),  # Bottom
                (max_point.z - point.position.z, Vec3(0, 0, 1))    # Top
            ]
            
            # Find closest face
            min_dist = float('inf')
            normal = Vec3(0, 0, 1)  # Default
            
            for dist, norm in distances:
                if dist < min_dist:
                    min_dist = dist
                    normal = norm
            
            # Update collision properties
            point.colliding = True
            point.normal = normal
            point.friction = box["friction"]
            point.bounce = box["bounce"]
            
            # Apply collision response
            correction = min_dist * normal
            point.position += correction
            
            # Apply bounce - modify the velocity component along the normal
            velocity = (point.position - point.old_position) / dt
            normal_vel = velocity.dot(normal)
            
            if normal_vel < 0:  # Only bounce if moving toward the surface
                bounce_vel = normal_vel * -point.bounce
                delta_vel = (bounce_vel - normal_vel) * normal
                
                # Adjust position to simulate bounce
                point.old_position -= delta_vel * dt
    
    def _handle_plane_collision(self, point: VerletPoint, plane: Dict, dt: float):
        """
        Handle collision with a plane
        
        Args:
            point: Verlet point
            plane: Plane collision object
            dt: Time step
        """
        normal = plane["normal"]
        distance = plane["distance"]
        
        # Calculate signed distance from point to plane
        signed_distance = normal.dot(point.position) - distance
        
        # Check if point is on negative side of plane (colliding)
        if signed_distance < 0:
            # Update collision properties
            point.colliding = True
            point.normal = normal
            point.friction = plane["friction"]
            point.bounce = plane["bounce"]
            
            # Apply collision response
            correction = normal * -signed_distance
            point.position += correction
            
            # Apply bounce - modify the velocity component along the normal
            velocity = (point.position - point.old_position) / dt
            normal_vel = velocity.dot(normal)
            
            if normal_vel < 0:  # Only bounce if moving toward the surface
                bounce_vel = normal_vel * -point.bounce
                delta_vel = (bounce_vel - normal_vel) * normal
                
                # Adjust position to simulate bounce
                point.old_position -= delta_vel * dt
    
    def set_gravity(self, gravity: Vec3):
        """
        Set the gravity vector
        
        Args:
            gravity: Gravity vector
        """
        self.gravity = gravity
    
    def enable_debug_visualization(self, render_node: NodePath):
        """
        Enable debug visualization
        
        Args:
            render_node: Node to attach visualization to
        """
        if self.debug_node:
            self.debug_node.removeNode()
            
        self.debug_node = render_node.attachNewNode("verlet_debug")
        self.debug_enabled = True
    
    def update_debug_visualization(self):
        """Update the debug visualization if enabled"""
        if not self.debug_enabled or not self.debug_node:
            return
            
        # Clear existing visualization
        self.debug_node.removeNode()
        self.debug_node = self.debug_node.getParent().attachNewNode("verlet_debug")
        
        # Draw points
        point_segs = LineSegs()
        point_segs.setThickness(4.0)
        point_segs.setColor(1.0, 1.0, 0.0, 1.0)  # Yellow
        
        for point in self.points:
            point_size = 0.05
            if point.fixed:
                point_segs.setColor(1.0, 0.0, 0.0, 1.0)  # Red for fixed points
            elif point.colliding:
                point_segs.setColor(0.0, 1.0, 0.0, 1.0)  # Green for colliding points
            else:
                point_segs.setColor(1.0, 1.0, 0.0, 1.0)  # Yellow for normal points
                
            # Draw a small cross
            point_segs.moveTo(point.position + Vec3(point_size, 0, 0))
            point_segs.drawTo(point.position - Vec3(point_size, 0, 0))
            point_segs.moveTo(point.position + Vec3(0, point_size, 0))
            point_segs.drawTo(point.position - Vec3(0, point_size, 0))
            point_segs.moveTo(point.position + Vec3(0, 0, point_size))
            point_segs.drawTo(point.position - Vec3(0, 0, point_size))
            
        self.debug_node.attachNewNode(point_segs.create())
        
        # Draw constraints
        constraint_segs = LineSegs()
        constraint_segs.setThickness(2.0)
        constraint_segs.setColor(0.0, 0.7, 1.0, 1.0)  # Cyan
        
        for constraint in self.constraints:
            if isinstance(constraint, DistanceConstraint):
                constraint_segs.moveTo(constraint.point1.position)
                constraint_segs.drawTo(constraint.point2.position)
                
        self.debug_node.attachNewNode(constraint_segs.create())
        
        # Draw collision objects
        collision_segs = LineSegs()
        collision_segs.setThickness(1.0)
        collision_segs.setColor(1.0, 0.5, 0.0, 0.7)  # Orange
        
        for collision_obj in self.collision_objects:
            if collision_obj["type"] == "box":
                min_point = collision_obj["min"]
                max_point = collision_obj["max"]
                
                # Draw box wireframe
                # Bottom face
                collision_segs.moveTo(Vec3(min_point.x, min_point.y, min_point.z))
                collision_segs.drawTo(Vec3(max_point.x, min_point.y, min_point.z))
                collision_segs.drawTo(Vec3(max_point.x, max_point.y, min_point.z))
                collision_segs.drawTo(Vec3(min_point.x, max_point.y, min_point.z))
                collision_segs.drawTo(Vec3(min_point.x, min_point.y, min_point.z))
                
                # Top face
                collision_segs.moveTo(Vec3(min_point.x, min_point.y, max_point.z))
                collision_segs.drawTo(Vec3(max_point.x, min_point.y, max_point.z))
                collision_segs.drawTo(Vec3(max_point.x, max_point.y, max_point.z))
                collision_segs.drawTo(Vec3(min_point.x, max_point.y, max_point.z))
                collision_segs.drawTo(Vec3(min_point.x, min_point.y, max_point.z))
                
                # Connecting edges
                collision_segs.moveTo(Vec3(min_point.x, min_point.y, min_point.z))
                collision_segs.drawTo(Vec3(min_point.x, min_point.y, max_point.z))
                
                collision_segs.moveTo(Vec3(max_point.x, min_point.y, min_point.z))
                collision_segs.drawTo(Vec3(max_point.x, min_point.y, max_point.z))
                
                collision_segs.moveTo(Vec3(max_point.x, max_point.y, min_point.z))
                collision_segs.drawTo(Vec3(max_point.x, max_point.y, max_point.z))
                
                collision_segs.moveTo(Vec3(min_point.x, max_point.y, min_point.z))
                collision_segs.drawTo(Vec3(min_point.x, max_point.y, max_point.z))
                
            elif collision_obj["type"] == "plane":
                # Draw plane as a grid (simplified representation)
                normal = collision_obj["normal"]
                distance = collision_obj["distance"]
                
                # Find a point on the plane
                point_on_plane = normal * distance
                
                # Create basis vectors on the plane
                v1 = Vec3(1, 0, 0)
                if abs(normal.dot(v1)) > 0.9:
                    v1 = Vec3(0, 1, 0)  # Choose a different vector if too aligned
                
                v2 = normal.cross(v1).normalized()
                v1 = v2.cross(normal).normalized()
                
                # Scale vectors
                v1 *= 5.0
                v2 *= 5.0
                
                # Draw a grid
                grid_size = 5
                for i in range(-grid_size, grid_size+1):
                    collision_segs.moveTo(point_on_plane + v1 * i - v2 * grid_size)
                    collision_segs.drawTo(point_on_plane + v1 * i + v2 * grid_size)
                    
                    collision_segs.moveTo(point_on_plane + v2 * i - v1 * grid_size)
                    collision_segs.drawTo(point_on_plane + v2 * i + v1 * grid_size)
                    
        self.debug_node.attachNewNode(collision_segs.create()) 