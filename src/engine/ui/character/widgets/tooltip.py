# src/engine/ui/character/widgets/tooltip.py
"""
Widget pour afficher des info-bulles (tooltips) contextuelles.
Apparaît près de la souris lors du survol d'éléments interactifs (objets, compétences).
"""

# Imports nécessaires (à compléter)
# from ...ui_base import UIWidget
# from ...ui.widgets.label import Label # Pourrait utiliser des labels internes
# from ...ui.layout.stack_layout import StackLayout # Pour organiser le contenu

class Tooltip: # Remplacer par UIWidget ou classe de base appropriée
    def __init__(self, offset=(15, 15), font_size=12, background_color=(30, 30, 30, 230), text_color=(255, 255, 255)):
        # super().__init__() # Appel au constructeur parent si nécessaire
        self.offset = offset # Décalage par rapport à la position de la souris
        self.font_size = font_size
        self.background_color = background_color # Fond semi-transparent
        self.text_color = text_color
        self.visible = False
        self.content = [] # Liste de lignes de texte ou de widgets Label/Layout
        self.position = (0, 0) # Position calculée dynamiquement
        self.size = (0, 0) # Taille calculée dynamiquement en fonction du contenu

        # Pourrait utiliser un layout interne pour gérer l'organisation du contenu
        # self.layout = StackLayout(orientation='vertical', padding=5)

    def show(self, content_data):
        """Affiche le tooltip avec le contenu spécifié."""
        self.visible = True
        self._build_content(content_data)
        # La position sera mise à jour dans update()

    def hide(self):
        """Masque le tooltip."""
        self.visible = False
        self.content = []
        # self.layout.clear_widgets() # Si layout interne

    def is_visible(self) -> bool:
        """Retourne True si le tooltip est actuellement visible."""
        return self.visible

    def _build_content(self, data):
        """Construit le contenu du tooltip à partir des données fournies."""
        # Vider le contenu précédent
        self.content = []
        # self.layout.clear_widgets()

        # Analyser 'data' (pourrait être un dictionnaire, une liste de strings, etc.)
        # Exemple simple avec une liste de strings:
        if isinstance(data, list):
            self.content = data
            # for line in data:
            #     label = Label(text=line, font_size=self.font_size, color=self.text_color)
            #     self.layout.add_widget(label)
        elif isinstance(data, dict):
            # Exemple: afficher clé: valeur
            # for key, value in data.items():
            #     label = Label(text=f"{key.capitalize()}: {value}", font_size=self.font_size, color=self.text_color)
            #     self.layout.add_widget(label)
            # Conversion simple pour le placeholder:
            self.content = [f"{k.capitalize()}: {v}" for k, v in data.items()]
        elif isinstance(data, str):
             self.content = [data]
             # label = Label(text=data, font_size=self.font_size, color=self.text_color)
             # self.layout.add_widget(label)

        # Calculer la nouvelle taille du tooltip basée sur le contenu
        self._calculate_size()
        print(f"Tooltip content set: {self.content} (Placeholder)") # Placeholder

    def _calculate_size(self):
        """Calcule la taille nécessaire pour afficher le contenu."""
        # Basé sur le layout interne ou calcul manuel
        # max_width = 0
        # total_height = 0
        # padding = 10 # Espace autour du texte
        # line_height = self.font_size + 2
        #
        # for line in self.content:
        #     # Estimer la largeur du texte (besoin d'une fonction de mesure de texte)
        #     # text_width = measure_text_width(line, self.font_size) # Fonction hypothétique
        #     text_width = len(line) * self.font_size * 0.6 # Estimation simple
        #     max_width = max(max_width, text_width)
        #     total_height += line_height
        #
        # self.size = (max_width + padding, total_height + padding)
        # self.layout.set_size(self.size) # Si layout interne
        # Placeholder simple:
        if not self.content:
            self.size = (0, 0)
            return
        max_len = max(len(line) for line in self.content) if self.content else 0
        width = int(max_len * self.font_size * 0.7) + 20 # Estimation + padding
        height = len(self.content) * (self.font_size + 4) + 10 # Estimation + padding
        self.size = (width, height)
        print(f"Tooltip size calculated: {self.size} (Placeholder)") # Placeholder


    def update(self, dt, mouse_pos):
        """Met à jour la position du tooltip pour suivre la souris."""
        if self.visible:
            self.position = (mouse_pos[0] + self.offset[0], mouse_pos[1] + self.offset[1])
            # Ajouter logique pour s'assurer que le tooltip reste dans les limites de l'écran
            # screen_width, screen_height = get_screen_size() # Fonction hypothétique
            # if self.position[0] + self.size[0] > screen_width:
            #     self.position = (mouse_pos[0] - self.size[0] - self.offset[0], self.position[1])
            # if self.position[1] + self.size[1] > screen_height:
            #     self.position = (self.position[0], mouse_pos[1] - self.size[1] - self.offset[1])
            # self.layout.set_position(self.position) # Si layout interne

    def draw(self, renderer):
        """Dessine le tooltip s'il est visible."""
        if self.visible:
            # Dessiner le fond
            # rect = Rect(self.position, self.size) # Exemple
            # renderer.draw_rect(rect, self.background_color) # Méthode hypothétique
            #
            # # Dessiner le contenu (via layout ou manuellement)
            # self.layout.draw(renderer)
            # Alternative:
            # current_y = self.position[1] + 5 # Padding top
            # for line in self.content:
            #     # renderer.draw_text(line, (self.position[0] + 5, current_y), self.font_size, self.text_color)
            #     current_y += self.font_size + 4 # Line height
            print(f"Drawing Tooltip at {self.position} with size {self.size} (Placeholder)") # Placeholder
            pass

    def handle_input(self, event):
        """Gestion des entrées (généralement pas nécessaire)."""
        return False # Widget passif

# Fonctions utilitaires si nécessaire (ex: mesure de texte)