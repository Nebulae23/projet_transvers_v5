# src/engine/rendering/effects/sprite_bloom.py
"""
Implémente un effet de bloom spécifiquement conçu pour les sprites 2D stylisés,
permettant un contrôle fin sur l'apparence du halo lumineux autour des sprites.
"""

from .post_process_effect import PostProcessEffect # Suppose une classe de base

class SpriteBloomEffect(PostProcessEffect):
    def __init__(self, shader_manager, resolution):
        """
        Initialise l'effet de bloom pour sprites.

        Args:
            shader_manager: Gestionnaire pour charger les shaders de bloom.
            resolution (tuple): Résolution de la cible de rendu (largeur, hauteur).
        """
        super().__init__("sprite_bloom")
        self.shader_manager = shader_manager
        self.resolution = resolution
        self.bloom_extract_shader = None
        self.blur_shader = None
        self.bloom_combine_shader = None
        # Paramètres configurables du bloom
        self.threshold = 0.8  # Luminosité minimale pour déclencher le bloom
        self.intensity = 1.2  # Intensité du bloom ajouté
        self.blur_passes = 5  # Nombre de passes de flou gaussien
        self.radius = 0.005 # Rayon du flou (en fraction de la résolution)
        # Cibles de rendu intermédiaires (Framebuffers)
        self.bright_pass_target = None
        self.blur_targets = [] # Paire de FBOs pour le flou ping-pong
        self._load_shaders()
        self._create_render_targets()
        print(f"SpriteBloomEffect initialized with resolution {resolution}.")

    def _load_shaders(self):
        """Charge les shaders nécessaires pour les étapes du bloom."""
        try:
            # 1. Shader pour extraire les zones brillantes des sprites
            self.bloom_extract_shader = self.shader_manager.load_shader(
                "bloom_extract_sprite",
                # Chemins hypothétiques
                vert_path="src/engine/shaders/effects/fullscreen.vert", # Shader de vertex générique
                frag_path="src/engine/shaders/effects/bloom_extract_sprite.frag"
            )
            # 2. Shader pour le flou gaussien (peut être réutilisé)
            self.blur_shader = self.shader_manager.load_shader(
                "gaussian_blur",
                vert_path="src/engine/shaders/effects/fullscreen.vert",
                frag_path="src/engine/shaders/effects/gaussian_blur.frag"
            )
            # 3. Shader pour combiner l'image originale avec le bloom flouté
            self.bloom_combine_shader = self.shader_manager.load_shader(
                "bloom_combine",
                vert_path="src/engine/shaders/effects/fullscreen.vert",
                frag_path="src/engine/shaders/effects/bloom_combine.frag"
            )
            print("Sprite bloom shaders loaded successfully.")
        except Exception as e:
            print(f"Error loading sprite bloom shaders: {e}")
            # Gérer l'erreur, potentiellement désactiver l'effet

    def _create_render_targets(self):
        """Crée les framebuffers nécessaires pour les passes intermédiaires."""
        # Utiliser une résolution potentiellement réduite pour le bloom (performance)
        bloom_width = self.resolution[0] // 2
        bloom_height = self.resolution[1] // 2
        print(f"Creating bloom render targets at {bloom_width}x{bloom_height}")
        try:
            # Cible pour la passe d'extraction des hautes lumières
            self.bright_pass_target = self.create_fbo(bloom_width, bloom_height, "bright_pass_sprite")

            # Cibles pour le flou ping-pong
            self.blur_targets.append(self.create_fbo(bloom_width, bloom_height, "blur_sprite_0"))
            self.blur_targets.append(self.create_fbo(bloom_width, bloom_height, "blur_sprite_1"))
            print("Bloom render targets created.")
        except Exception as e:
            print(f"Error creating bloom render targets: {e}")
            # Gérer l'erreur

    def apply(self, source_texture, target_framebuffer, params=None):
        """
        Applique l'effet de bloom sur la texture source.

        Args:
            source_texture: La texture contenant les sprites rendus.
            target_framebuffer: Le framebuffer de destination final.
            params (dict, optional): Paramètres additionnels (ex: masque).

        Returns:
            Texture: La texture résultante (peut être celle de target_framebuffer).
        """
        if not all([self.bloom_extract_shader, self.blur_shader, self.bloom_combine_shader,
                    self.bright_pass_target, len(self.blur_targets) == 2]):
            print("Error: Sprite bloom effect not properly initialized. Skipping.")
            # Retourner la source ou blitter vers la cible sans modification
            self.blit(source_texture, target_framebuffer)
            return target_framebuffer.get_texture() # Méthode hypothétique

        print("Applying sprite bloom effect...")
        mask_texture = params.get('mask_texture') if params else None

        # 1. Extraire les zones brillantes (Threshold Pass)
        self.bright_pass_target.bind()
        self.bloom_extract_shader.use()
        self.bloom_extract_shader.set_texture("u_sourceTexture", source_texture, 0)
        self.bloom_extract_shader.set_uniform("u_threshold", self.threshold)
        if mask_texture:
             self.bloom_extract_shader.set_texture("u_maskTexture", mask_texture, 1)
             self.bloom_extract_shader.set_uniform("u_useMask", True)
        else:
             self.bloom_extract_shader.set_uniform("u_useMask", False)
        self.draw_fullscreen_quad()
        print(" - Bright pass completed.")

        # 2. Flouter les zones brillantes (Blur Passes - Ping-Pong)
        current_source = self.bright_pass_target.get_texture()
        horizontal = True
        for i in range(self.blur_passes * 2): # *2 car une passe horiz + une passe vert = 1 blur pass
            target_index = i % 2
            ping_pong_target = self.blur_targets[target_index]
            ping_pong_target.bind()
            self.blur_shader.use()
            self.blur_shader.set_texture("u_sourceTexture", current_source, 0)
            self.blur_shader.set_uniform("u_resolution", (ping_pong_target.width, ping_pong_target.height))
            self.blur_shader.set_uniform("u_radius", self.radius)
            self.blur_shader.set_uniform("u_horizontal", horizontal)
            self.draw_fullscreen_quad()
            current_source = ping_pong_target.get_texture()
            horizontal = not horizontal # Alterner direction
        blurred_texture = current_source # Le résultat final du flou
        print(f" - Blur passes ({self.blur_passes}) completed.")

        # 3. Combiner l'image originale avec le bloom flouté
        target_framebuffer.bind()
        self.bloom_combine_shader.use()
        self.bloom_combine_shader.set_texture("u_originalTexture", source_texture, 0)
        self.bloom_combine_shader.set_texture("u_bloomTexture", blurred_texture, 1)
        self.bloom_combine_shader.set_uniform("u_bloomIntensity", self.intensity)
        self.draw_fullscreen_quad()
        print(" - Combine pass completed.")

        target_framebuffer.unbind()
        print("Sprite bloom effect applied successfully.")
        return target_framebuffer.get_texture()

    def resize(self, new_resolution):
        """Met à jour la résolution et recrée les cibles de rendu."""
        print(f"Resizing SpriteBloomEffect to {new_resolution}")
        self.resolution = new_resolution
        # Nettoyer les anciennes cibles
        self.bright_pass_target.delete() # Méthode hypothétique
        for target in self.blur_targets:
            target.delete()
        self.blur_targets = []
        # Recréer avec la nouvelle résolution
        self._create_render_targets()

    # Méthodes utilitaires (devraient être dans une classe de base ou un helper)
    def create_fbo(self, width, height, name):
        # Logique de création de Framebuffer Object (OpenGL, Vulkan, etc.)
        print(f"    Creating FBO '{name}' ({width}x{height})")
        # Simuler la création
        class MockFBO:
            def __init__(self, w, h, n): self.width, self.height, self.name = w, h, n
            def bind(self): pass # print(f"Binding FBO {self.name}")
            def unbind(self): pass # print(f"Unbinding FBO {self.name}")
            def get_texture(self): return f"texture_{self.name}"
            def delete(self): print(f"Deleting FBO {self.name}")
        return MockFBO(width, height, name)

    def draw_fullscreen_quad(self):
        # Logique pour dessiner un quad qui couvre tout l'écran
        # print("Drawing fullscreen quad...")
        pass

    def blit(self, source_texture, target_framebuffer):
        # Logique pour copier une texture vers un framebuffer
        print(f"Blitting {source_texture} to {target_framebuffer.name}")
        pass

# Exemple d'utilisation (simulation)
if __name__ == '__main__':
    class MockShader:
        def use(self): pass
        def set_texture(self, name, tex, unit): pass # print(f"SetTex {name}={tex} U{unit}")
        def set_uniform(self, name, val): pass # print(f"SetUni {name}={val}")
    class MockShaderManager:
        def load_shader(self, name, vert_path, frag_path):
            print(f"Loading shader '{name}'...")
            return MockShader()

    resolution = (1280, 720)
    shader_manager = MockShaderManager()
    bloom_effect = SpriteBloomEffect(shader_manager, resolution)

    # Simuler l'application
    source_tex = "sprite_render_output"
    final_target_fbo = bloom_effect.create_fbo(resolution[0], resolution[1], "final_output")
    result_texture = bloom_effect.apply(source_tex, final_target_fbo, params={'mask_texture': 'sprite_mask.png'})
    print(f"\nBloom effect finished. Result in texture: {result_texture}")

    # Simuler redimensionnement
    # bloom_effect.resize((1920, 1080))