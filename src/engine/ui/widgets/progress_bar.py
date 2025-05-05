# src/engine/ui/widgets/progress_bar.py
import numpy as np
from typing import Optional, Tuple, Any, Dict, List

from ..ui_base import UIElement

class ProgressBar(UIElement):
    """
    Widget pour afficher une barre de progression.
    """
    def __init__(self,
                 position: Tuple[int, int] = (0, 0),
                 size: Tuple[int, int] = (200, 20),
                 parent: Optional[UIElement] = None,
                 value: float = 0.0,
                 max_value: float = 100.0,
                 bar_color: Tuple[float, float, float, float] = (0.2, 0.8, 0.2, 1.0), # Vert par défaut
                 background_color: Optional[Tuple[float, float, float, float]] = (0.5, 0.5, 0.5, 1.0), # Gris par défaut
                 border_color: Optional[Tuple[float, float, float, float]] = None, # Pas de bordure par défaut
                 border_width: int = 1,
                 z_index: int = 0):
        """
        Initialise une nouvelle barre de progression.

        Args:
            position (Tuple[int, int]): Position relative au parent.
            size (Tuple[int, int]): Taille totale de la barre.
            parent (Optional[UIElement]): Élément parent.
            value (float): Valeur actuelle de la progression.
            max_value (float): Valeur maximale de la progression.
            bar_color (Tuple[float, float, float, float]): Couleur RGBA (0-1) de la barre de progression.
            background_color (Optional[Tuple[float, float, float, float]]): Couleur RGBA (0-1) du fond. Si None, pas de fond.
            border_color (Optional[Tuple[float, float, float, float]]): Couleur RGBA (0-1) de la bordure. Si None, pas de bordure.
            border_width (int): Largeur de la bordure.
            z_index (int): Ordre de rendu.
        """
        super().__init__(position=position, size=size, parent=parent, z_index=z_index)

        if max_value <= 0:
            raise ValueError("max_value doit être positif.")
        self._max_value = max_value
        self._value = max(0.0, min(value, max_value)) # Assurer que la valeur est dans [0, max_value]

        self.bar_color = bar_color
        self.background_color = background_color
        self.border_color = border_color
        self.border_width = border_width

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_value: float):
        self._value = max(0.0, min(float(new_value), self._max_value))

    @property
    def max_value(self) -> float:
        return self._max_value

    @max_value.setter
    def max_value(self, new_max_value: float):
        if new_max_value <= 0:
            raise ValueError("max_value doit être positif.")
        self._max_value = float(new_max_value)
        # Réajuster la valeur actuelle si elle dépasse le nouveau max
        self._value = min(self._value, self._max_value)

    @property
    def progress_ratio(self) -> float:
        """Retourne la progression sous forme de ratio (0.0 à 1.0)."""
        return self._value / self._max_value if self._max_value > 0 else 0.0

    def get_render_data(self) -> List[Dict[str, Any]]:
        """
        Génère les données de rendu pour le fond, la barre et la bordure.
        """
        render_list = []
        if not self.visible or self.opacity <= 0.0:
            return render_list

        base_pos = self.absolute_position.astype(float)
        base_size = self.size.astype(float)
        center_pos = base_pos + base_size / 2.0
        effective_opacity = self.opacity # Pourrait être modulé par les couleurs

        # 1. Bordure (si définie) - Dessinée en premier (en dessous)
        # Note: Le rendu de bordure simple peut être fait avec 4 rectangles fins,
        # ou idéalement géré par un shader ou une primitive de dessin de rectangle creux.
        # Ici, on simule avec un rectangle de fond légèrement plus grand.
        if self.border_color and self.border_width > 0:
            border_size = base_size + 2 * self.border_width
            border_center_pos = base_pos - self.border_width + border_size / 2.0
            border_color_final = (
                self.border_color[0], self.border_color[1], self.border_color[2],
                self.border_color[3] * effective_opacity
            )
            border_data = {
                'type': 'rect_fill', # Type générique pour un rectangle plein
                'position': border_center_pos,
                'size': border_size * self.scale, # Appliquer l'échelle
                'color': border_color_final,
                'texture_id': None,
                'rotation': 0.0,
                'z_index': self.z_index,
                'scale': np.array([1.0, 1.0]) # L'échelle est déjà appliquée à la taille
            }
            render_list.append(border_data)

        # 2. Fond (si défini) - Dessiné au-dessus de la bordure
        if self.background_color:
            bg_color_final = (
                self.background_color[0], self.background_color[1], self.background_color[2],
                self.background_color[3] * effective_opacity
            )
            bg_data = {
                'type': 'rect_fill',
                'position': center_pos,
                'size': base_size * self.scale, # Appliquer l'échelle
                'color': bg_color_final,
                'texture_id': None,
                'rotation': 0.0,
                'z_index': self.z_index + 1, # Légèrement au-dessus de la bordure
                'scale': np.array([1.0, 1.0])
            }
            render_list.append(bg_data)

        # 3. Barre de progression - Dessinée au-dessus du fond
        if self.progress_ratio > 0:
            bar_width = base_size[0] * self.progress_ratio
            # Ajuster la position et la taille pour la barre partielle
            bar_size = np.array([bar_width, base_size[1]])
            # Position du centre de la barre partielle
            bar_center_pos = base_pos + np.array([bar_width / 2.0, base_size[1] / 2.0])

            bar_color_final = (
                self.bar_color[0], self.bar_color[1], self.bar_color[2],
                self.bar_color[3] * effective_opacity
            )
            bar_data = {
                'type': 'rect_fill',
                'position': bar_center_pos,
                'size': bar_size * self.scale, # Appliquer l'échelle
                'color': bar_color_final,
                'texture_id': None,
                'rotation': 0.0,
                'z_index': self.z_index + 2, # Au-dessus du fond
                'scale': np.array([1.0, 1.0])
            }
            render_list.append(bar_data)

        # Trier par z_index (important car on a défini des z_index relatifs)
        render_list.sort(key=lambda data: data.get('z_index', 0))

        # Ajouter les données des enfants (si une barre de progression peut en avoir)
        for child in self.children:
             render_list.extend(child.get_render_data())
        # Re-trier si des enfants ont été ajoutés
        render_list.sort(key=lambda data: data.get('z_index', 0))


        return render_list

    def get_texture_id(self) -> Any:
        """Les barres de progression n'utilisent pas de texture unique par défaut."""
        return None

# --- Tests Basiques ---
if __name__ == "__main__":
    from ..ui_base import UIElement

    root = UIElement(size=(800, 600))

    progress1 = ProgressBar(position=(50, 50), size=(300, 25), parent=root, value=75, max_value=100, z_index=5)
    progress2 = ProgressBar(position=(50, 100), size=(300, 15), parent=root, value=20, max_value=50,
                            bar_color=(0.8, 0.8, 0.2, 1.0), background_color=(0.3, 0.3, 0.3, 1.0),
                            border_color=(1.0, 1.0, 1.0, 1.0), border_width=2, z_index=10)

    print("\n--- Test Initial State ---")
    print(f"Progress 1 Value: {progress1.value}/{progress1.max_value} (Ratio: {progress1.progress_ratio:.2f}), Z: {progress1.z_index}")
    print(f"Progress 2 Value: {progress2.value}/{progress2.max_value} (Ratio: {progress2.progress_ratio:.2f}), Z: {progress2.z_index}")
    assert abs(progress1.progress_ratio - 0.75) < 1e-6
    assert abs(progress2.progress_ratio - 0.40) < 1e-6 # 20 / 50 = 0.4

    print("\n--- Test Value Change ---")
    progress1.value = 110 # Devrait être capé à 100
    assert progress1.value == 100, f"Value should be capped at max_value. Got {progress1.value}"
    progress1.value = -10 # Devrait être capé à 0
    assert progress1.value == 0, f"Value should be capped at 0. Got {progress1.value}"
    progress1.value = 50
    assert progress1.value == 50
    assert abs(progress1.progress_ratio - 0.5) < 1e-6
    print(f"Progress 1 New Value: {progress1.value}/{progress1.max_value} (Ratio: {progress1.progress_ratio:.2f})")

    print("\n--- Test Max Value Change ---")
    progress2.max_value = 200
    assert progress2.max_value == 200
    assert progress2.value == 20 # La valeur ne change pas si elle est inférieure au nouveau max
    assert abs(progress2.progress_ratio - 0.10) < 1e-6 # 20 / 200 = 0.1
    print(f"Progress 2 New Max: {progress2.max_value}, Value: {progress2.value}, Ratio: {progress2.progress_ratio:.2f}")

    progress2.value = 150
    progress2.max_value = 100 # La valeur devrait être capée au nouveau max
    assert progress2.max_value == 100
    assert progress2.value == 100
    assert abs(progress2.progress_ratio - 1.0) < 1e-6
    print(f"Progress 2 Capped Value: {progress2.value}/{progress2.max_value}, Ratio: {progress2.progress_ratio:.2f}")


    print("\n--- Test Render Data ---")
    render_data = root.get_render_data()
    print(f"Nombre total d'éléments à rendre: {len(render_data)}")

    # Compter les éléments pour progress2 (bordure + fond + barre)
    progress2_items = [item for item in render_data if item['z_index'] >= 10 and item['z_index'] < 13]
    print(f"Éléments pour Progress 2: {len(progress2_items)}")
    assert len(progress2_items) == 3, "Progress 2 should have 3 render items (border, bg, bar)"

    # Vérifier les z_index relatifs de progress2
    z_indices_p2 = sorted([item['z_index'] for item in progress2_items])
    assert z_indices_p2 == [10, 11, 12], f"Incorrect z-indices for Progress 2 items: {z_indices_p2}"

    # Vérifier la taille de la barre de progress1 (qui est à 50%)
    progress1_bar_data = next(item for item in render_data if item['z_index'] == 5 + 2) # z_index de la barre
    expected_bar1_width = progress1.size[0] * progress1.progress_ratio
    assert abs(progress1_bar_data['size'][0] - expected_bar1_width) < 1e-6, f"Progress 1 bar width incorrect. Expected {expected_bar1_width}, got {progress1_bar_data['size'][0]}"
    print(f"Progress 1 Bar Width: {progress1_bar_data['size'][0]} (Correct)")

    print("Render data structure and z-ordering seem ok.")

    print("\n--- Tous les tests basiques de la barre de progression passés ---")