# src/engine/ui/ui_base.py
import numpy as np
import enum
import pygame
from typing import Callable, Dict, Any, Optional, List, Tuple

# Try to import OpenGL UI renderer
try:
    from .opengl_ui_renderer import OpenGLUIRenderer
    OPENGL_AVAILABLE = True
except ImportError:
    OPENGL_AVAILABLE = False
    print("OpenGL UI renderer not available, using fallback rendering")

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

# Global UI renderer instance
ui_renderer = None

def get_ui_renderer(width=800, height=600):
    """Get or create the global UI renderer instance"""
    global ui_renderer
    if ui_renderer is None:
        if OPENGL_AVAILABLE:
            ui_renderer = OpenGLUIRenderer(width, height)
        else:
            # Using None as a placeholder to indicate software rendering
            ui_renderer = None
    return ui_renderer

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
        self.texture_id = 0  # OpenGL texture ID for this element

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
        Les classes dérivées peuvent surcharger cette méthode.
        """
        return self.texture_id

    def on(self, event_type: UIEventType, handler: Callable[[UIEvent], bool]):
        """Enregistre un gestionnaire d'événements pour un type spécifique."""
        self.event_handlers[event_type].append(handler)
        return self  # Permet le chaînage des appels

    def off(self, event_type: UIEventType, handler: Callable[[UIEvent], bool]):
        """Retire un gestionnaire d'événements pour un type spécifique."""
        if handler in self.event_handlers[event_type]:
            self.event_handlers[event_type].remove(handler)
        return self  # Permet le chaînage des appels

    def _trigger_event(self, event) -> bool:
        """Déclenche les gestionnaires d'événements pour l'événement donné."""
        # Check if the event is a UIEvent or a pygame.event.Event
        # pygame events don't have a 'handled' attribute, so we need to handle both cases
        event_handled = getattr(event, 'handled', False)
        
        # Only process if the event hasn't been handled and the element is visible
        if not event_handled and self.visible:
            # Convert pygame.event.Event to UIEvent if needed
            if not hasattr(event, 'type') or not isinstance(event.type, UIEventType):
                # Map pygame event types to UIEventType
                event_type = None
                event_data = {}
                
                if hasattr(event, 'type'):
                    # Handle pygame mouse events
                    if event.type == pygame.MOUSEMOTION:
                        event_type = UIEventType.MOUSE_MOTION
                        event_data = {"x": event.pos[0], "y": event.pos[1]}
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        event_type = UIEventType.MOUSE_BUTTON_DOWN
                        event_data = {"x": event.pos[0], "y": event.pos[1], "button": event.button}
                    elif event.type == pygame.MOUSEBUTTONUP:
                        event_type = UIEventType.MOUSE_BUTTON_UP
                        event_data = {"x": event.pos[0], "y": event.pos[1], "button": event.button}
                    elif event.type == pygame.KEYDOWN:
                        event_type = UIEventType.KEY_DOWN
                        event_data = {"key": event.key, "unicode": getattr(event, 'unicode', '')}
                    elif event.type == pygame.KEYUP:
                        event_type = UIEventType.KEY_UP
                        event_data = {"key": event.key}
                
                # If we couldn't map the event, return False
                if event_type is None:
                    return False
                    
                # Create a UIEvent from the pygame event
                ui_event = UIEvent(event_type, event_data)
                event = ui_event
            
            # Call the handlers for this event type
            if hasattr(event, 'type') and isinstance(event.type, UIEventType):
                for handler in self.event_handlers[event.type]:
                    if handler(event):
                        if hasattr(event, 'handled'):
                            event.handled = True
                        return True
                        
                # Return whether the event was handled
                return getattr(event, 'handled', False)
        
        return False

    def handle_event(self, event) -> bool:
        """
        Gère un événement. Par défaut, l'événement est propagé aux enfants
        avant d'être traité par cet élément, donnant aux enfants la priorité.
        Les événements peuvent être consommés (traités) par les enfants avant d'arriver à nous.
        """
        if not self.visible or not self.is_event_relevant(event):
            return False

        # Propager l'événement aux enfants (parcours de l'avant à l'arrière pour la priorité)
        # Trier les enfants par z-index décroissant
        sorted_children = sorted(self.children, key=lambda child: -child.z_index)
        for child in sorted_children:
            if child.handle_event(event):
                return True

        # Si l'événement n'a pas été consommé par les enfants, le traiter
        return self._trigger_event(event)

    def is_event_relevant(self, event) -> bool:
        """
        Vérifie si un événement est pertinent pour cet élément.
        Par exemple, un événement de souris n'est pertinent que si le curseur
        est à l'intérieur de la zone de l'élément.
        Cette méthode peut être surchargée par les classes dérivées.
        """
        # For pygame events, map them to our event types
        event_type = None
        mouse_pos = None
        
        # Handle both UIEvent and pygame.event.Event
        if hasattr(event, 'type'):
            if isinstance(event.type, UIEventType):
                # It's a UIEvent
                event_type = event.type
                if event_type in [UIEventType.MOUSE_MOTION, UIEventType.MOUSE_BUTTON_DOWN, UIEventType.MOUSE_BUTTON_UP]:
                    mouse_pos = (event.data.get("x", 0), event.data.get("y", 0))
            else:
                # It's a pygame event
                if event.type == pygame.MOUSEMOTION:
                    event_type = UIEventType.MOUSE_MOTION
                    mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    event_type = UIEventType.MOUSE_BUTTON_DOWN
                    mouse_pos = event.pos
                elif event.type == pygame.MOUSEBUTTONUP:
                    event_type = UIEventType.MOUSE_BUTTON_UP
                    mouse_pos = event.pos
        
        # Check if it's a mouse event and if the mouse is inside our area
        if event_type in [UIEventType.MOUSE_MOTION, UIEventType.MOUSE_BUTTON_DOWN, UIEventType.MOUSE_BUTTON_UP] and mouse_pos:
            # Check if coordinates are inside our area
            x, y = self.absolute_position
            w, h = self.size
            return (x <= mouse_pos[0] <= x + w) and (y <= mouse_pos[1] <= y + h)
        
        # For other event types, consider them relevant by default
        return True

    def update(self, dt: float):
        """
        Met à jour l'élément UI et ses enfants.
        Par défaut, ne fait rien sauf propager l'appel aux enfants.
        """
        for child in self.children:
            child.update(dt)

    def draw(self, screen):
        """
        Draw this element using OpenGL or PyGame depending on availability.
        Override in subclasses to provide specific drawing behavior.
        """
        # Draw children by default
        if self.visible:
            for child in self.children:
                child.draw(screen)

class Panel(UIElement):
    """
    A panel UI element that can contain other UI elements.
    """
    def __init__(self, x=0, y=0, width=100, height=100, color=(0, 0, 0, 180), parent=None):
        super().__init__(x, y, width, height, parent)
        self.color = color
    
    def draw(self, screen):
        """Draw the panel"""
        if not self.visible:
            return
        
        renderer = get_ui_renderer(screen.get_width(), screen.get_height())
        
        # Use OpenGL if available
        if renderer is not None and OPENGL_AVAILABLE:
            # Draw with OpenGL
            x, y = self.absolute_position
            renderer.draw_rectangle(x, y, self.width, self.height, self.color)
        else:
            # Fallback to pygame
            x, y = self.absolute_position
            
            # Create surface with transparency if needed
            if len(self.color) > 3 and self.color[3] < 255:
                # Create transparent surface
                panel_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                pygame.draw.rect(panel_surface, self.color, (0, 0, self.width, self.height))
                screen.blit(panel_surface, (x, y))
            else:
                # Draw solid rectangle
                pygame.draw.rect(screen, self.color[:3], (x, y, self.width, self.height))
        
        # Draw children
        for child in self.children:
                child.draw(screen)

class Label(UIElement):
    """
    A text label UI element.
    """
    def __init__(self, x=0, y=0, text="Label", font_size=20, color=(255, 255, 255), 
                 centered=False, width=None, height=None, parent=None):
        """
        Initialize a text label.
        
        Args:
            x (int): X position relative to parent.
            y (int): Y position relative to parent.
            text (str): Text content to display.
            font_size (int): Font size to use.
            color (tuple): RGB (0-255) color of the text.
            centered (bool): Whether to center the text within the label bounds.
            width (int, optional): Width of the label. If None, will fit the text.
            height (int, optional): Height of the label. If None, will fit the text.
            parent (UIElement, optional): Parent element.
        """
        # Default width and height if not provided
        if width is None or height is None:
            # Create font to measure text
            font = pygame.font.SysFont(None, font_size)
            # Measure text
            text_surface = font.render(text, True, color)
            text_width, text_height = text_surface.get_size()
            
            # Use text size if width/height not specified
            if width is None:
                width = text_width
            if height is None:
                height = text_height
            
        # Initialize with calculated or provided dimensions
        super().__init__(x=x, y=y, width=width, height=height, parent=parent)
        
        self.text = text
        self.font_size = font_size
        self.color = color
        self.centered = centered
        self.font = pygame.font.SysFont(None, font_size)

    def _update_size_from_text(self):
        """Update the size of the label based on text content"""
        text_surface = self.font.render(self.text, True, self.color)
        text_width, text_height = text_surface.get_size()
        # Only update size if it's not explicitly set
        if self.width == 100:  # Default value
            self.width = text_width
        if self.height == 30:  # Default value
            self.height = text_height
    
    def draw(self, screen):
        """Draw the label"""
        if not self.visible:
            return
        
        renderer = get_ui_renderer(screen.get_width(), screen.get_height())
        x, y = self.absolute_position
        
        # Center text if requested
        if self.centered:
            text_surface = self.font.render(self.text, True, self.color)
            text_width, text_height = text_surface.get_size()
            x = x + (self.width - text_width) // 2
            y = y + (self.height - text_height) // 2
        
        # Use OpenGL if available
        if renderer is not None and OPENGL_AVAILABLE:
            # Render text with OpenGL
            renderer.render_text(self.text, self.font, self.color, x, y)
        else:
            # Fallback to pygame
            text_surface = self.font.render(self.text, True, self.color)
            screen.blit(text_surface, (x, y))

        # Draw children
        for child in self.children:
            child.draw(screen)

class Button(UIElement):
    """
    A clickable button UI element.
    """
    def __init__(self, x=0, y=0, width=100, height=30, text="Button", 
                 color=(100, 100, 140), hover_color=None, text_color=(255, 255, 255),
                 on_click=None, parent=None):
        super().__init__(x, y, width, height, parent)
        
        self.text = text
        self.color = color
        self.hover_color = hover_color or (min(color[0]+30, 255), min(color[1]+30, 255), min(color[2]+30, 255))
        self.text_color = text_color
        self.on_click = on_click
        
        # Button state
        self.hovered = False
        self.pressed = False
        
        # Create font
        self.font = pygame.font.SysFont(None, 24)
        
        # Create OpenGL texture for button (if OpenGL is available)
        self._create_textures()
    
    def _create_textures(self):
        """Create OpenGL textures for the button states"""
        renderer = get_ui_renderer()
        if not OPENGL_AVAILABLE or renderer is None:
            return
            
        # We'll create textures when needed in the draw method
        pass
    
    def handle_event(self, event):
        """Handle button events (hover, click)"""
        if not self.visible:
            return False
        
        # Process pygame events directly
        if hasattr(event, 'type') and not isinstance(event.type, UIEventType):
            # Handle mouse motion
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                x, y = self.absolute_position
                
                # Check if mouse is over the button
                was_hovered = self.hovered
                self.hovered = (x <= mouse_pos[0] <= x + self.width and y <= mouse_pos[1] <= y + self.height)
                
                # Return True if hover state changed
                return was_hovered != self.hovered
                
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                x, y = self.absolute_position
                if (x <= mouse_pos[0] <= x + self.width and y <= mouse_pos[1] <= y + self.height):
                    self.hovered = True
                    self.pressed = True
                    return True
                
            elif event.type == pygame.MOUSEBUTTONUP:
                was_pressed = self.pressed
                self.pressed = False
                
                mouse_pos = event.pos
                x, y = self.absolute_position
                self.hovered = (x <= mouse_pos[0] <= x + self.width and y <= mouse_pos[1] <= y + self.height)
                    
                # If button was pressed and mouse is still over it, trigger click event
                if was_pressed and self.hovered and self.on_click:
                    self.on_click()
                    return True
        # Process UIEvent objects
        elif hasattr(event, 'type') and isinstance(event.type, UIEventType):
            # Handle mouse motion
            if event.type == UIEventType.MOUSE_MOTION:
                mouse_x, mouse_y = event.data.get("x", 0), event.data.get("y", 0)
                x, y = self.absolute_position
                
                # Check if mouse is over the button
                was_hovered = self.hovered
                self.hovered = (x <= mouse_x <= x + self.width and y <= mouse_y <= y + self.height)
                
                # Return True if hover state changed
                return was_hovered != self.hovered
                
            elif event.type == UIEventType.MOUSE_BUTTON_DOWN:
                if self.hovered:
                    self.pressed = True
                    return True
                
            elif event.type == UIEventType.MOUSE_BUTTON_UP:
                was_pressed = self.pressed
                self.pressed = False
                    
                # If button was pressed and mouse is still over it, trigger click event
                if was_pressed and self.hovered and self.on_click:
                    self.on_click()
                    return True
                
        # Let parent handle events as well
        return super().handle_event(event)
    
    def draw(self, screen):
        """Draw the button"""
        if not self.visible:
            return
        
        renderer = get_ui_renderer(screen.get_width(), screen.get_height())
        x, y = self.absolute_position
        
        # Choose button color based on state
        button_color = self.hover_color if self.hovered else self.color
        if self.pressed:
            # Darken color when pressed
            button_color = (max(0, button_color[0]-30), max(0, button_color[1]-30), max(0, button_color[2]-30))
        
        # Use OpenGL if available
        if renderer is not None and OPENGL_AVAILABLE:
            # Draw button rectangle
            renderer.draw_rectangle(x, y, self.width, self.height, button_color)
        
            # Render button text
            text_surface = self.font.render(self.text, True, self.text_color)
            text_width, text_height = text_surface.get_size()
            text_x = x + (self.width - text_width) // 2
            text_y = y + (self.height - text_height) // 2
            renderer.render_text(self.text, self.font, self.text_color, text_x, text_y)
            
        else:
            # Fallback to pygame
            pygame.draw.rect(screen, button_color, (x, y, self.width, self.height))
            
            # Draw button text
            text_surface = self.font.render(self.text, True, self.text_color)
            text_width, text_height = text_surface.get_size()
            screen.blit(text_surface, (x + (self.width - text_width) // 2, y + (self.height - text_height) // 2))
        
        # Draw children
        for child in self.children:
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
        """Handle slider events."""
        if not self.visible:
            return False
        
        x, y = self.absolute_position
        width, height = self.size
        handle_x = self._get_handle_x()
        handle_width = self.handle_width
        
        # Calculate handle rect
        handle_rect = pygame.Rect(
            x + handle_x - handle_width//2,
            y - 5,
            handle_width,
            self.handle_height
        )
        
        # Handle pygame events directly
        if hasattr(event, 'type') and not isinstance(event.type, UIEventType):
            # Handle mouse motion
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
                
                # If dragging, update value
                if self.is_dragging:
                    relative_x = mouse_pos[0] - x
                    self.value = self._value_from_x(relative_x)
                    return True
            
            # Handle mouse button down    
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                mouse_pos = event.pos
                
                # Check if click is on the handle
                if handle_rect.collidepoint(mouse_pos):
                    self.is_dragging = True
                    return True
                
                # Check if click is on the track
                if pygame.Rect(x, y, width, height).collidepoint(mouse_pos):
                    # Set value directly based on click position
                    relative_x = mouse_pos[0] - x
                    self.value = self._value_from_x(relative_x)
                    self.is_dragging = True
                    return True
                    
            # Handle mouse button up
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:  # Left release
                if self.is_dragging:
                    self.is_dragging = False
                    return True
        
        # Process UIEvent objects
        elif hasattr(event, 'type') and isinstance(event.type, UIEventType):
            # Handle mouse events from UIEvent
            if event.type == UIEventType.MOUSE_MOTION:
                mouse_x = event.data.get("x", 0)
                mouse_y = event.data.get("y", 0)
                
                # If dragging, update value
                if self.is_dragging:
                    relative_x = mouse_x - x
                    self.value = self._value_from_x(relative_x)
                    return True
                
            elif event.type == UIEventType.MOUSE_BUTTON_DOWN:
                mouse_x = event.data.get("x", 0)
                mouse_y = event.data.get("y", 0)
                button = event.data.get("button", 1)
                
                if button == 1:  # Left click
                    # Check if click is on the handle
                    if handle_rect.collidepoint((mouse_x, mouse_y)):
                        self.is_dragging = True
                        return True
                    
                    # Check if click is on the track
                    if pygame.Rect(x, y, width, height).collidepoint((mouse_x, mouse_y)):
                        # Set value directly based on click position
                        relative_x = mouse_x - x
                        self.value = self._value_from_x(relative_x)
                        self.is_dragging = True
                        return True
                    
            elif event.type == UIEventType.MOUSE_BUTTON_UP:
                button = event.data.get("button", 1)
                if button == 1 and self.is_dragging:  # Left release
                    self.is_dragging = False
                    return True
        
        # Let parent handle events as well
        return super().handle_event(event)
    
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