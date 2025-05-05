# src/engine/quests/quest_scaling.py
from typing import List
# Supposons que Reward est défini ailleurs (par exemple dans quest_data.py ou quest_generator.py)
# from .quest_data import Reward # Ou l'importation correcte

# --- Supposition de la structure Reward ---
from dataclasses import dataclass
from typing import Any

@dataclass
class Reward:
    type: str # e.g., 'experience', 'gold', 'item'
    value: Any # Peut être un int (XP, gold) ou un str (item_id)
    amount: int = 1
# --- Fin de la supposition ---


def scale_difficulty(base_difficulty: int, player_level: int, world_state: object) -> int:
    """
    Ajuste la difficulté de base d'une quête en fonction du niveau du joueur
    et potentiellement de l'état du monde (par exemple, difficulté de la zone).

    Args:
        base_difficulty: La difficulté initiale définie dans le template.
        player_level: Le niveau actuel du joueur.
        world_state: Un objet fournissant des informations sur l'état actuel du jeu
                     (peut être simplifié ou rendu plus complexe).

    Returns:
        La difficulté ajustée.
    """
    # Exemple : Augmenter la difficulté si le joueur est dans une zone dangereuse
    zone_modifier = 1.0
    if hasattr(world_state, 'get_zone_difficulty_modifier'):
        # Supposons que cette méthode existe et retourne un multiplicateur
        try:
            zone_modifier = world_state.get_zone_difficulty_modifier()
        except Exception as e:
            print(f"Warning: Could not get zone difficulty modifier: {e}")
            zone_modifier = 1.0 # Valeur par défaut

    # Ajuster légèrement basé sur l'écart de niveau entre le joueur et la difficulté de base
    # Si le joueur est plus haut niveau, la difficulté perçue diminue (ou l'inverse)
    # Cet ajustement est conceptuel, la difficulté *intrinsèque* ne change pas forcément,
    # mais on peut l'utiliser pour scaler les objectifs/récompenses plus tard.
    # Ici, on retourne une difficulté "effective".
    level_diff_factor = 1.0 + (player_level - base_difficulty) * 0.05 # Ajustement léger
    level_diff_factor = max(0.5, min(1.5, level_diff_factor)) # Limiter l'impact

    # Calculer la difficulté finale, en s'assurant qu'elle est au moins 1
    scaled_diff = base_difficulty * zone_modifier * level_diff_factor
    final_difficulty = max(1, int(round(scaled_diff)))

    # print(f"Scaling difficulty: Base={base_difficulty}, PlayerLvl={player_level}, ZoneMod={zone_modifier:.2f}, LvlFactor={level_diff_factor:.2f} -> Final={final_difficulty}")

    return final_difficulty


def scale_rewards(base_rewards: List[Reward], quest_difficulty: int, player_level: int) -> List[Reward]:
    """
    Ajuste les récompenses de base d'une quête en fonction de sa difficulté réelle
    et du niveau du joueur.

    Args:
        base_rewards: La liste des récompenses calculées par le générateur.
        quest_difficulty: La difficulté finale de la quête (peut avoir été scalée).
        player_level: Le niveau actuel du joueur.

    Returns:
        La liste des récompenses ajustées.
    """
    scaled_rewards = []
    level_difference = player_level - quest_difficulty

    for reward in base_rewards:
        # Copier la récompense pour ne pas modifier l'original si elle vient d'un cache
        # Si Reward est un dataclass simple, une copie superficielle suffit souvent.
        # Pour des objets complexes, utiliser copy.deepcopy si nécessaire.
        import copy
        new_reward = copy.copy(reward) # Copie superficielle

        if new_reward.type == "experience":
            # Appliquer un malus si la quête est trop facile pour le joueur
            # et potentiellement un léger bonus si elle est difficile (ou garder tel quel)
            xp_multiplier = 1.0
            if level_difference > 5: # Quête significativement plus facile
                xp_multiplier = max(0.1, 1.0 - (level_difference - 5) * 0.15) # Réduction forte
            elif level_difference > 2: # Quête un peu facile
                xp_multiplier = max(0.5, 1.0 - (level_difference - 2) * 0.1) # Réduction modérée
            # Pas de bonus pour quête difficile pour éviter power-leveling trop rapide ? Ou léger bonus ?
            # elif level_difference < -3: # Quête difficile
            #    xp_multiplier = 1.1 # Léger bonus

            new_reward.value = max(1, int(round(new_reward.value * xp_multiplier))) # XP minimum de 1

        elif new_reward.type == "gold":
            # L'or pourrait être moins affecté par la différence de niveau,
            # ou suivre une logique similaire à l'XP.
            gold_multiplier = 1.0
            if level_difference > 7: # Malus plus tardif pour l'or ?
                 gold_multiplier = max(0.2, 1.0 - (level_difference - 7) * 0.2)
            new_reward.value = max(1, int(round(new_reward.value * gold_multiplier)))

        # Les récompenses en objets pourraient être affectées différemment
        # ou déterminées par d'autres systèmes (loot tables basées sur la difficulté)
        elif new_reward.type == "item":
            # On pourrait vérifier si l'item est toujours pertinent pour le niveau du joueur
            # ou laisser tel quel.
            pass

        scaled_rewards.append(new_reward)

    # print(f"Scaling rewards: Difficulty={quest_difficulty}, PlayerLvl={player_level}, LvlDiff={level_difference}")
    # print(f"Base Rewards: {base_rewards}")
    # print(f"Scaled Rewards: {scaled_rewards}")

    return scaled_rewards

# Exemple d'utilisation (pourrait être dans des tests unitaires)
if __name__ == '__main__':
    class MockWorldStateSimple:
        def get_zone_difficulty_modifier(self):
            return 1.0 # Zone normale

    class MockWorldStateHard:
         def get_zone_difficulty_modifier(self):
            return 1.5 # Zone difficile

    player_lvl = 10
    base_diff = 8
    rewards_in = [Reward(type='experience', value=100), Reward(type='gold', value=50)]

    print("--- Test Scaling Difficulty ---")
    print(f"Player Level: {player_lvl}")
    print(f"Base Quest Difficulty: {base_diff}")
    scaled_normal = scale_difficulty(base_diff, player_lvl, MockWorldStateSimple())
    scaled_hard = scale_difficulty(base_diff, player_lvl, MockWorldStateHard())
    print(f"Scaled Difficulty (Normal Zone): {scaled_normal}")
    print(f"Scaled Difficulty (Hard Zone): {scaled_hard}")

    print("\n--- Test Scaling Rewards (Quest Easy) ---")
    player_lvl_high = 15
    rewards_easy = scale_rewards(rewards_in, base_diff, player_lvl_high)
    print(f"Player Level: {player_lvl_high}, Quest Difficulty: {base_diff}")
    print(f"Base: {rewards_in}")
    print(f"Scaled: {rewards_easy}")

    print("\n--- Test Scaling Rewards (Quest Matched) ---")
    player_lvl_match = 8
    rewards_match = scale_rewards(rewards_in, base_diff, player_lvl_match)
    print(f"Player Level: {player_lvl_match}, Quest Difficulty: {base_diff}")
    print(f"Base: {rewards_in}")
    print(f"Scaled: {rewards_match}")

    print("\n--- Test Scaling Rewards (Quest Hard) ---")
    player_lvl_low = 5
    rewards_hard = scale_rewards(rewards_in, base_diff, player_lvl_low)
    print(f"Player Level: {player_lvl_low}, Quest Difficulty: {base_diff}")
    print(f"Base: {rewards_in}")
    print(f"Scaled: {rewards_hard}")