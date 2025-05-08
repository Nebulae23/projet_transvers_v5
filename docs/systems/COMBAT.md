# Système de Combat Basé sur les Trajectoires

Le système de combat de Nightfall Defenders se distingue par son approche originale basée sur différents types de trajectoires pour les projectiles et les capacités. Ce document détaille en profondeur ce système central du jeu.

## Principes Fondamentaux

Le système de combat est construit autour de deux idées principales :

1. **Trajectoires basées sur la physique** pour les capacités primaires
2. **Trajectoires prédéterminées avec variation** pour les capacités secondaires

Cette approche crée un gameplay riche et varié, où les joueurs doivent maîtriser différents types de trajectoires pour maximiser leur efficacité au combat.

## Architecture du Système

![Architecture du Système de Combat](../images/combat_system_architecture.png)

Le système de combat est implémenté principalement dans ces fichiers :

- `ability_system.py` : Définit la base du système de capacités
- `projectile.py` : Gère les projectiles et leurs comportements
- `physics_manager.py` : Fournit la simulation physique pour les trajectoires

## Types de Trajectoires

### Trajectoires Primaires (Basées sur la Physique)

Les capacités primaires utilisent des trajectoires basées sur un système de physique complet pour un comportement réaliste et interactif.

#### Ligne Droite

**Description :** Projectile se déplaçant en ligne droite jusqu'à collision ou portée maximale.

**Implémentation :**
```python
def create_straight_projectile(self, caster, target_pos):
    direction = (target_pos - caster.position).normalized()
    velocity = direction * self.projectile_speed
    return Projectile(
        position=caster.position,
        velocity=velocity,
        lifetime=self.range / self.projectile_speed,
        damage=self.get_total_damage(),
        owner=caster,
        effects=self.effects
    )
```

**Exemple d'utilisation :** L'Éclair Magique du Mage, le Tir Précis du Rôdeur

#### Arc (Balistique)

**Description :** Projectile affecté par la gravité, suivant une trajectoire parabolique.

**Implémentation :**
```python
def create_arcing_projectile(self, caster, target_pos):
    # Calcul de la trajectoire parabolique
    distance = (target_pos - caster.position).length()
    angle = calculate_optimal_angle(distance, self.projectile_speed, GRAVITY)
    
    # Détermination de la vitesse initiale
    direction = (target_pos - caster.position).normalized()
    horizontal_velocity = direction * self.projectile_speed * math.cos(angle)
    vertical_velocity = self.projectile_speed * math.sin(angle)
    velocity = Vec3(horizontal_velocity.x, horizontal_velocity.y, vertical_velocity)
    
    return Projectile(
        position=caster.position,
        velocity=velocity,
        gravity=Vec3(0, 0, -GRAVITY),
        lifetime=estimate_flight_time(distance, self.projectile_speed, angle),
        damage=self.get_total_damage(),
        owner=caster,
        effects=self.effects
    )
```

**Exemple d'utilisation :** Boule de Feu du Mage, Bombe Acide de l'Alchimiste

#### À Tête Chercheuse

**Description :** Projectile qui suit activement une cible, avec différentes intensités de poursuite.

**Implémentation :**
```python
def update_homing_projectile(self, dt):
    if self.target and self.target.is_alive():
        # Calculer la direction vers la cible
        direction_to_target = (self.target.position - self.position).normalized()
        
        # Appliquer un facteur de direction basé sur l'intensité de la poursuite
        self.velocity = lerp(
            self.velocity, 
            direction_to_target * self.speed,
            self.homing_intensity * dt
        )
    
    # Mettre à jour la position
    self.position += self.velocity * dt
```

**Exemple d'utilisation :** Missiles Guidés, Esprits Chasseurs de l'Invocateur

#### Orbital

**Description :** Projectile qui orbite autour du lanceur avant d'être relâché vers la cible.

**Implémentation :**
```python
def update_orbital_projectile(self, dt):
    if self.orbital_phase < self.orbital_duration:
        # Phase orbitale - tourner autour du lanceur
        self.orbital_angle += self.orbital_speed * dt
        orbit_position = Vec3(
            math.cos(self.orbital_angle) * self.orbital_radius,
            math.sin(self.orbital_angle) * self.orbital_radius,
            0
        )
        self.position = self.owner.position + orbit_position
        self.orbital_phase += dt
    else:
        # Phase de lancement - se diriger vers la cible
        if not self.launched:
            self.velocity = (self.target_position - self.position).normalized() * self.speed
            self.launched = True
        
        self.position += self.velocity * dt
```

**Exemple d'utilisation :** Orbes Orbitales, Étoiles Filantes

### Trajectoires Secondaires (Prédéterminées)

Les capacités secondaires utilisent des trajectoires prédéterminées avec des variations pour créer des motifs d'attaque plus complexes.

#### Zigzag

**Description :** Projectile qui suit un chemin en zigzag, alternant les directions.

**Implémentation :**
```python
def update_zigzag_projectile(self, dt):
    # Calculer le décalage latéral basé sur un motif sinusoïdal
    self.zigzag_phase += dt * self.zigzag_frequency
    lateral_offset = math.sin(self.zigzag_phase) * self.zigzag_amplitude
    
    # Calculer la direction vers l'avant avec un décalage latéral
    forward = self.forward_direction
    right = Vec3(-forward.y, forward.x, 0)  # Vecteur perpendiculaire
    
    # Combiner pour obtenir la direction réelle
    actual_direction = forward + right * lateral_offset
    
    # Mettre à jour la position
    self.position += actual_direction.normalized() * self.speed * dt
```

**Exemple d'utilisation :** Éclair Erratique, Flèche Serpentine

#### Spirale

**Description :** Projectiles multiples qui s'étendent vers l'extérieur dans un motif spiral.

**Implémentation :**
```python
def create_spiral_pattern(self, caster, center_pos, num_projectiles=8, spiral_turns=2):
    projectiles = []
    
    for i in range(num_projectiles):
        # Calculer l'angle dans la spirale
        angle_progress = i / num_projectiles
        angle = angle_progress * spiral_turns * 2 * math.pi
        
        # Calculer la distance radiale (augmente avec l'angle)
        radius = self.min_radius + (angle / (spiral_turns * 2 * math.pi)) * (self.max_radius - self.min_radius)
        
        # Calculer la position
        position = Vec3(
            center_pos.x + radius * math.cos(angle),
            center_pos.y + radius * math.sin(angle),
            center_pos.z
        )
        
        # Créer le projectile
        projectiles.append(Projectile(
            position=position,
            velocity=Vec3(0, 0, 0),  # Position statique ou avec mouvement personnalisé
            lifetime=self.duration,
            damage=self.get_total_damage() / num_projectiles,  # Répartir les dégâts
            owner=caster,
            effects=self.effects
        ))
    
    return projectiles
```

**Exemple d'utilisation :** Nova Arcanique, Tempête d'Éclats

#### Rebondissante

**Description :** Projectile qui rebondit sur les surfaces et continue son trajet.

**Implémentation :**
```python
def handle_collision(self, hit_point, normal):
    # Calculer la vélocité de rebond (réflexion)
    self.velocity = reflect(self.velocity, normal) * self.bounce_factor
    
    # Repositionner légèrement pour éviter de rester collé à la surface
    self.position = hit_point + normal * 0.1
    
    # Réduire la durée de vie et les dégâts à chaque rebond
    self.lifetime *= self.bounce_lifetime_factor
    self.damage *= self.bounce_damage_factor
    
    # Incrémenter le compteur de rebonds
    self.bounce_count += 1
    
    # Vérifier si le nombre maximal de rebonds est atteint
    if self.bounce_count >= self.max_bounces:
        self.destroy()
```

**Exemple d'utilisation :** Orbe Rebondissante, Dague Ricochante

#### Vague

**Description :** Projectiles qui se déplacent selon un motif ondulatoire.

**Implémentation :**
```python
def update_wave_projectile(self, dt):
    # Mettre à jour la phase de la vague
    self.wave_phase += dt * self.wave_frequency
    
    # Calculer le décalage basé sur une fonction sinusoïdale
    wave_offset = math.sin(self.wave_phase) * self.wave_amplitude
    
    # Calculer la direction vers l'avant
    forward = self.forward_direction
    
    # Calculer la direction latérale (perpendiculaire)
    lateral = Vec3(-forward.y, forward.x, 0)
    
    # Combiner pour obtenir la position réelle
    self.position += forward * self.speed * dt
    self.position += lateral * (wave_offset - self.last_wave_offset)
    
    # Stocker l'offset actuel pour le prochain calcul
    self.last_wave_offset = wave_offset
```

**Exemple d'utilisation :** Vague d'Énergie, Éclairs Sinusoïdaux

#### Aléatoire

**Description :** Projectiles avec des points d'apparition et/ou des comportements aléatoires.

**Implémentation :**
```python
def create_random_projectile_burst(self, caster, target_area, num_projectiles=5):
    projectiles = []
    
    for i in range(num_projectiles):
        # Générer une position aléatoire dans la zone cible
        random_offset = Vec3(
            random.uniform(-target_area.radius, target_area.radius),
            random.uniform(-target_area.radius, target_area.radius),
            0
        )
        position = target_area.center + random_offset
        
        # Générer une direction aléatoire si nécessaire
        random_direction = Vec3(
            random.uniform(-1, 1),
            random.uniform(-1, 1),
            0
        ).normalized()
        
        # Créer le projectile
        projectiles.append(Projectile(
            position=position,
            velocity=random_direction * self.projectile_speed,
            lifetime=random.uniform(self.min_lifetime, self.max_lifetime),
            damage=self.get_total_damage() / num_projectiles,
            owner=caster,
            effects=self.effects
        ))
    
    return projectiles
```

**Exemple d'utilisation :** Pluie Météorique, Éruption Chaotique

## Modèles de Capacités

Le système de combat comprend plusieurs modèles de capacités qui utilisent ces trajectoires.

### Capacités de Zone (AoE)

```python
class AreaAbility(Ability):
    def __init__(self, ability_id, name, description, 
                 effect_type="damage", value=10, radius=5.0, duration=0.0,
                 cooldown=5.0, resource_cost=20, icon=None):
        # Initialisation
        
    def use(self, caster, target=None, position=None):
        # Créer l'effet de zone
        effect = AreaEffect(
            position=position or caster.position,
            radius=self.radius,
            effect_type=self.effect_type,
            value=self.value,
            duration=self.duration,
            owner=caster,
            effects=self.effects
        )
        
        # Appliquer l'effet immédiatement à tous les objets dans le rayon
        for entity in get_entities_in_radius(effect.position, effect.radius):
            if self._can_affect(caster, entity):
                self._apply_effect(effect, entity)
        
        # Si l'effet a une durée, l'ajouter au gestionnaire d'effets
        if self.duration > 0:
            EffectManager.instance.add_area_effect(effect)
        
        return True
```

### Capacités de Mêlée

```python
class MeleeAbility(Ability):
    def __init__(self, ability_id, name, description, 
                 damage=20, range=2.0, angle=90.0,
                 cooldown=0.5, resource_cost=0, icon=None):
        # Initialisation
        
    def use(self, caster, target=None, position=None):
        # Déterminer la direction de l'attaque
        if position:
            direction = (position - caster.position).normalized()
        elif target:
            direction = (target.position - caster.position).normalized()
        else:
            direction = caster.facing_direction
        
        # Créer un secteur d'attaque
        attack_sector = {
            'position': caster.position,
            'direction': direction,
            'range': self.range,
            'angle': self.angle,
            'damage': self.get_total_damage(),
            'owner': caster,
            'effects': self.effects
        }
        
        # Trouver les cibles dans le secteur
        targets = find_targets_in_sector(attack_sector)
        
        # Appliquer les dégâts et effets
        for target in targets:
            self._apply_damage(target, self.get_total_damage())
            self._apply_effects(target)
        
        # Créer un effet visuel
        self._create_melee_visual(caster, direction, self.range, self.angle)
        
        return True
```

## Évolution des Capacités

Le système de combat permet trois types d'évolution des capacités :

### 1. Spécialisation

Permet de concentrer une capacité sur une voie spécifique, modifiant son comportement de base.

```python
def specialize(self, path):
    """
    Spécialiser la capacité dans une voie spécifique
    
    Args:
        path (SpecializationPath): Le chemin de spécialisation
    """
    if self.is_specialized:
        return False
    
    self.is_specialized = True
    self.specialization_path = path
    
    # Appliquer les modifications basées sur le chemin
    if path == SpecializationPath.DAMAGE:
        self.damage = int(self.damage * 1.5)  # +50% de dégâts
        self.cooldown = self.cooldown * 1.2  # +20% de temps de recharge
    elif path == SpecializationPath.UTILITY:
        # Ajouter des effets supplémentaires
        self.effects.append("stun_short")
        self.effects.append("knockback_small")
    elif path == SpecializationPath.EFFICIENCY:
        self.cooldown = self.cooldown * 0.7  # -30% de temps de recharge
        self.damage = int(self.damage * 0.9)  # -10% de dégâts
    
    return True
```

**Exemples de spécialisation :**
- Boule de Feu → Météore (dégâts et zone augmentés)
- Boule de Feu → Rayon (dégâts continus, précision)
- Boule de Feu → Nova de Feu (dispersion à 360°)

### 2. Fusion

Permet de combiner deux capacités pour créer une nouvelle capacité hybride.

```python
def create_fusion(self, other_ability):
    """
    Créer une fusion avec une autre capacité
    
    Args:
        other_ability (Ability): L'autre capacité à fusionner
        
    Returns:
        Ability: La nouvelle capacité fusionnée, ou None si incompatible
    """
    # Vérifier la compatibilité
    if not self.can_fuse_with(other_ability):
        return None
    
    # Chercher une recette de fusion
    fusion_manager = FusionRecipeManager.instance
    recipe = fusion_manager.find_recipe(self, other_ability)
    
    if not recipe:
        return None
    
    # Créer la nouvelle capacité fusionnée
    fusion = Ability(
        name=recipe.name,
        description=recipe.description,
        damage=(self.damage + other_ability.damage) // 2,  # Moyenne des dégâts
        cooldown=max(self.cooldown, other_ability.cooldown) * 1.2,  # Le plus long +20%
        range=max(self.range, other_ability.range),
        ability_type=recipe.output.get('ability_type', self.ability_type),
        trajectory="fusion",
        effects=recipe.output.get('effects', []),
        element_type=recipe.output.get('element_type', self.element_type)
    )
    
    fusion.is_fused = True
    fusion.fusion_components = [self, other_ability]
    
    return fusion
```

**Exemples de fusion :**
- Feu + Glace = Vapeur (obscurcit la vision, dégâts sur la durée)
- Foudre + Mouvement = Téléportation
- Bouclier + Projectile = Barrière Réfléchissante

### 3. Harmonisation

Permet d'améliorer une capacité existante avec des effets supplémentaires.

```python
def harmonize(self, effect_data=None):
    """
    Harmoniser la capacité pour améliorer ses effets
    
    Args:
        effect_data (dict, optional): Données spécifiques d'effet. Si None,
                                      utilise le gestionnaire d'harmonisation.
    
    Returns:
        bool: True si l'harmonisation a réussi
    """
    if self.is_harmonized:
        # Augmenter le niveau d'harmonisation si déjà harmonisé
        if self.harmonization_level < 3:  # Maximum 3 niveaux
            self.harmonization_level += 1
            self._apply_harmonization_level()
            return True
        return False
    
    # Chercher un effet d'harmonisation approprié si aucun n'est fourni
    if effect_data is None:
        harmonization_manager = HarmonizationManager.instance
        effect = harmonization_manager.find_effect(self)
        if effect:
            effect_data = effect.effect_data
            self.harmonization_effect = effect
        else:
            return False
    
    # Appliquer l'harmonisation
    self.is_harmonized = True
    self.harmonization_level = 1
    
    # Appliquer les modifications basées sur les données d'effet
    if 'projectile_count' in effect_data:
        self.projectile_count = effect_data['projectile_count']
    if 'damage_multiplier' in effect_data:
        self.damage = int(self.damage * effect_data['damage_multiplier'])
    if 'cooldown_multiplier' in effect_data:
        self.cooldown = self.cooldown * effect_data['cooldown_multiplier']
    
    # Modifier le comportement de la capacité
    self._modify_behavior_for_harmonization(effect_data)
    
    return True
```

**Exemples d'harmonisation :**
- Météore + Harmonisation = Multiples petits météores
- Laser + Harmonisation = Rayon continu avec dégâts croissants
- Nova de Feu + Harmonisation = Vagues de feu pulsantes

## Interaction avec les Systèmes de Physique

Le système de combat interagit directement avec le système de physique pour créer des comportements réalistes :

```python
def apply_physics_effects(self, world_physics):
    """
    Applique les effets physiques à ce projectile
    
    Args:
        world_physics: Le système de physique du monde
    """
    # Appliquer la gravité si activée
    if self.affected_by_gravity:
        self.velocity += world_physics.gravity * self.gravity_factor * dt
    
    # Appliquer la résistance de l'air
    if self.affected_by_air_resistance:
        speed = self.velocity.length()
        if speed > 0:
            drag_force = 0.5 * self.drag_coefficient * speed * speed
            drag_deceleration = drag_force / self.mass
            drag_direction = -self.velocity.normalized()
            self.velocity += drag_direction * drag_deceleration * dt
    
    # Déplacer le projectile
    self.old_position = self.position
    self.position += self.velocity * dt
    
    # Vérifier les collisions
    collision = world_physics.check_ray_collision(self.old_position, self.position)
    if collision:
        self.handle_collision(collision.hit_point, collision.normal)
```

## Effets Visuels et Sonores

Le système de combat s'accompagne d'effets visuels et sonores riches pour améliorer l'expérience utilisateur :

```python
def _create_projectile_visual(self, projectile):
    """
    Crée les effets visuels pour un projectile
    
    Args:
        projectile: Le projectile à visualiser
    """
    # Créer le modèle visuel du projectile
    visual = self._create_projectile_model()
    
    # Ajouter des particules si nécessaire
    if self.has_particle_trail:
        particle_system = ParticleSystem({
            'emission_rate': 30,
            'lifetime': 0.5,
            'size': (0.2, 0.1),
            'color': self.particle_color,
            'blend_mode': 'add'
        })
        visual.attach_particle_system(particle_system)
    
    # Ajouter une lueur si nécessaire
    if self.has_glow:
        glow = create_glow_effect(self.glow_color, self.glow_intensity)
        visual.attach_glow(glow)
    
    # Associer au projectile
    projectile.visual = visual
    
    # Jouer un son de lancement
    play_sound_3d(self.launch_sound, projectile.position)
```

## Extensibilité du Système

Le système de trajectoires est conçu pour être hautement extensible, permettant l'ajout facile de nouveaux types de trajectoires et de comportements. Cette flexibilité permet des mises à jour régulières avec de nouvelles capacités et mécaniques.

## Conclusion

Le système de combat basé sur les trajectoires est au cœur de l'expérience de jeu de Nightfall Defenders. Sa combinaison de trajectoires basées sur la physique et de motifs prédéterminés offre un gameplay riche et varié qui récompense la maîtrise et l'expérimentation.

En permettant l'évolution des capacités via la spécialisation, la fusion et l'harmonisation, le système offre une profondeur stratégique significative et une rejouabilité élevée, tout en maintenant une courbe d'apprentissage accessible pour les nouveaux joueurs. 