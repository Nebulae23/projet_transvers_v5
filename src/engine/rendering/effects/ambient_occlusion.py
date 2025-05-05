# src/engine/rendering/effects/ambient_occlusion.py
"""
Implémente l'occlusion ambiante en espace écran (SSAO - Screen Space Ambient Occlusion)
adaptée à une scène contenant à la fois des éléments 3D et des sprites 2D intégrés.
"""

import random
import numpy as np # Pour la génération des échantillons et potentiellement les FBOs

from .post_process_effect import PostProcessEffect # Suppose une classe de base

class AmbientOcclusionEffect(PostProcessEffect):
    def __init__(self, shader_manager, resolution, use_normals=True):
        """
        Initialise l'effet SSAO.

        Args:
            shader_manager: Gestionnaire pour charger les shaders SSAO.
            resolution (tuple): Résolution de la cible de rendu (largeur, hauteur).
            use_normals (bool): Indique si un G-Buffer avec normales est disponible et doit être utilisé.
        """
        super().__init__("ambient_occlusion")
        self.shader_manager = shader_manager
        self.resolution = resolution
        self.use_normals = use_normals # Si True, attend une texture de normales en entrée
        self.ssao_gen_shader = None
        self.ssao_blur_shader = None
        self.ssao_apply_shader = None # Optionnel: si l'application est une passe séparée

        # Paramètres SSAO configurables
        self.kernel_size = 32      # Nombre d'échantillons pour calculer l'occlusion
        self.radius = 0.5          # Rayon de recherche d'occlusion dans l'espace vue
        self.bias = 0.025          # Pour éviter l'auto-occlusion sur surfaces planes
        self.intensity = 1.0       # Force de l'effet SSAO
        self.blur_radius = 2       # Rayon du flou appliqué à la texture SSAO (en pixels)

        # Ressources SSAO
        self.ssao_kernel = self._generate_ssao_kernel(self.kernel_size)
        self.noise_texture = self._generate_noise_texture(4) # Texture 4x4 pour la rotation des échantillons

        # Cibles de rendu intermédiaires
        self.ssao_raw_target = None # FBO pour le calcul SSAO initial
        self.ssao_blur_target = None # FBO pour le SSAO flouté

        self._load_shaders()
        self._create_render_targets()
        print(f"AmbientOcclusionEffect initialized (Use Normals: {self.use_normals}).")

    def _generate_ssao_kernel(self, size):
        """Génère le noyau d'échantillons hémisphériques pour SSAO."""
        kernel = []
        for i in range(size):
            # Échantillons dans un hémisphère orienté Z+
            sample = np.array([
                random.uniform(-1.0, 1.0),
                random.uniform(-1.0, 1.0),
                random.uniform(0.0, 1.0) # Hémisphère Z+
            ])
            sample = sample / np.linalg.norm(sample) # Normaliser
            # Répartir les échantillons de manière à ce qu'ils soient plus proches du centre
            scale = float(i) / float(size)
            scale = 0.1 + 0.9 * scale * scale # lerp(0.1, 1.0, scale*scale)
            sample *= scale
            kernel.append(sample.tolist())
        print(f"Generated SSAO kernel with {size} samples.")
        return kernel

    def _generate_noise_texture(self, size):
        """Génère une petite texture de bruit pour faire tourner le noyau SSAO."""
        noise_data = np.zeros((size, size, 3), dtype=np.float32)
        for i in range(size):
            for j in range(size):
                noise_data[i, j, 0] = random.uniform(-1.0, 1.0)
                noise_data[i, j, 1] = random.uniform(-1.0, 1.0)
                noise_data[i, j, 2] = 0.0 # Z non utilisé, juste besoin d'un vecteur de rotation XY
        print(f"Generated {size}x{size} SSAO noise texture.")
        # Ici, il faudrait créer une vraie texture GPU à partir de noise_data
        # Pour la simulation, on retourne juste les données ou un mock.
        class MockNoiseTexture: pass
        return MockNoiseTexture() # Remplacer par la vraie création de texture

    def _load_shaders(self):
        """Charge les shaders nécessaires pour les étapes SSAO."""
        try:
            # 1. Shader pour générer la carte d'occlusion
            gen_frag = "ssao_gen_gbuffer.frag" if self.use_normals else "ssao_gen_depth_only.frag"
            self.ssao_gen_shader = self.shader_manager.load_shader(
                "ssao_generate",
                vert_path="src/engine/shaders/effects/fullscreen.vert",
                frag_path=f"src/engine/shaders/effects/{gen_frag}" # Chemin hypothétique
            )
            # 2. Shader pour flouter la carte SSAO (souvent bilatéral ou gaussien simple)
            self.ssao_blur_shader = self.shader_manager.load_shader(
                "ssao_blur",
                vert_path="src/engine/shaders/effects/fullscreen.vert",
                frag_path="src/engine/shaders/effects/ssao_blur.frag" # Chemin hypothétique
            )
            # 3. Shader pour appliquer l'occlusion (peut être intégré au shader d'éclairage principal)
            # self.ssao_apply_shader = ...
            print("SSAO shaders loaded successfully.")
        except Exception as e:
            print(f"Error loading SSAO shaders: {e}")

    def _create_render_targets(self):
        """Crée les framebuffers pour les passes SSAO."""
        # Utiliser la pleine résolution ou une demi-résolution pour la performance
        ssao_width = self.resolution[0] # // 2
        ssao_height = self.resolution[1] # // 2
        print(f"Creating SSAO render targets at {ssao_width}x{ssao_height}")
        try:
            # Cible pour SSAO brut (format R8 ou R16F typiquement)
            self.ssao_raw_target = self.create_fbo(ssao_width, ssao_height, "ssao_raw", format="R8")
            # Cible pour SSAO flouté (même format)
            self.ssao_blur_target = self.create_fbo(ssao_width, ssao_height, "ssao_blur", format="R8")
            print("SSAO render targets created.")
        except Exception as e:
            print(f"Error creating SSAO render targets: {e}")

    def apply(self, source_color_texture, depth_texture, normal_texture, camera_params, target_framebuffer):
        """
        Applique l'effet SSAO.

        Args:
            source_color_texture: Texture couleur de la scène (avant éclairage ambiant si possible).
            depth_texture: Texture de profondeur combinée (3D + sprites).
            normal_texture: Texture des normales (du G-Buffer, si use_normals=True). Peut être None.
            camera_params (dict): Paramètres caméra (matrices projection/vue, near/far).
            target_framebuffer: Framebuffer de destination final.

        Returns:
            Texture: La texture résultante (celle de target_framebuffer ou une texture intermédiaire
                     si l'application se fait dans une passe d'éclairage ultérieure).
                     Retourne souvent la texture SSAO floutée pour être utilisée par le shader d'éclairage.
        """
        if not self.ssao_gen_shader or not self.ssao_blur_shader or \
           not self.ssao_raw_target or not self.ssao_blur_target or \
           (self.use_normals and not normal_texture):
            print("Error: SSAO effect not properly initialized or missing inputs. Skipping.")
            # Si l'application est une passe séparée, on blit la source.
            # Sinon, on retourne None ou une texture blanche pour indiquer pas d'occlusion.
            # self.blit(source_color_texture, target_framebuffer)
            # return target_framebuffer.get_texture()
            return self.get_fallback_occlusion_texture() # Texture blanche

        print("Applying SSAO effect...")

        # --- Passe 1: Génération SSAO ---
        self.ssao_raw_target.bind()
        self.ssao_gen_shader.use()
        # Textures
        self.ssao_gen_shader.set_texture("u_depthTexture", depth_texture, 0)
        if self.use_normals:
            self.ssao_gen_shader.set_texture("u_normalTexture", normal_texture, 1)
        self.ssao_gen_shader.set_texture("u_noiseTexture", self.noise_texture, 2)
        # Paramètres SSAO
        self.ssao_gen_shader.set_uniform_array("u_ssaoKernel", self.ssao_kernel)
        self.ssao_gen_shader.set_uniform("u_kernelSize", self.kernel_size)
        self.ssao_gen_shader.set_uniform("u_radius", self.radius)
        self.ssao_gen_shader.set_uniform("u_bias", self.bias)
        self.ssao_gen_shader.set_uniform("u_resolution", (self.ssao_raw_target.width, self.ssao_raw_target.height))
        noise_scale_x = self.resolution[0] / self.noise_texture.width # Assumer que noise_texture a width/height
        noise_scale_y = self.resolution[1] / self.noise_texture.height
        self.ssao_gen_shader.set_uniform("u_noiseScale", (noise_scale_x, noise_scale_y))
        # Paramètres Caméra (Projection est souvent nécessaire pour reconstruire la position vue)
        self.ssao_gen_shader.set_uniform("u_projectionMatrix", camera_params['projection_matrix'])
        # self.ssao_gen_shader.set_uniform("u_inverseProjectionMatrix", camera_params['inverse_projection_matrix']) # Alternative
        # self.ssao_gen_shader.set_uniform("u_viewMatrix", camera_params['view_matrix']) # Si calcul en espace monde

        self.draw_fullscreen_quad()
        print(" - SSAO generation pass completed.")

        # --- Passe 2: Flou SSAO ---
        self.ssao_blur_target.bind()
        self.ssao_blur_shader.use()
        self.ssao_blur_shader.set_texture("u_ssaoInput", self.ssao_raw_target.get_texture(), 0)
        self.ssao_blur_shader.set_uniform("u_blurRadius", self.blur_radius)
        self.ssao_blur_shader.set_uniform("u_resolution", (self.ssao_blur_target.width, self.ssao_blur_target.height))
        # Un flou bilatéral aurait besoin de la texture de profondeur aussi
        # self.ssao_blur_shader.set_texture("u_depthTexture", depth_texture, 1)

        self.draw_fullscreen_quad()
        print(" - SSAO blur pass completed.")

        # --- Passe 3: Application (Optionnelle ici) ---
        # L'application se fait souvent dans le shader d'éclairage principal en multipliant
        # la composante ambiante par la texture SSAO floutée.
        # Si on devait le faire ici comme passe séparée :
        # target_framebuffer.bind()
        # self.ssao_apply_shader.use()
        # self.ssao_apply_shader.set_texture("u_sourceColor", source_color_texture, 0)
        # self.ssao_apply_shader.set_texture("u_ssaoTexture", self.ssao_blur_target.get_texture(), 1)
        # self.ssao_apply_shader.set_uniform("u_ssaoIntensity", self.intensity)
        # self.draw_fullscreen_quad()
        # print(" - SSAO application pass completed.")
        # return target_framebuffer.get_texture()

        # Retourner la texture SSAO floutée pour utilisation ultérieure
        blurred_ssao_texture = self.ssao_blur_target.get_texture()
        print(f"SSAO effect generated. Returning blurred texture: {blurred_ssao_texture}")
        return blurred_ssao_texture


    def resize(self, new_resolution):
        """Met à jour la résolution et recrée les cibles de rendu."""
        print(f"Resizing AmbientOcclusionEffect to {new_resolution}")
        self.resolution = new_resolution
        # Nettoyer
        if self.ssao_raw_target: self.ssao_raw_target.delete()
        if self.ssao_blur_target: self.ssao_blur_target.delete()
        # Recréer
        self._create_render_targets()
        # La texture de bruit n'a généralement pas besoin d'être redimensionnée

    def get_fallback_occlusion_texture(self):
        """Retourne une texture indiquant une occlusion nulle (blanc)."""
        # Devrait retourner une texture 1x1 blanche statique
        return "white_texture_placeholder"

    # Méthodes utilitaires (simulation)
    def create_fbo(self, width, height, name, format="RGBA8"):
        print(f"    Creating FBO '{name}' ({width}x{height}, Format: {format})")
        class MockFBO:
            def __init__(self, w, h, n): self.width, self.height, self.name = w, h, n
            def bind(self): pass
            def unbind(self): pass
            def get_texture(self): return f"texture_{self.name}_{format}"
            def delete(self): print(f"Deleting FBO {self.name}")
        fbo = MockFBO(width, height, name)
        # Simuler l'attachement de texture
        fbo.texture = fbo.get_texture()
        return fbo

    def draw_fullscreen_quad(self): pass
    def blit(self, source_texture, target_framebuffer): pass

# Exemple d'utilisation (simulation)
if __name__ == '__main__':
    class MockShader:
        def use(self): pass
        def set_texture(self, name, tex, unit): pass
        def set_uniform(self, name, val): pass
        def set_uniform_array(self, name, val): pass
    class MockShaderManager:
        def load_shader(self, name, vert_path, frag_path):
            print(f"Loading shader '{name}' from {frag_path}...")
            if "ssao" in name or "fullscreen" in name: return MockShader()
            raise FileNotFoundError(f"Shader not found: {frag_path}")
    class MockTexture:
        def __init__(self, name): self.name = name
        @property
        def width(self): return 4 # Pour la texture de bruit
        @property
        def height(self): return 4

    resolution = (1280, 720)
    shader_manager = MockShaderManager()
    # Simuler avec et sans normales
    ssao_effect_gbuf = AmbientOcclusionEffect(shader_manager, resolution, use_normals=True)
    ssao_effect_depth = AmbientOcclusionEffect(shader_manager, resolution, use_normals=False)

    # Simuler l'application (version G-Buffer)
    source_color = MockTexture("scene_color")
    depth_tex = MockTexture("combined_depth")
    normal_tex = MockTexture("gbuffer_normals")
    final_target_fbo = ssao_effect_gbuf.create_fbo(resolution[0], resolution[1], "final_output_ssao")
    cam_params = {'projection_matrix': np.identity(4).tolist()} # Matrice identité pour sim

    print("\nApplying SSAO (G-Buffer version)...")
    ssao_result_texture = ssao_effect_gbuf.apply(source_color, depth_tex, normal_tex, cam_params, final_target_fbo)
    print(f"SSAO (G-Buffer) finished. Result texture for lighting: {ssao_result_texture}")

    print("\nApplying SSAO (Depth-Only version)...")
    ssao_result_texture_depth = ssao_effect_depth.apply(source_color, depth_tex, None, cam_params, final_target_fbo)
    print(f"SSAO (Depth-Only) finished. Result texture for lighting: {ssao_result_texture_depth}")

    # Simuler redimensionnement
    # ssao_effect_gbuf.resize((1920, 1080))