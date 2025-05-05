# Mock pour le système de configuration
class MockConfigManager:
    def __init__(self, initial_config=None):
        self._config = initial_config if initial_config else {}

    def get(self, section, key, default=None):
        """Récupère une valeur de configuration."""
        return self._config.get(section, {}).get(key, default)

    def set(self, section, key, value):
        """Définit une valeur de configuration."""
        if section not in self._config:
            self._config[section] = {}
        self._config[section][key] = value
        # print(f"MockConfigManager: Set [{section}]{key} = {value}") # Pour le débogage

    def save(self):
        """Simule la sauvegarde de la configuration."""
        # Dans un vrai système, cela écrirait dans un fichier
        # print("MockConfigManager: Simulating config save.") # Pour le débogage
        pass # Ne fait rien dans le mock par défaut

    def load(self):
        """Simule le chargement de la configuration."""
        # Dans un vrai système, cela lirait depuis un fichier
        # print("MockConfigManager: Simulating config load.") # Pour le débogage
        pass # Ne fait rien dans le mock par défaut

    def get_section(self, section):
        """Retourne toute une section de configuration."""
        return self._config.get(section, {})

    def set_config(self, new_config):
        """Remplace toute la configuration actuelle."""
        self._config = new_config