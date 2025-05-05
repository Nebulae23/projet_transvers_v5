# src/engine/rendering/effects/sprite_shadows.py
"""
Gère la génération et l'application des ombres portées par les sprites 2D
sur l'environnement 3D.
"""

class SpriteShadowManager:
    def __init__(self, shader_manager, light_system, resolution=(1024, 1024)):
        """
        Initialise le gestionnaire d'ombres pour sprites.

        Args:
            shader_manager: Gestionnaire pour charger les shaders d'ombres.
            light_system: Système de lumière 3D pour obtenir la source lumineuse principale.
            resolution (tuple): Résolution de la shadow map pour les sprites.
        """
        self.shader_manager = shader_manager
        self.light_system = light_system
        self.shadow_map_resolution = resolution
        self.sprite_shadow_shader = None
        self.shadow_map_fbo = None
        self.light_view_projection_matrix = None # Matrice VP de la lumière
        self._load_shaders()
        self._create_render_targets()
        print(f"SpriteShadowManager initialized with shadow map resolution {resolution}.")

    def _load_shaders(self):
        """Charge le shader pour le rendu dans la shadow map."""
        try:
            # Ce shader est simple : il transforme la position du sprite en utilisant
            # la matrice vue-projection de la lumière et écrit la profondeur.
            # Il peut ignorer la couleur/texture.
            self.sprite_shadow_shader = self.shader_manager.load_shader(
                "sprite_shadow_map_gen",
                # Chemins hypothétiques, utiliser les shaders dédiés si créés
                vert_path="src/engine/shaders/shadows/sprite_shadow.vert", # Shader spécifique
                frag_path="src/engine/shaders/shadows/sprite_shadow.frag"  # Peut être très simple (juste écrit la profondeur)
            )
            print("Sprite shadow map generation shader loaded successfully.")
        except Exception as e:
            print(f"Error loading sprite shadow map shader: {e}")
            self.sprite_shadow_shader = None

    def _create_render_targets(self):
        """Crée le framebuffer (FBO) pour la shadow map des sprites."""
        try:
            # La shadow map ne nécessite généralement qu'un buffer de profondeur.
            self.shadow_map_fbo = self.create_depth_fbo(
                self.shadow_map_resolution[0],
                self.shadow_map_resolution[1],
                "sprite_shadow_map"
            )
            print("Sprite shadow map FBO created.")
        except Exception as e:
            print(f"Error creating sprite shadow map FBO: {e}")
            self.shadow_map_fbo = None

    def render_shadow_map(self, sprites_to_cast_shadows):
        """
        Effectue la passe de rendu pour générer la shadow map des sprites.

        Args:
            sprites_to_cast_shadows (list): Liste des entités sprites qui doivent projeter une ombre.
        """
        if not self.sprite_shadow_shader or not self.shadow_map_fbo:
            print("Error: Sprite shadow system not initialized. Skipping shadow map generation.")
            return

        # 1. Obtenir la lumière principale (ex: directionnelle) et calculer sa matrice VP
        main_light = self.light_system.get_main_directional_light() # Méthode hypothétique
        if not main_light:
            print("Warning: No main directional light found for sprite shadows.")
            return

        # Calculer la matrice Vue-Projection du point de vue de la lumière
        # Ceci dépend du type de lumière (orthographique pour directionnelle, perspective pour spot)
        self.light_view_projection_matrix = self._calculate_light_vp_matrix(main_light)

        # 2. Configurer le viewport et lier le FBO de la shadow map
        # graphics_api.set_viewport(0, 0, self.shadow_map_resolution[0], self.shadow_map_resolution[1])
        self.shadow_map_fbo.bind()
        # graphics_api.clear_depth_buffer(1.0) # Effacer le buffer de profondeur

        # 3. Activer le shader de génération de shadow map
        self.sprite_shadow_shader.use()
        self.sprite_shadow_shader.set_uniform("u_lightViewProjectionMatrix", self.light_view_projection_matrix)

        # 4. Itérer sur les sprites et les dessiner dans la shadow map
        print(f"Rendering shadow map for {len(sprites_to_cast_shadows)} sprites...")
        for sprite in sprites_to_cast_shadows:
            # Passer la matrice modèle du sprite (qui inclut sa position 3D)
            model_matrix = sprite.get_component('Transform').get_matrix()
            self.sprite_shadow_shader.set_uniform("u_modelMatrix", model_matrix)

            # Dessiner la géométrie du sprite (juste un quad généralement)
            # Le shader de vertex s'occupe de la transformation, le fragment shader est minimal.
            # renderer.draw_sprite_geometry(sprite.vao) # Appel de dessin simplifié
            self.draw_sprite_quad(sprite) # Simulation

        # 5. Délier le FBO
        self.shadow_map_fbo.unbind()
        # Restaurer le viewport original
        # graphics_api.restore_viewport()
        print("Sprite shadow map generated.")

    def _calculate_light_vp_matrix(self, light):
        """Calcule la matrice Vue-Projection pour la lumière donnée."""
        # Logique pour créer une projection orthographique ou perspective
        # basée sur la direction/position de la lumière et la zone de la scène à couvrir.
        # Ceci est souvent complexe et dépend de la taille de la scène visible par la caméra principale.
        print(f"Calculating VP matrix for light (direction: {light.direction})")
        # Simuler une matrice
        import numpy as np # Juste pour l'exemple
        # Matrice de vue regardant depuis la lumière vers l'origine (simplifié)
        light_pos = np.array(light.direction) * -100 # Position arbitraire le long de la direction inverse
        target = np.array([0, 0, 0])
        up = np.array([0, 1, 0])
        # Recalculer 'up' si la lumière pointe vers le haut/bas
        if np.abs(np.dot(light.direction, up)) > 0.99:
            up = np.array([0, 0, 1])
        # Construction simplifiée de la matrice de vue (lookAt)
        # ... (nécessite une bibliothèque de maths ou implémentation)

        # Projection orthographique (simplifiée)
        ortho_size = 50.0 # Taille de la zone couverte par l'ombre
        near_plane, far_plane = 1.0, 200.0
        # Construction simplifiée de la matrice ortho
        # ...

        # Combiner Vue * Projection
        # Pour la simulation, retourner une matrice identité
        return np.identity(4).tolist()


    def get_shadow_map_texture(self):
        """Retourne la texture de la shadow map générée."""
        return self.shadow_map_fbo.get_depth_texture() if self.shadow_map_fbo else None

    def get_light_vp_matrix(self):
        """Retourne la matrice Vue-Projection de la lumière utilisée pour la shadow map."""
        return self.light_view_projection_matrix

    def integrate_with_scene_rendering(self, scene_renderer):
        """
        Fournit les informations nécessaires (shadow map, matrice VP lumière)
        aux shaders de la scène 3D pour qu'ils puissent appliquer les ombres des sprites.
        """
        shadow_map_texture = self.get_shadow_map_texture()
        light_vp = self.get_light_vp_matrix()

        if shadow_map_texture and light_vp:
            print("Integrating sprite shadows into scene rendering.")
            # Passer ces informations aux shaders PBR/éclairage de la scène 3D
            # scene_renderer.set_global_uniform("u_spriteShadowMap", shadow_map_texture, unit=...)
            # scene_renderer.set_global_uniform("u_lightVPMatrixForSpriteShadows", light_vp)
            # scene_renderer.enable_feature("SPRITE_SHADOWS") # Activer le code de sampling dans les shaders 3D
        else:
            print("Skipping sprite shadow integration (missing data).")
            # scene_renderer.disable_feature("SPRITE_SHADOWS")

    # Méthodes utilitaires (simulation)
    def create_depth_fbo(self, width, height, name):
        print(f"    Creating Depth FBO '{name}' ({width}x{height})")
        class MockDepthFBO:
            def __init__(self, n): self.name = n
            def bind(self): pass # print(f"Binding Depth FBO {self.name}")
            def unbind(self): pass # print(f"Unbinding Depth FBO {self.name}")
            def get_depth_texture(self): return f"depth_texture_{self.name}"
            def delete(self): print(f"Deleting Depth FBO {self.name}")
        return MockDepthFBO(name)

    def draw_sprite_quad(self, sprite):
        # Simule le dessin de la géométrie du sprite
        pass

# Exemple d'utilisation (simulation)
if __name__ == '__main__':
    class MockShader:
        def use(self): pass
        def set_uniform(self, name, val): pass
    class MockShaderManager:
        def load_shader(self, name, vert_path, frag_path):
            print(f"Loading shader '{name}'...")
            return MockShader()
    class MockLight:
        direction = (0.5, -0.7, -0.5) # Exemple de direction
    class MockLightSystem:
        def get_main_directional_light(self): return MockLight()
    class MockTransform:
        def get_matrix(self): return [[1,0,0,0],[0,1,0,0],[0,0,1,0],[0,0,0,1]] # Identité
    class MockSprite:
        def __init__(self, id): self.id = id
        def get_component(self, name):
            if name == 'Transform': return MockTransform()
            return None

    shader_manager = MockShaderManager()
    light_system = MockLightSystem()
    shadow_manager = SpriteShadowManager(shader_manager, light_system)

    # Sprites de test
    sprites = [MockSprite(1), MockSprite(2)]

    # Générer la shadow map
    print("\nGenerating sprite shadow map...")
    shadow_manager.render_shadow_map(sprites)

    # Récupérer les infos pour le rendu de scène
    shadow_tex = shadow_manager.get_shadow_map_texture()
    light_matrix = shadow_manager.get_light_vp_matrix()
    print(f"\nShadow map texture: {shadow_tex}")
    # print(f"Light VP Matrix: {light_matrix}") # Matrix est longue

    # Intégration (conceptuel)
    # shadow_manager.integrate_with_scene_rendering(None) # Passer le renderer de scène