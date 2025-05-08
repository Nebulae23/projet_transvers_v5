# Architecture Technique de Nightfall Defenders

Ce document décrit l'architecture technique, les technologies et les implémentations spécifiques utilisées dans Nightfall Defenders.

## Vue d'Ensemble

Nightfall Defenders est développé en Python, utilisant un moteur de jeu personnalisé construit sur Panda3D avec des extensions PyOpenGL pour les rendus avancés et NumPy pour les calculs mathématiques et physiques.

## Stack Technologique

### Langages et Bibliothèques

| Technologie | Utilisation |
|-------------|-------------|
| Python 3.8+ | Langage principal du projet |
| PyOpenGL | Interface graphique de bas niveau |
| Panda3D | Framework de base pour la gestion de scène |
| NumPy | Calculs mathématiques et simulation physique |
| SQLite | Stockage de données persistantes |

### Outils de Développement

| Outil | Objectif |
|-------|----------|
| Git | Gestion de version |
| GitHub Actions | CI/CD, tests automatisés |
| VS Code / PyCharm | Éditeurs recommandés |
| Black | Formatage de code |
| MyPy | Vérification statique des types |
| Pytest | Tests unitaires et d'intégration |

## Architecture du Moteur

Le moteur de jeu personnalisé est construit sur une architecture modulaire qui sépare le rendu, la physique, le gameplay et l'interface utilisateur.

### Diagramme de l'Architecture

```
┌────────────────────┐
│     Application    │
└───────┬────────────┘
        │
┌───────▼────────────┐     ┌────────────────────┐
│   Scene Manager    │◄────►   Resource Manager │
└───────┬────────────┘     └────────────────────┘
        │
┌───────▼────────────┐     ┌────────────────────┐
│  Physics Engine    │◄────►   Event System     │
└───────┬────────────┘     └────────────────────┘
        │
┌───────▼────────────┐     ┌────────────────────┐
│   Render Engine    │◄────►   Shader Manager   │
└───────┬────────────┘     └────────────────────┘
        │
┌───────▼────────────┐     ┌────────────────────┐
│       GUI          │◄────►   Input Manager    │
└────────────────────┘     └────────────────────┘
```

### Composants Principaux

#### Gestionnaire de Scène (Scene Manager)

Responsable de l'organisation des entités de jeu et de leur mise à jour à chaque frame. Ce composant utilise un graphe de scène où chaque nœud représente une entité ou un groupe d'entités.

```python
class SceneManager:
    def __init__(self):
        self.root_node = NodePath("root")
        self.active_nodes = {}
        self.inactive_nodes = {}
        self.physics_nodes = []
        
    def update(self, dt):
        # Mise à jour de tous les nœuds actifs
        for node_id, node in self.active_nodes.items():
            node.update(dt)
            
        # Mise à jour de la physique
        self.update_physics(dt)
```

#### Moteur Physique (Physics Engine)

Implémente un système de physique personnalisé basé sur l'intégration de Verlet, permettant des animations organiques et des interactions dynamiques.

```python
class PhysicsEngine:
    def __init__(self, gravity=Vec3(0, 0, -9.8)):
        self.gravity = gravity
        self.objects = []
        self.constraints = []
        
    def update(self, dt):
        # Appliquer les forces et mettre à jour les positions
        for obj in self.objects:
            obj.apply_force(self.gravity * obj.mass)
            obj.integrate(dt)
            
        # Appliquer les contraintes
        for constraint in self.constraints:
            constraint.solve()
            
        # Détecter et résoudre les collisions
        self.resolve_collisions()
```

#### Moteur de Rendu (Render Engine)

Gère le rendu graphique, y compris les shaders, les effets de post-traitement et l'optimisation des performances.

```python
class RenderEngine:
    def __init__(self, window_size=(1280, 720), quality="medium"):
        self.window_size = window_size
        self.quality = quality
        self.shader_manager = ShaderManager()
        self.post_processors = []
        self.setup_pipeline()
        
    def render(self, scene, camera):
        # Pré-rendu - mettre à jour les tampons et les ombres
        self.prepare_render()
        
        # Rendu principal - dessiner géométrie et appliquer les shaders
        self.render_scene(scene, camera)
        
        # Post-traitement
        for processor in self.post_processors:
            processor.process()
            
        # Présenter à l'écran
        self.present()
```

#### Système d'Événements (Event System)

Implémente un modèle d'observateur pour la communication entre composants, permettant un couplage faible et une extensibilité.

```python
class EventSystem:
    def __init__(self):
        self.listeners = defaultdict(list)
        
    def subscribe(self, event_type, callback):
        self.listeners[event_type].append(callback)
        
    def unsubscribe(self, event_type, callback):
        if event_type in self.listeners:
            self.listeners[event_type].remove(callback)
            
    def emit(self, event_type, *args, **kwargs):
        for callback in self.listeners[event_type]:
            callback(*args, **kwargs)
```

## Système de Physique et Animation Organique

Un aspect clé de Nightfall Defenders est son système d'animation organique, basé sur l'intégration de Verlet et inspiré par des jeux comme Rain World.

### Intégration de Verlet

L'intégration de Verlet est une méthode de deuxième ordre pour l'intégration numérique des équations du mouvement. Contrairement à l'intégration d'Euler, elle stocke les positions précédentes au lieu des vitesses :

```python
class VerletObject:
    def __init__(self, position, mass=1.0):
        self.position = position
        self.old_position = position.copy()  # Position précédente
        self.acceleration = Vec3(0, 0, 0)
        self.mass = mass
        
    def update(self, dt):
        # Sauvegarder la position actuelle
        current = self.position.copy()
        
        # Calculer la vitesse implicite
        velocity = self.position - self.old_position
        
        # Mise à jour de la position : position + vitesse + accélération*dt²
        self.position = self.position + velocity + self.acceleration * dt * dt
        
        # Mettre à jour la position précédente
        self.old_position = current
        
        # Réinitialiser l'accélération
        self.acceleration = Vec3(0, 0, 0)
        
    def apply_force(self, force):
        self.acceleration += force / self.mass
```

### Système de Contraintes

Des contraintes sont utilisées pour connecter des objets Verlet ensemble, créant des structures comme des chaînes, des tissus, et des corps articulés :

```python
class DistanceConstraint:
    def __init__(self, object_a, object_b, rest_length, stiffness=0.8):
        self.object_a = object_a
        self.object_b = object_b
        self.rest_length = rest_length
        self.stiffness = stiffness
        
    def solve(self):
        # Calculer le vecteur entre les objets
        delta = self.object_b.position - self.object_a.position
        current_length = delta.length()
        
        if current_length == 0:
            # Éviter la division par zéro
            return
            
        # Calculer la différence entre la longueur actuelle et la longueur au repos
        difference = (current_length - self.rest_length) / current_length
        
        # Appliquer la correction à chaque objet
        if not self.object_a.is_fixed:
            self.object_a.position += delta * difference * 0.5 * self.stiffness
            
        if not self.object_b.is_fixed:
            self.object_b.position -= delta * difference * 0.5 * self.stiffness
```

### Animation Organique

Pour créer des animations organiques, nous utilisons une combinaison d'objets Verlet et de contraintes :

```python
class OrganicCreature:
    def __init__(self, start_position):
        self.points = []
        self.constraints = []
        
        # Créer les points du corps
        for i in range(10):
            pos = start_position + Vec3(i * 0.5, 0, 0)
            point = VerletObject(pos)
            self.points.append(point)
            
            # Connecter les points consécutifs
            if i > 0:
                constraint = DistanceConstraint(self.points[i-1], point, 0.5)
                self.constraints.append(constraint)
                
        # Créer des contraintes supplémentaires pour la rigidité
        for i in range(len(self.points) - 2):
            constraint = DistanceConstraint(self.points[i], self.points[i+2], 1.0, stiffness=0.6)
            self.constraints.append(constraint)
            
    def update(self, dt):
        # Appliquer les forces externes
        for point in self.points:
            point.update(dt)
            
        # Résoudre les contraintes plusieurs fois pour plus de stabilité
        for _ in range(5):
            for constraint in self.constraints:
                constraint.solve()
```

## Système de Trajectoires

Le système de trajectoires est fondamental pour le gameplay basé sur les projectiles :

```python
class TrajectorySystem:
    def __init__(self, physics_engine):
        self.physics_engine = physics_engine
        self.trajectories = {}
        
    def calculate_trajectory(self, start_pos, velocity, gravity, time_steps=20, dt=0.1):
        # Crée une simulation temporaire pour prédire la trajectoire
        positions = [start_pos]
        pos = start_pos.copy()
        vel = velocity.copy()
        
        for _ in range(time_steps):
            # Appliquer la gravité
            vel += gravity * dt
            
            # Mettre à jour la position
            pos += vel * dt
            
            # Vérifier les collisions
            collision = self.physics_engine.check_ray_collision(positions[-1], pos)
            if collision:
                positions.append(collision.hit_point)
                break
                
            positions.append(pos.copy())
            
        return positions
    
    def create_projectile(self, start_pos, velocity, type="standard"):
        # Crée un projectile réel basé sur les paramètres
        projectile = Projectile(start_pos, velocity, type)
        trajectory_id = id(projectile)
        self.trajectories[trajectory_id] = projectile
        return trajectory_id
    
    def update(self, dt):
        # Mettre à jour tous les projectiles actifs
        for trajectory_id, projectile in list(self.trajectories.items()):
            projectile.update(dt)
            
            # Vérifier les collisions
            if projectile.check_collisions(self.physics_engine):
                projectile.on_collision()
                
            # Supprimer les projectiles expirés
            if projectile.is_expired():
                del self.trajectories[trajectory_id]
```

## Système de Shaders

Un système de shader avancé permet des effets visuels complexes :

```python
class ShaderSystem:
    def __init__(self):
        self.shaders = {}
        self.load_default_shaders()
        
    def load_default_shaders(self):
        # Charger les shaders de base
        self.load_shader("default", "shaders/default.vert", "shaders/default.frag")
        self.load_shader("water", "shaders/water.vert", "shaders/water.frag")
        self.load_shader("bloom", "shaders/post/bloom.vert", "shaders/post/bloom.frag")
        
    def load_shader(self, name, vertex_path, fragment_path):
        # Charger et compiler un shader
        with open(vertex_path, 'r') as f:
            vertex_code = f.read()
            
        with open(fragment_path, 'r') as f:
            fragment_code = f.read()
            
        # Créer le programme shader
        shader = self.compile_shader(vertex_code, fragment_code)
        self.shaders[name] = shader
        
    def compile_shader(self, vertex_code, fragment_code):
        # Compiler les shaders et créer un programme
        vertex_shader = GL.glCreateShader(GL.GL_VERTEX_SHADER)
        GL.glShaderSource(vertex_shader, vertex_code)
        GL.glCompileShader(vertex_shader)
        
        fragment_shader = GL.glCreateShader(GL.GL_FRAGMENT_SHADER)
        GL.glShaderSource(fragment_shader, fragment_code)
        GL.glCompileShader(fragment_shader)
        
        program = GL.glCreateProgram()
        GL.glAttachShader(program, vertex_shader)
        GL.glAttachShader(program, fragment_shader)
        GL.glLinkProgram(program)
        
        # Vérifier les erreurs...
        
        return program
    
    def use_shader(self, name):
        if name in self.shaders:
            GL.glUseProgram(self.shaders[name])
    
    def set_uniform(self, name, uniform_name, value):
        if name in self.shaders:
            program = self.shaders[name]
            location = GL.glGetUniformLocation(program, uniform_name)
            
            # Définir la valeur uniforme en fonction du type
            if isinstance(value, int):
                GL.glUniform1i(location, value)
            elif isinstance(value, float):
                GL.glUniform1f(location, value)
            elif isinstance(value, (list, tuple)) and len(value) == 3:
                GL.glUniform3f(location, *value)
            elif isinstance(value, (list, tuple)) and len(value) == 4:
                GL.glUniform4f(location, *value)
            # Plus de types...
```

## Système de Cycle Jour/Nuit

Le cycle jour/nuit est un élément central du gameplay :

```python
class DayNightCycle:
    def __init__(self, day_length_minutes=15, night_length_minutes=5):
        self.day_length = day_length_minutes * 60  # En secondes
        self.night_length = night_length_minutes * 60  # En secondes
        self.cycle_length = self.day_length + self.night_length
        
        self.time = 0  # Temps écoulé en secondes
        self.callbacks = {
            "dawn": [],
            "day": [],
            "dusk": [],
            "night": []
        }
        
    def update(self, dt):
        old_time = self.time
        
        # Mettre à jour le temps
        self.time = (self.time + dt) % self.cycle_length
        
        # Vérifier les transitions
        if old_time < self.day_length and self.time >= self.day_length:
            self._trigger_callbacks("dusk")
            self._trigger_callbacks("night")
        elif old_time > self.day_length and self.time <= self.day_length:
            self._trigger_callbacks("dawn")
            self._trigger_callbacks("day")
            
    def get_time_of_day(self):
        # Retourne une valeur normalisée entre 0 (minuit) et 1 (midi)
        if self.time < self.day_length:
            # Jour
            return 0.5 + (self.time / self.day_length) * 0.5
        else:
            # Nuit
            night_progress = (self.time - self.day_length) / self.night_length
            return night_progress * 0.5
            
    def is_night(self):
        return self.time >= self.day_length
        
    def get_light_intensity(self):
        # Intensité de la lumière basée sur l'heure de la journée
        time_of_day = self.get_time_of_day()
        
        if time_of_day > 0.5:
            # Jour (midi à soir)
            return 1.0 - (time_of_day - 0.5) * 2
        elif time_of_day < 0.05:
            # Nuit profonde
            return 0.2
        else:
            # Matin (minuit à midi)
            return 0.2 + (time_of_day / 0.5) * 0.8
            
    def register_callback(self, event, callback):
        if event in self.callbacks:
            self.callbacks[event].append(callback)
            
    def _trigger_callbacks(self, event):
        for callback in self.callbacks[event]:
            callback()
```

## Optimisations de Performance

Plusieurs stratégies sont utilisées pour maintenir de bonnes performances même avec de nombreuses entités à l'écran.

### Partitionnement Spatial

Nous utilisons un quadtree pour optimiser les requêtes spatiales :

```python
class QuadTree:
    def __init__(self, boundary, capacity=4, max_depth=5, depth=0):
        self.boundary = boundary  # Rectangle délimitant cette région
        self.capacity = capacity  # Nombre max d'objets avant subdivision
        self.max_depth = max_depth  # Profondeur maximale de l'arbre
        self.depth = depth  # Profondeur actuelle
        
        self.objects = []  # Objets dans ce nœud
        self.divided = False  # Si ce nœud est divisé
        self.children = []  # Quadrants enfants
        
    def insert(self, obj):
        # Vérifier si l'objet appartient à ce quadrant
        if not self.boundary.contains_point(obj.position):
            return False
            
        # Si la capacité n'est pas dépassée, ajouter l'objet ici
        if len(self.objects) < self.capacity or self.depth >= self.max_depth:
            self.objects.append(obj)
            return True
            
        # Sinon, subdiviser et insérer dans les enfants
        if not self.divided:
            self.subdivide()
            
        # Tenter d'insérer dans un enfant
        for child in self.children:
            if child.insert(obj):
                return True
                
        # Si nous arrivons ici, insérer dans ce nœud
        self.objects.append(obj)
        return True
        
    def subdivide(self):
        # Créer quatre quadrants enfants
        x, y, w, h = self.boundary.x, self.boundary.y, self.boundary.width / 2, self.boundary.height / 2
        
        nw = Rectangle(x, y + h, w, h)
        ne = Rectangle(x + w, y + h, w, h)
        sw = Rectangle(x, y, w, h)
        se = Rectangle(x + w, y, w, h)
        
        self.children = [
            QuadTree(nw, self.capacity, self.max_depth, self.depth + 1),
            QuadTree(ne, self.capacity, self.max_depth, self.depth + 1),
            QuadTree(sw, self.capacity, self.max_depth, self.depth + 1),
            QuadTree(se, self.capacity, self.max_depth, self.depth + 1)
        ]
        
        self.divided = True
        
    def query(self, range_rect, found=None):
        if found is None:
            found = []
            
        # Si la plage ne chevauche pas ce quadrant, retourner vide
        if not self.boundary.intersects(range_rect):
            return found
            
        # Vérifier les objets dans ce quadrant
        for obj in self.objects:
            if range_rect.contains_point(obj.position):
                found.append(obj)
                
        # Si divisé, vérifier les enfants
        if self.divided:
            for child in self.children:
                child.query(range_rect, found)
                
        return found
```

### Instanciation GPU

Pour les objets répétitifs comme l'herbe et les arbres, nous utilisons l'instanciation GPU :

```python
class InstancedRenderer:
    def __init__(self, model, max_instances=1000):
        self.model = model
        self.max_instances = max_instances
        
        # Créer les tampons d'instance
        self.position_buffer = self.create_instance_buffer(3)  # vec3
        self.rotation_buffer = self.create_instance_buffer(4)  # quaternion
        self.scale_buffer = self.create_instance_buffer(3)  # vec3
        self.color_buffer = self.create_instance_buffer(4)  # vec4
        
        self.instance_count = 0
        self.instances = []
        
    def create_instance_buffer(self, components_per_instance):
        buffer = GL.glGenBuffers(1)
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, buffer)
        GL.glBufferData(GL.GL_ARRAY_BUFFER, 
                        self.max_instances * components_per_instance * 4,  # floats de 4 octets
                        None, GL.GL_DYNAMIC_DRAW)
        return buffer
        
    def add_instance(self, position, rotation, scale, color):
        if self.instance_count >= self.max_instances:
            return False
            
        instance = {
            "position": position,
            "rotation": rotation,
            "scale": scale,
            "color": color
        }
        
        self.instances.append(instance)
        self.instance_count += 1
        return True
        
    def update_buffers(self):
        # Mettre à jour les tampons avec les données d'instance
        
        # Positions
        positions = [v for instance in self.instances for v in instance["position"]]
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.position_buffer)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, len(positions) * 4, positions)
        
        # Rotations
        rotations = [v for instance in self.instances for v in instance["rotation"]]
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.rotation_buffer)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, len(rotations) * 4, rotations)
        
        # Échelles
        scales = [v for instance in self.instances for v in instance["scale"]]
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.scale_buffer)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, len(scales) * 4, scales)
        
        # Couleurs
        colors = [v for instance in self.instances for v in instance["color"]]
        GL.glBindBuffer(GL.GL_ARRAY_BUFFER, self.color_buffer)
        GL.glBufferSubData(GL.GL_ARRAY_BUFFER, 0, len(colors) * 4, colors)
        
    def render(self):
        if self.instance_count == 0:
            return
            
        # Mettre à jour les tampons avant le rendu
        self.update_buffers()
        
        # Configurer les attributs d'instance
        # ...
        
        # Rendre tous les instances en un seul appel de dessin
        GL.glDrawElementsInstanced(
            GL.GL_TRIANGLES, 
            self.model.index_count, 
            GL.GL_UNSIGNED_INT, 
            0, 
            self.instance_count
        )
```

## Gestion de la Mémoire

Nous utilisons un système de pooling d'objets pour réduire les allocations mémoire fréquentes :

```python
class ObjectPool:
    def __init__(self, factory, initial_size=100, grow_size=50):
        self.factory = factory  # Fonction qui crée un nouvel objet
        self.grow_size = grow_size  # Nombre d'objets à ajouter quand le pool est vide
        
        self.active_objects = set()
        self.inactive_objects = []
        
        # Pré-remplir le pool
        self.grow(initial_size)
        
    def grow(self, size):
        for _ in range(size):
            obj = self.factory()
            self.inactive_objects.append(obj)
            
    def get(self):
        if not self.inactive_objects:
            # Pool vide, créer plus d'objets
            self.grow(self.grow_size)
            
        # Obtenir un objet du pool
        obj = self.inactive_objects.pop()
        self.active_objects.add(obj)
        
        # Réinitialiser l'objet à son état par défaut
        if hasattr(obj, "reset"):
            obj.reset()
            
        return obj
        
    def release(self, obj):
        if obj in self.active_objects:
            self.active_objects.remove(obj)
            self.inactive_objects.append(obj)
            
    def clear(self):
        self.active_objects.clear()
        self.inactive_objects.clear()
```

## Multiprocessing

Pour les tâches lourdes comme la génération de terrain et l'IA, nous utilisons du multiprocessing :

```python
class WorkerPool:
    def __init__(self, num_workers=None):
        self.num_workers = num_workers or multiprocessing.cpu_count()
        self.pool = multiprocessing.Pool(self.num_workers)
        self.tasks = {}
        
    def submit_task(self, func, *args, **kwargs):
        # Soumettre une tâche à exécuter en arrière-plan
        task_id = str(uuid.uuid4())
        async_result = self.pool.apply_async(func, args, kwargs)
        self.tasks[task_id] = async_result
        return task_id
        
    def get_result(self, task_id, timeout=None):
        # Obtenir le résultat d'une tâche
        if task_id not in self.tasks:
            return None
            
        async_result = self.tasks[task_id]
        if not async_result.ready() and timeout is None:
            return None
            
        try:
            result = async_result.get(timeout=timeout)
            del self.tasks[task_id]
            return result
        except multiprocessing.TimeoutError:
            return None
        except Exception as e:
            return e
            
    def is_task_done(self, task_id):
        # Vérifier si une tâche est terminée
        if task_id not in self.tasks:
            return True
            
        return self.tasks[task_id].ready()
        
    def shutdown(self):
        # Arrêter le pool de travailleurs
        self.pool.close()
        self.pool.join()
```

## Conclusion

Cette documentation technique offre un aperçu de l'architecture et des implémentations clés de Nightfall Defenders. Pour plus de détails sur des systèmes spécifiques, consultez la documentation correspondante dans le dossier docs/. 