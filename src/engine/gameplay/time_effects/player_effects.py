# src/engine/gameplay/time_effects/player_effects.py
from engine.time.time_manager import TimeManager
from engine.time.day_night_cycle import TimeOfDay
# Supposer l'existence d'un composant joueur ou d'une classe Player
# from engine.ecs.components import PlayerStats # Exemple

class PlayerTimeEffects:
    """
    Gère les effets du cycle jour/nuit sur le joueur.
    Peut être implémenté comme un système ECS ou une classe de gestion.
    """
    # Exemples de modificateurs de statistiques (à adapter selon le game design)
    STAT_MODIFIERS = {
        TimeOfDay.DAWN: {"visibility_range": 1.0, "stamina_regen": 1.1, "attack_power": 1.0},
        TimeOfDay.DAY: {"visibility_range": 1.2, "stamina_regen": 1.0, "attack_power": 1.0},
        TimeOfDay.DUSK: {"visibility_range": 0.9, "stamina_regen": 0.9, "attack_power": 1.05}, # Léger bonus d'attaque au crépuscule?
        TimeOfDay.NIGHT: {"visibility_range": 0.7, "stamina_regen": 0.8, "attack_power": 1.1}  # Malus visibilité/endurance, bonus attaque?
    }

    def __init__(self, time_manager: TimeManager):
        """
        Initialise le gestionnaire d'effets sur le joueur.

        Args:
            time_manager (TimeManager): Le gestionnaire de temps du jeu.
        """
        if not isinstance(time_manager, TimeManager):
            raise TypeError("PlayerTimeEffects requiert une instance de TimeManager.")
        self.time_manager = time_manager
        self.current_modifiers = self.STAT_MODIFIERS[TimeOfDay.DAY] # Initialisation

        # Enregistrer un callback pour réagir aux changements de période
        self.time_manager.register_on_period_change(self._on_period_change)
        # Appliquer les modificateurs initiaux
        self._update_modifiers()

    def _on_period_change(self, old_period: TimeOfDay, new_period: TimeOfDay):
        """Callback appelé lors du changement de période jour/nuit."""
        # print(f"Player Effects: Période changée en {new_period.name}. Mise à jour des modificateurs.")
        self._update_modifiers()
        # Potentiellement déclencher d'autres logiques spécifiques au changement (ex: message UI)

    def _update_modifiers(self):
        """Met à jour les modificateurs actifs basés sur la période actuelle."""
        current_period = self.time_manager.get_current_period()
        self.current_modifiers = self.STAT_MODIFIERS.get(current_period, self.STAT_MODIFIERS[TimeOfDay.DAY])
        # print(f"Player Effects: Modificateurs actifs pour {current_period.name}: {self.current_modifiers}")

    def apply_effects(self, player_entity):
        """
        Applique les modificateurs actuels à l'entité joueur.
        Cette méthode devrait être appelée dans la boucle de jeu ou via un système ECS.

        Args:
            player_entity: L'entité représentant le joueur.
                           Doit avoir les composants/attributs correspondants aux modificateurs.
        """
        if not player_entity:
            return

        # Exemple d'application des modificateurs.
        # Adaptez ceci en fonction de la structure de votre entité joueur et de ses composants.
        # Exemple avec des attributs directs (moins flexible) :
        # if hasattr(player_entity, 'base_visibility_range'):
        #     player_entity.current_visibility_range = player_entity.base_visibility_range * self.current_modifiers.get("visibility_range", 1.0)
        # if hasattr(player_entity, 'base_stamina_regen'):
        #     player_entity.current_stamina_regen = player_entity.base_stamina_regen * self.current_modifiers.get("stamina_regen", 1.0)
        # if hasattr(player_entity, 'base_attack_power'):
        #      player_entity.current_attack_power = player_entity.base_attack_power * self.current_modifiers.get("attack_power", 1.0)

        # Exemple avec un composant Stats (plus flexible) :
        stats_component = getattr(player_entity, 'stats', None) # Supposons un composant 'stats'
        if stats_component:
            # Il est préférable de stocker les valeurs de base et d'appliquer les modificateurs
            # plutôt que de modifier directement les stats courantes pour éviter la dérive.
            # Ici, on suppose que le système de stats gère les modificateurs.
            # On pourrait ajouter/mettre à jour un modificateur lié au temps.
            time_modifier_id = "time_of_day_effect"

            for stat_name, modifier_value in self.current_modifiers.items():
                 if hasattr(stats_component, f"update_modifier"):
                     # Supposons une méthode pour ajouter/màj un modificateur
                     stats_component.update_modifier(time_modifier_id, stat_name, modifier_value, 'multiplicative') # ou 'additive'
                 # Alternative: Calculer la stat finale ici si le composant ne gère pas les modificateurs
                 # elif hasattr(stats_component, f"base_{stat_name}") and hasattr(stats_component, f"current_{stat_name}"):
                 #    base_value = getattr(stats_component, f"base_{stat_name}")
                 #    # Attention: ce calcul simple ne gère pas les cumuls d'autres modificateurs
                 #    setattr(stats_component, f"current_{stat_name}", base_value * modifier_value)


    def get_modifier(self, stat_name: str) -> float:
        """
        Retourne la valeur du modificateur actuel pour une statistique donnée.

        Args:
            stat_name (str): Le nom de la statistique (ex: "visibility_range").

        Returns:
            float: La valeur du modificateur (1.0 si non trouvé ou période inconnue).
        """
        return self.current_modifiers.get(stat_name, 1.0)

    def cleanup(self):
        """Nettoie les ressources, notamment en désenregistrant le callback."""
        self.time_manager.unregister_on_period_change(self._on_period_change)
        # print("Player Effects: Callback désenregistré.")

# Exemple d'utilisation (dans la boucle principale ou un système de gestion du joueur)
# time_mgr = TimeManager()
# player_effects_mgr = PlayerTimeEffects(time_mgr)
# player = get_player_entity() # Fonction pour récupérer l'entité joueur
#
# # Dans la boucle de jeu:
# time_mgr.update()
# # player_effects_mgr n'a pas besoin d'update si basé sur callback, mais on applique les effets
# player_effects_mgr.apply_effects(player)
#
# # N'oubliez pas d'appeler cleanup lorsque le système est détruit
# # player_effects_mgr.cleanup()