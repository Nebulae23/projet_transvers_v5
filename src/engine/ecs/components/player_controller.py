class PlayerController:
    """
    Composant pour gérer les entrées et l'état du contrôle du joueur.
    """
    def __init__(self, speed=5.0):
        self.speed = speed
        self.move_left = False
        self.move_right = False
        self.move_up = False
        self.move_down = False
        self.attack = False
        self.use_ability_1 = False
        self.use_ability_2 = False
        # Ajoutez d'autres états de capacité si nécessaire

    def reset_actions(self):
        """Réinitialise les actions ponctuelles comme l'attaque ou l'utilisation de capacités."""
        self.attack = False
        self.use_ability_1 = False
        self.use_ability_2 = False