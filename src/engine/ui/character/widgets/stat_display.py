# src/engine/ui/character/widgets/stat_display.py
"""
Widget simple pour afficher une statistique (nom et valeur).
Utilisé dans la fiche de personnage.
"""

# Imports nécessaires (à compléter)
# from ...ui_base import UIWidget
# from ...ui.widgets.label import Label # Pourrait utiliser un Label interne

class StatDisplay: # Remplacer par UIWidget ou classe de base appropriée
    def __init__(self, stat_name: str, position=(0, 0), font_size=12, color=(255, 255, 255)):
        # super().__init__(position) # Appel au constructeur parent si nécessaire
        self.stat_name = stat_name.replace('_', ' ').capitalize() # Nom formaté pour l'affichage
        self.position = position
        self.font_size = font_size
        self.color = color
        self.value_text = "0" # Texte final à afficher pour la valeur

        # Pourrait utiliser un widget Label interne pour gérer le rendu du texte
        # self.label = Label(text=f"{self.stat_name}: {self.value_text}", position=position, font_size=font_size, color=color)

    def set_value(self, current_value, base_value=None, bonus_value=None):
        """Met à jour la valeur affichée de la statistique."""
        if base_value is not None and bonus_value is not None:
            sign = "+" if bonus_value >= 0 else ""
            self.value_text = f"{current_value} ({base_value}{sign}{bonus_value})"
        elif base_value is not None: # Si on a juste la base et la valeur totale
             bonus = current_value - base_value
             sign = "+" if bonus >= 0 else ""
             self.value_text = f"{current_value} ({base_value}{sign}{bonus})"
        else:
            self.value_text = str(current_value)

        # Mettre à jour le label interne si utilisé
        # self.label.set_text(f"{self.stat_name}: {self.value_text}")

    def update(self, dt):
        """Mise à jour (généralement pas nécessaire pour un affichage statique)."""
        # self.label.update(dt) # Si label interne
        pass

    def draw(self, renderer):
        """Dessine le nom et la valeur de la statistique."""
        # Utiliser le label interne ou dessiner directement le texte
        # self.label.draw(renderer)
        # Alternative:
        display_text = f"{self.stat_name}: {self.value_text}"
        # renderer.draw_text(display_text, self.position, self.font_size, self.color) # Méthode hypothétique
        print(f"Drawing StatDisplay: {display_text} at {self.position} (Placeholder)") # Placeholder
        pass

    def handle_input(self, event):
        """Gestion des entrées (généralement pas nécessaire)."""
        # return self.label.handle_input(event) # Si label interne
        return False # Widget passif

    def get_rect(self):
        """Retourne le rectangle englobant (si nécessaire, dépend du label interne ou calcul manuel)."""
        # return self.label.get_rect() # Si label interne
        # Estimation simple pour placeholder:
        estimated_width = len(f"{self.stat_name}: {self.value_text}") * self.font_size * 0.6
        estimated_height = self.font_size
        return (self.position[0], self.position[1], estimated_width, estimated_height) # Tuple simple pour placeholder

# Fonctions utilitaires si nécessaire