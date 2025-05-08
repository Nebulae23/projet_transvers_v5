# Guide de Contribution à Nightfall Defenders

Merci de votre intérêt pour contribuer à Nightfall Defenders ! Ce document fournit les lignes directrices et les instructions pour participer efficacement au développement du projet.

## Configuration de l'Environnement de Développement

### Prérequis

- Python 3.8 ou supérieur
- Git
- Un éditeur de code (VS Code, PyCharm, etc.)

### Installation

1. Clonez le dépôt :
   ```bash
   git clone https://github.com/nightfall-defenders/nightfall-defenders.git
   cd nightfall-defenders
   ```

2. Installez les dépendances :
   ```bash
   pip install -r requirements.txt
   ```

3. Vérifiez que tout fonctionne :
   ```bash
   python test_import.py
   ```

## Structure du Projet

Veuillez vous familiariser avec la [structure du projet](STRUCTURE.md) avant de commencer à contribuer. Cela vous aidera à comprendre où placer vos contributions.

## Workflow de Développement

### Branches

- `main` : Branche principale, toujours stable
- `develop` : Branche de développement, intégration des fonctionnalités
- `feature/nom-de-la-fonctionnalité` : Pour le développement de nouvelles fonctionnalités
- `bugfix/nom-du-bug` : Pour les corrections de bugs
- `docs/sujet` : Pour les mises à jour de documentation

### Processus de Contribution

1. Créez votre branche à partir de `develop` :
   ```bash
   git checkout develop
   git pull
   git checkout -b feature/ma-fonctionnalité
   ```

2. Développez votre contribution

3. Exécutez les tests :
   ```bash
   python run_all_tests.bat
   ```

4. Commitez vos changements avec des messages clairs :
   ```bash
   git add .
   git commit -m "Fonctionnalité: Description claire de ce qui a été fait"
   ```

5. Poussez votre branche :
   ```bash
   git push origin feature/ma-fonctionnalité
   ```

6. Ouvrez une Pull Request vers `develop`

## Normes de Codage

### Style Python

Nous suivons PEP 8 avec quelques exceptions :

- Limite de ligne à 100 caractères
- Utilisation de docstrings pour toutes les fonctions et classes
- Typages avec les annotations Python

Exemple :
```python
def calculate_trajectory(start_pos: Vec3, velocity: Vec3, gravity: float = 9.8) -> list[Vec3]:
    """
    Calcule les points de la trajectoire d'un projectile.

    Args:
        start_pos: Position initiale du projectile
        velocity: Vecteur vitesse initiale
        gravity: Force de gravité (par défaut : 9.8)

    Returns:
        Liste des positions le long de la trajectoire
    """
    # Implémentation...
    return trajectory_points
```

### Tests

- Chaque nouvelle fonctionnalité doit être accompagnée de tests
- Les tests unitaires utilisent `unittest`
- Les tests doivent être placés dans le dossier `src/tests`

### Documentation

- Documentez tous les nouveaux systèmes
- Mettez à jour la documentation existante si nécessaire
- Suivez le format Markdown existant

## Systèmes Spécifiques

### Contribution aux Systèmes de Jeu

Pour contribuer à des systèmes spécifiques, veuillez consulter leur documentation dédiée :

- [Système de Combat](systems/COMBAT.md)
- [Système de Progression](systems/CHARACTER_PROGRESSION.md)
- [Système de Ville](systems/CITY_MANAGEMENT.md)
- etc.

### Contribution aux Aspects Visuels

- Les sprites doivent suivre le style artistique existant
- Résolution standard : sprites de base 16x16, 32x32 ou 64x64 pixels
- Palette de couleurs limitée par thème

### Contribution au Gameplay

- Discutez des nouvelles idées de gameplay dans les issues avant l'implémentation
- Testez l'équilibre de votre contribution
- Documentez comment votre ajout s'intègre dans le système existant

## Revue de Code

Votre Pull Request sera revue par au moins un mainteneur. Pour faciliter ce processus :

- Décrivez clairement ce que fait votre PR
- Incluez des détails sur comment tester vos changements
- Répondez aux commentaires et suggestions

## Communication

- Utilisez les issues GitHub pour discuter des fonctionnalités ou bugs
- Pour les discussions plus générales, rejoignez notre [Discord](https://discord.gg/nightfall-defenders)
- Pour les questions techniques complexes, contactez directement un mainteneur

## Reconnaissance des Contributions

Tous les contributeurs sont listés dans notre fichier [CONTRIBUTORS.md](CONTRIBUTORS.md) et sont remerciés dans les notes de version.

## Questions?

Si vous avez des questions sur le processus de contribution, n'hésitez pas à ouvrir une issue avec le tag "question".

Merci encore pour votre intérêt à contribuer à Nightfall Defenders ! 