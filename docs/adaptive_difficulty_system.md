# Adaptive Difficulty System Documentation

## Overview

The Adaptive Difficulty System in Nightfall Defenders dynamically adjusts the game's difficulty based on player performance. It aims to provide a balanced challenge for players of all skill levels, making the game more engaging and less frustrating.

## Core Components

The implementation consists of three main components:

1. **AdaptiveDifficultySystem** (`src/game/adaptive_difficulty.py`): Core system that adjusts difficulty parameters based on player performance.
2. **PerformanceTracker** (`src/game/performance_tracker.py`): Collects and analyzes player performance metrics.
3. **DifficultySettings** (`src/game/difficulty_settings.py`): Provides UI for players to customize difficulty settings.

## Difficulty Parameters

The system adjusts the following parameters:

| Parameter | Description | Range |
|-----------|-------------|-------|
| Enemy Health | Multiplier for enemy health | 0.6x - 1.5x |
| Enemy Damage | Multiplier for damage dealt by enemies | 0.6x - 1.5x |
| Enemy Spawn Rate | Multiplier for enemy spawn frequency | 0.7x - 1.4x |
| Enemy Aggression | Multiplier for enemy aggression level | 0.7x - 1.4x |
| Resource Drops | Multiplier for resource drop rates | 0.7x - 1.4x |
| Fog Speed | Multiplier for night fog movement speed | 0.7x - 1.5x |
| Fog Density | Multiplier for night fog density | 0.7x - 1.5x |
| Boss Difficulty | Multiplier for overall boss difficulty | 0.7x - 1.5x |

## Difficulty Presets

The system offers four difficulty presets:

1. **Easy**: Lower enemy health/damage, more resources, slower fog
2. **Normal**: Balanced settings (all multipliers at 1.0)
3. **Hard**: Higher enemy health/damage, fewer resources, faster fog
4. **Custom**: Player-defined settings

## Performance Evaluation

The system evaluates player performance based on several factors:

- **Combat Performance**: Damage dealt vs. taken, kill/death ratio
- **Resource Efficiency**: Rate of resource collection
- **City Defense**: Damage taken by city, sections lost
- **Boss Performance**: Success rate against bosses, time to defeat
- **Survival Rate**: Nights survived, health at end of night

Performance is rated on a scale from -1.0 (struggling) to 1.0 (excelling).

## Adjustment Mechanism

1. The system periodically evaluates player performance metrics
2. Based on the performance rating, difficulty parameters are adjusted:
   - High performance → Increased difficulty
   - Low performance → Decreased difficulty
3. Adjustments are gradual to avoid sudden difficulty spikes
4. Anti-frustration features provide relief after multiple deaths

## Anti-Frustration Features

The system includes anti-frustration measures to prevent player discouragement:

- After consecutive deaths, difficulty is temporarily reduced
- Close calls (near-death experiences) are monitored
- Pattern of repeated failure at specific challenges triggers adjustments

## Integration with Game Systems

The adaptive difficulty system integrates with:

- **Enemy System**: Adjusting health, damage, and behavior
- **Resource System**: Modifying drop rates
- **Environmental Systems**: Changing fog behavior and density
- **Boss Encounters**: Scaling overall difficulty

## Usage for Developers

### Initialization

The system is automatically initialized in the main game:

```python
# In NightfallDefenders.__init__
self.adaptive_difficulty_system = AdaptiveDifficultySystem(self)
self.performance_tracker = PerformanceTracker(self)
self.difficulty_settings = DifficultySettings(self)
```

### Recording Events

To have the system respond to game events, record them using:

```python
# Combat events
game.adaptive_difficulty_system.record_combat_event('damage_dealt', amount)
game.adaptive_difficulty_system.record_combat_event('damage_taken', amount)
game.adaptive_difficulty_system.record_combat_event('enemy_killed')
game.adaptive_difficulty_system.record_combat_event('player_death')

# Resource events
game.adaptive_difficulty_system.record_resource_event('collected', resource_type, amount)
game.adaptive_difficulty_system.record_resource_event('spent', resource_type, amount)

# City events
game.adaptive_difficulty_system.record_city_event('attack')
game.adaptive_difficulty_system.record_city_event('damage', amount)
game.adaptive_difficulty_system.record_city_event('section_lost')

# Boss events
game.adaptive_difficulty_system.record_boss_event('encounter')
game.adaptive_difficulty_system.record_boss_event('defeat', time_to_kill)

# Night survival
game.adaptive_difficulty_system.record_night_survived(health_percentage)
```

### Getting Difficulty Factors

To apply difficulty adjustments to game elements:

```python
# Get all difficulty factors
factors = game.adaptive_difficulty_system.get_current_difficulty_factors()

# Apply to game elements
enemy_health = base_health * factors['enemy_health']
enemy_damage = base_damage * factors['enemy_damage']
spawn_timer = base_timer / factors['enemy_spawn_rate']
resource_amount = base_amount * factors['resource_drop']
```

### Setting Difficulty

To programmatically change difficulty:

```python
# Set to a preset
from game.adaptive_difficulty import DifficultyPreset
game.adaptive_difficulty_system.set_difficulty_preset(DifficultyPreset.NORMAL)

# Set custom difficulty
custom_settings = {
    'enemy_health': 1.2,
    'enemy_damage': 1.1,
    'resource_drop': 0.9,
    # other parameters...
}
game.adaptive_difficulty_system.set_custom_difficulty(custom_settings)
```

## Player Controls

Players can adjust difficulty through the settings menu by pressing the 'O' key. The settings UI allows them to:

- Select a difficulty preset
- Customize individual difficulty parameters
- Save settings for the current game session

## Debugging

For debugging and testing the adaptive difficulty system:

1. Run the dedicated test: `run_adaptive_difficulty_test.bat`
2. Enable debug mode in-game: `game.adaptive_difficulty_system.enable_debug_mode(True)`
3. View difficulty stats: `stats = game.adaptive_difficulty_system.get_difficulty_stats()`

## Considerations for Game Balance

When designing content:

1. Base values should be balanced for Normal difficulty (multiplier = 1.0)
2. Test gameplay at both Easy and Hard presets
3. Consider how difficulty scaling affects different player types (offensive, defensive, etc.)
4. Ensure resource economy works across difficulty settings

## Future Enhancements

Planned improvements:

1. Per-player-profile difficulty tracking
2. More advanced behavior adjustments for enemies
3. Difficulty scaling based on party size for multiplayer
4. More granular control over specific game aspects 

## Adaptive Difficulty System Implementation

The adaptive difficulty system dynamically adjusts game difficulty based on player performance to provide an optimal challenge level for all players.

### Key Components

1. **AdaptiveDifficultySystem**
   - Core system that monitors player performance and adjusts difficulty parameters
   - Maintains difficulty factors for various game systems
   - Provides interfaces for game systems to query current difficulty

2. **PerformanceTracker**
   - Collects and analyzes player metrics
   - Records combat events, resource gathering, city defense, boss encounters, etc.
   - Calculates performance scores in different game aspects

3. **DifficultySettings UI**
   - Allows players to customize difficulty preferences
   - Provides presets (Easy, Normal, Hard, Custom)
   - Accessible in-game by pressing 'O'

### Difficulty Parameters

The system adjusts the following parameters:

- **Combat parameters**
  - Enemy health (`enemy_health`)
  - Enemy damage (`enemy_damage`) 
  - Enemy spawn rate (`enemy_spawn_rate`)
  - Enemy aggression (`enemy_aggression`)

- **Resource parameters**
  - Resource drop rates (`resource_drop`)
  - Resource node regeneration time (inversely proportional to `resource_drop`)

- **Night Fog parameters**
  - Fog speed (`fog_speed`)
  - Fog density (`fog_density`)

- **Boss parameters**
  - Boss health (affected by both `enemy_health` and `boss_difficulty`)
  - Boss damage (affected by both `enemy_damage` and `boss_difficulty`)
  - Ability cooldowns (affected by `boss_difficulty`)

### Player Performance Metrics

The system evaluates player performance based on:

1. **Combat Efficiency**
   - Damage dealt vs. taken ratio
   - Kill/death ratio
   - Time to kill enemies
   - Accuracy

2. **Resource Gathering**
   - Resource collection rate
   - Resource type diversity
   - Resource utilization

3. **City Defense**
   - Building preservation
   - Defense success rate
   - Damage resilience

4. **Boss Performance**
   - Victory rate
   - Time to defeat bosses

5. **Survival**
   - Night cycles survived
   - Death avoidance
   - Damage avoidance

### Integration Points

The adaptive difficulty system integrates with:

1. **Enemy System**
   - `Enemy.apply_difficulty_adjustment()` adjusts enemy stats based on difficulty
   - Records combat events through `performance_tracker`

2. **Boss System**
   - `Boss.apply_difficulty_adjustment()` adjusts boss stats with boss-specific scaling
   - Boss abilities and phase transitions are affected by difficulty
   - Boss performance is tracked and influences difficulty

3. **Resource System**
   - `ResourceNode` adjusts harvest amounts and regeneration times
   - Resources become more/less plentiful based on player gathering performance

4. **Night Fog System**
   - Fog speed, density, and damage are adjusted
   - Enemy spawn rates within fog are affected

5. **Entity Manager**
   - Enemy spawn rates and type probabilities are adjusted
   - Higher difficulty increases special enemy type chances

### Using the System

#### For Players
- Run the game with adaptive difficulty using `run_game_with_adaptive_difficulty.bat`
- Press 'O' in-game to open difficulty settings
- Choose a preset or customize individual parameters

#### For Developers
- Create game objects with `apply_difficulty_adjustment()` methods
- Call these methods after object creation and when difficulty changes
- Record relevant events through `performance_tracker`
- Query current difficulty using `adaptive_difficulty_system.get_current_difficulty_factors()`

### Anti-Frustration Features

The system includes several features to prevent player frustration:

1. **Performance-Based Adjustments**
   - Difficulty decreases if player is struggling consistently
   - Difficulty increases gradually for skilled players

2. **Fast Response to Struggle**
   - More responsive to player deaths than successes
   - Quicker adjustment when player is overwhelmed

3. **Boss-Specific Adjustments**
   - Boss difficulty decreases after player death to a boss
   - Adjusts based on boss defeat time 

4. **Resource Relief**
   - Increases resource drops when player is struggling
   - Helps players recover after setbacks

### Testing

Test the adaptive difficulty system using:
- `run_adaptive_difficulty_test.bat` - Tests boss integration, resource scaling, and fog adjustments
- The test simulates different player skill levels and verifies appropriate adjustments 