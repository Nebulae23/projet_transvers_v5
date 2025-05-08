#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Day/Night Cycle System for Nightfall Defenders
Controls the game world's time of day, lighting, and environmental effects
"""

from panda3d.core import NodePath, AmbientLight, DirectionalLight, Fog, Vec3, Vec4
import math
import os

class TimeOfDay:
    """Enumerates the different times of day"""
    DAWN = "dawn"       # Early morning
    DAY = "day"         # Full daylight
    DUSK = "dusk"       # Early evening
    NIGHT = "night"     # Full night
    MIDNIGHT = "midnight" # Deep night

class DayNightCycle:
    """Manages the day/night cycle and associated lighting effects"""
    
    def __init__(self, game):
        """
        Initialize the day/night cycle system
        
        Args:
            game: The main game instance
        """
        self.game = game
        
        # Cycle settings
        self.day_length = 600.0  # seconds (10 minutes per full day)
        self.time_scale = 1.0    # Can be adjusted to speed up/slow down time
        self.current_time = 0.0  # 0.0 to 1.0 (0 = dawn, 0.25 = day, 0.5 = dusk, 0.75 = night)
        
        # Time tracking
        self.time_of_day = TimeOfDay.DAWN
        self.transition_progress = 0.0  # Progress of current transition (0.0 to 1.0)
        
        # Time thresholds (as fraction of day)
        self.dawn_time = 0.0
        self.day_time = 0.25
        self.dusk_time = 0.5
        self.night_time = 0.75
        
        # Lighting setup
        self.setup_lighting()
        
        # Fog setup
        self.setup_fog()
        
        # Current environmental modifiers
        self.enemy_spawn_multiplier = 1.0
        self.enemy_strength_multiplier = 1.0
        self.visibility_distance = 100.0
        
        # Set up shader filter (if available)
        self.setup_shader_filter()
        
        # Update lighting for initial time
        self.update_lighting(0)
        
        # Debug display
        self.debug_node = None
        self.create_debug_display()
    
    def setup_lighting(self):
        """Set up the lighting system"""
        # Main directional light (sun/moon)
        self.directional_light = DirectionalLight("sun_moon_light")
        self.directional_light.setColor((0.8, 0.8, 0.7, 1))  # Yellowish for sun
        self.directional_light_np = self.game.render.attachNewNode(self.directional_light)
        self.directional_light_np.setHpr(0, -60, 0)  # Sun angled from east
        self.game.render.setLight(self.directional_light_np)
        
        # Ambient light (general illumination)
        self.ambient_light = AmbientLight("ambient_light")
        self.ambient_light.setColor((0.3, 0.3, 0.4, 1))  # Slight blue tint
        self.ambient_light_np = self.game.render.attachNewNode(self.ambient_light)
        self.game.render.setLight(self.ambient_light_np)
        
        # Blue fill light for night (moon/stars)
        self.night_fill_light = DirectionalLight("night_fill")
        self.night_fill_light.setColor((0.1, 0.1, 0.3, 1))  # Blue moonlight
        self.night_fill_np = self.game.render.attachNewNode(self.night_fill_light)
        self.night_fill_np.setHpr(0, -75, 0)  # Moon high in sky
        self.night_fill_np.setColor((0, 0, 0, 1))  # Start with it off
        self.game.render.setLight(self.night_fill_np)
        
        # Store light colors for each time of day
        self.light_settings = {
            TimeOfDay.DAWN: {
                "directional": Vec4(0.9, 0.7, 0.6, 1),  # Orange sunrise
                "ambient": Vec4(0.3, 0.3, 0.4, 1),
                "night_fill": Vec4(0, 0, 0, 1),  # Off
                "direction": Vec3(-45, -30, 0)   # Rising from east
            },
            TimeOfDay.DAY: {
                "directional": Vec4(1.0, 0.95, 0.9, 1),  # Bright white
                "ambient": Vec4(0.4, 0.4, 0.5, 1),
                "night_fill": Vec4(0, 0, 0, 1),  # Off
                "direction": Vec3(0, -60, 0)     # High in sky
            },
            TimeOfDay.DUSK: {
                "directional": Vec4(0.9, 0.6, 0.4, 1),  # Orange sunset
                "ambient": Vec4(0.3, 0.3, 0.4, 1),
                "night_fill": Vec4(0, 0, 0, 1),  # Off
                "direction": Vec3(45, -20, 0)    # Setting in west
            },
            TimeOfDay.NIGHT: {
                "directional": Vec4(0.2, 0.2, 0.3, 1),  # Dim blue
                "ambient": Vec4(0.1, 0.1, 0.2, 1),
                "night_fill": Vec4(0.1, 0.1, 0.3, 1),  # Blue moonlight
                "direction": Vec3(0, -45, 0)     # Moon in sky
            },
            TimeOfDay.MIDNIGHT: {
                "directional": Vec4(0.1, 0.1, 0.2, 1),  # Very dim
                "ambient": Vec4(0.05, 0.05, 0.1, 1),
                "night_fill": Vec4(0.05, 0.05, 0.2, 1),  # Faint moonlight
                "direction": Vec3(0, -80, 0)    # Moon high overhead
            }
        }
    
    def setup_fog(self):
        """Set up the fog system for distance culling and atmosphere"""
        self.fog = Fog("world_fog")
        self.fog.setColor(0.5, 0.5, 0.6)
        self.fog.setExpDensity(0.002)  # Low density by default
        
        # Apply fog to the render node
        self.game.render.setFog(self.fog)
        
        # Store fog settings for each time of day
        self.fog_settings = {
            TimeOfDay.DAWN: {
                "color": Vec4(0.7, 0.6, 0.6, 1),
                "density": 0.004  # Morning mist
            },
            TimeOfDay.DAY: {
                "color": Vec4(0.8, 0.8, 0.9, 1),
                "density": 0.001  # Clear day
            },
            TimeOfDay.DUSK: {
                "color": Vec4(0.6, 0.5, 0.5, 1),
                "density": 0.003  # Evening haze
            },
            TimeOfDay.NIGHT: {
                "color": Vec4(0.2, 0.2, 0.3, 1),
                "density": 0.01   # Night darkness
            },
            TimeOfDay.MIDNIGHT: {
                "color": Vec4(0.1, 0.1, 0.2, 1),
                "density": 0.02   # Deep night, heavy darkness
            }
        }
    
    def setup_shader_filter(self):
        """Set up a post-processing shader filter for day/night color correction"""
        # Try to set up the shader, but if it fails, continue without it
        try:
            from panda3d.core import CardMaker, NodePath, Shader
            
            # Create a full-screen card for the filter
            self.filter_cm = CardMaker("day_night_filter")
            self.filter_cm.setFrameFullscreenQuad()
            self.filter_quad = NodePath(self.filter_cm.generate())
            
            # Load the shader
            vertex_path = "src/assets/shaders/day_night_filter.vert"
            fragment_path = "src/assets/shaders/day_night_filter.frag"
            
            if os.path.exists(vertex_path) and os.path.exists(fragment_path):
                # Load from files
                self.filter_shader = Shader.load(Shader.SL_GLSL, 
                                              vertex=vertex_path,
                                              fragment=fragment_path)
                print("Day/night shader loaded from files")
            else:
                # Create inline shader as fallback
                self.filter_shader = Shader.make(Shader.SL_GLSL,
                    """
                    #version 330
                    
                    uniform mat4 p3d_ModelViewProjectionMatrix;
                    in vec4 p3d_Vertex;
                    in vec2 p3d_MultiTexCoord0;
                    out vec2 texcoord;
                    
                    void main() {
                        gl_Position = p3d_ModelViewProjectionMatrix * p3d_Vertex;
                        texcoord = p3d_MultiTexCoord0;
                    }
                    """,
                    """
                    #version 330
                    
                    uniform sampler2D p3d_Texture0;
                    uniform vec4 day_tint;
                    uniform vec4 night_tint;
                    uniform float blend_factor;
                    in vec2 texcoord;
                    out vec4 fragColor;
                    
                    void main() {
                        vec4 color = texture(p3d_Texture0, texcoord);
                        vec4 tinted = mix(color * day_tint, color * night_tint, blend_factor);
                        fragColor = tinted;
                    }
                    """
                )
                print("Using fallback day/night shader")
                
            # Apply the shader
            self.filter_quad.setShader(self.filter_shader)
            
            # Set up initial shader parameters
            self.filter_quad.setShaderInput("day_tint", (1.0, 1.0, 1.0, 1.0))
            self.filter_quad.setShaderInput("night_tint", (0.6, 0.7, 1.0, 1.0))
            self.filter_quad.setShaderInput("blend_factor", 0.0)
            self.filter_quad.setShaderInput("fog_density", 0.8)
            self.filter_quad.setShaderInput("fog_distance", 0.3)
            
            # Add the filter to the render pipeline
            self.filter_quad.reparentTo(self.game.render2d)
            
            # Make sure it's rendered after everything else
            self.filter_quad.setBin("fixed", 100)
            
            print("Day/night shader filter applied successfully")
            self.has_shader = True
        except Exception as e:
            print(f"Could not set up day/night shader filter: {e}")
            self.has_shader = False
    
    def update(self, dt):
        """
        Update the day/night cycle
        
        Args:
            dt: Delta time in seconds
        """
        # Update time
        time_delta = dt * self.time_scale / self.day_length
        self.current_time = (self.current_time + time_delta) % 1.0
        
        # Determine current time of day
        prev_time_of_day = self.time_of_day
        
        if self.current_time < self.day_time:
            # Dawn to day
            if self.current_time < self.day_time / 2:
                self.time_of_day = TimeOfDay.DAWN
                self.transition_progress = self.current_time / (self.day_time / 2)
            else:
                self.time_of_day = TimeOfDay.DAY
                self.transition_progress = (self.current_time - self.day_time / 2) / (self.day_time / 2)
        elif self.current_time < self.dusk_time:
            # Day to dusk
            self.time_of_day = TimeOfDay.DAY
            self.transition_progress = (self.current_time - self.day_time) / (self.dusk_time - self.day_time)
        elif self.current_time < self.night_time:
            # Dusk to night
            if self.current_time < (self.dusk_time + self.night_time) / 2:
                self.time_of_day = TimeOfDay.DUSK
                self.transition_progress = (self.current_time - self.dusk_time) / ((self.dusk_time + self.night_time) / 2 - self.dusk_time)
            else:
                self.time_of_day = TimeOfDay.NIGHT
                self.transition_progress = (self.current_time - (self.dusk_time + self.night_time) / 2) / (self.night_time - (self.dusk_time + self.night_time) / 2)
        else:
            # Night to dawn (through midnight)
            if self.current_time < (self.night_time + 1 + self.dawn_time) / 2:
                self.time_of_day = TimeOfDay.MIDNIGHT
                self.transition_progress = (self.current_time - self.night_time) / ((self.night_time + 1 + self.dawn_time) / 2 - self.night_time)
            else:
                self.time_of_day = TimeOfDay.DAWN
                self.transition_progress = (self.current_time - (self.night_time + 1 + self.dawn_time) / 2) / (1 - (self.night_time + 1 + self.dawn_time) / 2)
        
        # Update lighting based on time of day
        self.update_lighting(dt)
        
        # Update gameplay modifiers
        self.update_gameplay_modifiers()
        
        # Update debug display
        self.update_debug_display()
        
        # Notify if time of day changed
        if prev_time_of_day != self.time_of_day:
            self.on_time_of_day_changed()
    
    def update_lighting(self, dt):
        """
        Update lighting based on current time of day
        
        Args:
            dt: Delta time in seconds
        """
        # Determine next time of day for transitions
        next_time = None
        
        if self.time_of_day == TimeOfDay.DAWN:
            next_time = TimeOfDay.DAY
        elif self.time_of_day == TimeOfDay.DAY:
            next_time = TimeOfDay.DUSK
        elif self.time_of_day == TimeOfDay.DUSK:
            next_time = TimeOfDay.NIGHT
        elif self.time_of_day == TimeOfDay.NIGHT:
            next_time = TimeOfDay.MIDNIGHT
        elif self.time_of_day == TimeOfDay.MIDNIGHT:
            next_time = TimeOfDay.DAWN
        
        # Get current and next lighting settings
        current_settings = self.light_settings[self.time_of_day]
        next_settings = self.light_settings[next_time] if next_time else current_settings
        
        # Interpolate between current and next settings
        directional_color = self.interpolate_color(
            current_settings["directional"],
            next_settings["directional"],
            self.transition_progress
        )
        
        ambient_color = self.interpolate_color(
            current_settings["ambient"],
            next_settings["ambient"],
            self.transition_progress
        )
        
        night_fill_color = self.interpolate_color(
            current_settings["night_fill"],
            next_settings["night_fill"],
            self.transition_progress
        )
        
        # Apply lighting colors
        self.directional_light.setColor(directional_color)
        self.ambient_light.setColor(ambient_color)
        self.night_fill_light.setColor(night_fill_color)
        
        # Interpolate direction
        direction = self.interpolate_vec3(
            current_settings["direction"],
            next_settings["direction"],
            self.transition_progress
        )
        
        self.directional_light_np.setHpr(direction)
        
        # Update fog
        current_fog = self.fog_settings[self.time_of_day]
        next_fog = self.fog_settings[next_time] if next_time else current_fog
        
        # Interpolate fog color
        fog_color = self.interpolate_color(
            current_fog["color"],
            next_fog["color"],
            self.transition_progress
        )
        
        # Interpolate fog density
        fog_density = current_fog["density"] * (1 - self.transition_progress) + next_fog["density"] * self.transition_progress
        
        # Apply fog settings
        self.fog.setColor(fog_color)
        self.fog.setExpDensity(fog_density)
        
        # Update shader filter if available
        if self.has_shader:
            # Calculate day/night blend factor
            blend_factor = 0.0
            
            if self.time_of_day == TimeOfDay.NIGHT:
                blend_factor = 0.7 + 0.3 * self.transition_progress
            elif self.time_of_day == TimeOfDay.MIDNIGHT:
                blend_factor = 1.0
            elif self.time_of_day == TimeOfDay.DAWN:
                blend_factor = 0.7 * (1.0 - self.transition_progress)
            elif self.time_of_day == TimeOfDay.DUSK:
                blend_factor = 0.7 * self.transition_progress
            
            # Apply the blend factor to the shader
            self.filter_quad.setShaderInput("blend_factor", blend_factor)
            
            # Update fog density based on time of day
            fog_density = 0.8  # Default
            if self.time_of_day == TimeOfDay.MIDNIGHT:
                fog_density = 1.2
            elif self.time_of_day == TimeOfDay.NIGHT:
                fog_density = 0.8 + 0.4 * self.transition_progress
            elif self.time_of_day == TimeOfDay.DAWN:
                fog_density = 0.8 * (1.0 - self.transition_progress)
            elif self.time_of_day == TimeOfDay.DUSK:
                fog_density = 0.8 * self.transition_progress
            
            self.filter_quad.setShaderInput("fog_density", fog_density)
            
            # Update day/night tint colors
            current_time_settings = self.light_settings[self.time_of_day]
            next_time = self._get_next_time_of_day()
            next_time_settings = self.light_settings[next_time]
            
            day_tint = Vec4(1.0, 1.0, 1.0, 1.0)
            night_tint = Vec4(0.6, 0.7, 1.0, 1.0)
            
            if self.time_of_day == TimeOfDay.DAWN:
                day_tint = Vec4(1.0, 0.9, 0.8, 1.0)  # Golden sunrise
            elif self.time_of_day == TimeOfDay.DAY:
                day_tint = Vec4(1.0, 1.0, 1.0, 1.0)  # Neutral daylight
            elif self.time_of_day == TimeOfDay.DUSK:
                day_tint = Vec4(1.0, 0.8, 0.7, 1.0)  # Orange sunset
            
            if self.time_of_day == TimeOfDay.NIGHT:
                night_tint = Vec4(0.6, 0.7, 0.9, 1.0)  # Blue moonlight
            elif self.time_of_day == TimeOfDay.MIDNIGHT:
                night_tint = Vec4(0.4, 0.5, 0.8, 1.0)  # Deep blue night
            
            self.filter_quad.setShaderInput("day_tint", day_tint)
            self.filter_quad.setShaderInput("night_tint", night_tint)
    
    def update_gameplay_modifiers(self):
        """Update gameplay modifiers based on time of day"""
        # Set enemy spawn and strength multipliers based on time of day
        if self.time_of_day == TimeOfDay.DAY:
            self.enemy_spawn_multiplier = 1.0
            self.enemy_strength_multiplier = 1.0
            self.visibility_distance = 100.0
        elif self.time_of_day == TimeOfDay.DAWN or self.time_of_day == TimeOfDay.DUSK:
            self.enemy_spawn_multiplier = 1.5
            self.enemy_strength_multiplier = 1.2
            self.visibility_distance = 80.0
        elif self.time_of_day == TimeOfDay.NIGHT:
            self.enemy_spawn_multiplier = 2.0
            self.enemy_strength_multiplier = 1.5
            self.visibility_distance = 60.0
        elif self.time_of_day == TimeOfDay.MIDNIGHT:
            self.enemy_spawn_multiplier = 3.0
            self.enemy_strength_multiplier = 2.0
            self.visibility_distance = 40.0
    
    def get_enemy_spawn_multiplier(self):
        """
        Get the current enemy spawn rate multiplier
        
        Returns:
            float: Spawn rate multiplier
        """
        return self.enemy_spawn_multiplier
    
    def get_enemy_strength_multiplier(self):
        """
        Get the current enemy strength multiplier
        
        Returns:
            float: Strength multiplier
        """
        return self.enemy_strength_multiplier
    
    def get_visibility_distance(self):
        """
        Get the current visibility distance
        
        Returns:
            float: Visibility distance
        """
        return self.visibility_distance
    
    def get_time_of_day_name(self):
        """
        Get the name of the current time of day
        
        Returns:
            str: Time of day name
        """
        return self.time_of_day.capitalize()
    
    def on_time_of_day_changed(self):
        """Handle time of day transitions"""
        # Notify the player about time change
        if hasattr(self.game, 'message_system'):
            self.game.message_system.add_message(f"Time changed to {self.get_time_of_day_name()}")
        else:
            print(f"Time changed to {self.get_time_of_day_name()}")
    
    def _get_next_time_of_day(self):
        """
        Get the next time of day for transitions
        
        Returns:
            str: Next time of day
        """
        if self.time_of_day == TimeOfDay.DAWN:
            return TimeOfDay.DAY
        elif self.time_of_day == TimeOfDay.DAY:
            return TimeOfDay.DUSK
        elif self.time_of_day == TimeOfDay.DUSK:
            return TimeOfDay.NIGHT
        elif self.time_of_day == TimeOfDay.NIGHT:
            return TimeOfDay.MIDNIGHT
        elif self.time_of_day == TimeOfDay.MIDNIGHT:
            return TimeOfDay.DAWN
    
    def interpolate_color(self, color1, color2, t):
        """
        Interpolate between two colors
        
        Args:
            color1: First color (Vec4)
            color2: Second color (Vec4)
            t: Interpolation factor (0-1)
            
        Returns:
            Vec4: Interpolated color
        """
        return color1 * (1 - t) + color2 * t
    
    def interpolate_vec3(self, vec1, vec2, t):
        """
        Interpolate between two Vec3 values
        
        Args:
            vec1: First vector (Vec3)
            vec2: Second vector (Vec3)
            t: Interpolation factor (0-1)
        
        Returns:
            Vec3: Interpolated vector
        """
        return vec1 * (1 - t) + vec2 * t
    
    def set_time_scale(self, scale):
        """
        Set the time scale (speed of day/night cycle)
        
        Args:
            scale: Time scale factor (1.0 = normal speed)
        """
        self.time_scale = max(0.1, min(100.0, scale))
    
    def set_time(self, time_of_day):
        """
        Set the time of day directly
        
        Args:
            time_of_day: TimeOfDay value to set
        """
        if time_of_day == TimeOfDay.DAWN:
            self.current_time = 0.0
        elif time_of_day == TimeOfDay.DAY:
            self.current_time = 0.25
        elif time_of_day == TimeOfDay.DUSK:
            self.current_time = 0.5
        elif time_of_day == TimeOfDay.NIGHT:
            self.current_time = 0.75
        elif time_of_day == TimeOfDay.MIDNIGHT:
            self.current_time = 0.9
        
        # Force an update to apply changes immediately
        self.update(0)
    
    def create_debug_display(self):
        """Create a visual debug display of the day/night cycle"""
        # Remove existing debug node if it exists
        if self.debug_node:
            self.debug_node.removeNode()
        
        # Only create debug display if debug mode is enabled
        if not hasattr(self.game, 'debug_mode') or not self.game.debug_mode:
            return
            
        from panda3d.core import TextNode
        from direct.gui.OnscreenText import OnscreenText
        
        # Create a new debug node
        self.debug_node = self.game.aspect2d.attachNewNode("DayNightDebug")
        
        # Create a time of day text display
        self.debug_text = OnscreenText(
            text=f"Time: {self.get_time_of_day_name()} ({self.current_time * 24:.1f} hrs)",
            pos=(-1.3, 0.9),
            scale=0.05,
            align=TextNode.ALeft,
            fg=(1, 1, 1, 1),
            shadow=(0, 0, 0, 0.5),
            parent=self.debug_node
        )
        
        # Create a day cycle visualization
        from direct.gui.DirectFrame import DirectFrame
        
        # Frame for the cycle visualization
        self.cycle_frame = DirectFrame(
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(-0.3, 0.3, -0.05, 0.05),
            pos=(-1.0, 0, 0.8),
            parent=self.debug_node
        )
        
        # Time markers
        markers = [
            (0.0, "Dawn", (0.9, 0.7, 0.6, 1)),
            (0.25, "Day", (1.0, 1.0, 0.8, 1)),
            (0.5, "Dusk", (0.9, 0.6, 0.4, 1)),
            (0.75, "Night", (0.2, 0.2, 0.5, 1)),
            (0.9, "Midnight", (0.1, 0.1, 0.3, 1))
        ]
        
        for time, label, color in markers:
            # Calculate position within frame (-0.3 to 0.3)
            marker_pos = -0.3 + time * 0.6
            
            # Add marker line
            marker_frame = DirectFrame(
                frameColor=color,
                frameSize=(-0.003, 0.003, -0.04, 0.04),
                pos=(marker_pos, 0, 0),
                parent=self.cycle_frame
            )
            
            # Add label
            marker_text = OnscreenText(
                text=label,
                pos=(marker_pos, -0.07),
                scale=0.03,
                fg=color,
                align=TextNode.ACenter,
                parent=self.cycle_frame
            )
        
        # Current time indicator (will be updated)
        self.time_indicator = DirectFrame(
            frameColor=(1, 1, 1, 1),
            frameSize=(-0.005, 0.005, -0.05, 0.05),
            pos=(-0.3, 0, 0),
            parent=self.cycle_frame
        )
    
    def update_debug_display(self):
        """Update the debug display with current time information"""
        if not self.debug_node:
            return
            
        # Update time text
        hours = self.current_time * 24
        self.debug_text.setText(f"Time: {self.get_time_of_day_name()} ({hours:.1f} hrs)")
        
        # Update time indicator position
        indicator_pos = -0.3 + self.current_time * 0.6
        self.time_indicator.setPos(indicator_pos, 0, 0)
        
        # Update indicator color based on time of day
        if self.time_of_day == TimeOfDay.DAWN:
            color = (0.9, 0.7, 0.6, 1)
        elif self.time_of_day == TimeOfDay.DAY:
            color = (1.0, 1.0, 0.8, 1)
        elif self.time_of_day == TimeOfDay.DUSK:
            color = (0.9, 0.6, 0.4, 1)
        elif self.time_of_day == TimeOfDay.NIGHT:
            color = (0.2, 0.2, 0.5, 1)
        else:  # Midnight
            color = (0.1, 0.1, 0.3, 1)
            
        self.time_indicator.setColor(color) 