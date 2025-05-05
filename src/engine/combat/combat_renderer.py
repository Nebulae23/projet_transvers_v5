# src/engine/combat/combat_renderer.py
import pygame
import numpy as np
from ..ecs.world import World
from ..ecs.components import Transform, Health
from ..fx.particle_system import ParticleSystem # Ajout pour les particules
from ..rendering.effect_system import EffectSystem # Ajout pour les effets (lumières, etc.)
from collections import deque # Pour la file d'attente

# TODO: Importer les modules fx spécifiques (warrior_fx, mage_fx, etc.)
# from .fx.ability_effects import warrior_fx, mage_fx, cleric_fx, alchemist_fx, ranger_fx, summoner_fx

class CombatRenderer:
    def __init__(self, world: World, particle_system: ParticleSystem, effect_system: EffectSystem):
        self.world = world
        self.particle_system = particle_system
        self.effect_system = effect_system
        self._effect_queue = deque() # File d'attente pour les effets visuels
        # Couleurs pour les barres de vie
        self.health_bar_background_color = (50, 50, 50) # Gris foncé
        self.health_bar_foreground_color = (0, 255, 0) # Vert
        self.health_bar_width = 40  # Largeur en pixels
        self.health_bar_height = 5   # Hauteur en pixels
        self.health_bar_offset_y = -20 # Décalage vertical au-dessus de l'entité

    def queue_effect(self, effect_type: str, position: np.ndarray, **kwargs):
        """Ajoute un effet visuel à la file d'attente."""
        self._effect_queue.append({
            "type": effect_type,
            "position": position,
            "params": kwargs
        })

    def _render_warrior_effect(self, surface: pygame.Surface, camera_offset: np.ndarray, position: np.ndarray, params: dict):
        """Rendu spécifique pour les effets du guerrier."""
        # TODO: Implémenter le rendu (particules, shaders, etc.)
        # Exemple: self.particle_system.emit('sword_slash', position - camera_offset)
        # Exemple: self.effect_system.add_light(position, color=(200, 200, 200), radius=50, duration=0.1)
        pass

    def _render_mage_effect(self, surface: pygame.Surface, camera_offset: np.ndarray, position: np.ndarray, params: dict):
        """Rendu spécifique pour les effets du mage."""
        # TODO: Implémenter le rendu
        pass

    def _render_cleric_effect(self, surface: pygame.Surface, camera_offset: np.ndarray, position: np.ndarray, params: dict):
        """Rendu spécifique pour les effets du clerc."""
        # TODO: Implémenter le rendu
        pass

    def _render_alchemist_effect(self, surface: pygame.Surface, camera_offset: np.ndarray, position: np.ndarray, params: dict):
        """Rendu spécifique pour les effets de l'alchimiste."""
        # TODO: Implémenter le rendu
        pass

    def _render_ranger_effect(self, surface: pygame.Surface, camera_offset: np.ndarray, position: np.ndarray, params: dict):
        """Rendu spécifique pour les effets du rôdeur."""
        # TODO: Implémenter le rendu
        pass

    def _render_summoner_effect(self, surface: pygame.Surface, camera_offset: np.ndarray, position: np.ndarray, params: dict):
        """Rendu spécifique pour les effets de l'invocateur."""
        # TODO: Implémenter le rendu
        pass

    def draw(self, surface: pygame.Surface, camera_offset: np.ndarray):
        """Dessine les éléments visuels liés au combat (barres de vie, effets)."""
        # --- Dessin des barres de vie ---
        entities_with_health = self.world.get_entities_with_components([Transform, Health])
        for entity in entities_with_health:
            transform = entity.get_component(Transform)
            health = entity.get_component(Health)

            if not transform or not health:
                continue

            # Ne pas dessiner la barre de vie si l'entité est morte
            if health.current_health <= 0:
                continue

            # Calculer la position de la barre de vie à l'écran
            screen_pos = transform.position - camera_offset
            bar_x = screen_pos[0] - self.health_bar_width / 2
            bar_y = screen_pos[1] + self.health_bar_offset_y - self.health_bar_height / 2

            # Calculer la largeur de la barre de santé actuelle
            health_ratio = health.current_health / health.max_health
            current_health_width = int(self.health_bar_width * health_ratio)

            # Dessiner le fond de la barre de vie
            background_rect = pygame.Rect(
                bar_x,
                bar_y,
                self.health_bar_width,
                self.health_bar_height
            )
            pygame.draw.rect(surface, self.health_bar_background_color, background_rect)

            # Dessiner la barre de vie actuelle (si > 0)
            if current_health_width > 0:
                foreground_rect = pygame.Rect(
                    bar_x,
                    bar_y,
                    current_health_width,
                    self.health_bar_height
                )
                pygame.draw.rect(surface, self.health_bar_foreground_color, foreground_rect)

        # --- Traitement et dessin des effets visuels en file d'attente ---
        effects_to_render = list(self._effect_queue) # Copie pour itération
        self._effect_queue.clear() # Vider la file originale

        for effect_data in effects_to_render:
            effect_type = effect_data["type"]
            position = effect_data["position"]
            params = effect_data["params"]

            # Appeler la méthode de rendu appropriée
            render_method_name = f"_render_{effect_type}_effect"
            render_method = getattr(self, render_method_name, None)

            if render_method:
                render_method(surface, camera_offset, position, params)
            else:
                print(f"Warning: No render method found for effect type '{effect_type}'")

        # TODO: Implémenter l'affichage des nombres de dégâts flottants (peut être géré comme un autre type d'effet)