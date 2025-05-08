#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Boss Component System for Nightfall Defenders
Base class for boss behavior components in a component-based design
"""

class BossComponent:
    """Base class for all boss components"""
    
    def __init__(self, boss):
        """
        Initialize the component
        
        Args:
            boss: The boss entity this component belongs to
        """
        self.boss = boss
        self.active = True
        self.phase_requirements = []  # List of phases where this component is active
        
    def update(self, dt):
        """
        Update the component
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            bool: True if component is active, False otherwise
        """
        # Only process if active and phase requirements are met
        if not self.active:
            return False
            
        if self.phase_requirements and self.boss.current_phase not in self.phase_requirements:
            return False
            
        return True
    
    def activate(self):
        """Activate the component"""
        self.active = True
        
    def deactivate(self):
        """Deactivate the component"""
        self.active = False
        
    def on_phase_change(self, new_phase):
        """
        Handle phase change events
        
        Args:
            new_phase: The new phase the boss has entered
        """
        # Check if this component should be active in the new phase
        if self.phase_requirements and new_phase in self.phase_requirements:
            self.activate()
        elif self.phase_requirements and new_phase not in self.phase_requirements:
            self.deactivate()
            
    def on_health_change(self, current_health, max_health):
        """
        Handle health change events
        
        Args:
            current_health: Current boss health
            max_health: Maximum boss health
        """
        # Default implementation does nothing
        pass
        
    def on_spawn(self):
        """Handle boss spawn event"""
        # Default implementation does nothing
        pass
        
    def on_despawn(self):
        """Handle boss despawn event"""
        # Default implementation does nothing
        pass
        
    def on_ability_use(self, ability_name):
        """
        Handle ability use events
        
        Args:
            ability_name: Name of the ability being used
        """
        # Default implementation does nothing
        pass
        
    def on_damage_taken(self, damage, damage_source):
        """
        Handle damage taken events
        
        Args:
            damage: Amount of damage taken
            damage_source: Source of the damage (player, environment, etc.)
        """
        # Default implementation does nothing
        pass
        
    def on_damage_dealt(self, damage, target):
        """
        Handle damage dealt events
        
        Args:
            damage: Amount of damage dealt
            target: Target of the damage
        """
        # Default implementation does nothing
        pass
        
    def cleanup(self):
        """Clean up component resources"""
        # Default implementation does nothing
        pass 