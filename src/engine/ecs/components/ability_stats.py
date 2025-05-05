import dataclasses

@dataclasses.dataclass
class AbilityStats:
    """
    Contient les statistiques de base d'une capacité.

    Attributes:
        damage (float): Les dégâts de base de la capacité.
        cost (float): Le coût en ressource (mana, énergie, etc.) pour utiliser la capacité.
        range (float): La portée maximale de la capacité.
        cast_time (float): Le temps nécessaire pour lancer la capacité.
        area_of_effect (float): Le rayon de la zone d'effet (0 si cible unique).
        projectile_speed (float): La vitesse du projectile (0 si instantané).
    """
    damage: float = 10.0
    cost: float = 5.0
    range: float = 5.0
    cast_time: float = 0.5
    area_of_effect: float = 0.0
    projectile_speed: float = 0.0 # 0 signifie instantané ou non applicable

    def get_damage(self) -> float:
        """Retourne les dégâts de la capacité."""
        return self.damage

    def set_damage(self, value: float):
        """Modifie les dégâts de la capacité."""
        self.damage = max(0.0, value)

    def get_cost(self) -> float:
        """Retourne le coût de la capacité."""
        return self.cost

    def set_cost(self, value: float):
        """Modifie le coût de la capacité."""
        self.cost = max(0.0, value)

    def get_range(self) -> float:
        """Retourne la portée de la capacité."""
        return self.range

    def set_range(self, value: float):
        """Modifie la portée de la capacité."""
        self.range = max(0.0, value)

    # Ajoutez d'autres getters/setters si nécessaire pour les autres attributs