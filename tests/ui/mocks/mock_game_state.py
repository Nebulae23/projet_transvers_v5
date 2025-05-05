# Mock pour l'état global du jeu
class MockGameState:
    def __init__(self):
        # Simuler les différentes parties de l'état du jeu nécessaires pour l'UI
        self.player_stats = {
            'health': 100,
            'max_health': 100,
            'mana': 50,
            'max_mana': 50,
            'stamina': 80,
            'max_stamina': 100,
            'level': 5,
            'xp': 120,
            'xp_to_next_level': 200
        }
        self.inventory = {
            'items': [], # Liste d'objets simulés
            'gold': 150
        }
        self.active_quests = [] # Liste de quêtes simulées
        self.current_map = "Test Map"
        self.game_time = "12:00 PM" # Heure simulée
        self.is_paused = False
        self.current_menu = None # Pour suivre quel menu est actif

        # Ajoutez d'autres états si nécessaire pour les tests UI
        # self.skill_points_available = 3
        # self.learned_skills = set()

    def get_player_stat(self, stat_name):
        """Retourne une statistique spécifique du joueur."""
        return self.player_stats.get(stat_name)

    def get_inventory_items(self):
        """Retourne les objets de l'inventaire."""
        return self.inventory['items']

    def get_gold(self):
        """Retourne l'or du joueur."""
        return self.inventory['gold']

    def set_pause_state(self, paused):
        """Définit l'état de pause du jeu."""
        self.is_paused = paused

    def set_current_menu(self, menu_instance):
        """Définit le menu actuellement affiché."""
        self.current_menu = menu_instance

    # Méthodes pour modifier l'état pour les tests
    def update_player_stat(self, stat_name, value):
        if stat_name in self.player_stats:
            self.player_stats[stat_name] = value

    def add_item_to_inventory(self, item):
        self.inventory['items'].append(item)

    def remove_item_from_inventory(self, item_id):
        self.inventory['items'] = [item for item in self.inventory['items'] if item.get('id') != item_id]