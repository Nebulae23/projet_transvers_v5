# src/engine/weather/components/visibility_component.py

class VisibilityComponent:
    """
    Composant attaché aux entités dont la visibilité peut être affectée
    par les conditions météorologiques (par exemple, brouillard, forte pluie).
    """
    def __init__(self, base_visibility_range: float):
        self.base_visibility_range = base_visibility_range
        self.current_visibility_range = base_visibility_range
        self.visibility_modifier = 1.0 # Modificateur appliqué par la météo

    def update_visibility(self, modifier: float):
        """ Met à jour la visibilité en appliquant un modificateur. """
        self.visibility_modifier = modifier
        self.current_visibility_range = self.base_visibility_range * self.visibility_modifier

    def get_visibility(self) -> float:
        """ Retourne la portée de visibilité actuelle. """
        return self.current_visibility_range