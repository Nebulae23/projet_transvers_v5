# src/engine/ui/widgets/icon.py
import numpy as np
from typing import Optional, Tuple, Any, Dict, List

from ..ui_base import UIElement

class Icon(UIElement):
    """
    Widget simple pour afficher une image ou une icône.
    """
    def __init__(self,
                 position: Tuple[int, int] = (0, 0),
                 size: Optional[Tuple[int, int]] = None, # La taille peut être celle de la texture si non fournie
                 parent: Optional[UIElement] = None,
                 texture_id: Optional[Any] = None, # ID de la texture/image à afficher
                 color: Tuple[float, float, float, float] = (1.0, 1.0, 1.0, 1.0), # Teinte (blanc par défaut = pas de teinte)
                 z_index: int = 0):
        """
        Initialise une nouvelle icône.

        Args:
            position (Tuple[int, int]): Position relative au parent.
            size (Optional[Tuple[int, int]]): Taille explicite. Si None, dépendra de la texture (non implémenté ici).
                                                Utilise une taille par défaut si None et pas de texture info.
            parent (Optional[UIElement]): Élément parent.
            texture_id (Optional[Any]): ID de la texture (dépendant du système de rendu/ressources).
            color (Tuple[float, float, float, float]): Couleur RGBA (0-1) pour teinter l'icône.
            z_index (int): Ordre de rendu.
        """
        # Si la taille n'est pas fournie, on utilise une taille par défaut.
        # Idéalement, on lirait la taille de la texture.
        default_size = (32, 32) # Taille par défaut arbitraire
        calculated_size = size if size is not None else default_size
        # TODO: Lire la taille de la texture si size is None et texture_id est valide

        super().__init__(position=position, size=calculated_size, parent=parent, z_index=z_index)

        self._texture_id = texture_id
        self.color = color # Pour la teinte

    def get_texture_id(self) -> Any:
        """Retourne l'ID de texture de l'icône."""
        return self._texture_id

    @property
    def texture_id(self) -> Any:
        return self._texture_id

    @texture_id.setter
    def texture_id(self, new_texture_id: Any):
        """Met à jour l'ID de texture."""
        if new_texture_id != self._texture_id:
            self._texture_id = new_texture_id
            # Potentiellement recalculer la taille si elle dépend de la texture
            # if self._size_depends_on_texture: self.recalculate_size()

    # def recalculate_size(self):
    #     """Recalcule la taille basée sur la texture actuelle."""
    #     # Nécessite accès au système de ressources pour obtenir les dimensions de la texture
    #     # tex_width, tex_height = resource_manager.get_texture_size(self._texture_id)
    #     # self.size = (tex_width, tex_height)
    #     pass

    def get_render_data(self) -> List[Dict[str, Any]]:
        """
        Génère les données de rendu pour l'icône.
        """
        render_list = []
        if self.visible and self.opacity > 0.0 and self._texture_id is not None:
            effective_size = self.size.astype(float) * self.scale
            center_position = self.absolute_position.astype(float) + self.size.astype(float) / 2.0

            # Appliquer l'opacité globale à la teinte alpha
            final_color = (
                self.color[0],
                self.color[1],
                self.color[2],
                self.color[3] * self.opacity
            )

            icon_data = {
                'type': 'sprite', # Ou 'icon', selon le renderer
                'position': center_position,
                'size': effective_size,
                'texture_id': self._texture_id,
                'color': final_color, # Teinte
                'rotation': 0.0,
                'z_index': self.z_index,
                'scale': self.scale.copy(),
            }
            render_list.append(icon_data)

            # Les icônes simples n'ont généralement pas d'enfants
            # Mais on garde la structure pour la cohérence
            for child in self.children:
                 render_list.extend(child.get_render_data())
            render_list.sort(key=lambda data: data.get('z_index', 0))

        return render_list

# --- Tests Basiques ---
if __name__ == "__main__":
    from ..ui_base import UIElement

    root = UIElement(size=(800, 600))

    # Simuler des ID de texture
    TEX_SWORD = "textures/items/sword.png"
    TEX_SHIELD = "textures/items/shield.png"

    icon1 = Icon(position=(100, 100), size=(64, 64), parent=root, texture_id=TEX_SWORD, z_index=5)
    icon2 = Icon(position=(200, 100), parent=root, texture_id=TEX_SHIELD, color=(1.0, 0.5, 0.5, 0.8), z_index=6) # Taille par défaut (32x32), teinte rouge/transparente

    print("\n--- Test Initial State ---")
    print(f"Icon 1 Texture: {icon1.texture_id}, Pos: {icon1.absolute_position}, Size: {icon1.size}, Z: {icon1.z_index}")
    print(f"Icon 2 Texture: {icon2.texture_id}, Pos: {icon2.absolute_position}, Size: {icon2.size}, Z: {icon2.z_index}")
    assert icon1.size[0] == 64 and icon1.size[1] == 64
    assert icon2.size[0] == 32 and icon2.size[1] == 32 # Taille par défaut

    print("\n--- Test Change Texture ---")
    icon1.texture_id = TEX_SHIELD
    assert icon1.texture_id == TEX_SHIELD
    print(f"Icon 1 New Texture: {icon1.texture_id}")

    print("\n--- Test Render Data ---")
    render_data = root.get_render_data()
    print(f"Nombre total d'éléments à rendre: {len(render_data)}")
    # Devrait contenir les données des deux icônes
    assert len(render_data) == 2, "Should have 2 render items (icon1, icon2)"

    # Vérifier l'ordre Z
    all_z = sorted([item['z_index'] for item in render_data])
    print(f"All Z-indices: {all_z}")
    assert all_z == [5, 6], f"Incorrect overall z-indices: {all_z}"

    # Vérifier les données spécifiques
    icon1_data = next(item for item in render_data if item['z_index'] == 5)
    icon2_data = next(item for item in render_data if item['z_index'] == 6)

    assert icon1_data['texture_id'] == TEX_SHIELD, "Icon 1 texture ID incorrect in render data"
    assert np.allclose(icon1_data['color'], (1.0, 1.0, 1.0, 1.0 * icon1.opacity)), "Icon 1 color incorrect"
    assert icon1_data['size'][0] == 64.0, "Icon 1 size incorrect"

    assert icon2_data['texture_id'] == TEX_SHIELD, "Icon 2 texture ID incorrect"
    assert np.allclose(icon2_data['color'], (1.0, 0.5, 0.5, 0.8 * icon2.opacity)), "Icon 2 color incorrect"
    assert icon2_data['size'][0] == 32.0, "Icon 2 size incorrect"

    print("Render data structure seems ok.")

    print("\n--- Tous les tests basiques de l'icône passés ---")