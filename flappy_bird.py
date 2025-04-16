import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60
PIPE_SPAWN_INTERVAL = 1500  # milliseconds
FALL_SPEED = 3  # Speed at which bird falls through pipe
BASE_PIPE_SPEED = 3  # Initial pipe speed
BACKGROUND_SPEED = 0.5  # Speed of background movement

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0, 128)  # Semi-transparent green (alpha = 128)
BUILDING_COLORS = [
    (100, 100, 100),  # Dark gray
    (120, 120, 120),  # Medium gray
    (140, 140, 140),  # Light gray
    (160, 160, 160),  # Very light gray
]

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
            width = random.randint(30, 80)
            height = random.randint(100, 300)
            color = random.choice(BUILDING_COLORS)
            self.buildings.append({
                'x': x,
                'width': width,
                'height': height,
                'color': color
            })
            x += width + random.randint(10, 30)  # Add some space between buildings
            
    def update(self):
        # Move buildings to the left
        for building in self.buildings:
            building['x'] -= BACKGROUND_SPEED
            
        # Remove buildings that are off screen and add new ones
        if self.buildings[0]['x'] + self.buildings[0]['width'] < 0:
            last_building = self.buildings[-1]
            new_x = last_building['x'] + last_building['width'] + random.randint(10, 30)
            width = random.randint(30, 80)
            height = random.randint(100, 300)
            color = random.choice(BUILDING_COLORS)
            self.buildings.append({
                'x': new_x,
                'width': width,
                'height': height,
                'color': color
            })
            self.buildings.pop(0)
            
    def draw(self):
        # Draw buildings
        for building in self.buildings:
            if building['x'] + building['width'] > 0 and building['x'] < SCREEN_WIDTH:
                pygame.draw.rect(screen, building['color'], 
                               (building['x'], SCREEN_HEIGHT - building['height'],
                                building['width'], building['height']))

class Bird:
    def __init__(self):
        self.reset()

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity

    def jump(self):
        self.velocity = self.jump_strength

    def draw(self):
        pygame.draw.rect(screen, BLUE, (self.x, self.y, self.width, self.height))

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

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update_sucking(self):
        if self.target_pipe:
            if not self.is_falling_through:
                # First phase: Move bird to the pipe's x position
                self.x = self.target_pipe.x + (self.target_pipe.width - self.width) // 2
                self.is_falling_through = True
                # Position bird at the top of the pipe gap
                self.y = self.target_pipe.top_height
            else:
                # Second phase: Bird falls through the pipe
                self.y += FALL_SPEED
                # Keep bird aligned with the pipe (which is now stationary)
                self.x = self.target_pipe.x + (self.target_pipe.width - self.width) // 2
            
            # Check if bird has fallen through the pipe
            if self.y > SCREEN_HEIGHT:
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

    def update(self):
        if self.is_moving:
            self.x -= self.speed

    def draw(self):
        # Create a surface for the pipe with per-pixel alpha
        pipe_surface = pygame.Surface((self.width, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        # Draw top pipe
        pygame.draw.rect(pipe_surface, GREEN, (0, 0, self.width, self.top_height))
        # Draw bottom pipe
        pygame.draw.rect(pipe_surface, GREEN, (0, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y))
        
        # Blit the pipe surface onto the screen
        screen.blit(pipe_surface, (self.x, 0))

    def get_top_rect(self):
        return pygame.Rect(self.x, 0, self.width, self.top_height)

    def get_bottom_rect(self):
        return pygame.Rect(self.x, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y)

def check_collision(bird, pipes):
    bird_rect = bird.get_rect()
    
    # Check collision with screen boundaries
    if bird.y <= 0 or bird.y + bird.height >= SCREEN_HEIGHT:
        return True
    
    # Check collision with pipes
    for pipe in pipes:
        if bird_rect.colliderect(pipe.get_top_rect()) or bird_rect.colliderect(pipe.get_bottom_rect()):
            bird.target_pipe = pipe
            # Stop all pipes when collision occurs
            for p in pipes:
                p.is_moving = False
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

def calculate_pipe_speed(score):
    # Increase speed by 25% for every 10 points
    speed_level = 1 + (score // 10) * 0.25
    return BASE_PIPE_SPEED * speed_level, speed_level

# Initialize game objects
bird = Bird()
pipes = []
cityscape = Cityscape()
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
                    game_state = GAME_STATE_PLAY
                    score = 0  # Reset score when starting new game
                    current_pipe_speed, speed_level = calculate_pipe_speed(score)
                elif game_state == GAME_STATE_OVER:
                    # Reset game
                    game_state = GAME_STATE_START
                    bird = Bird()  # Create a new bird instance
                    pipes = []  # Clear all pipes
                    last_pipe_time = current_time  # Reset pipe spawn timer
                    score = 0  # Reset score
                    current_pipe_speed, speed_level = calculate_pipe_speed(score)  # Reset speed
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
                # Update pipe speed based on new score
                current_pipe_speed, speed_level = calculate_pipe_speed(score)
                # Update speed of all moving pipes
                for p in pipes:
                    if p.is_moving:
                        p.speed = current_pipe_speed
            
            # Remove pipes that are off screen
            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)

        # Draw score and speed
        draw_score(score, speed_level)

        # Check for collisions
        if check_collision(bird, pipes):
            game_state = GAME_STATE_SUCKING

    elif game_state == GAME_STATE_SUCKING:
        # Draw cityscape (no update to keep it stationary)
        cityscape.draw()
        
        # Update sucking animation
        if bird.update_sucking():
            game_state = GAME_STATE_OVER
        bird.draw()
        
        # Draw pipes (they won't move anymore)
        for pipe in pipes:
            pipe.draw()
        
        # Draw score and speed
        draw_score(score, speed_level)

    elif game_state == GAME_STATE_START:
        # Draw cityscape (no update to keep it stationary)
        cityscape.draw()
        
        # Draw start screen
        bird.draw()
        font = pygame.font.Font(None, 36)
        text = font.render("Press SPACE to Start", True, BLACK)
        text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(text, text_rect)

    elif game_state == GAME_STATE_OVER:
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