import pygame
import sys
import random
import os
import math
import json
from datetime import datetime

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound effects

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
PIPE_SPAWN_INTERVAL = 1500  # milliseconds
FALL_SPEED = 3  # Normal falling speed
BASE_PIPE_SPEED = 2  # Initial pipe speed
BACKGROUND_SPEED = 0.5  # Speed of background movement
POWER_UP_SPAWN_CHANCE = 0.50  # 50% chance to spawn a power-up
POWER_UP_DURATION = 5000  # 5 seconds duration for power-ups
ENEMY_SPAWN_CHANCE = 0.2  # 20% chance to spawn an enemy
FIREBALL_SPEED = 7  # Speed of fireballs
PARTICLE_COUNT = 20  # Number of particles for effects
LIGHT_SOURCE = (SCREEN_WIDTH//2, 0)  # Light source position for realistic lighting
RAIN_DENSITY = 0.3  # Density of rain particles
LIGHTNING_CHANCE = 0.001  # Chance of lightning per frame
WIND_SPEED = 0.5  # Speed of wind effect
WEATHER_CHANGE_INTERVAL = 10000  # Weather changes every 10 seconds

# Add after the game constants
LEADERBOARD_FILE = 'leaderboard.json'
MAX_LEADERBOARD_ENTRIES = 10
NAME_INPUT_BOX = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2, 300, 40)

# Load sound effects
try:
    jump_sound = pygame.mixer.Sound('sounds/jump.wav')
    score_sound = pygame.mixer.Sound('sounds/score.wav')
    collision_sound = pygame.mixer.Sound('sounds/collision.wav')
    game_over_sound = pygame.mixer.Sound('sounds/game_over.wav')
    power_pipe_sound = pygame.mixer.Sound('sounds/power_pipe.wav')
    lightning_sound = pygame.mixer.Sound('sounds/lightning.wav')
    rain_sound = pygame.mixer.Sound('sounds/rain.wav')
except:
    print("Warning: Sound files not found. Game will run without sound effects.")
    jump_sound = None
    score_sound = None
    collision_sound = None
    game_over_sound = None
    power_pipe_sound = None
    lightning_sound = None
    rain_sound = None

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
MAGENTA = (255, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)

# Mario and Luigi colors
MARIO_RED = (230, 0, 0)  # Slightly darker red for Mario
MARIO_BLUE = (30, 60, 255)  # Richer blue for overalls
MARIO_SKIN = (255, 200, 150)  # Skin tone
MARIO_BROWN = (101, 67, 33)  # Darker brown for hair and mustache
MARIO_YELLOW = (255, 215, 0)  # Gold color for buttons
LUIGI_GREEN = (40, 180, 40)  # Luigi's signature green
DONKEY_KONG_BROWN = (139, 69, 19)  # Brown color for Donkey Kong
DONKEY_KONG_RED = (255, 0, 0)  # Red color for Donkey Kong's tie
POWER_PIPE_COLOR = (255, 215, 0)  # Gold color for Power Pipes
POWER_PIPE_GLOW = (255, 255, 150)  # Lighter gold for glow effect
ENEMY_COLOR = (255, 0, 0)  # Red color for enemies
FIREBALL_COLOR = (255, 165, 0)  # Orange color for fireballs
SHADOW_COLOR = (0, 0, 0, 64)  # Semi-transparent black for shadows
HIGHLIGHT_COLOR = (255, 255, 255, 32)  # Semi-transparent white for highlights
REFLECTION_COLOR = (255, 255, 255, 16)  # Very subtle white for reflections
BUILDING_COLORS = [
    (100, 100, 100),  # Dark gray
    (120, 120, 120),  # Medium gray
    (140, 140, 140),  # Light gray
    (160, 160, 160),  # Very light gray
]
WINDOW_COLOR = (255, 255, 200)  # Light yellow for windows
LIGHT_COLOR = (255, 255, 150)   # Brighter yellow for lit windows
EMPIRE_STATE_COLOR = (150, 150, 150)  # Special color for Empire State Building
SHIELD_COLOR = (0, 191, 255)  # Deep Sky Blue
SHIELD_GLOW = (135, 206, 250)  # Light Sky Blue
PIPE_COLOR = (10, 40, 10, 220)  # Very dark green, mostly opaque
PIPE_HIGHLIGHT = (20, 60, 20, 180)  # Slightly lighter dark green, mostly opaque
PIPE_SHADOW = (5, 20, 5, 180)  # Even darker green, mostly opaque
SKY_COLOR = (135, 206, 235)  # Sky blue
CLOUD_COLOR = (255, 255, 255)  # White for clouds
CLOUD_SHADOW = (200, 200, 200)  # Light gray for cloud shadows
RAIN_COLOR = (200, 200, 255, 128)  # Light blue for rain
LIGHTNING_COLOR = (255, 255, 255)  # White for lightning
WIND_PARTICLE_COLOR = (200, 200, 200, 64)  # Gray for wind particles

# Mario colors
MARIO_RED = (255, 0, 0)  # Mario's hat and shirt
MARIO_BLUE = (0, 0, 255)  # Mario's overalls
MARIO_BROWN = (139, 69, 19)  # Mario's hair and shoes
MARIO_SKIN = (255, 198, 140)  # Mario's skin tone

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Game states
GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_OVER = 2  # Game over state
GAME_STATE_LEADERBOARD = 3
GAME_STATE_NAME_ENTRY = 4  # For entering name in leaderboard
GAME_STATE_HELP = 5
GAME_STATE_WINNING = 6  # Mario battle
GAME_STATE_LUIGI_BATTLE = 7  # Luigi battle
GAME_STATE_COUNTDOWN = 8  # 3-second countdown state

class WeatherSystem:
    def __init__(self):
        self.rain_particles = []
        self.lightning_active = False
        self.lightning_timer = 0
        self.lightning_duration = 5
        self.wind_particles = []
        self.weather_type = 'clear'  # 'clear', 'rainy', 'stormy'
        self.weather_timer = 0
        self.generate_rain()
        self.generate_wind()

    def generate_rain(self):
        for _ in range(int(SCREEN_WIDTH * SCREEN_HEIGHT * RAIN_DENSITY)):
            self.rain_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(-SCREEN_HEIGHT, 0),
                'speed': random.uniform(5, 10),
                'length': random.randint(5, 15),
                'alpha': random.randint(64, 128)
            })

    def generate_wind(self):
        for _ in range(50):
            self.wind_particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'vx': random.uniform(-WIND_SPEED, WIND_SPEED),
                'vy': random.uniform(-WIND_SPEED, WIND_SPEED),
                'life': random.randint(30, 60),
                'size': random.uniform(1, 3)
            })

    def update(self):
        # Update rain
        for particle in self.rain_particles:
            particle['y'] += particle['speed']
            if particle['y'] > SCREEN_HEIGHT:
                particle['y'] = random.randint(-SCREEN_HEIGHT, 0)
                particle['x'] = random.randint(0, SCREEN_WIDTH)

        # Update lightning
        if self.lightning_active:
            self.lightning_timer += 1
            if self.lightning_timer >= self.lightning_duration:
                self.lightning_active = False
        elif random.random() < LIGHTNING_CHANCE:
            self.lightning_active = True
            self.lightning_timer = 0
            if lightning_sound:
                lightning_sound.play()

        # Update wind particles
        for particle in self.wind_particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.wind_particles.remove(particle)
                self.wind_particles.append({
                    'x': random.randint(0, SCREEN_WIDTH),
                    'y': random.randint(0, SCREEN_HEIGHT),
                    'vx': random.uniform(-WIND_SPEED, WIND_SPEED),
                    'vy': random.uniform(-WIND_SPEED, WIND_SPEED),
                    'life': random.randint(30, 60),
                    'size': random.uniform(1, 3)
                })

        # Update weather type
        self.weather_timer += 1
        if self.weather_timer >= WEATHER_CHANGE_INTERVAL:
            self.weather_timer = 0
            self.weather_type = random.choice(['clear', 'rainy', 'stormy'])
            if self.weather_type == 'rainy' and rain_sound:
                rain_sound.play()

    def draw(self):
        # Draw rain
        if self.weather_type in ['rainy', 'stormy']:
            for particle in self.rain_particles:
                alpha = particle['alpha']
                if self.weather_type == 'stormy':
                    alpha = min(255, alpha * 1.5)
                pygame.draw.line(screen, (*RAIN_COLOR[:3], alpha),
                               (particle['x'], particle['y']),
                               (particle['x'], particle['y'] + particle['length']), 1)

        # Draw lightning
        if self.lightning_active:
            # Create lightning flash effect
            flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            flash_surface.fill((*LIGHTNING_COLOR, 128))
            screen.blit(flash_surface, (0, 0))

            # Draw lightning bolts
            for _ in range(3):
                start_x = random.randint(0, SCREEN_WIDTH)
                start_y = 0
                points = [(start_x, start_y)]
                current_x, current_y = start_x, start_y
                
                while current_y < SCREEN_HEIGHT:
                    current_x += random.randint(-20, 20)
                    current_y += random.randint(10, 30)
                    points.append((current_x, current_y))
                
                pygame.draw.lines(screen, LIGHTNING_COLOR, False, points, 2)

        # Draw wind particles
        for particle in self.wind_particles:
            alpha = int(255 * (particle['life'] / 60))
            pygame.draw.circle(screen, (*WIND_PARTICLE_COLOR[:3], alpha),
                             (int(particle['x']), int(particle['y'])),
                             int(particle['size']))

class Cityscape:
    def __init__(self):
        self.buildings = []
        self.generate_buildings()
        self.clouds = []
        self.generate_clouds()
        self.particles = []  # Add particles for atmospheric effects
        self.lightning_flash = 0  # Add lightning flash effect
        
    def generate_buildings(self):
        # Create initial set of buildings
        x = 0
        while x < SCREEN_WIDTH * 2:  # Generate enough buildings to cover screen twice
            # 5% chance to generate Empire State Building
            if random.random() < 0.05 and x > SCREEN_WIDTH:  # Don't place it at the very start
                self.buildings.append(self.create_empire_state(x))
                x += 120  # Empire State Building width
            else:
                width = random.randint(30, 80)
                height = random.randint(100, 300)
                color = random.choice(BUILDING_COLORS)
                self.buildings.append({
                    'x': x,
                    'width': width,
                    'height': height,
                    'color': color,
                    'windows': self.generate_windows(width, height),
                    'is_empire_state': False,
                    'lighting': random.random() < 0.3  # 30% chance of having dynamic lighting
                })
                x += width + random.randint(10, 30)  # Add some space between buildings

    def create_empire_state(self, x):
        height = 400  # Taller than regular buildings
        width = 120   # Wider than regular buildings
        return {
            'x': x,
            'width': width,
            'height': height,
            'color': EMPIRE_STATE_COLOR,
            'windows': self.generate_empire_state_windows(width, height),
            'is_empire_state': True,
            'lighting': True  # Empire State Building always has dynamic lighting
        }

    def generate_windows(self, width, height):
        windows = []
        window_size = 4
        window_spacing = 8
        
        # Calculate number of windows that can fit
        num_windows_x = (width - window_spacing) // (window_size + window_spacing)
        num_windows_y = (height - window_spacing) // (window_size + window_spacing)
        
        # Generate window positions
        for i in range(num_windows_x):
            for j in range(num_windows_y):
                # Randomly decide if window is lit
                is_lit = random.random() < 0.3  # 30% chance of being lit
                windows.append({
                    'x': window_spacing + i * (window_size + window_spacing),
                    'y': window_spacing + j * (window_size + window_spacing),
                    'size': window_size,
                    'is_lit': is_lit,
                    'flicker': random.random() < 0.1  # 10% chance of flickering
                })
        
        return windows

    def generate_empire_state_windows(self, width, height):
        windows = []
        window_size = 4
        window_spacing = 8
        
        # Empire State Building has more windows and distinctive pattern
        num_windows_x = (width - window_spacing) // (window_size + window_spacing)
        num_windows_y = (height - window_spacing) // (window_size + window_spacing)
        
        # Generate window positions with more lit windows
        for i in range(num_windows_x):
            for j in range(num_windows_y):
                # Higher chance of being lit for Empire State Building
                is_lit = random.random() < 0.5  # 50% chance of being lit
                windows.append({
                    'x': window_spacing + i * (window_size + window_spacing),
                    'y': window_spacing + j * (window_size + window_spacing),
                    'size': window_size,
                    'is_lit': is_lit,
                    'flicker': random.random() < 0.2  # 20% chance of flickering
                })
        
        return windows

    def generate_clouds(self):
        for _ in range(5):
            self.clouds.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(50, 200),
                'width': random.randint(60, 120),
                'height': random.randint(20, 40),
                'speed': random.uniform(0.2, 0.5),
                'density': random.uniform(0.5, 1.0),  # Add cloud density
                'lightning': random.random() < 0.3  # 30% chance of lightning cloud
            })

    def update(self):
        # Move buildings to the left
        for building in self.buildings:
            building['x'] -= BACKGROUND_SPEED
            
        # Update clouds
        for cloud in self.clouds:
            cloud['x'] -= cloud['speed']
            if cloud['x'] + cloud['width'] < 0:
                cloud['x'] = SCREEN_WIDTH
                cloud['y'] = random.randint(50, 200)
                cloud['density'] = random.uniform(0.5, 1.0)
                cloud['lightning'] = random.random() < 0.3
                
        # Add atmospheric particles
        if random.random() < 0.1:
            self.particles.append({
                'x': random.randint(0, SCREEN_WIDTH),
                'y': random.randint(0, SCREEN_HEIGHT),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'life': random.randint(30, 60),
                'color': (255, 255, 255, 32)
            })
            
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
            
        # Remove buildings that are off screen and add new ones
        if self.buildings[0]['x'] + self.buildings[0]['width'] < 0:
            last_building = self.buildings[-1]
            new_x = last_building['x'] + last_building['width'] + random.randint(10, 30)
            
            if random.random() < 0.05:
                self.buildings.append(self.create_empire_state(new_x))
            else:
                width = random.randint(30, 80)
                height = random.randint(100, 300)
                color = random.choice(BUILDING_COLORS)
                self.buildings.append({
                    'x': new_x,
                    'width': width,
                    'height': height,
                    'color': color,
                    'windows': self.generate_windows(width, height),
                    'is_empire_state': False,
                    'lighting': random.random() < 0.3
                })
            self.buildings.pop(0)

    def draw(self):
        # Draw sky gradient
        for y in range(SCREEN_HEIGHT):
            alpha = int(255 * (1 - y / SCREEN_HEIGHT))
            color = (*SKY_COLOR, alpha)
            pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Draw atmospheric particles
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 60))
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(screen, color,
                             (int(particle['x']), int(particle['y'])),
                             1)
        
        # Draw clouds with density
        for cloud in self.clouds:
            # Draw cloud shadow with density
            shadow_alpha = int(64 * cloud['density'])
            pygame.draw.ellipse(screen, (*CLOUD_SHADOW, shadow_alpha),
                              (cloud['x'] + 2, cloud['y'] + 2,
                               cloud['width'], cloud['height']))
            # Draw cloud with density
            cloud_alpha = int(255 * cloud['density'])
            pygame.draw.ellipse(screen, (*CLOUD_COLOR, cloud_alpha),
                              (cloud['x'], cloud['y'],
                               cloud['width'], cloud['height']))
            
            # Draw lightning in cloud
            if cloud['lightning'] and random.random() < 0.01:
                self.lightning_flash = 10
                if lightning_sound:
                    lightning_sound.play()
        
        # Draw buildings
        for building in self.buildings:
            if building['x'] + building['width'] > 0 and building['x'] < SCREEN_WIDTH:
                # Draw building shadow with gradient
                for i in range(3):
                    alpha = 64 - i * 20
                    if alpha > 0:
                        pygame.draw.rect(screen, (*SHADOW_COLOR[:3], alpha),
                                       (building['x'] + 2 + i, SCREEN_HEIGHT - building['height'] + 2 + i,
                                        building['width'], building['height']))
                
                # Draw building base
                pygame.draw.rect(screen, building['color'],
                               (building['x'], SCREEN_HEIGHT - building['height'],
                                building['width'], building['height']))
                
                # Draw windows with reflection
                for window in building['windows']:
                    window_x = building['x'] + window['x']
                    window_y = SCREEN_HEIGHT - building['height'] + window['y']
                    
                    # Draw window shadow with gradient
                    for i in range(2):
                        alpha = 32 - i * 16
                        if alpha > 0:
                            pygame.draw.rect(screen, (*SHADOW_COLOR[:3], alpha),
                                           (window_x + 1 + i, window_y + 1 + i,
                                            window['size'], window['size']))
                    
                    # Draw window with flickering effect
                    if window['flicker'] and random.random() < 0.1:
                        window['is_lit'] = not window['is_lit']
                    
                    color = LIGHT_COLOR if window['is_lit'] else WINDOW_COLOR
                    pygame.draw.rect(screen, color,
                                   (window_x, window_y,
                                    window['size'], window['size']))
                                    
                    # Draw window reflection
                    if window['is_lit']:
                        pygame.draw.rect(screen, REFLECTION_COLOR,
                                       (window_x + 1, window_y + 1,
                                        window['size'] - 2, window['size'] - 2))
                
                # Add Empire State Building spire
                if building['is_empire_state']:
                    spire_height = 50
                    spire_width = 10
                    # Draw spire shadow with gradient
                    for i in range(3):
                        alpha = 64 - i * 20
                        if alpha > 0:
                            pygame.draw.rect(screen, (*SHADOW_COLOR[:3], alpha),
                                           (building['x'] + (building['width'] - spire_width) // 2 + 1 + i,
                                            SCREEN_HEIGHT - building['height'] - spire_height + 1 + i,
                                            spire_width, spire_height))
                    # Draw spire
                    pygame.draw.rect(screen, building['color'],
                                   (building['x'] + (building['width'] - spire_width) // 2,
                                    SCREEN_HEIGHT - building['height'] - spire_height,
                                    spire_width, spire_height))
                    
                    # Add lightning rod effect
                    if self.lightning_flash > 0:
                        pygame.draw.line(screen, LIGHTNING_COLOR,
                                       (building['x'] + building['width']//2,
                                        SCREEN_HEIGHT - building['height'] - spire_height),
                                       (building['x'] + building['width']//2,
                                        SCREEN_HEIGHT - building['height'] - spire_height - 20), 2)
                        self.lightning_flash -= 1

class Bird:
    def __init__(self):
        self.reset()
        self.mouth_angle = 0
        self.mouth_opening = True
        self.animation_speed = 5
        self.shield_active = False
        self.shield_timer = 0
        self.shield_glow_phase = 0
        self.particles = []
        self.trail_particles = []  # Add trail particles for more realistic movement

    def update(self):
        if game_state == GAME_STATE_PLAYING:
            self.velocity += self.gravity
            self.y += self.velocity
            
            # Update mouth animation
            if self.mouth_opening:
                self.mouth_angle = min(45, self.mouth_angle + self.animation_speed)
                if self.mouth_angle >= 45:
                    self.mouth_opening = False
            else:
                self.mouth_angle = max(0, self.mouth_angle - self.animation_speed)
                if self.mouth_angle <= 0:
                    self.mouth_opening = True

            # Update shield if active
            if self.shield_active:
                self.shield_timer -= 16
                self.shield_glow_phase = (self.shield_glow_phase + 0.1) % (2 * math.pi)
                if self.shield_timer <= 0:
                    self.shield_active = False

            # Add movement particles
            if abs(self.velocity) > 0.1:
                for _ in range(2):
                    self.particles.append({
                        'x': self.x + random.randint(-5, 5),
                        'y': self.y + random.randint(-5, 5),
                        'vx': random.uniform(-1, 1),
                        'vy': random.uniform(-1, 1),
                        'life': random.randint(10, 20),
                        'color': (255, 255, 0, 128)
                    })
                    
                    # Add trail particles
                    self.trail_particles.append({
                        'x': self.x + self.width/2,
                        'y': self.y + self.height/2,
                        'life': random.randint(20, 40),
                        'size': random.uniform(1, 3),
                        'color': (255, 255, 0, 64)
                    })

            # Update particles
            for particle in self.particles[:]:
                particle['x'] += particle['vx']
                particle['y'] += particle['vy']
                particle['life'] -= 1
                if particle['life'] <= 0:
                    self.particles.remove(particle)
                    
            # Update trail particles
            for particle in self.trail_particles[:]:
                particle['life'] -= 1
                if particle['life'] <= 0:
                    self.trail_particles.remove(particle)

    def jump(self):
        self.velocity = self.jump_strength
        if jump_sound:
            jump_sound.play()

    def draw(self):
        # Draw trail particles
        for particle in self.trail_particles:
            alpha = int(255 * (particle['life'] / 40))
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(screen, color,
                             (int(particle['x']), int(particle['y'])),
                             int(particle['size']))

        # Draw movement particles
        for particle in self.particles:
            alpha = int(255 * (particle['life'] / 20))
            color = (*particle['color'][:3], alpha)
            pygame.draw.circle(screen, color,
                             (int(particle['x']), int(particle['y'])),
                             2)

        # Calculate rotation angle based on velocity
        rotation_angle = max(-30, min(30, self.velocity * 3))
        
        # Draw shadow with distance-based blur
        shadow_offset = 3
        shadow_alpha = 64
        for i in range(3):
            alpha = shadow_alpha - i * 20
            if alpha > 0:
                pygame.draw.circle(screen, (*SHADOW_COLOR[:3], alpha),
                                 (int(self.x + self.width/2 + shadow_offset + i),
                                  int(self.y + self.height/2 + shadow_offset + i)),
                                 self.width//2)
        
        # Draw Pac-Man body with highlight
        pygame.draw.circle(screen, YELLOW,
                         (int(self.x + self.width/2), int(self.y + self.height/2)),
                         self.width//2)
        
        # Add highlight with gradient
        highlight_offset = -3
        for i in range(3):
            alpha = 32 - i * 10
            if alpha > 0:
                pygame.draw.circle(screen, (*HIGHLIGHT_COLOR[:3], alpha),
                                 (int(self.x + self.width/2 + highlight_offset - i),
                                  int(self.y + self.height/2 + highlight_offset - i)),
                                 self.width//4)
        
        # Draw shield if active
        if self.shield_active:
            glow_intensity = 0.5 + 0.5 * math.sin(self.shield_glow_phase)
            shield_radius = self.width//2 + 10
            shield_color = (
                int(SHIELD_COLOR[0] * glow_intensity),
                int(SHIELD_COLOR[1] * glow_intensity),
                int(SHIELD_COLOR[2] * glow_intensity)
            )
            # Draw shield with gradient
            for i in range(3):
                alpha = 128 - i * 40
                if alpha > 0:
                    pygame.draw.circle(screen, (*shield_color, alpha),
                                     (int(self.x + self.width/2), int(self.y + self.height/2)),
                                     shield_radius - i, 2)
        
        # Calculate mouth points
        center = (int(self.x + self.width/2), int(self.y + self.height/2))
        radius = self.width//2
        
        # Convert angles to radians and adjust for rotation
        start_angle = math.radians(self.mouth_angle - rotation_angle)
        end_angle = math.radians(-self.mouth_angle - rotation_angle)
        
        # Create mouth points
        points = [center]
        for angle in [start_angle, end_angle]:
            x = center[0] + radius * math.cos(angle)
            y = center[1] - radius * math.sin(angle)
            points.append((int(x), int(y)))
        
        # Draw mouth (black triangle)
        pygame.draw.polygon(screen, BLACK, points)

    def reset(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.width = 30
        self.height = 30
        self.velocity = 0
        self.gravity = 0.15
        self.jump_strength = -4
        self.target_pipe = None
        self.is_falling_through = False
        self.mouth_angle = 0
        self.mouth_opening = True
        self.shield_active = False
        self.shield_timer = 0
        self.shield_glow_phase = 0
        self.particles = []
        self.trail_particles = []  # Reset trail particles

    def get_rect(self):
        # Use a slightly smaller rect for more forgiving collisions
        margin = 4
        return pygame.Rect(self.x + margin, self.y + margin, 
                         self.width - 2*margin, self.height - 2*margin)

    def update_sucking(self):
        if self.target_pipe:
            if not self.is_falling_through:
                self.x = self.target_pipe.x + (self.target_pipe.width - self.width) // 2
                self.is_falling_through = True
                self.y = self.target_pipe.top_height
            else:
                self.y += FALL_SPEED
                self.x = self.target_pipe.x + (self.target_pipe.width - self.width) // 2
                
                # Continue mouth animation during falling
                if self.mouth_opening:
                    self.mouth_angle = min(45, self.mouth_angle + self.animation_speed)
                    if self.mouth_angle >= 45:
                        self.mouth_opening = False
                else:
                    self.mouth_angle = max(0, self.mouth_angle - self.animation_speed)
                    if self.mouth_angle <= 0:
                        self.mouth_opening = True
            
            if self.y > SCREEN_HEIGHT:
                print("Bird fell through pipe")
                return True
        else:
            self.y += FALL_SPEED
            if self.y > SCREEN_HEIGHT:
                print("Bird fell through screen")
                return True
        return False

    def activate_shield(self):
        self.shield_active = True
        self.shield_timer = POWER_UP_DURATION
        if power_pipe_sound:
            power_pipe_sound.play()

class Pipe:
    def __init__(self, speed):
        self.gap = 150
        self.width = 50
        self.x = SCREEN_WIDTH
        self.top_height = random.randint(50, SCREEN_HEIGHT - self.gap - 50)
        self.bottom_y = self.top_height + self.gap
        self.speed = speed
        self.is_moving = True
        self.scored = False
        self.is_power_pipe = random.random() < 0.2
        self.glow_phase = 0
        self.glow_speed = 0.1
        self.power_effect_active = False
        self.power_effect_timer = 0
        self.power_effect_duration = 3000
        self.texture_offset = 0
        self.particles = []  # Add particles for pipe effects

    def update(self):
        if self.is_moving:
            self.x -= self.speed
            
            # Update glow effect for power pipes
            if self.is_power_pipe:
                self.glow_phase = (self.glow_phase + self.glow_speed) % (2 * math.pi)
                
            # Update power effect timer
            if self.power_effect_active:
                self.power_effect_timer += 16
                if self.power_effect_timer >= self.power_effect_duration:
                    self.power_effect_active = False
                    self.power_effect_timer = 0
                    
            # Add particles for power pipes
            if self.is_power_pipe and random.random() < 0.1:
                self.particles.append({
                    'x': self.x + random.randint(0, self.width),
                    'y': random.choice([self.top_height, self.bottom_y]),
                    'vy': random.uniform(-1, 1),
                    'life': random.randint(10, 20),
                    'color': (*POWER_PIPE_COLOR[:3], 128)
                })
                
            # Update particles
            for particle in self.particles[:]:
                particle['y'] += particle['vy']
                particle['life'] -= 1
                if particle['life'] <= 0:
                    self.particles.remove(particle)

    def draw(self):
        # Create a surface for the pipe with per-pixel alpha
        pipe_surface = pygame.Surface((self.width, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        if self.is_power_pipe:
            # Calculate glow intensity
            glow_intensity = 0.5 + 0.5 * math.sin(self.glow_phase)
            
            # Draw glowing effect
            glow_color = (
                int(POWER_PIPE_GLOW[0] * glow_intensity),
                int(POWER_PIPE_GLOW[1] * glow_intensity),
                int(POWER_PIPE_GLOW[2] * glow_intensity),
                128
            )
            
            # Draw top pipe with glow and texture
            self.draw_pipe_texture(pipe_surface, 0, self.top_height, glow_color, POWER_PIPE_COLOR)
            
            # Draw bottom pipe with glow and texture
            self.draw_pipe_texture(pipe_surface, self.bottom_y, SCREEN_HEIGHT - self.bottom_y,
                                 glow_color, POWER_PIPE_COLOR)
                                 
            # Draw particles
            for particle in self.particles:
                alpha = int(255 * (particle['life'] / 20))
                color = (*particle['color'][:3], alpha)
                pygame.draw.circle(screen, color,
                                 (int(particle['x']), int(particle['y'])),
                                 2)
        else:
            # Draw regular pipes with texture
            self.draw_pipe_texture(pipe_surface, 0, self.top_height, PIPE_SHADOW, PIPE_COLOR)
            self.draw_pipe_texture(pipe_surface, self.bottom_y, SCREEN_HEIGHT - self.bottom_y,
                                 PIPE_SHADOW, PIPE_COLOR)
        
        # Blit the pipe surface onto the screen
        screen.blit(pipe_surface, (self.x, 0))

    def draw_pipe_texture(self, surface, y, height, shadow_color, base_color):
        # Draw base pipe
        pygame.draw.rect(surface, base_color, (0, y, self.width, height))
        
        # Draw shadow with gradient
        for i in range(3):
            alpha = 64 - i * 20
            if alpha > 0:
                pygame.draw.rect(surface, (*shadow_color[:3], alpha),
                               (0, y + i, self.width, height))
        
        # Draw texture lines with gradient
        for i in range(0, height, 10):
            line_y = y + i
            if line_y < y + height:
                # Draw highlight with gradient
                for j in range(3):
                    alpha = 32 - j * 10
                    if alpha > 0:
                        pygame.draw.line(surface, (*PIPE_HIGHLIGHT[:3], alpha),
                                       (0, line_y - j), (self.width, line_y - j), 1)
                # Draw shadow with gradient
                for j in range(3):
                    alpha = 32 - j * 10
                    if alpha > 0:
                        pygame.draw.line(surface, (*PIPE_SHADOW[:3], alpha),
                                       (0, line_y + 1 + j), (self.width, line_y + 1 + j), 1)

    def get_top_rect(self):
        return pygame.Rect(self.x, 0, self.width, self.top_height)

    def get_bottom_rect(self):
        return pygame.Rect(self.x, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y)

class DonkeyKong:
    def __init__(self):
        self.x = SCREEN_WIDTH - 100
        self.y = 100
        self.width = 60
        self.height = 80
        self.visible = False
        self.animation_frame = 0
        self.animation_speed = 0.1
        self.animation_time = 0

    def update(self):
        if self.visible:
            self.animation_time += self.animation_speed
            self.animation_frame = int(self.animation_time) % 2

    def draw(self):
        if not self.visible:
            return

        # Draw Donkey Kong's body
        pygame.draw.rect(screen, DONKEY_KONG_BROWN, 
                        (self.x, self.y, self.width, self.height))
        
        # Draw head
        pygame.draw.circle(screen, DONKEY_KONG_BROWN,
                         (self.x + self.width//2, self.y - 20), 25)
        
        # Draw eyes
        eye_offset = 10 if self.animation_frame == 0 else 8
        pygame.draw.circle(screen, WHITE,
                         (self.x + self.width//2 - eye_offset, self.y - 25), 5)
        pygame.draw.circle(screen, WHITE,
                         (self.x + self.width//2 + eye_offset, self.y - 25), 5)
        
        # Draw pupils
        pygame.draw.circle(screen, BLACK,
                         (self.x + self.width//2 - eye_offset, self.y - 25), 2)
        pygame.draw.circle(screen, BLACK,
                         (self.x + self.width//2 + eye_offset, self.y - 25), 2)
        
        # Draw tie
        pygame.draw.rect(screen, DONKEY_KONG_RED,
                        (self.x + self.width//2 - 5, self.y + 20, 10, 30))

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

class DeathCutscene:
    def __init__(self, screen):
        self.screen = screen
        self.particles = []
        self.explosion_radius = 0
        self.max_explosion_radius = 200
        self.explosion_color = (255, 0, 0)
        self.shake_intensity = 0
        self.max_shake_intensity = 20
        self.shake_duration = 60  # frames
        self.current_frame = 0
        self.screen_flash_alpha = 0
        self.screen_flash_duration = 30
        self.screen_flash_color = (255, 0, 0)
        self.slow_motion_factor = 0.1
        self.original_fps = FPS
        self.is_active = False

    def start(self, bird_pos):
        self.is_active = True
        self.current_frame = 0
        self.explosion_radius = 0
        self.shake_intensity = 0
        self.screen_flash_alpha = 0
        self.particles = []
        
        # Create explosion particles
        for _ in range(100):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 8)
            size = random.uniform(2, 6)
            color = (
                random.randint(200, 255),
                random.randint(0, 100),
                random.randint(0, 100)
            )
            self.particles.append({
                'x': bird_pos[0],
                'y': bird_pos[1],
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'size': size,
                'color': color,
                'life': random.randint(30, 60)
            })

    def update(self):
        if not self.is_active:
            return False

        self.current_frame += 1
        
        # Update explosion radius
        if self.explosion_radius < self.max_explosion_radius:
            self.explosion_radius += 5
        
        # Update shake intensity
        if self.current_frame < self.shake_duration:
            self.shake_intensity = self.max_shake_intensity * (1 - self.current_frame / self.shake_duration)
        
        # Update screen flash
        if self.current_frame < self.screen_flash_duration:
            self.screen_flash_alpha = 255 * (1 - self.current_frame / self.screen_flash_duration)
        
        # Update particles
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            if particle['life'] <= 0:
                self.particles.remove(particle)
        
        # End cutscene after certain duration
        if self.current_frame > 120:  # 2 seconds at 60 FPS
            self.is_active = False
            return False
        
        return True

    def draw(self):
        if not self.is_active:
            return

        # Create a surface for the screen flash
        flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        flash_surface.fill((*self.screen_flash_color, int(self.screen_flash_alpha)))
        
        # Apply screen shake
        shake_x = random.uniform(-self.shake_intensity, self.shake_intensity)
        shake_y = random.uniform(-self.shake_intensity, self.shake_intensity)
        
        # Draw explosion circle
        pygame.draw.circle(
            self.screen,
            self.explosion_color,
            (SCREEN_WIDTH // 2 + shake_x, SCREEN_HEIGHT // 2 + shake_y),
            self.explosion_radius,
            2
        )
        
        # Draw particles
        for particle in self.particles:
            pygame.draw.circle(
                self.screen,
                particle['color'],
                (int(particle['x'] + shake_x), int(particle['y'] + shake_y)),
                int(particle['size'])
            )
        
        # Draw screen flash
        self.screen.blit(flash_surface, (0, 0))

class LuigiBattle:
    def __init__(self):
        self.phase = 0
        self.timer = 0
        self.luigi_x = SCREEN_WIDTH
        self.luigi_y = SCREEN_HEIGHT // 2
        self.flappy_original_pos = None
        self.flash_timer = 0
        self.battle_effects = []
        self.fireballs = []  # List to store active fireballs
        self.luigi_health = 150  # Luigi is stronger than Mario
        self.flappy_health = 100
        self.winner = None
        self.dialogue_timer = 0
        self.current_dialogue = ""
        self.dialogue_phase = 0
        self.countdown = 3
        self.countdown_start = False
        self.effect_timer = 0  # Timer for special effects
        self.dialogues = [
            "Luigi: HOW DARE YOU DEFEAT MY BROTHER!",
            "Flappy: *Unfazed chirp*",
            "Luigi: I WILL AVENGE HIM! PREPARE YOURSELF!",
            "Flappy: *Battle-ready squawk*",
            "Luigi: WITNESS THE POWER OF THE GREEN THUNDER!",
            "Flappy: *Dodges gracefully*",
            "Luigi: WHAT?! NOBODY HAS EVER DODGED THAT!",
            "Flappy: *Powers up with intense glow*",
            "Luigi: No... you're even stronger than before...",
            "Luigi: MARIO... I'M SORRY... I FAILED YOU!",
            "Flappy: *Triumphant victory cry*"
        ]
        
    def start(self, flappy_pos):
        self.flappy_original_pos = flappy_pos
        self.timer = 0
        self.phase = 0
        
    def add_battle_effect(self, x, y, color, effect_type=None):
        self.battle_effects.append({
            'x': x,
            'y': y,
            'color': color,
            'size': 20,
            'timer': 10,
            'type': effect_type
        })
        
    def update(self):
        self.timer += 1
        self.dialogue_timer += 1
        self.effect_timer += 1
        
        # Handle countdown after victory
        if self.countdown_start:
            if self.timer % 60 == 0:
                self.countdown -= 1
                if self.countdown < 0:
                    return True
        
        # Update battle effects
        for effect in self.battle_effects[:]:
            effect['timer'] -= 1
            effect['size'] -= 1
            if effect['timer'] <= 0:
                self.battle_effects.remove(effect)
                
        # Update fireballs
        for fireball in self.fireballs[:]:
            fireball['x'] += fireball['dx']
            fireball['y'] += fireball['dy']
            fireball['timer'] -= 1
            if fireball['timer'] <= 0:
                self.fireballs.remove(fireball)
            # Add flame trail
            if self.timer % 2 == 0:
                self.add_battle_effect(fireball['x'], fireball['y'], 
                                     random.choice([(255, 165, 0), (255, 69, 0)]),
                                     'flame_trail')
        
        # Phase 0: Luigi enters dramatically with a jump
        if self.phase == 0:
            self.luigi_x -= 6  # Faster than Mario
            self.luigi_y = SCREEN_HEIGHT // 2 - math.sin(self.timer * 0.1) * 30  # Jumping motion
            if self.luigi_x <= SCREEN_WIDTH - 100:
                self.phase = 1
                self.current_dialogue = self.dialogues[0]
                self.dialogue_phase = 1
                
        # Phase 1: Battle sequence
        elif self.phase == 1:
            if self.timer % 45 == 0:  # Faster attacks than Mario
                # Flappy attacks Luigi (stronger)
                damage = random.randint(20, 30)
                self.luigi_health -= damage
                self.add_battle_effect(self.luigi_x + 25, self.luigi_y, (255, 255, 0))
                
                # Luigi attacks Flappy with green lightning
                if random.random() > 0.4:  # 40% chance to miss
                    damage = random.randint(10, 15)
                    self.flappy_health -= damage
                    
                    # Main lightning bolt
                    start_x = self.luigi_x + 25
                    start_y = self.luigi_y
                    end_x = self.flappy_original_pos[0]
                    end_y = self.flappy_original_pos[1]
                    
                    # Create zigzag lightning path
                    points = [(start_x, start_y)]
                    current_x = start_x
                    current_y = start_y
                    steps = 5
                    for i in range(steps):
                        next_x = start_x + (end_x - start_x) * (i + 1) / steps
                        next_y = start_y + (end_y - start_y) * (i + 1) / steps
                        # Add some randomness to create zigzag
                        offset = random.randint(-20, 20)
                        points.append((next_x + offset, next_y))
                    points.append((end_x, end_y))
                    
                    # Draw main lightning bolt
                    for i in range(len(points) - 1):
                        self.add_battle_effect(points[i][0], points[i][1], 
                                             (100, 255, 100), 'lightning')
                        # Add branching lightning
                        if random.random() < 0.5:
                            branch_x = points[i][0] + random.randint(-30, 30)
                            branch_y = points[i][1] + random.randint(-30, 30)
                            self.add_battle_effect(branch_x, branch_y,
                                                 (100, 255, 100), 'lightning')
                    
                    # Add impact effects at the end
                    for _ in range(5):
                        self.add_battle_effect(
                            end_x + random.randint(-20, 20),
                            end_y + random.randint(-20, 20),
                            (150, 255, 150),
                            'lightning_impact'
                        )
                
                # After attack, show next dialogue
                if self.dialogue_phase < len(self.dialogues) - 1:
                    self.dialogue_phase += 1
                    self.current_dialogue = self.dialogues[self.dialogue_phase]
                    self.dialogue_timer = 0
                
                # Make sure Flappy always wins
                if self.luigi_health <= 0:
                    self.winner = "flappy"
                    self.phase = 2
                    self.current_dialogue = self.dialogues[-1]
                    
        # Phase 2: Victory animation
        elif self.phase == 2:
            self.flash_timer += 1
            if self.flash_timer >= 120:
                self.countdown_start = True
        
        return False
        
    def draw(self, screen, bird):
        # Draw countdown if active
        if self.countdown_start and self.countdown >= 0:
            font = pygame.font.Font(None, 74)
            countdown_text = str(self.countdown) if self.countdown > 0 else "GO!"
            text = font.render(countdown_text, True, (255, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
            return
            
        # Draw dialogue box and text
        if self.current_dialogue:
            dialogue_surface = pygame.Surface((SCREEN_WIDTH - 40, 80))
            dialogue_surface.fill((255, 255, 255))
            dialogue_surface.set_alpha(200)
            screen.blit(dialogue_surface, (20, SCREEN_HEIGHT - 100))
            
            font = pygame.font.Font(None, 32)
            text = font.render(self.current_dialogue, True, (0, 0, 0))
            screen.blit(text, (30, SCREEN_HEIGHT - 80))
        
        # Draw health bars with labels
        font = pygame.font.Font(None, 24)
        flappy_label = font.render("Flappy", True, (0, 0, 0))
        luigi_label = font.render("Luigi", True, (0, 0, 0))
        
        # Draw health bars
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 100, 20))
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, self.flappy_health, 20))
        screen.blit(flappy_label, (10, 35))
        
        pygame.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH - 110, 10, 100, 20))
        pygame.draw.rect(screen, (0, 255, 0), (SCREEN_WIDTH - 110, 10, self.luigi_health * 100 // 150, 20))
        screen.blit(luigi_label, (SCREEN_WIDTH - 110, 35))
        
        # Draw Luigi with enhanced features
        # Hat
        pygame.draw.rect(screen, LUIGI_GREEN, (self.luigi_x, self.luigi_y - 35, 50, 15))
        pygame.draw.ellipse(screen, LUIGI_GREEN, (self.luigi_x - 5, self.luigi_y - 25, 60, 12))
        # L emblem
        pygame.draw.rect(screen, WHITE, (self.luigi_x + 20, self.luigi_y - 32, 12, 10))
        pygame.draw.line(screen, LUIGI_GREEN, (self.luigi_x + 22, self.luigi_y - 30),
                        (self.luigi_x + 22, self.luigi_y - 24), 2)
        pygame.draw.line(screen, LUIGI_GREEN, (self.luigi_x + 22, self.luigi_y - 24),
                        (self.luigi_x + 30, self.luigi_y - 24), 2)
        
        # Head and face
        pygame.draw.ellipse(screen, MARIO_SKIN, (self.luigi_x + 10, self.luigi_y - 25, 30, 35))
        
        # Hair
        for i in range(3):
            pygame.draw.arc(screen, MARIO_BROWN,
                          (self.luigi_x + 8 + i*10, self.luigi_y - 25, 10, 10),
                          math.pi, 2*math.pi, 2)
        
        # Eyes
        pygame.draw.ellipse(screen, WHITE, (self.luigi_x + 15, self.luigi_y - 20, 8, 10))
        pygame.draw.ellipse(screen, WHITE, (self.luigi_x + 27, self.luigi_y - 20, 8, 10))
        pygame.draw.ellipse(screen, (0, 0, 150), (self.luigi_x + 17, self.luigi_y - 18, 4, 6))
        pygame.draw.ellipse(screen, (0, 0, 150), (self.luigi_x + 29, self.luigi_y - 18, 4, 6))
        pygame.draw.circle(screen, WHITE, (self.luigi_x + 18, self.luigi_y - 17), 1)
        pygame.draw.circle(screen, WHITE, (self.luigi_x + 30, self.luigi_y - 17), 1)
        
        # Nose and mustache (longer than Mario's)
        pygame.draw.ellipse(screen, (200, 120, 80), (self.luigi_x + 22, self.luigi_y - 15, 8, 12))
        pygame.draw.arc(screen, MARIO_BROWN, (self.luigi_x + 10, self.luigi_y - 10, 25, 12), 0, math.pi, 3)
        pygame.draw.arc(screen, MARIO_BROWN, (self.luigi_x + 15, self.luigi_y - 10, 25, 12), 0, math.pi, 3)
        
        # Clothing
        pygame.draw.rect(screen, LUIGI_GREEN, (self.luigi_x + 5, self.luigi_y, 40, 30))
        pygame.draw.rect(screen, MARIO_BLUE, (self.luigi_x + 10, self.luigi_y + 10, 30, 20))
        pygame.draw.rect(screen, MARIO_BLUE, (self.luigi_x + 12, self.luigi_y, 5, 15))
        pygame.draw.rect(screen, MARIO_BLUE, (self.luigi_x + 33, self.luigi_y, 5, 15))
        pygame.draw.circle(screen, MARIO_YELLOW, (self.luigi_x + 15, self.luigi_y + 12), 3)
        pygame.draw.circle(screen, MARIO_YELLOW, (self.luigi_x + 35, self.luigi_y + 12), 3)
        
        # Expression based on health and dialogue phase
        if self.luigi_health > 100:
            # Angry, vengeful expression
            # Intense eyebrows
            pygame.draw.line(screen, MARIO_BROWN, (self.luigi_x + 15, self.luigi_y - 22),
                           (self.luigi_x + 22, self.luigi_y - 25), 3)
            pygame.draw.line(screen, MARIO_BROWN, (self.luigi_x + 28, self.luigi_y - 25),
                           (self.luigi_x + 35, self.luigi_y - 22), 3)
            # Determined mouth
            pygame.draw.line(screen, (0, 0, 0), (self.luigi_x + 15, self.luigi_y - 5),
                           (self.luigi_x + 35, self.luigi_y - 5), 3)
            
        elif self.luigi_health > 50:
            # Battle expression
            if self.timer % 30 < 15:  # Make mouth animate for shouting
                # Open mouth shouting
                pygame.draw.ellipse(screen, (0, 0, 0), (self.luigi_x + 18, self.luigi_y - 8, 14, 12))
                pygame.draw.ellipse(screen, (150, 0, 0), (self.luigi_x + 20, self.luigi_y - 6, 10, 8))  # Tongue
            else:
                # Determined mouth
                pygame.draw.line(screen, (0, 0, 0), (self.luigi_x + 15, self.luigi_y - 5),
                               (self.luigi_x + 35, self.luigi_y - 5), 3)
            # Intense eyebrows
            pygame.draw.line(screen, MARIO_BROWN, (self.luigi_x + 15, self.luigi_y - 22),
                           (self.luigi_x + 22, self.luigi_y - 24), 3)
            pygame.draw.line(screen, MARIO_BROWN, (self.luigi_x + 28, self.luigi_y - 24),
                           (self.luigi_x + 35, self.luigi_y - 22), 3)
            
        else:
            # Devastated expression
            # Sad eyebrows
            pygame.draw.line(screen, MARIO_BROWN, (self.luigi_x + 15, self.luigi_y - 18),
                           (self.luigi_x + 22, self.luigi_y - 23), 2)
            pygame.draw.line(screen, MARIO_BROWN, (self.luigi_x + 28, self.luigi_y - 23),
                           (self.luigi_x + 35, self.luigi_y - 18), 2)
            # Trembling mouth (animated)
            mouth_offset = math.sin(self.timer * 0.5) * 2
            pygame.draw.arc(screen, (0, 0, 0),
                          (self.luigi_x + 20, self.luigi_y - 8 + mouth_offset, 10, 8),
                          math.pi, 2*math.pi, 2)
            # Tears
            if self.timer % 15 < 8:
                pygame.draw.line(screen, (100, 149, 237), 
                               (self.luigi_x + 18, self.luigi_y - 15),
                               (self.luigi_x + 18, self.luigi_y - 5), 2)
                pygame.draw.line(screen, (100, 149, 237),
                               (self.luigi_x + 32, self.luigi_y - 15),
                               (self.luigi_x + 32, self.luigi_y - 5), 2)
        
        # Draw battle effects
        for effect in self.battle_effects:
            effect_type = effect.get('type')
            if effect_type == 'flame_trail':
                # Draw flame trail with gradient
                alpha_surface = pygame.Surface((effect['size']*2, effect['size']*2), pygame.SRCALPHA)
                pygame.draw.circle(alpha_surface, (*effect['color'], 150),
                                 (effect['size'], effect['size']), effect['size'])
                screen.blit(alpha_surface, 
                           (int(effect['x'])-effect['size'],
                            int(effect['y'])-effect['size']))
            elif effect_type == 'lightning':
                # Draw lightning with glow effect
                glow_size = effect['size'] + 4
                # Outer glow
                pygame.draw.circle(screen, (200, 255, 200),
                                 (int(effect['x']), int(effect['y'])),
                                 glow_size)
                # Inner bright core
                pygame.draw.circle(screen, (255, 255, 255),
                                 (int(effect['x']), int(effect['y'])),
                                 effect['size'])
            elif effect_type == 'lightning_impact':
                # Draw lightning impact with expanding ring
                ring_size = effect['size'] + (10 - effect['timer']) * 2
                pygame.draw.circle(screen, effect['color'],
                                 (int(effect['x']), int(effect['y'])),
                                 ring_size, 2)
                # Add center glow
                pygame.draw.circle(screen, (255, 255, 255),
                                 (int(effect['x']), int(effect['y'])),
                                 effect['size'] // 2)
            else:
                # Draw regular effects
                pygame.draw.circle(screen, effect['color'],
                                 (int(effect['x']), int(effect['y'])),
                                 effect['size'])
        
        # Draw fireballs with flame core
        for fireball in self.fireballs:
            # Draw outer glow
            for i, color in enumerate(fireball['color']):
                size = fireball['size'] - i * 3
                if size > 0:
                    pygame.draw.circle(screen, color,
                                     (int(fireball['x']), int(fireball['y'])),
                                     size)
            # Add white hot center
            pygame.draw.circle(screen, (255, 255, 200),
                             (int(fireball['x']), int(fireball['y'])),
                             fireball['size'] // 3)
        
        # Draw Flappy Bird
        bird.draw()

class WinningCutscene:
    def __init__(self):
        self.phase = 0  # Animation phase
        self.mario_health = 100
        self.flappy_health = 100
        self.mario_x = SCREEN_WIDTH
        self.mario_y = SCREEN_HEIGHT // 2
        self.flappy_original_pos = None
        self.flash_timer = 0
        self.battle_effects = []
        self.fireballs = []  # List to store active fireballs
        self.winner = None
        self.dialogue_timer = 0
        self.current_dialogue = ""
        self.dialogue_phase = 0
        self.countdown = 3
        self.countdown_start = False
        self.effect_timer = 0  # Timer for special effects
        self.dialogues = [
            "Mario: So, you're the one causing trouble in these pipes!",
            "Flappy: ...",
            "Mario: Not much of a talker, huh? Let's see how you handle this!",
            "Flappy: *Angry bird noises*",
            "Mario: Mama mia! You're stronger than you look!",
            "Flappy: *Determined chirp*",
            "Mario: Is that all you've got?!",
            "Flappy: *INTENSE BATTLE CRY*",
            "Mario: No... This can't be... IMPOSSIBLE!",
            "Flappy: *Victorious chirp*"        
        ]
        
    def start(self, flappy_pos):
        self.flappy_original_pos = flappy_pos
        self.phase = 0
        self.timer = 0
        self.mario_x = SCREEN_WIDTH
        self.mario_health = 100
        self.flappy_health = 100
        self.winner = None
        self.battle_effects = []
        
    def add_battle_effect(self, x, y, color, effect_type=None):
        self.battle_effects.append({
            'x': x,
            'y': y,
            'color': color,
            'size': 20,
            'timer': 10,
            'type': effect_type
        })
        
    def update(self):
        self.timer += 1
        self.dialogue_timer += 1
        
        # Handle countdown after victory
        if self.countdown_start:
            if self.timer % 60 == 0:  # Every second
                self.countdown -= 1
                if self.countdown < 0:
                    return True  # Signal to resume game
        
        # Update battle effects
        for effect in self.battle_effects[:]:  # Copy list to safely remove items
            effect['timer'] -= 1
            effect['size'] -= 1
            if effect['timer'] <= 0:
                self.battle_effects.remove(effect)
        
        # Phase 0: Mario enters from right
        if self.phase == 0:
            self.mario_x -= 5
            if self.mario_x <= SCREEN_WIDTH - 100:
                self.phase = 1
                self.current_dialogue = self.dialogues[0]
                self.dialogue_phase = 1
                self.dialogue_timer = 0
                
        # Phase 1: Battle sequence
        elif self.phase == 1:
            # Attack sequence
            if self.timer % 120 == 0:  # Attack every 2 seconds
                # Flappy attacks Mario (stronger)
                damage = random.randint(15, 25)
                self.mario_health -= damage
                self.add_battle_effect(self.mario_x + 25, self.mario_y, (255, 255, 0))
                
                # Mario attacks Flappy with fireballs
                if random.random() > 0.3:  # 30% chance to miss
                    damage = random.randint(5, 10)
                    self.flappy_health -= damage
                    # Add multiple fireballs in a spread pattern
                    for _ in range(3):
                        self.add_battle_effect(
                            self.mario_x + 25,
                            self.mario_y,
                            (255, 0, 0),
                            'fireball'
                        )
                    # Add impact effects
                    for _ in range(5):
                        self.add_battle_effect(
                            self.flappy_original_pos[0] + random.randint(-20, 20),
                            self.flappy_original_pos[1] + random.randint(-20, 20),
                            (255, 100, 0),
                            'impact'
                        )
                # After attack, show next dialogue
                if self.dialogue_phase < len(self.dialogues) - 1:
                    self.dialogue_phase += 1
                    self.current_dialogue = self.dialogues[self.dialogue_phase]
                    self.dialogue_timer = 0
                
                # Make sure Flappy always wins
                if self.mario_health <= 0:
                    self.winner = "flappy"
                    self.phase = 2
                    self.current_dialogue = self.dialogues[-1]  # Victory dialogue
                    
        # Phase 2: Victory animation
        elif self.phase == 2:
            self.flash_timer += 1
            if self.flash_timer >= 120:  # After 2 seconds of flashing
                self.countdown_start = True  # Start countdown
            if self.flash_timer >= 60:  # After 1 second of victory animation
                return True  # Cutscene complete
                
        return False
        
    def draw(self, screen, bird):
        # Draw countdown if active
        if self.countdown_start and self.countdown >= 0:
            font = pygame.font.Font(None, 74)
            countdown_text = str(self.countdown) if self.countdown > 0 else "GO!"
            text = font.render(countdown_text, True, (255, 0, 0))
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
            return
            
        # Draw dialogue box and text
        if self.current_dialogue:
            # Draw semi-transparent dialogue box
            dialogue_surface = pygame.Surface((SCREEN_WIDTH - 40, 80))
            dialogue_surface.fill((255, 255, 255))
            dialogue_surface.set_alpha(200)
            screen.blit(dialogue_surface, (20, SCREEN_HEIGHT - 100))
            
            # Draw dialogue text
            font = pygame.font.Font(None, 32)
            text = font.render(self.current_dialogue, True, (0, 0, 0))
            screen.blit(text, (30, SCREEN_HEIGHT - 80))
        
        # Draw health bars with labels
        font = pygame.font.Font(None, 24)
        flappy_label = font.render("Flappy", True, (0, 0, 0))
        mario_label = font.render("Mario", True, (0, 0, 0))
        
        # Draw health bars
        pygame.draw.rect(screen, (255, 0, 0), (10, 10, 100, 20))  # Red background
        pygame.draw.rect(screen, (0, 255, 0), (10, 10, self.flappy_health, 20))  # Green health
        screen.blit(flappy_label, (10, 35))
        
        pygame.draw.rect(screen, (255, 0, 0), (SCREEN_WIDTH - 110, 10, 100, 20))  # Red background
        pygame.draw.rect(screen, (0, 255, 0), (SCREEN_WIDTH - 110, 10, self.mario_health, 20))  # Green health
        screen.blit(mario_label, (SCREEN_WIDTH - 110, 35))
        
        # Draw Mario with enhanced face
        # Hat
        pygame.draw.rect(screen, MARIO_RED, (self.mario_x, self.mario_y - 35, 50, 15))  # Main hat
        pygame.draw.ellipse(screen, MARIO_RED, (self.mario_x - 5, self.mario_y - 25, 60, 12))  # Hat brim
        # M emblem on hat
        pygame.draw.rect(screen, WHITE, (self.mario_x + 20, self.mario_y - 32, 12, 10))  # M background
        pygame.draw.line(screen, MARIO_RED, (self.mario_x + 22, self.mario_y - 30),
                        (self.mario_x + 26, self.mario_y - 24), 2)  # M left
        pygame.draw.line(screen, MARIO_RED, (self.mario_x + 26, self.mario_y - 24),
                        (self.mario_x + 30, self.mario_y - 30), 2)  # M right
        
        # Head (more oval shaped)
        pygame.draw.ellipse(screen, MARIO_SKIN, (self.mario_x + 10, self.mario_y - 25, 30, 35))
        
        # Hair
        for i in range(3):  # Multiple hair strands
            pygame.draw.arc(screen, MARIO_BROWN, 
                          (self.mario_x + 8 + i*10, self.mario_y - 25, 10, 10),
                          math.pi, 2*math.pi, 2)
        
        # Eyes with more detail
        # Eye whites
        pygame.draw.ellipse(screen, WHITE, (self.mario_x + 15, self.mario_y - 20, 8, 10))  # Left eye
        pygame.draw.ellipse(screen, WHITE, (self.mario_x + 27, self.mario_y - 20, 8, 10))  # Right eye
        # Pupils
        pygame.draw.ellipse(screen, (0, 0, 150), (self.mario_x + 17, self.mario_y - 18, 4, 6))  # Left pupil
        pygame.draw.ellipse(screen, (0, 0, 150), (self.mario_x + 29, self.mario_y - 18, 4, 6))  # Right pupil
        # Eye highlights
        pygame.draw.circle(screen, WHITE, (self.mario_x + 18, self.mario_y - 17), 1)  # Left highlight
        pygame.draw.circle(screen, WHITE, (self.mario_x + 30, self.mario_y - 17), 1)  # Right highlight
        
        # Enhanced nose
        pygame.draw.ellipse(screen, (200, 120, 80), (self.mario_x + 22, self.mario_y - 15, 8, 12))
        
        # Enhanced mustache
        pygame.draw.arc(screen, MARIO_BROWN, (self.mario_x + 12, self.mario_y - 10, 20, 12), 0, math.pi, 3)  # Left side
        pygame.draw.arc(screen, MARIO_BROWN, (self.mario_x + 18, self.mario_y - 10, 20, 12), 0, math.pi, 3)  # Right side
        
        # Shirt and overalls
        pygame.draw.rect(screen, MARIO_RED, (self.mario_x + 5, self.mario_y, 40, 30))  # Shirt
        pygame.draw.rect(screen, MARIO_BLUE, (self.mario_x + 10, self.mario_y + 10, 30, 20))  # Overalls
        # Overall straps
        pygame.draw.rect(screen, MARIO_BLUE, (self.mario_x + 12, self.mario_y, 5, 15))  # Left strap
        pygame.draw.rect(screen, MARIO_BLUE, (self.mario_x + 33, self.mario_y, 5, 15))  # Right strap
        # Buttons
        pygame.draw.circle(screen, YELLOW, (self.mario_x + 15, self.mario_y + 12), 3)  # Left button
        pygame.draw.circle(screen, YELLOW, (self.mario_x + 35, self.mario_y + 12), 3)  # Right button
        
        # Expression based on health (more detailed)
        if self.mario_health > 70:
            # Happy mouth with teeth
            pygame.draw.arc(screen, (0, 0, 0), (self.mario_x + 15, self.mario_y - 8, 20, 15), 0, math.pi, 2)
            pygame.draw.rect(screen, WHITE, (self.mario_x + 18, self.mario_y - 8, 14, 3))  # Teeth
        elif self.mario_health > 30:
            # Determined expression
            pygame.draw.line(screen, (0, 0, 0), (self.mario_x + 15, self.mario_y - 5),
                           (self.mario_x + 35, self.mario_y - 5), 3)
            # Furrowed brows
            pygame.draw.line(screen, MARIO_BROWN, (self.mario_x + 15, self.mario_y - 22),
                           (self.mario_x + 22, self.mario_y - 20), 2)
            pygame.draw.line(screen, MARIO_BROWN, (self.mario_x + 28, self.mario_y - 20),
                           (self.mario_x + 35, self.mario_y - 22), 2)
        else:
            # Worried expression with open mouth
            pygame.draw.ellipse(screen, (0, 0, 0), (self.mario_x + 20, self.mario_y - 8, 10, 8))
            pygame.draw.ellipse(screen, (150, 0, 0), (self.mario_x + 22, self.mario_y - 6, 6, 4))  # Tongue
            # Worried eyebrows
            pygame.draw.line(screen, MARIO_BROWN, (self.mario_x + 15, self.mario_y - 20),
                           (self.mario_x + 22, self.mario_y - 23), 2)
            pygame.draw.line(screen, MARIO_BROWN, (self.mario_x + 28, self.mario_y - 23),
                           (self.mario_x + 35, self.mario_y - 20), 2)
        
        # Draw Flappy Bird (use existing bird sprite)
        bird.draw()
        
        # Draw battle effects
        for effect in self.battle_effects:
            pygame.draw.circle(screen, effect['color'], (int(effect['x']), int(effect['y'])), effect['size'])
        
        # Draw victory flash
        if self.phase == 2:
            if self.flash_timer % 10 < 5:  # Flash every 5 frames
                flash_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                flash_surface.fill((255, 255, 255))
                flash_surface.set_alpha(100)
                screen.blit(flash_surface, (0, 0))
                
            # Draw winner text
            font = pygame.font.Font(None, 74)
            if self.winner == "flappy":
                text = font.render("FLAPPY WINS!", True, (255, 255, 0))
            else:
                text = font.render("MARIO WINS!", True, MARIO_RED)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)

class Leaderboard:
    def __init__(self):
        self.scores = []
        self.load_scores()
        # Initialize previous_top_score and previous_top_name safely
        self.previous_top_score = self.get_top_score()
        self.previous_top_name = self.get_top_name()
        self.beat_message_active = False
        self.beat_message_timer = 0
        self.beat_message_duration = 180  # 3 seconds at 60 FPS
        self.beat_message_scale = 1.0
        self.beat_message_growing = True

    def load_scores(self):
        try:
            if os.path.exists(LEADERBOARD_FILE):
                with open(LEADERBOARD_FILE, 'r') as f:
                    self.scores = json.load(f)
            else:
                # Create empty leaderboard file if it doesn't exist
                self.scores = []
                self.save_scores()
        except Exception as e:
            print(f"Error loading leaderboard: {e}")
            self.scores = []

    def save_scores(self):
        with open(LEADERBOARD_FILE, 'w') as f:
            json.dump(self.scores, f)

    def add_score(self, name, score):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.scores.append({
            'name': name,
            'score': score,
            'date': current_time
        })
        # Sort by score in descending order
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        # Keep only top scores
        self.scores = self.scores[:MAX_LEADERBOARD_ENTRIES]
        self.save_scores()

    def get_top_score(self):
        return self.scores[0]['score'] if self.scores else 0

    def get_top_name(self):
        return self.scores[0]['name'] if self.scores else ""

    def is_high_score(self, score):
        if not self.scores:
            return True
        return len(self.scores) < MAX_LEADERBOARD_ENTRIES or score > self.scores[-1]['score']

    def check_beat_previous_leader(self, current_score):
        if current_score > self.previous_top_score and self.previous_top_score > 0:
            self.beat_message_active = True
            self.beat_message_timer = 0
            self.beat_message_scale = 1.0
            self.beat_message_growing = True
            return True
        return False

    def update_beat_message(self):
        if self.beat_message_active:
            self.beat_message_timer += 1
            # Scale animation
            if self.beat_message_growing:
                self.beat_message_scale += 0.02
                if self.beat_message_scale >= 1.2:
                    self.beat_message_growing = False
            else:
                self.beat_message_scale -= 0.02
                if self.beat_message_scale <= 1.0:
                    self.beat_message_growing = True

            if self.beat_message_timer >= self.beat_message_duration:
                self.beat_message_active = False

    def draw_beat_message(self, screen):
        if self.beat_message_active:
            font = pygame.font.Font(None, 36)
            message = f"You just beat {self.previous_top_name}'s score of {self.previous_top_score}!"
            
            # Create text with scaling
            text = font.render(message, True, (255, 215, 0))  # Gold color
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, 100))
            
            # Apply scaling
            scaled_text = pygame.transform.scale(text, 
                (int(text.get_width() * self.beat_message_scale), 
                 int(text.get_height() * self.beat_message_scale)))
            scaled_rect = scaled_text.get_rect(center=(SCREEN_WIDTH//2, 100))
            
            screen.blit(scaled_text, scaled_rect)

    def draw_leaderboard(self, screen):
        font = pygame.font.Font(None, 36)
        title = font.render("LEADERBOARD", True, BLACK)
        screen.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))

        y_offset = 100
        for i, entry in enumerate(self.scores[:5]):  # Show top 5
            text = f"{i+1}. {entry['name']} - {entry['score']}"
            score_text = font.render(text, True, BLACK)
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, y_offset))
            y_offset += 40

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.power_type = power_type
        self.collected = False
        self.animation_frame = 0
        self.glow_phase = 0
        self.glow_speed = 0.1

    def update(self):
        if not self.collected:
            self.animation_frame += 1
            self.glow_phase = (self.glow_phase + self.glow_speed) % (2 * math.pi)
            self.x -= BASE_PIPE_SPEED  # Move with the same speed as pipes

    def draw(self):
        if not self.collected:
            # Draw power-up icon based on type
            if self.power_type == 'shield':
                # Draw shield with glow effect
                glow_intensity = 0.5 + 0.5 * math.sin(self.glow_phase)
                glow_color = (
                    int(SHIELD_GLOW[0] * glow_intensity),
                    int(SHIELD_GLOW[1] * glow_intensity),
                    int(SHIELD_GLOW[2] * glow_intensity)
                )
                
                # Draw outer glow
                pygame.draw.circle(screen, glow_color, 
                                 (int(self.x + self.width/2), int(self.y + self.height/2)),
                                 self.width//2 + 5)
                
                # Draw shield
                pygame.draw.circle(screen, SHIELD_COLOR,
                                 (int(self.x + self.width/2), int(self.y + self.height/2)),
                                 self.width//2)
                
                # Draw shield symbol
                pygame.draw.arc(screen, WHITE,
                              (self.x + 5, self.y + 5, self.width - 10, self.height - 10),
                              0, math.pi, 3)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.speed = BASE_PIPE_SPEED
        self.animation_frame = 0
        self.glow_phase = 0
        self.glow_speed = 0.1

    def update(self):
        self.x -= self.speed
        self.animation_frame += 1
        self.glow_phase = (self.glow_phase + self.glow_speed) % (2 * math.pi)

    def draw(self):
        # Draw enemy with glow effect
        glow_intensity = 0.5 + 0.5 * math.sin(self.glow_phase)
        glow_color = (
            int(ENEMY_COLOR[0] * glow_intensity),
            int(ENEMY_COLOR[1] * glow_intensity),
            int(ENEMY_COLOR[2] * glow_intensity)
        )
        
        # Draw outer glow
        pygame.draw.circle(screen, glow_color, 
                         (int(self.x + self.width/2), int(self.y + self.height/2)),
                         self.width//2 + 5)
        
        # Draw enemy body
        pygame.draw.circle(screen, ENEMY_COLOR,
                         (int(self.x + self.width/2), int(self.y + self.height/2)),
                         self.width//2)
        
        # Draw enemy eyes
        eye_offset = 5
        pygame.draw.circle(screen, WHITE,
                         (int(self.x + self.width/2 - eye_offset), int(self.y + self.height/2 - eye_offset)), 3)
        pygame.draw.circle(screen, WHITE,
                         (int(self.x + self.width/2 + eye_offset), int(self.y + self.height/2 - eye_offset)), 3)
        
        # Draw enemy pupils
        pygame.draw.circle(screen, BLACK,
                         (int(self.x + self.width/2 - eye_offset), int(self.y + self.height/2 - eye_offset)), 1)
        pygame.draw.circle(screen, BLACK,
                         (int(self.x + self.width/2 + eye_offset), int(self.y + self.height/2 - eye_offset)), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Fireball:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 20
        self.height = 20
        self.speed = FIREBALL_SPEED
        self.animation_frame = 0
        self.glow_phase = 0
        self.glow_speed = 0.2

    def update(self):
        self.x += self.speed
        self.animation_frame += 1
        self.glow_phase = (self.glow_phase + self.glow_speed) % (2 * math.pi)

    def draw(self):
        # Draw fireball with glow effect
        glow_intensity = 0.5 + 0.5 * math.sin(self.glow_phase)
        glow_color = (
            int(FIREBALL_COLOR[0] * glow_intensity),
            int(FIREBALL_COLOR[1] * glow_intensity),
            int(FIREBALL_COLOR[2] * glow_intensity)
        )
        
        # Draw outer glow
        pygame.draw.circle(screen, glow_color, 
                         (int(self.x + self.width/2), int(self.y + self.height/2)),
                         self.width//2 + 3)
        
        # Draw fireball body
        pygame.draw.circle(screen, FIREBALL_COLOR,
                         (int(self.x + self.width/2), int(self.y + self.height/2)),
                         self.width//2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

def check_collision(bird, pipes):
    bird_rect = bird.get_rect()
    
    # Check collision with screen boundaries
    if bird.y <= 0 or bird.y + bird.height >= SCREEN_HEIGHT:
        if not bird.shield_active:  # Only trigger collision if shield is not active
            print("Collision with screen boundary")
            if collision_sound:
                collision_sound.play()
            return True
    
    # Check collision with pipes
    for pipe in pipes:
        if (bird_rect.colliderect(pipe.get_top_rect()) or 
            bird_rect.colliderect(pipe.get_bottom_rect())):
            if not bird.shield_active:  # Only trigger collision if shield is not active
                print("Collision with pipe")
                bird.target_pipe = pipe
                # Stop all pipes when collision occurs
                for p in pipes:
                    p.is_moving = False
                if collision_sound:
                    collision_sound.play()
                return True
    
    return False

def draw_score(score, speed_level):
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, BLACK)
    score_rect = score_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
    screen.blit(score_text, score_rect)
    
    # Draw speed level
    speed_text = font.render(f"Speed: {speed_level}x", True, BLACK)
    speed_rect = speed_text.get_rect(topright=(SCREEN_WIDTH - 10, 50))
    screen.blit(speed_text, speed_rect)

    # Show/hide Donkey Kong based on score
    if score > 20:
        donkey_kong.show()
    else:
        donkey_kong.hide()

    # Show power effect indicator if active
    for pipe in pipes:
        if pipe.power_effect_active:
            power_text = font.render("POWER MODE!", True, POWER_PIPE_COLOR)
            power_rect = power_text.get_rect(center=(SCREEN_WIDTH//2, 30))
            screen.blit(power_text, power_rect)
            break

def calculate_pipe_speed(score):
    speed_level = score // 10
    # Instead of doubling, add 0.25 for each level
    speed_increase = 0.25 * speed_level
    return BASE_PIPE_SPEED + speed_increase, speed_level

# Initialize game objects
bird = Bird()
pipes = []
cityscape = Cityscape()
donkey_kong = DonkeyKong()
weather_system = WeatherSystem()
leaderboard = Leaderboard()
winning_cutscene = WinningCutscene()
death_cutscene = DeathCutscene(screen)
luigi_battle = LuigiBattle()
game_state = GAME_STATE_START
countdown_start = 0  # For tracking countdown timer
last_pipe_time = 0
score = 0
current_pipe_speed, speed_level = calculate_pipe_speed(score)
player_name = ""
name_input_active = False
power_ups = []
enemies = []  # Add enemies list
fireballs = []  # Add fireballs list

# Main game loop
while True:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if game_state == GAME_STATE_NAME_ENTRY:
                if event.key == pygame.K_RETURN:
                    if player_name and player_name.strip():
                        leaderboard.add_score(player_name, score)
                        game_state = GAME_STATE_LEADERBOARD
                    else:
                        game_state = GAME_STATE_START
                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]
                elif len(player_name) < 10 and event.unicode.isalnum():
                    player_name += event.unicode
            elif event.key == pygame.K_SPACE:
                if game_state == GAME_STATE_START:
                    game_state = GAME_STATE_PLAYING
                    score = 0
                    current_pipe_speed, speed_level = calculate_pipe_speed(score)
                elif game_state == GAME_STATE_OVER:
                    game_state = GAME_STATE_START
                    bird = Bird()
                    pipes = []
                    enemies = []  # Reset enemies
                    fireballs = []  # Reset fireballs
                    last_pipe_time = current_time
                    score = 0
                    current_pipe_speed, speed_level = calculate_pipe_speed(score)
                elif game_state == GAME_STATE_LEADERBOARD:
                    game_state = GAME_STATE_START
                    bird = Bird()
                    pipes = []
                    enemies = []  # Reset enemies
                    fireballs = []  # Reset fireballs
                    last_pipe_time = current_time
                    score = 0
                    current_pipe_speed, speed_level = calculate_pipe_speed(score)
                elif game_state == GAME_STATE_PLAYING:
                    bird.jump()
            elif event.key == pygame.K_a and game_state == GAME_STATE_PLAYING:
                # Shoot fireball
                fireballs.append(Fireball(bird.x + bird.width, bird.y + bird.height/2))

# ... (rest of the code remains the same)
    # Clear screen
    screen.fill(WHITE)

    # Update and draw based on game state
    if game_state == GAME_STATE_PLAYING:
        # Update bird position
        bird.update()
        cityscape.draw()
        
        bird.update()
        bird.draw()

        # Update and draw Donkey Kong
        donkey_kong.update()
        donkey_kong.draw()

        # Spawn new pipes
        if current_time - last_pipe_time > PIPE_SPAWN_INTERVAL:
            new_pipe = Pipe(current_pipe_speed)
            pipes.append(new_pipe)
            
            # Try to spawn power-up in the pipe gap
            if random.random() < POWER_UP_SPAWN_CHANCE:
                # Calculate position in the middle of the pipe gap
                power_up_y = new_pipe.top_height + (new_pipe.gap // 2)
                power_ups.append(PowerUp(new_pipe.x + new_pipe.width//2 - 15,  # Center horizontally
                                       power_up_y,
                                       'shield'))
            
            # Try to spawn enemy in the pipe gap
            if random.random() < ENEMY_SPAWN_CHANCE:
                # Calculate position in the middle of the pipe gap
                enemy_y = new_pipe.top_height + (new_pipe.gap // 2)
                enemies.append(Enemy(new_pipe.x + new_pipe.width//2 - 15,  # Center horizontally
                                   enemy_y))
            
            last_pipe_time = current_time

        # Update and draw pipes
        for pipe in pipes[:]:
            pipe.update()
            pipe.draw()
            
            # Check if bird passed the pipe
            if not pipe.scored and pipe.x + pipe.width < bird.x:
                score += 1
                pipe.scored = True
                
                # Check for cutscene triggers
                if score == 10:  # Mario battle at 10 points
                    game_state = GAME_STATE_WINNING
                    winning_cutscene = WinningCutscene()
                    winning_cutscene.start((bird.x, bird.y))
                    print("Starting Mario battle!")
                elif score == 30:  # Luigi battle at 30 points
                    game_state = GAME_STATE_LUIGI_BATTLE
                    luigi_battle = LuigiBattle()
                    luigi_battle.start((bird.x, bird.y))
                    print("Starting Luigi battle!")
                
                # Check if it's a power pipe
                if pipe.is_power_pipe and not pipe.power_effect_active:
                    score += 2  # Bonus points
                    pipe.power_effect_active = True
                    # Slow down all pipes temporarily
                    for p in pipes:
                        if p.is_moving:
                            p.speed = max(1, p.speed * 0.5)  # Reduce speed by half, minimum 1
                    if power_pipe_sound:
                        power_pipe_sound.play()
                else:
                    if score_sound:
                        score_sound.play()
                
                # Update pipe speed based on new score
                current_pipe_speed, speed_level = calculate_pipe_speed(score)
                # Update speed of all moving pipes that aren't in power mode
                for p in pipes:
                    if p.is_moving and not p.power_effect_active:
                        p.speed = current_pipe_speed
            
            # Remove pipes that are off screen
            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)

        # Update and draw power-ups
        for power_up in power_ups[:]:
            power_up.update()
            power_up.draw()
            
            # Check collision with bird
            if power_up.get_rect().colliderect(bird.get_rect()):
                if power_up.power_type == 'shield':
                    bird.activate_shield()
                power_up.collected = True
                power_ups.remove(power_up)
            
            # Remove power-ups that are off screen
            if power_up.x + power_up.width < 0:
                power_ups.remove(power_up)

        # Update and draw enemies
        for enemy in enemies[:]:
            enemy.update()
            enemy.draw()
            
            # Check collision with bird
            if enemy.get_rect().colliderect(bird.get_rect()):
                if not bird.shield_active:  # Only trigger collision if shield is not active
                    game_state = GAME_STATE_OVER
                    break
            
            # Remove enemies that are off screen
            if enemy.x + enemy.width < 0:
                enemies.remove(enemy)

        # Update and draw fireballs
        for fireball in fireballs[:]:
            fireball.update()
            fireball.draw()
            
            # Check collision with enemies
            for enemy in enemies[:]:
                if fireball.get_rect().colliderect(enemy.get_rect()):
                    enemies.remove(enemy)
                    fireballs.remove(fireball)
                    score += 2  # Bonus points for destroying an enemy
                    if score_sound:
                        score_sound.play()
                    break
            
            # Remove fireballs that are off screen
            if fireball.x > SCREEN_WIDTH:
                fireballs.remove(fireball)

        # Draw score and speed
        draw_score(score, speed_level)

        # Check for collisions
        if check_collision(bird, pipes):
            game_state = GAME_STATE_OVER

        # Check if player beat previous leader
        if leaderboard.check_beat_previous_leader(score):
            if score_sound:
                score_sound.play()  # Play special sound for beating record
        
        # Update and draw beat message
        leaderboard.update_beat_message()
        leaderboard.draw_beat_message(screen)

    elif game_state == GAME_STATE_OVER:
        if not death_cutscene.is_active:
            death_cutscene.start((bird.x, bird.y))
        if not death_cutscene.update():
            game_state = GAME_STATE_OVER
            if game_over_sound:
                game_over_sound.play()
        # Draw cityscape (no update to keep it stationary)
        cityscape.draw()
        
        # Update sucking animation
        if bird.update_sucking():
            game_state = GAME_STATE_OVER
            if game_over_sound:
                game_over_sound.play()
        bird.draw()
        
        # Draw pipes (they won't move anymore)
        for pipe in pipes:
            pipe.draw()
        
        # Draw score and speed
        draw_score(score, speed_level)

    elif game_state == GAME_STATE_START:
        # Draw background
        cityscape.draw()
        
        # Draw start screen
        bird.draw()
        font = pygame.font.Font(None, 36)
        text = font.render("Press SPACE to Start", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)

    elif game_state == GAME_STATE_OVER:
        print("In OVER state")
        # Draw cityscape (no update to keep it stationary)
        cityscape.draw()
        
        # Draw game over screen
        font = pygame.font.Font(None, 36)
        text = font.render("Game Over! Press SPACE", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)
        
        # Draw final score and speed
        draw_score(score, speed_level)

        # Check if score is high enough for leaderboard
        if score > 0 and leaderboard.is_high_score(score):
            game_state = GAME_STATE_NAME_ENTRY
            name_input_active = True
            player_name = ""
        else:
            # If not a high score, show leaderboard directly
            game_state = GAME_STATE_LEADERBOARD

    elif game_state == GAME_STATE_NAME_ENTRY:
        # Draw background
        cityscape.draw()
        
        # Draw name entry prompt
        font = pygame.font.Font(None, 36)
        prompt = font.render("Enter your name (3-10 chars):", True, BLACK)
        screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 - 50))
        
        # Draw name input box with cursor
        pygame.draw.rect(screen, BLACK, NAME_INPUT_BOX, 2)
        
        # Draw the current name
        name_text = font.render(player_name, True, BLACK)
        screen.blit(name_text, (NAME_INPUT_BOX.x + 5, NAME_INPUT_BOX.y + 5))
        
        # Draw cursor (blinking)
        if pygame.time.get_ticks() % 1000 < 500:  # Blink every 500ms
            cursor_x = NAME_INPUT_BOX.x + 5 + name_text.get_width()
            pygame.draw.line(screen, BLACK, 
                            (cursor_x, NAME_INPUT_BOX.y + 5),
                            (cursor_x, NAME_INPUT_BOX.y + NAME_INPUT_BOX.height - 5), 2)
        
        # Draw submit button
        submit_text = font.render("Press ENTER to submit", True, BLACK)
        screen.blit(submit_text, (SCREEN_WIDTH//2 - submit_text.get_width()//2, 
                                SCREEN_HEIGHT//2 + 60))

    elif game_state == GAME_STATE_WINNING:
        if winning_cutscene.update():
            game_state = GAME_STATE_COUNTDOWN
            countdown_start = pygame.time.get_ticks()
            print("Mario battle complete! Starting 3-second countdown...")
            # Add bonus points for beating Mario
            score += 5
            print(f"Bonus points awarded! New score: {score}")
        # Draw background
        cityscape.draw()
        
        # Draw winning cutscene
        winning_cutscene.draw(screen, bird)

    elif game_state == GAME_STATE_LUIGI_BATTLE:
        if luigi_battle.update():
            game_state = GAME_STATE_COUNTDOWN
            countdown_start = pygame.time.get_ticks()
            print("Luigi battle complete! Starting 3-second countdown...")
            # Add bonus points for beating Luigi
            score += 10
            print(f"Bonus points awarded! New score: {score}")
        
        # Draw background
        cityscape.draw()
        
        # Draw Luigi battle
        luigi_battle.draw(screen, bird)

    elif game_state == GAME_STATE_LEADERBOARD:
        # Draw background
        cityscape.draw()
        
        # Draw leaderboard
        leaderboard.draw_leaderboard(screen)
        
        # Draw continue prompt
        font = pygame.font.Font(None, 36)
        continue_text = font.render("Press SPACE to continue", True, BLACK)
        screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, 
                                  SCREEN_HEIGHT - 50))

    elif game_state == GAME_STATE_COUNTDOWN:
        # Draw background
        cityscape.draw()
        bird.draw()
        
        # Calculate remaining countdown time
        elapsed = (pygame.time.get_ticks() - countdown_start) // 1000  # Convert to seconds
        remaining = 3 - elapsed
        
        if remaining > 0:
            # Draw countdown number
            font = pygame.font.Font(None, 72)
            text = font.render(str(remaining), True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
        else:
            # Countdown finished
            if game_state == GAME_STATE_COUNTDOWN:
                # Reset game objects but keep score
                bird = Bird()
                pipes = []
                enemies = []
                fireballs = []
                power_ups = []
                current_pipe_speed, speed_level = calculate_pipe_speed(score)
                game_state = GAME_STATE_PLAYING
                print(f"Countdown complete! Restarting with score {score}...")

    # Update weather
    weather_system.update()
    weather_system.draw()

    # Update display
    pygame.display.flip()
    clock.tick(FPS) 