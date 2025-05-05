# src/engine/scenes/scene.py

class Scene:
    """
    Classe de base pour toutes les scènes du jeu.
    Gère les entités, la mise à jour et le rendu de la scène.
    """
    def __init__(self, world, renderer, ui_manager):
        """
        Initialise la scène.

        Args:
            world (World): L'instance du monde ECS.
            renderer (Renderer): L'instance du moteur de rendu.
            ui_manager (UIManager): Le gestionnaire d'interface utilisateur.
        """
        self.world = world
        self.renderer = renderer
        self.ui_manager = ui_manager
        self.entities = [] # Liste des entités gérées par cette scène

    def initialize(self):
        """
        Méthode appelée une fois lors du chargement de la scène.
        À surcharger par les classes filles pour initialiser les entités,
        charger les ressources spécifiques à la scène, etc.
        """
        pass

    def update(self, dt):
        """
        Met à jour la logique de la scène à chaque frame.
        À surcharger par les classes filles.

        Args:
            dt (float): Le temps écoulé depuis la dernière frame.
        """
        # Mise à jour des systèmes liés à la scène (ex: IA spécifique à la scène)
        pass

    def fixed_update(self, dt):
        """
        Met à jour la physique et d'autres systèmes à intervalles fixes.
        À surcharger par les classes filles.

        Args:
            dt (float): L'intervalle de temps fixe.
        """
        pass

    def render(self, screen=None):
        """
        Effectue le rendu de la scène.
        À surcharger par les classes filles pour dessiner les éléments spécifiques.
        
        Args:
            screen: La surface pygame sur laquelle effectuer le rendu.
                   Si None, utilise self.renderer.screen par défaut.
        """
        # Si screen n'est pas fourni, utiliser l'écran du renderer
        if screen is None and hasattr(self.renderer, 'screen'):
            screen = self.renderer.screen
            
        # Le rendu principal est géré par le Renderer global,
        # mais cette méthode peut être utilisée pour des rendus spécifiques à la scène
        # (ex: arrière-plan, effets spéciaux de scène).
        pass

    def enter(self):
        """
        Appelée lorsque la scène devient active via set_active_scene.
        Initialise la scène et prépare sa transition.
        """
        print(f"Entering scene: {self.__class__.__name__}")
        self.load()

    def exit(self):
        """
        Appelée lorsque la scène n'est plus active via set_active_scene.
        Effectue le nettoyage avant de passer à une autre scène.
        """
        print(f"Exiting scene: {self.__class__.__name__}")
        self.unload()

    def load(self):
        """
        Appelée lorsque la scène devient active.
        """
        self.initialize()
        # Potentiellement enregistrer les systèmes spécifiques à la scène auprès du World

    def unload(self):
        """
        Appelée lorsque la scène est déchargée.
        Nettoie les ressources et les entités de la scène.
        """
        # Clean up all entities managed by this scene
        for entity_id in self.entities:
            # Try various methods to delete entities depending on the actual World implementation
            try:
                # Try remove_entity first
                if hasattr(self.world, 'remove_entity'):
                    self.world.remove_entity(entity_id)
                # Try destroy_entity next
                elif hasattr(self.world, 'destroy_entity'):
                    self.world.destroy_entity(entity_id)
                # Try delete_entity last
                elif hasattr(self.world, 'delete_entity'):
                    self.world.delete_entity(entity_id)
                else:
                    # If no deletion method is found, just print a warning
                    print(f"Warning: Could not delete entity {entity_id}. No compatible delete method found in World.")
            except Exception as e:
                print(f"Error deleting entity {entity_id}: {e}")
                
        # Clear the list of entities regardless
        self.entities.clear()
        
        # Potentially unregister scene-specific systems

    def add_entity(self, entity_id):
        """
        Ajoute une entité à la gestion de la scène.

        Args:
            entity_id (int): L'ID de l'entité créée dans le World.
        """
        self.entities.append(entity_id)

    def handle_event(self, event):
        """
        Gère les événements d'entrée pour cette scène.
        
        Args:
            event: L'événement pygame à traiter.
            
        Returns:
            bool: True si l'événement a été géré, False sinon.
        """
        # Par défaut, les événements ne sont pas gérés
        return False