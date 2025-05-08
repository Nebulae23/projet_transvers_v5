#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Points of Interest System for Nightfall Defenders
Manages the generation, tracking, and interaction with various world points of interest
"""

from enum import Enum
import random
import math
from panda3d.core import Vec3, NodePath, TextNode
from direct.gui.OnscreenText import OnscreenText

class POIType(Enum):
    """Enumeration of different point of interest types"""
    DUNGEON = "dungeon"
    RESOURCE_CACHE = "resource_cache"
    MERCHANT_CAMP = "merchant_camp"
    PUZZLE_AREA = "puzzle_area"
    BOSS_ARENA = "boss_arena"
    SHRINE = "shrine"
    ABANDONED_SETTLEMENT = "abandoned_settlement"
    UNIQUE_LANDMARK = "unique_landmark"

class POIState(Enum):
    """Enumeration of point of interest states"""
    UNDISCOVERED = "undiscovered"
    DISCOVERED = "discovered"
    COMPLETED = "completed"
    AVAILABLE = "available"

class PointOfInterest:
    """Individual point of interest in the game world"""
    
    def __init__(self, poi_id, name, poi_type, position, description="", difficulty=1):
        """
        Initialize a point of interest
        
        Args:
            poi_id (str): Unique identifier for this POI
            name (str): Display name of the POI
            poi_type (POIType): Type of POI
            position (Vec3): World position
            description (str): Description shown when discovered
            difficulty (int): Difficulty level from 1-10
        """
        self.poi_id = poi_id
        self.name = name
        self.poi_type = poi_type
        self.position = position
        self.description = description
        self.difficulty = difficulty
        
        # State information
        self.state = POIState.UNDISCOVERED
        self.node_path = None
        self.discovered_time = None
        self.completed_time = None
        
        # Associated entities/objects
        self.associated_npcs = []
        self.associated_quests = []
        self.loot_tables = {}
        
        # Visual elements
        self.map_icon = None
        self.world_marker = None
        
    def create_world_representation(self, render):
        """
        Create the visual representation of this POI in the world
        
        Args:
            render: The render node to attach to
        """
        # Create a node for this POI
        self.node_path = NodePath(f"POI_{self.poi_id}")
        self.node_path.reparentTo(render)
        self.node_path.setPos(self.position)
        
        # The visual representation depends on the POI type
        try:
            if self.poi_type == POIType.DUNGEON:
                model = render.getParent().loader.loadModel("models/dungeon_entrance")
            elif self.poi_type == POIType.RESOURCE_CACHE:
                model = render.getParent().loader.loadModel("models/treasure_chest")
            elif self.poi_type == POIType.MERCHANT_CAMP:
                model = render.getParent().loader.loadModel("models/tent")
            elif self.poi_type == POIType.PUZZLE_AREA:
                model = render.getParent().loader.loadModel("models/stone_circle")
            elif self.poi_type == POIType.BOSS_ARENA:
                model = render.getParent().loader.loadModel("models/boss_gate")
            elif self.poi_type == POIType.SHRINE:
                model = render.getParent().loader.loadModel("models/shrine")
            elif self.poi_type == POIType.ABANDONED_SETTLEMENT:
                model = render.getParent().loader.loadModel("models/ruins")
            elif self.poi_type == POIType.UNIQUE_LANDMARK:
                model = render.getParent().loader.loadModel("models/landmark")
            else:
                # Fallback for unknown types
                model = render.getParent().loader.loadModel("models/box")
                
            # Apply model-specific scaling and offset
            if self.poi_type == POIType.DUNGEON:
                model.setScale(2.0)
                model.setPos(0, 0, 0)
            elif self.poi_type == POIType.RESOURCE_CACHE:
                model.setScale(0.8)
                model.setPos(0, 0, 0.4)
            else:
                model.setScale(1.0)
                
            model.reparentTo(self.node_path)
                
        except Exception as e:
            print(f"Error loading model for POI {self.name}: {e}")
            # Use a default cube if model loading fails
            from panda3d.core import CardMaker
            cm = CardMaker("poi_marker")
            cm.setFrame(-1, 1, 0, 2)
            marker = self.node_path.attachNewNode(cm.generate())
            marker.setColor(0.8, 0.1, 0.1, 1)  # Red marker
            marker.setBillboardPointEye()
        
        # Add name text above the POI (only visible when nearby or discovered)
        if self.state != POIState.UNDISCOVERED:
            self._create_name_display()
            
        # If undiscovered, hide or partially hide the POI
        if self.state == POIState.UNDISCOVERED:
            # Make it invisible until discovered or special conditions are met
            self.node_path.hide()
        
        return self.node_path
            
    def _create_name_display(self):
        """Create a floating name display above the POI"""
        if self.node_path:
            # Text node to display the name
            text_node = TextNode(f"POI_text_{self.poi_id}")
            text_node.setText(self.name)
            text_node.setAlign(TextNode.ACenter)
            text_node.setTextColor(1, 1, 0.8, 1)  # Yellowish text
            text_node.setShadow(0.05, 0.05)
            text_node.setShadowColor(0, 0, 0, 1)
            
            # Create a node path for the text
            text_np = self.node_path.attachNewNode(text_node)
            text_np.setScale(0.5)
            text_np.setPos(0, 0, 2)  # Position above the POI
            text_np.setBillboardPointEye()  # Make it always face the camera
            
            # Store the text node path
            self.name_display = text_np
    
    def discover(self, discovery_time=None):
        """
        Mark this POI as discovered
        
        Args:
            discovery_time: Game time when discovered
        """
        self.state = POIState.DISCOVERED
        self.discovered_time = discovery_time
        
        # If we have a node path, update its appearance for discovered state
        if self.node_path:
            self.node_path.show()
            self._create_name_display()
    
    def complete(self, completion_time=None):
        """
        Mark this POI as completed
        
        Args:
            completion_time: Game time when completed
        """
        self.state = POIState.COMPLETED
        self.completed_time = completion_time
        
        # If we have a node path, update its appearance for completed state
        if self.node_path and hasattr(self, 'name_display'):
            # Change text color to indicate completion
            text_node = self.name_display.node()
            text_node.setTextColor(0.8, 0.8, 0.8, 1)  # Gray out the text
            
            # Could also add a completion marker
            from panda3d.core import CardMaker
            cm = CardMaker("completed_marker")
            cm.setFrame(-0.5, 0.5, -0.5, 0.5)
            marker = self.node_path.attachNewNode(cm.generate())
            marker.setColor(0, 1, 0, 1)  # Green checkmark
            marker.setPos(0, 0, 2.5)
            marker.setBillboardPointEye()
    
    def add_associated_quest(self, quest_id):
        """Add a quest associated with this POI"""
        if quest_id not in self.associated_quests:
            self.associated_quests.append(quest_id)
    
    def add_associated_npc(self, npc_id):
        """Add an NPC associated with this POI"""
        if npc_id not in self.associated_npcs:
            self.associated_npcs.append(npc_id)
    
    def set_loot_table(self, difficulty_tier, loot_table):
        """Set the loot table for a specific difficulty tier"""
        self.loot_tables[difficulty_tier] = loot_table
    
    def get_loot_table(self, player_level=None):
        """Get the appropriate loot table based on player level"""
        if not player_level:
            return self.loot_tables.get(self.difficulty, {})
            
        # Find the closest difficulty tier that doesn't exceed player level
        valid_tiers = [tier for tier in self.loot_tables.keys() if tier <= player_level]
        if not valid_tiers:
            return {}
            
        return self.loot_tables[max(valid_tiers)]
        
    def get_distance_to(self, position):
        """Get distance to another position"""
        return (self.position - position).length()
    
    def is_within_range(self, position, range_distance):
        """Check if a position is within range of this POI"""
        return self.get_distance_to(position) <= range_distance


class PointOfInterestManager:
    """Manages all points of interest in the game world"""
    
    def __init__(self, game):
        """
        Initialize the POI manager
        
        Args:
            game: The main game instance
        """
        self.game = game
        self.points_of_interest = {}
        self.discovery_range = 50.0  # Distance at which POIs are automatically discovered
        self.poi_density = 0.01  # POIs per square unit of world area
        self.minimum_poi_distance = 100.0  # Minimum distance between POIs
        
        # Discovery effects
        self.discovery_sfx = None
        try:
            self.discovery_sfx = game.loader.loadSfx("sounds/sfx/discovery.wav")
        except:
            print("Could not load discovery sound effect")
        
    def create_poi(self, poi_id, name, poi_type, position, description="", difficulty=1):
        """
        Create a new point of interest
        
        Args:
            poi_id: Unique identifier
            name: Display name
            poi_type: Type of POI
            position: World position
            description: Description
            difficulty: Difficulty level (1-10)
            
        Returns:
            PointOfInterest: The created POI object
        """
        poi = PointOfInterest(poi_id, name, poi_type, position, description, difficulty)
        self.points_of_interest[poi_id] = poi
        return poi
    
    def generate_pois_for_region(self, region_min, region_max, world_seed=None):
        """
        Generate points of interest in a region
        
        Args:
            region_min (Vec3): Minimum corner of region
            region_max (Vec3): Maximum corner of region
            world_seed: Seed for random generation
            
        Returns:
            list: List of generated POI objects
        """
        if world_seed:
            random.seed(world_seed)
            
        # Calculate region dimensions
        width = region_max.x - region_min.x
        depth = region_max.y - region_min.y
        area = width * depth
        
        # Calculate number of POIs based on density
        num_pois = max(1, int(area * self.poi_density))
        
        generated_pois = []
        
        # Generate POIs
        for i in range(num_pois):
            # Attempt to place POI with minimum distance from others
            max_attempts = 20
            for attempt in range(max_attempts):
                # Generate random position
                x = region_min.x + random.random() * width
                y = region_min.y + random.random() * depth
                z = 0  # We'll assume ground level for now
                
                position = Vec3(x, y, z)
                
                # Check distance from other POIs
                too_close = False
                for poi in generated_pois:
                    if (poi.position - position).length() < self.minimum_poi_distance:
                        too_close = True
                        break
                
                if not too_close:
                    # Position is acceptable, create the POI
                    poi_type = random.choice(list(POIType))
                    difficulty = min(10, max(1, int(random.gauss(5, 2))))
                    
                    # Generate a name based on type and region
                    name = self._generate_poi_name(poi_type)
                    
                    # Generate a unique ID
                    poi_id = f"poi_{len(self.points_of_interest)+1}_{poi_type.value}"
                    
                    # Create and add the POI
                    poi = self.create_poi(poi_id, name, poi_type, position, difficulty=difficulty)
                    generated_pois.append(poi)
                    break
        
        return generated_pois
    
    def _generate_poi_name(self, poi_type):
        """Generate a name for a POI based on its type"""
        if poi_type == POIType.DUNGEON:
            prefixes = ["Dark", "Forgotten", "Ancient", "Cursed", "Hidden", "Lost"]
            nouns = ["Cavern", "Crypt", "Dungeon", "Catacomb", "Vault", "Chamber"]
            return f"{random.choice(prefixes)} {random.choice(nouns)}"
            
        elif poi_type == POIType.RESOURCE_CACHE:
            owners = ["Bandit's", "Merchant's", "Explorer's", "Hunter's", "Traveler's"]
            types = ["Cache", "Stash", "Hideout", "Treasure", "Supplies"]
            return f"{random.choice(owners)} {random.choice(types)}"
            
        elif poi_type == POIType.MERCHANT_CAMP:
            adjectives = ["Wandering", "Exotic", "Mysterious", "Well-stocked", "Shrewd"]
            types = ["Trader's Camp", "Merchant's Outpost", "Market", "Bazaar", "Trading Post"]
            return f"{random.choice(adjectives)} {random.choice(types)}"
            
        elif poi_type == POIType.PUZZLE_AREA:
            adjectives = ["Mysterious", "Ancient", "Enigmatic", "Arcane", "Puzzling"]
            types = ["Stones", "Monument", "Structure", "Formation", "Ruins"]
            return f"{random.choice(adjectives)} {random.choice(types)}"
            
        elif poi_type == POIType.BOSS_ARENA:
            owners = ["Dragon's", "Giant's", "Titan's", "Demon's", "Overlord's"]
            types = ["Lair", "Arena", "Stronghold", "Domain", "Throne"]
            return f"{random.choice(owners)} {random.choice(types)}"
            
        elif poi_type == POIType.SHRINE:
            elements = ["Sun", "Moon", "Earth", "Water", "Fire", "Wind"]
            types = ["Shrine", "Altar", "Temple", "Sanctuary", "Monument"]
            return f"{random.choice(elements)} {random.choice(types)}"
            
        elif poi_type == POIType.ABANDONED_SETTLEMENT:
            adjectives = ["Deserted", "Ruined", "Abandoned", "Forgotten", "Ancient"]
            types = ["Village", "Outpost", "Settlement", "Town", "Encampment"]
            return f"{random.choice(adjectives)} {random.choice(types)}"
            
        elif poi_type == POIType.UNIQUE_LANDMARK:
            adjectives = ["Towering", "Majestic", "Breathtaking", "Infamous", "Legendary"]
            types = ["Spire", "Mountain", "Waterfall", "Canyon", "Monument"]
            return f"The {random.choice(adjectives)} {random.choice(types)}"
            
        else:
            return f"Unknown Location {random.randint(100, 999)}"
    
    def update(self, player_position):
        """
        Update the POI manager, checking for discoveries
        
        Args:
            player_position: Current player position
        """
        # Check for POI discoveries based on player proximity
        for poi_id, poi in self.points_of_interest.items():
            if poi.state == POIState.UNDISCOVERED:
                if poi.is_within_range(player_position, self.discovery_range):
                    self._discover_poi(poi)
    
    def _discover_poi(self, poi):
        """Handle POI discovery logic and effects"""
        poi.discover(self.game.day_night_cycle.current_time)
        
        # Play discovery sound
        if self.discovery_sfx:
            self.discovery_sfx.play()
        
        # Show discovery message
        self._show_discovery_message(poi)
        
        # Update minimap
        if hasattr(self.game, 'minimap') and self.game.minimap:
            self.game.minimap.add_poi_marker(poi)
        
        # Trigger any discovery-related quests
        if hasattr(self.game, 'quest_system') and self.game.quest_system:
            self.game.quest_system.on_poi_discovered(poi)
    
    def _show_discovery_message(self, poi):
        """Show an on-screen message for discovery"""
        # Create a text message
        message = f"Discovered: {poi.name}"
        
        # If the game has a message system, use it
        if hasattr(self.game, 'message_system') and self.game.message_system:
            self.game.message_system.show_message(message, duration=4.0, message_type="discovery")
        else:
            # Create a simple on-screen message
            text = OnscreenText(
                text=message,
                pos=(0, 0.2),
                scale=0.07,
                fg=(1, 1, 0.8, 1),
                shadow=(0, 0, 0, 0.5),
                mayChange=True
            )
            # Remove after 4 seconds
            taskMgr = self.game.taskMgr
            taskMgr.doMethodLater(4.0, lambda task: text.destroy(), "remove_poi_msg")
    
    def get_nearest_poi(self, position, max_distance=float('inf'), filter_type=None, filter_state=None):
        """
        Get the nearest POI to a position
        
        Args:
            position: The position to check from
            max_distance: Maximum distance to consider
            filter_type: Optional POIType to filter by
            filter_state: Optional POIState to filter by
            
        Returns:
            PointOfInterest or None: The nearest POI, or None if none found
        """
        nearest_poi = None
        nearest_distance = max_distance
        
        for poi_id, poi in self.points_of_interest.items():
            # Apply filters
            if filter_type and poi.poi_type != filter_type:
                continue
                
            if filter_state and poi.state != filter_state:
                continue
            
            # Check distance
            distance = poi.get_distance_to(position)
            if distance < nearest_distance:
                nearest_poi = poi
                nearest_distance = distance
        
        return nearest_poi
    
    def get_pois_in_radius(self, position, radius, filter_type=None, filter_state=None):
        """
        Get all POIs within a radius
        
        Args:
            position: The position to check from
            radius: The radius to check within
            filter_type: Optional POIType to filter by
            filter_state: Optional POIState to filter by
            
        Returns:
            list: List of POIs within the radius
        """
        result = []
        
        for poi_id, poi in self.points_of_interest.items():
            # Apply filters
            if filter_type and poi.poi_type != filter_type:
                continue
                
            if filter_state and poi.state != filter_state:
                continue
            
            # Check distance
            if poi.is_within_range(position, radius):
                result.append(poi)
        
        return result
    
    def show_all_pois(self):
        """Force all POIs to be visible (for debugging or special abilities)"""
        for poi_id, poi in self.points_of_interest.items():
            if poi.state == POIState.UNDISCOVERED:
                poi.discover()
                
            # Ensure world representation exists
            if not poi.node_path and hasattr(self.game, 'render'):
                poi.create_world_representation(self.game.render)
    
    def save_data(self):
        """
        Create a serializable data representation of all POIs
        
        Returns:
            dict: Serializable POI data
        """
        data = {
            "pois": {}
        }
        
        for poi_id, poi in self.points_of_interest.items():
            poi_data = {
                "id": poi.poi_id,
                "name": poi.name,
                "type": poi.poi_type.value,
                "position": [poi.position.x, poi.position.y, poi.position.z],
                "description": poi.description,
                "difficulty": poi.difficulty,
                "state": poi.state.value,
                "discovered_time": poi.discovered_time,
                "completed_time": poi.completed_time,
                "associated_quests": poi.associated_quests,
                "associated_npcs": poi.associated_npcs
            }
            data["pois"][poi_id] = poi_data
        
        return data
    
    def load_data(self, data):
        """
        Load POIs from serialized data
        
        Args:
            data: Serialized POI data
        """
        if "pois" not in data:
            return
            
        # Clear existing POIs
        self.points_of_interest = {}
        
        # Load POIs from data
        for poi_id, poi_data in data["pois"].items():
            position = Vec3(
                poi_data["position"][0],
                poi_data["position"][1],
                poi_data["position"][2]
            )
            
            poi = PointOfInterest(
                poi_data["id"],
                poi_data["name"],
                POIType(poi_data["type"]),
                position,
                poi_data["description"],
                poi_data["difficulty"]
            )
            
            # Set state
            poi.state = POIState(poi_data["state"])
            poi.discovered_time = poi_data["discovered_time"]
            poi.completed_time = poi_data["completed_time"]
            
            # Set associations
            poi.associated_quests = poi_data["associated_quests"]
            poi.associated_npcs = poi_data["associated_npcs"]
            
            # Add to manager
            self.points_of_interest[poi_id] = poi 