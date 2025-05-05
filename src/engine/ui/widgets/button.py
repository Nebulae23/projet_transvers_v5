# src/engine/ui/widgets/button.py
import numpy as np
from typing import Optional, Tuple, Callable, Any

from ..ui_base import UIElement, UIEvent, UIEventType

class Button(UIElement):
    """
    Widget Bouton interactif.
    Peut réagir aux clics et afficher différents états (normal, survolé, cliqué).
    """
    def __init__(self,
                 position: Tuple[int, int] = (0, 0),
                 size: Tuple[int, int] = (100, 30),
                 parent: Optional[UIElement] = None,
                 text: str = "Button",
                 on_click: Optional[Callable[['Button'], None]] = None,
                 z_index: int = 1):
        """
        Initialise un nouveau bouton.

        Args:
            position (Tuple[int, int]): Position relative au parent.
            size (Tuple[int, int]): Taille du bouton.
            parent (Optional[UIElement]): Élément parent.
            text (str): Texte affiché sur le bouton.
            on_click (Optional[Callable[['Button'], None]]): Fonction à appeler lors d'un clic.
            z_index (int): Ordre de rendu.
        """
        super().__init__(position=position, size=size, parent=parent, z_index=z_index)
        self.text = text
        self.on_click_callback = on_click

        self.is_hovered = False
        self.is_pressed = False

        # Enregistrer les gestionnaires d'événements internes
        self.on(UIEventType.MOUSE_BUTTON_DOWN, self._handle_mouse_down)
        self.on(UIEventType.MOUSE_BUTTON_UP, self._handle_mouse_up)
        self.on(UIEventType.MOUSE_MOTION, self._handle_mouse_motion) # Pour gérer le survol

    def _handle_mouse_down(self, event: UIEvent) -> bool:
        """Gère l'événement de clic souris enfoncé."""
        # Vérifie si le clic est dans les limites (déjà fait par is_event_relevant)
        mouse_button = event.data.get('button', -1)
        if mouse_button == 1: # Bouton gauche
            self.is_pressed = True
            # Ici, on pourrait changer l'apparence du bouton (ex: texture_pressed)
            print(f"Button '{self.text}' pressed.")
            return True # Événement géré
        return False

    def _handle_mouse_up(self, event: UIEvent) -> bool:
        """Gère l'événement de clic souris relâché."""
        mouse_button = event.data.get('button', -1)
        if mouse_button == 1: # Bouton gauche
            was_pressed = self.is_pressed
            self.is_pressed = False
            # Vérifier si la souris est toujours sur le bouton au moment du relâchement
            mouse_pos = event.data.get('position')
            if was_pressed and mouse_pos and self.is_event_relevant(event):
                # Le clic est valide, appeler le callback
                print(f"Button '{self.text}' clicked!")
                if self.on_click_callback:
                    self.on_click_callback(self)
                # Ici, on pourrait changer l'apparence (retour à normal/hover)
                return True # Événement géré
            # Si relâché en dehors ou non pressé initialement, ne rien faire d'autre
            # Ici, on pourrait changer l'apparence (retour à normal/hover)
        return False # Laisser l'événement se propager si ce n'était pas un clic gauche valide

    def _handle_mouse_motion(self, event: UIEvent) -> bool:
        """Gère le mouvement de la souris pour détecter le survol."""
        mouse_pos = event.data.get('position')
        if mouse_pos:
            is_currently_over = self.is_event_relevant(event) # is_event_relevant vérifie les limites

            if is_currently_over and not self.is_hovered:
                self.is_hovered = True
                # Changer l'apparence pour l'état survolé
                print(f"Button '{self.text}' hovered.")
                # On ne retourne pas True ici, car le survol ne "consomme" généralement pas l'événement
                # pour les autres éléments (sauf si on veut un comportement exclusif).
            elif not is_currently_over and self.is_hovered:
                self.is_hovered = False
                self.is_pressed = False # Si on quitte en étant pressé, on annule le clic potentiel
                # Changer l'apparence pour l'état normal
                print(f"Button '{self.text}' unhovered.")

        return False # Laisser l'événement se propager

    def get_texture_id(self) -> Any:
        """
        Retourne l'ID de texture approprié en fonction de l'état du bouton.
        Pour l'instant, retourne None. À adapter avec le système de rendu/ressources.
        """
        if self.is_pressed and self.is_hovered:
            # return "texture_button_pressed"
            pass
        elif self.is_hovered:
            # return "texture_button_hover"
            pass
        else:
            # return "texture_button_normal"
            pass
        return None # Placeholder

    def get_render_data(self) -> list[dict]:
        """
        Génère les données de rendu pour le bouton, y compris le texte.
        """
        render_list = super().get_render_data()

        # Ajouter les données pour le rendu du texte (simplifié)
        # Ceci suppose qu'il existe un moyen de rendre du texte via le système de rendu.
        # Il faudrait une classe TextElement dédiée ou intégrer le rendu de texte ici.
        if self.visible and self.opacity > 0.0 and self.text:
            # Calculer la position du texte (centré dans le bouton par exemple)
            text_pos = self.absolute_position + self.size / 2
            text_data = {
                'type': 'text', # Indiquer au renderer qu'il s'agit de texte
                'text': self.text,
                'position': text_pos.astype(float),
                'font_id': None, # Placeholder pour l'ID de la police
                'font_size': 16, # Placeholder
                'color': (0.0, 0.0, 0.0, self.opacity), # Couleur du texte (noir opaque)
                'z_index': self.z_index + 1, # Assurer que le texte est au-dessus du fond du bouton
                # Autres options : alignement, etc.
            }
            # Trouver l'index où insérer le texte pour respecter le z_index
            # (Alternative: le système UI global trie tout à la fin)
            insert_index = len(render_list)
            for i, item in enumerate(render_list):
                if item.get('z_index', 0) > text_data['z_index']:
                    insert_index = i
                    break
            render_list.insert(insert_index, text_data)


        return render_list

# --- Tests Basiques ---
if __name__ == "__main__":
    root = UIElement(size=(800, 600)) # Parent racine virtuel

    def my_button_click(button_instance):
        print(f"Callback: Bouton '{button_instance.text}' a été cliqué !")
        button_instance.text = "Clicked!" # Changer le texte après clic

    button1 = Button(position=(50, 50), size=(120, 40), text="Click Me", parent=root, on_click=my_button_click)
    button2 = Button(position=(50, 100), size=(120, 40), text="Disabled?", parent=root)

    print("\n--- Test Initial State ---")
    print(f"Button 1 Text: {button1.text}, Hovered: {button1.is_hovered}, Pressed: {button1.is_pressed}")
    print(f"Button 2 Text: {button2.text}, Hovered: {button2.is_hovered}, Pressed: {button2.is_pressed}")

    print("\n--- Test Mouse Motion (Hover Button 1) ---")
    motion_event_over = UIEvent(UIEventType.MOUSE_MOTION, {'position': (70, 60)}) # Sur bouton 1
    root.handle_event(motion_event_over)
    assert button1.is_hovered is True, "Button 1 should be hovered"
    assert button2.is_hovered is False, "Button 2 should not be hovered"
    print(f"Button 1 Hovered: {button1.is_hovered}")

    print("\n--- Test Mouse Button Down (Press Button 1) ---")
    down_event = UIEvent(UIEventType.MOUSE_BUTTON_DOWN, {'position': (70, 60), 'button': 1})
    root.handle_event(down_event)
    assert button1.is_pressed is True, "Button 1 should be pressed"
    print(f"Button 1 Pressed: {button1.is_pressed}")

    print("\n--- Test Mouse Motion (Move off Button 1 while pressed) ---")
    motion_event_off = UIEvent(UIEventType.MOUSE_MOTION, {'position': (200, 60)}) # Hors bouton 1
    root.handle_event(motion_event_off)
    assert button1.is_hovered is False, "Button 1 should not be hovered anymore"
    # Note: is_pressed reste True jusqu'au relâchement, mais le survol est parti
    print(f"Button 1 Hovered: {button1.is_hovered}, Pressed: {button1.is_pressed}")

    print("\n--- Test Mouse Button Up (Release off Button 1) ---")
    up_event_off = UIEvent(UIEventType.MOUSE_BUTTON_UP, {'position': (200, 60), 'button': 1})
    root.handle_event(up_event_off)
    assert button1.is_pressed is False, "Button 1 should not be pressed anymore"
    assert button1.text == "Click Me", "Button 1 text should not have changed (released off)"
    print(f"Button 1 Pressed: {button1.is_pressed}, Text: {button1.text}")

    print("\n--- Test Full Click (Hover, Down, Up on Button 1) ---")
    # Hover
    root.handle_event(UIEvent(UIEventType.MOUSE_MOTION, {'position': (75, 65)}))
    # Down
    root.handle_event(UIEvent(UIEventType.MOUSE_BUTTON_DOWN, {'position': (75, 65), 'button': 1}))
    # Up
    root.handle_event(UIEvent(UIEventType.MOUSE_BUTTON_UP, {'position': (75, 65), 'button': 1}))
    assert button1.is_pressed is False, "Button 1 should not be pressed after click"
    assert button1.is_hovered is True, "Button 1 should still be hovered after click"
    assert button1.text == "Clicked!", "Button 1 text should have changed"
    print(f"Button 1 Text: {button1.text}, Hovered: {button1.is_hovered}, Pressed: {button1.is_pressed}")

    print("\n--- Test Render Data ---")
    render_data = root.get_render_data()
    # Devrait contenir les données du bouton 1, son texte, bouton 2, son texte
    print(f"Nombre d'éléments à rendre: {len(render_data)}")
    assert len(render_data) == 4, "Should have 4 render items (2 buttons + 2 texts)"

    button1_bg_data = next(item for item in render_data if item.get('type') != 'text' and np.array_equal(item['size'], button1.size.astype(float)))
    button1_text_data = next(item for item in render_data if item.get('type') == 'text' and item['text'] == button1.text)

    assert button1_bg_data is not None, "Button 1 background render data not found"
    assert button1_text_data is not None, "Button 1 text render data not found"
    assert button1_text_data['z_index'] > button1_bg_data['z_index'], "Text z_index should be higher than background"
    print("Render data structure seems ok.")

    print("\n--- Tous les tests basiques du bouton passés ---")