# Système Psychologique des Ennemis

Le système psychologique des ennemis de Nightfall Defenders est une mécanique unique qui fait réagir les ennemis différemment en fonction de la puissance relative du joueur, créant une expérience dynamique et immersive.

## Vue d'Ensemble

Dans la plupart des jeux, les ennemis attaquent le joueur sans considération pour leur propre survie ou la puissance du joueur. Nightfall Defenders adopte une approche plus réaliste : les ennemis évaluent continuellement la menace que représente le joueur et ajustent leur comportement en conséquence.

## États Psychologiques

Les ennemis peuvent se trouver dans l'un des cinq états psychologiques suivants :

| État | Description | Comportement | Déclencheur |
|------|-------------|--------------|-------------|
| **Normal** | État standard | Attaque normalement | - |
| **Hésitant** | Légèrement intimidé | Pauses avant d'attaquer, peut se replier temporairement | Joueur ~20% plus fort |
| **Effrayé** | Inquiet pour sa survie | Évite activement le joueur, n'attaque que lorsqu'il est acculé | Joueur ~50% plus fort |
| **Terrifié** | Complètement dominé | Fuit à vue, n'attaque jamais | Joueur ~100% plus fort |
| **Soumis** | Reconnaît le joueur comme dominant | Suit le joueur, attaque d'autres ennemis | Joueur ~200% plus fort (rare) |
| **Renforcé** | Plus puissant dans le brouillard | Augmentation d'agressivité et de puissance | Dans le brouillard nocturne |

## Implémentation Technique

Le système est principalement implémenté dans `enemy_psychology.py` et comprend les composants suivants :

### 1. Calcul de Puissance Relative

```python
def calculate_player_power_ratio(self):
    """
    Calcule le ratio de puissance entre le joueur et l'ennemi
    
    Returns:
        float: Ratio de puissance (>1 signifie que le joueur est plus fort)
    """
    # Obtenir les statistiques pertinentes du joueur
    player = self.game.player
    player_level = player.level
    player_power = player_level * player.damage_multiplier
    
    # Ajuster en fonction de l'équipement
    if hasattr(player, 'equipment'):
        for item in player.equipment.values():
            if item:
                player_power += item.get('power_value', 0)
    
    # Ajuster en fonction des reliques
    if hasattr(player, 'relics'):
        for relic in player.relics:
            if relic.is_active:
                player_power += relic.power_value
    
    # Obtenir la puissance de base de l'ennemi
    enemy_level = getattr(self.enemy, 'level', 1)
    enemy_power = enemy_level * self.enemy.damage
    
    # Ajuster en fonction des traits psychologiques
    enemy_power *= self.traits.bravery
    
    # Calculer le ratio
    if enemy_power <= 0:
        return 10.0  # Éviter la division par zéro
    
    ratio = player_power / enemy_power
    
    # Appliquer des modificateurs contextuels
    ratio = self._apply_contextual_modifiers(ratio)
    
    return ratio
```

### 2. Traits Psychologiques

Chaque ennemi possède des traits psychologiques qui influencent ses réactions :

```python
class PsychologyTraits:
    """Définit les traits psychologiques qui affectent le comportement et les réponses de l'ennemi"""
    
    def __init__(self, 
                 bravery=1.0, 
                 aggression=1.0, 
                 intelligence=1.0, 
                 pack_mentality=1.0, 
                 dominance=1.0):
        """
        Initialiser les traits psychologiques
        
        Args:
            bravery (float): Résistance à la peur (0.5-1.5)
                - Des valeurs plus élevées augmentent les seuils pour les états psychologiques négatifs
                - Des valeurs plus basses rendent l'ennemi plus facilement effrayé
            
            aggression (float): Tendance à l'action offensive (0.5-1.5)
                - Des valeurs plus élevées augmentent la fréquence et les dégâts des attaques
                - Des valeurs plus basses conduisent à un comportement plus défensif
            
            intelligence (float): Capacité de prise de décision tactique (0.5-1.5)
                - Des valeurs plus élevées permettent des stratégies plus complexes
                - Des valeurs plus basses conduisent à un comportement plus prévisible
            
            pack_mentality (float): Influence de et sur les alliés proches (0.5-1.5)
                - Des valeurs plus élevées rendent l'ennemi plus affecté par la psychologie de groupe
                - Des valeurs plus basses rendent l'ennemi plus indépendant
            
            dominance (float): Leadership et influence sur les autres (0.5-1.5)
                - Des valeurs plus élevées permettent aux ennemis de rallier les autres
                - Des valeurs plus basses les rendent plus susceptibles de suivre les autres
        """
        # Assurer que les traits sont dans la plage valide
        self.bravery = max(0.5, min(1.5, bravery))
        self.aggression = max(0.5, min(1.5, aggression))
        self.intelligence = max(0.5, min(1.5, intelligence))
        self.pack_mentality = max(0.5, min(1.5, pack_mentality))
        self.dominance = max(0.5, min(1.5, dominance))
        
        # Attributs dérivés
        self.is_alpha = dominance >= 1.3  # Les ennemis alpha ont une dominance élevée
```

### 3. Mise à Jour de l'État Psychologique

```python
def update(self, dt):
    """
    Mettre à jour l'état psychologique
    
    Args:
        dt: Delta temps en secondes
    """
    # Calculer le ratio de puissance actuel
    power_ratio = self.calculate_player_power_ratio()
    
    # Mettre à jour le niveau de confiance
    target_confidence = 1.0 / max(1.0, power_ratio)
    self.confidence = lerp(self.confidence, target_confidence, dt * (1.0 - self.inertia))
    
    # Calculer la puissance du pack
    pack_bonus = self.calculate_pack_strength()
    adjusted_confidence = self.confidence + pack_bonus
    
    # Déterminer l'état cible
    target_state = self._determine_target_state(adjusted_confidence)
    
    # Changer d'état si nécessaire
    if target_state != self.state:
        # Transition avec délai
        if self.pending_state_change is None:
            # Déterminer le délai basé sur l'intelligence
            delay = 1.0 / max(0.5, self.traits.intelligence)
            
            # Moins de délai pour des changements plus importants
            severity_diff = abs(self._get_state_severity(target_state) - 
                             self._get_state_severity(self.state))
            delay /= max(1.0, severity_diff)
            
            self.pending_state_change = target_state
            self.state_change_delay = delay
            self.reaction_timer = 0.0
        else:
            # Déjà en attente d'un changement d'état
            if target_state != self.pending_state_change:
                # Nouvel état cible différent, mettre à jour
                self.pending_state_change = target_state
                # Réinitialiser le timer pour le nouvel état
                self.reaction_timer = 0.0
    else:
        # Même état cible, annuler toute transition en attente
        self.pending_state_change = None
    
    # Gérer les transitions d'état en attente
    if self.pending_state_change:
        self.reaction_timer += dt
        if self.reaction_timer >= self.state_change_delay:
            # Transition terminée
            old_state = self.state
            self.state = self.pending_state_change
            self.pending_state_change = None
            
            # Réagir au changement d'état
            self._on_state_changed(old_state, self.state)
    
    # Mettre à jour les modificateurs de comportement
    self._update_behavior_modifiers()
    
    # Vérifier si l'ennemi est dans le brouillard
    self._check_fog_state()
    
    # Mettre à jour l'animation de l'indicateur
    self.update_indicator_animation(dt)
```

### 4. Détermination de l'État Cible

```python
def _determine_target_state(self, confidence):
    """
    Déterminer l'état psychologique cible basé sur le niveau de confiance
    
    Args:
        confidence: Niveau de confiance actuel (0.0-1.0)
        
    Returns:
        PsychologicalState: L'état cible
    """
    # Vérifier si l'ennemi est renforcé par le brouillard
    if self.in_fog and self.fog_empowerment > 0.5:
        return PsychologicalState.EMPOWERED
    
    # Appliquer des seuils basés sur les traits
    if confidence < 1.0 / self.subservient_threshold:
        # Chance de soumission au lieu de terreur
        if random.random() < self.subservience_chance:
            return PsychologicalState.SUBSERVIENT
        else:
            return PsychologicalState.TERRIFIED
    elif confidence < 1.0 / self.terrified_threshold:
        return PsychologicalState.TERRIFIED
    elif confidence < 1.0 / self.fearful_threshold:
        return PsychologicalState.FEARFUL
    elif confidence < 1.0 / self.hesitant_threshold:
        return PsychologicalState.HESITANT
    else:
        return PsychologicalState.NORMAL
```

### 5. Modificateurs de Comportement

```python
def _update_behavior_modifiers(self):
    """Mettre à jour les modificateurs de comportement basés sur l'état psychologique"""
    # Réinitialiser les modificateurs
    self.attack_chance_modifier = 1.0
    self.speed_modifier = 1.0
    self.damage_modifier = 1.0
    
    # Appliquer les modifications basées sur l'état
    if self.state == PsychologicalState.NORMAL:
        # Comportement standard
        pass
    
    elif self.state == PsychologicalState.HESITANT:
        # Moins susceptible d'attaquer, légèrement plus rapide (nerveux)
        self.attack_chance_modifier = 0.7
        self.speed_modifier = 1.1
        self.damage_modifier = 0.9
        
        # Mise à jour de l'indicateur visuel
        self.indicator_color = (1.0, 0.8, 0.2, 1.0)  # Orange
        self.indicator_emoji = "❓"
    
    elif self.state == PsychologicalState.FEARFUL:
        # Beaucoup moins susceptible d'attaquer, plus rapide (fuite)
        self.attack_chance_modifier = 0.4
        self.speed_modifier = 1.3
        self.damage_modifier = 0.8
        
        # Mise à jour de l'indicateur visuel
        self.indicator_color = (1.0, 0.5, 0.0, 1.0)  # Orange foncé
        self.indicator_emoji = "⚠️"
    
    elif self.state == PsychologicalState.TERRIFIED:
        # Ne veut pas attaquer, très rapide (fuite paniquée)
        self.attack_chance_modifier = 0.1
        self.speed_modifier = 1.5
        self.damage_modifier = 0.6
        
        # Mise à jour de l'indicateur visuel
        self.indicator_color = (1.0, 0.0, 0.0, 1.0)  # Rouge
        self.indicator_emoji = "😱"
    
    elif self.state == PsychologicalState.SUBSERVIENT:
        # Attaque les autres ennemis, pas le joueur
        self.attack_chance_modifier = 0.0  # N'attaque pas le joueur
        self.speed_modifier = 0.9  # Légèrement plus lent (suit le joueur)
        
        # Mise à jour de l'indicateur visuel
        self.indicator_color = (0.0, 0.8, 1.0, 1.0)  # Bleu clair
        self.indicator_emoji = "🙏"
    
    elif self.state == PsychologicalState.EMPOWERED:
        # Plus agressif et plus fort dans le brouillard
        self.attack_chance_modifier = 1.3
        self.speed_modifier = 1.2
        self.damage_modifier = 1.4
        
        # Mise à jour de l'indicateur visuel
        self.indicator_color = (0.7, 0.0, 1.0, 1.0)  # Violet
        self.indicator_emoji = "💪"
    
    # Appliquer des modifications basées sur les traits
    self.attack_chance_modifier *= self.traits.aggression
    
    # Appliquer le modificateur de groupe (plus confiant en groupe)
    if self.nearby_ally_count > 0:
        pack_confidence_boost = min(0.5, self.nearby_ally_count * 0.1 * self.traits.pack_mentality)
        self.attack_chance_modifier *= (1.0 + pack_confidence_boost)
    
    # Effet alpha: les ennemis alpha restent plus agressifs même quand ils ont peur
    if self.traits.is_alpha and self.state in [PsychologicalState.HESITANT, PsychologicalState.FEARFUL]:
        self.attack_chance_modifier *= 1.5
```

### 6. Contagion Émotionnelle

```python
def calculate_pack_strength(self):
    """
    Calculer le bonus de force du groupe
    
    Returns:
        float: Bonus de confiance basé sur les alliés proches
    """
    if not self.nearby_allies or len(self.nearby_allies) == 0:
        self.nearby_ally_count = 0
        self.pack_strength_bonus = 0.0
        self.alpha_nearby = False
        return 0.0
    
    # Mettre à jour le compteur d'alliés
    self.nearby_ally_count = len(self.nearby_allies)
    
    # Base de la force du groupe dépend du nombre d'alliés
    base_strength = min(0.3, self.nearby_ally_count * 0.05)
    
    # Multiplier par la mentalité de groupe
    pack_bonus = base_strength * self.traits.pack_mentality
    
    # Rechercher des alphas et calculer la confiance moyenne du groupe
    alpha_present = False
    total_confidence = 0.0
    influencers_count = 0
    
    for ally in self.nearby_allies:
        if hasattr(ally, 'psychology'):
            # Les alliés à haute dominance ont plus d'influence
            influence = ally.psychology.traits.get_pack_influence()
            total_confidence += ally.psychology.confidence * influence
            influencers_count += influence
            
            # Vérifier si c'est un alpha
            if ally.psychology.traits.is_alpha:
                alpha_present = True
                # Les alphas donnent un bonus supplémentaire
                pack_bonus += 0.2 * influence
    
    # Stocker pour référence
    self.alpha_nearby = alpha_present
    
    # Calculer la confiance moyenne du groupe si des alliés avec psychologie sont présents
    if influencers_count > 0:
        average_confidence = total_confidence / influencers_count
        
        # La contagion émotionnelle - tirer vers la moyenne du groupe
        contagion_strength = self.traits.pack_mentality * 0.5
        pack_bonus += (average_confidence - self.confidence) * contagion_strength
    
    # Limiter les valeurs
    pack_bonus = max(-0.5, min(0.5, pack_bonus))
    
    # Stocker pour référence
    self.pack_strength_bonus = pack_bonus
    
    return pack_bonus
```

### 7. Mémoire et Apprentissage

```python
def record_player_encounter(self, encounter_type='spotted', damage_taken=0):
    """
    Enregistrer une rencontre avec le joueur
    
    Args:
        encounter_type (str): Type de rencontre ('spotted', 'damaged', 'attacked')
        damage_taken (float): Quantité de dégâts reçus
    """
    self.memory['player_encounters'] += 1
    
    if damage_taken > 0:
        self.memory['damage_taken'] += damage_taken
        self.memory['last_encounter_outcome'] = 'damaged'
        
        # Augmenter le facteur de rancune proportionnellement aux dégâts
        grudge_increase = min(0.2, damage_taken / self.enemy.max_health)
        self.memory['grudge_factor'] = min(1.0, self.memory['grudge_factor'] + grudge_increase)
        
        # Les ennemis intelligents se souviennent mieux des interactions négatives
        if self.traits.intelligence > 1.2:
            self.memory['grudge_factor'] *= 1.2
    else:
        # Interaction neutre ou positive
        self.memory['last_encounter_outcome'] = encounter_type
    
    # Enregistrer l'horodatage
    self.memory['encounter_timestamps'].append(time.time())
    
    # Limiter la taille de l'historique
    if len(self.memory['encounter_timestamps']) > 10:
        self.memory['encounter_timestamps'] = self.memory['encounter_timestamps'][-10:]
    
    # Déclin de la rancune avec le temps si pas de dommage récent
    recent_encounters = time.time() - self.memory['encounter_timestamps'][0] < 300  # 5 minutes
    if not recent_encounters and self.memory['grudge_factor'] > 0:
        self.memory['grudge_factor'] *= 0.95  # Déclin lent
```

### 8. Effets du Brouillard Nocturne

```python
def _check_fog_state(self):
    """Vérifier si l'ennemi est dans le brouillard nocturne et appliquer les effets appropriés"""
    # Vérifie si le système de brouillard existe et si l'ennemi est dedans
    if hasattr(self.game, 'night_fog') and self.game.night_fog.active:
        was_in_fog = self.in_fog
        self.in_fog = self.game.night_fog.is_in_fog(self.enemy.position)
        
        if self.in_fog:
            # Augmenter progressivement l'empowerment dans le brouillard
            self.fog_empowerment = min(1.0, self.fog_empowerment + 0.05)
            
            # Chance de passer à l'état renforcé si suffisamment dans le brouillard
            if self.fog_empowerment > 0.7 and random.random() < 0.1:
                old_state = self.state
                self.state = PsychologicalState.EMPOWERED
                self._on_state_changed(old_state, self.state)
        else:
            # Diminuer progressivement l'empowerment hors du brouillard
            self.fog_empowerment = max(0.0, self.fog_empowerment - 0.1)
            
            # Revenir à l'état normal si renforcé mais plus dans le brouillard
            if self.state == PsychologicalState.EMPOWERED and self.fog_empowerment < 0.2:
                # Recalculer l'état approprié
                power_ratio = self.calculate_player_power_ratio()
                confidence = 1.0 / max(1.0, power_ratio)
                target_state = self._determine_target_state(confidence)
                
                old_state = self.state
                self.state = target_state
                self._on_state_changed(old_state, self.state)
        
        # Notifier du changement si nécessaire
        if was_in_fog != self.in_fog:
            self._on_fog_state_changed(self.in_fog)
    else:
        # Pas de brouillard actif
        self.in_fog = False
        self.fog_empowerment = 0.0
```

### 9. Indicateurs Visuels

```python
def _update_visual_indicator(self):
    """Mettre à jour l'indicateur visuel basé sur l'état psychologique"""
    
    if not self.indicator_node:
        return
        
    try:
        from panda3d.core import TextNode, NodePath, TransparencyAttrib
        
        # Nettoyer l'ancien emoji s'il existe
        for child in self.indicator_node.getChildren():
            if child.getName() == "emoji_text":
                child.removeNode()
        
        # Créer un nœud de texte pour l'emoji
        text_node = TextNode("emoji_text")
        text_node.setText(self._get_state_emoji())
        text_node.setAlign(TextNode.ACenter)
        
        # Ajuster la taille de l'emoji
        emoji_size = 0.7 * self.indicator_size
        if self.state == PsychologicalState.TERRIFIED:
            emoji_size *= 1.2  # Plus grand pour terrified
        elif self.state == PsychologicalState.EMPOWERED:
            emoji_size *= 1.3  # Plus grand pour empowered
        
        text_node.setTextScale(emoji_size, emoji_size)
        
        # Créer le NodePath et le convertir pour regarder la caméra
        emoji_np = self.indicator_node.attachNewNode(text_node)
        emoji_np.setBillboardPointEye()
        emoji_np.setDepthWrite(False)
        emoji_np.setDepthTest(False)
        emoji_np.setTransparency(TransparencyAttrib.MAlpha)
        
        # Le positionner au-dessus de l'ennemi
        emoji_np.setPos(0, 0, 0.2)
        
        # Créer un effet de pulsation si l'état est intense
        if self.state in [PsychologicalState.TERRIFIED, PsychologicalState.EMPOWERED, 
                         PsychologicalState.SUBSERVIENT]:
            
            from direct.interval.LerpInterval import LerpScaleInterval
            from direct.interval.MetaInterval import Sequence
            
            # Créer une séquence de pulsation
            pulse = Sequence(
                LerpScaleInterval(emoji_np, 0.5 / self.indicator_pulse_speed, 
                                 1.2, startScale=1.0,
                                 blendType='easeInOut'),
                LerpScaleInterval(emoji_np, 0.5 / self.indicator_pulse_speed, 
                                 1.0, startScale=1.2,
                                 blendType='easeInOut')
            )
            pulse.loop()
            
            # Stocker pour pouvoir l'arrêter plus tard
            self.indicator_animation = pulse
    
    except ImportError as e:
        print(f"Cannot update visual indicator: {e}")
```

## Intégration avec d'Autres Systèmes

### Brouillard Nocturne

Le système psychologique interagit directement avec le brouillard nocturne :

- Les ennemis dans le brouillard gagnent progressivement un état **Renforcé**
- Cet état augmente leur agressivité, leur vitesse et leurs dégâts
- Le brouillard peut temporairement neutraliser la peur d'ennemis normalement effrayés

### Système de Combat

Le comportement de combat des ennemis est profondément affecté par leur état psychologique :

```python
def should_attack_player(self):
    """
    Détermine si l'ennemi doit attaquer le joueur
    
    Returns:
        bool: True si l'ennemi doit attaquer
    """
    # Les ennemis soumis n'attaquent jamais le joueur
    if self.state == PsychologicalState.SUBSERVIENT:
        return False
    
    # Les ennemis terrifiés attaquent rarement et seulement s'ils sont acculés
    if self.state == PsychologicalState.TERRIFIED:
        # Attaque seulement si acculé
        is_cornered = self.enemy.check_if_cornered()
        if is_cornered:
            return random.random() < (self.attack_chance_modifier * 0.5)
        return False
    
    # Pour les autres états, utiliser le modificateur de chance d'attaque
    base_attack_chance = 0.8  # 80% de chance en temps normal
    return random.random() < (base_attack_chance * self.attack_chance_modifier)
```

### Système de Groupe

Les ennemis peuvent:
- Communiquer leur état psychologique aux alliés proches
- Être influencés par des ennemis alpha
- Prendre des décisions tactiques en groupe
- Alerter d'autres ennemis de la présence du joueur

## Exemples de Comportements

### Exemple 1: Groupe d'Ennemis Faibles vs Joueur Puissant

1. Le joueur puissant approche
2. Les ennemis calculent le ratio de puissance (~2.0)
3. La plupart passent à l'état **Effrayé**
4. Ils se regroupent pour bénéficier du bonus de groupe
5. S'ils ont un alpha, ils peuvent rester à l'état **Hésitant**
6. Les plus faibles fuient tandis que certains tenteront des attaques occasionnelles

### Exemple 2: Ennemi dans le Brouillard

1. L'ennemi entre dans le brouillard nocturne
2. Son niveau d'empowerment augmente progressivement
3. Il passe à l'état **Renforcé**
4. Son agressivité, sa vitesse et ses dégâts augmentent
5. Même face à un joueur plus fort, il maintient une posture agressive
6. En quittant le brouillard, il revient progressivement à son état normal

## Impacts sur le Gameplay

Le système psychologique des ennemis crée plusieurs impacts positifs sur l'expérience de jeu :

1. **Feedback Organique sur la Progression** - Les joueurs ressentent leur progression de puissance à travers le comportement des ennemis
2. **Décisions Stratégiques** - Les joueurs peuvent choisir d'intimider les ennemis ou rester discrets
3. **Variété des Rencontres** - Même les ennemis identiques peuvent se comporter différemment selon les circonstances
4. **Moments d'Adrénaline** - Quand des ennemis effrayés se retrouvent soudainement renforcés dans le brouillard
5. **Conséquences Emergeantes** - Les interactions entre ennemis de différents états créent des situations uniques

## Extensibilité Future

Le système est conçu pour être étendu avec :

- Plus d'états psychologiques spécialisés
- Mémoire à long terme des ennemis (reconnaissance des joueurs)
- Communications complexes entre groupes d'ennemis
- Tactiques de groupe basées sur l'état psychologique collectif
- Émotions plus complexes comme la jalousie, la loyauté ou la vengeance 