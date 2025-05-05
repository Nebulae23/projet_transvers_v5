# Mock pour le système de rendu
class MockRenderer:
    def __init__(self):
        self.draw_calls = []

    def draw_element(self, element, position, size):
        """Simule le dessin d'un élément UI."""
        self.draw_calls.append({
            'type': 'element',
            'element': element,
            'position': position,
            'size': size
        })
        # print(f"MockRenderer: Drawing {element} at {position} with size {size}") # Pour le débogage

    def draw_text(self, text, position, font, color):
        """Simule le dessin de texte."""
        self.draw_calls.append({
            'type': 'text',
            'text': text,
            'position': position,
            'font': font,
            'color': color
        })
        # print(f"MockRenderer: Drawing text '{text}' at {position}") # Pour le débogage

    def clear_draw_calls(self):
        """Réinitialise les appels de dessin enregistrés."""
        self.draw_calls = []

    def get_last_draw_call(self):
        """Retourne le dernier appel de dessin enregistré."""
        return self.draw_calls[-1] if self.draw_calls else None

    # Ajoutez d'autres méthodes de rendu mockées si nécessaire
    # def load_texture(self, path): ...
    # def set_viewport(self, x, y, width, height): ...