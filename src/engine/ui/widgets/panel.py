# src/engine/ui/widgets/panel.py
import numpy as np
from typing import Optional, Tuple, Any, Dict, List

from ..ui_base import UIElement, LayoutManager

class Panel(UIElement):
    """
    Widget Panneau simple servant de conteneur pour d'autres éléments UI.
    Peut avoir une couleur de fond ou une texture.
    """
    def __init__(self,
                 position: Tuple[int, int] = (0, 0),
                 size: Tuple[int, int] = (100, 100),
                 parent: Optional[UIElement] = None,
                 layout: Optional[LayoutManager] = None,
                 background_color: Optional[Tuple[float, float, float, float]] = (0.8, 0.8, 0.8, 1.0), # Gris clair par défaut
                 texture_id: Optional[Any] = None, # Pour une image de fond
                 z_index: int = 0):
        """
        Initialise un nouveau panneau.

        Args:
            position (Tuple[int, int]): Position relative au parent.
            size (Tuple[int, int]): Taille du panneau.
            parent (Optional[UIElement]): Élément parent.
            layout (Optional[LayoutManager]): Gestionnaire de layout pour les enfants.
            background_color (Optional[Tuple[float, float, float, float]]): Couleur RGBA (0-1) du fond.
            texture_id (Optional[Any]): ID de la texture de fond (prioritaire sur la couleur).
            z_index (int): Ordre de rendu.
        """
        super().__init__(position=position, size=size, parent=parent, layout=layout, z_index=z_index)
        self.background_color = background_color
        self._texture_id = texture_id # Stockage interne de l'ID de texture

    def get_texture_id(self) -> Any:
        """
        Retourne l'ID de texture pour le fond du panneau.
        """
        return self._texture_id

    def get_render_data(self) -> List[Dict[str, Any]]:
        """
        Génère les données de rendu pour le panneau (fond) et ses enfants.
        """
        render_list = []
        if self.visible and self.opacity > 0.0:
            # 1. Données pour le fond du panneau lui-même
            effective_size = self._size.astype(float) * self.scale
            center_position = self.absolute_position.astype(float) + self._size.astype(float) / 2.0

            panel_bg_data = {
                'position': center_position,
                'size': effective_size,
                'texture_id': self.get_texture_id(),
                # Utiliser la couleur de fond si pas de texture, sinon couleur neutre (blanc)
                'color': self.background_color if self._texture_id is None else (1.0, 1.0, 1.0, self.opacity),
                 # Appliquer l'opacité globale à la couleur alpha si pas de texture
                'color': (
                    self.background_color[0],
                    self.background_color[1],
                    self.background_color[2],
                    self.background_color[3] * self.opacity
                 ) if self.background_color and self._texture_id is None else (1.0, 1.0, 1.0, self.opacity),
                'rotation': 0.0,
                'z_index': self.z_index,
                'scale': self.scale.copy(),
                # Indiquer que c'est un fond de panneau si nécessaire pour le shader
                'type': 'panel_background'
            }
            # Si pas de texture et pas de couleur, on ne rend pas le fond
            if self._texture_id is not None or self.background_color is not None:
                 render_list.append(panel_bg_data)


            # 2. Collecter les données des enfants visibles
            for child in self.children:
                render_list.extend(child.get_render_data())

            # 3. Trier la liste complète par z_index
            # (Comme mentionné dans UIElement, idéalement fait globalement)
            render_list.sort(key=lambda data: data.get('z_index', 0))

        return render_list

# --- Tests Basiques ---
if __name__ == "__main__":
    from ..ui_base import UIElement # Nécessaire pour créer un parent racine
    from .button import Button # Pour tester l'ajout d'enfants

    root = UIElement(size=(800, 600))

    panel1 = Panel(position=(20, 30), size=(300, 200), parent=root, background_color=(0.2, 0.2, 0.5, 0.8), z_index=5)
    panel2 = Panel(position=(50, 50), size=(150, 100), parent=panel1, background_color=(0.9, 0.9, 0.9, 1.0), z_index=10) # Dans panel1
    button_in_panel2 = Button(position=(10, 10), size=(80, 30), text="Inside", parent=panel2, z_index=15)

    print("\n--- Test Initial State ---")
    print(f"Panel 1 Pos: {panel1.absolute_position}, Size: {panel1.size}, Z: {panel1.z_index}")
    print(f"Panel 2 Pos: {panel2.absolute_position}, Size: {panel2.size}, Z: {panel2.z_index}")
    print(f"Button Pos: {button_in_panel2.absolute_position}, Size: {button_in_panel2.size}, Z: {button_in_panel2.z_index}")

    # Vérifier les positions absolues
    expected_panel1_abs = np.array([20, 30])
    expected_panel2_abs = expected_panel1_abs + np.array([50, 50]) # (70, 80)
    expected_button_abs = expected_panel2_abs + np.array([10, 10]) # (80, 90)

    assert np.array_equal(panel1.absolute_position, expected_panel1_abs), "Panel 1 Absolute Position incorrect"
    assert np.array_equal(panel2.absolute_position, expected_panel2_abs), "Panel 2 Absolute Position incorrect"
    assert np.array_equal(button_in_panel2.absolute_position, expected_button_abs), "Button Absolute Position incorrect"
    print("Positions absolues OK.")

    print("\n--- Test Render Data ---")
    render_data = root.get_render_data()
    print(f"Nombre d'éléments à rendre: {len(render_data)}")
    # Devrait contenir: fond panel1, fond panel2, fond bouton, texte bouton
    # (UIElement racine n'a pas de rendu par défaut)
    assert len(render_data) == 4, "Should have 4 render items (panel1 bg, panel2 bg, button bg, button text)"

    # Vérifier l'ordre Z
    z_indices = [item.get('z_index', 0) for item in render_data]
    print(f"Z-indices: {z_indices}")
    assert all(z_indices[i] <= z_indices[i+1] for i in range(len(z_indices)-1)), "Render items should be sorted by z_index"

    # Vérifier les données spécifiques (ex: couleur panel1)
    panel1_data = next(item for item in render_data if item.get('type') == 'panel_background' and np.array_equal(item['size'], panel1.size.astype(float)))
    assert panel1_data is not None, "Panel 1 background data not found"
    assert np.allclose(panel1_data['color'], (0.2, 0.2, 0.5, 0.8 * panel1.opacity)), f"Panel 1 color incorrect: {panel1_data['color']}"
    assert panel1_data['z_index'] == 5, "Panel 1 z_index incorrect"

    print("Render data structure and z-ordering seem ok.")

    print("\n--- Tous les tests basiques du panneau passés ---")