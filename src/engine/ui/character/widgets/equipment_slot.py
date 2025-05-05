# src/engine/ui/character/widgets/equipment_slot.py
"""
Widget représentant un emplacement d'équipement (tête, torse, arme, etc.).
Accepte les objets déposés (drop) s'ils sont du type approprié.
"""

# Imports nécessaires (à compléter)
# from ...ui_base import UIWidget
# from ...inventory.items import Item, EquipmentType # EquipmentType pourrait être un Enum: HEAD, CHEST, WEAPON...
# from ...ui.ui_events import DragEvent

class EquipmentSlot: # Remplacer par UIWidget ou classe de base appropriée
    def __init__(self, slot_type: 'EquipmentType', position=(0, 0), size=(50, 50)):
        # super().__init__(position, size) # Appel au constructeur parent si nécessaire
        self.slot_type = slot_type # Type d'équipement accepté (ex: EquipmentType.HEAD)
        self.item: 'Item' = None # L'objet actuellement équipé
        self.position = position
        self.size = size
        self.is_hovered = False
        self.background_color = (40, 40, 60) # Bleu/gris foncé par défaut
        self.hover_color = (60, 60, 80)
        self.placeholder_icon = None # Icône à afficher si le slot est vide (ex: silhouette de casque)

        # Signaux
        self.signals = {'hovered': [], 'unhovered': [], 'item_changed': [], 'dropped_on': []}

    def set_item(self, item: 'Item'):
        """Définit l'objet équipé dans ce slot."""
        if item is not None and not self.can_equip(item):
            print(f"Warning: Cannot equip item {item.name} in slot type {self.slot_type}.")
            return

        old_item = self.item
        self.item = item
        if old_item != self.item:
            self._emit_signal('item_changed', self, self.item, old_item)
        # Mettre à jour l'affichage

    def get_item(self) -> 'Item':
        """Retourne l'objet équipé."""
        return self.item

    def get_slot_type(self) -> 'EquipmentType':
        """Retourne le type d'équipement accepté par ce slot."""
        return self.slot_type

    def can_equip(self, item_to_check: 'Item') -> bool:
        """Vérifie si l'objet donné peut être équipé dans ce slot."""
        # Vérifier si item_to_check a un attribut 'equip_type' ou similaire
        # return hasattr(item_to_check, 'equip_type') and item_to_check.equip_type == self.slot_type
        # Placeholder simple:
        return item_to_check is not None # Accepte tout pour l'instant (à affiner)

    def is_empty(self) -> bool:
        """Vérifie si le slot est vide."""
        return self.item is None

    def update(self, dt, mouse_pos):
        """Met à jour l'état du slot (survol)."""
        # rect = self.get_rect()
        # previously_hovered = self.is_hovered
        # self.is_hovered = rect.collidepoint(mouse_pos)
        #
        # if self.is_hovered and not previously_hovered:
        #     self._emit_signal('hovered', self)
        # elif not self.is_hovered and previously_hovered:
        #     self._emit_signal('unhovered', self)
        pass

    def draw(self, renderer):
        """Dessine le slot d'équipement."""
        # Dessiner le fond (couleur change si survolé)
        # color = self.hover_color if self.is_hovered else self.background_color
        # renderer.draw_rect(self.get_rect(), color)
        #
        # if self.item:
        #     # Dessiner l'icône de l'objet équipé
        #     # icon = self.item.get_icon()
        #     # renderer.draw_texture(icon, self.position)
        #     pass
        # else:
        #     # Dessiner l'icône placeholder si elle existe
        #     # if self.placeholder_icon:
        #     #     renderer.draw_texture(self.placeholder_icon, self.position)
        #     pass
        print(f"Drawing EquipmentSlot ({self.slot_type}) at {self.position} (Item: {self.item.name if self.item else 'None'}) (Placeholder)") # Placeholder
        pass

    def handle_input(self, event, mouse_pos):
        """Gère le drop d'un objet sur le slot."""
        # if event.type == MOUSEBUTTONUP and event.button == 1: # Relâchement clic gauche
        #     # Si un drag est en cours globalement et que la souris est sur ce slot
        #     # if DragEvent.is_dragging() and self.get_rect().collidepoint(mouse_pos):
        #     #     dragged_item = DragEvent.get_item()
        #     #     if self.can_equip(dragged_item):
        #     #         self._emit_signal('dropped_on', self, dragged_item)
        #     #         # La logique d'équipement réelle se fait dans le menu parent
        #     #         return True # Événement géré
        #     #     else:
        #     #         # Indiquer visuellement que le drop est invalide ?
        #     #         pass
        #     pass
        print(f"EquipmentSlot handling input: {event} (Placeholder)") # Placeholder
        return False

    def get_rect(self):
        """Retourne le rectangle englobant le slot."""
        # return Rect(self.position, self.size) # Exemple
        return (self.position[0], self.position[1], self.size[0], self.size[1]) # Tuple simple pour placeholder

    def connect_signal(self, signal_name, callback):
        """Connecte une fonction à un signal."""
        if signal_name in self.signals:
            self.signals[signal_name].append(callback)
        else:
            print(f"Warning: Signal '{signal_name}' not found in EquipmentSlot.")

    def _emit_signal(self, signal_name, *args):
        """Émet un signal, appelant toutes les fonctions connectées."""
        if signal_name in self.signals:
            for callback in self.signals[signal_name]:
                callback(*args)

# Fonctions utilitaires si nécessaire