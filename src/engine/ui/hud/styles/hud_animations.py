import pygame
import math

# TODO: Integrate with a potential global animation system

class HUDAnimation:
    """Base class for HUD animations."""
    def __init__(self, duration=1.0, loop=False):
        self.duration = duration
        self.loop = loop
        self.elapsed_time = 0.0
        self.is_running = False
        self.target_element = None

    def start(self, element):
        self.target_element = element
        self.elapsed_time = 0.0
        self.is_running = True

    def stop(self):
        self.is_running = False

    def update(self, dt):
        if not self.is_running:
            return False # Indicate animation is not active

        self.elapsed_time += dt
        progress = min(self.elapsed_time / self.duration, 1.0)

        self._apply_animation(progress)

        if self.elapsed_time >= self.duration:
            if self.loop:
                self.elapsed_time = 0.0 # Reset for next loop
            else:
                self.stop()
                return False # Indicate animation finished

        return True # Indicate animation is still running

    def _apply_animation(self, progress):
        """Subclasses implement the actual animation logic here."""
        raise NotImplementedError


class HealthFlash(HUDAnimation):
    """Simple flashing animation for health bar."""
    def __init__(self, duration=0.5, loop=True, flash_color=(255, 255, 255), frequency=4.0):
        super().__init__(duration, loop)
        self.flash_color = flash_color
        self.frequency = frequency # Flashes per second

    def _apply_animation(self, progress):
        if not self.target_element: return

        # Use sine wave to create flashing effect
        flash_intensity = (math.sin(self.elapsed_time * self.frequency * 2 * math.pi) + 1) / 2
        # TODO: Need a way to modify the target element's color temporarily
        # This might involve adding a temporary overlay or modifying draw logic
        # Example: self.target_element.set_overlay_color(lerp_color(original_color, self.flash_color, flash_intensity))
        pass # Placeholder - requires modification of HealthBar draw


class FadeIn(HUDAnimation):
    """Fade in an element by adjusting its alpha."""
    def __init__(self, duration=0.5):
        super().__init__(duration, loop=False)

    def _apply_animation(self, progress):
        if not self.target_element: return
        # TODO: Requires elements to support alpha blending
        # Example: self.target_element.set_alpha(int(progress * 255))
        pass # Placeholder


class Pulse(HUDAnimation):
    """Subtly pulse the size of an element."""
    def __init__(self, duration=1.0, loop=True, scale_factor=1.1, frequency=1.0):
        super().__init__(duration, loop)
        self.scale_factor = scale_factor
        self.frequency = frequency

    def _apply_animation(self, progress):
        if not self.target_element: return
        # Use sine wave for smooth pulsing
        scale = 1.0 + (self.scale_factor - 1.0) * (math.sin(self.elapsed_time * self.frequency * 2 * math.pi) + 1) / 2
        # TODO: Requires elements to support scaling or modify their rect
        # Example: self.target_element.set_scale(scale)
        pass # Placeholder

# TODO: Add more animations (e.g., slide in/out, shake)