# src/engine/ui/layout/stack_layout.py
import numpy as np
from typing import List, Tuple, Optional

from ..ui_base import LayoutManager, UIElement

class StackLayout(LayoutManager):
    """
    Dispose les éléments enfants les uns sur les autres (verticalement) ou côte à côte (horizontalement).
    Peut étirer les éléments pour remplir l'espace disponible.
    """
    def __init__(self,
                 orientation: str = 'vertical', # 'vertical' ou 'horizontal'
                 padding: int = 5, # Espacement entre les éléments
                 margin: Tuple[int, int, int, int] = (0, 0, 0, 0), # Marge (haut, droite, bas, gauche)
                 stretch: bool = False): # Indique si les éléments doivent être étirés
        """
        Initialise le StackLayout.

        Args:
            orientation (str): 'vertical' pour empiler, 'horizontal' pour aligner.
            padding (int): Espacement entre les éléments.
            margin (Tuple[int, int, int, int]): Marge intérieure (haut, droite, bas, gauche).
            stretch (bool): Si True, étire les éléments dans la direction secondaire.
                            (Largeur si vertical, Hauteur si horizontal).
        """
        if orientation not in ['vertical', 'horizontal']:
            raise ValueError("orientation must be 'vertical' or 'horizontal'.")
        self.orientation = orientation
        self.padding = padding
        self.margin = np.array(margin, dtype=int) # [top, right, bottom, left]
        self.stretch = stretch

    def apply_layout(self, element: UIElement):
        """
        Applique la disposition en pile aux enfants visibles de l'élément.
        """
        if not element.children:
            return

        visible_children = [child for child in element.children if child.visible]
        if not visible_children:
            return

        parent_width = element.size[0]
        parent_height = element.size[1]

        # Zone disponible après application des marges
        available_width = parent_width - self.margin[3] - self.margin[1] # width - left - right
        available_height = parent_height - self.margin[0] - self.margin[2] # height - top - bottom

        if available_width <= 0 or available_height <= 0:
            # Pas d'espace pour disposer les éléments
            for child in visible_children:
                 child.relative_position = (self.margin[3], self.margin[0]) # Positionner à la marge
            return

        current_pos = np.array([self.margin[3], self.margin[0]], dtype=float) # Position (x, y) de départ

        for i, child in enumerate(visible_children):
            child_size = child.size.copy() # Copie pour modification potentielle (stretch)

            # Appliquer l'étirement si nécessaire
            if self.stretch:
                if self.orientation == 'vertical':
                    # Étirer horizontalement pour remplir la largeur disponible
                    child_size[0] = available_width
                else: # Horizontal
                    # Étirer verticalement pour remplir la hauteur disponible
                    child_size[1] = available_height
                # Mettre à jour la taille de l'enfant (affecte son rendu et potentiellement ses propres enfants)
                # Note: Ceci modifie directement la taille de l'enfant.
                child.size = child_size.astype(int)


            # Positionner l'enfant
            # On aligne en haut à gauche pour l'instant. On pourrait ajouter des options d'alignement.
            child.relative_position = current_pos.round().astype(int)

            # Mettre à jour la position pour le prochain élément
            if self.orientation == 'vertical':
                # Déplacer vers le bas
                current_pos[1] += child_size[1] + self.padding
            else: # Horizontal
                # Déplacer vers la droite
                current_pos[0] += child_size[0] + self.padding

        # Note: Ce layout ne gère pas le dépassement de l'espace disponible.
        # Les éléments pourraient sortir des limites du parent.

# --- Tests Basiques ---
if __name__ == "__main__":
    from ..ui_base import UIElement
    from ..widgets.button import Button # Utiliser un widget concret

    # --- Test Vertical ---
    print("\n--- Test Vertical Stack ---")
    root_v = UIElement(size=(800, 600))
    container_v = UIElement(position=(50, 50), size=(200, 400), parent=root_v)

    stack_v = StackLayout(orientation='vertical', padding=10, margin=(5, 5, 5, 5))
    container_v.layout = stack_v

    bv1 = Button(text="BV1", size=(150, 30), parent=container_v)
    bv2 = Button(text="BV2", size=(180, 40), parent=container_v)
    bv3 = Button(text="BV3", size=(160, 50), parent=container_v)

    container_v.apply_layout()

    # Vérifier les positions relatives (vertical)
    # Marge: 5. Padding: 10.
    # BV1: Pos=(5, 5). current_y = 5 + 30 + 10 = 45.
    # BV2: Pos=(5, 45). current_y = 45 + 40 + 10 = 95.
    # BV3: Pos=(5, 95). current_y = 95 + 50 + 10 = 155.
    expected_bv1_pos = (5, 5)
    expected_bv2_pos = (5, 45)
    expected_bv3_pos = (5, 95)

    print(f"BV1 Pos: {bv1.relative_position}")
    print(f"BV2 Pos: {bv2.relative_position}")
    print(f"BV3 Pos: {bv3.relative_position}")

    assert np.allclose(bv1.relative_position, expected_bv1_pos), "BV1 position incorrect"
    assert np.allclose(bv2.relative_position, expected_bv2_pos), "BV2 position incorrect"
    assert np.allclose(bv3.relative_position, expected_bv3_pos), "BV3 position incorrect"
    print("Positions verticales OK.")

    # --- Test Vertical Stretch ---
    print("\n--- Test Vertical Stack with Stretch ---")
    container_v_stretch = UIElement(position=(300, 50), size=(200, 400), parent=root_v)
    stack_v_stretch = StackLayout(orientation='vertical', padding=10, margin=(5, 5, 5, 5), stretch=True)
    container_v_stretch.layout = stack_v_stretch

    bv_s1 = Button(text="BVS1", size=(150, 30), parent=container_v_stretch)
    bv_s2 = Button(text="BVS2", size=(180, 40), parent=container_v_stretch)

    container_v_stretch.apply_layout()

    # Vérifier les positions et les tailles (stretch horizontal)
    # Largeur dispo: 200 - 5 - 5 = 190.
    # BVS1: Pos=(5, 5). Size=(190, 30). current_y = 5 + 30 + 10 = 45.
    # BVS2: Pos=(5, 45). Size=(190, 40). current_y = 45 + 40 + 10 = 95.
    expected_bv_s1_pos = (5, 5)
    expected_bv_s2_pos = (5, 45)
    expected_stretched_width = 190

    print(f"BVS1 Pos: {bv_s1.relative_position}, Size: {bv_s1.size}")
    print(f"BVS2 Pos: {bv_s2.relative_position}, Size: {bv_s2.size}")

    assert np.allclose(bv_s1.relative_position, expected_bv_s1_pos), "BVS1 position incorrect"
    assert bv_s1.size[0] == expected_stretched_width, f"BVS1 width incorrect. Expected {expected_stretched_width}, got {bv_s1.size[0]}"
    assert np.allclose(bv_s2.relative_position, expected_bv_s2_pos), "BVS2 position incorrect"
    assert bv_s2.size[0] == expected_stretched_width, f"BVS2 width incorrect. Expected {expected_stretched_width}, got {bv_s2.size[0]}"
    print("Positions et tailles verticales stretch OK.")


    # --- Test Horizontal ---
    print("\n--- Test Horizontal Stack ---")
    root_h = UIElement(size=(800, 600))
    container_h = UIElement(position=(50, 50), size=(500, 200), parent=root_h)

    stack_h = StackLayout(orientation='horizontal', padding=15, margin=(10, 10, 10, 10))
    container_h.layout = stack_h

    bh1 = Button(text="BH1", size=(100, 50), parent=container_h)
    bh2 = Button(text="BH2", size=(120, 60), parent=container_h)
    bh3 = Button(text="BH3", size=(80, 70), parent=container_h)

    container_h.apply_layout()

    # Vérifier les positions relatives (horizontal)
    # Marge: 10. Padding: 15.
    # BH1: Pos=(10, 10). current_x = 10 + 100 + 15 = 125.
    # BH2: Pos=(125, 10). current_x = 125 + 120 + 15 = 260.
    # BH3: Pos=(260, 10). current_x = 260 + 80 + 15 = 355.
    expected_bh1_pos = (10, 10)
    expected_bh2_pos = (125, 10)
    expected_bh3_pos = (260, 10)

    print(f"BH1 Pos: {bh1.relative_position}")
    print(f"BH2 Pos: {bh2.relative_position}")
    print(f"BH3 Pos: {bh3.relative_position}")

    assert np.allclose(bh1.relative_position, expected_bh1_pos), "BH1 position incorrect"
    assert np.allclose(bh2.relative_position, expected_bh2_pos), "BH2 position incorrect"
    assert np.allclose(bh3.relative_position, expected_bh3_pos), "BH3 position incorrect"
    print("Positions horizontales OK.")

    # --- Test Horizontal Stretch ---
    print("\n--- Test Horizontal Stack with Stretch ---")
    container_h_stretch = UIElement(position=(50, 300), size=(500, 200), parent=root_h)
    stack_h_stretch = StackLayout(orientation='horizontal', padding=15, margin=(10, 10, 10, 10), stretch=True)
    container_h_stretch.layout = stack_h_stretch

    bh_s1 = Button(text="BHS1", size=(100, 50), parent=container_h_stretch)
    bh_s2 = Button(text="BHS2", size=(120, 60), parent=container_h_stretch)

    container_h_stretch.apply_layout()

    # Vérifier les positions et les tailles (stretch vertical)
    # Hauteur dispo: 200 - 10 - 10 = 180.
    # BHS1: Pos=(10, 10). Size=(100, 180). current_x = 10 + 100 + 15 = 125.
    # BHS2: Pos=(125, 10). Size=(120, 180). current_x = 125 + 120 + 15 = 260.
    expected_bh_s1_pos = (10, 10)
    expected_bh_s2_pos = (125, 10)
    expected_stretched_height = 180

    print(f"BHS1 Pos: {bh_s1.relative_position}, Size: {bh_s1.size}")
    print(f"BHS2 Pos: {bh_s2.relative_position}, Size: {bh_s2.size}")

    assert np.allclose(bh_s1.relative_position, expected_bh_s1_pos), "BHS1 position incorrect"
    assert bh_s1.size[1] == expected_stretched_height, f"BHS1 height incorrect. Expected {expected_stretched_height}, got {bh_s1.size[1]}"
    assert np.allclose(bh_s2.relative_position, expected_bh_s2_pos), "BHS2 position incorrect"
    assert bh_s2.size[1] == expected_stretched_height, f"BHS2 height incorrect. Expected {expected_stretched_height}, got {bh_s2.size[1]}"
    print("Positions et tailles horizontales stretch OK.")


    print("\n--- Tous les tests basiques du StackLayout passés ---")