# src/engine/combat/ability.py
from typing import Optional, List, Dict, Any # Ajout de Dict et Any
import numpy as np
from ..ecs.entity import Entity
from ..ecs.components import TrajectoryProjectile, Transform, Sprite # Ajouter Sprite pour le projectile
from ..ecs.world import World # Importer World

# Retirer les imports de trajectoires spécifiques pour l'instant si non utilisés
# from .trajectory import TrajectoryPattern, LinearTrajectory, ArcingTrajectory
# ...

class Ability:
    """Classe de base pour une capacité, initialisée à partir de données."""
    # Modification de __init__ pour accepter ability_id et data
    def __init__(self, ability_id: str, data: Dict[str, Any]):
        self.ability_id = ability_id
        self.data = data # Garder une référence aux données brutes peut être utile

        # Extraire les propriétés communes depuis les données
        self.name: str = data.get("name", "Unnamed Ability")
        self.cooldown: float = data.get("cooldown", 1.0)
        self.cost: float = data.get("cost", 0.0)
        # Note: 'damage' est souvent plus complexe (scaling, effets multiples)
        # Il pourrait être géré par des composants d'effet ou calculé dynamiquement.
        # Pour la simplicité, on peut garder une valeur de base si présente.
        self.base_damage: float = data.get("base_damage", 0.0) # Utilisation de base_damage

        self.current_cooldown: float = 0.0
        self.level: int = 1 # Le niveau pourrait aussi venir d'ailleurs (ex: composant sur l'entité)
        # self.trajectory_pattern: Optional[TrajectoryPattern] = None # Simplifié pour l'instant

    def can_use(self, caster: Entity) -> bool:
        """Vérifie si la capacité peut être utilisée (cooldown et coût)."""
        # TODO: Vérifier si le caster a assez de ressource (e.g., mana) pour le self.cost
        # caster_resources = caster.get_component(Resources) # Exemple
        # has_enough_resource = caster_resources is None or caster_resources.mana >= self.cost
        has_enough_resource = True # Placeholder
        return self.current_cooldown <= 0.0 and has_enough_resource

    def update(self, dt: float) -> None:
        """Met à jour le cooldown."""
        if self.current_cooldown > 0:
            self.current_cooldown -= dt

    def use(self, caster: Entity, target_pos: np.ndarray, world: World) -> List[Entity]:
        """Tente d'utiliser la capacité."""
        if not self.can_use(caster):
            return []

        # TODO: Déduire le coût en ressource du caster
        # caster_resources = caster.get_component(Resources) # Exemple
        # if caster_resources:
        #     caster_resources.mana -= self.cost

        self.current_cooldown = self.cooldown
        print(f"Ability '{self.name}' (ID: {self.ability_id}) used by {caster.entity_id}. Cooldown started.") # Ajout ID
        # Appeler la méthode spécifique pour créer les effets (projectiles, etc.)
        return self._apply_effect(caster, target_pos, world)

    def _apply_effect(self, caster: Entity, target_pos: np.ndarray, world: World) -> List[Entity]:
        """Méthode à surcharger par les sous-classes pour définir l'effet de la capacité."""
        # Par défaut, crée des projectiles, mais pourrait faire autre chose (buff, debuff, etc.)
        return self._create_projectiles(caster, target_pos, world)

    def _create_projectiles(self, caster: Entity, target_pos: np.ndarray, world: World) -> List[Entity]:
        """Méthode de base (ou à surcharger) pour créer des projectiles."""
        # Cette méthode peut être surchargée pour des comportements complexes
        # ou utilisée directement par des capacités simples.
        raise NotImplementedError("Subclasses must implement _create_projectiles or _apply_effect")

# --- Capacité de Test : Projectile Simple ---
# Cette classe utilise déjà la nouvelle initialisation
class SimpleProjectileAbility(Ability):
    """Capacité créant un projectile simple, configurée par des données."""
    def __init__(self, ability_id: str, data: Dict[str, Any]):
        # Appel à super() modifié pour correspondre à la nouvelle signature
        super().__init__(ability_id, data)

        # Extraire les propriétés spécifiques au projectile depuis les données
        # Utiliser des valeurs par défaut si les clés n'existent pas
        self.projectile_speed: float = data.get("projectile_speed", 200.0)
        self.projectile_lifetime: float = data.get("projectile_lifetime", 2.0)
        self.projectile_texture: str = data.get("projectile_texture", "assets/default_projectile.png") # Chemin par défaut
        # Le 'damage' spécifique au projectile pourrait aussi être ici ou calculé
        # Utilise base_damage de la classe parent par défaut
        self.projectile_damage: float = data.get("projectile_damage", self.base_damage)

    def _create_projectiles(self, caster: Entity, target_pos: np.ndarray, world: World) -> List[Entity]:
        """Crée un projectile simple allant vers la cible."""
        caster_transform = caster.get_component(Transform)
        if not caster_transform:
            print(f"Warning: Caster {caster.entity_id} missing Transform component.")
            return []

        # Créer l'entité projectile dans le monde
        projectile = world.create_entity()

        # Position de départ du projectile (position du lanceur)
        start_pos = caster_transform.position.copy()

        # Calculer la direction et la vélocité
        direction = target_pos - start_pos
        norm = np.linalg.norm(direction)
        if norm < 1e-6: # Si la cible est trop proche ou sur le lanceur
            # Choisir une direction par défaut (ex: vers la droite)
            direction = np.array([1.0, 0.0])
        else:
            direction = direction / norm # Normaliser le vecteur direction

        velocity = direction * self.projectile_speed

        # Ajouter les composants au projectile
        projectile.add_component(Transform(position=start_pos))
        projectile.add_component(TrajectoryProjectile(
            velocity=velocity,
            acceleration=np.zeros(2), # Pas d'accélération pour un projectile simple
            lifetime=self.projectile_lifetime,
            # Utiliser projectile_damage et potentiellement le niveau pour le calcul final
            damage=self.projectile_damage * (1.0 + 0.1 * (self.level - 1)) # Exemple de scaling simple par niveau
        ))
        # Ajouter un composant Sprite pour le rendu (optionnel mais recommandé)
        projectile.add_component(Sprite(texture_path=self.projectile_texture, z_index=1))

        print(f"Projectile {projectile.entity_id} (Ability: {self.ability_id}) created by {caster.entity_id} at {start_pos} heading towards {target_pos} with velocity {velocity}")

        # L'entité est déjà ajoutée au monde par world.create_entity() (supposition)
        # Si ce n'est pas le cas, il faudrait faire world.add_entity(projectile) ici.
        return [projectile]

# Retrait de WarriorAbility pour se concentrer sur la tâche de base
# class WarriorAbility(Ability):
#     ...