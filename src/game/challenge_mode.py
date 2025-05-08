#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Challenge Mode System for Nightfall Defenders
Implements special challenge modes with rule modifiers and rewards
"""

from enum import Enum
import random
import time
import math

class ChallengeType(Enum):
    """Types of challenges"""
    TIME_TRIAL = "time_trial"
    SURVIVAL = "survival"
    BOSS_RUSH = "boss_rush"
    HARDCORE = "hardcore"
    SPECIAL_RULES = "special_rules"

class ChallengeStatus(Enum):
    """Challenge status states"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class ChallengeModifier:
    """A modifier that changes challenge rules"""
    
    def __init__(self, modifier_id, name, description):
        """
        Initialize a challenge modifier
        
        Args:
            modifier_id (str): Unique identifier
            name (str): Display name
            description (str): Description of the effect
        """
        self.modifier_id = modifier_id
        self.name = name
        self.description = description
        
        # Effect factors (applied to game systems)
        self.player_damage_factor = 1.0
        self.player_speed_factor = 1.0
        self.player_health_factor = 1.0
        self.enemy_damage_factor = 1.0
        self.enemy_health_factor = 1.0
        self.enemy_speed_factor = 1.0
        self.enemy_count_factor = 1.0
        self.resource_drop_factor = 1.0
        self.time_limit_factor = 1.0
        
        # Special rule flags
        self.permadeath = False
        self.reduced_visibility = False
        self.no_healing = False
        self.abilities_disabled = []
        self.enemy_types_only = []
        
    def apply_to_game(self, game):
        """
        Apply this modifier to the game
        
        Args:
            game: The game instance
        """
        # Apply player modifiers
        if hasattr(game, 'player'):
            # Damage
            if hasattr(game.player, 'damage_multiplier'):
                game.player.damage_multiplier *= self.player_damage_factor
            
            # Speed
            if hasattr(game.player, 'speed'):
                game.player.speed *= self.player_speed_factor
            
            # Health
            if hasattr(game.player, 'max_health') and hasattr(game.player, 'health'):
                old_max = game.player.max_health
                game.player.max_health = int(game.player.max_health * self.player_health_factor)
                # Adjust current health proportionally
                health_ratio = game.player.health / old_max
                game.player.health = int(game.player.max_health * health_ratio)
                
        # Apply enemy modifiers through the adaptive difficulty system
        if hasattr(game, 'adaptive_difficulty'):
            difficulty_factors = game.adaptive_difficulty.get_current_difficulty_factors()
            
            # Apply modifiers
            difficulty_factors['enemy_damage'] *= self.enemy_damage_factor
            difficulty_factors['enemy_health'] *= self.enemy_health_factor
            difficulty_factors['enemy_speed'] *= self.enemy_speed_factor
            difficulty_factors['enemy_spawn_rate'] *= self.enemy_count_factor
            difficulty_factors['resource_drop'] *= self.resource_drop_factor
            
            # Update difficulty factors
            game.adaptive_difficulty.set_difficulty_factors(difficulty_factors)
        
        # Apply special rules
        game.challenge_mode.special_rules = {
            'permadeath': self.permadeath,
            'reduced_visibility': self.reduced_visibility,
            'no_healing': self.no_healing,
            'abilities_disabled': self.abilities_disabled.copy(),
            'enemy_types_only': self.enemy_types_only.copy()
        }
    
    def remove_from_game(self, game):
        """
        Remove this modifier from the game
        
        Args:
            game: The game instance
        """
        # In a proper implementation, we would restore original values
        # Here we'll just reset challenge mode rules
        game.challenge_mode.special_rules = {}
        
        # Reset the adaptive difficulty to default
        if hasattr(game, 'adaptive_difficulty'):
            game.adaptive_difficulty.reset_to_defaults()
            
        # Since we can't easily reset player stats without knowing original values,
        # we'd typically have stored those values when applying the modifier

class Challenge:
    """A single challenge with objectives and rewards"""
    
    def __init__(self, challenge_id, name, challenge_type, description, difficulty=1):
        """
        Initialize a challenge
        
        Args:
            challenge_id (str): Unique identifier
            name (str): Display name
            challenge_type (ChallengeType): Type of challenge
            description (str): Description of the challenge
            difficulty (int): Difficulty level (1-10)
        """
        self.challenge_id = challenge_id
        self.name = name
        self.challenge_type = challenge_type
        self.description = description
        self.difficulty = difficulty
        
        # Challenge parameters
        self.time_limit = 600  # 10 minutes default
        self.target_score = 1000
        self.wave_count = 10
        self.boss_count = 1
        
        # Modifiers
        self.modifiers = []
        
        # Rewards
        self.rewards = {
            "experience": 0,
            "gold": 0,
            "items": {},
            "special_rewards": {}
        }
        
        # Status tracking
        self.status = ChallengeStatus.NOT_STARTED
        self.start_time = None
        self.end_time = None
        self.score = 0
        self.best_score = 0
        self.completion_count = 0
    
    def add_modifier(self, modifier):
        """
        Add a modifier to this challenge
        
        Args:
            modifier (ChallengeModifier): The modifier to add
        """
        self.modifiers.append(modifier)
    
    def add_reward(self, reward_type, value):
        """
        Add a reward for completing the challenge
        
        Args:
            reward_type (str): Type of reward
            value: Value of the reward
        """
        if reward_type == "item":
            if isinstance(value, tuple) and len(value) == 2:
                item_id, amount = value
                if item_id in self.rewards["items"]:
                    self.rewards["items"][item_id] += amount
                else:
                    self.rewards["items"][item_id] = amount
        elif reward_type == "special":
            if isinstance(value, tuple) and len(value) == 2:
                reward_id, reward_data = value
                self.rewards["special_rewards"][reward_id] = reward_data
        else:
            if reward_type in self.rewards:
                self.rewards[reward_type] += value
    
    def start(self, game):
        """
        Start the challenge
        
        Args:
            game: The game instance
            
        Returns:
            bool: True if challenge was started
        """
        if self.status != ChallengeStatus.NOT_STARTED and self.status != ChallengeStatus.FAILED:
            return False
            
        self.status = ChallengeStatus.IN_PROGRESS
        self.start_time = time.time()
        self.end_time = None
        self.score = 0
        
        # Apply modifiers
        for modifier in self.modifiers:
            modifier.apply_to_game(game)
            
        # Apply challenge-specific setup
        if self.challenge_type == ChallengeType.TIME_TRIAL:
            self._setup_time_trial(game)
        elif self.challenge_type == ChallengeType.SURVIVAL:
            self._setup_survival(game)
        elif self.challenge_type == ChallengeType.BOSS_RUSH:
            self._setup_boss_rush(game)
        elif self.challenge_type == ChallengeType.HARDCORE:
            self._setup_hardcore(game)
        elif self.challenge_type == ChallengeType.SPECIAL_RULES:
            self._setup_special_rules(game)
            
        return True
    
    def complete(self, game):
        """
        Complete the challenge
        
        Args:
            game: The game instance
            
        Returns:
            bool: True if challenge was completed
        """
        if self.status != ChallengeStatus.IN_PROGRESS:
            return False
            
        self.status = ChallengeStatus.COMPLETED
        self.end_time = time.time()
        self.completion_count += 1
        
        # Update best score
        if self.score > self.best_score:
            self.best_score = self.score
            
        # Give rewards
        self._give_rewards(game)
        
        # Remove modifiers
        for modifier in self.modifiers:
            modifier.remove_from_game(game)
            
        return True
    
    def fail(self, game):
        """
        Fail the challenge
        
        Args:
            game: The game instance
            
        Returns:
            bool: True if challenge was failed
        """
        if self.status != ChallengeStatus.IN_PROGRESS:
            return False
            
        self.status = ChallengeStatus.FAILED
        self.end_time = time.time()
        
        # Remove modifiers
        for modifier in self.modifiers:
            modifier.remove_from_game(game)
            
        return True
    
    def update(self, dt, game):
        """
        Update the challenge state
        
        Args:
            dt: Time delta
            game: The game instance
            
        Returns:
            bool: True if challenge state changed
        """
        if self.status != ChallengeStatus.IN_PROGRESS:
            return False
            
        # Check time limit for time-based challenges
        if self.challenge_type == ChallengeType.TIME_TRIAL:
            elapsed_time = time.time() - self.start_time
            if elapsed_time >= self.time_limit:
                # Check if score meets target
                if self.score >= self.target_score:
                    self.complete(game)
                    return True
                else:
                    self.fail(game)
                    return True
                    
        # Update based on challenge type
        if self.challenge_type == ChallengeType.TIME_TRIAL:
            return self._update_time_trial(dt, game)
        elif self.challenge_type == ChallengeType.SURVIVAL:
            return self._update_survival(dt, game)
        elif self.challenge_type == ChallengeType.BOSS_RUSH:
            return self._update_boss_rush(dt, game)
        elif self.challenge_type == ChallengeType.HARDCORE:
            return self._update_hardcore(dt, game)
        elif self.challenge_type == ChallengeType.SPECIAL_RULES:
            return self._update_special_rules(dt, game)
            
        return False
    
    def _give_rewards(self, game):
        """Give rewards for completing the challenge"""
        # Experience
        if self.rewards["experience"] > 0:
            game.player.add_experience(self.rewards["experience"])
            
        # Gold
        if self.rewards["gold"] > 0:
            if hasattr(game.player, 'gold'):
                game.player.gold += self.rewards["gold"]
                
        # Items
        for item_id, amount in self.rewards["items"].items():
            if hasattr(game.player, 'inventory'):
                if item_id in game.player.inventory:
                    game.player.inventory[item_id] += amount
                else:
                    game.player.inventory[item_id] = amount
                    
        # Special rewards
        for reward_id, reward_data in self.rewards["special_rewards"].items():
            # Handle special rewards like cosmetics, titles, etc.
            pass
    
    def add_score(self, amount):
        """
        Add to the challenge score
        
        Args:
            amount: Amount to add
        """
        self.score += amount
    
    def get_time_remaining(self):
        """
        Get the time remaining for time-limited challenges
        
        Returns:
            float: Time remaining in seconds
        """
        if self.status != ChallengeStatus.IN_PROGRESS:
            return 0.0
            
        elapsed_time = time.time() - self.start_time
        remaining_time = max(0.0, self.time_limit - elapsed_time)
        return remaining_time
    
    def get_completion_time(self):
        """
        Get the time taken to complete the challenge
        
        Returns:
            float: Completion time in seconds
        """
        if self.status != ChallengeStatus.COMPLETED:
            return 0.0
            
        return self.end_time - self.start_time
    
    # Challenge type-specific setup and update methods
    def _setup_time_trial(self, game):
        """Setup for time trial challenge"""
        pass
    
    def _update_time_trial(self, dt, game):
        """Update for time trial challenge"""
        return False
    
    def _setup_survival(self, game):
        """Setup for survival challenge"""
        pass
    
    def _update_survival(self, dt, game):
        """Update for survival challenge"""
        return False
    
    def _setup_boss_rush(self, game):
        """Setup for boss rush challenge"""
        pass
    
    def _update_boss_rush(self, dt, game):
        """Update for boss rush challenge"""
        return False
    
    def _setup_hardcore(self, game):
        """Setup for hardcore challenge"""
        pass
    
    def _update_hardcore(self, dt, game):
        """Update for hardcore challenge"""
        return False
    
    def _setup_special_rules(self, game):
        """Setup for special rules challenge"""
        pass
    
    def _update_special_rules(self, dt, game):
        """Update for special rules challenge"""
        return False

class ChallengeSystem:
    """Manages all challenge modes"""
    
    def __init__(self, game):
        """
        Initialize the challenge system
        
        Args:
            game: The game instance
        """
        self.game = game
        self.challenges = {}  # All challenges by ID
        self.current_challenge = None
        self.completed_challenges = set()
        
        # Special rules
        self.special_rules = {}
        
        # Challenge rewards
        self.unlocked_rewards = set()
        
        # Load challenges
        self._create_default_challenges()
    
    def _create_default_challenges(self):
        """Create default challenge set"""
        # Time Trial Challenge
        time_trial = Challenge(
            "time_trial_1",
            "Speed Runner",
            ChallengeType.TIME_TRIAL,
            "Kill 50 enemies in 5 minutes", 
            difficulty=3
        )
        time_trial.time_limit = 300  # 5 minutes
        time_trial.target_score = 50
        time_trial.add_reward("experience", 500)
        time_trial.add_reward("gold", 200)
        
        # Add a modifier
        speed_mod = ChallengeModifier(
            "speed_boost",
            "Speed Boost",
            "Increased player movement speed"
        )
        speed_mod.player_speed_factor = 1.5
        speed_mod.enemy_count_factor = 1.2
        time_trial.add_modifier(speed_mod)
        
        self.challenges[time_trial.challenge_id] = time_trial
        
        # Survival Challenge
        survival = Challenge(
            "survival_1",
            "Last Stand",
            ChallengeType.SURVIVAL,
            "Survive 10 waves of increasingly difficult enemies",
            difficulty=5
        )
        survival.wave_count = 10
        survival.add_reward("experience", 800)
        survival.add_reward("gold", 300)
        survival.add_reward("item", ("rare_relic_1", 1))
        
        # Add modifiers
        survival_mod = ChallengeModifier(
            "waves_mod",
            "Endless Waves",
            "Enemies come in continuous waves"
        )
        survival_mod.enemy_damage_factor = 1.2
        survival_mod.enemy_health_factor = 1.3
        survival_mod.resource_drop_factor = 0.8
        survival.add_modifier(survival_mod)
        
        self.challenges[survival.challenge_id] = survival
        
        # Boss Rush Challenge
        boss_rush = Challenge(
            "boss_rush_1",
            "Boss Gauntlet",
            ChallengeType.BOSS_RUSH,
            "Defeat 3 bosses in succession with limited healing",
            difficulty=8
        )
        boss_rush.boss_count = 3
        boss_rush.add_reward("experience", 1200)
        boss_rush.add_reward("gold", 500)
        boss_rush.add_reward("item", ("legendary_relic_1", 1))
        
        # Add modifiers
        boss_mod = ChallengeModifier(
            "boss_mod",
            "Boss Frenzy",
            "Bosses have enhanced abilities but reduced health"
        )
        boss_mod.enemy_damage_factor = 1.5
        boss_mod.enemy_health_factor = 0.8
        boss_mod.no_healing = True
        boss_rush.add_modifier(boss_mod)
        
        self.challenges[boss_rush.challenge_id] = boss_rush
        
        # Hardcore Challenge
        hardcore = Challenge(
            "hardcore_1",
            "Perma-Death",
            ChallengeType.HARDCORE,
            "Complete a night with permadeath - one hit and you're out",
            difficulty=10
        )
        hardcore.add_reward("experience", 2000)
        hardcore.add_reward("gold", 1000)
        hardcore.add_reward("special", ("title_1", "The Unstoppable"))
        
        # Add modifiers
        hardcore_mod = ChallengeModifier(
            "hardcore_mod",
            "One Life",
            "You die in one hit"
        )
        hardcore_mod.player_health_factor = 0.01  # Effectively one hit death
        hardcore_mod.player_damage_factor = 2.0
        hardcore_mod.permadeath = True
        hardcore.add_modifier(hardcore_mod)
        
        self.challenges[hardcore.challenge_id] = hardcore
    
    def start_challenge(self, challenge_id):
        """
        Start a challenge
        
        Args:
            challenge_id (str): ID of the challenge to start
            
        Returns:
            bool: True if challenge was started
        """
        if challenge_id not in self.challenges:
            return False
            
        # Cannot start a challenge while another is in progress
        if self.current_challenge and self.current_challenge.status == ChallengeStatus.IN_PROGRESS:
            return False
            
        challenge = self.challenges[challenge_id]
        if challenge.start(self.game):
            self.current_challenge = challenge
            
            # Notify UI
            if hasattr(self.game, 'message_system') and self.game.message_system:
                self.game.message_system.show_message(
                    f"Challenge started: {challenge.name}",
                    duration=3.0,
                    message_type="challenge_started"
                )
                
            return True
            
        return False
    
    def abandon_challenge(self):
        """
        Abandon the current challenge
        
        Returns:
            bool: True if challenge was abandoned
        """
        if not self.current_challenge or self.current_challenge.status != ChallengeStatus.IN_PROGRESS:
            return False
            
        # Fail the challenge
        self.current_challenge.fail(self.game)
        
        # Notify UI
        if hasattr(self.game, 'message_system') and self.game.message_system:
            self.game.message_system.show_message(
                f"Challenge abandoned: {self.current_challenge.name}",
                duration=3.0,
                message_type="challenge_abandoned"
            )
            
        return True
    
    def update(self, dt):
        """
        Update the challenge system
        
        Args:
            dt: Time delta
        """
        # Update current challenge
        if self.current_challenge and self.current_challenge.status == ChallengeStatus.IN_PROGRESS:
            self.current_challenge.update(dt, self.game)
            
            # If the challenge is no longer in progress, it was completed or failed
            if self.current_challenge.status == ChallengeStatus.COMPLETED:
                self.completed_challenges.add(self.current_challenge.challenge_id)
                
                # Notify UI
                if hasattr(self.game, 'message_system') and self.game.message_system:
                    self.game.message_system.show_message(
                        f"Challenge completed: {self.current_challenge.name}",
                        duration=5.0,
                        message_type="challenge_completed"
                    )
            elif self.current_challenge.status == ChallengeStatus.FAILED:
                # Notify UI
                if hasattr(self.game, 'message_system') and self.game.message_system:
                    self.game.message_system.show_message(
                        f"Challenge failed: {self.current_challenge.name}",
                        duration=5.0,
                        message_type="challenge_failed"
                    )
    
    def on_enemy_killed(self, enemy_type, score_value=1):
        """
        Register enemy kill for challenge scoring
        
        Args:
            enemy_type (str): Type of enemy killed
            score_value (int): Score value for this enemy
        """
        if self.current_challenge and self.current_challenge.status == ChallengeStatus.IN_PROGRESS:
            self.current_challenge.add_score(score_value)
    
    def on_boss_killed(self, boss_type, score_value=10):
        """
        Register boss kill for challenge scoring
        
        Args:
            boss_type (str): Type of boss killed
            score_value (int): Score value for this boss
        """
        if self.current_challenge and self.current_challenge.status == ChallengeStatus.IN_PROGRESS:
            self.current_challenge.add_score(score_value)
            
            # Check for boss rush completion
            if (self.current_challenge.challenge_type == ChallengeType.BOSS_RUSH and 
                self.current_challenge.score >= self.current_challenge.boss_count):
                self.current_challenge.complete(self.game)
    
    def on_player_died(self):
        """Handle player death"""
        if self.current_challenge and self.current_challenge.status == ChallengeStatus.IN_PROGRESS:
            # Check for permadeath rule
            if 'permadeath' in self.special_rules and self.special_rules['permadeath']:
                self.current_challenge.fail(self.game)
    
    def on_wave_completed(self, wave_number):
        """
        Register wave completion for challenge scoring
        
        Args:
            wave_number (int): Wave number completed
        """
        if self.current_challenge and self.current_challenge.status == ChallengeStatus.IN_PROGRESS:
            # Check for survival challenge completion
            if (self.current_challenge.challenge_type == ChallengeType.SURVIVAL and 
                wave_number >= self.current_challenge.wave_count):
                self.current_challenge.complete(self.game)
    
    def get_challenge_ui_data(self):
        """
        Get data for challenge UI display
        
        Returns:
            dict: Challenge UI data
        """
        ui_data = {
            "active_challenge": None,
            "time_remaining": 0,
            "score": 0,
            "target_score": 0,
            "progress": 0
        }
        
        if self.current_challenge and self.current_challenge.status == ChallengeStatus.IN_PROGRESS:
            challenge = self.current_challenge
            ui_data["active_challenge"] = {
                "id": challenge.challenge_id,
                "name": challenge.name,
                "description": challenge.description,
                "type": challenge.challenge_type.value
            }
            
            ui_data["time_remaining"] = challenge.get_time_remaining()
            ui_data["score"] = challenge.score
            ui_data["target_score"] = challenge.target_score
            
            # Calculate progress based on challenge type
            if challenge.challenge_type == ChallengeType.TIME_TRIAL:
                if challenge.target_score > 0:
                    ui_data["progress"] = min(100, (challenge.score / challenge.target_score) * 100)
            elif challenge.challenge_type == ChallengeType.SURVIVAL:
                if challenge.wave_count > 0:
                    ui_data["progress"] = min(100, (challenge.score / challenge.wave_count) * 100)
            elif challenge.challenge_type == ChallengeType.BOSS_RUSH:
                if challenge.boss_count > 0:
                    ui_data["progress"] = min(100, (challenge.score / challenge.boss_count) * 100)
            
        return ui_data
    
    def get_available_challenges(self):
        """
        Get all available challenges
        
        Returns:
            list: Available challenges
        """
        return [challenge for challenge_id, challenge in self.challenges.items() 
                if challenge.status != ChallengeStatus.IN_PROGRESS]
    
    def get_challenge_by_id(self, challenge_id):
        """
        Get a challenge by ID
        
        Args:
            challenge_id (str): Challenge ID
            
        Returns:
            Challenge or None: The challenge if found
        """
        return self.challenges.get(challenge_id)
    
    def is_challenge_active(self):
        """
        Check if a challenge is currently active
        
        Returns:
            bool: True if a challenge is active
        """
        return self.current_challenge is not None and self.current_challenge.status == ChallengeStatus.IN_PROGRESS
    
    def save_data(self):
        """
        Create a serializable data representation of challenge state
        
        Returns:
            dict: Serializable challenge data
        """
        data = {
            "completed_challenges": list(self.completed_challenges),
            "unlocked_rewards": list(self.unlocked_rewards),
            "challenge_progress": {}
        }
        
        # Save progress for each challenge
        for challenge_id, challenge in self.challenges.items():
            challenge_data = {
                "best_score": challenge.best_score,
                "completion_count": challenge.completion_count
            }
            data["challenge_progress"][challenge_id] = challenge_data
            
        return data
    
    def load_data(self, data):
        """
        Load challenge state from serialized data
        
        Args:
            data: Serialized challenge data
        """
        # Load completed challenges
        if "completed_challenges" in data:
            self.completed_challenges = set(data["completed_challenges"])
            
        # Load unlocked rewards
        if "unlocked_rewards" in data:
            self.unlocked_rewards = set(data["unlocked_rewards"])
            
        # Load challenge progress
        if "challenge_progress" in data:
            for challenge_id, challenge_data in data["challenge_progress"].items():
                if challenge_id in self.challenges:
                    challenge = self.challenges[challenge_id]
                    challenge.best_score = challenge_data.get("best_score", 0)
                    challenge.completion_count = challenge_data.get("completion_count", 0) 