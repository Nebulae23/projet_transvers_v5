# src/engine/ui/layout/flow_layout.py
import numpy as np
from typing import List, Tuple, Optional

from ..ui_base import LayoutManager, UIElement

class FlowLayout(LayoutManager):
    """
    Dispose les éléments enfants séquentiellement de gauche à droite,
    en passant à la ligne suivante lorsque la largeur disponible est dépassée.
    """
    def __init__(self,
                 padding: Tuple[int, int] = (5, 5), # Padding (horizontal, vertical) entre les éléments
                 margin: Tuple[int, int, int, int] = (0, 0, 0, 0)): # Marge (haut, droite, bas, gauche) à l'intérieur du parent
        """
        Initialise le FlowLayout.

        Args:
            padding (Tuple[int, int]): Espacement (horizontal, vertical) entre les éléments.
            margin (Tuple[int, int, int, int]): Marge intérieure (haut, droite, bas, gauche).
        """
        self.padding = np.array(padding, dtype=int)
        self.margin = np.array(margin, dtype=int) # [top, right, bottom, left]

    def apply_layout(self, element: UIElement):
        """
        Applique la disposition fluide aux enfants visibles de l'élément.
        """
        if not element.children:
            return

        visible_children = [child for child in element.children if child.visible]
        if not visible_children:
            return

        parent_width = element.size[0]
        # parent_height = element.size[1] # Non utilisé directement ici

        # Zone disponible après application des marges
        available_width = parent_width - self.margin[3] - self.margin[1] # width - left - right

        if available_width <= 0:
            # Pas d'espace pour disposer les éléments
            for child in visible_children:
                 child.relative_position = (self.margin[3], self.margin[0]) # Positionner à la marge
            return

        start_x = self.margin[3] # Position X initiale (marge gauche)
        current_x = start_x
        current_y = self.margin[0] # Position Y initiale (marge haute)
        max_row_height = 0 # Hauteur max des éléments de la ligne actuelle

        for i, child in enumerate(visible_children):
            child_width = child.size[0]
            child_height = child.size[1]

            # Déterminer si l'élément doit passer à la ligne suivante
            # Condition: Si ce n'est pas le premier élément de la ligne ET
            #            si l'élément dépasse la largeur disponible sur la ligne actuelle
            needs_wrap = (current_x > start_x) and (current_x + child_width > start_x + available_width)

            if needs_wrap:
                # Passer à la ligne suivante
                current_x = start_x
                current_y += max_row_height + self.padding[1] # Ajouter hauteur max + padding vertical
                max_row_height = 0 # Réinitialiser pour la nouvelle ligne

            # Positionner l'enfant
            child.relative_position = (int(round(current_x)), int(round(current_y)))

            # Mettre à jour la position X pour le prochain élément
            current_x += child_width + self.padding[0]

            # Mettre à jour la hauteur max de la ligne
            max_row_height = max(max_row_height, child_height)

        # Note: Comme pour GridLayout, cette implémentation ne redimensionne pas les enfants.

# --- Tests Basiques ---
if __name__ == "__main__":
    from ..ui_base import UIElement
    from ..widgets.button import Button # Utiliser un widget concret

    root = UIElement(size=(800, 600))
    container = UIElement(position=(50, 50), size=(250, 300), parent=root) # Conteneur plus étroit

    # Appliquer un FlowLayout au conteneur
    flow = FlowLayout(padding=(10, 8), margin=(5, 5, 5, 5))
    container.layout = flow

    # Ajouter des enfants de différentes largeurs
    b1 = Button(text="B1", size=(80, 30), parent=container)
    b2 = Button(text="B2", size=(100, 40), parent=container) # Devrait passer à la ligne
    b3 = Button(text="B3", size=(70, 30), parent=container)
    b4 = Button(text="B4", size=(90, 50), parent=container) # Devrait passer à la ligne
    b5 = Button(text="B5", size=(60, 30), parent=container)

    print("\n--- Test Initial Layout ---")
    container.apply_layout()

    # Vérifier les positions relatives
    # Marges: 5px. Padding: 10px H, 8px V.
    # Largeur conteneur: 250. Largeur dispo: 250 - 5 - 5 = 240.
    # StartX = 5, StartY = 5.

    # Ligne 1:
    # B1: Pos=(5, 5). current_x = 5 + 80 + 10 = 95. max_row_height = 30.
    expected_b1_pos = (5, 5)

    # Ligne 2:
    # B2: current_x (95) + width (100) = 195 <= 240. Ne passe pas à la ligne ? Non, > start_x + available_width (5+240=245) ?
    # Correction: La condition est current_x + child_width > start_x + available_width
    # Pour B2: current_x=95. 95 + 100 = 195. start_x + available_width = 5 + 240 = 245. 195 <= 245. B2 reste sur la ligne 1.
    # B2: Pos=(95, 5). current_x = 95 + 100 + 10 = 205. max_row_height = max(30, 40) = 40.
    expected_b2_pos = (95, 5)

    # Ligne 3:
    # B3: current_x=205. 205 + 70 = 275. start_x + available_width = 245. 275 > 245. B3 passe à la ligne.
    # Nouvelle ligne: current_x = 5. current_y = 5 (marge Y) + 40 (max_row_height L1) + 8 (padding V) = 53.
    # B3: Pos=(5, 53). current_x = 5 + 70 + 10 = 85. max_row_height = 30.
    expected_b3_pos = (5, 53)

    # Ligne 4:
    # B4: current_x=85. 85 + 90 = 175. 175 <= 245. B4 reste sur la ligne 3.
    # B4: Pos=(85, 53). current_x = 85 + 90 + 10 = 185. max_row_height = max(30, 50) = 50.
    expected_b4_pos = (85, 53)

    # Ligne 5:
    # B5: current_x=185. 185 + 60 = 245. 245 <= 245. B5 reste sur la ligne 3.
    # B5: Pos=(185, 53). current_x = 185 + 60 + 10 = 255. max_row_height = max(50, 30) = 50.
    expected_b5_pos = (185, 53)


    print(f"B1 Pos: {b1.relative_position}")
    print(f"B2 Pos: {b2.relative_position}")
    print(f"B3 Pos: {b3.relative_position}")
    print(f"B4 Pos: {b4.relative_position}")
    print(f"B5 Pos: {b5.relative_position}")

    assert np.allclose(b1.relative_position, expected_b1_pos, atol=1), f"B1 position incorrect. Expected ~{expected_b1_pos}"
    assert np.allclose(b2.relative_position, expected_b2_pos, atol=1), f"B2 position incorrect. Expected ~{expected_b2_pos}"
    assert np.allclose(b3.relative_position, expected_b3_pos, atol=1), f"B3 position incorrect. Expected ~{expected_b3_pos}"
    assert np.allclose(b4.relative_position, expected_b4_pos, atol=1), f"B4 position incorrect. Expected ~{expected_b4_pos}"
    assert np.allclose(b5.relative_position, expected_b5_pos, atol=1), f"B5 position incorrect. Expected ~{expected_b5_pos}"

    print("Positions relatives après layout initial OK.")

    print("\n--- Test Layout Update after Container Resize ---")
    container.size = (150, 300) # Rendre le conteneur encore plus étroit
    container.apply_layout()

    # Recalculer les positions attendues
    # Largeur conteneur: 150. Largeur dispo: 150 - 5 - 5 = 140.
    # StartX = 5, StartY = 5.

    # Ligne 1:
    # B1: Pos=(5, 5). current_x = 5 + 80 + 10 = 95. max_row_height = 30.
    expected_b1_pos_new = (5, 5)

    # Ligne 2:
    # B2: current_x=95. 95 + 100 = 195. start_x + available_width = 5 + 140 = 145. 195 > 145. B2 passe à la ligne.
    # Nouvelle ligne: current_x = 5. current_y = 5 + 30 + 8 = 43.
    # B2: Pos=(5, 43). current_x = 5 + 100 + 10 = 115. max_row_height = 40.
    expected_b2_pos_new = (5, 43)

    # Ligne 3:
    # B3: current_x=115. 115 + 70 = 185. 185 > 145. B3 passe à la ligne.
    # Nouvelle ligne: current_x = 5. current_y = 43 + 40 + 8 = 91.
    # B3: Pos=(5, 91). current_x = 5 + 70 + 10 = 85. max_row_height = 30.
    expected_b3_pos_new = (5, 91)

    # Ligne 4:
    # B4: current_x=85. 85 + 90 = 175. 175 > 145. B4 passe à la ligne.
    # Nouvelle ligne: current_x = 5. current_y = 91 + 30 + 8 = 129.
    # B4: Pos=(5, 129). current_x = 5 + 90 + 10 = 105. max_row_height = 50.
    expected_b4_pos_new = (5, 129)

    # Ligne 5:
    # B5: current_x=105. 105 + 60 = 165. 165 > 145. B5 passe à la ligne.
    # Nouvelle ligne: current_x = 5. current_y = 129 + 50 + 8 = 187.
    # B5: Pos=(5, 187). current_x = 5 + 60 + 10 = 75. max_row_height = 30.
    expected_b5_pos_new = (5, 187)

    print(f"B1 New Pos: {b1.relative_position}")
    print(f"B2 New Pos: {b2.relative_position}")
    print(f"B3 New Pos: {b3.relative_position}")
    print(f"B4 New Pos: {b4.relative_position}")
    print(f"B5 New Pos: {b5.relative_position}")

    assert np.allclose(b1.relative_position, expected_b1_pos_new, atol=1), f"B1 position incorrect après resize. Expected ~{expected_b1_pos_new}"
    assert np.allclose(b2.relative_position, expected_b2_pos_new, atol=1), f"B2 position incorrect après resize. Expected ~{expected_b2_pos_new}"
    assert np.allclose(b3.relative_position, expected_b3_pos_new, atol=1), f"B3 position incorrect après resize. Expected ~{expected_b3_pos_new}"
    assert np.allclose(b4.relative_position, expected_b4_pos_new, atol=1), f"B4 position incorrect après resize. Expected ~{expected_b4_pos_new}"
    assert np.allclose(b5.relative_position, expected_b5_pos_new, atol=1), f"B5 position incorrect après resize. Expected ~{expected_b5_pos_new}"

    print("Positions relatives après redimensionnement OK.")

    print("\n--- Tous les tests basiques du FlowLayout passés ---")