# src/engine/ecs/entity.py
from typing import Dict, Type, TypeVar, Optional
from uuid import UUID, uuid4

T = TypeVar('T', bound='Component')

class Entity:
    def __init__(self, world: 'World'):
        self.id: UUID = uuid4()
        self.world = world
        self.components: Dict[Type[T], T] = {}
        self.is_active = True
        
    def add_component(self, component: T) -> None:
        """Add a component to the entity."""
        component_type = type(component)
        if component_type in self.components:
            raise ValueError(f"Entity already has component of type {component_type}")
        self.components[component_type] = component
        component.entity = self
        
    def remove_component(self, component_type: Type[T]) -> None:
        """Remove a component from the entity."""
        if component_type in self.components:
            del self.components[component_type]
            
    def get_component(self, component_type: Type[T]) -> Optional[T]:
        """
        Get a component by type.
        
        Args:
            component_type: Can be a type or a string name of a component type
            
        Returns:
            The component instance or None if not found
        """
        # Handle component_type as string
        if isinstance(component_type, str):
            # Try to find component by name match
            for comp_type, comp in self.components.items():
                if comp_type.__name__ == component_type:
                    return comp
            # Not found by name
            return None
            
        # Normal component type lookup
        return self.components.get(component_type)
        
    def has_component(self, component_type: Type[T]) -> bool:
        """
        Check if entity has a specific component.
        
        Args:
            component_type: Can be a type or a string name of a component type
            
        Returns:
            True if the entity has the component, False otherwise
        """
        # Handle component_type as string
        if isinstance(component_type, str):
            # Try to find component by name match
            for comp_type in self.components.keys():
                if comp_type.__name__ == component_type:
                    return True
            # Not found by name
            return False
            
        # Normal component type check
        return component_type in self.components