# src/engine/ui/styles/themes.py

# Définition des palettes de couleurs pour différents thèmes

THEMES = {
    "default": {
        "text": (230, 230, 230),
        "text_hover": (255, 255, 255),
        "text_disabled": (150, 150, 150),
        "button_bg": (50, 50, 80),
        "button_bg_hover": (70, 70, 100),
        "button_border": (90, 90, 120),
        "panel_bg": (40, 40, 60, 200), # RGBA
        "panel_border": (90, 90, 120),
        "background": (30, 30, 30),
        "accent": (100, 100, 255), # Couleur d'accentuation
        "error": (255, 80, 80),
        "success": (80, 255, 80),
    },
    "light": {
        "text": (20, 20, 20),
        "text_hover": (0, 0, 0),
        "text_disabled": (100, 100, 100),
        "button_bg": (220, 220, 220),
        "button_bg_hover": (200, 200, 200),
        "button_border": (180, 180, 180),
        "panel_bg": (240, 240, 240, 230), # RGBA
        "panel_border": (180, 180, 180),
        "background": (250, 250, 250),
        "accent": (0, 120, 255),
        "error": (200, 0, 0),
        "success": (0, 180, 0),
    },
    "forest": {
        "text": (210, 220, 200),
        "text_hover": (240, 255, 230),
        "text_disabled": (120, 130, 110),
        "button_bg": (60, 80, 50),
        "button_bg_hover": (80, 100, 70),
        "button_border": (100, 120, 90),
        "panel_bg": (40, 60, 35, 210), # RGBA
        "panel_border": (100, 120, 90),
        "background": (30, 40, 25),
        "accent": (120, 180, 80),
        "error": (180, 80, 60),
        "success": (100, 200, 120),
    }
    # Ajouter d'autres thèmes ici...
}

# Thème actif par défaut
_active_theme_name = "default"
_active_theme = THEMES[_active_theme_name]

def set_active_theme(theme_name):
    """Change le thème actif."""
    global _active_theme_name, _active_theme
    if theme_name in THEMES:
        _active_theme_name = theme_name
        _active_theme = THEMES[theme_name]
        print(f"Thème '{theme_name}' activé.")
        # TODO: Potentiellement déclencher une mise à jour de l'UI globale
    else:
        print(f"Erreur: Thème '{theme_name}' non trouvé.")

def get_color(color_key, default_color=(255, 0, 255)):
    """Récupère une couleur du thème actif."""
    return _active_theme.get(color_key, default_color)

def get_current_theme_name():
    """Retourne le nom du thème actif."""
    return _active_theme_name

def get_theme_colors(theme_name=None):
    """Retourne le dictionnaire de couleurs pour un thème donné ou le thème actif."""
    if theme_name:
        return THEMES.get(theme_name)
    return _active_theme

# Exemple d'utilisation pour mettre à jour les styles globaux (si nécessaire)
# import src.engine.ui.styles.menu_styles as menu_styles
#
# def update_global_styles_with_theme():
#     theme = get_theme_colors()
#     menu_styles.COLOR_TEXT = theme.get('text')
#     menu_styles.COLOR_BUTTON_BG = theme.get('button_bg')
#     # ... mettre à jour toutes les couleurs dans menu_styles ...
#
#     # Mettre à jour les styles composites
#     menu_styles.BUTTON_STYLE.update({
#         "text_color": theme.get('text'),
#         "hover_text_color": theme.get('text_hover'),
#         # ... etc ...
#     })
#     # TODO: Recharger les polices ou autres ressources si elles dépendent du thème