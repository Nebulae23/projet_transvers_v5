import dataclasses
from src.engine.time.game_clock import GameClock # Assurez-vous que le chemin d'importation est correct

@dataclasses.dataclass
class Cooldown:
    """
    Gère le temps de recharge d'une capacité ou d'une action.

    Attributes:
        total_time (float): Le temps de recharge total en secondes.
        remaining_time (float): Le temps de recharge restant en secondes.
    """
    total_time: float = 1.0
    remaining_time: float = 0.0

    def update(self, game_clock: GameClock):
        """
        Met à jour le temps de recharge restant.
        Doit être appelée à chaque frame ou tick logique.

        Args:
            game_clock (GameClock): L'horloge du jeu pour obtenir le delta_time.
        """
        if self.remaining_time > 0:
            self.remaining_time -= game_clock.delta_time
            if self.remaining_time < 0:
                self.remaining_time = 0

    def reset(self):
        """
        Réinitialise le temps de recharge à sa valeur totale.
        Appelée généralement après l'utilisation de la capacité.
        """
        self.remaining_time = self.total_time

    def is_ready(self) -> bool:
        """
        Vérifie si le temps de recharge est terminé.

        Returns:
            bool: True si la capacité est prête à être utilisée, False sinon.
        """
        return self.remaining_time <= 0

    def set_total_time(self, value: float):
        """Modifie le temps de recharge total."""
        self.total_time = max(0.0, value)
        # Optionnel: ajuster remaining_time si nécessaire?
        # self.remaining_time = min(self.remaining_time, self.total_time)

    def get_remaining_ratio(self) -> float:
        """
        Retourne le ratio du temps de recharge restant (0.0 à 1.0).
        Utile pour les indicateurs visuels (barres de cooldown).

        Returns:
            float: Ratio du temps restant (1.0 = complet, 0.0 = prêt).
        """
        if self.total_time <= 0:
            return 0.0
        return self.remaining_time / self.total_time