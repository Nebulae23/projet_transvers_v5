import pygame

class InputManager:
    def __init__(self):
        self.key_states = {}
        self.mouse_buttons = {1: False, 2: False, 3: False} # Left, Middle, Right
        self.mouse_pos = (0, 0)
        self.quit_requested = False

    def process_events(self):
        """Traite tous les événements Pygame en attente."""
        self.quit_requested = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
            elif event.type == pygame.KEYDOWN:
                self.key_states[event.key] = True
            elif event.type == pygame.KEYUP:
                self.key_states[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.mouse_buttons[event.button] = True
            elif event.type == pygame.MOUSEBUTTONUP:
                self.mouse_buttons[event.button] = False
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos

    def is_key_pressed(self, key_code):
        """Vérifie si une touche spécifique est actuellement enfoncée."""
        return self.key_states.get(key_code, False)

    def is_mouse_button_pressed(self, button_code):
        """Vérifie si un bouton spécifique de la souris est actuellement enfoncé."""
        return self.mouse_buttons.get(button_code, False)

    def get_mouse_position(self):
        """Retourne la position actuelle du curseur de la souris."""
        return self.mouse_pos

    def is_quit_requested(self):
        """Vérifie si l'utilisateur a demandé à quitter."""
        return self.quit_requested

# Exemple d'utilisation (peut être retiré ou commenté plus tard)
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Input Manager Test")
    input_manager = InputManager()
    running = True
    while running:
        input_manager.process_events()

        if input_manager.is_quit_requested():
            running = False

        if input_manager.is_key_pressed(pygame.K_SPACE):
            print("Space bar pressed")
        if input_manager.is_mouse_button_pressed(1):
            print(f"Left mouse button pressed at {input_manager.get_mouse_position()}")

        screen.fill((0, 0, 0))
        pygame.display.flip()

    pygame.quit()