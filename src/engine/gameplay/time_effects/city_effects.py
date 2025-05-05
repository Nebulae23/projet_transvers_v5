# src/engine/gameplay/time_effects/city_effects.py
from engine.time.time_manager import TimeManager
from engine.time.day_night_cycle import TimeOfDay
# Importer les systèmes ou composants liés à la ville si nécessaire
# from engine.city.city_manager import CityManager
# from engine.city.defense import DefenseComponent

class CityTimeEffects:
    """
    Gère les effets du cycle jour/nuit sur la ville, ses bâtiments et ses défenses.
    """

    # Exemples de modificateurs ou d'états pour la ville
    CITY_STATES = {
        TimeOfDay.DAWN: {"defense_bonus": 0.9, "citizen_activity": "waking_up", "trade_efficiency": 0.8},
        TimeOfDay.DAY: {"defense_bonus": 1.0, "citizen_activity": "active", "trade_efficiency": 1.0},
        TimeOfDay.DUSK: {"defense_bonus": 1.1, "citizen_activity": "returning_home", "trade_efficiency": 0.9},
        TimeOfDay.NIGHT: {"defense_bonus": 1.2, "citizen_activity": "sleeping", "trade_efficiency": 0.5} # Bonus défense la nuit? Malus commerce?
    }

    def __init__(self, time_manager: TimeManager, city_manager=None):
        """
        Initialise le gestionnaire d'effets sur la ville.

        Args:
            time_manager (TimeManager): Le gestionnaire de temps du jeu.
            city_manager: Référence au gestionnaire de la ville pour appliquer les effets.
        """
        if not isinstance(time_manager, TimeManager):
            raise TypeError("CityTimeEffects requiert une instance de TimeManager.")
        self.time_manager = time_manager
        self.city_manager = city_manager # Garder une référence pour interagir
        self.current_state = self.CITY_STATES[TimeOfDay.DAY] # Initialisation

        # Enregistrer le callback
        self.time_manager.register_on_period_change(self._on_period_change)
        # Appliquer l'état initial
        self._update_state()
        self._apply_city_effects()

    def _on_period_change(self, old_period: TimeOfDay, new_period: TimeOfDay):
        """Callback appelé lors du changement de période jour/nuit."""
        # print(f"City Effects: Période changée en {new_period.name}. Mise à jour de l'état de la ville.")
        self._update_state()
        self._apply_city_effects()

    def _update_state(self):
        """Met à jour l'état actif basé sur la période actuelle."""
        current_period = self.time_manager.get_current_period()
        self.current_state = self.CITY_STATES.get(current_period, self.CITY_STATES[TimeOfDay.DAY])
        # print(f"City Effects: État actif pour {current_period.name}: {self.current_state}")

    def _apply_city_effects(self):
        """
        Applique les effets de l'état actuel sur la ville et ses composants.
        """
        if not self.city_manager:
            print("City Effects: CityManager non fourni, impossible d'appliquer les effets.")
            return

        # --- Effets sur les Défenses (Exemple) ---
        defense_bonus = self.current_state.get("defense_bonus", 1.0)
        # Supposons que le city_manager peut accéder aux défenses
        # for defense_entity in self.city_manager.get_all_defenses():
        #     defense_component = getattr(defense_entity, 'defense', None) # Composant fictif
        #     if defense_component:
        #         # Appliquer le bonus (additivement, multiplicativement?)
        #         # defense_component.set_time_modifier(defense_bonus)
        #         pass # Logique à implémenter

        # --- Effets sur l'Activité des Citoyens (Exemple) ---
        activity_level = self.current_state.get("citizen_activity", "idle")
        # Le city_manager pourrait utiliser cette information pour l'IA des PNJ, l'apparence de la ville, etc.
        # self.city_manager.set_citizen_activity_level(activity_level)

        # --- Effets sur le Commerce (Exemple) ---
        trade_efficiency = self.current_state.get("trade_efficiency", 1.0)
        # Affecter les revenus commerciaux, la disponibilité des marchands, etc.
        # self.city_manager.set_trade_efficiency_modifier(trade_efficiency)

        print(f"City Effects: Effets pour {self.time_manager.get_current_period().name} appliqués à la ville (simulation). Bonus défense: {defense_bonus:.2f}")


    def update(self, dt):
        """
        Mise à jour continue si des effets graduels sont nécessaires.
        """
        # Pourrait être utilisé pour des transitions douces des effets
        pass

    def cleanup(self):
        """Nettoie les ressources."""
        self.time_manager.unregister_on_period_change(self._on_period_change)
        # print("City Effects: Callback désenregistré.")

# Exemple d'utilisation
# time_mgr = TimeManager()
# city_mgr = get_city_manager_instance() # Récupérer le gestionnaire de ville
# city_effects_mgr = CityTimeEffects(time_mgr, city_mgr)
#
# # Dans la boucle de jeu (si update est nécessaire):
# # city_effects_mgr.update(dt)
#
# # Cleanup
# # city_effects_mgr.cleanup()