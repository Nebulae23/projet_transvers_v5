# src/engine/ui/ui_events.py
from typing import List, Dict, Callable, Any, Optional
from enum import Enum
import pygame

class UIEventType(Enum):
    CLICK = "click"
    HOVER = "hover"
    KEY = "key"
    CLOSE = "close"
    OPEN = "open"

class UIEvent:
    def __init__(self, event_type: UIEventType, data: Any = None):
        self.type = event_type
        self.data = data
        self.handled = False

class UIEventHandler:
    def __init__(self):
        self.listeners: Dict[UIEventType, List[Callable[[UIEvent], None]]] = {
            event_type: [] for event_type in UIEventType
        }
        
    def add_listener(self, 
                    event_type: UIEventType,
                    callback: Callable[[UIEvent], None]):
        self.listeners[event_type].append(callback)
        
    def remove_listener(self,
                       event_type: UIEventType,
                       callback: Callable[[UIEvent], None]):
        if callback in self.listeners[event_type]:
            self.listeners[event_type].remove(callback)
            
    def dispatch_event(self, event: UIEvent):
        for listener in self.listeners[event.type]:
            listener(event)
            if event.handled:
                break

class UIInputHandler:
    def __init__(self, event_handler: UIEventHandler):
        self.event_handler = event_handler
        self.active_element = None
        
    def handle_input(self, pygame_event: pygame.event.Event):
        if pygame_event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_click(pygame_event.pos)
        elif pygame_event.type == pygame.MOUSEMOTION:
            self._handle_hover(pygame_event.pos)
        elif pygame_event.type == pygame.KEYDOWN:
            self._handle_key(pygame_event.key)
            
    def _handle_click(self, position: Tuple[int, int]):
        event = UIEvent(UIEventType.CLICK, position)
        self.event_handler.dispatch_event(event)
        
    def _handle_hover(self, position: Tuple[int, int]):
        event = UIEvent(UIEventType.HOVER, position)
        self.event_handler.dispatch_event(event)
        
    def _handle_key(self, key: int):
        event = UIEvent(UIEventType.KEY, key)
        self.event_handler.dispatch_event(event)