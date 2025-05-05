# src/engine/systems/system_integrator.py
from typing import Optional
from ..city.city_manager import CityManager
from ..world.world_manager import WorldManager
from ..combat.combat_system import CombatSystem
from ..audio.sound_manager import SoundManager
from .tutorial_system import TutorialSystem
from .achievement_system import AchievementSystem
from .random_events import RandomEventSystem
from .progression_system import ProgressionSystem
from .cloud_save_system import CloudSaveSystem
from .event_rewards import EventRewardSystem

class SystemIntegrator:
    def __init__(self, config: dict):
        # Core systems
        self.city_manager = CityManager()
        self.world_manager = WorldManager()
        self.combat_system = CombatSystem()
        self.sound_manager = SoundManager()
        
        # Additional systems
        self.tutorial_system = TutorialSystem(
            self.world_manager.ui_manager,
            self.sound_manager
        )
        
        self.achievement_system = AchievementSystem(
            self.sound_manager
        )
        
        self.random_events = RandomEventSystem(
            self.city_manager,
            self.world_manager,
            self.world_manager.weather_system
        )
        
        self.progression_system = ProgressionSystem()
        
        self.cloud_save = CloudSaveSystem(
            config["cloud_api_endpoint"],
            config["cloud_api_key"]
        )
        
        self.event_rewards = EventRewardSystem(
            self.progression_system
        )
        
        self._setup_integrations()
        
    def _setup_integrations(self):
        # Connect achievement triggers
        self.combat_system.on_combat_victory.connect(
            self._handle_combat_victory
        )
        
        self.city_manager.on_building_complete.connect(
            self._handle_building_complete
        )
        
        self.world_manager.on_location_discovered.connect(
            self._handle_location_discovered
        )
        
        # Connect tutorial triggers
        self.city_manager.on_first_build.connect(
            lambda: self.tutorial_system.complete_step("city_basics")
        )
        
        self.combat_system.on_training_complete.connect(
            lambda: self.tutorial_system.complete_step("combat_basics")
        )
        
        # Connect reward distribution
        self.random_events.on_event_complete.connect(
            self._handle_event_completion
        )
        
    def update(self, dt: float):
        # Update core systems
        self.city_manager.update(dt)
        self.world_manager.update(dt)
        self.combat_system.update(dt)
        self.sound_manager.update(dt)
        
        # Update additional systems
        self.tutorial_system.update(dt)
        self.random_events.update(dt)
        
        # Check for auto-save
        if self.cloud_save.check_auto_save():
            self.save_game("auto_save")
            
    async def save_game(self, save_name: str):
        game_state = {
            "city": self.city_manager.save_state(),
            "world": self.world_manager.save_state(),
            "combat": self.combat_system.save_state(),
            "tutorial": self.tutorial_system.save_state(),
            "achievements": self.achievement_system.save_state(),
            "progression": self.progression_system.save_state(),
            "events": self.random_events.save_state()
        }
        
        await self.cloud_save.save_game(save_name, game_state)
        
    async def load_game(self, save_name: str):
        game_state = await self.cloud_save.load_game(save_name)
        if not game_state:
            return False
            
        self.city_manager.load_state(game_state["city"])
        self.world_manager.load_state(game_state["world"])
        self.combat_system.load_state(game_state["combat"])
        self.tutorial_system.load_state(game_state["tutorial"])
        self.achievement_system.load_state(game_state["achievements"])
        self.progression_system.load_state(game_state["progression"])
        self.random_events.load_state(game_state["events"])
        
        return True
        
    def _handle_combat_victory(self, enemy_level: int, is_boss: bool):
        if is_boss:
            self.achievement_system.update_progress("defeat_boss", 1)
            rewards = self.event_rewards.generate_rewards(
                "boss_defeat",
                bonus_multiplier=1.5 if enemy_level > 20 else 1.0
            )
            self.event_rewards.apply_rewards(
                rewards,
                self.combat_system.player_inventory,
                self.city_manager
            )
            
    def _handle_building_complete(self, building_type: str, level: int):
        if level == 1:
            self.achievement_system.update_progress(f"build_{building_type}", 1)
        if level == 5:
            self.achievement_system.update_progress("master_builder", 1)
            
    def _handle_location_discovered(self, location_type: str):
        self.achievement_system.update_progress("explorer", 1)
        if location_type == "legendary":
            self.achievement_system.update_progress("legendary_explorer", 1)
            
    def _handle_event_completion(self, event_id: str, success: bool):
        if success:
            self.achievement_system.update_progress("event_master", 1)
            rewards = self.event_rewards.generate_rewards(
                event_id,
                bonus_multiplier=1.2,
                luck_modifier=self.progression_system.get_total_bonus(
                    ParagonStat.LUCK
                )
            )
            self.event_rewards.apply_rewards(
                rewards,
                self.combat_system.player_inventory,
                self.city_manager
            )