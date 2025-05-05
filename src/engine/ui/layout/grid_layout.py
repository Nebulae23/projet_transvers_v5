# src/engine/ui/layout/grid_layout.py
import numpy as np
from typing import List, Tuple, Optional

from ..ui_base import LayoutManager, UIElement

class GridLayout(LayoutManager):
    """
    Dispose les éléments enfants dans une grille simple avec un nombre fixe de colonnes.
    """
    def __init__(self,
                 cols: int = 2,
                 padding: Tuple[int, int] = (5, 5), # Padding (horizontal, vertical) entre les cellules
                 margin: Tuple[int, int, int, int] = (0, 0, 0, 0)): # Marge (haut, droite, bas, gauche) à l'intérieur du parent
        """
        Initialise le GridLayout.

        Args:
            cols (int): Nombre de colonnes dans la grille.
            padding (Tuple[int, int]): Espacement (horizontal, vertical) entre les éléments.
            margin (Tuple[int, int, int, int]): Marge intérieure (haut, droite, bas, gauche).
        """
        if cols <= 0:
            raise ValueError("Le nombre de colonnes doit être positif.")
        self.cols = cols
        self.padding = np.array(padding, dtype=int)
        self.margin = np.array(margin, dtype=int) # [top, right, bottom, left]

    def apply_layout(self, element: UIElement):
        """
        Applique la disposition en grille aux enfants visibles de l'élément.
        """
        if not element.children:
            return

        visible_children = [child for child in element.children if child.visible]
        if not visible_children:
            return

        parent_width = element.size[0]
        parent_height = element.size[1] # Non utilisé directement pour le positionnement, mais pourrait l'être pour le calcul de hauteur

        # Zone disponible après application des marges
        available_width = parent_width - self.margin[3] - self.margin[1] # width - left - right
        # available_height = parent_height - self.margin[0] - self.margin[2] # height - top - bottom

        if available_width <= 0:
            # Pas d'espace pour disposer les éléments
            # On pourrait choisir de les cacher ou de les laisser à (0,0) relatif
            for child in visible_children:
                 child.relative_position = (0,0) # Ou une autre position par défaut
            return


        # Calculer la largeur de chaque colonne (suppose une largeur égale pour l'instant)
        # Prend en compte le padding entre les colonnes
        total_padding_width = self.padding[0] * (self.cols - 1)
        cell_width = (available_width - total_padding_width) / self.cols

        if cell_width <= 0:
             # Pas assez d'espace même pour une colonne sans padding
             cell_width = available_width # Utiliser tout l'espace pour la première colonne
             effective_cols = 1
        else:
             effective_cols = self.cols


        current_col = 0
        current_row = 0
        max_row_height = 0 # Hauteur max des éléments de la ligne actuelle

        start_x = self.margin[3] # Position X initiale (marge gauche)
        current_y = self.margin[0] # Position Y initiale (marge haute)

        for child in visible_children:
            # Calculer la position X de la cellule actuelle
            cell_x = start_x + current_col * (cell_width + self.padding[0])

            # Positionner l'enfant dans la cellule
            # Pour l'instant, on aligne en haut à gauche de la cellule.
            # On pourrait ajouter des options d'alignement dans la cellule.
            child.relative_position = (int(round(cell_x)), int(round(current_y)))

            # Mettre à jour la hauteur max de la ligne
            max_row_height = max(max_row_height, child.size[1])

            # Passer à la colonne suivante
            current_col += 1
            if current_col >= effective_cols:
                # Passer à la ligne suivante
                current_col = 0
                current_row += 1
                current_y += max_row_height + self.padding[1] # Ajouter hauteur max + padding vertical
                max_row_height = 0 # Réinitialiser pour la nouvelle ligne

        # Note: Cette implémentation simple ne redimensionne pas les enfants pour
        #       s'adapter à cell_width. Elle les positionne simplement.
        #       Une version plus avancée pourrait offrir des options d'étirement.

# --- Tests Basiques ---
if __name__ == "__main__":
    from ..ui_base import UIElement
    from ..widgets.button import Button # Utiliser un widget concret pour tester

    root = UIElement(size=(800, 600))
    container = UIElement(position=(50, 50), size=(400, 300), parent=root)

    # Appliquer un GridLayout au conteneur
    grid = GridLayout(cols=3, padding=(10, 10), margin=(5, 5, 5, 5))
    container.layout = grid

    # Ajouter des enfants au conteneur
    b1 = Button(text="B1", size=(80, 30), parent=container)
    b2 = Button(text="B2", size=(100, 40), parent=container) # Plus haut
    b3 = Button(text="B3", size=(70, 30), parent=container)
    b4 = Button(text="B4", size=(90, 30), parent=container)
    b5 = Button(text="B5", size=(80, 50), parent=container) # Encore plus haut

    print("\n--- Test Initial Layout ---")
    # Forcer l'application du layout (normalement fait lors de l'ajout/modif)
    container.apply_layout()

    # Vérifier les positions relatives des enfants
    # Marges: 5px tout autour. Padding: 10px H, 10px V. Cols: 3.
    # Largeur conteneur: 400. Largeur dispo: 400 - 5 - 5 = 390.
    # Padding total H: 10 * (3 - 1) = 20.
    # Largeur cellule: (390 - 20) / 3 = 370 / 3 = 123.33
    # Hauteur B2 = 40. Hauteur B5 = 50.

    # Ligne 1
    # B1: (gauche=5, haut=5) -> (5, 5)
    # B2: (5 + 123.33 + 10, 5) -> (138.33, 5)
    # B3: (138.33 + 123.33 + 10, 5) -> (271.66, 5)
    expected_b1_pos = (5, 5)
    expected_b2_pos = (5 + 123 + 10, 5) # 138, 5 (arrondi int)
    expected_b3_pos = (138 + 123 + 10, 5) # 271, 5

    # Ligne 2
    # Hauteur max Ligne 1 = 40 (B2). Padding V = 10.
    # Y Ligne 2 = 5 (marge haut) + 40 (hauteur max L1) + 10 (padding V) = 55
    # B4: (gauche=5, 55) -> (5, 55)
    # B5: (5 + 123 + 10, 55) -> (138, 55)
    expected_b4_pos = (5, 55)
    expected_b5_pos = (138, 55)

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

    print("\n--- Test Layout Update after Child Removal ---")
    container.remove_child(b3) # Supprimer le dernier de la première ligne
    # Le layout devrait se recalculer (ici on le force)
    container.apply_layout()

    # B4 devrait maintenant être à la fin de la première ligne
    # B5 devrait être au début de la deuxième ligne
    # Ligne 1
    # B1: (5, 5)
    # B2: (138, 5)
    # B4: (271, 5) <- Nouvelle position de B4
    expected_b4_pos_new = (271, 5)

    # Ligne 2
    # Hauteur max Ligne 1 = max(B1, B2, B4) = max(30, 40, 30) = 40.
    # Y Ligne 2 = 5 + 40 + 10 = 55
    # B5: (5, 55) <- Nouvelle position de B5
    expected_b5_pos_new = (5, 55)

    print(f"B4 New Pos: {b4.relative_position}")
    print(f"B5 New Pos: {b5.relative_position}")

    assert np.allclose(b4.relative_position, expected_b4_pos_new, atol=1), f"B4 position incorrect après remove. Expected ~{expected_b4_pos_new}"
    assert np.allclose(b5.relative_position, expected_b5_pos_new, atol=1), f"B5 position incorrect après remove. Expected ~{expected_b5_pos_new}"

    print("Positions relatives après suppression OK.")

    print("\n--- Tous les tests basiques du GridLayout passés ---")