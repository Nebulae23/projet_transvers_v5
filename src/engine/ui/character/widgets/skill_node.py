# src/engine/ui/character/widgets/skill_node.py
"""
Widget représentant un nœud (compétence) dans l'arbre de compétences.
Affiche l'icône, le statut (bloqué, achetable, acquis) et gère l'interaction.
"""

# Imports nécessaires (à compléter)
# from ...ui_base import UIWidget
# from ...progression.skills import SkillData # Structure de données pour une compétence

class SkillNode: # Remplacer par UIWidget ou classe de base appropriée
    # États possibles du nœud
    STATE_LOCKED = 0
    STATE_AVAILABLE = 1
    STATE_LEARNED = 2

    def __init__(self, skill_data: 'SkillData', position=(0, 0), size=(40, 40)):
        # super().__init__(position, size) # Appel au constructeur parent si nécessaire
        self.skill_data = skill_data # Contient id, name, description, icon, cost, prerequisites, etc.
        self.position = position
        self.size = size
        self.state = SkillNode.STATE_LOCKED # État actuel (locked, available, learned)
        self.can_afford = False # Si le joueur a assez de points (si state == AVAILABLE)
        self.is_hovered = False

        # Couleurs/styles pour les différents états (à définir)
        self.colors = {
            SkillNode.STATE_LOCKED: (100, 100, 100), # Gris
            SkillNode.STATE_AVAILABLE: (200, 200, 0), # Jaune/Or
            SkillNode.STATE_LEARNED: (0, 200, 0), # Vert
        }
        self.hover_border_color = (255, 255, 255) # Blanc

        # Signaux
        self.signals = {'hovered': [], 'unhovered': [], 'clicked': []}

    def get_id(self):
        """Retourne l'ID de la compétence associée."""
        return self.skill_data.id # Supposant que skill_data a un attribut 'id'

    def get_skill_data(self) -> 'SkillData':
        """Retourne les données complètes de la compétence."""
        return self.skill_data

    def set_state(self, state: int, can_afford: bool):
        """Met à jour l'état visuel du nœud."""
        self.state = state
        self.can_afford = can_afford
        # Potentiellement changer l'apparence (couleur, icône grisée ?)

    def update(self, dt, mouse_pos):
        """Met à jour l'état du nœud (survol)."""
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
        """Dessine le nœud de compétence."""
        # Déterminer la couleur de fond/bordure en fonction de l'état et du survol
        # base_color = self.colors.get(self.state, (0, 0, 0))
        # if self.state == SkillNode.STATE_AVAILABLE and not self.can_afford:
        #     # Griser ou indiquer différemment si achetable mais pas assez de points
        #     base_color = (150, 150, 100) # Exemple : Jaune plus sombre
        #
        # rect = self.get_rect()
        # renderer.draw_rect(rect, base_color) # Dessiner le fond
        #
        # # Dessiner l'icône de la compétence (peut être grisée si locked)
        # icon = self.skill_data.get_icon() # Méthode hypothétique
        # if self.state == SkillNode.STATE_LOCKED:
        #     # Appliquer un effet "grisé" à l'icône
        #     pass
        # renderer.draw_texture(icon, self.position) # Ajuster position/taille
        #
        # # Dessiner une bordure si survolé
        # if self.is_hovered:
        #     renderer.draw_rect_outline(rect, self.hover_border_color, thickness=2) # Méthode hypothétique
        print(f"Drawing SkillNode {self.get_id()} at {self.position} (State: {self.state}) (Placeholder)") # Placeholder
        pass

    def handle_input(self, event, mouse_pos):
        """Gère les clics sur le nœud."""
        # if self.get_rect().collidepoint(mouse_pos):
        #     if event.type == MOUSEBUTTONDOWN and event.button == 1: # Clic gauche
        #         # Émettre le signal 'clicked' uniquement si le nœud est potentiellement interactif
        #         if self.state == SkillNode.STATE_AVAILABLE:
        #             self._emit_signal('clicked', self)
        #             return True # Événement géré
        #         else:
        #             # On pourrait quand même émettre un signal pour indiquer un clic sur un nœud non achetable/déjà appris
        #             # self._emit_signal('clicked_invalid', self)
        #             pass
        print(f"SkillNode handling input: {event} (Placeholder)") # Placeholder
        return False

    def get_rect(self):
        """Retourne le rectangle englobant le nœud."""
        # return Rect(self.position, self.size) # Exemple
        return (self.position[0], self.position[1], self.size[0], self.size[1]) # Tuple simple pour placeholder

    def connect_signal(self, signal_name, callback):
        """Connecte une fonction à un signal."""
        if signal_name in self.signals:
            self.signals[signal_name].append(callback)
        else:
            print(f"Warning: Signal '{signal_name}' not found in SkillNode.")

    def _emit_signal(self, signal_name, *args):
        """Émet un signal, appelant toutes les fonctions connectées."""
        if signal_name in self.signals:
            for callback in self.signals[signal_name]:
                callback(*args)

# Fonctions utilitaires si nécessaire