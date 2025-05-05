# src/engine/rendering/integration/environment_blender.py
"""
Combine le rendu final des sprites 2D avec la scène 3D rendue
pour créer l'image composite finale, en assurant une intégration visuelle
harmonieuse (mélange, profondeur, etc.).
"""

class EnvironmentBlender:
    def __init__(self, shader_manager):
        """
        Initialise le mélangeur d'environnement.

        Args:
            shader_manager: Le gestionnaire de shaders pour charger le shader de composition.
        """
        self.shader_manager = shader_manager
        self.composition_shader = None
        self._load_shaders()
        print("EnvironmentBlender initialized.")

    def _load_shaders(self):
        """Charge le shader nécessaire pour la composition finale."""
        try:
            # Ce shader prendra en entrée la texture de la scène 3D rendue
            # et la texture des sprites rendus (potentiellement avec effets)
            # ainsi que les buffers de profondeur respectifs pour gérer l'occlusion.
            self.composition_shader = self.shader_manager.load_shader(
                "sprite_environment_composition",
                # Ces chemins sont hypothétiques, les shaders devront être créés
                vert_path="src/engine/shaders/integration/composition.vert",
                frag_path="src/engine/shaders/integration/composition.frag"
            )
            print("Composition shader loaded successfully.")
        except Exception as e:
            print(f"Error loading composition shader: {e}")
            self.composition_shader = None # Fallback

    def blend(self, scene_3d_texture, sprites_texture, depth_3d_texture, depth_sprites_texture, target_framebuffer):
        """
        Effectue l'opération de mélange entre la scène 3D et les sprites.

        Args:
            scene_3d_texture: Texture contenant le rendu final de la scène 3D.
            sprites_texture: Texture contenant le rendu final des sprites (avec effets).
            depth_3d_texture: Texture de profondeur de la scène 3D.
            depth_sprites_texture: Texture de profondeur générée pour les sprites (peut être la même que depth_3d si rendu intégré).
            target_framebuffer: Le framebuffer où écrire l'image finale composée.
        """
        if not self.composition_shader:
            print("Error: Composition shader not available. Cannot blend.")
            # Peut-être copier juste la scène 3D comme fallback ?
            # self.blit(scene_3d_texture, target_framebuffer)
            return

        print("Blending 3D scene and sprites...")

        # 1. Activer le framebuffer cible
        target_framebuffer.bind() # Méthode hypothétique

        # 2. Activer le shader de composition
        self.composition_shader.use()

        # 3. Lier les textures d'entrée aux unités de texture appropriées
        self.composition_shader.set_texture("u_scene3DTexture", scene_3d_texture, unit=0)
        self.composition_shader.set_texture("u_spritesTexture", sprites_texture, unit=1)
        self.composition_shader.set_texture("u_sceneDepthTexture", depth_3d_texture, unit=2)
        self.composition_shader.set_texture("u_spriteDepthTexture", depth_sprites_texture, unit=3)

        # 4. Passer d'autres uniforms si nécessaire (ex: résolution, temps)
        # self.composition_shader.set_uniform("u_resolution", target_framebuffer.resolution)

        # 5. Dessiner un quad plein écran pour exécuter le shader de composition
        #    Le VAO/VBO pour un quad plein écran est généralement géré par le renderer ou post-processor.
        #    renderer.draw_fullscreen_quad()

        print(f"Scene and sprites blended into target: {target_framebuffer}")

        # 6. Délier le framebuffer
        target_framebuffer.unbind() # Méthode hypothétique

    def integrate_into_pipeline(self, render_pipeline):
        """
        Définit où cette étape de mélange s'insère dans le pipeline de rendu global.
        """
        # Cette étape intervient généralement après le rendu de la scène 3D
        # et après le rendu (et les effets) des sprites. C'est souvent l'une
        # des dernières étapes avant les effets de post-processing finaux comme
        # le tone mapping ou l'anti-aliasing final (FXAA/TAA).
        print("Integrating environment blending step into the main pipeline.")
        # Exemple:
        # render_pipeline.add_step(
        #     "compose_scene_sprites",
        #     self.blend_callback, # Une fonction qui appelle self.blend avec les bonnes textures
        #     depends_on=["render_scene_3d", "render_sprites_with_effects"],
        #     outputs=["final_composite_texture"]
        # )

    def blend_callback(self, inputs, outputs):
        """Fonction de rappel pour l'intégration pipeline."""
        # Récupérer les textures depuis les étapes précédentes
        scene_tex = inputs["render_scene_3d"].get_output_texture("color")
        sprite_tex = inputs["render_sprites_with_effects"].get_output_texture("color")
        scene_depth = inputs["render_scene_3d"].get_output_texture("depth")
        sprite_depth = inputs["render_sprites"].get_output_texture("depth") # Ou une autre source

        target_fb = outputs["final_composite_texture"].framebuffer # Ou obtenir le FB cible

        self.blend(scene_tex, sprite_tex, scene_depth, sprite_depth, target_fb)


# Exemple d'utilisation (simulation)
if __name__ == '__main__':
    class MockShader:
        def use(self): pass
        def set_texture(self, name, texture, unit): print(f"Set texture uniform {name} = {texture} (unit {unit})")
        def set_uniform(self, name, value): pass
    class MockShaderManager:
        def load_shader(self, name, vert_path, frag_path):
            print(f"Loading shader '{name}' from {vert_path}, {frag_path}")
            return MockShader() # Simule succès
    class MockFramebuffer:
        def __init__(self, name): self.name = name
        def bind(self): print(f"Binding framebuffer: {self.name}")
        def unbind(self): print(f"Unbinding framebuffer: {self.name}")
        @property
        def resolution(self): return (1920, 1080)

    # Initialisation
    shader_manager = MockShaderManager()
    blender = EnvironmentBlender(shader_manager)

    # Simulation de l'opération de mélange
    print("\nSimulating blending operation...")
    scene_texture = "render_output_3d.png"
    sprites_texture = "render_output_sprites_fx.png"
    depth_3d = "depth_buffer_3d.depth"
    depth_sprites = "depth_buffer_sprites.depth" # Peut être identique à depth_3d
    final_target = MockFramebuffer("final_output_buffer")

    blender.blend(scene_texture, sprites_texture, depth_3d, depth_sprites, final_target)

    # Simulation de l'intégration (conceptuel)
    # blender.integrate_into_pipeline(None)