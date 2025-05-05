# src/engine/ui/styles/menu_styles.py
import pygame

# Couleurs (exemple, à adapter selon le thème)
COLOR_TEXT = (230, 230, 230)
COLOR_TEXT_HOVER = (255, 255, 255)
COLOR_TEXT_DISABLED = (150, 150, 150)
COLOR_BUTTON_BG = (50, 50, 80)
COLOR_BUTTON_BG_HOVER = (70, 70, 100)
COLOR_BUTTON_BORDER = (90, 90, 120)
COLOR_PANEL_BG = (40, 40, 60, 200) # Avec alpha pour transparence

# Polices (charger une seule fois si possible)
try:
    pygame.font.init()
    FONT_DEFAULT_PATH = None # Utiliser la police par défaut de pygame
    FONT_TITLE_PATH = None   # Ou spécifier des chemins vers des .ttf
    FONT_DEFAULT_SIZE = 24
    FONT_TITLE_SIZE = 48
    FONT_DEFAULT = pygame.font.Font(FONT_DEFAULT_PATH, FONT_DEFAULT_SIZE)
    FONT_TITLE = pygame.font.Font(FONT_TITLE_PATH, FONT_TITLE_SIZE)
except pygame.error as e:
    print(f"Erreur chargement police: {e}. Utilisation de la police système par défaut.")
    FONT_DEFAULT = pygame.font.SysFont(None, FONT_DEFAULT_SIZE)
    FONT_TITLE = pygame.font.SysFont(None, FONT_TITLE_SIZE)


# Styles des Widgets
BUTTON_STYLE = {
    "font": FONT_DEFAULT,
    "text_color": COLOR_TEXT,
    "hover_text_color": COLOR_TEXT_HOVER,
    "disabled_text_color": COLOR_TEXT_DISABLED,
    "bg_color": COLOR_BUTTON_BG,
    "hover_bg_color": COLOR_BUTTON_BG_HOVER,
    "border_color": COLOR_BUTTON_BORDER,
    "border_width": 2,
    "padding": (15, 10), # Padding horizontal, vertical
    "min_size": (150, 40),
}

LABEL_STYLE = {
    "font": FONT_DEFAULT,
    "text_color": COLOR_TEXT,
}

TITLE_LABEL_STYLE = {
    "font": FONT_TITLE,
    "text_color": COLOR_TEXT,
}

PANEL_STYLE = {
    "bg_color": COLOR_PANEL_BG,
    "border_color": COLOR_BUTTON_BORDER,
    "border_width": 1,
    "padding": (20, 20),
}

# TODO: Ajouter d'autres styles si nécessaire (sliders, progress bars, etc.)

# Fonction pour appliquer un style à un widget (si les widgets ne le gèrent pas nativement)
def apply_style(widget, style):
    for key, value in style.items():
        if hasattr(widget, key):
            setattr(widget, key, value)
        # Gérer les cas spécifiques comme la recréation de la surface du texte pour la police/couleur
        if key in ["font", "text_color"] and hasattr(widget, "render_text"):
             widget.render_text() # Méthode hypothétique pour re-rendre le texte
        if key in ["bg_color", "border_color", "border_width", "padding"] and hasattr(widget, "update_appearance"):
             widget.update_appearance() # Méthode hypothétique pour màj l'apparence