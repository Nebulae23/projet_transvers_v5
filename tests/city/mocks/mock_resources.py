# Mock pour les ressources utilisées dans les tests de la ville
class MockResources:
    def __init__(self):
        # Initialiser les ressources simulées ici
        self.resources = {}

    def get_resource(self, name):
        return self.resources.get(name, 0)

    def add_resource(self, name, amount):
        self.resources[name] = self.resources.get(name, 0) + amount

    def remove_resource(self, name, amount):
        current_amount = self.resources.get(name, 0)
        if current_amount >= amount:
            self.resources[name] = current_amount - amount
            return True
        return False

# TODO: Implémenter le mock pour les ressources