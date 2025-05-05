# src/engine/ui/layout/anchor_layout.py
import numpy as np
from typing import List, Tuple, Optional, Dict, Any

from ..ui_base import LayoutManager, UIElement

class AnchorLayout(LayoutManager):
    """
    Positionne les éléments enfants en fonction d'ancres définies par rapport aux bords
    ou au centre du conteneur parent.
    Les enfants doivent avoir des propriétés d'ancrage définies (par exemple, dans un dict `anchor_props`).
    """
    def __init__(self,
                 margin: Tuple[int, int, int, int] = (0, 0, 0, 0)): # Marge (haut, droite, bas, gauche)
        """
        Initialise l'AnchorLayout.

        Args:
            margin (Tuple[int, int, int, int]): Marge intérieure (haut, droite, bas, gauche).
        """
        self.margin = np.array(margin, dtype=int) # [top, right, bottom, left]

    def apply_layout(self, element: UIElement):
        """
        Applique la disposition par ancres aux enfants visibles de l'élément.
        Chaque enfant doit avoir un attribut `anchor_props` (dict) spécifiant ses ancres.

        Exemple d'anchor_props pour un enfant:
        {
            'left': 10,           # Ancré à 10px du bord gauche du parent
            'right': 10,          # Ancré à 10px du bord droit du parent (étire l'élément)
            'top': 20,            # Ancré à 20px du bord haut
            'bottom': 20,         # Ancré à 20px du bord bas (étire l'élément)
            'center_h': True,     # Centré horizontalement (ignore left/right si True)
            'center_v': True,     # Centré verticalement (ignore top/bottom si True)
            'offset_x': 5,        # Décalage supplémentaire après calcul de l'ancre X
            'offset_y': -5        # Décalage supplémentaire après calcul de l'ancre Y
        }
        """
        if not element.children:
            return

        visible_children = [child for child in element.children if child.visible]
        if not visible_children:
            return

        parent_width = element.size[0]
        parent_height = element.size[1]

        # Zone disponible après application des marges
        available_width = parent_width - self.margin[3] - self.margin[1]
        available_height = parent_height - self.margin[0] - self.margin[2]
        origin_x = self.margin[3] # Coin supérieur gauche de la zone disponible
        origin_y = self.margin[0]

        if available_width <= 0 or available_height <= 0:
            # Pas d'espace, positionner à l'origine
            for child in visible_children:
                 child.relative_position = (origin_x, origin_y)
            return

        for child in visible_children:
            props = getattr(child, 'anchor_props', {}) # Récupérer les props d'ancrage
            if not props:
                # Si pas de props, on pourrait le laisser tel quel ou le mettre à (0,0) relatif
                # Ici, on le place à l'origine des marges pour éviter qu'il soit à (0,0) absolu
                child.relative_position = (origin_x, origin_y)
                continue

            child_pos = child.relative_position.astype(float) # Position actuelle comme base
            child_size = child.size.astype(float) # Taille actuelle comme base

            offset_x = props.get('offset_x', 0)
            offset_y = props.get('offset_y', 0)

            # --- Calcul Horizontal (X et Largeur) ---
            anchor_left = props.get('left')
            anchor_right = props.get('right')
            center_h = props.get('center_h', False)

            if center_h:
                # Centrer horizontalement
                child_pos[0] = origin_x + (available_width - child_size[0]) / 2.0
                # Ignorer left/right si centré
            elif anchor_left is not None and anchor_right is not None:
                # Ancré des deux côtés -> étirer
                child_pos[0] = origin_x + anchor_left
                new_width = available_width - anchor_left - anchor_right
                child_size[0] = max(0, new_width) # Assurer une largeur non négative
            elif anchor_left is not None:
                # Ancré à gauche seulement
                child_pos[0] = origin_x + anchor_left
            elif anchor_right is not None:
                # Ancré à droite seulement
                child_pos[0] = origin_x + available_width - anchor_right - child_size[0]
            # Si ni left, ni right, ni center_h ne sont définis, la position X n'est pas modifiée par l'ancre

            # Appliquer le décalage X
            child_pos[0] += offset_x

            # --- Calcul Vertical (Y et Hauteur) ---
            anchor_top = props.get('top')
            anchor_bottom = props.get('bottom')
            center_v = props.get('center_v', False)

            if center_v:
                # Centrer verticalement
                child_pos[1] = origin_y + (available_height - child_size[1]) / 2.0
                # Ignorer top/bottom si centré
            elif anchor_top is not None and anchor_bottom is not None:
                # Ancré des deux côtés -> étirer
                child_pos[1] = origin_y + anchor_top
                new_height = available_height - anchor_top - anchor_bottom
                child_size[1] = max(0, new_height) # Assurer une hauteur non négative
            elif anchor_top is not None:
                # Ancré en haut seulement
                child_pos[1] = origin_y + anchor_top
            elif anchor_bottom is not None:
                # Ancré en bas seulement
                child_pos[1] = origin_y + available_height - anchor_bottom - child_size[1]
            # Si ni top, ni bottom, ni center_v ne sont définis, la position Y n'est pas modifiée par l'ancre

            # Appliquer le décalage Y
            child_pos[1] += offset_y

            # Mettre à jour la position et la taille de l'enfant
            child.relative_position = child_pos.round().astype(int)
            # Mettre à jour la taille seulement si elle a été modifiée par l'étirement
            if (anchor_left is not None and anchor_right is not None) or \
               (anchor_top is not None and anchor_bottom is not None):
                child.size = child_size.round().astype(int)


# --- Tests Basiques ---
if __name__ == "__main__":
    from ..ui_base import UIElement
    from ..widgets.button import Button # Utiliser un widget concret

    root = UIElement(size=(800, 600))
    container = UIElement(position=(100, 100), size=(400, 300), parent=root)

    # Appliquer un AnchorLayout au conteneur
    anchor_layout = AnchorLayout(margin=(10, 20, 10, 20)) # Marges: T=10, R=20, B=10, L=20
    container.layout = anchor_layout

    # Créer des enfants avec des propriétés d'ancrage
    # 1. Ancré en haut à gauche avec offset
    child1 = Button(text="TL", size=(80, 30), parent=container)
    child1.anchor_props = {'top': 5, 'left': 5, 'offset_x': 2, 'offset_y': 3}

    # 2. Ancré en haut à droite
    child2 = Button(text="TR", size=(90, 40), parent=container)
    child2.anchor_props = {'top': 10, 'right': 15}

    # 3. Ancré en bas à gauche
    child3 = Button(text="BL", size=(100, 35), parent=container)
    child3.anchor_props = {'bottom': 5, 'left': 10}

    # 4. Ancré en bas à droite avec offset
    child4 = Button(text="BR", size=(70, 30), parent=container)
    child4.anchor_props = {'bottom': 20, 'right': 5, 'offset_x': -3, 'offset_y': -4}

    # 5. Centré horizontalement, ancré en haut
    child5 = Button(text="CH", size=(120, 40), parent=container)
    child5.anchor_props = {'center_h': True, 'top': 50}

    # 6. Centré verticalement, ancré à droite
    child6 = Button(text="CV", size=(60, 80), parent=container)
    child6.anchor_props = {'center_v': True, 'right': 30}

    # 7. Centré complètement
    child7 = Button(text="C", size=(50, 50), parent=container)
    child7.anchor_props = {'center_h': True, 'center_v': True}

    # 8. Étiré horizontalement, ancré en haut/bas
    child8 = Button(text="Stretch H", size=(10, 40), parent=container) # Largeur initiale ignorée
    child8.anchor_props = {'left': 25, 'right': 25, 'top': 100, 'bottom': 160} # Devrait avoir hauteur 300-10-10 - 100 - 160 = 20?

    # 9. Étiré verticalement, ancré gauche/droite
    child9 = Button(text="Stretch V", size=(50, 10), parent=container) # Hauteur initiale ignorée
    child9.anchor_props = {'top': 150, 'bottom': 30, 'left': 150, 'right': 150} # Devrait avoir largeur 400-20-20 - 150 - 150 = 60?

    # 10. Étiré complètement avec marges d'ancrage
    child10 = Button(text="Stretch All", size=(10, 10), parent=container)
    child10.anchor_props = {'top': 5, 'bottom': 5, 'left': 5, 'right': 5}


    print("\n--- Test Layout Application ---")
    container.apply_layout()

    # Vérifier les positions et tailles
    # Parent: 400x300. Marges: T=10, R=20, B=10, L=20.
    # Zone dispo: W=400-20-20=360, H=300-10-10=280. Origin=(20, 10).

    # Child1: TL offset
    # X = origin_x + left + offset_x = 20 + 5 + 2 = 27
    # Y = origin_y + top + offset_y = 10 + 5 + 3 = 18
    expected_c1_pos = (27, 18)
    assert np.allclose(child1.relative_position, expected_c1_pos), f"Child1 pos incorrect. Expected {expected_c1_pos}, got {child1.relative_position}"

    # Child2: TR
    # X = origin_x + avail_w - right - width = 20 + 360 - 15 - 90 = 275
    # Y = origin_y + top = 10 + 10 = 20
    expected_c2_pos = (275, 20)
    assert np.allclose(child2.relative_position, expected_c2_pos), f"Child2 pos incorrect. Expected {expected_c2_pos}, got {child2.relative_position}"

    # Child3: BL
    # X = origin_x + left = 20 + 10 = 30
    # Y = origin_y + avail_h - bottom - height = 10 + 280 - 5 - 35 = 250
    expected_c3_pos = (30, 250)
    assert np.allclose(child3.relative_position, expected_c3_pos), f"Child3 pos incorrect. Expected {expected_c3_pos}, got {child3.relative_position}"

    # Child4: BR offset
    # X = origin_x + avail_w - right - width + offset_x = 20 + 360 - 5 - 70 - 3 = 302
    # Y = origin_y + avail_h - bottom - height + offset_y = 10 + 280 - 20 - 30 - 4 = 236
    expected_c4_pos = (302, 236)
    assert np.allclose(child4.relative_position, expected_c4_pos), f"Child4 pos incorrect. Expected {expected_c4_pos}, got {child4.relative_position}"

    # Child5: CH, top
    # X = origin_x + (avail_w - width) / 2 = 20 + (360 - 120) / 2 = 20 + 120 = 140
    # Y = origin_y + top = 10 + 50 = 60
    expected_c5_pos = (140, 60)
    assert np.allclose(child5.relative_position, expected_c5_pos), f"Child5 pos incorrect. Expected {expected_c5_pos}, got {child5.relative_position}"

    # Child6: CV, right
    # X = origin_x + avail_w - right - width = 20 + 360 - 30 - 60 = 290
    # Y = origin_y + (avail_h - height) / 2 = 10 + (280 - 80) / 2 = 10 + 100 = 110
    expected_c6_pos = (290, 110)
    assert np.allclose(child6.relative_position, expected_c6_pos), f"Child6 pos incorrect. Expected {expected_c6_pos}, got {child6.relative_position}"

    # Child7: Center H, Center V
    # X = origin_x + (avail_w - width) / 2 = 20 + (360 - 50) / 2 = 20 + 155 = 175
    # Y = origin_y + (avail_h - height) / 2 = 10 + (280 - 50) / 2 = 10 + 115 = 125
    expected_c7_pos = (175, 125)
    assert np.allclose(child7.relative_position, expected_c7_pos), f"Child7 pos incorrect. Expected {expected_c7_pos}, got {child7.relative_position}"

    # Child8: Stretch H
    # X = origin_x + left = 20 + 25 = 45
    # Width = avail_w - left - right = 360 - 25 - 25 = 310
    # Y = origin_y + top = 10 + 100 = 110
    # Height = avail_h - top - bottom = 280 - 100 - 160 = 20
    expected_c8_pos = (45, 110)
    expected_c8_size = (310, 20)
    assert np.allclose(child8.relative_position, expected_c8_pos), f"Child8 pos incorrect. Expected {expected_c8_pos}, got {child8.relative_position}"
    assert np.allclose(child8.size, expected_c8_size), f"Child8 size incorrect. Expected {expected_c8_size}, got {child8.size}"

    # Child9: Stretch V
    # X = origin_x + left = 20 + 150 = 170
    # Width = avail_w - left - right = 360 - 150 - 150 = 60
    # Y = origin_y + top = 10 + 150 = 160
    # Height = avail_h - top - bottom = 280 - 150 - 30 = 100
    expected_c9_pos = (170, 160)
    expected_c9_size = (60, 100)
    assert np.allclose(child9.relative_position, expected_c9_pos), f"Child9 pos incorrect. Expected {expected_c9_pos}, got {child9.relative_position}"
    assert np.allclose(child9.size, expected_c9_size), f"Child9 size incorrect. Expected {expected_c9_size}, got {child9.size}"

    # Child10: Stretch All
    # X = origin_x + left = 20 + 5 = 25
    # Width = avail_w - left - right = 360 - 5 - 5 = 350
    # Y = origin_y + top = 10 + 5 = 15
    # Height = avail_h - top - bottom = 280 - 5 - 5 = 270
    expected_c10_pos = (25, 15)
    expected_c10_size = (350, 270)
    assert np.allclose(child10.relative_position, expected_c10_pos), f"Child10 pos incorrect. Expected {expected_c10_pos}, got {child10.relative_position}"
    assert np.allclose(child10.size, expected_c10_size), f"Child10 size incorrect. Expected {expected_c10_size}, got {child10.size}"


    print("Positions et tailles avec ancres OK.")

    print("\n--- Tous les tests basiques de l'AnchorLayout passés ---")