# src/engine/progression/ability/ability_progression.py
from pathlib import Path
from typing import Dict, Any, Optional

# Importer les chargeurs et validateurs
from ...data.ability_loader import load_ability_data
from ...data.upgrade_loader import load_upgrade_data
from ...data.effect_loader import load_effect_data
# Importer le chargeur pour scaling.json (à créer si ce n'est pas fait)
# from ...data.scaling_loader import load_scaling_data # Supposons qu'il existe
# Note: Ajout d'un import pour scaling_loader.py s'il est créé
try:
    from ...data.scaling_loader import load_scaling_data
    from ...data.data_validator import validate_scaling_data
    SCALING_LOADER_AVAILABLE = True
except ImportError:
    SCALING_LOADER_AVAILABLE = False
    # Définir des placeholders si le module n'existe pas encore
    def load_scaling_data(data_path: Path): return []
    def validate_scaling_data(data: Any): return True


from ...data.data_validator import (
    validate_ability_data,
    validate_upgrade_data,
    validate_effect_data,
    # validate_scaling_data est importé conditionnellement ci-dessus
)

class AbilityProgressionManager:
    """
    Manages the progression of abilities, including leveling up and applying upgrades.
    Loads and holds ability configuration data.
    """
    def __init__(self, data_path: Path, perform_validation: bool = True):
        """
        Initializes the manager and loads all ability-related data.

        Args:
            data_path: Path to the directory containing configuration files (e.g., assets/data).
            perform_validation: Whether to validate the loaded data against schemas.
        """
        print(f"Initializing AbilityProgressionManager with data path: {data_path}")
        self.data_path = data_path
        self.ability_definitions: Dict[str, Dict[str, Any]] = {}
        self.upgrade_definitions: Dict[str, Dict[str, Any]] = {}
        self.effect_definitions: Dict[str, Dict[str, Any]] = {}
        self.scaling_formulas: Dict[str, Any] = {} # Ou une autre structure adaptée

        self._load_all_data(perform_validation)

    def _load_all_data(self, perform_validation: bool):
        """Loads all configuration data from JSON files."""
        print("Loading ability configuration data...")

        raw_abilities = load_ability_data(self.data_path)
        if perform_validation and not validate_ability_data(raw_abilities):
            print("Warning: Ability data validation failed.")
        self.ability_definitions = {ability['id']: ability for ability in raw_abilities if isinstance(ability, dict) and 'id' in ability}
        print(f"Loaded {len(self.ability_definitions)} ability definitions.")

        raw_upgrades = load_upgrade_data(self.data_path)
        if perform_validation and not validate_upgrade_data(raw_upgrades):
            print("Warning: Upgrade data validation failed.")
        self.upgrade_definitions = {upgrade['id']: upgrade for upgrade in raw_upgrades if isinstance(upgrade, dict) and 'id' in upgrade}
        print(f"Loaded {len(self.upgrade_definitions)} upgrade definitions.")

        raw_effects = load_effect_data(self.data_path)
        if perform_validation and not validate_effect_data(raw_effects):
            print("Warning: Effect data validation failed.")
        self.effect_definitions = {effect['id']: effect for effect in raw_effects if isinstance(effect, dict) and 'id' in effect}
        print(f"Loaded {len(self.effect_definitions)} effect definitions.")

        # Charger les données de scaling
        raw_scaling = load_scaling_data(self.data_path)
        if perform_validation and not validate_scaling_data(raw_scaling):
             print("Warning: Scaling data validation failed.")
        # Adapter la structure si nécessaire, par exemple, un dict par stat
        self.scaling_formulas = {formula['stat']: formula for formula in raw_scaling if isinstance(formula, dict) and 'stat' in formula}
        print(f"Loaded {len(self.scaling_formulas)} scaling formulas.")

        print("Finished loading configuration data.")


    def get_ability_data(self, ability_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves the configuration data for a specific ability by its ID."""
        return self.ability_definitions.get(ability_id)

    # --- Méthodes existantes (inchangées pour l'instant) ---
    def gain_experience(self, ability_id, experience_amount):
        """
        Adds experience to a specific ability.
        """
        # TODO: Utiliser self.ability_definitions ou l'état du joueur pour trouver l'ability
        print(f"Ability {ability_id} gained {experience_amount} XP.")
        # Check for level up

    def level_up_ability(self, ability_id):
        """
        Levels up an ability when enough experience is gained.
        """
        # TODO: Utiliser self.ability_definitions/scaling_formulas pour les changements de stats
        print(f"Ability {ability_id} leveled up!")

    def apply_upgrade(self, ability_id, upgrade_id):
        """
        Applies a selected upgrade to an ability.
        """
        # TODO: Utiliser self.upgrade_definitions pour trouver les modificateurs
        upgrade_data = self.upgrade_definitions.get(upgrade_id)
        ability_instance_data = self.get_ability_data(ability_id) # Ceci récupère la définition, pas l'état actuel
        # Il faudrait probablement récupérer l'instance d'Ability depuis le monde/joueur
        if upgrade_data and ability_instance_data:
            print(f"Applying upgrade '{upgrade_data.get('name', upgrade_id)}' to ability '{ability_instance_data.get('name', ability_id)}'.")
            # Logique pour modifier les stats/comportement de l'ability instance
        else:
            print(f"Error: Could not apply upgrade {upgrade_id} to ability {ability_id}. Data not found.")

# Exemple d'utilisation (peut être déplacé ou supprimé)
if __name__ == '__main__':
    # Déterminer le chemin racine du projet (remonter de ability, progression, engine, src)
    project_root = Path(__file__).resolve().parents[4]
    assets_data_path = project_root / "assets" / "data"

    if assets_data_path.exists() and assets_data_path.is_dir():
        print(f"Attempting to load data from: {assets_data_path}")
        try:
            manager = AbilityProgressionManager(assets_data_path)

            # Tester la récupération de données
            test_ability_id = "fireball" # Remplacer par un ID valide si défini dans abilities.json
            fireball_data = manager.get_ability_data(test_ability_id)
            if fireball_data:
                print(f"\nData for '{test_ability_id}':")
                print(fireball_data)
            else:
                print(f"\nAbility data for '{test_ability_id}' not found (This is expected if not defined in JSON).")

            # Tester l'application d'une amélioration (si des données existent)
            test_upgrade_id = "faster_cast" # Remplacer par un ID valide
            manager.apply_upgrade(test_ability_id, test_upgrade_id)

            # Afficher les formules de scaling chargées
            if manager.scaling_formulas:
                print("\nLoaded Scaling Formulas:")
                for stat, formula_data in manager.scaling_formulas.items():
                    print(f"  - {stat}: {formula_data.get('formula', 'N/A')}")
            else:
                print("\nNo scaling formulas loaded (or scaling_loader.py not found).")

        except Exception as e:
            print(f"\nAn error occurred during AbilityProgressionManager initialization or testing: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"Error: Data directory not found or is not a directory at {assets_data_path}")