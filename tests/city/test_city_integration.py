import unittest
from unittest.mock import MagicMock, patch

# Supposons l'existence de ces classes (à adapter aux imports réels)
# from src.engine.ecs.world import World # Remplacé par MockWorld
# from src.engine.city.city_manager import CityManager
# from src.engine.systems.resource_system import ResourceSystem
# from src.engine.systems.building_system import BuildingSystem
# from src.engine.systems.defense_system import DefenseSystem
# from src.engine.ecs.entity import Entity # Supposé utilisé par les systèmes

# --- Mocks et Placeholders ---
# Mock simple pour le monde ECS
class MockWorld:
    def __init__(self):
        self.entities = {}
        self._entity_counter = 0
        self.components = {} # {entity_id: {component_type: component_instance}}

    def create_entity(self):
        entity_id = self._entity_counter
        self.entities[entity_id] = True # Simule l'existence de l'entité
        self.components[entity_id] = {}
        self._entity_counter += 1
        # Simule le retour d'un objet Entity ou juste l'ID
        mock_entity = MagicMock()
        mock_entity.id = entity_id
        return mock_entity # Retourne un mock d'entité avec un ID

    def add_component(self, entity_id, component):
        if entity_id not in self.components:
            self.components[entity_id] = {}
        self.components[entity_id][type(component)] = component
        print(f"DEBUG: Added {type(component).__name__} to entity {entity_id}")

    def get_component(self, entity_id, component_type):
        return self.components.get(entity_id, {}).get(component_type)

    def get_entities_with_component(self, component_type):
        entities = []
        for entity_id, components in self.components.items():
            if component_type in components:
                # Retourne l'ID de l'entité pour la simulation
                entities.append(entity_id)
        return entities

    def remove_component(self, entity_id, component_type):
         if entity_id in self.components and component_type in self.components[entity_id]:
             del self.components[entity_id][component_type]
             print(f"DEBUG: Removed {component_type.__name__} from entity {entity_id}")


# Placeholders pour les composants (juste pour les type hints et instanceof)
class BuildingComponent:
    def __init__(self, building_type, level=1):
        self.type = building_type
        self.level = level
class ConstructionComponent:
     def __init__(self, building_type, remaining_time):
        self.building_type = building_type
        self.remaining_time = remaining_time
class ResourceProducerComponent:
    def __init__(self, resource_type, rate):
        self.resource_type = resource_type
        self.rate = rate
class ResourceStorageComponent:
     def __init__(self, capacity):
         self.capacity = capacity
         self.current_storage = {} # {resource_type: amount}
class DefenseComponent:
    def __init__(self, defense_value):
        self.defense_value = defense_value
class HousingComponent:
     def __init__(self, capacity):
         self.capacity = capacity

# Placeholders pour les systèmes (avec logique simplifiée pour les tests)
class CityManager:
    def __init__(self, world):
        self.world = world
        print("CityManager Initialized")
    def update(self, dt):
        # Logique de gestion globale (population, bonheur, etc.) - Simplifié
        pass

class ResourceSystem:
    def __init__(self, world):
        self.world = world
        self.global_resources = {'wood': 100, 'stone': 100, 'food': 50} # Stock initial global
        print(f"ResourceSystem Initialized with: {self.global_resources}")

    def has_resources(self, cost):
        return all(self.global_resources.get(res, 0) >= amount for res, amount in cost.items())

    def consume_resources(self, cost):
        if self.has_resources(cost):
            for res, amount in cost.items():
                self.global_resources[res] -= amount
            print(f"Consumed resources: {cost}. Remaining: {self.global_resources}")
            return True
        print(f"Failed to consume resources: {cost}. Available: {self.global_resources}")
        return False

    def add_resources(self, resource_type, amount):
        self.global_resources[resource_type] = self.global_resources.get(resource_type, 0) + amount
        print(f"Added {amount} {resource_type}. Total: {self.global_resources[resource_type]}")

    def update(self, dt):
        # Simule la production basée sur les ResourceProducerComponent
        producer_entities = self.world.get_entities_with_component(ResourceProducerComponent)
        for entity_id in producer_entities:
            producer = self.world.get_component(entity_id, ResourceProducerComponent)
            produced_amount = producer.rate * dt
            self.add_resources(producer.resource_type, produced_amount)
            print(f"Entity {entity_id} produced {produced_amount} {producer.resource_type}")

class BuildingSystem:
    def __init__(self, world):
        self.world = world
        # Définitions simplifiées des bâtiments
        self.building_definitions = {
            'house': {'cost': {'wood': 10}, 'build_time': 5, 'components': [HousingComponent(capacity=5)]},
            'sawmill': {'cost': {'wood': 20, 'stone': 5}, 'build_time': 10, 'components': [ResourceProducerComponent(resource_type='wood', rate=1)]},
            'quarry': {'cost': {'wood': 5, 'stone': 20}, 'build_time': 10, 'components': [ResourceProducerComponent(resource_type='stone', rate=0.5)]},
            'wall': {'cost': {'stone': 30}, 'build_time': 8, 'components': [DefenseComponent(defense_value=50)]}
        }
        print("BuildingSystem Initialized")

    def start_construction(self, entity_id, building_type):
        if building_type not in self.building_definitions:
            print(f"Error: Building type '{building_type}' not defined.")
            return False
        definition = self.building_definitions[building_type]
        # Vérification et consommation des ressources gérées par ResourceSystem
        # Ici, on suppose que ResourceSystem est accessible ou que CityManager le coordonne
        # Pour ce test, on accède directement au ResourceSystem via le world mock (si ajouté comme système)
        resource_system = self.world.get_system(ResourceSystem) # Besoin d'ajouter les systèmes au world dans setUp
        if resource_system and resource_system.consume_resources(definition['cost']):
            construction_time = definition['build_time']
            self.world.add_component(entity_id, ConstructionComponent(building_type, construction_time))
            print(f"Started construction of {building_type} (ID: {entity_id}) - Time: {construction_time}")
            return True
        else:
            print(f"Failed to start construction of {building_type} (ID: {entity_id}) due to lack of resources.")
            return False

    def update(self, dt):
        # Gère la progression de la construction
        construction_entities = list(self.world.get_entities_with_component(ConstructionComponent)) # Copie pour itération sûre
        for entity_id in construction_entities:
            construction = self.world.get_component(entity_id, ConstructionComponent)
            if construction:
                construction.remaining_time -= dt
                print(f"Construction progress for {construction.building_type} (ID: {entity_id}): {construction.remaining_time:.1f}s remaining")
                if construction.remaining_time <= 0:
                    self.complete_construction(entity_id, construction.building_type)

    def complete_construction(self, entity_id, building_type):
        print(f"Completing construction of {building_type} (ID: {entity_id})")
        self.world.remove_component(entity_id, ConstructionComponent)
        definition = self.building_definitions[building_type]
        # Ajoute les composants finaux du bâtiment
        self.world.add_component(entity_id, BuildingComponent(building_type))
        for component_instance in definition.get('components', []):
             # Crée une nouvelle instance pour chaque bâtiment
             if isinstance(component_instance, HousingComponent):
                 self.world.add_component(entity_id, HousingComponent(component_instance.capacity))
             elif isinstance(component_instance, ResourceProducerComponent):
                 self.world.add_component(entity_id, ResourceProducerComponent(component_instance.resource_type, component_instance.rate))
             elif isinstance(component_instance, DefenseComponent):
                  self.world.add_component(entity_id, DefenseComponent(component_instance.defense_value))
             # Ajouter d'autres types de composants si nécessaire
        print(f"Finished construction of {building_type} (ID: {entity_id}). Final components added.")


class DefenseSystem:
    def __init__(self, world):
        self.world = world
        print("DefenseSystem Initialized")

    def get_total_defense(self):
        total_defense = 0
        defense_entities = self.world.get_entities_with_component(DefenseComponent)
        for entity_id in defense_entities:
            defense_comp = self.world.get_component(entity_id, DefenseComponent)
            total_defense += defense_comp.defense_value
        print(f"Calculated total defense: {total_defense}")
        return total_defense

    def simulate_attack(self, attack_power):
        total_defense = self.get_total_defense()
        print(f"Simulating attack with power {attack_power} against defense {total_defense}")
        if attack_power > total_defense:
            print("Defense failed!")
            # Logique de dégâts/destruction (simplifié)
            return False # L'attaque réussit (défense percée)
        else:
            print("Defense holds!")
            return True # L'attaque échoue (défense suffisante)

    def update(self, dt):
        # Logique de défense (réparations, état d'alerte, etc.) - Simplifié
        pass

# --- Classe de Test ---
class TestCityIntegration(unittest.TestCase):
    def setUp(self):
        """Initialisation des systèmes et composants pour chaque test."""
        self.world = MockWorld()
        # Instancie les systèmes avec le monde mock
        self.resource_system = ResourceSystem(self.world)
        self.building_system = BuildingSystem(self.world)
        self.defense_system = DefenseSystem(self.world)
        self.city_manager = CityManager(self.world) # CityManager peut dépendre d'autres systèmes

        # Ajoute les systèmes au monde pour qu'ils puissent interagir (si nécessaire)
        # Utilise une méthode fictive add_system/get_system sur MockWorld si besoin
        self.world.get_system = lambda sys_type: { # Permet aux systèmes de se trouver
            ResourceSystem: self.resource_system,
            BuildingSystem: self.building_system,
            DefenseSystem: self.defense_system,
            CityManager: self.city_manager
        }.get(sys_type)

        print("\n--- Test Setup Complete ---")


    def test_complete_building_cycle(self):
        """Test du cycle complet de construction d'un bâtiment (maison)."""
        print("\n--- Testing: Complete Building Cycle (House) ---")
        entity = self.world.create_entity()
        building_type = 'house'
        definition = self.building_system.building_definitions[building_type]
        initial_wood = self.resource_system.global_resources['wood']

        # 1. Démarrer la construction
        can_build = self.building_system.start_construction(entity.id, building_type)
        self.assertTrue(can_build, "La construction de la maison devrait démarrer.")
        self.assertIsNotNone(self.world.get_component(entity.id, ConstructionComponent), "Le composant Construction devrait être ajouté.")
        self.assertEqual(self.resource_system.global_resources['wood'], initial_wood - definition['cost']['wood'], "Le bois devrait être consommé.")

        # 2. Simuler le temps de construction
        build_time = definition['build_time']
        print(f"Simulating build time: {build_time} seconds...")
        self.building_system.update(build_time + 0.1) # Ajoute un petit delta pour être sûr

        # 3. Vérifier l'achèvement
        self.assertIsNone(self.world.get_component(entity.id, ConstructionComponent), "Le composant Construction devrait être retiré.")
        self.assertIsNotNone(self.world.get_component(entity.id, BuildingComponent), "Le composant Building devrait être ajouté.")
        self.assertIsNotNone(self.world.get_component(entity.id, HousingComponent), "Le composant Housing devrait être ajouté.")
        self.assertEqual(self.world.get_component(entity.id, BuildingComponent).type, building_type)
        print("--- Test Complete Building Cycle: Success ---")


    def test_resource_production_chain(self):
        """Test de la chaîne : construire scierie -> produire bois -> construire maison."""
        print("\n--- Testing: Resource Production Chain (Sawmill -> House) ---")
        sawmill_entity = self.world.create_entity()
        house_entity = self.world.create_entity()
        sawmill_type = 'sawmill'
        house_type = 'house'
        sawmill_def = self.building_system.building_definitions[sawmill_type]
        house_def = self.building_system.building_definitions[house_type]

        initial_wood = self.resource_system.global_resources['wood']
        initial_stone = self.resource_system.global_resources['stone']

        # 1. Construire la scierie
        print("Building Sawmill...")
        can_build_sawmill = self.building_system.start_construction(sawmill_entity.id, sawmill_type)
        self.assertTrue(can_build_sawmill, "La construction de la scierie devrait démarrer.")
        self.assertEqual(self.resource_system.global_resources['wood'], initial_wood - sawmill_def['cost']['wood'])
        self.assertEqual(self.resource_system.global_resources['stone'], initial_stone - sawmill_def['cost']['stone'])
        # Simuler l'achèvement de la scierie
        self.building_system.update(sawmill_def['build_time'] + 0.1)
        self.assertIsNotNone(self.world.get_component(sawmill_entity.id, ResourceProducerComponent), "La scierie devrait avoir un ResourceProducerComponent.")
        wood_after_sawmill_build = self.resource_system.global_resources['wood']

        # 2. Simuler la production de bois
        production_time = 20 # Simule 20 secondes de production
        sawmill_producer = self.world.get_component(sawmill_entity.id, ResourceProducerComponent)
        expected_production = sawmill_producer.rate * production_time
        print(f"Simulating wood production for {production_time} seconds...")
        self.resource_system.update(production_time) # Le système de ressources met à jour le stock global
        self.assertEqual(self.resource_system.global_resources['wood'], wood_after_sawmill_build + expected_production, "La production de bois n'est pas correcte.")
        wood_after_production = self.resource_system.global_resources['wood']

        # 3. Construire la maison avec les ressources produites/restantes
        print("Building House with produced resources...")
        can_build_house = self.building_system.start_construction(house_entity.id, house_type)
        self.assertTrue(can_build_house, "La construction de la maison devrait démarrer avec les ressources disponibles.")
        self.assertEqual(self.resource_system.global_resources['wood'], wood_after_production - house_def['cost']['wood'], "Le bois devrait être consommé pour la maison.")
        # Simuler l'achèvement de la maison
        self.building_system.update(house_def['build_time'] + 0.1)
        self.assertIsNotNone(self.world.get_component(house_entity.id, BuildingComponent), "La maison devrait être construite.")
        print("--- Test Resource Production Chain: Success ---")


    def test_defense_mechanics(self):
        """Test de la construction de défenses et simulation d'attaques."""
        print("\n--- Testing: Defense Mechanics (Wall) ---")
        wall_entity = self.world.create_entity()
        wall_type = 'wall'
        wall_def = self.building_system.building_definitions[wall_type]
        initial_stone = self.resource_system.global_resources['stone']

        # 1. Construire un mur
        print("Building Wall...")
        can_build_wall = self.building_system.start_construction(wall_entity.id, wall_type)
        self.assertTrue(can_build_wall, "La construction du mur devrait démarrer.")
        self.assertEqual(self.resource_system.global_resources['stone'], initial_stone - wall_def['cost']['stone'])
        # Simuler l'achèvement du mur
        self.building_system.update(wall_def['build_time'] + 0.1)
        self.assertIsNotNone(self.world.get_component(wall_entity.id, DefenseComponent), "Le mur devrait avoir un DefenseComponent.")
        wall_defense_value = self.world.get_component(wall_entity.id, DefenseComponent).defense_value

        # 2. Vérifier la défense totale
        self.assertEqual(self.defense_system.get_total_defense(), wall_defense_value, "La défense totale devrait correspondre à celle du mur.")

        # 3. Simuler des attaques
        attack_weak = wall_defense_value - 10
        attack_strong = wall_defense_value + 10
        self.assertTrue(self.defense_system.simulate_attack(attack_weak), "La défense devrait résister à une attaque faible.")
        self.assertFalse(self.defense_system.simulate_attack(attack_strong), "La défense ne devrait pas résister à une attaque forte.")
        print("--- Test Defense Mechanics: Success ---")


    def test_city_development(self):
        """Test du développement global : plusieurs bâtiments, production, défense."""
        print("\n--- Testing: City Development (Multiple Buildings & Time Progression) ---")
        # Entités pour différents bâtiments
        house1_entity = self.world.create_entity()
        sawmill_entity = self.world.create_entity()
        quarry_entity = self.world.create_entity()
        wall_entity = self.world.create_entity()
        house2_entity = self.world.create_entity()

        initial_resources = self.resource_system.global_resources.copy()

        # Phase 1: Construction initiale (Maison, Scierie)
        print("Phase 1: Initial construction (House, Sawmill)")
        self.assertTrue(self.building_system.start_construction(house1_entity.id, 'house'))
        self.assertTrue(self.building_system.start_construction(sawmill_entity.id, 'sawmill'))
        # Simuler le temps pour terminer ces constructions (max des deux temps)
        time_phase1 = max(self.building_system.building_definitions['house']['build_time'],
                          self.building_system.building_definitions['sawmill']['build_time'])
        print(f"Simulating {time_phase1}s for Phase 1...")
        self.building_system.update(time_phase1 + 0.1)
        self.resource_system.update(time_phase1 + 0.1) # La production commence après construction
        self.assertIsNotNone(self.world.get_component(house1_entity.id, BuildingComponent))
        self.assertIsNotNone(self.world.get_component(sawmill_entity.id, BuildingComponent))
        resources_after_phase1 = self.resource_system.global_resources.copy()
        print(f"Resources after Phase 1: {resources_after_phase1}")

        # Phase 2: Production et construction Carrière + Mur
        print("Phase 2: Production and construction (Quarry, Wall)")
        time_phase2 = 15 # Simuler 15s de production/construction
        # Démarrer construction Carrière et Mur (si ressources suffisantes après production)
        self.resource_system.update(time_phase2) # Produire pendant 15s
        self.building_system.update(time_phase2) # Mettre à jour constructions existantes (aucune ici)
        resources_before_build_phase2 = self.resource_system.global_resources.copy()
        print(f"Resources before building in Phase 2: {resources_before_build_phase2}")

        can_build_quarry = self.building_system.start_construction(quarry_entity.id, 'quarry')
        can_build_wall = self.building_system.start_construction(wall_entity.id, 'wall')
        self.assertTrue(can_build_quarry, "Devrait pouvoir construire la carrière.")
        self.assertTrue(can_build_wall, "Devrait pouvoir construire le mur.")

        # Simuler le temps pour terminer Carrière et Mur
        time_phase2_build = max(self.building_system.building_definitions['quarry']['build_time'],
                                self.building_system.building_definitions['wall']['build_time'])
        print(f"Simulating {time_phase2_build}s for Phase 2 builds...")
        self.building_system.update(time_phase2_build + 0.1)
        self.resource_system.update(time_phase2_build + 0.1) # Production pendant la construction
        self.assertIsNotNone(self.world.get_component(quarry_entity.id, BuildingComponent))
        self.assertIsNotNone(self.world.get_component(wall_entity.id, BuildingComponent))
        resources_after_phase2 = self.resource_system.global_resources.copy()
        print(f"Resources after Phase 2: {resources_after_phase2}")

        # Phase 3: Vérification finale et attaque simulée
        print("Phase 3: Final checks and simulated attack")
        # Vérifier que les producteurs sont actifs
        self.assertIsNotNone(self.world.get_component(sawmill_entity.id, ResourceProducerComponent))
        self.assertIsNotNone(self.world.get_component(quarry_entity.id, ResourceProducerComponent))
        # Vérifier la défense
        expected_defense = self.building_system.building_definitions['wall']['components'][0].defense_value
        self.assertEqual(self.defense_system.get_total_defense(), expected_defense)
        # Simuler une attaque
        self.assertTrue(self.defense_system.simulate_attack(expected_defense - 1), "La ville devrait survivre à une attaque faible.")

        # Optionnel: Construire une deuxième maison
        print("Building second house...")
        can_build_house2 = self.building_system.start_construction(house2_entity.id, 'house')
        self.assertTrue(can_build_house2, "Devrait pouvoir construire une deuxième maison.")
        # ... (simulation achèvement)

        print("--- Test City Development: Success ---")


if __name__ == '__main__':
    unittest.main(verbosity=2)