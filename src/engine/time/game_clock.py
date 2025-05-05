# src/engine/time/game_clock.py
import time

class GameClock:
    """
    Gère l'horloge interne du jeu, indépendante du temps réel.
    Permet de contrôler la vitesse du temps et de déclencher des événements temporels.
    """
    def __init__(self, time_scale=1.0):
        """
        Initialise l'horloge de jeu.

        Args:
            time_scale (float): Facteur d'échelle pour la vitesse du temps.
                                1.0 = temps réel, > 1.0 = accéléré, < 1.0 = ralenti.
        """
        self._game_time = 0.0  # Temps total écoulé dans le jeu en secondes
        self._delta_time = 0.0  # Temps écoulé depuis la dernière frame en secondes de jeu
        self._time_scale = time_scale
        self._last_real_time = time.perf_counter()
        self._paused = False
        self._time_events = [] # Liste de tuples (target_time, callback, recurring, interval)

    def update(self):
        """Met à jour l'horloge de jeu."""
        if self._paused:
            self._delta_time = 0.0
            return

        current_real_time = time.perf_counter()
        real_delta_time = current_real_time - self._last_real_time
        self._last_real_time = current_real_time

        self._delta_time = real_delta_time * self._time_scale
        self._game_time += self._delta_time

        self._check_time_events()

    def _check_time_events(self):
        """Vérifie et déclenche les événements temporels programmés."""
        triggered_events = []
        new_events = [] # Pour les événements récurrents

        for i, event in enumerate(self._time_events):
            target_time, callback, recurring, interval = event
            if self._game_time >= target_time:
                try:
                    callback()
                except Exception as e:
                    print(f"Erreur lors de l'exécution de l'événement temporel : {e}")

                triggered_events.append(i)

                if recurring and interval is not None:
                    # Reprogrammer l'événement récurrent
                    next_target_time = target_time + interval
                    # S'assurer que le prochain temps cible est dans le futur
                    while next_target_time <= self._game_time:
                         next_target_time += interval
                    new_events.append((next_target_time, callback, recurring, interval))

        # Supprimer les événements déclenchés (en ordre inverse pour éviter les problèmes d'index)
        for i in sorted(triggered_events, reverse=True):
            del self._time_events[i]

        # Ajouter les nouveaux événements récurrents reprogrammés
        self._time_events.extend(new_events)
        # Trier les événements par temps cible pour optimiser la vérification
        self._time_events.sort(key=lambda x: x[0])


    def set_time_scale(self, scale):
        """Définit le facteur d'échelle du temps."""
        if scale >= 0:
            self._time_scale = scale
        else:
            print("Avertissement : time_scale ne peut pas être négatif.")

    def get_time_scale(self):
        """Retourne le facteur d'échelle actuel du temps."""
        return self._time_scale

    def get_game_time(self):
        """Retourne le temps total écoulé dans le jeu."""
        return self._game_time

    def get_delta_time(self):
        """Retourne le temps écoulé depuis la dernière frame (en temps de jeu)."""
        return self._delta_time

    def pause(self):
        """Met en pause l'horloge de jeu."""
        self._paused = True
        self._delta_time = 0.0 # Assurer que delta_time est 0 quand en pause

    def resume(self):
        """Reprend l'horloge de jeu."""
        if self._paused:
            self._paused = False
            # Réinitialiser last_real_time pour éviter un grand saut de delta_time
            self._last_real_time = time.perf_counter()

    def is_paused(self):
        """Retourne True si l'horloge est en pause."""
        return self._paused

    def schedule_event(self, delay_seconds, callback, recurring=False, interval_seconds=None):
        """
        Programme un événement à déclencher après un certain délai en temps de jeu.

        Args:
            delay_seconds (float): Délai en secondes de jeu avant le déclenchement.
            callback (callable): La fonction à appeler lorsque l'événement se déclenche.
            recurring (bool): Si True, l'événement se répétera.
            interval_seconds (float, optional): Intervalle en secondes de jeu pour les événements récurrents.
                                                Requis si recurring est True.
        """
        if recurring and interval_seconds is None:
            print("Erreur: interval_seconds est requis pour un événement récurrent.")
            return

        if recurring and interval_seconds <= 0:
             print("Erreur: interval_seconds doit être positif pour un événement récurrent.")
             return

        target_time = self._game_time + delay_seconds
        event = (target_time, callback, recurring, interval_seconds)
        self._time_events.append(event)
        # Trier pour optimiser la vérification
        self._time_events.sort(key=lambda x: x[0])

    def cancel_events(self, callback_to_cancel):
        """Annule tous les événements programmés associés à un callback spécifique."""
        initial_count = len(self._time_events)
        self._time_events = [event for event in self._time_events if event[1] != callback_to_cancel]
        removed_count = initial_count - len(self._time_events)
        # print(f"{removed_count} événements annulés pour le callback {callback_to_cancel.__name__}")
        return removed_count