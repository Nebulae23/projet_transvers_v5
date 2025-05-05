# src/engine/ecs/world.py
from typing import Dict, List, Type, TypeVar, Optional
from .entity import Entity
from .components import Component, Transform, Sprite, Animation
import numpy as np

T = TypeVar('T', bound=Component)

class World:
    def __init__(self):
        self.entities: List[Entity] = []
        self.components_by_type: Dict[Type[Component], List[Component]] = {}
        
    def create_entity(self) -> Entity:
        """Create a new entity in the world."""
        entity = Entity(self)
        self.entities.append(entity)
        return entity
        
    def remove_entity(self, entity_or_id) -> None:
        """Remove an entity from the world by entity object or ID."""
        if isinstance(entity_or_id, str):
            # If it's a string ID, find the entity
            entity = self.get_entity(entity_or_id)
            if entity is None:
                return
        else:
            entity = entity_or_id
            
        if entity in self.entities:
            # Remove all components
            for component_type in list(entity.components.keys()):
                self._remove_component_reference(entity.components[component_type])
            self.entities.remove(entity)
            
    def get_entity(self, entity_id: str) -> Optional[Entity]:
        """Get an entity by its ID."""
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None
        
    def get_entities_with_component(self, component_type: Type[T]) -> List[Entity]:
        """Get all entities that have a specific component."""
        return [entity for entity in self.entities if entity.has_component(component_type)]
        
    def _add_component_reference(self, component: Component) -> None:
        """Track component by type for efficient querying."""
        component_type = type(component)
        if component_type not in self.components_by_type:
            self.components_by_type[component_type] = []
        self.components_by_type[component_type].append(component)
        
    def _remove_component_reference(self, component: Component) -> None:
        """Remove component from type tracking."""
        component_type = type(component)
        if component_type in self.components_by_type:
            self.components_by_type[component_type].remove(component)
            
    def update(self, dt: float) -> None:
        """Update all entities and their components."""
        entities_to_remove = []
        for entity in self.entities:
            if not entity.is_active:
                entities_to_remove.append(entity)
                continue

            # Update Animation components
            animation = entity.get_component(Animation)
            if animation and animation.is_playing:
                animation.time_since_last_frame += dt
                if animation.time_since_last_frame >= animation.frame_duration:
                    animation.time_since_last_frame -= animation.frame_duration
                    animation.current_frame_index += 1
                    if animation.current_frame_index >= len(animation.frames):
                        if animation.loop:
                            animation.current_frame_index = 0
                        else:
                            animation.current_frame_index = len(animation.frames) - 1
                            animation.is_playing = False # Stop animation if not looping

            # Placeholder for other component updates (e.g., physics)
            # physics = entity.get_component(PhysicsBody)
            # if physics:
            #     physics.update(dt) # Assuming PhysicsBody has an update method

        # Clean up inactive entities
        for entity in entities_to_remove:
            self.remove_entity(entity)

    def get_renderable_entities(self) -> List[Entity]:
        """Get all entities with Transform and Sprite components, sorted by z-index."""
        renderable_entities = []
        for entity in self.entities:
            try:
                if entity.has_component(Transform) and entity.has_component(Sprite):
                    # Make sure both components are actually present and valid
                    transform = entity.get_component(Transform)
                    sprite = entity.get_component(Sprite)
                    
                    if transform and sprite and hasattr(transform, 'position') and transform.position is not None:
                        renderable_entities.append(entity)
            except Exception as e:
                print(f"Error checking entity renderability: {e}")

        try:
            # Sort entities based on the z_index of their Sprite component
            # Add a default z_index if it doesn't exist
            renderable_entities.sort(key=lambda e: getattr(e.get_component(Sprite), 'z_index', 0))
        except Exception as e:
            print(f"Error sorting renderable entities: {e}")
            
        return renderable_entities