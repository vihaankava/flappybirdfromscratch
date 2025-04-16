import pygame
import sys
import random
import os
import math

# Initialize Pygame
pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound effects

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
PIPE_SPAWN_INTERVAL = 1500  # milliseconds
FALL_SPEED = 8  # Increased from 3 to 8 for faster falling
BASE_PIPE_SPEED = 3  # Initial pipe speed
BACKGROUND_SPEED = 0.5  # Speed of background movement

# Load sound effects
try:
    jump_sound = pygame.mixer.Sound('sounds/jump.wav')
    score_sound = pygame.mixer.Sound('sounds/score.wav')
    collision_sound = pygame.mixer.Sound('sounds/collision.wav')
    game_over_sound = pygame.mixer.Sound('sounds/game_over.wav')
    power_pipe_sound = pygame.mixer.Sound('sounds/power_pipe.wav')
except:
    print("Warning: Sound files not found. Game will run without sound effects.")
    jump_sound = None
    score_sound = None
    collision_sound = None
    game_over_sound = None
    power_pipe_sound = None

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0, 128)  # Semi-transparent green (alpha = 128)
PACMAN_YELLOW = (255, 255, 0)  # Bright yellow for Pac-Man
DONKEY_KONG_BROWN = (139, 69, 19)  # Brown color for Donkey Kong
DONKEY_KONG_RED = (255, 0, 0)  # Red color for Donkey Kong's tie
POWER_PIPE_COLOR = (255, 215, 0)  # Gold color for Power Pipes
POWER_PIPE_GLOW = (255, 255, 150)  # Lighter gold for glow effect
BUILDING_COLORS = [
    (100, 100, 100),  # Dark gray
    (120, 120, 120),  # Medium gray
    (140, 140, 140),  # Light gray
    (160, 160, 160),  # Very light gray
]
WINDOW_COLOR = (255, 255, 200)  # Light yellow for windows
LIGHT_COLOR = (255, 255, 150)   # Brighter yellow for lit windows
EMPIRE_STATE_COLOR = (150, 150, 150)  # Special color for Empire State Building

# Set up the game window
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

# Game states
GAME_STATE_START = 0
GAME_STATE_PLAY = 1
GAME_STATE_SUCKING = 2
GAME_STATE_OVER = 3

class Cityscape:
    def __init__(self):
        self.buildings = []
        self.generate_buildings()
        
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
                    'is_empire_state': False
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
            'is_empire_state': True
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
                    'is_lit': is_lit
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
                    'is_lit': is_lit
                })
        
        return windows

    def update(self):
        # Move buildings to the left
        for building in self.buildings:
            building['x'] -= BACKGROUND_SPEED
            
        # Remove buildings that are off screen and add new ones
        if self.buildings[0]['x'] + self.buildings[0]['width'] < 0:
            last_building = self.buildings[-1]
            new_x = last_building['x'] + last_building['width'] + random.randint(10, 30)
            
            # 5% chance to generate Empire State Building
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
                    'is_empire_state': False
                })
            self.buildings.pop(0)
            
    def draw(self):
        # Draw buildings
        for building in self.buildings:
            if building['x'] + building['width'] > 0 and building['x'] < SCREEN_WIDTH:
                # Draw building base
                pygame.draw.rect(screen, building['color'], 
                               (building['x'], SCREEN_HEIGHT - building['height'],
                                building['width'], building['height']))
                
                # Draw windows
                for window in building['windows']:
                    window_x = building['x'] + window['x']
                    window_y = SCREEN_HEIGHT - building['height'] + window['y']
                    
                    # Draw window
                    color = LIGHT_COLOR if window['is_lit'] else WINDOW_COLOR
                    pygame.draw.rect(screen, color,
                                   (window_x, window_y,
                                    window['size'], window['size']))
                
                # Add Empire State Building spire
                if building['is_empire_state']:
                    spire_height = 50
                    spire_width = 10
                    pygame.draw.rect(screen, building['color'],
                                   (building['x'] + (building['width'] - spire_width) // 2,
                                    SCREEN_HEIGHT - building['height'] - spire_height,
                                    spire_width, spire_height))

class Bird:
    def __init__(self):
        self.reset()
        self.mouth_angle = 0  # Angle for mouth animation
        self.mouth_opening = True  # Whether mouth is opening or closing
        self.animation_speed = 5  # Speed of mouth animation

    def update(self):
        if game_state == GAME_STATE_PLAY:
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

    def jump(self):
        self.velocity = self.jump_strength
        if jump_sound:
            jump_sound.play()

    def draw(self):
        # Calculate rotation angle based on velocity
        rotation_angle = max(-30, min(30, self.velocity * 3))  # Convert velocity to angle, clamped between -30 and 30 degrees
        
        # Draw Pac-Man body
        pygame.draw.circle(screen, PACMAN_YELLOW, (int(self.x + self.width/2), int(self.y + self.height/2)), self.width//2)
        
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
            y = center[1] - radius * math.sin(angle)  # Subtract because pygame y-axis is inverted
            points.append((int(x), int(y)))
        
        # Draw mouth (black triangle)
        pygame.draw.polygon(screen, BLACK, points)

    def reset(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.width = 30
        self.height = 30
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8
        self.target_pipe = None
        self.is_falling_through = False
        self.mouth_angle = 0
        self.mouth_opening = True

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

class Pipe:
    def __init__(self, speed):
        self.gap = 150
        self.width = 50
        self.x = SCREEN_WIDTH
        self.top_height = random.randint(50, SCREEN_HEIGHT - self.gap - 50)
        self.bottom_y = self.top_height + self.gap
        self.speed = speed
        self.is_moving = True
        self.scored = False  # Track if this pipe has been scored
        self.is_power_pipe = random.random() < 0.2  # 20% chance to be a power pipe
        self.glow_phase = 0
        self.glow_speed = 0.1
        self.power_effect_active = False
        self.power_effect_timer = 0
        self.power_effect_duration = 3000  # 3 seconds

    def update(self):
        if self.is_moving:
            self.x -= self.speed
            
            # Update glow effect for power pipes
            if self.is_power_pipe:
                self.glow_phase = (self.glow_phase + self.glow_speed) % (2 * math.pi)
                
            # Update power effect timer
            if self.power_effect_active:
                self.power_effect_timer += 16  # Assuming 60 FPS
                if self.power_effect_timer >= self.power_effect_duration:
                    self.power_effect_active = False
                    self.power_effect_timer = 0

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
                128  # Semi-transparent
            )
            
            # Draw top pipe with glow
            pygame.draw.rect(pipe_surface, glow_color, 
                           (0, 0, self.width, self.top_height))
            pygame.draw.rect(pipe_surface, POWER_PIPE_COLOR, 
                           (0, 0, self.width, self.top_height))
            
            # Draw bottom pipe with glow
            pygame.draw.rect(pipe_surface, glow_color, 
                           (0, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y))
            pygame.draw.rect(pipe_surface, POWER_PIPE_COLOR, 
                           (0, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y))
        else:
            # Draw regular pipes
            pygame.draw.rect(pipe_surface, GREEN, (0, 0, self.width, self.top_height))
            pygame.draw.rect(pipe_surface, GREEN, 
                           (0, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y))
        
        # Blit the pipe surface onto the screen
        screen.blit(pipe_surface, (self.x, 0))

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

def check_collision(bird, pipes):
    bird_rect = bird.get_rect()
    
    # Check collision with screen boundaries
    if bird.y <= 0 or bird.y + bird.height >= SCREEN_HEIGHT:
        print("Collision with screen boundary")
        if collision_sound:
            collision_sound.play()
        return True
    
    # Check collision with pipes
    for pipe in pipes:
        if bird_rect.colliderect(pipe.get_top_rect()) or bird_rect.colliderect(pipe.get_bottom_rect()):
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
    # Increase speed by 25% for every 10 points
    speed_level = 1 + (score // 10) * 0.25
    return BASE_PIPE_SPEED * speed_level, speed_level

# Initialize game objects
bird = Bird()
pipes = []
cityscape = Cityscape()
donkey_kong = DonkeyKong()  # Add Donkey Kong instance
game_state = GAME_STATE_START
last_pipe_time = 0
score = 0
current_pipe_speed, speed_level = calculate_pipe_speed(score)

# Main game loop
while True:
    current_time = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                if game_state == GAME_STATE_START:
                    print("Starting new game")
                    game_state = GAME_STATE_PLAY
                    score = 0  # Reset score when starting new game
                    current_pipe_speed, speed_level = calculate_pipe_speed(score)
                elif game_state == GAME_STATE_OVER:
                    print("Resetting game")
                    # Reset game
                    game_state = GAME_STATE_START
                    bird = Bird()  # Create a new bird instance
                    pipes = []  # Clear all pipes
                    last_pipe_time = current_time  # Reset pipe spawn timer
                    score = 0  # Reset score
                    current_pipe_speed, speed_level = calculate_pipe_speed(score)  # Reset speed
                elif game_state == GAME_STATE_PLAY:  # Only allow jumping during play state
                    bird.jump()

    # Clear screen
    screen.fill(WHITE)

    # Update and draw based on game state
    if game_state == GAME_STATE_PLAY:
        # Update and draw cityscape
        cityscape.update()
        cityscape.draw()
        
        bird.update()
        bird.draw()

        # Update and draw Donkey Kong
        donkey_kong.update()
        donkey_kong.draw()

        # Spawn new pipes
        if current_time - last_pipe_time > PIPE_SPAWN_INTERVAL:
            pipes.append(Pipe(current_pipe_speed))
            last_pipe_time = current_time

        # Update and draw pipes
        for pipe in pipes[:]:
            pipe.update()
            pipe.draw()
            
            # Check if bird passed the pipe
            if not pipe.scored and pipe.x + pipe.width < bird.x:
                score += 1
                pipe.scored = True
                
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

        # Draw score and speed
        draw_score(score, speed_level)

        # Check for collisions
        if check_collision(bird, pipes):
            print("Game state changing to SUCKING")
            game_state = GAME_STATE_SUCKING

    elif game_state == GAME_STATE_SUCKING:
        print("In SUCKING state")
        # Draw cityscape (no update to keep it stationary)
        cityscape.draw()
        
        # Update sucking animation
        if bird.update_sucking():
            print("Game state changing to OVER")
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
        print("In START state")
        # Draw cityscape (no update to keep it stationary)
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

    # Update display
    pygame.display.flip()
    clock.tick(FPS) 