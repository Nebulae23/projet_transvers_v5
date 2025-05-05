# src/engine/time/time_manager.py
from .game_clock import GameClock
from .day_night_cycle import DayNightCycle, TimeOfDay

class TimeManager:
    """
    Gère le temps global du jeu, intégrant l'horloge de jeu et le cycle jour/nuit.
    Sert de point d'accès centralisé pour les informations temporelles.
    """
    def __init__(self, cycle_duration_seconds=1200, time_scale=1.0):
        """
        Initialise le gestionnaire de temps.

        Args:
            cycle_duration_seconds (int): Durée d'un cycle jour/nuit complet en secondes de jeu.
            time_scale (float): Facteur d'échelle initial pour la vitesse du temps.
        """
        self.game_clock = GameClock(time_scale=time_scale)
        self.day_night_cycle = DayNightCycle(cycle_duration_seconds=cycle_duration_seconds)

        # Connecter le changement de période du cycle à une méthode interne si nécessaire
        # self.day_night_cycle.register_on_period_change(self._handle_period_change)

    def update(self):
        """Met à jour l'horloge de jeu et le cycle jour/nuit."""
        # 1. Mettre à jour l'horloge pour obtenir le delta_time de jeu
        self.game_clock.update()
        delta_time = self.game_clock.get_delta_time()

        # 2. Mettre à jour le cycle jour/nuit avec le delta_time de jeu
        if delta_time > 0: # Ne met à jour le cycle que si le temps avance
            self.day_night_cycle.update(delta_time)

    def get_game_time(self):
        """Retourne le temps total écoulé dans le jeu (secondes)."""
        return self.game_clock.get_game_time()

    def get_delta_time(self):
        """Retourne le temps écoulé depuis la dernière frame (secondes de jeu)."""
        return self.game_clock.get_delta_time()

    def get_time_scale(self):
        """Retourne le facteur d'échelle actuel du temps."""
        return self.game_clock.get_time_scale()

    def set_time_scale(self, scale):
        """Définit le facteur d'échelle du temps."""
        self.game_clock.set_time_scale(scale)

    def pause_game(self):
        """Met en pause le temps de jeu."""
        self.game_clock.pause()

    def resume_game(self):
        """Reprend le temps de jeu."""
        self.game_clock.resume()

    def is_paused(self):
        """Retourne True si le jeu est en pause."""
        return self.game_clock.is_paused()

    def get_current_period(self):
        """Retourne la période actuelle de la journée (TimeOfDay)."""
        return self.day_night_cycle.get_current_period()

    def get_cycle_progress(self):
        """Retourne la progression dans le cycle actuel (0.0 à 1.0)."""
        return self.day_night_cycle.get_cycle_progress()

    def get_period_progress(self):
        """Retourne la progression dans la période actuelle (0.0 à 1.0)."""
        return self.day_night_cycle.get_period_progress()

    def get_sun_angle(self, zenith_angle=90.0):
        """Retourne l'angle approximatif du soleil en degrés."""
        return self.day_night_cycle.get_sun_angle(zenith_angle)

    def is_day(self):
        """Retourne True si c'est le jour (DAWN ou DAY)."""
        return self.day_night_cycle.is_day()

    def is_night(self):
        """Retourne True si c'est la nuit (DUSK ou NIGHT)."""
        return self.day_night_cycle.is_night()

    def register_on_period_change(self, callback):
        """Enregistre un callback pour les changements de période jour/nuit."""
        self.day_night_cycle.register_on_period_change(callback)

    def unregister_on_period_change(self, callback):
        """Désenregistre un callback de changement de période."""
        self.day_night_cycle.unregister_on_period_change(callback)

    def schedule_event(self, delay_seconds, callback, recurring=False, interval_seconds=None):
         """
         Programme un événement basé sur le temps de jeu via GameClock.

         Args:
             delay_seconds (float): Délai en secondes de jeu.
             callback (callable): Fonction à appeler.
             recurring (bool): Si l'événement doit se répéter.
             interval_seconds (float, optional): Intervalle pour les événements récurrents.
         """
         self.game_clock.schedule_event(delay_seconds, callback, recurring, interval_seconds)

    def cancel_scheduled_events(self, callback_to_cancel):
        """Annule les événements programmés associés à un callback."""
        return self.game_clock.cancel_events(callback_to_cancel)

    # Méthode privée pour gérer les changements de période si nécessaire en interne
    # def _handle_period_change(self, old_period, new_period):
    #     print(f"TimeManager a détecté un changement: {old_period.name} -> {new_period.name}")
    #     # Ajouter ici une logique spécifique au TimeManager si besoin