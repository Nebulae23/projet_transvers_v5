#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nightfall Defenders - Game Module
Game-specific components and systems
"""

from game.main import NightfallDefenders
from game.day_night_cycle import DayNightCycle
from game.camera_controller import CameraController
from game.player import Player
from game.enemy import Enemy, BasicEnemy, RangedEnemy
from game.projectile import Projectile, StraightProjectile, ArcingProjectile, HomingProjectile, SpiralProjectile
from game.entity_manager import EntityManager

__all__ = [
    'NightfallDefenders',
    'DayNightCycle',
    'CameraController',
    'Player',
    'Enemy',
    'BasicEnemy',
    'RangedEnemy',
    'Projectile',
    'StraightProjectile',
    'ArcingProjectile',
    'HomingProjectile',
    'SpiralProjectile',
    'EntityManager'
]

"""
Game module for Nightfall Defenders
This file marks the 'game' directory as a Python package.
""" 
