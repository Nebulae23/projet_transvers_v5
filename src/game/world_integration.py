#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
World Integration Module for Nightfall Defenders
Connects and initializes all the new world systems
"""

from panda3d.core import Vec3

from game.points_of_interest import PointOfInterestManager, POIType
from game.npc_system import NPCManager, NPCType, DialogueType
from game.quest_system import QuestManager, QuestType, QuestObjective, ObjectiveType
from game.boss_patterns import BossPatternSystem, PatternType, BossPhase
from game.challenge_mode import ChallengeSystem
# Import city automation system
from game.city_automation import CityGrid, ResourceManager, BuildingType, ResourceType
from game.city_buildings import create_building

class WorldIntegration:
    """Handles the integration of world systems into the main game"""
    
    def __init__(self, game):
        """
        Initialize the world integration
        
        Args:
            game: The main game instance
        """
        self.game = game
        
        # Initialize all managers if they don't exist
        if not hasattr(game, 'poi_manager'):
            game.poi_manager = PointOfInterestManager(game)
            
        if not hasattr(game, 'npc_manager'):
            game.npc_manager = NPCManager(game)
            
        if not hasattr(game, 'quest_manager'):
            game.quest_manager = QuestManager(game)
            
        if not hasattr(game, 'challenge_system'):
            game.challenge_system = ChallengeSystem(game)
            
        # Initialize city automation system
        if not hasattr(game, 'city_manager'):
            self._initialize_city_automation()
    
    def _initialize_city_automation(self):
        """Initialize the city automation system"""
        # Create a simple city manager implementation
        class CityManager:
            def __init__(self, game):
                self.game = game
                self.grid = CityGrid(50, 50)  # 50x50 grid for the city
                self.resource_manager = ResourceManager()
                self.buildings = {}
                self.next_building_id = 1
                
                # Building placement information
                self.city_center = (25, 25)  # Center of the city grid
                
                # Visual representation
                self.render = None
                if hasattr(game, 'render'):
                    self.render = game.render
                
                # Initialize terrain
                self.grid.initialize_terrain()
                
                # Add initial resources
                for resource_type in ResourceType:
                    self.resource_manager.add_resource(resource_type, 100)
            
            def update(self, dt):
                """Update city state"""
                # Update resource manager
                self.resource_manager.update(dt)
                
                # Update all buildings
                for building in self.buildings.values():
                    building.update(dt, self)
            
            def create_building(self, building_type, position):
                """Create a new building"""
                building_id = f"building_{self.next_building_id}"
                self.next_building_id += 1
                
                building = create_building(building_type, building_id, position)
                
                # Try to place on grid
                if self.grid.place_building(building):
                    self.buildings[building_id] = building
                    
                    # Create visual representation if render is available
                    if self.render:
                        building.create_visual_representation(self.render, self)
                        
                    return building
                
                return None
            
            def destroy_building(self, building_id):
                """Destroy a building"""
                if building_id in self.buildings:
                    building = self.buildings[building_id]
                    
                    # Remove visual representation
                    if building.node_path:
                        building.node_path.removeNode()
                    
                    # Remove from grid
                    self.grid.remove_building(building)
                    del self.buildings[building_id]
                    return True
                
                return False
            
            def grid_to_world(self, grid_pos):
                """Convert grid position to world position"""
                # Convert from city grid to world coordinates
                # This will depend on how your world is set up
                return (grid_pos[0] * 2 - 50, grid_pos[1] * 2 - 50, 0)
            
            def world_to_grid(self, world_pos):
                """Convert world position to grid position"""
                # Convert from world coordinates to city grid
                x = int((world_pos.x + 50) / 2)
                y = int((world_pos.y + 50) / 2)
                return (x, y)
            
            def on_building_completed(self, building):
                """Handle building completion"""
                print(f"Building completed: {building.name}")
                
                # Update resource rates
                for resource_type, amount in building.production.items():
                    self.resource_manager.update_rate(resource_type, amount)
                    
                for resource_type, amount in building.consumption.items():
                    self.resource_manager.update_rate(resource_type, -amount)
                    
                # Update storage capacity
                for resource_type, amount in building.storage.items():
                    self.resource_manager.increase_capacity(resource_type, amount)
                
                # Update visual effects
                if self.render and building.node_path:
                    building._update_visual_effects(self)
            
            def on_building_upgraded(self, building):
                """Handle building upgrade"""
                print(f"Building upgraded: {building.name} to level {building.level}")
                
                # Update resource rates based on changes from upgrade
                # This is simplified and would need to track previous rates
                for resource_type, amount in building.production.items():
                    # Assume production increased by 30%
                    self.resource_manager.update_rate(resource_type, amount * 0.3)
                    
                for resource_type, amount in building.consumption.items():
                    # Assume consumption increased by 20%
                    self.resource_manager.update_rate(resource_type, -amount * 0.2)
                
                # Update visual effects
                if self.render and building.node_path:
                    building._update_visual_effects(self)
            
            def on_building_destroyed(self, building):
                """
                Handle building destruction
                
                Args:
                    building: The destroyed building
                """
                print(f"City manager handling destruction of {building.name}")
                
                # We don't remove the building from the grid or buildings list
                # so the rubble remains visible, but we mark it as destroyed
                
                # Trigger any city-wide effects or events
                if hasattr(self.game, 'event_manager'):
                    self.game.event_manager.trigger_event('building_destroyed', {
                        'building': building,
                        'position': building.position,
                        'building_type': building.building_type
                    })
                
                # Check city defense impact
                if building.building_type in [BuildingType.TOWER, BuildingType.WALL, BuildingType.GATE]:
                    print("Warning: City defenses have been weakened!")
                    
                # Check if vital building (could trigger game over or major events)
                if building.building_type == BuildingType.HOUSE:
                    # Population impact when housing is destroyed
                    self.resource_manager.consume_resource(ResourceType.POPULATION, 
                                                           min(5, self.resource_manager.get_resource(ResourceType.POPULATION)))
                    print("Housing destroyed! Population decreased.")
            
            def damage_building(self, building, amount, source=None):
                """
                Damage a building and handle destruction if needed
                
                Args:
                    building: The building to damage
                    amount: Amount of damage
                    source: Entity that caused the damage (optional)
                    
                Returns:
                    bool: True if building was destroyed
                """
                was_destroyed = building.take_damage(amount, source)
                
                if was_destroyed:
                    building.on_destroyed(self)
                elif building.state == BuildingState.DAMAGED and building.node_path:
                    # Update visual effects to show damage
                    building._update_visual_effects(self)
                    
                return was_destroyed
            
            def create_visual_representations(self):
                """Create visual representations for all buildings"""
                if not self.render:
                    return
                    
                # Create grid visualization
                self.grid.create_visual_representation(self.render)
                
                # Create building visualizations
                for building in self.buildings.values():
                    building.create_visual_representation(self.render, self)
            
            def setup_starting_city(self):
                """Set up the starting city layout"""
                # Create initial buildings for city center
                # House at center
                house = self.create_building(BuildingType.HOUSE, self.city_center)
                if house:
                    house.construction_progress = 100
                    house._on_construction_complete(self)
                    house.assign_workers(3)
                
                # Farm nearby
                farm_pos = (self.city_center[0] + 3, self.city_center[1])
                farm = self.create_building(BuildingType.FARM, farm_pos)
                if farm:
                    farm.construction_progress = 100
                    farm._on_construction_complete(self)
                    farm.assign_workers(5)
                
                # Storage
                storage_pos = (self.city_center[0], self.city_center[1] + 3)
                storage = self.create_building(BuildingType.STORAGE, storage_pos)
                if storage:
                    storage.construction_progress = 100
                    storage._on_construction_complete(self)
                
                # Defense tower
                tower_pos = (self.city_center[0] - 3, self.city_center[1])
                tower = self.create_building(BuildingType.TOWER, tower_pos)
                if tower:
                    tower.construction_progress = 100
                    tower._on_construction_complete(self)
                    tower.assign_workers(2)
        
        # Create and initialize the city manager
        self.game.city_manager = CityManager(self.game)
        
        # Set up the starting city
        self.game.city_manager.setup_starting_city()
    
    def setup_world(self, world_seed=None):
        """
        Set up the game world with POIs, NPCs, and quests
        
        Args:
            world_seed: Seed for random generation
        """
        # Define world boundaries
        world_min = Vec3(-500, -500, 0)
        world_max = Vec3(500, 500, 0)
        
        # Generate POIs
        self._generate_pois(world_min, world_max, world_seed)
        
        # Create NPCs
        self._create_npcs()
        
        # Set up quests
        self._create_quests()
        
        # Configure boss patterns
        self._configure_boss_patterns()
        
        print("World integration complete!")
    
    def _generate_pois(self, world_min, world_max, world_seed):
        """Generate points of interest in the world"""
        print("Generating points of interest...")
        
        # Generate POIs for the entire world
        self.game.poi_manager.generate_pois_for_region(world_min, world_max, world_seed)
        
        # Create some hand-placed important POIs
        self._create_important_pois()
    
    def _create_important_pois(self):
        """Create important hand-placed POIs"""
        # Main dungeon
        dungeon = self.game.poi_manager.create_poi(
            "main_dungeon",
            "The Ancient Catacombs",
            POIType.DUNGEON,
            Vec3(200, 200, 0),
            "A vast underground complex filled with powerful enemies and ancient treasures.",
            difficulty=8
        )
        
        # Trader outpost
        trader = self.game.poi_manager.create_poi(
            "trader_outpost",
            "Wayfarer's Rest",
            POIType.MERCHANT_CAMP,
            Vec3(-150, 100, 0),
            "A small trading post where merchants gather to sell their goods.",
            difficulty=2
        )
        
        # Major boss arena
        arena = self.game.poi_manager.create_poi(
            "dragon_lair",
            "Dragon's Peak",
            POIType.BOSS_ARENA,
            Vec3(-300, -250, 0),
            "An imposing mountain peak where a fearsome dragon makes its lair.",
            difficulty=10
        )
        
        # Ancient shrine
        shrine = self.game.poi_manager.create_poi(
            "ancient_shrine",
            "Forgotten Shrine",
            POIType.SHRINE,
            Vec3(50, -200, 0),
            "A mystical shrine dedicated to forgotten gods, imbued with strange powers.",
            difficulty=5
        )
    
    def _create_npcs(self):
        """Create NPCs in the world"""
        print("Creating NPCs...")
        
        # Main quest giver
        quest_giver = self.game.npc_manager.create_npc(
            "elder_maya",
            "Elder Maya",
            NPCType.QUEST_GIVER,
            Vec3(5, 10, 0),
            "models/elder"
        )
        
        # Add dialogues
        quest_giver.add_dialogue(DialogueType.GREETING, "Welcome, defender. Our city needs your help in these dark times.")
        quest_giver.add_dialogue(DialogueType.GREETING, "The night creatures grow bolder with each passing day. We're fortunate to have you with us.")
        quest_giver.add_dialogue(DialogueType.QUEST_OFFER, "The ancient catacombs have been overrun with monsters. Can you clear them out?")
        quest_giver.add_dialogue(DialogueType.QUEST_PROGRESS, "How goes your expedition into the catacombs?")
        quest_giver.add_dialogue(DialogueType.QUEST_COMPLETE, "You've done a great service to our city. Please accept this reward.")
        quest_giver.add_lore_dialogue("This city has stood for centuries, but never have we faced such darkness as we do now.")
        quest_giver.add_lore_dialogue("Legends speak of an ancient evil that rises when the balance between day and night is disturbed.")
        
        # Add a new NPC that talks about the city
        city_planner = self.game.npc_manager.create_npc(
            "planner_theo",
            "Planner Theo",
            NPCType.QUEST_GIVER,
            Vec3(0, 15, 0),
            "models/planner"
        )
        
        # Add dialogues about city building
        city_planner.add_dialogue(DialogueType.GREETING, "Greetings, traveler. I oversee the development of our city's infrastructure.")
        city_planner.add_dialogue(DialogueType.GREETING, "As our city grows, we must plan carefully. Resources are limited, but our needs are many.")
        city_planner.add_lore_dialogue("The city walls are our first line of defense against the night creatures.")
        city_planner.add_lore_dialogue("We need more farms to support our growing population.")
        
        # Add a city-related quest
        city_planner.add_dialogue(DialogueType.QUEST_OFFER, "Our food supplies are running low. We need to build more farms to sustain our population.")
        city_planner.add_dialogue(DialogueType.QUEST_PROGRESS, "How is the farm construction progressing?")
        city_planner.add_dialogue(DialogueType.QUEST_COMPLETE, "Excellent work! Our food situation is much improved now.")
        
        # Merchant
        merchant = self.game.npc_manager.create_npc(
            "trader_finn",
            "Trader Finn",
            NPCType.MERCHANT,
            Vec3(-5, 15, 0),
            "models/merchant"
        )
        
        # Add items and dialogue
        merchant.add_dialogue(DialogueType.GREETING, "Got some rare goods for sale today!")
        merchant.add_dialogue(DialogueType.GREETING, "Well met, traveler! Looking to trade?")
        merchant.add_dialogue(DialogueType.MERCHANT_DIALOGUE, "These items are hard to come by. You won't find better prices anywhere else.")
        merchant.add_dialogue(DialogueType.MERCHANT_DIALOGUE, "I've got just what you need for your adventures.")
        merchant.add_merchant_item("health_potion", 10, 5)
        merchant.add_merchant_item("damage_boost", 25, 2)
        merchant.add_merchant_item("rare_crystal", 50, 1)
        
        # Trainer
        trainer = self.game.npc_manager.create_npc(
            "master_kora",
            "Master Kora",
            NPCType.TRAINER,
            Vec3(15, 5, 0),
            "models/trainer"
        )
        
        # Add training services
        trainer.add_dialogue(DialogueType.GREETING, "Seeking to improve your skills? You've come to the right place.")
        trainer.add_dialogue(DialogueType.GREETING, "Only through discipline and training can one truly master the art of combat.")
        trainer.add_dialogue(DialogueType.TRAINING_DIALOGUE, "I can teach you techniques that will give you an edge in battle.")
        trainer.add_training_service("double_strike", "Double Strike", "Perform two quick attacks in succession", 100)
        trainer.add_training_service("defensive_stance", "Defensive Stance", "Reduce incoming damage for a short time", 150)
        
        # Village
        import random
        for i in range(5):
            villager = self.game.npc_manager.create_npc(
                f"villager_{i}",
                f"Villager {i+1}",
                NPCType.VILLAGER,
                Vec3(random.randint(-20, 20), random.randint(-20, 20), 0),
                "models/villager"
            )
            villager.add_dialogue(DialogueType.GREETING, "Hello there!")
            villager.add_lore_dialogue("They say the ancient shrine to the south grants powers to those who make offerings.")
            villager.add_lore_dialogue("The fog at night... it's not natural. Something evil lurks within it.")
    
    def _create_quests(self):
        """Create quests in the world"""
        print("Creating quests...")
        
        # Main quest
        main_quest = self.game.quest_manager.create_quest(
            "main_catacombs",
            "The Ancient Catacombs",
            QuestType.MAIN,
            "Explore the ancient catacombs and defeat the evil that lurks within.",
            level_requirement=3
        )
        
        # Add objectives
        objective1 = QuestObjective(
            "explore_catacombs",
            "Explore the Ancient Catacombs",
            ObjectiveType.DISCOVER,
            "main_dungeon",
            1
        )
        main_quest.add_objective(objective1)
        
        objective2 = QuestObjective(
            "defeat_skeletons",
            "Defeat 10 Skeleton Guards",
            ObjectiveType.KILL,
            "skeleton_guard",
            10
        )
        main_quest.add_objective(objective2)
        
        objective3 = QuestObjective(
            "defeat_boss",
            "Defeat the Catacombs Guardian",
            ObjectiveType.KILL,
            "catacombs_guardian",
            1
        )
        main_quest.add_objective(objective3)
        
        # Add rewards
        main_quest.add_reward("experience", 500)
        main_quest.add_reward("gold", 200)
        main_quest.add_reward("item", ("rare_weapon", 1))
        
        # Associate with NPC
        main_quest.giver_npc_id = "elder_maya"
        main_quest.turn_in_npc_id = "elder_maya"
        main_quest.make_available()
        
        # Add city building quest
        city_quest = self.game.quest_manager.create_quest(
            "city_farms",
            "Expanding the City",
            QuestType.SIDE,
            "Build farms to increase the city's food production.",
            level_requirement=2
        )
        
        # Add objectives
        farm_objective = QuestObjective(
            "build_farms",
            "Build 2 Farms",
            ObjectiveType.CRAFT,  # Using CRAFT as a proxy for building
            "farm",
            2
        )
        city_quest.add_objective(farm_objective)
        
        # Add rewards
        city_quest.add_reward("experience", 300)
        city_quest.add_reward("gold", 150)
        city_quest.add_reward("item", ("building_plans", 1))
        
        # Associate with NPC
        city_quest.giver_npc_id = "planner_theo"
        city_quest.turn_in_npc_id = "planner_theo"
        city_quest.make_available()
        
        # Side quest
        side_quest = self.game.quest_manager.create_quest(
            "trader_supplies",
            "Trader's Supplies",
            QuestType.SIDE,
            "Collect resources for Trader Finn.",
            level_requirement=1
        )
        
        # Add objectives
        objective1 = QuestObjective(
            "collect_wood",
            "Collect 15 Wood",
            ObjectiveType.COLLECT,
            "wood",
            15
        )
        side_quest.add_objective(objective1)
        
        objective2 = QuestObjective(
            "collect_herb",
            "Collect 5 Medicinal Herbs",
            ObjectiveType.COLLECT,
            "herb",
            5
        )
        side_quest.add_objective(objective2)
        
        # Add rewards
        side_quest.add_reward("experience", 150)
        side_quest.add_reward("gold", 50)
        side_quest.add_reward("item", ("health_potion", 3))
        
        # Associate with NPC
        side_quest.giver_npc_id = "trader_finn"
        side_quest.turn_in_npc_id = "trader_finn"
        side_quest.make_available()
    
    def _configure_boss_patterns(self):
        """Configure boss attack patterns"""
        print("Configuring boss patterns...")
        
        # We'll add patterns to existing bosses if they exist
        if hasattr(self.game, 'entity_manager') and hasattr(self.game.entity_manager, 'bosses'):
            for boss_id, boss in self.game.entity_manager.bosses.items():
                if not hasattr(boss, 'pattern_system'):
                    # Create pattern system for this boss
                    boss.pattern_system = BossPatternSystem(boss)
                    
                    # Configure patterns based on boss type
                    self._configure_boss_specific_patterns(boss)
    
    def _configure_boss_specific_patterns(self, boss):
        """Configure patterns for a specific boss"""
        # Import necessary pattern components
        from game.boss_patterns import (
            PatternSequence, AttackPattern, ProjectileBurstPattern,
            ChargePattern, GroundSlamPattern, PatternDifficulty,
            create_pattern
        )
        
        # Check boss type and configure accordingly
        if hasattr(boss, 'boss_type'):
            if boss.boss_type == "forest_guardian":
                self._configure_forest_guardian_patterns(boss)
            elif boss.boss_type == "ancient_construct":
                self._configure_ancient_construct_patterns(boss)
            elif boss.boss_type == "void_amalgamation":
                self._configure_void_amalgamation_patterns(boss)
            elif boss.boss_type == "dragon":
                self._configure_dragon_patterns(boss)
            else:
                # Generic boss patterns
                self._configure_generic_boss_patterns(boss)
    
    def _configure_forest_guardian_patterns(self, boss):
        """Configure patterns for the Forest Guardian boss"""
        # Import necessary pattern components
        from game.boss_patterns import (
            PatternSequence, PatternDifficulty,
            create_pattern
        )
        
        # Phase 1 patterns (75-100% health)
        phase1 = PatternSequence(BossPhase.PHASE_1, 1.0)
        
        # Add patterns
        pattern1 = create_pattern(
            PatternType.PROJECTILE_BURST,
            "thorn_burst",
            "Thorn Burst",
            PatternDifficulty.MEDIUM
        )
        # Customize pattern
        if hasattr(pattern1, 'projectile_count'):
            pattern1.projectile_count = 8
            pattern1.projectile_type = "thorn"
            pattern1.damage = 15
            pattern1.cooldown = 5.0
        
        pattern2 = create_pattern(
            PatternType.GROUND_SLAM,
            "root_eruption",
            "Root Eruption",
            PatternDifficulty.MEDIUM
        )
        # Customize pattern
        if hasattr(pattern2, 'slam_radius'):
            pattern2.slam_radius = 5.0
            pattern2.damage = 25
            pattern2.cooldown = 8.0
        
        # Add patterns to sequence
        phase1.add_pattern(pattern1, 2.0)  # Higher weight = more frequent
        phase1.add_pattern(pattern2, 1.0)
        
        # Add sequence to boss
        boss.pattern_system.add_sequence(BossPhase.PHASE_1, phase1)
        
        # Phase 2 patterns (50-75% health)
        phase2 = PatternSequence(BossPhase.PHASE_2, 1.2)  # 20% harder
        
        # Add patterns
        pattern3 = create_pattern(
            PatternType.PROJECTILE_BURST,
            "thorn_storm",
            "Thorn Storm",
            PatternDifficulty.HARD
        )
        # Customize pattern
        if hasattr(pattern3, 'projectile_count'):
            pattern3.projectile_count = 12
            pattern3.projectile_type = "poison_thorn"
            pattern3.damage = 20
            pattern3.cooldown = 6.0
            pattern3.waves = 2
        
        pattern4 = create_pattern(
            PatternType.CHARGE,
            "vine_charge",
            "Vine Charge",
            PatternDifficulty.MEDIUM
        )
        # Customize pattern
        if hasattr(pattern4, 'charge_speed'):
            pattern4.charge_speed = 12.0
            pattern4.damage = 30
            pattern4.cooldown = 10.0
        
        # Add patterns to sequence
        phase2.add_pattern(pattern3, 1.5)
        phase2.add_pattern(pattern4, 1.0)
        phase2.add_pattern(pattern1, 0.5)  # Less frequent now
        
        # Add sequence to boss
        boss.pattern_system.add_sequence(BossPhase.PHASE_2, phase2)
        
        # Phase 3 patterns (25-50% health)
        phase3 = PatternSequence(BossPhase.PHASE_3, 1.5)  # 50% harder
        
        # This would continue with more complex patterns...
        # For brevity, we'll stop here
    
    def _configure_ancient_construct_patterns(self, boss):
        """Configure patterns for the Ancient Construct boss"""
        # Similar to the forest guardian configuration, but with different patterns
        # This is just a stub - in a full implementation, this would be filled out
        pass
    
    def _configure_void_amalgamation_patterns(self, boss):
        """Configure patterns for the Void Amalgamation boss"""
        # Similar to the forest guardian configuration, but with different patterns
        # This is just a stub - in a full implementation, this would be filled out  
        pass
    
    def _configure_dragon_patterns(self, boss):
        """Configure patterns for the Dragon boss"""
        # Similar to the forest guardian configuration, but with different patterns
        # This is just a stub - in a full implementation, this would be filled out
        pass
    
    def _configure_generic_boss_patterns(self, boss):
        """Configure generic patterns for any boss type"""
        # Import necessary pattern components
        from game.boss_patterns import (
            PatternSequence, PatternDifficulty,
            create_pattern
        )
        
        # Phase 1 patterns (75-100% health)
        phase1 = PatternSequence(BossPhase.PHASE_1, 1.0)
        
        # Add basic patterns that any boss could use
        pattern1 = create_pattern(
            PatternType.PROJECTILE_BURST,
            "generic_burst",
            "Energy Burst",
            PatternDifficulty.MEDIUM
        )
        
        pattern2 = create_pattern(
            PatternType.CHARGE,
            "generic_charge",
            "Charging Attack",
            PatternDifficulty.MEDIUM
        )
        
        # Add patterns to sequence
        phase1.add_pattern(pattern1, 1.0)
        phase1.add_pattern(pattern2, 1.0)
        
        # Add sequence to boss
        boss.pattern_system.add_sequence(BossPhase.PHASE_1, phase1)
        
        # Add a simple phase 2 as well
        phase2 = PatternSequence(BossPhase.PHASE_2, 1.2)
        phase2.add_pattern(pattern1, 1.5)  # More frequent projectiles
        phase2.add_pattern(pattern2, 0.8)  # Less frequent charges
        
        # Add ground slam for phase 2
        pattern3 = create_pattern(
            PatternType.GROUND_SLAM,
            "generic_slam",
            "Ground Slam",
            PatternDifficulty.HARD
        )
        phase2.add_pattern(pattern3, 1.0)
        
        # Add sequence to boss
        boss.pattern_system.add_sequence(BossPhase.PHASE_2, phase2)
    
    def update(self, dt):
        """
        Update all world systems
        
        Args:
            dt: Time delta
        """
        # Update POI manager
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'position'):
            self.game.poi_manager.update(self.game.player.position)
        
        # Update NPC manager
        if hasattr(self.game, 'player') and hasattr(self.game.player, 'position'):
            self.game.npc_manager.update(dt, self.game.player.position)
        
        # Update quest manager
        self.game.quest_manager.update(dt)
        
        # Update challenge system
        self.game.challenge_system.update(dt)
        
        # Update city manager
        if hasattr(self.game, 'city_manager'):
            self.game.city_manager.update(dt)

def integrate_world_systems(game):
    """
    Integrate all world systems into the game
    
    Args:
        game: The game instance
        
    Returns:
        WorldIntegration: The world integration instance
    """
    integration = WorldIntegration(game)
    
    # Set up the world
    integration.setup_world()
    
    # Add update task to game loop
    def update_world_systems(task):
        integration.update(task.time - task.last)
        return task.cont
    
    game.taskMgr.add(update_world_systems, "update_world_systems")
    
    return integration 