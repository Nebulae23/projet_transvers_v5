# Mock pour le système de gestion des entrées
class MockInputManager:
    def __init__(self):
        self._key_states = {}
        self._mouse_buttons = {}
        self._mouse_position = (0, 0)
        self._events = [] # Liste pour simuler les événements d'entrée

    def is_key_pressed(self, key_code):
        """Vérifie si une touche est actuellement pressée."""
        return self._key_states.get(key_code, False)

    def is_mouse_button_pressed(self, button_code):
        """Vérifie si un bouton de la souris est actuellement pressé."""
        return self._mouse_buttons.get(button_code, False)

    def get_mouse_position(self):
        """Retourne la position actuelle de la souris."""
        return self._mouse_position

    # Méthodes pour simuler des entrées
    def simulate_key_press(self, key_code):
        """Simule l'appui sur une touche."""
        self._key_states[key_code] = True
        self._events.append({'type': 'key_down', 'key': key_code})

    def simulate_key_release(self, key_code):
        """Simule le relâchement d'une touche."""
        self._key_states[key_code] = False
        self._events.append({'type': 'key_up', 'key': key_code})

    def simulate_mouse_press(self, button_code, position=None):
        """Simule un clic de souris."""
        if position:
            self._mouse_position = position
        self._mouse_buttons[button_code] = True
        self._events.append({'type': 'mouse_down', 'button': button_code, 'pos': self._mouse_position})

    def simulate_mouse_release(self, button_code, position=None):
        """Simule le relâchement d'un bouton de souris."""
        if position:
            self._mouse_position = position
        self._mouse_buttons[button_code] = False
        self._events.append({'type': 'mouse_up', 'button': button_code, 'pos': self._mouse_position})

    def simulate_mouse_move(self, position):
        """Simule le mouvement de la souris."""
        self._mouse_position = position
        self._events.append({'type': 'mouse_motion', 'pos': self._mouse_position})

    def process_events(self):
        """Retourne et vide la liste des événements simulés."""
        # Dans un vrai système, cela lirait les événements de la bibliothèque sous-jacente (SDL, Pygame, etc.)
        processed_events = list(self._events) # Copie pour éviter modification pendant itération externe
        self._events = [] # Vide la file d'attente interne
        return processed_events

    def clear_states(self):
        """Réinitialise tous les états simulés."""
        self._key_states = {}
        self._mouse_buttons = {}
        self._mouse_position = (0, 0)
        self._events = []