# Système de Cycle Jour/Nuit

Le cycle jour/nuit est l'un des systèmes fondamentaux de Nightfall Defenders, structurant le gameplay en deux phases distinctes et créant un rythme unique.

## Vue d'Ensemble

Le cycle jour/nuit divise le gameplay en deux phases avec des mécaniques et des objectifs différents :

1. **Phase Diurne** : Exploration, collecte de ressources, développement de la ville
2. **Phase Nocturne** : Défense de la ville contre des hordes de monstres

Cette alternance crée une boucle de jeu dynamique et offre différents styles de jeu.

## Implémentation Technique

### Classe Principale

```python
class DayNightCycle:
    def __init__(self, game, day_length_minutes=15, night_length_minutes=5):
        self.game = game
        self.day_length = day_length_minutes * 60  # En secondes
        self.night_length = night_length_minutes * 60  # En secondes
        self.cycle_length = self.day_length + self.night_length
        
        self.time = 0  # Temps écoulé en secondes
        self.cycle_count = 0  # Nombre de cycles complets
        
        self.is_night_active = False
        self.dawn_time = 0  # Heure du lever du soleil
        self.dusk_time = self.day_length  # Heure du coucher du soleil
        
        # Enregistrer les callbacks pour les transitions
        self.transition_callbacks = {
            "dawn": [],  # Début du jour
            "day": [],   # Milieu du jour
            "dusk": [],  # Début de la nuit
            "night": []  # Milieu de la nuit
        }
        
        # Paramètres visuels
        self.sky_colors = {
            "dawn": (0.8, 0.6, 0.5, 1.0),
            "day": (0.5, 0.7, 1.0, 1.0),
            "dusk": (0.9, 0.5, 0.3, 1.0),
            "night": (0.1, 0.1, 0.2, 1.0)
        }
        
        # Système de météo intégré
        self.weather_system = WeatherSystem(self)
        
        # Initialiser l'UI
        self._setup_ui()
    
    def update(self, dt):
        """Mettre à jour le cycle jour/nuit"""
        old_time = self.time
        old_is_night = self.is_night()
        
        # Progresser le temps
        self.time += dt
        
        # Gérer le passage à un nouveau cycle
        if self.time >= self.cycle_length:
            self.time %= self.cycle_length
            self.cycle_count += 1
            
            # Déclencher des événements liés à la progression des jours
            self.game.event_manager.trigger_event("new_day", {"day": self.cycle_count})
        
        # Vérifier les transitions jour/nuit
        current_is_night = self.is_night()
        if old_is_night != current_is_night:
            if current_is_night:
                self._trigger_night_phase()
            else:
                self._trigger_day_phase()
        
        # Vérifier d'autres moments clés du cycle
        self._check_time_triggers(old_time)
        
        # Mettre à jour les effets visuels
        self._update_visual_effects()
        
        # Mettre à jour la météo
        self.weather_system.update(dt)
        
        # Mettre à jour l'interface utilisateur
        self._update_ui()
    
    def is_night(self):
        """Vérifier si c'est actuellement la nuit"""
        return self.time >= self.day_length
    
    def get_normalized_time(self):
        """Obtenir l'heure normalisée (0.0 à 1.0 pour un cycle complet)"""
        return self.time / self.cycle_length
    
    def get_day_phase(self):
        """Obtenir la phase actuelle du jour"""
        norm_time = self.get_normalized_time() * self.cycle_length
        
        # Dawn: première heure du jour
        dawn_duration = self.day_length * 0.1
        if norm_time < dawn_duration:
            return "dawn", norm_time / dawn_duration
        
        # Day: milieu de journée
        day_duration = self.day_length * 0.8
        if norm_time < dawn_duration + day_duration:
            return "day", (norm_time - dawn_duration) / day_duration
        
        # Dusk: dernière heure du jour
        dusk_duration = self.day_length * 0.1
        if norm_time < self.day_length:
            return "dusk", (norm_time - (dawn_duration + day_duration)) / dusk_duration
        
        # Night: phase nocturne
        night_progress = (norm_time - self.day_length) / self.night_length
        return "night", night_progress
    
    def get_light_intensity(self):
        """Obtenir l'intensité de la lumière basée sur l'heure du jour"""
        phase, progress = self.get_day_phase()
        
        if phase == "dawn":
            # Augmentation progressive de la lumière
            return 0.2 + progress * 0.8
        elif phase == "day":
            # Lumière maximale
            return 1.0
        elif phase == "dusk":
            # Diminution progressive de la lumière
            return 1.0 - progress * 0.8
        else:  # night
            # Lumière minimale
            return 0.2
    
    def get_sky_color(self):
        """Obtenir la couleur du ciel basée sur l'heure du jour"""
        phase, progress = self.get_day_phase()
        
        # Phase de transition : interpoler entre deux couleurs
        if phase == "dawn":
            return self._lerp_color(self.sky_colors["night"], self.sky_colors["day"], progress)
        elif phase == "day":
            return self.sky_colors["day"]
        elif phase == "dusk":
            return self._lerp_color(self.sky_colors["day"], self.sky_colors["night"], progress)
        else:  # night
            return self.sky_colors["night"]
    
    def register_callback(self, event, callback):
        """Enregistrer un callback pour un événement du cycle"""
        if event in self.transition_callbacks:
            self.transition_callbacks[event].append(callback)
    
    def _trigger_day_phase(self):
        """Déclencher les effets de la phase diurne"""
        self.is_night_active = False
        
        # Arrêter les spawns nocturnes
        self.game.enemy_manager.stop_night_spawning()
        
        # Désactiver le brouillard nocturne
        if hasattr(self.game, 'night_fog'):
            self.game.night_fog.deactivate()
        
        # Restaurer les ressources de la ville
        self.game.city_manager.restore_daily_resources()
        
        # Déclencher la récompense de survie si la ville a survécu
        if self.game.city_manager.has_survived_night():
            self.game.reward_manager.give_night_survival_reward()
        
        # Restaurer l'équipement perdu en cas de résurrection
        self.game.player.restore_lost_equipment()
        
        # Actualiser les nœuds de ressources du monde
        self.game.world.refresh_resource_nodes()
        
        # Déclencher les callbacks enregistrés
        self._trigger_callbacks("dawn")
    
    def _trigger_night_phase(self):
        """Déclencher les effets de la phase nocturne"""
        self.is_night_active = True
        
        # Activer le brouillard nocturne
        if hasattr(self.game, 'night_fog'):
            self.game.night_fog.activate()
        
        # Déclencher l'apparition des ennemis nocturnes
        self.game.enemy_manager.start_night_spawning()
        
        # Préparer les défenses de la ville
        self.game.city_manager.activate_night_defenses()
        
        # Réinitialiser le compteur de résurrection du joueur
        self.game.player.reset_resurrection_count()
        
        # Si c'est une nuit de boss (tous les 7 jours), déclencher l'événement
        if self.cycle_count > 0 and self.cycle_count % 7 == 0:
            self.game.boss_manager.trigger_boss_night()
        
        # Déclencher les callbacks enregistrés
        self._trigger_callbacks("dusk")
    
    def _check_time_triggers(self, old_time):
        """Vérifier et déclencher les événements basés sur le temps"""
        # Milieu de journée
        mid_day = self.day_length * 0.5
        if old_time < mid_day <= self.time:
            self._trigger_callbacks("day")
        
        # Milieu de nuit
        mid_night = self.day_length + (self.night_length * 0.5)
        if old_time < mid_night <= self.time:
            self._trigger_callbacks("night")
    
    def _trigger_callbacks(self, event):
        """Déclencher tous les callbacks pour un événement spécifique"""
        for callback in self.transition_callbacks[event]:
            callback()
    
    def _lerp_color(self, color1, color2, t):
        """Interpoler entre deux couleurs"""
        return tuple(a + (b - a) * t for a, b in zip(color1, color2))
    
    def _setup_ui(self):
        """Configurer l'interface utilisateur pour le cycle jour/nuit"""
        # Créer l'indicateur de cycle jour/nuit et l'horloge
        self.ui_clock = ClockInterface(self)
        self.ui_cycle_indicator = CycleIndicator(self)
        
        # Ajouter à l'interface du jeu
        self.game.ui_manager.add_element(self.ui_clock)
        self.game.ui_manager.add_element(self.ui_cycle_indicator)
    
    def _update_ui(self):
        """Mettre à jour l'interface utilisateur du cycle jour/nuit"""
        if self.ui_clock:
            self.ui_clock.update()
        
        if self.ui_cycle_indicator:
            self.ui_cycle_indicator.update()
    
    def _update_visual_effects(self):
        """Mettre à jour les effets visuels liés au cycle jour/nuit"""
        # Mettre à jour la couleur du ciel
        sky_color = self.get_sky_color()
        self.game.renderer.set_sky_color(sky_color)
        
        # Mettre à jour l'intensité lumineuse globale
        light_intensity = self.get_light_intensity()
        self.game.renderer.set_ambient_light(light_intensity)
        
        # Mettre à jour les ombres
        shadow_length = 1.0
        if self.get_day_phase()[0] in ["dawn", "dusk"]:
            # Ombres plus longues à l'aube et au crépuscule
            shadow_length = 2.0
        
        shadow_direction = Vec3(-1, -1, -1)  # Direction par défaut
        if self.get_day_phase()[0] == "dawn":
            shadow_direction = Vec3(-1, 1, -1)  # Ombres du matin (est)
        elif self.get_day_phase()[0] == "dusk":
            shadow_direction = Vec3(1, -1, -1)  # Ombres du soir (ouest)
        
        self.game.renderer.set_shadow_params(shadow_direction, shadow_length)
```

### Système de Météo Intégré

Le cycle jour/nuit intègre un système de météo qui affecte le gameplay :

```python
class WeatherSystem:
    def __init__(self, day_night_cycle):
        self.day_night_cycle = day_night_cycle
        self.game = day_night_cycle.game
        
        self.current_weather = "clear"
        self.weather_intensity = 0.0  # 0.0 à 1.0
        self.target_intensity = 0.0
        self.transition_speed = 0.2  # Vitesse de transition
        
        self.weather_duration = 0.0  # Durée restante
        self.weather_change_cooldown = 0.0  # Cooldown avant changement
        
        self.weather_types = {
            "clear": {
                "particle_system": None,
                "sound": "ambient/clear.ogg",
                "light_modifier": 0.0,
                "movement_modifier": 0.0,
                "resource_modifier": 0.0
            },
            "rain": {
                "particle_system": "effects/rain",
                "sound": "ambient/rain.ogg",
                "light_modifier": -0.2,  # Plus sombre
                "movement_modifier": -0.1,  # Plus lent
                "resource_modifier": 0.2  # Plus de ressources
            },
            "fog": {
                "particle_system": "effects/fog",
                "sound": "ambient/fog.ogg",
                "light_modifier": -0.1,
                "movement_modifier": -0.05,
                "resource_modifier": 0.0
            },
            "storm": {
                "particle_system": "effects/storm",
                "sound": "ambient/storm.ogg",
                "light_modifier": -0.3,
                "movement_modifier": -0.2,
                "resource_modifier": -0.1
            }
        }
        
        # Système de particules actif
        self.active_particle_system = None
        
        # Son ambiant actif
        self.ambient_sound = None
    
    def update(self, dt):
        """Mettre à jour le système de météo"""
        # Gérer les changements de météo
        if self.weather_duration > 0:
            self.weather_duration -= dt
        else:
            # La météo actuelle est terminée
            if self.weather_change_cooldown > 0:
                self.weather_change_cooldown -= dt
            else:
                # Possibilité de changer de météo
                self._consider_weather_change()
        
        # Gérer les transitions d'intensité
        self._update_intensity(dt)
        
        # Mettre à jour les effets visuels et sonores
        self._update_effects()
    
    def _consider_weather_change(self):
        """Considérer un changement de météo en fonction des probabilités"""
        # Pas de changement pendant la nuit pour certains types de météo
        if self.day_night_cycle.is_night() and self.current_weather != "clear":
            return
        
        # Probabilités de base pour chaque type de météo
        probabilities = {
            "clear": 0.6,
            "rain": 0.2,
            "fog": 0.15,
            "storm": 0.05
        }
        
        # Ajustements saisonniers (si implémentés)
        if hasattr(self.game, 'season_system'):
            season = self.game.season_system.current_season
            if season == "spring":
                probabilities["rain"] += 0.1
            elif season == "autumn":
                probabilities["fog"] += 0.1
            elif season == "winter":
                probabilities["storm"] += 0.05
        
        # Sélectionner un nouveau type de météo
        weather_types = list(probabilities.keys())
        weights = [probabilities[w] for w in weather_types]
        
        new_weather = random.choices(weather_types, weights=weights)[0]
        
        # Éviter de choisir la même météo
        if new_weather == self.current_weather:
            return
        
        # Définir la nouvelle météo
        self.set_weather(new_weather)
    
    def set_weather(self, weather_type, duration=None, intensity=None):
        """Définir la météo actuelle"""
        if weather_type not in self.weather_types:
            return False
        
        self.current_weather = weather_type
        
        # Définir la durée (par défaut: 3-10 minutes)
        if duration is None:
            if weather_type == "storm":
                duration = random.uniform(120, 300)  # 2-5 minutes
            else:
                duration = random.uniform(180, 600)  # 3-10 minutes
        
        self.weather_duration = duration
        
        # Définir l'intensité cible (par défaut: 0.5-1.0)
        if intensity is None:
            intensity = random.uniform(0.5, 1.0)
        
        self.target_intensity = intensity
        
        # Réinitialiser le cooldown pour le prochain changement
        self.weather_change_cooldown = random.uniform(60, 180)  # 1-3 minutes
        
        # Déclencher les effets de la météo
        self._activate_weather_effects()
        
        return True
    
    def _update_intensity(self, dt):
        """Mettre à jour l'intensité de la météo actuelle"""
        if self.weather_intensity < self.target_intensity:
            self.weather_intensity = min(
                self.weather_intensity + self.transition_speed * dt,
                self.target_intensity
            )
        elif self.weather_intensity > self.target_intensity:
            self.weather_intensity = max(
                self.weather_intensity - self.transition_speed * dt,
                self.target_intensity
            )
    
    def _activate_weather_effects(self):
        """Activer les effets pour la météo actuelle"""
        # Arrêter les effets précédents
        if self.active_particle_system:
            self.game.particle_manager.stop_system(self.active_particle_system)
            self.active_particle_system = None
        
        if self.ambient_sound:
            self.game.audio_manager.stop_sound(self.ambient_sound)
            self.ambient_sound = None
        
        # Activer le nouveau système de particules si nécessaire
        particle_system = self.weather_types[self.current_weather]["particle_system"]
        if particle_system:
            self.active_particle_system = self.game.particle_manager.start_system(
                particle_system,
                position=None,  # Global
                follow_camera=True
            )
        
        # Jouer le nouveau son ambiant
        sound = self.weather_types[self.current_weather]["sound"]
        if sound:
            self.ambient_sound = self.game.audio_manager.play_sound(
                sound,
                loop=True,
                volume=0.0  # Commencer silencieux, fade in progressif
            )
    
    def _update_effects(self):
        """Mettre à jour les effets visuels et sonores basés sur l'intensité"""
        # Mettre à jour le volume du son
        if self.ambient_sound:
            self.game.audio_manager.set_sound_volume(
                self.ambient_sound,
                self.weather_intensity * 0.8
            )
        
        # Mettre à jour l'intensité du système de particules
        if self.active_particle_system:
            self.game.particle_manager.set_system_intensity(
                self.active_particle_system,
                self.weather_intensity
            )
        
        # Appliquer les modificateurs d'éclairage
        light_mod = self.weather_types[self.current_weather]["light_modifier"]
        if light_mod != 0:
            adjusted_light = light_mod * self.weather_intensity
            base_light = self.day_night_cycle.get_light_intensity()
            self.game.renderer.set_ambient_light(base_light + adjusted_light)
        
        # Appliquer les modificateurs de mouvement au joueur
        movement_mod = self.weather_types[self.current_weather]["movement_modifier"]
        if movement_mod != 0:
            adjusted_movement = 1.0 + (movement_mod * self.weather_intensity)
            self.game.player.set_movement_multiplier(adjusted_movement)
```

## Interface Utilisateur du Cycle

Le cycle jour/nuit dispose d'éléments d'interface dédiés :

```python
class ClockInterface:
    def __init__(self, day_night_cycle):
        self.day_night_cycle = day_night_cycle
        self.game = day_night_cycle.game
        
        # Charger les ressources graphiques
        self.clock_bg = self.game.resource_manager.get_texture("ui/clock_bg.png")
        self.clock_hand = self.game.resource_manager.get_texture("ui/clock_hand.png")
        self.sun_icon = self.game.resource_manager.get_texture("ui/sun_icon.png")
        self.moon_icon = self.game.resource_manager.get_texture("ui/moon_icon.png")
        
        # Configurer l'élément d'interface
        self.position = Vec2(50, 50)  # Position à l'écran
        self.size = Vec2(100, 100)  # Taille
        
        # Créer le nœud d'interface
        self.ui_node = self.game.ui_manager.create_ui_node("clock")
        
        # Ajouter les éléments graphiques
        self._setup_graphics()
    
    def update(self):
        """Mettre à jour l'affichage de l'horloge"""
        # Calculer la rotation de l'aiguille (0 à 360 degrés)
        time_progress = self.day_night_cycle.get_normalized_time()
        rotation = time_progress * 360.0
        
        # Appliquer la rotation à l'aiguille
        self.hand_node.setH(rotation)
        
        # Mettre à jour l'icône (soleil/lune)
        is_night = self.day_night_cycle.is_night()
        self.sun_node.setVisible(not is_night)
        self.moon_node.setVisible(is_night)
        
        # Mettre à jour le texte du jour
        day_count = self.day_night_cycle.cycle_count + 1
        self.day_text_node.setText(f"Jour {day_count}")
    
    def _setup_graphics(self):
        """Configurer les éléments graphiques de l'horloge"""
        # Fond de l'horloge
        self.bg_node = self.ui_node.attachNewNode("clock_bg")
        # ... configuration du fond
        
        # Aiguille de l'horloge
        self.hand_node = self.ui_node.attachNewNode("clock_hand")
        # ... configuration de l'aiguille
        
        # Icônes du soleil et de la lune
        self.sun_node = self.ui_node.attachNewNode("sun_icon")
        self.moon_node = self.ui_node.attachNewNode("moon_icon")
        # ... configuration des icônes
        
        # Texte du jour
        self.day_text_node = TextNode("day_text")
        day_count = self.day_night_cycle.cycle_count + 1
        self.day_text_node.setText(f"Jour {day_count}")
        # ... configuration du texte
```

## Effets sur le Gameplay

### Phases Diurnes

Pendant le jour, les joueurs peuvent :

- Explorer le monde ouvert en toute sécurité avec une excellente visibilité
- Collecter des ressources des nœuds qui se régénèrent chaque jour
- Développer et améliorer leur ville centrale
- Interagir avec les PNJ et les marchands
- Effectuer des quêtes secondaires

Les mécaniques de jour favorisent l'exploration et la préparation.

### Phases Nocturnes

Pendant la nuit, les joueurs doivent :

- Défendre leur ville contre des vagues d'ennemis émergeant du brouillard
- Utiliser les défenses de la ville, telles que des tourelles et des pièges
- Combattre les ennemis directement avec leurs capacités
- Gérer leurs ressources (santé, mana) avec une capacité de régénération limitée
- Faire face à des boss qui apparaissent toutes les 7 nuits

Les mécaniques de nuit favorisent le combat et la survie.

### Transitions Jour/Nuit

Les transitions entre le jour et la nuit sont cruciales :

- **Transition Jour → Nuit (Crépuscule)** :
  - Avertissement visuel et sonore 2 minutes avant
  - Les PNJ commencent à rentrer dans leurs maisons
  - Activation des défenses automatiques de la ville
  - Apparition du brouillard nocturne aux bords de la carte

- **Transition Nuit → Jour (Aube)** :
  - Le brouillard nocturne se dissipe progressivement
  - Les ennemis restants se replient
  - Les ressources de la ville se régénèrent
  - Les récompenses de survie nocturne sont accordées

## Avantages pour l'Expérience de Jeu

Le cycle jour/nuit offre plusieurs avantages :

1. **Variété de Gameplay** : Alterne entre exploration et combat
2. **Tension et Relâchement** : Crée un rythme naturel d'action et de repos
3. **Choix Stratégiques** : Les joueurs doivent décider comment utiliser le temps limité du jour
4. **Progression Visible** : Le nombre de jours survécus est un indicateur clair de progression
5. **Structure Narrative** : Facilite le déploiement d'événements scénarisés à des moments spécifiques

## Interaction avec d'Autres Systèmes

### Brouillard Nocturne

Le brouillard nocturne est intimement lié au cycle jour/nuit :

- Apparaît progressivement au crépuscule
- Sert de milieu d'apparition pour les ennemis
- Augmente en densité et en danger à mesure que la nuit avance
- Recule à l'aube quelle que soit l'issue de la bataille

### Système Psychologique des Ennemis

Les ennemis se comportent différemment selon l'heure :

- Plus agressifs et puissants dans le brouillard nocturne
- Certains types d'ennemis n'apparaissent que la nuit
- Les ennemis diurnes peuvent devenir plus puissants la nuit
- Les ennemis sont plus susceptibles de battre en retraite à l'approche de l'aube

### Système de Ressources

La génération et la collecte de ressources sont affectées par le cycle :

- Certaines ressources rares n'apparaissent qu'à des moments spécifiques
- Les ressources se régénèrent au début de chaque journée
- Les bâtiments de production fonctionnent principalement le jour
- Certaines ressources spéciales n'apparaissent qu'avec certaines conditions météorologiques

## Conclusion

Le système de cycle jour/nuit est l'épine dorsale du gameplay de Nightfall Defenders, créant une expérience rythmée avec des objectifs et des défis clairs. L'alternance entre l'exploration diurne et la défense nocturne offre une variété de gameplay qui maintient l'engagement des joueurs sur le long terme. 