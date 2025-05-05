# src/engine/rendering/effects/depth_of_field.py
"""
Implémente un effet de profondeur de champ (Depth of Field - DoF)
qui fonctionne avec la scène composite 2D/3D, en floutant les zones
hors focus tout en respectant la profondeur des sprites intégrés.
"""

from .post_process_effect import PostProcessEffect # Suppose une classe de base

class DepthOfFieldEffect(PostProcessEffect):
    def __init__(self, shader_manager, resolution):
        """
        Initialise l'effet de profondeur de champ.

        Args:
            shader_manager: Gestionnaire pour charger les shaders DoF.
            resolution (tuple): Résolution de la cible de rendu (largeur, hauteur).
        """
        super().__init__("depth_of_field")
        self.shader_manager = shader_manager
        self.resolution = resolution
        self.dof_shader = None
        # Paramètres DoF configurables
        self.focus_distance = 10.0 # Distance du plan de focus net
        self.focus_range = 5.0    # Plage autour de la distance de focus qui reste nette
        self.max_blur_radius = 8.0 # Rayon maximum du flou (en pixels) - influence la qualité/performance
        self.bokeh_shape = "hexagon" # Ou "circle", etc. (influence le shader)
        self._load_shaders()
        # Pas de FBO intermédiaire nécessaire pour un DoF simple en une passe,
        # mais pourrait être requis pour des techniques Bokeh plus avancées.
        print(f"DepthOfFieldEffect initialized with resolution {resolution}.")

    def _load_shaders(self):
        """Charge le shader nécessaire pour l'effet DoF."""
        try:
            # Le shader DoF utilise la texture de profondeur pour déterminer
            # le niveau de flou à appliquer à chaque pixel de l'image source.
            # Il peut implémenter différentes techniques (Gaussian, Bokeh).
            # Le nom du fragment shader pourrait dépendre de self.bokeh_shape
            shader_name = f"dof_{self.bokeh_shape}" # Ex: dof_hexagon
            frag_shader_path = f"src/engine/shaders/effects/{shader_name}.frag" # Hypothétique

            self.dof_shader = self.shader_manager.load_shader(
                shader_name,
                vert_path="src/engine/shaders/effects/fullscreen.vert", # Générique
                frag_path=frag_shader_path
            )
            print(f"Depth of Field shader ({shader_name}) loaded successfully.")
        except Exception as e:
            print(f"Error loading Depth of Field shader: {e}")
            self.dof_shader = None

    def set_focus(self, distance, range):
        """
        Met à jour les paramètres de focus.

        Args:
            distance (float): Nouvelle distance de focus.
            range (float): Nouvelle plage de focus net.
        """
        self.focus_distance = distance
        self.focus_range = range
        print(f"DoF focus updated: distance={distance}, range={range}")

    def apply(self, source_texture, depth_texture, target_framebuffer, camera_params):
        """
        Applique l'effet de profondeur de champ.

        Args:
            source_texture: Texture de la scène composite (3D + sprites).
            depth_texture: Texture de profondeur combinée (ou de la scène principale).
            target_framebuffer: Framebuffer de destination.
            camera_params (dict): Dictionnaire contenant les paramètres de la caméra
                                  nécessaires pour reconstruire la position depuis la profondeur
                                  (ex: near_plane, far_plane, projection_matrix).

        Returns:
            Texture: La texture résultante (celle de target_framebuffer).
        """
        if not self.dof_shader:
            print("Error: Depth of Field effect not properly initialized. Skipping.")
            self.blit(source_texture, target_framebuffer) # Copie simple
            return target_framebuffer.get_texture()

        print("Applying Depth of Field effect...")

        target_framebuffer.bind()
        self.dof_shader.use()

        # Lier les textures
        self.dof_shader.set_texture("u_sourceTexture", source_texture, 0)
        self.dof_shader.set_texture("u_depthTexture", depth_texture, 1)

        # Passer les paramètres DoF et caméra au shader
        self.dof_shader.set_uniform("u_focusDistance", self.focus_distance)
        self.dof_shader.set_uniform("u_focusRange", self.focus_range)
        self.dof_shader.set_uniform("u_maxBlurRadius", self.max_blur_radius)
        self.dof_shader.set_uniform("u_resolution", self.resolution)

        # Paramètres caméra pour la reconstruction de la position/distance linéaire
        self.dof_shader.set_uniform("u_cameraNear", camera_params.get('near', 0.1))
        self.dof_shader.set_uniform("u_cameraFar", camera_params.get('far', 1000.0))
        # Le shader pourrait avoir besoin de l'inverse de la matrice de projection
        # ou d'autres informations selon la méthode de reconstruction de la profondeur.
        # inv_proj_matrix = camera_params.get('inverse_projection_matrix')
        # self.dof_shader.set_uniform("u_inverseProjectionMatrix", inv_proj_matrix)

        self.draw_fullscreen_quad()
        target_framebuffer.unbind()

        print("Depth of Field effect applied successfully.")
        return target_framebuffer.get_texture()

    def resize(self, new_resolution):
        """Met à jour la résolution."""
        print(f"Resizing DepthOfFieldEffect to {new_resolution}")
        self.resolution = new_resolution
        # Pas de FBO à recréer pour la version simple

    # Méthodes utilitaires (simulation)
    def draw_fullscreen_quad(self):
        pass
    def blit(self, source_texture, target_framebuffer):
        print(f"Blitting {source_texture} to {target_framebuffer.name}")
        pass
    # Simuler FBO pour l'exemple
    class MockFBO:
        def __init__(self, name): self.name = name
        def bind(self): pass
        def unbind(self): pass
        def get_texture(self): return f"texture_{self.name}"

# Exemple d'utilisation (simulation)
if __name__ == '__main__':
    class MockShader:
        def use(self): pass
        def set_texture(self, name, tex, unit): pass
        def set_uniform(self, name, val): pass
    class MockShaderManager:
        def load_shader(self, name, vert_path, frag_path):
            print(f"Loading shader '{name}' from {frag_path}...")
            # Simuler le chargement réussi
            if "dof" in name:
                return MockShader()
            raise FileNotFoundError(f"Shader not found: {frag_path}")

    resolution = (1280, 720)
    shader_manager = MockShaderManager()
    dof_effect = DepthOfFieldEffect(shader_manager, resolution)

    # Simuler l'application
    source_tex = "composite_scene_sprites.png"
    depth_tex = "combined_depth_buffer.depth"
    final_target_fbo = dof_effect.MockFBO("final_output_dof") # Utilise la classe interne pour simuler

    # Paramètres caméra simulés
    cam_params = {
        'near': 0.1,
        'far': 500.0,
        # 'inverse_projection_matrix': [...] # Matrice 4x4
    }

    # Appliquer l'effet avec les paramètres par défaut
    print("\nApplying DoF with default settings...")
    result_texture = dof_effect.apply(source_tex, depth_tex, final_target_fbo, cam_params)
    print(f"DoF effect finished. Result in texture: {result_texture}")

    # Changer le focus et réappliquer
    dof_effect.set_focus(distance=5.0, range=2.0)
    print("\nApplying DoF with updated focus...")
    result_texture = dof_effect.apply(source_tex, depth_tex, final_target_fbo, cam_params)
    print(f"DoF effect finished. Result in texture: {result_texture}")

    # Simuler redimensionnement
    # dof_effect.resize((1920, 1080))