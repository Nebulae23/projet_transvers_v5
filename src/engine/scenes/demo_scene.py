# src/engine/scenes/demo_scene.py

import pygame
import numpy as np
import math
import random
from ..ecs.components import Transform, Sprite, PhysicsBody

class DemoScene:
    def __init__(self, width, height, world):
        self.width = width
        self.height = height
        self.world = world
        
        # Initialize demo entities
        self.player_id = None
        self.player_pos = np.array([width // 2, height // 2], dtype=float)
        self.player_velocity = np.zeros(2, dtype=float)
        self.player_speed = 200.0
        self.player_sprite = None
        
        # Enemy spawning
        self.enemy_ids = []
        self.enemy_spawn_timer = 0
        self.enemy_spawn_interval = 2.0  # Spawn enemy every 2 seconds
        
        # Background elements
        self.stars = []
        self.generate_stars(100)
        
        # UI elements
        self.font = pygame.font.SysFont(None, 36)
        self.small_font = pygame.font.SysFont(None, 24)
        
        # Create demo HUD
        self.hud = DemoHUD(width, height)
        
        # Debug info
        self.debug_info = {
            'fps': 0,
            'entities': 0,
            'player_pos': self.player_pos.copy()
        }
        
        # Audio (placeholder)
        self.music_playing = False
        
        # Load assets
        self.assets = {
            'player': None,
            'enemy': None,
            'background': None
        }
        self.load_assets()
        
    def load_assets(self):
        """Load scene assets"""
        try:
            # Load player sprite
            try:
                self.assets['player'] = pygame.image.load("assets/sprites/player.png").convert_alpha()
                self.assets['player'] = pygame.transform.scale(self.assets['player'], (48, 48))
            except Exception as e:
                print(f"Could not load player sprite: {e}")
                # Create a simple player sprite
                player_surface = pygame.Surface((48, 48), pygame.SRCALPHA)
                pygame.draw.circle(player_surface, (0, 255, 100), (24, 24), 20)
                pygame.draw.circle(player_surface, (0, 200, 80), (24, 24), 16)
                pygame.draw.circle(player_surface, (255, 255, 255), (18, 18), 5)
                self.assets['player'] = player_surface
            
            # Load enemy sprite
            try:
                self.assets['enemy'] = pygame.image.load("assets/sprites/enemy.png").convert_alpha()
                self.assets['enemy'] = pygame.transform.scale(self.assets['enemy'], (32, 32))
            except Exception as e:
                print(f"Could not load enemy sprite: {e}")
                # Create a simple enemy sprite
                enemy_surface = pygame.Surface((32, 32), pygame.SRCALPHA)
                pygame.draw.circle(enemy_surface, (255, 50, 50), (16, 16), 14)
                pygame.draw.circle(enemy_surface, (200, 0, 0), (16, 16), 10)
                pygame.draw.circle(enemy_surface, (255, 255, 0), (13, 13), 3)
                self.assets['enemy'] = enemy_surface
            
            # Load background
            try:
                self.assets['background'] = pygame.image.load("assets/backgrounds/demo_bg.png").convert_alpha()
                self.assets['background'] = pygame.transform.scale(self.assets['background'], (self.width, self.height))
            except Exception as e:
                print(f"Could not load background: {e}")
                # Create a gradient background
                bg_surface = pygame.Surface((self.width, self.height))
                for y in range(0, self.height):
                    color_val = max(0, min(255, int(20 + (y / self.height) * 40)))
                    color = (color_val // 4, color_val // 3, color_val)
                    pygame.draw.line(bg_surface, color, (0, y), (self.width, y))
                self.assets['background'] = bg_surface
        except Exception as e:
            print(f"Error in asset loading: {e}")
            
    def generate_stars(self, count):
        """Generate star positions for background"""
        self.stars = []
        for _ in range(count):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 3)
            brightness = random.randint(150, 255)
            speed = random.uniform(5, 20)
            self.stars.append({
                'pos': np.array([x, y], dtype=float),
                'size': size,
                'color': (brightness, brightness, brightness),
                'speed': speed
            })
        
    def enter(self):
        """Called when scene becomes active"""
        print("Entering Demo Scene")
        self._setup_entities()
        
        # Try to start music
        try:
            pygame.mixer.music.load("assets/music/demo_music.mp3")
            pygame.mixer.music.play(-1)  # Loop indefinitely
            self.music_playing = True
        except:
            print("Music file not found or audio error")
        
    def exit(self):
        """Called when scene is no longer active"""
        print("Exiting Demo Scene")
        if self.music_playing:
            pygame.mixer.music.stop()
        
    def reset(self):
        """Reset the scene to its initial state"""
        print("Resetting Demo Scene")
        self._setup_entities()
        
    def _setup_entities(self):
        """Setup demo entities"""
        print("Setting up demo entities")
        try:
            # Create player entity
            player_entity = self.world.create_entity()
            self.player_id = player_entity.id
            
            # Center the player
            self.player_pos = np.array([self.width // 2, self.height // 2], dtype=float)
            
            # Add components to player entity
            player_entity.add_component(Transform(position=self.player_pos.copy()))
            player_entity.add_component(Sprite(texture_path="assets/sprites/player.png"))
            player_entity.add_component(PhysicsBody(mass=10.0))
            
            print(f"Created player entity with ID: {self.player_id}")
            
            # Clear existing enemies
            self.enemy_ids = []
            
        except Exception as e:
            print(f"Error setting up demo entities: {e}")
            
    def spawn_enemy(self):
        """Spawn a new enemy at a random position"""
        try:
            # Create position on edge of screen
            side = random.randint(0, 3)
            pos = np.zeros(2, dtype=float)
            if side == 0:  # Top
                pos[0] = random.randint(0, self.width)
                pos[1] = 0
            elif side == 1:  # Right
                pos[0] = self.width
                pos[1] = random.randint(0, self.height)
            elif side == 2:  # Bottom
                pos[0] = random.randint(0, self.width)
                pos[1] = self.height
            else:  # Left
                pos[0] = 0
                pos[1] = random.randint(0, self.height)
                
            # Create enemy entity
            enemy_entity = self.world.create_entity()
            enemy_id = enemy_entity.id
            
            # Add components
            enemy_entity.add_component(Transform(position=pos.copy()))
            enemy_entity.add_component(Sprite(texture_path="assets/sprites/enemy.png"))
            enemy_entity.add_component(PhysicsBody(mass=5.0))
            
            # Store enemy ID
            self.enemy_ids.append(enemy_id)
            
            return enemy_id
        except Exception as e:
            print(f"Error spawning enemy: {e}")
            return None
            
    def update(self, dt):
        """Update scene logic (variable timestep)"""
        # Update stars (parallax background)
        for star in self.stars:
            star['pos'][1] += star['speed'] * dt
            if star['pos'][1] > self.height:
                star['pos'][1] = 0
                star['pos'][0] = random.randint(0, self.width)
        
        # Update player position based on velocity
        self.player_pos += self.player_velocity * dt
        
        # Constrain player to screen
        self.player_pos[0] = max(24, min(self.width - 24, self.player_pos[0]))
        self.player_pos[1] = max(24, min(self.height - 24, self.player_pos[1]))
        
        # Update player entity
        player_entity = self.world.get_entity(self.player_id)
        if player_entity:
            transform = player_entity.get_component(Transform)
            if transform:
                transform.position = self.player_pos.copy()
        
        # Enemy spawning
        self.enemy_spawn_timer += dt
        if self.enemy_spawn_timer >= self.enemy_spawn_interval:
            self.enemy_spawn_timer = 0
            self.spawn_enemy()
            
        # Update enemies - move towards player
        for enemy_id in self.enemy_ids[:]:  # Copy list to allow removal
            enemy_entity = self.world.get_entity(enemy_id)
            if enemy_entity:
                transform = enemy_entity.get_component(Transform)
                if transform:
                    # Move towards player
                    direction = self.player_pos - transform.position
                    distance = np.linalg.norm(direction)
                    if distance > 0:
                        direction = direction / distance
                        transform.position += direction * 100 * dt
                        
                    # Check collision with player (simple circle collision)
                    if distance < 30:
                        # Placeholder for player hit
                        self.player_velocity = -direction * 400  # Knockback
                        
                    # Remove enemies that go off screen
                    pos = transform.position
                    if (pos[0] < -50 or pos[0] > self.width + 50 or 
                        pos[1] < -50 or pos[1] > self.height + 50):
                        self.world.remove_entity(enemy_id)
                        self.enemy_ids.remove(enemy_id)
        
        # Update debug info
        self.debug_info['entities'] = len(self.world.entities)
        self.debug_info['player_pos'] = self.player_pos.copy()
        
        # Update HUD
        if self.hud:
            self.hud.update(dt, self.debug_info)
        
    def fixed_update(self, dt):
        """Update scene physics (fixed timestep)"""
        # Slow down player velocity (friction)
        if np.linalg.norm(self.player_velocity) > 0:
            self.player_velocity *= 0.95
        
    def handle_event(self, event):
        """Handle input events"""
        # Handle player movement
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w or event.key == pygame.K_UP:
                self.player_velocity[1] = -self.player_speed
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.player_velocity[1] = self.player_speed
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.player_velocity[0] = -self.player_speed
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.player_velocity[0] = self.player_speed
            elif event.key == pygame.K_SPACE:
                # Placeholder for player action
                pass
                
        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN):
                self.player_velocity[1] = 0
            elif event.key in (pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT):
                self.player_velocity[0] = 0
        
    def render(self, screen):
        """Render the scene"""
        # Fill background
        if self.assets['background']:
            screen.blit(self.assets['background'], (0, 0))
        else:
            screen.fill((20, 20, 30))
        
        # Draw stars
        for star in self.stars:
            pygame.draw.circle(screen, star['color'], 
                              (int(star['pos'][0]), int(star['pos'][1])), 
                              star['size'])
        
        # Draw enemies
        if self.assets['enemy']:
            for enemy_id in self.enemy_ids:
                enemy_entity = self.world.get_entity(enemy_id)
                if enemy_entity:
                    transform = enemy_entity.get_component(Transform)
                    if transform:
                        pos = transform.position
                        enemy_rect = self.assets['enemy'].get_rect(center=(int(pos[0]), int(pos[1])))
                        screen.blit(self.assets['enemy'], enemy_rect)
        
        # Draw player
        if self.assets['player']:
            player_rect = self.assets['player'].get_rect(center=(int(self.player_pos[0]), int(self.player_pos[1])))
            screen.blit(self.assets['player'], player_rect)
        else:
            # Fallback if sprite not loaded
            pygame.draw.circle(screen, (0, 255, 0), 
                              (int(self.player_pos[0]), int(self.player_pos[1])), 
                              24)
                              
        # Render movement direction indicator
        if np.linalg.norm(self.player_velocity) > 10:
            direction = self.player_velocity / np.linalg.norm(self.player_velocity)
            end_pos = self.player_pos + direction * 40
            pygame.draw.line(screen, (0, 255, 0), 
                            (int(self.player_pos[0]), int(self.player_pos[1])),
                            (int(end_pos[0]), int(end_pos[1])), 2)
                              
        # Draw game title
        title = self.font.render("Demo Scene", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.width//2, 50))
        screen.blit(title, title_rect)
        
        # Draw instructions
        instructions = self.small_font.render("Use WASD or Arrow Keys to move", True, (200, 200, 200))
        instruct_rect = instructions.get_rect(center=(self.width//2, self.height - 30))
        screen.blit(instructions, instruct_rect)
        
        # Draw info about enemies
        enemy_text = self.small_font.render(f"Enemies: {len(self.enemy_ids)}", True, (200, 200, 200))
        enemy_rect = enemy_text.get_rect(topleft=(20, 20))
        screen.blit(enemy_text, enemy_rect)


class DemoHUD:
    """Heads-up display for the demo scene"""
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.font = pygame.font.SysFont(None, 24)
        
        # HUD elements
        self.fps_text = None
        self.entity_count_text = None
        self.position_text = None
        
        # Demo health bar
        self.health = 100
        self.max_health = 100
        
    def update(self, dt, debug_info):
        """Update HUD elements"""
        # Update text elements
        self.fps_text = self.font.render(f"FPS: {int(1/dt) if dt > 0 else 0}", True, (200, 200, 200))
        self.entity_count_text = self.font.render(f"Entities: {debug_info['entities']}", True, (200, 200, 200))
        
        pos = debug_info['player_pos']
        self.position_text = self.font.render(f"Position: ({int(pos[0])}, {int(pos[1])})", True, (200, 200, 200))
        
        # Demo health decrease over time
        self.health = max(0, self.health - 0.1)
        if self.health <= 0:
            # Reset health when depleted
            self.health = self.max_health
        
    def draw(self, screen):
        """Draw HUD elements"""
        # Draw debug info in top-left corner
        screen.blit(self.fps_text, (10, 10))
        screen.blit(self.entity_count_text, (10, 30))
        screen.blit(self.position_text, (10, 50))
        
        # Draw health bar in bottom-left
        health_width = 200
        health_height = 20
        health_x = 20
        health_y = self.height - 60
        
        # Draw health bar background
        pygame.draw.rect(screen, (60, 60, 60), 
                        (health_x, health_y, health_width, health_height))
        
        # Draw health bar fill
        health_fill_width = int((self.health / self.max_health) * health_width)
        health_color = (0, 255, 0)  # Green
        # Change color based on health percentage
        if self.health < self.max_health * 0.6:
            health_color = (255, 255, 0)  # Yellow
        if self.health < self.max_health * 0.3:
            health_color = (255, 0, 0)  # Red
            
        pygame.draw.rect(screen, health_color, 
                        (health_x, health_y, health_fill_width, health_height))
        
        # Draw health bar border
        pygame.draw.rect(screen, (200, 200, 200), 
                        (health_x, health_y, health_width, health_height), 2)
        
        # Draw health text
        health_text = self.font.render(f"Health: {int(self.health)}/{self.max_health}", True, (255, 255, 255))
        screen.blit(health_text, (health_x + 10, health_y + 2))