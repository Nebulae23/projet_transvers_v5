from typing import Dict, Any

def validate_ability_data(data: Dict[str, Any]) -> bool:
    """Valide la structure et les types des données des capacités."""
    # TODO: Implémenter la logique de validation détaillée
    # - Vérifier la présence des clés requises (ex: id, name, base_stats)
    # - Vérifier les types de données (ex: id est une chaîne, base_stats est un dict)
    # - Vérifier les valeurs (ex: cooldown >= 0)
    if not isinstance(data, list):
        print("Erreur de validation : Les données des capacités devraient être une liste.")
        return False
    
    for ability in data:
        if not isinstance(ability, dict):
            print("Erreur de validation : Chaque capacité devrait être un dictionnaire.")
            return False
        # Ajouter d'autres vérifications ici
        
    print("Validation des données des capacités réussie (basique).")
    return True

def validate_upgrade_data(data: Dict[str, Any]) -> bool:
    """Valide la structure et les types des données des améliorations."""
    # TODO: Implémenter la logique de validation détaillée
    if not isinstance(data, list):
        print("Erreur de validation : Les données des améliorations devraient être une liste.")
        return False
        
    print("Validation des données des améliorations réussie (basique).")
    return True

def validate_effect_data(data: Dict[str, Any]) -> bool:
    """Valide la structure et les types des données des effets."""
    # TODO: Implémenter la logique de validation détaillée
    if not isinstance(data, list):
        print("Erreur de validation : Les données des effets devraient être une liste.")
        return False
        
    print("Validation des données des effets réussie (basique).")
    return True

def validate_scaling_data(data: Dict[str, Any]) -> bool:
    """Valide la structure et les types des données de progression (scaling)."""
    # TODO: Implémenter la logique de validation détaillée
    if not isinstance(data, list):
         print("Erreur de validation : Les données de scaling devraient être une liste.")
         return False
         
    print("Validation des données de scaling réussie (basique).")
    return True

# Exemple d'utilisation (peut être retiré ou mis sous condition __main__)
if __name__ == '__main__':
    # Créer des données factices pour tester les validateurs
    dummy_abilities = [{"id": "fireball", "name": "Fireball", "base_stats": {"damage": 10}}]
    dummy_upgrades = [{"id": "faster_cast", "target_ability": "fireball", "modifier": {"cooldown": -0.1}}]
    dummy_effects = [{"id": "fire_explosion", "particle_system": "explosion_small"}]
    dummy_scaling = [{"stat": "damage", "formula": "base * (1 + level * 0.1)"}]

    print("Test de validation des capacités :", validate_ability_data(dummy_abilities))
    print("Test de validation des améliorations :", validate_upgrade_data(dummy_upgrades))
    print("Test de validation des effets :", validate_effect_data(dummy_effects))
    print("Test de validation de la progression :", validate_scaling_data(dummy_scaling))