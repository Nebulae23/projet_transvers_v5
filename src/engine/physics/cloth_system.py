#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Cloth Simulation System using Verlet Physics for Nightfall Defenders
Implements cloth simulation for capes, banners, and other fabric
"""

import math
import random
from typing import List, Tuple, Dict, Optional
from panda3d.core import (
    Vec3, Point3, NodePath, Geom, GeomNode, GeomVertexFormat, GeomVertexData,
    GeomVertexWriter, GeomTriangles, GeomVertexRewriter, InternalName,
    LineSegs, TransparencyAttrib
)

from src.engine.physics.verlet import VerletSystem, VerletPoint, DistanceConstraint

class ClothSystem:
    """Simulates cloth using Verlet physics"""
    
    def __init__(self, verlet_system: Optional[VerletSystem] = None):
        """
        Initialize cloth simulation system
        
        Args:
            verlet_system: Optional existing VerletSystem to use
        """
        self.verlet_system = verlet_system if verlet_system else VerletSystem()
        
        # Wind force
        self.wind_direction = Vec3(1.0, 0.0, 0.0)
        self.wind_strength = 0.0
        self.wind_turbulence = 0.3
        self.time_accumulator = 0.0
        
        # Cloth collision sphere list
        self.collision_spheres = []
        
        # For tracking a created cloth object
        self.cloths = []
    
    def create_cloth_grid(self, 
                         position: Vec3, 
                         width: float, 
                         height: float, 
                         rows: int, 
                         cols: int, 
                         fixed_top: bool = True,
                         stiffness: float = 0.8,
                         mass: float = 1.0) -> Dict:
        """
        Create a cloth grid of Verlet points
        
        Args:
            position: Position of top left corner
            width: Width of cloth
            height: Height of cloth
            rows: Number of rows (points)
            cols: Number of columns (points)
            fixed_top: Whether to fix the top row of points
            stiffness: Stiffness of cloth constraints (0-1)
            mass: Mass per cloth point
            
        Returns:
            Dictionary with cloth data
        """
        # Create a grid of points
        points = []
        
        for r in range(rows):
            row_points = []
            for c in range(cols):
                # Calculate position within the grid
                x = position.x + (c / (cols - 1)) * width
                y = position.y
                z = position.z - (r / (rows - 1)) * height
                
                # Set top row as fixed if requested
                is_fixed = (r == 0 and fixed_top)
                
                # Add point to the Verlet system
                point = self.verlet_system.add_point(Vec3(x, y, z), mass, is_fixed)
                row_points.append(point)
            
            points.append(row_points)
        
        # Create distance constraints for the grid structure
        horizontal_constraints = []
        vertical_constraints = []
        diagonal_constraints = []
        
        # Horizontal constraints (along rows)
        for r in range(rows):
            row_constraints = []
            for c in range(cols - 1):
                constraint = self.verlet_system.add_distance_constraint(
                    points[r][c], points[r][c + 1], None, stiffness
                )
                row_constraints.append(constraint)
            horizontal_constraints.append(row_constraints)
        
        # Vertical constraints (along columns)
        for c in range(cols):
            col_constraints = []
            for r in range(rows - 1):
                constraint = self.verlet_system.add_distance_constraint(
                    points[r][c], points[r + 1][c], None, stiffness
                )
                col_constraints.append(constraint)
            vertical_constraints.append(col_constraints)
        
        # Diagonal constraints for added stability
        for r in range(rows - 1):
            diag_row_constraints = []
            for c in range(cols - 1):
                # Diagonal: top-left to bottom-right
                constraint1 = self.verlet_system.add_distance_constraint(
                    points[r][c], points[r + 1][c + 1], None, stiffness * 0.8
                )
                diag_row_constraints.append(constraint1)
                
                # Diagonal: top-right to bottom-left
                constraint2 = self.verlet_system.add_distance_constraint(
                    points[r][c + 1], points[r + 1][c], None, stiffness * 0.8
                )
                diag_row_constraints.append(constraint2)
            diagonal_constraints.append(diag_row_constraints)
        
        # Store and return cloth data
        cloth_data = {
            "points": points,
            "rows": rows,
            "cols": cols,
            "horizontal_constraints": horizontal_constraints,
            "vertical_constraints": vertical_constraints,
            "diagonal_constraints": diagonal_constraints,
            "position": position,
            "width": width,
            "height": height,
            "mesh_node": None,
            "vertex_data": None
        }
        
        self.cloths.append(cloth_data)
        return cloth_data
    
    def create_cloth_mesh(self, cloth_data: Dict, render_node: NodePath, 
                         texture_path: str = None) -> NodePath:
        """
        Create a visible mesh for the cloth
        
        Args:
            cloth_data: Cloth data from create_cloth_grid
            render_node: Parent node to attach the mesh to
            texture_path: Optional texture path
            
        Returns:
            NodePath to the created mesh
        """
        points = cloth_data["points"]
        rows = cloth_data["rows"]
        cols = cloth_data["cols"]
        
        # Create vertex format with position, normal, and texture coordinates
        format = GeomVertexFormat.getV3n3t2()
        vdata = GeomVertexData("cloth", format, Geom.UHDynamic)
        
        # Create writers for each data column
        vertex = GeomVertexWriter(vdata, "vertex")
        normal = GeomVertexWriter(vdata, "normal")
        texcoord = GeomVertexWriter(vdata, "texcoord")
        
        # Add all points as vertices
        for r in range(rows):
            for c in range(cols):
                point = points[r][c]
                vertex.addData3(point.position)
                normal.addData3(0, 1, 0)  # Initial normal facing forward
                texcoord.addData2(c / (cols - 1), 1.0 - r / (rows - 1))
        
        # Create triangles
        tris = GeomTriangles(Geom.UHDynamic)
        
        for r in range(rows - 1):
            for c in range(cols - 1):
                # Calculate vertex indices for each quad
                i0 = r * cols + c
                i1 = r * cols + (c + 1)
                i2 = (r + 1) * cols + c
                i3 = (r + 1) * cols + (c + 1)
                
                # First triangle
                tris.addVertices(i0, i2, i1)
                tris.closePrimitive()
                
                # Second triangle
                tris.addVertices(i1, i2, i3)
                tris.closePrimitive()
        
        # Create the Geom and GeomNode
        geom = Geom(vdata)
        geom.addPrimitive(tris)
        
        gnode = GeomNode("cloth_mesh")
        gnode.addGeom(geom)
        
        # Create and position the node path
        cloth_np = render_node.attachNewNode(gnode)
        
        # Apply texture if provided
        if texture_path:
            cloth_np.setTexture(loader.loadTexture(texture_path))
        
        # Save data for updates
        cloth_data["mesh_node"] = cloth_np
        cloth_data["vertex_data"] = vdata
        
        # Enable transparency if texture has alpha channel
        cloth_np.setTransparency(TransparencyAttrib.MDual)
        
        return cloth_np
    
    def update_cloth_mesh(self, cloth_data: Dict):
        """
        Update the cloth mesh to match physics simulation
        
        Args:
            cloth_data: Cloth data dictionary
        """
        if not cloth_data["mesh_node"]:
            return
            
        points = cloth_data["points"]
        rows = cloth_data["rows"]
        cols = cloth_data["cols"]
        vdata = cloth_data["vertex_data"]
        
        # Rewriter to modify vertex positions
        vertex_rewriter = GeomVertexRewriter(vdata, "vertex")
        normal_rewriter = GeomVertexRewriter(vdata, "normal")
        
        # Reset to beginning of data
        vertex_rewriter.setRow(0)
        normal_rewriter.setRow(0)
        
        # Update vertex positions from physics points
        for r in range(rows):
            for c in range(cols):
                point = points[r][c]
                vertex_rewriter.setData3(point.position)
                
                # Calculate and update normals
                if r < rows - 1 and c < cols - 1:
                    # Get three nearby points to calculate normal
                    p0 = points[r][c].position
                    p1 = points[r][c + 1].position
                    p2 = points[r + 1][c].position
                    
                    # Calculate normal using cross product
                    v1 = p1 - p0
                    v2 = p2 - p0
                    normal_vec = v1.cross(v2)
                    normal_vec.normalize()
                    
                    normal_rewriter.setData3(normal_vec)
                else:
                    # Use previous normal for edge points
                    normal_rewriter.setData3(0, 1, 0)
    
    def apply_wind_force(self, dt: float):
        """
        Apply wind forces to cloth points
        
        Args:
            dt: Time delta in seconds
        """
        # Update time for turbulence
        self.time_accumulator += dt
        
        for cloth_data in self.cloths:
            points = cloth_data["points"]
            rows = cloth_data["rows"]
            cols = cloth_data["cols"]
            
            for r in range(rows):
                for c in range(cols):
                    # Skip fixed points
                    if points[r][c].fixed:
                        continue
                    
                    # Calculate turbulence factor (varies over time)
                    turbulence_x = math.sin(self.time_accumulator * 2.0 + r * 0.3 + c * 0.2) * self.wind_turbulence
                    turbulence_y = math.cos(self.time_accumulator * 2.5 + r * 0.4 + c * 0.3) * self.wind_turbulence
                    turbulence_z = math.sin(self.time_accumulator * 3.0 + r * 0.2 + c * 0.4) * self.wind_turbulence
                    
                    # Apply turbulent wind force
                    wind = self.wind_direction * self.wind_strength
                    wind += Vec3(turbulence_x, turbulence_y, turbulence_z) * self.wind_strength
                    
                    # Apply the force
                    points[r][c].apply_force(wind)
    
    def add_collision_sphere(self, center: Vec3, radius: float):
        """
        Add a sphere that the cloth will collide with
        
        Args:
            center: Center position of the sphere
            radius: Radius of the collision sphere
        """
        self.collision_spheres.append({
            "center": center,
            "radius": radius
        })
    
    def handle_sphere_collisions(self):
        """Handle collisions between cloth points and spheres"""
        # Process each cloth
        for cloth_data in self.cloths:
            points = cloth_data["points"]
            rows = cloth_data["rows"]
            cols = cloth_data["cols"]
            
            # Check each point against all spheres
            for r in range(rows):
                for c in range(cols):
                    point = points[r][c]
                    
                    # Skip fixed points
                    if point.fixed:
                        continue
                    
                    # Check against all collision spheres
                    for sphere in self.collision_spheres:
                        center = sphere["center"]
                        radius = sphere["radius"]
                        
                        # Calculate vector from sphere to point
                        to_point = point.position - center
                        distance = to_point.length()
                        
                        # If point is inside the sphere, push it out
                        if distance < radius:
                            # Calculate pushout vector (normalize and scale by penetration depth)
                            if distance > 0.0001:
                                pushout = to_point * (radius / distance - 1.0)
                            else:
                                # Point is exactly at center, push in random direction
                                pushout = Vec3(random.uniform(-0.1, 0.1), 
                                            random.uniform(-0.1, 0.1),
                                            random.uniform(-0.1, 0.1)).normalized() * radius
                            
                            # Move the point outside the sphere
                            point.position += pushout
    
    def update(self, dt: float):
        """
        Update the cloth simulation
        
        Args:
            dt: Time delta in seconds
        """
        # Apply wind forces
        self.apply_wind_force(dt)
        
        # Handle sphere collisions
        self.handle_sphere_collisions()
        
        # Update all cloth meshes
        for cloth_data in self.cloths:
            self.update_cloth_mesh(cloth_data)
    
    def set_wind(self, direction: Vec3, strength: float, turbulence: float = 0.3):
        """
        Set wind parameters
        
        Args:
            direction: Wind direction vector (will be normalized)
            strength: Wind strength
            turbulence: Wind turbulence factor (0-1)
        """
        # Normalize direction
        if direction.length_squared() > 0.0001:
            self.wind_direction = direction.normalized()
        else:
            self.wind_direction = Vec3(1, 0, 0)
            
        self.wind_strength = max(0.0, strength)
        self.wind_turbulence = max(0.0, min(1.0, turbulence))
    
    def tear_cloth(self, cloth_data: Dict, tear_position: Vec3, tear_radius: float):
        """
        Tear the cloth around a point
        
        Args:
            cloth_data: Cloth data to modify
            tear_position: Center of the tear
            tear_radius: Radius of the tear area
        """
        points = cloth_data["points"]
        rows = cloth_data["rows"]
        cols = cloth_data["cols"]
        
        # Remove constraints within the tear area
        horizontal = cloth_data["horizontal_constraints"]
        vertical = cloth_data["vertical_constraints"]
        diagonal = cloth_data["diagonal_constraints"]
        
        # Track constraints to remove
        to_remove = []
        
        # Check horizontal constraints
        for r in range(rows):
            for c in range(cols - 1):
                point_a = points[r][c]
                point_b = points[r][c + 1]
                constraint = horizontal[r][c]
                
                # Check if midpoint of constraint is within tear radius
                midpoint = (point_a.position + point_b.position) * 0.5
                if (midpoint - tear_position).length() < tear_radius:
                    to_remove.append(constraint)
        
        # Check vertical constraints
        for c in range(cols):
            for r in range(rows - 1):
                point_a = points[r][c]
                point_b = points[r + 1][c]
                constraint = vertical[c][r]
                
                # Check if midpoint of constraint is within tear radius
                midpoint = (point_a.position + point_b.position) * 0.5
                if (midpoint - tear_position).length() < tear_radius:
                    to_remove.append(constraint)
        
        # Check diagonal constraints
        for r in range(rows - 1):
            for c in range(cols - 1):
                # Diagonal: top-left to bottom-right
                point_a = points[r][c]
                point_b = points[r + 1][c + 1]
                constraint1 = diagonal[r][c * 2]
                
                # Check if midpoint of constraint is within tear radius
                midpoint = (point_a.position + point_b.position) * 0.5
                if (midpoint - tear_position).length() < tear_radius:
                    to_remove.append(constraint1)
                
                # Diagonal: top-right to bottom-left
                point_a = points[r][c + 1]
                point_b = points[r + 1][c]
                constraint2 = diagonal[r][c * 2 + 1]
                
                # Check if midpoint of constraint is within tear radius
                midpoint = (point_a.position + point_b.position) * 0.5
                if (midpoint - tear_position).length() < tear_radius:
                    to_remove.append(constraint2)
        
        # Remove constraints from the Verlet system
        for constraint in to_remove:
            if constraint in self.verlet_system.constraints:
                self.verlet_system.constraints.remove(constraint)
    
    def create_flag(self, position: Vec3, width: float, height: float, 
                  pole_offset: float = 0.1, render_node: NodePath = None,
                  texture_path: str = None) -> Dict:
        """
        Create a flag with fixed left side
        
        Args:
            position: Top of flag pole position
            width: Flag width
            height: Flag height
            pole_offset: Offset from pole
            render_node: Node to attach visuals to
            texture_path: Optional texture path
            
        Returns:
            Cloth data dictionary
        """
        # Determine appropriate number of vertices
        rows = max(5, int(height * 5))
        cols = max(7, int(width * 7))
        
        # Create position with offset from pole
        flag_pos = position + Vec3(pole_offset, 0, 0)
        
        # Create the cloth grid, fixing the left side
        cloth_data = self.create_cloth_grid(
            flag_pos, width, height, rows, cols,
            fixed_top=False,  # Don't fix the top edge
            stiffness=0.7,    # More flexible for flag
            mass=0.8          # Lighter mass
        )
        
        # Fix all points on the left edge
        for r in range(rows):
            cloth_data["points"][r][0].fixed = True
        
        # Create the mesh if render_node provided
        if render_node:
            self.create_cloth_mesh(cloth_data, render_node, texture_path)
        
        return cloth_data
    
    def create_cape(self, position: Vec3, width: float, height: float, 
                   shoulder_curve: float = 0.3, render_node: NodePath = None,
                   texture_path: str = None) -> Dict:
        """
        Create a cape attached at the top
        
        Args:
            position: Position of cape top center
            width: Cape width
            height: Cape height
            shoulder_curve: Amount of curve at the shoulders (0-1)
            render_node: Node to attach visuals to
            texture_path: Optional texture path
            
        Returns:
            Cloth data dictionary
        """
        # Determine appropriate number of vertices
        rows = max(8, int(height * 8))
        cols = max(6, int(width * 6))
        
        # Calculate top left corner position
        top_left = position + Vec3(-width/2, 0, 0)
        
        # Create the cloth grid, fixing the top edge
        cloth_data = self.create_cloth_grid(
            top_left, width, height, rows, cols,
            fixed_top=True,
            stiffness=0.6,  # More flexible for cape
            mass=1.2        # Heavier mass for cloth
        )
        
        # Apply shoulder curve to top row
        if shoulder_curve > 0:
            top_row = cloth_data["points"][0]
            for c in range(cols):
                # Calculate a curve factor (0 at edges, max in middle)
                normalized_pos = c / (cols - 1)
                curve_factor = math.sin(normalized_pos * math.pi) * shoulder_curve
                
                # Lower the point based on curve factor
                top_row[c].position.z -= height * curve_factor
        
        # Create the mesh if render_node provided
        if render_node:
            self.create_cloth_mesh(cloth_data, render_node, texture_path)
        
        return cloth_data 