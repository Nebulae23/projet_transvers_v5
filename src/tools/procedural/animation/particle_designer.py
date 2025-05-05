# Placeholder for designing and generating particle effects
# TODO: Implement parameters and logic for various particle behaviors

import random
import math

class ParticleEmitterConfig:
    """Configuration for a particle emitter."""
    def __init__(self, name="default_emitter"):
        self.name = name
        # Emission properties
        self.emission_rate = 100 # Particles per second
        self.max_particles = 1000
        self.emitter_type = 'point' # point, sphere, box
        self.emitter_shape_params = {} # e.g., radius for sphere, size for box

        # Particle lifetime
        self.lifetime_min = 1.0
        self.lifetime_max = 3.0

        # Particle initial properties
        self.start_color_min = (1.0, 1.0, 1.0, 1.0)
        self.start_color_max = (1.0, 1.0, 1.0, 1.0)
        self.end_color_min = (1.0, 1.0, 1.0, 0.0)
        self.end_color_max = (1.0, 1.0, 1.0, 0.0)

        self.start_size_min = 0.1
        self.start_size_max = 0.3
        self.end_size_min = 0.0
        self.end_size_max = 0.0

        self.start_speed_min = 1.0
        self.start_speed_max = 5.0
        self.start_angle_min = -math.pi / 4 # Radians
        self.start_angle_max = math.pi / 4

        # Particle physics/forces
        self.gravity = (0, -9.81, 0)
        self.drag = 0.1
        self.noise_strength = 0.0
        self.noise_frequency = 1.0

        # Texture/Rendering
        self.texture_path = "particles/default.png"
        self.blend_mode = "additive" # additive, alpha

    def randomize_lifetime(self):
        return random.uniform(self.lifetime_min, self.lifetime_max)

    def randomize_start_color(self):
        return tuple(random.uniform(self.start_color_min[i], self.start_color_max[i]) for i in range(4))

    def randomize_end_color(self):
         return tuple(random.uniform(self.end_color_min[i], self.end_color_max[i]) for i in range(4))

    def randomize_start_size(self):
        return random.uniform(self.start_size_min, self.start_size_max)

    def randomize_end_size(self):
        return random.uniform(self.end_size_min, self.end_size_max)

    def randomize_start_velocity(self):
        speed = random.uniform(self.start_speed_min, self.start_speed_max)
        angle = random.uniform(self.start_angle_min, self.start_angle_max)
        # Assuming 2D for simplicity here, adapt for 3D
        vx = speed * math.cos(angle)
        vy = speed * math.sin(angle)
        return (vx, vy, 0) # Return as 3D vector

    def save_to_file(self, path):
        """Saves the emitter configuration to a file (e.g., JSON, YAML)."""
        print(f"Saving particle emitter config '{self.name}' to {path}...")
        # TODO: Implement serialization (e.g., using json module)
        import json
        try:
            with open(path, 'w') as f:
                # Convert tuples to lists for JSON compatibility
                config_dict = {k: (list(v) if isinstance(v, tuple) else v) for k, v in self.__dict__.items()}
                json.dump(config_dict, f, indent=4)
            print("Save successful.")
        except Exception as e:
            print(f"Error saving config: {e}")


    @classmethod
    def load_from_file(cls, path):
        """Loads an emitter configuration from a file."""
        print(f"Loading particle emitter config from {path}...")
        # TODO: Implement deserialization
        import json
        try:
            with open(path, 'r') as f:
                config_dict = json.load(f)
            emitter = cls(name=config_dict.get('name', 'loaded_emitter'))
            for key, value in config_dict.items():
                 # Convert lists back to tuples where appropriate (e.g., colors, gravity)
                 if key in ['start_color_min', 'start_color_max', 'end_color_min', 'end_color_max', 'gravity']:
                     setattr(emitter, key, tuple(value))
                 elif hasattr(emitter, key):
                     setattr(emitter, key, value)
            print("Load successful.")
            return emitter
        except Exception as e:
            print(f"Error loading config: {e}")
            return None


def create_fire_effect():
    """Creates a configuration preset for a fire effect."""
    fire = ParticleEmitterConfig("fire_effect")
    fire.emission_rate = 200
    fire.lifetime_min = 0.5
    fire.lifetime_max = 1.5
    fire.start_color_min = (1.0, 0.5, 0.0, 1.0) # Orange/Yellow
    fire.start_color_max = (1.0, 0.8, 0.2, 1.0)
    fire.end_color_min = (0.5, 0.0, 0.0, 0.0)   # Dark red, fades out
    fire.end_color_max = (0.8, 0.2, 0.0, 0.0)
    fire.start_size_min = 0.2
    fire.start_size_max = 0.5
    fire.end_size_min = 0.05
    fire.end_size_max = 0.1
    fire.start_speed_min = 0.5
    fire.start_speed_max = 2.0
    fire.start_angle_min = -math.pi / 16 # Narrow upward cone
    fire.start_angle_max = math.pi / 16
    fire.gravity = (0, 2.0, 0) # Slight upward force initially
    fire.drag = 0.05
    fire.texture_path = "particles/flame.png"
    fire.blend_mode = "additive"
    print("Fire effect preset created.")
    return fire

def create_smoke_effect():
     """Creates a configuration preset for a smoke effect."""
     smoke = ParticleEmitterConfig("smoke_effect")
     smoke.emission_rate = 50
     smoke.lifetime_min = 2.0
     smoke.lifetime_max = 5.0
     smoke.start_color_min = (0.5, 0.5, 0.5, 0.8) # Gray
     smoke.start_color_max = (0.8, 0.8, 0.8, 0.9)
     smoke.end_color_min = (0.2, 0.2, 0.2, 0.0)   # Darker gray, fades out
     smoke.end_color_max = (0.4, 0.4, 0.4, 0.0)
     smoke.start_size_min = 0.5
     smoke.start_size_max = 1.5
     smoke.end_size_min = 2.0 # Smoke expands
     smoke.end_size_max = 4.0
     smoke.start_speed_min = 0.2
     smoke.start_speed_max = 1.0
     smoke.start_angle_min = -math.pi / 8
     smoke.start_angle_max = math.pi / 8
     smoke.gravity = (0, 1.0, 0) # Rises slowly
     smoke.drag = 0.1
     smoke.noise_strength = 0.5 # Add some turbulence
     smoke.noise_frequency = 0.5
     smoke.texture_path = "particles/smoke_puff.png"
     smoke.blend_mode = "alpha"
     print("Smoke effect preset created.")
     return smoke


if __name__ == '__main__':
    # Example usage
    fire_config = create_fire_effect()
    smoke_config = create_smoke_effect()

    # Simulate saving and loading
    fire_config.save_to_file("fire_particle_config.json")
    loaded_fire = ParticleEmitterConfig.load_from_file("fire_particle_config.json")

    if loaded_fire:
        print(f"Loaded emitter name: {loaded_fire.name}")
        print(f"Loaded gravity: {loaded_fire.gravity}")

    # Clean up dummy file
    import os
    try:
        os.remove("fire_particle_config.json")
    except OSError:
        pass