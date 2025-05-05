import os
from PIL import Image

# Définir le répertoire de base des assets
ASSETS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'assets')
SPRITES_DIR = os.path.join(ASSETS_DIR, 'sprites')
UI_DIR = os.path.join(ASSETS_DIR, 'ui')
BACKGROUNDS_DIR = os.path.join(ASSETS_DIR, 'backgrounds')

# Créer les répertoires s'ils n'existent pas
os.makedirs(SPRITES_DIR, exist_ok=True)
os.makedirs(UI_DIR, exist_ok=True)
os.makedirs(BACKGROUNDS_DIR, exist_ok=True)

# Définir les chemins de fichiers
player_path = os.path.join(SPRITES_DIR, 'player.png')
enemy_path = os.path.join(SPRITES_DIR, 'enemy.png')
button_path = os.path.join(UI_DIR, 'button.png')
demo_bg_path = os.path.join(BACKGROUNDS_DIR, 'demo_bg.png')

# Générer player.png (carré bleu 32x32)
img_player = Image.new('RGB', (32, 32), color = 'blue')
img_player.save(player_path)
print(f"Généré: {player_path}")

# Générer enemy.png (carré rouge 32x32)
img_enemy = Image.new('RGB', (32, 32), color = 'red')
img_enemy.save(enemy_path)
print(f"Généré: {enemy_path}")

# Générer button.png (rectangle gris 200x50)
img_button = Image.new('RGB', (200, 50), color = 'grey')
img_button.save(button_path)
print(f"Généré: {button_path}")

# Générer demo_bg.png (motif simple 800x600)
img_bg = Image.new('RGB', (800, 600), color = (200, 200, 255)) # Fond bleu clair
# Ajoutons quelques lignes pour un motif simple
pixels = img_bg.load()
for i in range(img_bg.size[0]):
    for j in range(img_bg.size[1]):
        if (i // 50 + j // 50) % 2 == 0:
            pixels[i, j] = (180, 180, 230) # Lignes plus sombres
img_bg.save(demo_bg_path)
print(f"Généré: {demo_bg_path}")

print("Génération des assets de test terminée.")