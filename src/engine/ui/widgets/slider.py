# src/engine/ui/widgets/slider.py
import numpy as np
from typing import Optional, Tuple, Any, Dict, List, Callable

from ..ui_base import UIElement, UIEvent, UIEventType

class Slider(UIElement):
    """
    Widget Slider (contrôle glissant) pour sélectionner une valeur dans une plage.
    """
    def __init__(self,
                 position: Tuple[int, int] = (0, 0),
                 size: Tuple[int, int] = (200, 20), # Taille totale du slider
                 parent: Optional[UIElement] = None,
                 min_value: float = 0.0,
                 max_value: float = 100.0,
                 value: float = 50.0,
                 orientation: str = 'horizontal', # 'horizontal' ou 'vertical'
                 track_color: Tuple[float, float, float, float] = (0.6, 0.6, 0.6, 1.0), # Couleur du rail
                 handle_color: Tuple[float, float, float, float] = (0.9, 0.9, 0.9, 1.0), # Couleur du curseur
                 handle_size: Optional[Tuple[int, int]] = None, # Taille du curseur (défaut basé sur la taille du slider)
                 on_value_changed: Optional[Callable[['Slider', float], None]] = None,
                 z_index: int = 0):
        """
        Initialise un nouveau slider.

        Args:
            position (Tuple[int, int]): Position relative au parent.
            size (Tuple[int, int]): Taille totale du slider (rail).
            parent (Optional[UIElement]): Élément parent.
            min_value (float): Valeur minimale.
            max_value (float): Valeur maximale.
            value (float): Valeur initiale.
            orientation (str): 'horizontal' ou 'vertical'.
            track_color (Tuple): Couleur RGBA (0-1) du rail.
            handle_color (Tuple): Couleur RGBA (0-1) du curseur.
            handle_size (Optional[Tuple[int, int]]): Taille du curseur. Si None, calculée.
            on_value_changed (Optional[Callable]): Callback appelé quand la valeur change.
            z_index (int): Ordre de rendu.
        """
        super().__init__(position=position, size=size, parent=parent, z_index=z_index)

        if max_value <= min_value:
            raise ValueError("max_value doit être supérieur à min_value.")
        self._min_value = min_value
        self._max_value = max_value
        self._value = max(min_value, min(value, max_value)) # Assurer valeur initiale dans la plage

        if orientation not in ['horizontal', 'vertical']:
            raise ValueError("orientation doit être 'horizontal' ou 'vertical'.")
        self.orientation = orientation

        self.track_color = track_color
        self.handle_color = handle_color

        # Calculer la taille du curseur si non fournie
        if handle_size is None:
            if self.orientation == 'horizontal':
                self._handle_size = np.array([size[1], size[1]], dtype=int) # Carré basé sur la hauteur
            else:
                self._handle_size = np.array([size[0], size[0]], dtype=int) # Carré basé sur la largeur
        else:
            if not isinstance(handle_size, tuple) or len(handle_size) != 2 or not all(isinstance(v, int) and v > 0 for v in handle_size):
                 raise TypeError("handle_size doit être un tuple de deux entiers positifs.")
            self._handle_size = np.array(handle_size, dtype=int)

        self.on_value_changed_callback = on_value_changed
        self._is_dragging = False

        # Enregistrer les gestionnaires d'événements
        self.on(UIEventType.MOUSE_BUTTON_DOWN, self._handle_mouse_down)
        self.on(UIEventType.MOUSE_BUTTON_UP, self._handle_mouse_up)
        self.on(UIEventType.MOUSE_MOTION, self._handle_mouse_motion)

    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, new_value: float):
        clamped_value = max(self._min_value, min(float(new_value), self._max_value))
        if clamped_value != self._value:
            old_value = self._value
            self._value = clamped_value
            if self.on_value_changed_callback:
                self.on_value_changed_callback(self, self._value)
            # Potentiellement redessiner ou mettre à jour l'affichage

    @property
    def min_value(self) -> float:
        return self._min_value

    @property
    def max_value(self) -> float:
        return self._max_value

    @property
    def value_ratio(self) -> float:
        """Retourne la position relative de la valeur (0.0 à 1.0)."""
        range_ = self._max_value - self._min_value
        return (self._value - self._min_value) / range_ if range_ > 0 else 0.0

    def _get_handle_position(self) -> np.ndarray:
        """Calcule la position du coin supérieur gauche du curseur."""
        track_length = self.size[0] if self.orientation == 'horizontal' else self.size[1]
        handle_dim = self._handle_size[0] if self.orientation == 'horizontal' else self._handle_size[1]
        # Espace disponible pour le centre du curseur
        available_track = track_length - handle_dim
        offset = self.value_ratio * available_track

        if self.orientation == 'horizontal':
            # Position X relative au début du slider, Y centré verticalement
            handle_x = self.absolute_position[0] + offset
            handle_y = self.absolute_position[1] + (self.size[1] - self._handle_size[1]) / 2
            return np.array([handle_x, handle_y], dtype=float)
        else:
            # Position Y relative au début du slider, X centré horizontalement
            handle_x = self.absolute_position[0] + (self.size[0] - self._handle_size[0]) / 2
            handle_y = self.absolute_position[1] + offset
            return np.array([handle_x, handle_y], dtype=float)

    def _update_value_from_pos(self, mouse_pos: Tuple[int, int]):
        """Met à jour la valeur du slider en fonction de la position de la souris."""
        relative_pos = np.array(mouse_pos) - self.absolute_position

        if self.orientation == 'horizontal':
            track_length = self.size[0]
            handle_width = self._handle_size[0]
            # Position de la souris relative au début de la zone cliquable du rail
            click_pos_on_track = relative_pos[0] - handle_width / 2
            # Espace de déplacement effectif du centre du curseur
            available_track = track_length - handle_width
            ratio = click_pos_on_track / available_track if available_track > 0 else 0.0
        else: # Vertical
            track_length = self.size[1]
            handle_height = self._handle_size[1]
            click_pos_on_track = relative_pos[1] - handle_height / 2
            available_track = track_length - handle_height
            ratio = click_pos_on_track / available_track if available_track > 0 else 0.0

        # Convertir le ratio en valeur
        clamped_ratio = max(0.0, min(1.0, ratio))
        range_ = self._max_value - self._min_value
        self.value = self._min_value + clamped_ratio * range_

    def _handle_mouse_down(self, event: UIEvent) -> bool:
        """Gère l'appui sur le bouton de la souris."""
        if event.data.get('button') == 1: # Bouton gauche
            mouse_pos = event.data.get('position')
            if mouse_pos:
                # Vérifier si le clic est sur le rail ou le curseur
                # Pour simplifier, on considère tout clic dans les limites du slider comme pertinent
                if self.is_event_relevant(event):
                    self._is_dragging = True
                    self._update_value_from_pos(mouse_pos)
                    # Changer l'apparence si nécessaire (ex: curseur plus sombre)
                    print(f"Slider drag started. Value: {self.value:.2f}")
                    return True # Événement géré
        return False

    def _handle_mouse_up(self, event: UIEvent) -> bool:
        """Gère le relâchement du bouton de la souris."""
        if event.data.get('button') == 1 and self._is_dragging: # Bouton gauche et en cours de drag
            self._is_dragging = False
            # Changer l'apparence si nécessaire (retour à la normale)
            print(f"Slider drag ended. Final Value: {self.value:.2f}")
            # Note: L'événement a déjà été géré par le MOUSE_BUTTON_DOWN initial
            # et les MOUSE_MOTION suivants. On peut retourner True pour confirmer
            # la fin de l'interaction, mais ce n'est pas crucial ici.
            return True
        return False

    def _handle_mouse_motion(self, event: UIEvent) -> bool:
        """Gère le mouvement de la souris pendant le drag."""
        if self._is_dragging:
            mouse_pos = event.data.get('position')
            if mouse_pos:
                self._update_value_from_pos(mouse_pos)
                print(f"Slider dragging. Value: {self.value:.2f}")
                return True # Événement géré pendant le drag
        return False

    def get_render_data(self) -> List[Dict[str, Any]]:
        """
        Génère les données de rendu pour le rail (track) et le curseur (handle).
        """
        render_list = []
        if not self.visible or self.opacity <= 0.0:
            return render_list

        base_pos = self.absolute_position.astype(float)
        base_size = self.size.astype(float)
        effective_opacity = self.opacity

        # 1. Rail (Track)
        track_center_pos = base_pos + base_size / 2.0
        track_color_final = (
            self.track_color[0], self.track_color[1], self.track_color[2],
            self.track_color[3] * effective_opacity
        )
        track_data = {
            'type': 'rect_fill',
            'position': track_center_pos,
            'size': base_size * self.scale, # Appliquer l'échelle au rail
            'color': track_color_final,
            'texture_id': None,
            'rotation': 0.0,
            'z_index': self.z_index,
            'scale': np.array([1.0, 1.0]) # Échelle déjà appliquée à la taille
        }
        render_list.append(track_data)

        # 2. Curseur (Handle)
        handle_pos = self._get_handle_position()
        handle_size_float = self._handle_size.astype(float)
        handle_center_pos = handle_pos + handle_size_float / 2.0
        handle_color_final = (
            self.handle_color[0], self.handle_color[1], self.handle_color[2],
            self.handle_color[3] * effective_opacity
        )
        handle_data = {
            'type': 'rect_fill',
            'position': handle_center_pos,
            'size': handle_size_float * self.scale, # Appliquer l'échelle au curseur
            'color': handle_color_final,
            'texture_id': None,
            'rotation': 0.0,
            'z_index': self.z_index + 1, # Au-dessus du rail
            'scale': np.array([1.0, 1.0])
        }
        render_list.append(handle_data)

        # Trier par z_index
        render_list.sort(key=lambda data: data.get('z_index', 0))

        # Ajouter les enfants si nécessaire (peu probable pour un slider simple)
        for child in self.children:
             render_list.extend(child.get_render_data())
        render_list.sort(key=lambda data: data.get('z_index', 0))

        return render_list

    def get_texture_id(self) -> Any:
        """Les sliders n'utilisent pas de texture unique par défaut."""
        return None

# --- Tests Basiques ---
if __name__ == "__main__":
    from ..ui_base import UIElement

    root = UIElement(size=(800, 600))
    changed_values = []
    def value_changed_cb(slider_instance, new_value):
        print(f"Callback: Slider value changed to {new_value:.2f}")
        changed_values.append(new_value)

    slider_h = Slider(position=(50, 50), size=(300, 15), parent=root, value=25, max_value=100, on_value_changed=value_changed_cb, z_index=3)
    slider_v = Slider(position=(400, 50), size=(15, 200), parent=root, value=80, max_value=100, orientation='vertical', on_value_changed=value_changed_cb, z_index=4)

    print("\n--- Test Initial State ---")
    print(f"Slider H Value: {slider_h.value:.2f}, Ratio: {slider_h.value_ratio:.2f}, Z: {slider_h.z_index}")
    print(f"Slider V Value: {slider_v.value:.2f}, Ratio: {slider_v.value_ratio:.2f}, Z: {slider_v.z_index}")
    assert abs(slider_h.value - 25.0) < 1e-6
    assert abs(slider_v.value - 80.0) < 1e-6

    print("\n--- Test Mouse Down & Drag (Horizontal) ---")
    # Simuler un clic au milieu du slider H (devrait donner environ 50)
    # Position absolue du slider H: (50, 50)
    # Taille: (300, 15), Taille curseur: (15, 15)
    # Milieu du rail: 50 + 300/2 = 200
    # Espace dispo: 300 - 15 = 285
    # Clic à x=200 -> pos relative = 150. click_pos_on_track = 150 - 15/2 = 142.5
    # Ratio = 142.5 / 285 = 0.5. Value = 0 + 0.5 * 100 = 50
    down_pos_h = (50 + 150, 50 + 7) # x=200, y=57
    root.handle_event(UIEvent(UIEventType.MOUSE_BUTTON_DOWN, {'position': down_pos_h, 'button': 1}))
    assert slider_h._is_dragging is True, "Slider H should be dragging"
    assert abs(slider_h.value - 50.0) < 1, f"Slider H value should be ~50 after click. Got {slider_h.value}"
    assert len(changed_values) > 0 and abs(changed_values[-1] - 50.0) < 1, "Callback not called or incorrect value"

    # Simuler un drag vers la droite (vers 75%)
    # 75% -> ratio 0.75. click_pos_on_track = 0.75 * 285 = 213.75
    # pos relative = 213.75 + 15/2 = 221.25. Position absolue x = 50 + 221.25 = 271.25
    drag_pos_h = (50 + 225, 50 + 7) # x=275, y=57 (environ 75%)
    root.handle_event(UIEvent(UIEventType.MOUSE_MOTION, {'position': drag_pos_h}))
    assert abs(slider_h.value - 75.0) < 5, f"Slider H value should be ~75 after drag. Got {slider_h.value}" # Tolérance plus large pour le calcul inverse
    assert len(changed_values) > 1 and abs(changed_values[-1] - 75.0) < 5, "Callback not called or incorrect value during drag"

    # Simuler relâchement
    root.handle_event(UIEvent(UIEventType.MOUSE_BUTTON_UP, {'position': drag_pos_h, 'button': 1}))
    assert slider_h._is_dragging is False, "Slider H should not be dragging anymore"
    print(f"Slider H Final Value after drag: {slider_h.value:.2f}")

    print("\n--- Test Mouse Down & Drag (Vertical) ---")
    # Simuler un clic en bas du slider V (devrait donner environ 100)
    # Position absolue: (400, 50)
    # Taille: (15, 200), Taille curseur: (15, 15)
    # Bas du rail: 50 + 200 = 250
    # Espace dispo: 200 - 15 = 185
    # Clic à y=245 -> pos relative = 195. click_pos_on_track = 195 - 15/2 = 187.5
    # Ratio = 187.5 / 185 ~= 1.0. Value = 0 + 1.0 * 100 = 100
    down_pos_v = (400 + 7, 50 + 195) # x=407, y=245
    root.handle_event(UIEvent(UIEventType.MOUSE_BUTTON_DOWN, {'position': down_pos_v, 'button': 1}))
    assert slider_v._is_dragging is True, "Slider V should be dragging"
    assert abs(slider_v.value - 100.0) < 1, f"Slider V value should be ~100 after click. Got {slider_v.value}"

    # Relâcher
    root.handle_event(UIEvent(UIEventType.MOUSE_BUTTON_UP, {'position': down_pos_v, 'button': 1}))
    assert slider_v._is_dragging is False, "Slider V should not be dragging anymore"
    print(f"Slider V Final Value after click: {slider_v.value:.2f}")


    print("\n--- Test Render Data ---")
    render_data = root.get_render_data()
    print(f"Nombre total d'éléments à rendre: {len(render_data)}")
    # 2 sliders * (1 track + 1 handle) = 4 éléments
    assert len(render_data) == 4, "Should have 4 render items (2 tracks + 2 handles)"

    # Vérifier les z_index relatifs (handle au-dessus du track)
    slider_h_items = sorted([item for item in render_data if item['z_index'] in [3, 4]], key=lambda x: x['z_index'])
    slider_v_items = sorted([item for item in render_data if item['z_index'] in [4, 5]], key=lambda x: x['z_index']) # Z-index 4 et 5 pour V

    # Correction: slider_v a z_index 4, son handle est 5. slider_h a z_index 3, son handle est 4.
    # Donc les z_indices attendus sont 3 (track H), 4 (handle H), 4 (track V), 5 (handle V)
    all_z = sorted([item['z_index'] for item in render_data])
    print(f"All Z-indices: {all_z}")
    assert all_z == [3, 4, 4, 5], f"Incorrect overall z-indices: {all_z}"

    # Vérifier la position du handle H (valeur ~75)
    handle_h_data = next(item for item in render_data if item['z_index'] == 4 and item['size'][0] == slider_h._handle_size[0]) # Handle H a z=4
    expected_handle_h_pos = slider_h._get_handle_position()
    # Comparer les positions des coins supérieurs gauches
    assert np.allclose(handle_h_data['position'] - handle_h_data['size']/2, expected_handle_h_pos, atol=1.0), \
        f"Slider H handle position incorrect. Expected ~{expected_handle_h_pos}, got {handle_h_data['position'] - handle_h_data['size']/2}"
    print("Slider H handle position seems ok.")

    print("\n--- Tous les tests basiques du slider passés ---")