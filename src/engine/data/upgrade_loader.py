import json
from pathlib import Path

def load_upgrade_data(data_path: Path):
    """Charge les données des améliorations depuis le fichier JSON."""
    file_path = data_path / "upgrades.json"
    if not file_path.is_file():
        # Gérer l'erreur si le fichier n'existe pas
        print(f"Erreur : Fichier de données des améliorations introuvable à {file_path}")
        return {}

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        # Ici, vous pourriez ajouter une validation du schéma des données
        return data.get("upgrades", {})
    except json.JSONDecodeError:
        print(f"Erreur : Impossible de décoder le JSON dans {file_path}")
        return {}
    except Exception as e:
        print(f"Erreur inattendue lors du chargement de {file_path}: {e}")
        return {}

# Exemple d'utilisation (peut être retiré ou mis sous condition __main__)
if __name__ == '__main__':
    project_root = Path(__file__).resolve().parents[3] # Remonter de data, engine, src
    data_dir = project_root / "assets" / "data"
    upgrades = load_upgrade_data(data_dir)
    print("Données des améliorations chargées :")
    print(upgrades)