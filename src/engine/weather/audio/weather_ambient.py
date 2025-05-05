# src/engine/weather/audio/weather_ambient.py

class WeatherAudioManager:
    """Gère les sons d'ambiance liés à la météo."""
    def __init__(self, config, audio_system):
        self.config = config
        self.audio_system = audio_system
        self.current_ambient_sound = None
        self.current_weather_type = None

    def update_weather(self, weather_type):
        """Met à jour l'ambiance sonore en fonction du type de météo."""
        if weather_type == self.current_weather_type:
            return

        new_ambient_config = self.config.get(weather_type, {}).get("ambient")
        if not new_ambient_config:
            # Pas de configuration d'ambiance pour ce type de météo
            if self.current_ambient_sound:
                self.audio_system.stop_sound(self.current_ambient_sound, fade_out=True)
                self.current_ambient_sound = None
            self.current_weather_type = weather_type
            return

        sound_file = new_ambient_config.get("file")
        volume = new_ambient_config.get("volume", 1.0)
        fade_duration = new_ambient_config.get("fade_duration", 2.0) # Durée de transition par défaut

        if self.current_ambient_sound:
            self.audio_system.stop_sound(self.current_ambient_sound, fade_out=True, duration=fade_duration)

        self.current_ambient_sound = self.audio_system.play_sound(
            sound_file,
            loop=True,
            volume=volume,
            fade_in=True,
            duration=fade_duration
        )
        self.current_weather_type = weather_type

    def play_one_shot(self, sound_key):
        """Joue un son ponctuel (ex: tonnerre)."""
        one_shot_config = self.config.get(self.current_weather_type, {}).get("one_shots", {}).get(sound_key)
        if one_shot_config:
            sound_file = one_shot_config.get("file")
            volume = one_shot_config.get("volume", 1.0)
            if sound_file:
                self.audio_system.play_sound(sound_file, volume=volume)

    def update(self, delta_time):
        """Mise à jour du mixage dynamique ou d'autres logiques audio."""
        # Pourrait être utilisé pour ajuster le volume en fonction de l'intensité de la météo, etc.
        pass

    def stop_all(self):
        """Arrête tous les sons liés à la météo."""
        if self.current_ambient_sound:
            self.audio_system.stop_sound(self.current_ambient_sound)
            self.current_ambient_sound = None
        self.current_weather_type = None