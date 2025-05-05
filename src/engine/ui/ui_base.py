# src/engine/ui/ui_base.py
import numpy as np
import enum
import pygame
from typing import Callable, Dict, Any, Optional, List, Tuple

# --- Événements UI ---

class UIEventType(enum.Enum):
    MOUSE_MOTION = 1
    MOUSE_BUTTON_DOWN = 2
    MOUSE_BUTTON_UP = 3
    KEY_DOWN = 4
    KEY_UP = 5
    # Ajoutez d'autres types si nécessaire

class UIEvent:
    """Représente un événement UI."""
    def __init__(self, type: UIEventType, data: Optional[Dict[str, Any]] = None):
        self.type = type
        self.data = data if data is not None else {}
        self.handled = False # Indique si l'événement a été traité

    def __repr__(self):
        return f"UIEvent(type={self.type.name}, data={self.data}, handled={self.handled})"

# --- Gestionnaire de Layout (Base) ---

class LayoutManager:
    """Classe de base abstraite pour les gestionnaires de layout."""
    def apply_layout(self, element: 'UIElement'):
        """
        Applique la logique de disposition aux enfants de l'élément donné.
        Doit être implémentée par les sous-classes.
        """
        raise NotImplementedError

    def update(self, element: 'UIElement'):
        """
        Méthode appelée pour mettre à jour le layout (ex: si la taille du parent change).
        Par défaut, réapplique le layout.
        """
        self.apply_layout(element)

# --- Élément UI de Base ---

class UIElement:
    """
    Classe de base pour tous les éléments de l'interface utilisateur.
    Gère la position, la taille, la hiérarchie parent-enfant et le rendu de base.
    """
    def __init__(self,
                 x: int = 0,
                 y: int = 0,
                 width: int = 10,
                 height: int = 10,
                 parent: Optional['UIElement'] = None,
                 layout: Optional[LayoutManager] = None,
                 z_index: int = 0):
        """
        Initialise un nouvel élément UI.

        Args:
            x (int): Position X relative au parent.
            y (int): Position Y relative au parent.
            width (int): Largeur de l'élément.
            height (int): Hauteur de l'élément.
            parent (Optional[UIElement]): Élément parent dans la hiérarchie UI.
            layout (Optional[LayoutManager]): Gestionnaire de layout pour les enfants.
            z_index (int): Ordre de rendu (plus élevé = dessus).
        """
        self._relative_position = np.array((x, y), dtype=int)
        self._size = np.array((width, height), dtype=int)
        self._absolute_position = np.array((x, y), dtype=int) # Sera recalculée si parent existe
        self.parent: Optional[UIElement] = None
        self.children: List[UIElement] = []
        self.visible: bool = True
        self.z_index: int = z_index
        self.layout: Optional[LayoutManager] = layout
        self.opacity: float = 1.0
        self.scale: np.ndarray = np.array([1.0, 1.0], dtype=float)

        # Gestionnaires d'événements spécifiques à cet élément
        self.event_handlers: Dict[UIEventType, List[Callable[[UIEvent], bool]]] = {
            etype: [] for etype in UIEventType
        }

        # Attacher au parent si fourni
        if parent:
            parent.add_child(self)
        else:
            # Si pas de parent, la position absolue est la position relative initiale
            self._update_absolute_position_recursive()

        # Appliquer le layout initial si défini
        if self.layout:
            self.apply_layout()

    @property
    def relative_position(self) -> np.ndarray:
        """Position relative au coin supérieur gauche du parent."""
        return self._relative_position

    @relative_position.setter
    def relative_position(self, value: Tuple[int, int] | np.ndarray):
        if isinstance(value, tuple) and len(value) == 2 and all(isinstance(v, int) for v in value):
            new_pos = np.array(value, dtype=int)
        elif isinstance(value, np.ndarray) and value.shape == (2,):
            new_pos = value
        else:
            raise TypeError("La position relative doit être un tuple ou un ndarray numpy de deux entiers.")

        if not np.array_equal(self._relative_position, new_pos):
            self._relative_position = new_pos
            self._update_absolute_position_recursive()

    @property
    def absolute_position(self) -> np.ndarray:
        """Position absolue sur l'écran (coin supérieur gauche). Calculée."""
        return self._absolute_position

    @property
    def size(self) -> np.ndarray:
        """Taille de l'élément (largeur, hauteur)."""
        return self._size

    @size.setter
    def size(self, value: Tuple[int, int] | np.ndarray):
        if isinstance(value, tuple) and len(value) == 2 and all(isinstance(v, int) and v >= 0 for v in value):
            new_size = np.array(value, dtype=int)
        elif isinstance(value, np.ndarray) and value.shape == (2,) and np.all(value >= 0):
            new_size = value
        else:
            raise TypeError("La taille doit être un tuple ou un ndarray numpy de deux entiers positifs.")

        if not np.array_equal(self._size, new_size):
            self._size = new_size
            # Recalculer la disposition des enfants si la taille change et qu'un layout existe
            if self.layout:
                self.apply_layout()

    @property
    def width(self) -> int:
        return self._size[0]

    @width.setter
    def width(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise TypeError("La largeur doit être un entier positif.")
        self.size = (value, self._size[1])

    @property
    def height(self) -> int:
        return self._size[1]

    @height.setter
    def height(self, value: int):
        if not isinstance(value, int) or value < 0:
            raise TypeError("La hauteur doit être un entier positif.")
        self.size = (self._size[0], value)

    # --- Nouvelles propriétés pour animation/effets ---
    @property
    def opacity(self) -> float:
        return self._opacity

    @opacity.setter
    def opacity(self, value: float):
        self._opacity = max(0.0, min(1.0, float(value)))

    @property
    def scale(self) -> np.ndarray:
        return self._scale

    @scale.setter
    def scale(self, value: Tuple[float, float] | np.ndarray):
        if isinstance(value, tuple) and len(value) == 2 and all(isinstance(v, (int, float)) for v in value):
            self._scale = np.array(value, dtype=float)
        elif isinstance(value, np.ndarray) and value.shape == (2,):
            self._scale = value
        else:
            raise TypeError("L'échelle doit être un tuple ou un ndarray de deux flottants.")

    # --- Gestion Hiérarchie et Layout ---

    def add_child(self, child: 'UIElement'):
        """Ajoute un élément enfant et met à jour le layout si nécessaire."""
        if not isinstance(child, UIElement):
            raise TypeError("L'enfant doit être une instance de UIElement.")
        if child.parent is not None:
            child.parent.remove_child(child) # Détacher de l'ancien parent

        child.parent = self
        self.children.append(child)
        child._update_absolute_position_recursive() # Mettre à jour la position initiale

        # Appliquer le layout du parent à l'ensemble des enfants
        if self.layout:
            self.apply_layout()

    def remove_child(self, child: 'UIElement'):
        """Retire un élément enfant et met à jour le layout si nécessaire."""
        if child in self.children:
            child.parent = None
            self.children.remove(child)
            # La position absolue de l'enfant détaché n'est plus relative à ce parent,
            # mais sa position relative est conservée. Son absolue devient sa relative.
            child._absolute_position = child._relative_position.copy()
            # Mettre à jour les descendants de l'enfant retiré
            for grandchild in child.children:
                grandchild._update_absolute_position_recursive()

            # Mettre à jour le layout du parent après suppression
            if self.layout:
                self.apply_layout()

    def _update_absolute_position(self):
        """Met à jour la position absolue de cet élément basée sur son parent."""
        if self.parent:
            self._absolute_position = self.parent.absolute_position + self._relative_position
        else:
            self._absolute_position = self._relative_position.copy()

    def _update_absolute_position_recursive(self):
        """Met à jour la position absolue de cet élément et de tous ses descendants."""
        self._update_absolute_position()
        for child in self.children:
            child._update_absolute_position_recursive()

    def apply_layout(self):
        """Applique le layout manager aux enfants, s'il est défini."""
        if self.layout:
            self.layout.apply_layout(self)
            # Après application du layout, les positions relatives des enfants ont pu changer,
            # il faut donc mettre à jour leurs positions absolues.
            for child in self.children:
                child._update_absolute_position_recursive()

    def get_render_data(self) -> List[Dict[str, Any]]:
        """
        Génère les données à utiliser pour le rendu.
        Cette méthode de base collecte les données de tous les enfants visibles.
        Les classes dérivées peuvent ajouter leur propre rendu.
        """
        render_list = []
        if self.visible and self.opacity > 0:
            # Collecter les données de rendu des enfants visibles
            for child in self.children:
                render_list.extend(child.get_render_data())

        return render_list

    def get_texture_id(self) -> Any:
        """
        Retourne l'ID de texture pour cet élément, si applicable.
        Par défaut, retourne None. Les classes dérivées peuvent surcharger.
        """
        return None

    def on(self, event_type: UIEventType, handler: Callable[[UIEvent], bool]):
        """Ajoute un gestionnaire d'événement pour le type spécifié."""
        self.event_handlers[event_type].append(handler)

    def off(self, event_type: UIEventType, handler: Callable[[UIEvent], bool]):
        """Retire un gestionnaire d'événement pour le type spécifié."""
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)

    def _trigger_event(self, event: UIEvent) -> bool:
        """Déclenche les gestionnaires d'événements enregistrés pour ce type."""
        if event.type not in self.event_handlers:
            return False

        for handler in self.event_handlers[event.type]:
            if handler(event):
                event.handled = True
                return True
        return False

    def handle_event(self, event: UIEvent) -> bool:
        """
        Traite un événement UI et le propage aux enfants si nécessaire.
        Retourne True si l'événement a été géré.
        """
        if not self.visible:
            return False

        # Vérifier si l'événement est pertinent pour cet élément
        if not self.is_event_relevant(event):
            return False

        # Propager aux enfants d'abord (du dessus vers le dessous)
        for child in sorted(self.children, key=lambda c: -c.z_index):
            if child.handle_event(event):
                return True

        # Si aucun enfant n'a géré l'événement, essayer de le gérer soi-même
        return self._trigger_event(event)

    def is_event_relevant(self, event: UIEvent) -> bool:
        """
        Détermine si un événement est pertinent pour cet élément.
        Par exemple, pour les événements de souris, vérifie si la position est dans les limites.
        """
        if event.type in [UIEventType.MOUSE_MOTION, UIEventType.MOUSE_BUTTON_DOWN, UIEventType.MOUSE_BUTTON_UP]:
            # Vérifier si la position de la souris est à l'intérieur des limites
            mouse_pos = event.data.get('position')
            if mouse_pos:
                x, y = mouse_pos
                return (self.absolute_position[0] <= x <= self.absolute_position[0] + self.size[0] and
                        self.absolute_position[1] <= y <= self.absolute_position[1] + self.size[1])
            return False
        # Pour les autres types d'événements, considérer que c'est pertinent
        return True

    def update(self, dt: float):
        """
        Met à jour l'état de l'élément UI et de ses enfants.
        Args:
            dt (float): Temps écoulé depuis la dernière mise à jour (en secondes).
        """
        # Mettre à jour les enfants
        for child in self.children:
            child.update(dt)

# --- Panel UI ---

class Panel(UIElement):
    """
    Un conteneur rectangulaire simple pour regrouper des éléments UI.
    Peut avoir une couleur de fond ou une bordure.
    """
    def __init__(self, x=0, y=0, width=100, height=100, color=(0, 0, 0, 180), parent=None):
        """
        Initialise un panneau.
        
        Args:
            x (int): Position X relative au parent.
            y (int): Position Y relative au parent.
            width (int): Largeur du panneau.
            height (int): Hauteur du panneau.
            color (tuple): Couleur RGBA (0-255) du panneau.
            parent (UIElement, optional): Élément parent.
        """
        super().__init__(x=x, y=y, width=width, height=height, parent=parent)
        self.color = color
        self.border_color = None
        self.border_width = 0
    
    def draw(self, screen):
        """
        Dessine le panneau et ses enfants sur l'écran.
        
        Args:
            screen: Surface pygame sur laquelle dessiner.
        """
        if not self.visible or self.opacity <= 0:
            return
        
        # Créer une surface avec transparence
        panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Dessiner le fond
        if self.color:
            pygame.draw.rect(panel_surface, self.color, (0, 0, self.width, self.height))
        
        # Dessiner la bordure si nécessaire
        if self.border_color and self.border_width > 0:
            pygame.draw.rect(panel_surface, self.border_color, (0, 0, self.width, self.height), self.border_width)
        
        # Appliquer l'opacité
        if self.opacity < 1.0:
            alpha = int(255 * self.opacity)
            panel_surface.set_alpha(alpha)
        
        # Afficher le panneau
        screen.blit(panel_surface, self.absolute_position)
        
        # Dessiner les enfants
        for child in self.children:
            if hasattr(child, 'draw'):
                child.draw(screen)

# --- Label UI ---

class Label(UIElement):
    """
    Un élément UI pour afficher du texte.
    """
    def __init__(self, x=0, y=0, text="Label", font_size=20, color=(255, 255, 255), 
                 centered=False, width=None, height=None, parent=None):
        """
        Initialise une étiquette.
        
        Args:
            x (int): Position X relative au parent.
            y (int): Position Y relative au parent.
            text (str): Texte à afficher.
            font_size (int): Taille de la police.
            color (tuple): Couleur RGB (0-255) du texte.
            centered (bool): Si True, le texte est centré à la position (x, y).
            width (int, optional): Largeur explicite. Si None, déterminée par le texte.
            height (int, optional): Hauteur explicite. Si None, déterminée par le texte.
            parent (UIElement, optional): Élément parent.
        """
        # Créer la police et calculer la taille du texte si nécessaire
        self.font = pygame.font.SysFont(None, font_size)
        text_surface = self.font.render(text, True, color)
        text_width, text_height = text_surface.get_size()
        
        # Utiliser la taille calculée si non spécifiée
        if width is None:
            width = text_width
        if height is None:
            height = text_height
        
        super().__init__(x=x, y=y, width=width, height=height, parent=parent)
        
        self.text = text
        self.font_size = font_size
        self.color = color
        self.centered = centered
    
    def draw(self, screen):
        """
        Dessine l'étiquette sur l'écran.
        
        Args:
            screen: Surface pygame sur laquelle dessiner.
        """
        if not self.visible or self.opacity <= 0 or not self.text:
            return
        
        # Rendre le texte
        text_surface = self.font.render(self.text, True, self.color)
        
        # Calculer la position d'affichage
        x, y = self.absolute_position
        
        if self.centered:
            # Centrer le texte à la position spécifiée
            text_rect = text_surface.get_rect(center=(x + self.width // 2, y + self.height // 2))
            display_pos = text_rect.topleft
        else:
            # Utiliser la position directement
            display_pos = (x, y)
        
        # Appliquer l'opacité si nécessaire
        if self.opacity < 1.0:
            alpha = int(255 * self.opacity)
            text_surface.set_alpha(alpha)
        
        # Afficher le texte
        screen.blit(text_surface, display_pos)

# --- Button UI ---

class Button(UIElement):
    """
    Un bouton interactif qui peut être cliqué.
    """
    def __init__(self, x=0, y=0, width=100, height=30, text="Button", 
                 color=(100, 100, 140), hover_color=None, text_color=(255, 255, 255),
                 on_click=None, parent=None):
        """
        Initialise un bouton.
        
        Args:
            x (int): Position X relative au parent.
            y (int): Position Y relative au parent.
            width (int): Largeur du bouton.
            height (int): Hauteur du bouton.
            text (str): Texte à afficher sur le bouton.
            color (tuple): Couleur RGB (0-255) du bouton.
            hover_color (tuple, optional): Couleur du bouton lors du survol. Si None, calculée à partir de color.
            text_color (tuple): Couleur RGB (0-255) du texte.
            on_click (callable, optional): Fonction à appeler lors d'un clic.
            parent (UIElement, optional): Élément parent.
        """
        super().__init__(x=x, y=y, width=width, height=height, parent=parent)
        
        self.text = text
        self.color = color
        self.text_color = text_color
        self.on_click = on_click
        
        # Calculer une couleur de survol par défaut si non spécifiée
        if hover_color is None:
            # Plus claire que la couleur normale
            self.hover_color = tuple(min(c + 30, 255) for c in color)
        else:
            self.hover_color = hover_color
        
        # État du bouton
        self.is_hovered = False
        self.is_pressed = False
        
        # Créer la police
        self.font = pygame.font.SysFont(None, 24)
    
    def handle_event(self, event):
        """
        Gère les événements pour le bouton.
        
        Args:
            event: L'événement pygame à traiter.
            
        Returns:
            bool: True si l'événement a été traité, False sinon.
        """
        if not self.visible:
            return False
        
        # Vérifier si la souris est sur le bouton
        if hasattr(event, 'pos'):
            mouse_x, mouse_y = event.pos
            is_over = (self.absolute_position[0] <= mouse_x <= self.absolute_position[0] + self.width and
                       self.absolute_position[1] <= mouse_y <= self.absolute_position[1] + self.height)
            
            # Mise à jour de l'état du survol
            if is_over != self.is_hovered:
                self.is_hovered = is_over
                # Changer l'apparence pour le survol
            
            # Gérer les clics
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and is_over:
                self.is_pressed = True
                return True
            
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                was_pressed = self.is_pressed
                self.is_pressed = False
                
                if was_pressed and is_over and self.on_click:
                    self.on_click()
                
                return was_pressed and is_over
        
        return False
    
    def draw(self, screen):
        """
        Dessine le bouton sur l'écran.
        
        Args:
            screen: Surface pygame sur laquelle dessiner.
        """
        if not self.visible or self.opacity <= 0:
            return
        
        # Choisir la couleur selon l'état
        if self.is_pressed and self.is_hovered:
            # Couleur plus foncée pour l'état enfoncé
            button_color = tuple(max(c - 30, 0) for c in self.color)
        elif self.is_hovered:
            button_color = self.hover_color
        else:
            button_color = self.color
        
        # Créer une surface avec transparence pour le bouton
        button_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Dessiner le fond du bouton
        pygame.draw.rect(button_surface, button_color, (0, 0, self.width, self.height), border_radius=5)
        
        # Rendre le texte
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=(self.width // 2, self.height // 2))
        
        # Ajouter le texte sur le bouton
        button_surface.blit(text_surface, text_rect)
        
        # Appliquer l'opacité si nécessaire
        if self.opacity < 1.0:
            alpha = int(255 * self.opacity)
            button_surface.set_alpha(alpha)
        
        # Afficher le bouton
        screen.blit(button_surface, self.absolute_position)
        
        # Dessiner les enfants
        for child in self.children:
            if hasattr(child, 'draw'):
                child.draw(screen)

class Slider(UIElement):
    """
    A sliding control for selecting values.
    """
    def __init__(self, x=0, y=0, width=200, height=20, min_value=0.0, max_value=1.0, 
                 value=0.5, color=(80, 80, 100), handle_color=(180, 180, 220), parent=None):
        """
        Initialize a slider control.
        
        Args:
            x (int): X position relative to parent.
            y (int): Y position relative to parent.
            width (int): Width of the slider.
            height (int): Height of the slider.
            min_value (float): Minimum value of the slider.
            max_value (float): Maximum value of the slider.
            value (float): Initial value of the slider.
            color (tuple): RGB (0-255) color of the slider track.
            handle_color (tuple): RGB (0-255) color of the slider handle.
            parent (UIElement, optional): Parent element.
        """
        super().__init__(x=x, y=y, width=width, height=height, parent=parent)
        
        self.min_value = min_value
        self.max_value = max_value
        self._value = min(max(value, min_value), max_value)  # Clamp initial value
        self.color = color
        self.handle_color = handle_color
        
        # Handle properties
        self.handle_width = max(10, height)
        self.handle_height = height + 10
        
        # Interaction state
        self.is_dragging = False
    
    @property
    def value(self):
        """Get current value of the slider."""
        return self._value
    
    @value.setter
    def value(self, new_value):
        """Set the slider value, ensuring it's within bounds."""
        self._value = min(max(new_value, self.min_value), self.max_value)
    
    def _get_handle_x(self):
        """Calculate handle position from current value."""
        value_range = self.max_value - self.min_value
        if value_range == 0:
            return 0
        value_ratio = (self.value - self.min_value) / value_range
        return int(value_ratio * (self.width - self.handle_width))
    
    def _value_from_x(self, x_position):
        """Calculate value from handle position."""
        absolute_x = x_position - self.absolute_position[0]
        track_width = self.width - self.handle_width
        if track_width <= 0:
            return self.min_value
        value_ratio = max(0, min(1, absolute_x / track_width))
        return self.min_value + value_ratio * (self.max_value - self.min_value)
    
    def handle_event(self, event):
        """Handle input events for the slider."""
        if not self.visible:
            return False
        
        # Get absolute mouse position
        mouse_x, mouse_y = 0, 0
        if hasattr(event, 'pos'):
            mouse_x, mouse_y = event.pos
        
        # Calculate handle position and bounds
        handle_x = self._get_handle_x()
        abs_x, abs_y = self.absolute_position
        handle_bounds = (
            abs_x + handle_x,
            abs_y - 5,  # Slightly larger hitbox
            self.handle_width,
            self.handle_height + 10
        )
        
        # Check if mouse is over handle or track
        is_over_handle = (
            handle_bounds[0] <= mouse_x <= handle_bounds[0] + handle_bounds[2] and
            handle_bounds[1] <= mouse_y <= handle_bounds[1] + handle_bounds[3]
        )
        
        is_over_track = (
            abs_x <= mouse_x <= abs_x + self.width and
            abs_y <= mouse_y <= abs_y + self.height
        )
        
        # Handle mouse events
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                if is_over_handle:
                    self.is_dragging = True
                    return True
                elif is_over_track:
                    # Set value directly when clicking on track
                    self.value = self._value_from_x(mouse_x)
                    return True
                    
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1 and self.is_dragging:
                self.is_dragging = False
                return True
                
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                # Update value when dragging
                self.value = self._value_from_x(mouse_x)
                return True
        
        return False
    
    def draw(self, screen):
        """Draw the slider on the screen."""
        if not self.visible or self.opacity <= 0:
            return
        
        abs_x, abs_y = self.absolute_position
        
        # Draw track
        track_rect = pygame.Rect(abs_x, abs_y + (self.height // 2) - 3, self.width, 6)
        pygame.draw.rect(screen, self.color, track_rect, border_radius=3)
        
        # Draw filled portion of track
        handle_x = self._get_handle_x()
        filled_rect = pygame.Rect(abs_x, abs_y + (self.height // 2) - 3, handle_x + (self.handle_width // 2), 6)
        filled_color = tuple(min(c + 40, 255) for c in self.color)
        pygame.draw.rect(screen, filled_color, filled_rect, border_radius=3)
        
        # Draw handle
        handle_rect = pygame.Rect(
            abs_x + handle_x, 
            abs_y + (self.height // 2) - (self.handle_height // 2), 
            self.handle_width, 
            self.handle_height
        )
        pygame.draw.rect(screen, self.handle_color, handle_rect, border_radius=5)
        
        # Draw children
        for child in self.children:
            if hasattr(child, 'draw'):
                child.draw(screen)
                
    def update(self, dt):
        """Update slider logic."""
        # No animation for now, but could be added here
        pass