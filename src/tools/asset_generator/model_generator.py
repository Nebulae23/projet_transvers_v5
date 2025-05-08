#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
3D Model Generator for Nightfall Defenders
Generates procedural 3D models for buildings, props and environmental features
"""

import os
import random
import math
import numpy as np
from panda3d.core import NodePath, PandaNode, GeomNode
from panda3d.core import GeomVertexFormat, GeomVertexData, Geom
from panda3d.core import GeomTriangles, GeomVertexWriter
from panda3d.core import Point3, Vec3, Vec4, LVector3
from panda3d.core import TransformState, Mat4, LMatrix4f
from panda3d.core import Filename, LoaderOptions
from enum import Enum

from src.tools.asset_generator.base_generator import AssetGenerator, AssetType, AssetCategory

class ModelType(Enum):
    """Types of 3D models that can be generated"""
    PROP = "prop"
    BUILDING = "building"
    CHARACTER = "character"
    TERRAIN = "terrain"
    EFFECT = "effect"

class ModelGenerator(AssetGenerator):
    """Générateur de modèles 3D procéduraux pour Panda3D"""
    
    def __init__(self, output_dir):
        """
        Initialise le générateur de modèles 3D
        
        Args:
            output_dir (str): Répertoire de sortie pour les modèles générés
        """
        super().__init__(output_dir)
        
        # Créer des sous-répertoires pour différentes catégories de modèles
        self.model_dirs = {
            ModelType.BUILDING: os.path.join(output_dir, "buildings"),
            ModelType.PROP: os.path.join(output_dir, "props"),
            ModelType.TERRAIN: os.path.join(output_dir, "terrain"),
            ModelType.EFFECT: os.path.join(output_dir, "effects"),
            ModelType.CHARACTER: os.path.join(output_dir, "characters")
        }
        
        for directory in self.model_dirs.values():
            os.makedirs(directory, exist_ok=True)
    
    def generate(self, asset_id, asset_params, seed=None):
        """
        Génère un modèle 3D selon les paramètres spécifiés
        
        Args:
            asset_id (str): Identifiant du modèle
            asset_params (dict): Paramètres de génération incluant le type de modèle
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            NodePath: Le modèle 3D généré
        """
        if seed is not None:
            random.seed(seed)
            np.random.seed(seed)
        
        # Extraire les paramètres
        model_type = asset_params.get("model_type", ModelType.PROP)
        model_subtype = asset_params.get("model_subtype", "generic")
        
        # Générer le modèle selon son type
        if model_type == ModelType.BUILDING:
            return self._generate_building(asset_id, asset_params)
        elif model_type == ModelType.PROP:
            return self._generate_prop(asset_id, asset_params)
        elif model_type == ModelType.TERRAIN:
            return self._generate_terrain_feature(asset_id, asset_params)
        elif model_type == ModelType.EFFECT:
            return self._generate_effect(asset_id, asset_params)
        elif model_type == ModelType.CHARACTER:
            return self._generate_character(asset_id, asset_params)
        else:
            # Type inconnu, générer un modèle par défaut (cube)
            return self._generate_default_model(asset_id, asset_params)
    
    def _generate_building(self, asset_id, params):
        """Génère un modèle de bâtiment 3D"""
        # Extraire les paramètres pertinents
        building_type = params.get("building_subtype", "house")
        width = params.get("width", 5.0)
        depth = params.get("depth", 5.0)
        height = params.get("height", 3.0)
        
        # Créer un nœud racine pour le bâtiment
        building_node = NodePath(PandaNode(f"building_{asset_id}"))
        
        # Générer selon le type de bâtiment
        if building_type == "house":
            self._generate_house(building_node, width, depth, height)
        elif building_type == "tower":
            self._generate_tower(building_node, width, depth, height)
        elif building_type == "wall":
            self._generate_wall(building_node, width, height)
        else:
            # Type inconnu, générer une maison générique
            self._generate_house(building_node, width, depth, height)
        
        return building_node
    
    def _generate_prop(self, asset_id, params):
        """Génère un modèle de prop 3D (objet, rocher, arbre, etc.)"""
        # Extraire les paramètres pertinents
        prop_type = params.get("prop_subtype", "rock")
        
        # Créer un nœud racine pour le prop
        prop_node = NodePath(PandaNode(f"prop_{asset_id}"))
        
        # Générer selon le type de prop
        if prop_type == "rock":
            self._generate_rock(prop_node, params)
        elif prop_type == "tree":
            self._generate_tree(prop_node, params)
        elif prop_type == "chest":
            self._generate_chest(prop_node, params)
        else:
            # Type inconnu, générer un cube
            self._generate_default_model(asset_id, params)
        
        return prop_node
    
    def _generate_terrain_feature(self, asset_id, params):
        """Génère un élément de terrain 3D"""
        # Créer un nœud racine pour la caractéristique de terrain
        terrain_node = NodePath(PandaNode(f"terrain_{asset_id}"))
        
        # Génération à implémenter
        
        return terrain_node
    
    def _generate_effect(self, asset_id, params):
        """Génère un effet 3D"""
        # Créer un nœud racine pour l'effet
        effect_node = NodePath(PandaNode(f"effect_{asset_id}"))
        
        # Génération à implémenter
        
        return effect_node
    
    def _generate_character(self, asset_id, params):
        """Génère un personnage 3D"""
        # Créer un nœud racine pour le personnage
        character_node = NodePath(PandaNode(f"character_{asset_id}"))
        
        # Génération à implémenter
        
        return character_node
    
    def _generate_default_model(self, asset_id, params):
        """Génère un modèle par défaut (cube)"""
        # Créer un nœud pour le modèle par défaut
        default_node = NodePath(PandaNode(f"default_{asset_id}"))
        
        # Créer un cube simple
        size = params.get("size", 1.0)
        color = params.get("color", (0.7, 0.7, 0.7, 1.0))
        
        # Génération à implémenter
        
        return default_node
    
    def _generate_house(self, parent_node, width, depth, height):
        """
        Génère un modèle de maison simple
        
        Args:
            parent_node: Nœud parent auquel attacher la maison
            width: Largeur de la maison
            depth: Profondeur de la maison
            height: Hauteur des murs
        """
        # Implémenter la génération de maison
        pass
    
    def _generate_tower(self, parent_node, width, depth, height):
        """
        Génère un modèle de tour simple
        
        Args:
            parent_node: Nœud parent auquel attacher la tour
            width: Largeur de la tour
            depth: Profondeur de la tour
            height: Hauteur de la tour
        """
        # Implémenter la génération de tour
        pass
    
    def _generate_wall(self, parent_node, width, height):
        """
        Génère un modèle de mur simple
        
        Args:
            parent_node: Nœud parent auquel attacher le mur
            width: Largeur du mur
            height: Hauteur du mur
        """
        # Implémenter la génération de mur
        pass
    
    def _generate_rock(self, parent_node, params):
        """
        Génère un modèle de rocher
        
        Args:
            parent_node: Nœud parent auquel attacher le rocher
            params: Paramètres de génération
        """
        # Implémenter la génération de rocher
        pass
    
    def _generate_tree(self, parent_node, params):
        """
        Génère un modèle d'arbre
        
        Args:
            parent_node: Nœud parent auquel attacher l'arbre
            params: Paramètres de génération
        """
        # Implémenter la génération d'arbre
        pass
    
    def _generate_chest(self, parent_node, params):
        """
        Génère un modèle de coffre
        
        Args:
            parent_node: Nœud parent auquel attacher le coffre
            params: Paramètres de génération
        """
        # Implémenter la génération de coffre
        pass
    
    def save_model(self, model, filepath, file_format="bam"):
        """
        Sauvegarde un modèle 3D dans un fichier
        
        Args:
            model: Le modèle à sauvegarder (NodePath)
            filepath: Chemin de destination
            file_format: Format du fichier (bam ou egg)
            
        Returns:
            bool: True si la sauvegarde a réussi
        """
        try:
            # Assurer que l'extension correspond au format
            if file_format == "bam" and not filepath.endswith(".bam"):
                filepath += ".bam"
            elif file_format == "egg" and not filepath.endswith(".egg"):
                filepath += ".egg"
            
            # Créer le répertoire parent s'il n'existe pas
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Sauvegarder le modèle
            if file_format == "bam":
                model.writeBamFile(Filename.fromOsSpecific(filepath))
            else:  # egg
                model.writeEggFile(Filename.fromOsSpecific(filepath))
                
            return True
        except Exception as e:
            print(f"Erreur lors de la sauvegarde du modèle: {e}")
            return False

    def generate_with_cache(self, asset_id, params=None, seed=None):
        """
        Génère un modèle 3D avec cache et métadonnées
        
        Args:
            asset_id (str): Identifiant du modèle
            params (dict, optional): Paramètres de génération spécifiques
            seed (int, optional): Seed pour la génération déterministe
            
        Returns:
            NodePath: Le modèle 3D généré
        """
        # Initialiser les paramètres
        if params is None:
            params = {}
            
        # Définir un seed aléatoire si non fourni
        if seed is not None:
            random.seed(seed)
            self.perlin_seeds = [seed, seed+1, seed+2]
        else:
            self.perlin_seeds = [random.randint(0, 1000) for _ in range(3)]
            
        # Détecter le type de modèle à partir de l'ID si non spécifié
        model_type = params.get("model_type", None)
        if model_type is None:
            if asset_id.startswith("prop_") or asset_id.startswith("item_"):
                model_type = ModelType.PROP
            elif asset_id.startswith("building_") or asset_id.startswith("structure_"):
                model_type = ModelType.BUILDING
            elif asset_id.startswith("terrain_"):
                model_type = ModelType.TERRAIN
            elif asset_id.startswith("dungeon_"):
                model_type = ModelType.DUNGEON
            else:
                model_type = ModelType.PROP  # Type par défaut
        
        # Assigner les paramètres de génération
        asset_params = params.copy()
        
        # Plane model generation
        if asset_id == "plane" or asset_id.startswith("plane_"):
            return self.generate_plane_model(asset_params)
        
        # Générer le modèle en fonction du type
        if model_type == ModelType.PROP:
            return self._generate_prop(asset_id, asset_params)
        elif model_type == ModelType.BUILDING:
            return self._generate_building(asset_id, asset_params)
        elif model_type == ModelType.TERRAIN:
            return self._generate_terrain_feature(asset_id, asset_params)
        elif model_type == ModelType.EFFECT:
            return self._generate_effect(asset_id, asset_params)
        elif model_type == ModelType.CHARACTER:
            return self._generate_character(asset_id, asset_params)
        else:
            # Type inconnu, générer un modèle par défaut (cube)
            return self._generate_default_model(asset_id, asset_params)

    def generate_plane_model(self, params=None):
        """
        Generate a simple plane model in EGG format
        
        Args:
            params (dict): Parameters for generation
            
        Returns:
            NodePath: The generated plane model
        """
        if params is None:
            params = {}
            
        # Model parameters
        width = params.get("width", 20.0)
        length = params.get("length", 20.0)
        subdivisions = params.get("subdivisions", 4)
        
        # Create the output directory if it doesn't exist
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Create the model file path
        model_file = os.path.join(self.output_dir, "plane.egg")
        
        # Generate the EGG file content
        egg_content = self._generate_plane_egg_file(width, length, subdivisions)
        
        # Save the EGG file
        try:
            with open(model_file, 'w') as f:
                f.write(egg_content)
                
            print(f"Generated plane model at {model_file}")
            
            # Load the model into a NodePath
            from panda3d.core import Filename, LoaderOptions
            from direct.showbase.Loader import Loader
            
            # Create a dummy loader for loading the model
            loader = Loader(None)
            model = loader.loadModel(Filename.fromOsSpecific(model_file))
            
            if model:
                return model
            else:
                print("Warning: Failed to load the generated plane model")
                return NodePath("plane_fallback")
        except Exception as e:
            print(f"Error generating plane model: {e}")
            return NodePath("plane_fallback")
    
    def _generate_plane_egg_file(self, width, length, subdivisions):
        """
        Generate the content of an EGG file for a plane model
        
        Args:
            width (float): Width of the plane
            length (float): Length of the plane
            subdivisions (int): Number of subdivisions
            
        Returns:
            str: EGG file content
        """
        half_width = width / 2.0
        half_length = length / 2.0
        
        step_x = width / subdivisions
        step_z = length / subdivisions
        
        # Start EGG file
        egg_content = '<CoordinateSystem> { Z-up }\n\n'
        egg_content += '<Comment> { "Generated by Nightfall Defenders Model Generator" }\n\n'
        
        # Add vertex pool
        egg_content += '<VertexPool> plane {\n'
        
        # Generate vertices
        vertex_index = 1
        vertices = []
        
        for i in range(subdivisions + 1):
            z = -half_length + i * step_z
            for j in range(subdivisions + 1):
                x = -half_width + j * step_x
                # Format: <Vertex> index { x y z <UV> { u v } <Normal> { nx ny nz } }
                u = j / subdivisions
                v = i / subdivisions
                
                vertex = f'  <Vertex> {vertex_index} {{ {x} 0 {z} <UV> {{ {u} {v} }} <Normal> {{ 0 1 0 }} }}\n'
                egg_content += vertex
                vertices.append(vertex_index)
                vertex_index += 1
        
        egg_content += '}\n\n'
        
        # Add group
        egg_content += '<Group> plane {\n'
        
        # Add material with a name (required)
        egg_content += '  <Material> plane_material {\n'
        egg_content += '    <Scalar> diffr { 0.8 }\n'
        egg_content += '    <Scalar> diffg { 0.8 }\n'
        egg_content += '    <Scalar> diffb { 0.8 }\n'
        egg_content += '    <Scalar> specr { 0.2 }\n'
        egg_content += '    <Scalar> specg { 0.2 }\n'
        egg_content += '    <Scalar> specb { 0.2 }\n'
        egg_content += '    <Scalar> shininess { 25 }\n'
        egg_content += '  }\n'
        
        # Add polygons (quads)
        for i in range(subdivisions):
            for j in range(subdivisions):
                # Calculate vertex indices for this quad
                v1 = i * (subdivisions + 1) + j + 1
                v2 = i * (subdivisions + 1) + (j + 1) + 1
                v3 = (i + 1) * (subdivisions + 1) + (j + 1) + 1
                v4 = (i + 1) * (subdivisions + 1) + j + 1
                
                # Add polygon (fix the syntax error by using the correct format)
                egg_content += '  <Polygon> {\n'
                # Use <ref> instead of <Ref> and fix the vertex order
                egg_content += f'    <VertexRef> {{ {v1} {v2} {v3} {v4} }}\n'
                egg_content += '    <ref> { plane }\n'
                egg_content += '  }\n'
        
        egg_content += '}\n'
        
        return egg_content 