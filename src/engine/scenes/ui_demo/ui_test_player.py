# src/engine/scenes/ui_demo/ui_test_player.py

import pygame

from src.engine.ecs.world import World
from src.engine.ecs.components import (
    Transform, Stats, Inventory, Equipment, Skills, PlayerInfo, Health
)

class UITestPlayer:
    """
    Représente un joueur simplifié pour la scène de démonstration UI.
    Fournit une entité ECS avec les composants nécessaires pour les tests UI.
    """
    def __init__(self, world: World):
        self.world = world
        self.entity = self.world.create_entity()

        # Ajouter les composants essentiels pour l'UI
        self.world.add_component(self.entity, Transform(x=100, y=100))
        self.world.add_component(self.entity, PlayerInfo(name="DemoPlayer"))
        self.world.add_component(self.entity, Health(current=80, max_value=100))
        self.world.add_component(self.entity, Stats(
            strength=10,
            dexterity=8,
            intelligence=5,
            vitality=12,
            attack_power=20,
            defense=15,
            magic_resist=5,
            level=1,
            xp=0,
            xp_to_next_level=100
        ))
        self.world.add_component(self.entity, Inventory(items=[], capacity=20))
        self.world.add_component(self.entity, Equipment(slots={
            "weapon": None,
            "armor": None,
            "accessory1": None,
            "accessory2": None,
        }))
        # Ajouter des compétences de test
        self.world.add_component(self.entity, Skills(
            learned=[
                {"id": "fireball", "level": 1},
                {"id": "ice_shard", "level": 2}
            ],
            available_points=3 # Points disponibles pour tester l'arbre de compétences
        ))

        # Ajouter des items de test initiaux
        self._add_test_items()

        print(f"UITestPlayer entity {self.entity} created with components.")

    def _add_test_items(self):
        """Ajoute des items de démonstration à l'inventaire."""
        inventory = self.world.get_component(self.entity, Inventory)
        if inventory:
            # Assurez-vous que ces IDs existent ou adaptez selon vos données d'items réelles
            inventory.items.extend([
                {"id": "basic_sword", "quantity": 1, "name": "Basic Sword", "type": "weapon"},
                {"id": "health_potion", "quantity": 5, "name": "Health Potion", "type": "consumable"},
                {"id": "mana_potion", "quantity": 3, "name": "Mana Potion", "type": "consumable"},
                {"id": "leather_armor", "quantity": 1, "name": "Leather Armor", "type": "armor"},
                {"id": "iron_ore", "quantity": 10, "name": "Iron Ore", "type": "material"}
            ])
            print(f"Added demo items to inventory for entity {self.entity}.")
        else:
             print(f"Could not add demo items: Inventory component not found for entity {self.entity}.")


    def update(self, dt: float):
        # Logique de mise à jour minimale si nécessaire pour la démo
        pass

    def render(self, screen: pygame.Surface):
        # Logique de rendu minimale (ex: un simple cercle)
        transform = self.world.get_component(self.entity, Transform)
        if transform:
            pygame.draw.circle(screen, (0, 255, 0), (int(transform.x), int(transform.y)), 10)

    def handle_event(self, event: pygame.event.Event):
        # Gérer les événements spécifiques au joueur de test si nécessaire
        pass