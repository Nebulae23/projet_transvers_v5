# src/engine/ui/styles/animations.py
import pygame
import math

# Fonctions d'interpolation (easing functions)
def linear(t):
    return t

def ease_in_quad(t):
    return t * t

def ease_out_quad(t):
    return t * (2 - t)

def ease_in_out_quad(t):
    return 2 * t * t if t < 0.5 else -1 + (4 - 2 * t) * t

def ease_in_sine(t):
    return 1 - math.cos((t * math.pi) / 2)

def ease_out_sine(t):
    return math.sin((t * math.pi) / 2)

def ease_in_out_sine(t):
    return -(math.cos(math.pi * t) - 1) / 2

# Classe de base pour les animations
class Animation:
    def __init__(self, duration, target_widget, property_name, start_value, end_value, easing_func=ease_in_out_quad):
        self.duration = duration
        self.target_widget = target_widget
        self.property_name = property_name
        self.start_value = start_value
        self.end_value = end_value
        self.easing_func = easing_func
        self.elapsed_time = 0.0
        self.is_running = False
        self.is_finished = False

    def start(self):
        self.elapsed_time = 0.0
        self.is_running = True
        self.is_finished = False
        # S'assurer que la valeur de départ est appliquée
        self._set_property(self.start_value)

    def update(self, dt):
        if not self.is_running or self.is_finished:
            return

        self.elapsed_time += dt
        progress = min(self.elapsed_time / self.duration, 1.0)
        eased_progress = self.easing_func(progress)

        # Interpolation pour différents types de valeurs
        if isinstance(self.start_value, (int, float)):
            current_value = self.start_value + (self.end_value - self.start_value) * eased_progress
        elif isinstance(self.start_value, (tuple, list)) and all(isinstance(v, (int, float)) for v in self.start_value):
            # Interpolation pour les tuples/listes (ex: couleurs, positions)
            current_value = tuple(
                s + (e - s) * eased_progress
                for s, e in zip(self.start_value, self.end_value)
            )
            # Convertir en entiers si les valeurs de départ/fin étaient des entiers (pour les couleurs/positions)
            if all(isinstance(v, int) for v in self.start_value):
                 current_value = tuple(int(round(v)) for v in current_value)
        else:
            # Pour d'autres types, on ne peut qu'assigner la valeur finale à la fin
            current_value = self.end_value if progress >= 1.0 else self.start_value

        self._set_property(current_value)

        if progress >= 1.0:
            self.is_finished = True
            self.is_running = False

    def _set_property(self, value):
        if hasattr(self.target_widget, self.property_name):
            setattr(self.target_widget, self.property_name, value)
            # Potentiellement déclencher une mise à jour visuelle si nécessaire
            if hasattr(self.target_widget, 'needs_redraw'):
                self.target_widget.needs_redraw = True
            if hasattr(self.target_widget, 'update_appearance'): # Pour les widgets complexes
                self.target_widget.update_appearance()
        else:
            print(f"Warning: Property '{self.property_name}' not found on widget {self.target_widget}")

# Exemples d'animations courantes (à instancier)
def fade_in(widget, duration=0.5):
    # Suppose que le widget a une propriété 'alpha' ou similaire
    # Ou manipule sa surface directement si possible
    # Ceci est un exemple conceptuel, l'implémentation dépendra des widgets
    if hasattr(widget, 'alpha'):
        return Animation(duration, widget, 'alpha', 0, 255, ease_in_quad)
    elif hasattr(widget, 'image') and hasattr(widget.image, 'set_alpha'):
         widget.image.set_alpha(0) # Start transparent
         # Need a custom animation class or logic to handle surface alpha
         print("Fade-in for surface alpha needs custom handling.")
         return None # Placeholder
    return None

def fade_out(widget, duration=0.5):
    if hasattr(widget, 'alpha'):
        return Animation(duration, widget, 'alpha', 255, 0, ease_out_quad)
    elif hasattr(widget, 'image') and hasattr(widget.image, 'set_alpha'):
         # Need a custom animation class or logic to handle surface alpha
         print("Fade-out for surface alpha needs custom handling.")
         return None # Placeholder
    return None

def slide_in_from_left(widget, duration=0.5, screen_width=800):
     # Suppose que le widget a une propriété 'rect' ou 'position'
     if hasattr(widget, 'rect'):
         start_pos = (-widget.rect.width, widget.rect.y)
         end_pos = (widget.original_pos[0], widget.rect.y) # Suppose original_pos stored
         # Need animation for position (tuple)
         print("Slide animation needs position handling.")
         return None # Placeholder
     return None

# TODO: Ajouter d'autres animations (slide, scale, color transition, etc.)
# TODO: Gérer les séquences d'animations ou les groupes d'animations