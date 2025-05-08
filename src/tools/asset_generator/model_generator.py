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

from src.tools.asset_generator.base_generator import AssetGenerator, AssetType, AssetCategory

class ModelType(object):
    """Types de modèles 3D que le générateur peut produire"""
    BUILDING = "building"
    PROP = "prop"
    TERRAIN = "terrain"
    DUNGEON = "dungeon"

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
            ModelType.DUNGEON: os.path.join(output_dir, "dungeons")
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
        elif model_type == ModelType.DUNGEON:
            return self._generate_dungeon_element(asset_id, asset_params)
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
    
    def _generate_dungeon_element(self, asset_id, params):
        """Génère un élément de donjon 3D"""
        # Créer un nœud racine pour l'élément de donjon
        dungeon_node = NodePath(PandaNode(f"dungeon_{asset_id}"))
        
        # Génération à implémenter
        
        return dungeon_node
    
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