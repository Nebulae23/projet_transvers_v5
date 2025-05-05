# src/engine/environment/spawn_system.py
import random
from engine.ecs.system import System
from engine.time.time_manager import TimeManager # Remplacé TimeSystem
from engine.time.day_night_cycle import TimeOfDay # Remplacé TimePhase

# Configuration des apparitions par période
SPAWN_CONFIG = {
    TimeOfDay.DAWN: {'interval': 8.0, 'chance': 0.25, 'max_concurrent': 5}, # Moins fréquent, chance modérée
    TimeOfDay.DAY: {'interval': 10.0, 'chance': 0.10, 'max_concurrent': 3}, # Très peu fréquent, faible chance
    TimeOfDay.DUSK: {'interval': 6.0, 'chance': 0.40, 'max_concurrent': 8}, # Plus fréquent, chance élevée
    TimeOfDay.NIGHT: {'interval': 3.0, 'chance': 0.75, 'max_concurrent': 15} # Très fréquent, très haute chance
}
# TODO: Déplacer la configuration dans un fichier externe ?

class SpawnSystem(System):
    """
    Gère l'apparition des entités (ennemis) en fonction du cycle jour/nuit.
    """
    def __init__(self, time_manager: TimeManager, spawn_areas=None, entity_factory=None):
        """
        Initialise le système d'apparition.

        Args:
            time_manager (TimeManager): Le gestionnaire de temps du jeu.
            spawn_areas (list, optional): Liste de zones (rectangles) où les apparitions peuvent se produire.
                                          Format: [(x_min, y_min, x_max, y_max), ...].
            entity_factory: L'usine utilisée pour créer les entités (ex: ennemis).
        """
        if not isinstance(time_manager, TimeManager):
            raise TypeError("SpawnSystem requiert une instance de TimeManager.")
        self.time_manager = time_manager
        self.entity_factory = entity_factory # Doit être fourni pour créer des entités
        if self.entity_factory is None:
             print("Avertissement: SpawnSystem initialisé sans entity_factory. Aucune entité ne sera créée.")

        self.spawn_areas = spawn_areas or [(0, 0, 1000, 1000)]  # Zone par défaut
        self.spawn_timer = 0.0
        self.current_config = SPAWN_CONFIG[TimeOfDay.DAY] # Config initiale

    def _get_current_enemy_count(self, world):
        """Compte le nombre d'ennemis actuellement actifs dans le monde."""
        # Suppose que les ennemis ont un composant spécifique, ex: 'EnemyAI' ou 'EnemyStats'
        # Ceci est un exemple, adaptez selon votre structure de composants
        count = 0
        # TODO: Remplacer par une query ECS optimisée si disponible
        # Exemple: count = len(world.get_entities_with_component(EnemyComponent))
        for entity in world.entities:
             if hasattr(entity, 'is_enemy') and entity.is_enemy: # Supposition d'un attribut
                 count += 1
        return count


    def get_random_spawn_position(self):
        """Choisit une position aléatoire dans l'une des zones d'apparition."""
        if not self.spawn_areas:
            print("Erreur: Aucune zone d'apparition définie.")
            return None # Ou une position par défaut ?
        area = random.choice(self.spawn_areas)
        try:
            x = random.uniform(area[0], area[2])
            y = random.uniform(area[1], area[3])
            return x, y
        except IndexError:
             print(f"Erreur: Format de zone d'apparition invalide : {area}")
             return None


    def update(self, dt, world):
        """
        Met à jour le timer d'apparition et tente de faire apparaître des ennemis
        en fonction de la période actuelle et de la configuration.

        Args:
            dt (float): Delta time.
            world (World): L'instance du monde ECS.
        """
        if self.time_manager.is_paused() or self.entity_factory is None:
            return # Ne rien faire si le jeu est en pause ou si pas de factory

        # 1. Mettre à jour la configuration basée sur la période actuelle
        current_period = self.time_manager.get_current_period()
        self.current_config = SPAWN_CONFIG[current_period]

        # 2. Mettre à jour le timer
        self.spawn_timer += dt

        # 3. Vérifier si une tentative d'apparition doit avoir lieu
        if self.spawn_timer >= self.current_config['interval']:
            self.spawn_timer = 0 # Réinitialiser le timer (ou soustraire l'intervalle)

            # 4. Vérifier le nombre maximum d'ennemis
            current_enemy_count = self._get_current_enemy_count(world)
            if current_enemy_count >= self.current_config['max_concurrent']:
                # print(f"Max concurrent enemies reached ({current_enemy_count}/{self.current_config['max_concurrent']}). No spawn attempt.")
                return # Limite atteinte

            # 5. Tenter l'apparition basée sur la chance
            if random.random() < self.current_config['chance']:
                spawn_pos = self.get_random_spawn_position()
                if spawn_pos:
                    # print(f"Spawning enemy at {spawn_pos} during {current_period.name}")
                    # Utiliser l'entity_factory pour créer l'ennemi
                    # Le type d'ennemi pourrait aussi dépendre de la période
                    enemy_type = "standard_enemy" # Exemple
                    if current_period == TimeOfDay.NIGHT:
                        enemy_type = "night_stalker" # Exemple d'ennemi spécifique à la nuit

                    try:
                        # L'usine pourrait avoir besoin du monde ou d'autres infos
                        new_enemy = self.entity_factory.create(enemy_type, position=spawn_pos, world=world)
                        if new_enemy:
                             # Ajouter l'entité au monde (si l'usine ne le fait pas déjà)
                             if hasattr(world, 'add_entity') and new_enemy not in world.entities:
                                 world.add_entity(new_enemy)
                             # Marquer comme ennemi pour le comptage (si nécessaire)
                             if not hasattr(new_enemy, 'is_enemy'):
                                 new_enemy.is_enemy = True # Ajout d'un marqueur simple
                    except Exception as e:
                        print(f"Erreur lors de la création de l'ennemi via factory: {e}")