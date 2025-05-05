# src/engine/time/day_night_cycle.py
import math
from enum import Enum, auto

class TimeOfDay(Enum):
    """Représente les différentes périodes de la journée."""
    DAWN = auto()      # Aube
    DAY = auto()       # Jour
    DUSK = auto()      # Crépuscule
    NIGHT = auto()     # Nuit

class DayNightCycle:
    """
    Gère la logique du cycle jour/nuit, y compris les transitions
    et l'état actuel de la journée.
    """
    # Durées par défaut en proportion du cycle total (doivent sommer à 1.0)
    # Ajustables si nécessaire
    DEFAULT_DURATION_RATIOS = {
        TimeOfDay.DAWN: 0.10,  # 10% du cycle
        TimeOfDay.DAY: 0.40,   # 40% du cycle
        TimeOfDay.DUSK: 0.10,  # 10% du cycle
        TimeOfDay.NIGHT: 0.40, # 40% du cycle
    }

    def __init__(self, cycle_duration_seconds=1200):
        """
        Initialise le système de cycle jour/nuit.

        Args:
            cycle_duration_seconds (int): Durée totale d'un cycle jour/nuit en secondes de jeu.
                                          Par défaut 1200 (20 minutes).
        """
        if cycle_duration_seconds <= 0:
            raise ValueError("La durée du cycle doit être positive.")
        self.cycle_duration = float(cycle_duration_seconds)

        # Vérifier que les ratios somment à 1.0
        total_ratio = sum(self.DEFAULT_DURATION_RATIOS.values())
        if not math.isclose(total_ratio, 1.0):
             raise ValueError(f"La somme des ratios de durée ({total_ratio}) doit être égale à 1.0.")

        # Calculer les durées absolues pour chaque période
        self.durations = {
            period: ratio * self.cycle_duration
            for period, ratio in self.DEFAULT_DURATION_RATIOS.items()
        }

        # Calculer les temps de début pour chaque période
        self.start_times = {}
        current_time = 0.0
        # Ordre important: Aube -> Jour -> Crépuscule -> Nuit
        ordered_periods = [TimeOfDay.DAWN, TimeOfDay.DAY, TimeOfDay.DUSK, TimeOfDay.NIGHT]
        for period in ordered_periods:
            self.start_times[period] = current_time
            current_time += self.durations[period]

        self.current_time_in_cycle = 0.0
        self.current_period = TimeOfDay.DAWN # Commence à l'aube par défaut
        self.cycle_count = 0

        # Callbacks pour les changements de période
        self._on_period_change_callbacks = []

    def update(self, delta_time):
        """
        Met à jour le temps du cycle et détermine la période actuelle.

        Args:
            delta_time (float): Temps écoulé depuis la dernière mise à jour (en secondes de jeu).
        """
        if delta_time < 0:
            return # Ne rien faire si le temps recule

        self.current_time_in_cycle += delta_time
        previous_period = self.current_period

        # Gérer le passage à un nouveau cycle
        if self.current_time_in_cycle >= self.cycle_duration:
            overflow = self.current_time_in_cycle - self.cycle_duration
            self.cycle_count += 1
            self.current_time_in_cycle = overflow % self.cycle_duration # Recommencer le cycle avec l'excédent

        # Déterminer la période actuelle
        # Itérer dans l'ordre inverse pour trouver la période correspondante
        ordered_periods = [TimeOfDay.NIGHT, TimeOfDay.DUSK, TimeOfDay.DAY, TimeOfDay.DAWN]
        for period in ordered_periods:
            if self.current_time_in_cycle >= self.start_times[period]:
                self.current_period = period
                break
        else:
             # Normalement impossible si start_times[DAWN] est 0.0
             self.current_period = TimeOfDay.DAWN

        # Déclencher les callbacks si la période a changé
        if self.current_period != previous_period:
            self._notify_period_change(previous_period, self.current_period)

    def get_current_period(self):
        """Retourne la période actuelle de la journée (TimeOfDay)."""
        return self.current_period

    def get_time_in_cycle(self):
        """Retourne le temps écoulé dans le cycle actuel (en secondes de jeu)."""
        return self.current_time_in_cycle

    def get_cycle_progress(self):
        """Retourne la progression dans le cycle actuel (entre 0.0 et 1.0)."""
        return self.current_time_in_cycle / self.cycle_duration

    def get_period_progress(self):
        """Retourne la progression dans la période actuelle (entre 0.0 et 1.0)."""
        period_start_time = self.start_times[self.current_period]
        period_duration = self.durations[self.current_period]
        if period_duration <= 0:
            return 1.0 # Période instantanée
        time_in_period = self.current_time_in_cycle - period_start_time
        return max(0.0, min(1.0, time_in_period / period_duration))

    def get_cycle_count(self):
        """Retourne le nombre total de cycles complets écoulés."""
        return self.cycle_count

    def is_day(self):
        """Retourne True si c'est le jour (DAWN ou DAY)."""
        return self.current_period in [TimeOfDay.DAWN, TimeOfDay.DAY]

    def is_night(self):
        """Retourne True si c'est la nuit (DUSK ou NIGHT)."""
        return self.current_period in [TimeOfDay.DUSK, TimeOfDay.NIGHT]

    def register_on_period_change(self, callback):
        """
        Enregistre une fonction à appeler lors d'un changement de période.
        Le callback recevra (ancienne_periode, nouvelle_periode) en arguments.
        """
        if callback not in self._on_period_change_callbacks:
            self._on_period_change_callbacks.append(callback)

    def unregister_on_period_change(self, callback):
        """Désenregistre une fonction de callback."""
        try:
            self._on_period_change_callbacks.remove(callback)
        except ValueError:
            pass # Callback non trouvé

    def _notify_period_change(self, old_period, new_period):
        """Appelle tous les callbacks enregistrés."""
        # print(f"Changement de période : {old_period.name} -> {new_period.name} (Cycle {self.cycle_count}, Temps: {self.current_time_in_cycle:.2f}s)")
        for callback in self._on_period_change_callbacks:
            try:
                callback(old_period, new_period)
            except Exception as e:
                print(f"Erreur dans le callback de changement de période ({callback.__name__}): {e}")

    def get_overall_progress_normalized(self):
        """
        Retourne une valeur normalisée (0.0 à 1.0) représentant la progression
        globale du cycle, utile pour les transitions douces (ex: couleur du ciel).
        0.0 = Début de l'aube
        0.25 = Milieu du jour (approximatif)
        0.5 = Début du crépuscule
        0.75 = Milieu de la nuit (approximatif)
        1.0 = Fin de la nuit (juste avant la nouvelle aube)
        """
        # Cette fonction fournit une interpolation plus linéaire que get_cycle_progress
        # pour des effets visuels comme la couleur du ciel.
        # Elle mappe le cycle sur une échelle 0-1 où 0.5 est le zénith (milieu du jour)
        # et 0/1 est minuit. C'est une simplification.
        # Une implémentation plus précise pourrait utiliser une courbe sinusoïdale.

        progress = self.get_cycle_progress() # 0.0 à 1.0

        # Simplification: on considère que le "pic" de lumière est au milieu de la période DAY
        day_start_ratio = self.start_times[TimeOfDay.DAY] / self.cycle_duration
        day_duration_ratio = self.durations[TimeOfDay.DAY] / self.cycle_duration
        zenith_ratio = day_start_ratio + (day_duration_ratio / 2.0)

        # Mapper la progression pour que zenith_ratio devienne 0.5
        if progress < zenith_ratio:
            # De minuit (0.0) au zénith (zenith_ratio) -> mapper vers 0.0 à 0.5
            return 0.5 * (progress / zenith_ratio)
        else:
            # Du zénith (zenith_ratio) à minuit (1.0) -> mapper vers 0.5 à 1.0
            return 0.5 + 0.5 * ((progress - zenith_ratio) / (1.0 - zenith_ratio))

    def get_sun_angle(self, zenith_angle=90.0):
        """
        Calcule l'angle approximatif du soleil basé sur la progression du cycle.

        Args:
            zenith_angle (float): Angle du soleil au zénith (milieu du jour), en degrés.
                                  Typiquement 90 (directement au-dessus).

        Returns:
            float: Angle du soleil en degrés (0 = horizon au lever/coucher, zenith_angle = zénith).
                   Peut être négatif la nuit.
        """
        progress = self.get_cycle_progress() # 0.0 à 1.0
        # Utiliser une fonction sinusoïdale pour simuler le mouvement du soleil
        # sin(0) = 0, sin(pi/2) = 1, sin(pi) = 0, sin(3pi/2) = -1, sin(2pi) = 0
        # On mappe progress (0 à 1) sur l'angle (0 à 2*pi)
        angle_rad = progress * 2.0 * math.pi
        # sin(angle_rad) varie de -1 à 1.
        # On veut 0 à l'horizon (progress 0 et 0.5 approx), zenith_angle au zénith (progress 0.25 approx)
        # Ajustons la phase pour que le lever soit à progress=0 (ou proche de DAWN start)
        dawn_start_ratio = self.start_times[TimeOfDay.DAWN] / self.cycle_duration
        phase_shift = -math.pi / 2 # Pour que sin commence à -1 (minuit)
        # Recalculer l'angle avec le décalage pour aligner sur le cycle
        angle_rad_shifted = (progress * 2.0 * math.pi) + phase_shift

        # sin varie de -1 (minuit) à 1 (zénith)
        sin_value = math.sin(angle_rad_shifted)

        # Mapper sin_value (-1 à 1) vers l'angle du soleil (peut être négatif la nuit)
        # Lorsque sin_value = 1 (zénith), angle = zenith_angle
        # Lorsque sin_value = 0 (horizon), angle = 0
        # Lorsque sin_value = -1 (minuit), angle = -zenith_angle (ou une valeur négative)
        sun_angle = sin_value * zenith_angle

        return sun_angle