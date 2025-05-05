# src/engine/ui/widgets/label.py
import numpy as np
from typing import Optional, Tuple, Any, Dict, List

from ..ui_base import UIElement

class Label(UIElement):
    """
    Widget simple pour afficher du texte statique.
    """
    def __init__(self,
                 position: Tuple[int, int] = (0, 0),
                 size: Optional[Tuple[int, int]] = None, # La taille peut être déterminée par le texte
                 parent: Optional[UIElement] = None,
                 text: str = "Label",
                 font_id: Optional[Any] = None, # ID de la police à utiliser
                 font_size: int = 16,
                 color: Tuple[float, float, float, float] = (0.0, 0.0, 0.0, 1.0), # Noir par défaut
                 h_align: str = 'left', # 'left', 'center', 'right'
                 v_align: str = 'top', # 'top', 'center', 'bottom'
                 z_index: int = 1):
        """
        Initialise une nouvelle étiquette.

        Args:
            position (Tuple[int, int]): Position relative au parent.
            size (Optional[Tuple[int, int]]): Taille explicite. Si None, elle pourrait être calculée.
                                                Pour l'instant, une taille par défaut est utilisée si None.
            parent (Optional[UIElement]): Élément parent.
            text (str): Texte à afficher.
            font_id (Optional[Any]): ID de la police (dépendant du système de rendu/ressources).
            font_size (int): Taille de la police.
            color (Tuple[float, float, float, float]): Couleur RGBA (0-1) du texte.
            h_align (str): Alignement horizontal du texte dans le 'size' donné.
            v_align (str): Alignement vertical du texte dans le 'size' donné.
            z_index (int): Ordre de rendu.
        """
        # Si la taille n'est pas fournie, on utilise une taille par défaut pour l'instant.
        # Idéalement, on calculerait la taille nécessaire pour le texte.
        calculated_size = size if size is not None else (len(text) * font_size // 2, font_size) # Estimation très grossière
        super().__init__(position=position, size=calculated_size, parent=parent, z_index=z_index)

        self.text = text
        self.font_id = font_id
        self.font_size = font_size
        self.color = color
        self.h_align = h_align
        self.v_align = v_align

        # Recalculer la taille si le texte ou la police change (simplifié)
        # self.recalculate_size() # À implémenter si nécessaire

    # def recalculate_size(self):
    #     """Recalcule la taille de l'élément en fonction du texte et de la police."""
    #     # Cette fonction nécessiterait l'accès au système de rendu/font pour mesurer le texte.
    #     # Exemple : new_width, new_height = font_system.measure_text(self.text, self.font_id, self.font_size)
    #     # self.size = (new_width, new_height)
    #     pass

    def get_render_data(self) -> List[Dict[str, Any]]:
        """
        Génère les données de rendu pour le texte de l'étiquette.
        """
        render_list = []
        if self.visible and self.opacity > 0.0 and self.text:
            # La position pour le rendu de texte dépend souvent de l'alignement.
            # Le système de rendu devrait idéalement gérer l'alignement basé sur la position
            # et la taille fournies. Ici, on fournit le coin supérieur gauche.
            # Ou alors, on calcule la position ici en fonction de l'alignement.

            # Calcul simple de la position de base (coin sup gauche)
            # Le renderer devra interpréter l'alignement.
            render_pos = self.absolute_position.astype(float)

            # Appliquer l'opacité globale à la couleur alpha
            final_color = (
                self.color[0],
                self.color[1],
                self.color[2],
                self.color[3] * self.opacity
            )

            text_data = {
                'type': 'text',
                'text': self.text,
                'position': render_pos, # Position de référence (ex: coin sup gauche)
                'size': self.size.astype(float), # Taille de la boîte pour l'alignement
                'font_id': self.font_id,
                'font_size': self.font_size,
                'color': final_color,
                'h_align': self.h_align,
                'v_align': self.v_align,
                'z_index': self.z_index,
                # Pas d'échelle appliquée directement au texte ici, pourrait être géré par le renderer
            }
            render_list.append(text_data)

            # Les Labels n'ont généralement pas d'enfants directs à rendre eux-mêmes
            # (sauf si on compose des éléments complexes)

        return render_list

    def get_texture_id(self) -> Any:
        """Les labels n'ont pas de texture de fond par défaut."""
        return None

# --- Tests Basiques ---
if __name__ == "__main__":
    from ..ui_base import UIElement

    root = UIElement(size=(800, 600))

    label1 = Label(position=(10, 10), text="Hello World", parent=root, font_size=20, color=(1, 0, 0, 1), z_index=2)
    label2 = Label(position=(10, 40), text="Centered Text", size=(200, 50), parent=root, h_align='center', v_align='center', color=(0, 0, 1, 0.5), z_index=1)

    print("\n--- Test Initial State ---")
    print(f"Label 1 Text: '{label1.text}', Pos: {label1.absolute_position}, Size: {label1.size}, Z: {label1.z_index}")
    print(f"Label 2 Text: '{label2.text}', Pos: {label2.absolute_position}, Size: {label2.size}, Z: {label2.z_index}")

    print("\n--- Test Render Data ---")
    render_data = root.get_render_data()
    print(f"Nombre d'éléments à rendre: {len(render_data)}")
    # Devrait contenir les données des deux labels
    assert len(render_data) == 2, "Should have 2 render items (label1, label2)"

    # Vérifier l'ordre Z (label2 devrait être avant label1)
    z_indices = [item.get('z_index', 0) for item in render_data]
    print(f"Z-indices: {z_indices}")
    # Note: Le tri global n'est pas fait ici, chaque get_render_data trie ses propres éléments.
    # Le test ici vérifie juste que les z_index sont corrects dans les données générées.
    label1_data = next(item for item in render_data if item['text'] == "Hello World")
    label2_data = next(item for item in render_data if item['text'] == "Centered Text")

    assert label1_data['z_index'] == 2, "Label 1 z_index incorrect"
    assert label2_data['z_index'] == 1, "Label 2 z_index incorrect"

    # Vérifier les données spécifiques
    assert np.allclose(label1_data['color'], (1, 0, 0, 1 * label1.opacity)), "Label 1 color incorrect"
    assert label1_data['h_align'] == 'left', "Label 1 h_align incorrect"
    assert label2_data['h_align'] == 'center', "Label 2 h_align incorrect"
    assert label2_data['v_align'] == 'center', "Label 2 v_align incorrect"
    assert np.allclose(label2_data['color'], (0, 0, 1, 0.5 * label2.opacity)), "Label 2 color incorrect"

    print("Render data structure seems ok.")

    print("\n--- Tous les tests basiques du label passés ---")