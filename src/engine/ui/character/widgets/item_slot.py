# src/engine/ui/character/widgets/item_slot.py
"""
Widget représentant un emplacement (slot) dans l'inventaire.
Gère l'affichage de l'icône de l'objet, la quantité, et le drag & drop.
"""

# Imports nécessaires (à compléter)
# from ...ui_base import UIWidget # Ou une classe de base pour les widgets
# from ...inventory.items import Item # Pour typer l'objet contenu
# from ...ui.ui_events import DragEvent # Pour gérer le drag & drop

class ItemSlot: # Remplacer par UIWidget ou classe de base appropriée
    def __init__(self, item: 'Item' = None, quantity: int = 0, position=(0, 0), size=(50, 50)):
        # super().__init__(position, size) # Appel au constructeur parent si nécessaire
        self.item = item
        self.quantity = quantity
        self.position = position # Position relative au parent (ex: grille)
        self.size = size
        self.is_hovered = False
        self.is_dragging = False # Indique si cet item est en cours de déplacement
        self.background_color = (50, 50, 50) # Gris foncé par défaut
        self.hover_color = (70, 70, 70)
        # Signaux (à implémenter avec un système d'événements/callbacks)
        self.signals = {'hovered': [], 'unhovered': [], 'clicked': [], 'drag_started': [], 'dropped_on': []}

    def set_item(self, item: 'Item', quantity: int = 1):
        """Définit l'objet et la quantité pour ce slot."""
        self.item = item
        self.quantity = quantity if item else 0
        # Mettre à jour l'affichage (icône, texte de quantité)

    def get_item(self) -> 'Item':
        """Retourne l'objet contenu dans ce slot."""
        return self.item

    def get_quantity(self) -> int:
        """Retourne la quantité de l'objet."""
        return self.quantity

    def is_empty(self) -> bool:
        """Vérifie si le slot est vide."""
        return self.item is None

    def update(self, dt, mouse_pos):
        """Met à jour l'état du slot (survol)."""
        # Vérifier si la souris est sur le slot
        # rect = self.get_rect() # Obtenir le rectangle du slot
        # previously_hovered = self.is_hovered
        # self.is_hovered = rect.collidepoint(mouse_pos) # Méthode hypothétique
        #
        # if self.is_hovered and not previously_hovered:
        #     self._emit_signal('hovered', self)
        # elif not self.is_hovered and previously_hovered:
        #     self._emit_signal('unhovered', self)
        pass

    def draw(self, renderer):
        """Dessine le slot et son contenu."""
        # Dessiner le fond (couleur change si survolé)
        # color = self.hover_color if self.is_hovered else self.background_color
        # renderer.draw_rect(self.get_rect(), color) # Méthode hypothétique
        #
        # if self.item and not self.is_dragging:
        #     # Dessiner l'icône de l'objet
        #     # icon = self.item.get_icon() # Méthode hypothétique
        #     # renderer.draw_texture(icon, self.position) # Ajuster position/taille
        #
        #     # Dessiner la quantité si > 1
        #     if self.quantity > 1:
        #         # renderer.draw_text(str(self.quantity), position_quantity, font_size=10, color=(255, 255, 255))
        #         pass
        print(f"Drawing ItemSlot at {self.position} (Item: {self.item.name if self.item else 'None'}) (Placeholder)") # Placeholder
        pass

    def handle_input(self, event, mouse_pos):
        """Gère les clics et le début du drag & drop."""
        # if self.get_rect().collidepoint(mouse_pos):
        #     if event.type == MOUSEBUTTONDOWN: # Constante hypothétique
        #         if event.button == 1: # Clic gauche
        #             self._emit_signal('clicked', self)
        #             if self.item:
        #                 # Commencer le drag & drop
        #                 self.is_dragging = True
        #                 self._emit_signal('drag_started', self)
        #                 # Créer un événement DragEvent global ?
        #                 # DragEvent.start_drag(self.item, self)
        #                 return True # Événement géré
        #         elif event.button == 3: # Clic droit
        #             # Ouvrir menu contextuel ?
        #             pass
        # elif event.type == MOUSEBUTTONUP and event.button == 1: # Relâchement clic gauche
        #     # Si un drag est en cours globalement et que la souris est sur ce slot
        #     # if DragEvent.is_dragging() and self.get_rect().collidepoint(mouse_pos):
        #     #     self._emit_signal('dropped_on', self)
        #     #     return True # Événement géré
        #     pass
        print(f"ItemSlot handling input: {event} (Placeholder)") # Placeholder
        return False

    def get_rect(self):
        """Retourne le rectangle englobant le slot."""
        # Doit retourner un objet Rect (type Pygame Rect ou similaire)
        # return Rect(self.position, self.size) # Exemple
        return (self.position[0], self.position[1], self.size[0], self.size[1]) # Tuple simple pour placeholder

    def connect_signal(self, signal_name, callback):
        """Connecte une fonction à un signal."""
        if signal_name in self.signals:
            self.signals[signal_name].append(callback)
        else:
            print(f"Warning: Signal '{signal_name}' not found in ItemSlot.")

    def _emit_signal(self, signal_name, *args):
        """Émet un signal, appelant toutes les fonctions connectées."""
        if signal_name in self.signals:
            for callback in self.signals[signal_name]:
                callback(*args)

# Fonctions utilitaires si nécessaire