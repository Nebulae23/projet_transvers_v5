# src/engine/rendering/integration/sprite_lighting.py
"""
Applique un éclairage dynamique aux sprites 2D en utilisant les informations
d'éclairage de la scène 3D pour une meilleure intégration visuelle.
"""

class SpriteLightingManager:
    def __init__(self, light_system_3d, shader_manager):
        """
        Initialise le gestionnaire d'éclairage des sprites.

        Args:
            light_system_3d: Le système gérant les lumières dans la scène 3D.
            shader_manager: Le gestionnaire de shaders pour charger/compiler les shaders.
        """
        self.light_system_3d = light_system_3d
        self.shader_manager = shader_manager
        self.sprite_lighting_shader = None
        self._load_shaders()
        print("SpriteLightingManager initialized.")

    def _load_shaders(self):
        """Charge les shaders nécessaires pour l'éclairage des sprites."""
        try:
            # Charger un shader PBR ou un shader spécifique pour l'éclairage des sprites
            # Ce shader utilisera les informations de lumière 3D (position, couleur, intensité)
            # et potentiellement les normales des sprites (si disponibles/simulées)
            # pour calculer l'éclairage.
            self.sprite_lighting_shader = self.shader_manager.load_shader(
                "sprite_pbr", # Nom logique du shader d'intégration
                vert_path="src/engine/shaders/integration/sprite_pbr.vert",
                frag_path="src/engine/shaders/integration/sprite_pbr.frag"
            )
            print("Sprite lighting shader loaded successfully.")
        except Exception as e:
            print(f"Error loading sprite lighting shader: {e}")
            # Fallback ou gestion d'erreur
            self.sprite_lighting_shader = None # Ou un shader par défaut

    def apply_lighting_to_sprite(self, sprite, render_context):
        """
        Applique l'éclairage au rendu d'un sprite individuel.
        Cette méthode serait appelée pendant la passe de rendu des sprites.

        Args:
            sprite: L'entité sprite à éclairer.
            render_context: Contexte de rendu contenant les informations globales (caméra, lumières).
        """
        if not self.sprite_lighting_shader:
            # Si le shader n'est pas chargé, utiliser un rendu simple (sans éclairage dynamique)
            # Ou logguer une erreur et skipper l'éclairage
            # print("Warning: Sprite lighting shader not available.")
            # self.render_sprite_unlit(sprite, render_context) # Méthode de rendu sans éclairage
            return

        # 1. Activer le shader d'éclairage des sprites
        self.sprite_lighting_shader.use()

        # 2. Récupérer les informations de lumière pertinentes de la scène 3D
        #    Ceci pourrait être les lumières les plus proches, la lumière directionnelle globale, etc.
        sprite_pos = sprite.get_component('Transform').position
        relevant_lights = self.light_system_3d.get_lights_affecting_point(sprite_pos, max_lights=4)

        # 3. Passer les informations de lumière et les propriétés du sprite au shader
        #    - Position du sprite, texture, couleur de base, etc.
        #    - Données des lumières (position, couleur, intensité, type)
        #    - Informations de la caméra (position, matrices de projection/vue)
        #    - Potentiellement une "normal map" simulée pour le sprite si on veut des effets plus avancés

        # Exemple de passage d'uniforms (les noms et types dépendent du shader GLSL)
        self.sprite_lighting_shader.set_uniform("u_spriteTexture", sprite.get_component('Renderable').texture_unit)
        self.sprite_lighting_shader.set_uniform("u_modelMatrix", sprite.get_component('Transform').get_matrix())
        self.sprite_lighting_shader.set_uniform("u_viewMatrix", render_context.camera.get_view_matrix())
        self.sprite_lighting_shader.set_uniform("u_projectionMatrix", render_context.camera.get_projection_matrix())
        self.sprite_lighting_shader.set_uniform("u_cameraPosition", render_context.camera.position)
        self.sprite_lighting_shader.set_uniform("u_ambientLight", self.light_system_3d.get_ambient_light())

        # Passer les données des lumières (souvent sous forme de tableaux d'uniforms ou UBO)
        for i, light in enumerate(relevant_lights):
            prefix = f"u_lights[{i}]"
            self.sprite_lighting_shader.set_uniform(f"{prefix}.position", light.position)
            self.sprite_lighting_shader.set_uniform(f"{prefix}.color", light.color)
            self.sprite_lighting_shader.set_uniform(f"{prefix}.intensity", light.intensity)
            self.sprite_lighting_shader.set_uniform(f"{prefix}.type", light.type) # 0: Point, 1: Directional, etc.
        self.sprite_lighting_shader.set_uniform("u_numLights", len(relevant_lights))

        # 4. Dessiner le sprite (le VAO/VBO du sprite doit être lié au préalable)
        #    La commande de dessin réelle est généralement gérée par le système de rendu principal.
        #    Ici, on s'assure que le shader est correctement configuré AVANT le dessin.
        #    Exemple: renderer.draw_sprite_vao(sprite.vao)

        # print(f"Applied dynamic lighting to sprite {sprite.id}") # Peut être verbeux

    def update(self, dt):
        """
        Mise à jour périodique si nécessaire (ex: recharger les shaders).
        """
        # Peut être utilisé pour des mises à jour dynamiques ou le rechargement de shaders à chaud
        pass

# Exemple d'utilisation (simulation)
if __name__ == '__main__':
    # Mocks pour la simulation
    class MockLight:
        def __init__(self, pos, color, intensity, type):
            self.position = pos
            self.color = color
            self.intensity = intensity
            self.type = type
    class MockLightSystem:
        def get_lights_affecting_point(self, pos, max_lights):
            # Simule la récupération des lumières proches
            return [
                MockLight((10, 20, 5), (1.0, 0.8, 0.8), 1.5, 0), # Point light
                MockLight((0, 0, 1), (0.2, 0.2, 0.5), 0.5, 1)   # Directional light (position is direction)
            ]
        def get_ambient_light(self):
            return (0.1, 0.1, 0.1)
    class MockShader:
        def use(self): pass
        def set_uniform(self, name, value): pass # print(f"Set uniform {name} = {value}")
    class MockShaderManager:
        def load_shader(self, name, vert_path, frag_path):
            print(f"Loading shader '{name}' from {vert_path}, {frag_path}")
            # Simule le chargement réussi
            return MockShader()
    class MockTransform:
        def __init__(self, x=0, y=0, z=0):
            self.position = type('Vec3', (), {'x': x, 'y': y, 'z': z})()
        def get_matrix(self): return [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]] # Matrice identité
    class MockRenderable:
        def __init__(self):
            self.texture_unit = 0
    class MockSprite:
        def __init__(self, id, x, y, z=0): # Ajout de Z pour la position 3D
            self.id = id
            self._components = {
                'Transform': MockTransform(x, y, z),
                'Renderable': MockRenderable()
            }
        def get_component(self, name):
            return self._components[name]
    class MockCamera:
        position = (0, 10, 50)
        def get_view_matrix(self): return [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
        def get_projection_matrix(self): return [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]]
    class MockRenderContext:
        camera = MockCamera()

    # Initialisation
    light_system = MockLightSystem()
    shader_manager = MockShaderManager()
    lighting_manager = SpriteLightingManager(light_system, shader_manager)

    # Création d'un sprite de test
    test_sprite = MockSprite(1, 10, 5, 2) # Positionné dans l'espace 3D

    # Simulation de l'application de l'éclairage pendant le rendu
    print("\nApplying lighting to test sprite...")
    render_context = MockRenderContext()
    lighting_manager.apply_lighting_to_sprite(test_sprite, render_context)
    print("Lighting application simulated.")