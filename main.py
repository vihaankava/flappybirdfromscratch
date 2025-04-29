import asyncio
import pygame
import random
import os
import math
import json
import sys
from datetime import datetime

from flappy_bird import Bird, Pipe, Cityscape, WeatherSystem, Leaderboard
from flappy_bird import PowerUp, Enemy, Fireball
from flappy_bird import DonkeyKong, DeathCutscene, LuigiBattle, WinningCutscene
from flappy_bird import check_collision, draw_score, calculate_pipe_speed

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

GAME_STATE_START = 0
GAME_STATE_PLAYING = 1
GAME_STATE_OVER = 2
GAME_STATE_NAME_ENTRY = 3
GAME_STATE_LEADERBOARD = 4
GAME_STATE_WINNING = 5
GAME_STATE_LUIGI_BATTLE = 6
GAME_STATE_COUNTDOWN = 7

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

LEADERBOARD_FILE = 'leaderboard.json'

pygame.init()
pygame.mixer.init()  # Initialize the mixer for sound effects

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()

is_browser = hasattr(sys, 'platform') and sys.platform.startswith('emscripten')

jump_sound = None
score_sound = None
collision_sound = None
game_over_sound = None
power_pipe_sound = None
lightning_sound = None
rain_sound = None

bird = None
pipes = []
cityscape = None
donkey_kong = None
weather_system = None
leaderboard = None
winning_cutscene = None
death_cutscene = None
luigi_battle = None

game_state = GAME_STATE_START
countdown_start = 0
last_pipe_time = 0
score = 0
current_pipe_speed = 0
speed_level = 0
player_name = ""
name_input_active = False

power_ups = []
enemies = []
fireballs = []

NAME_INPUT_BOX = pygame.Rect(SCREEN_WIDTH//2 - 150, SCREEN_HEIGHT//2, 300, 40)

async def initialize_game():
    """Initialize game objects and load resources"""
    global jump_sound, score_sound, collision_sound, game_over_sound, power_pipe_sound, lightning_sound, rain_sound
    global bird, pipes, cityscape, donkey_kong, weather_system, leaderboard, winning_cutscene, death_cutscene, luigi_battle
    global game_state, countdown_start, last_pipe_time, score, current_pipe_speed, speed_level, player_name, power_ups, enemies, fireballs
    
    # Load sound effects
    try:
        jump_sound = pygame.mixer.Sound('sounds/jump.wav')
        score_sound = pygame.mixer.Sound('sounds/score.wav')
        collision_sound = pygame.mixer.Sound('sounds/collision.wav')
        game_over_sound = pygame.mixer.Sound('sounds/game_over.wav')
        power_pipe_sound = pygame.mixer.Sound('sounds/power_pipe.wav')
        lightning_sound = pygame.mixer.Sound('sounds/lightning.wav')
        rain_sound = pygame.mixer.Sound('sounds/rain.wav')
    except Exception as e:
        print(f"Warning: Sound files not found. Error: {e}")
        print("Game will run without sound effects.")
    
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
    countdown_start = 0
    last_pipe_time = pygame.time.get_ticks()
    score = 0
    current_pipe_speed, speed_level = calculate_pipe_speed(score)
    player_name = ""
    
    power_ups = []
    enemies = []
    fireballs = []
    
    print("Game initialized successfully!")

async def main():
    """Main game loop"""
    global game_state, countdown_start, last_pipe_time, score, current_pipe_speed, speed_level, player_name
    global bird, pipes, cityscape, donkey_kong, weather_system, leaderboard, winning_cutscene, death_cutscene, luigi_battle
    global power_ups, enemies, fireballs
    
    if is_browser:
        print("Running in browser environment")
    
    await initialize_game()
    
    while True:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return  # Exit cleanly
                
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
                        enemies = []
                        fireballs = []
                        last_pipe_time = current_time
                        score = 0
                        current_pipe_speed, speed_level = calculate_pipe_speed(score)
                    elif game_state == GAME_STATE_LEADERBOARD:
                        game_state = GAME_STATE_START
                        bird = Bird()
                        pipes = []
                        enemies = []
                        fireballs = []
                        last_pipe_time = current_time
                        score = 0
                        current_pipe_speed, speed_level = calculate_pipe_speed(score)
                    elif game_state == GAME_STATE_PLAYING:
                        bird.jump()
                        if jump_sound:
                            jump_sound.play()
                elif event.key == pygame.K_a and game_state == GAME_STATE_PLAYING:
                    fireballs.append(Fireball(bird.x + bird.width, bird.y + bird.height/2))
        
        screen.fill(WHITE)
        
        if game_state == GAME_STATE_PLAYING:
            bird.update()
            cityscape.update()
            
            cityscape.draw()
            
            bird.draw()
            
            # Update and draw Donkey Kong
            donkey_kong.update()
            donkey_kong.draw()
            
            if current_time - last_pipe_time > 1500:  # PIPE_SPAWN_INTERVAL
                new_pipe = Pipe(current_pipe_speed)
                pipes.append(new_pipe)
                
                if random.random() < 0.5:  # POWER_UP_SPAWN_CHANCE
                    power_up_y = new_pipe.top_height + (new_pipe.gap // 2)
                    power_ups.append(PowerUp(new_pipe.x + new_pipe.width//2 - 15,
                                           power_up_y,
                                           'shield'))
                
                if random.random() < 0.2:  # ENEMY_SPAWN_CHANCE
                    enemy_y = new_pipe.top_height + (new_pipe.gap // 2)
                    enemies.append(Enemy(new_pipe.x + new_pipe.width//2 - 15,
                                       enemy_y))
                
                last_pipe_time = current_time
            
            # Update and draw pipes
            for pipe in pipes[:]:
                pipe.update()
                pipe.draw()
                
                if not pipe.scored and pipe.x + pipe.width < bird.x:
                    score += 1
                    pipe.scored = True
                    
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
                    
                    if pipe.is_power_pipe and not pipe.power_effect_active:
                        score += 2  # Bonus points
                        pipe.power_effect_active = True
                        for p in pipes:
                            if p.is_moving:
                                p.speed = max(1, p.speed * 0.5)  # Reduce speed by half, minimum 1
                        if power_pipe_sound:
                            power_pipe_sound.play()
                    else:
                        if score_sound:
                            score_sound.play()
                    
                    current_pipe_speed, speed_level = calculate_pipe_speed(score)
                    for p in pipes:
                        if p.is_moving and not p.power_effect_active:
                            p.speed = current_pipe_speed
                
                if pipe.x + pipe.width < 0:
                    pipes.remove(pipe)
            
            # Update and draw power-ups
            for power_up in power_ups[:]:
                power_up.update()
                power_up.draw()
                
                if power_up.get_rect().colliderect(bird.get_rect()):
                    if power_up.power_type == 'shield':
                        bird.activate_shield()
                    power_up.collected = True
                    power_ups.remove(power_up)
                
                if power_up.x + power_up.width < 0:
                    power_ups.remove(power_up)
            
            # Update and draw enemies
            for enemy in enemies[:]:
                enemy.update()
                enemy.draw()
                
                if enemy.get_rect().colliderect(bird.get_rect()):
                    if not bird.shield_active:  # Only trigger collision if shield is not active
                        game_state = GAME_STATE_OVER
                        if collision_sound:
                            collision_sound.play()
                        break
                
                if enemy.x + enemy.width < 0:
                    enemies.remove(enemy)
            
            # Update and draw fireballs
            for fireball in fireballs[:]:
                fireball.update()
                fireball.draw()
                
                for enemy in enemies[:]:
                    if fireball.get_rect().colliderect(enemy.get_rect()):
                        enemies.remove(enemy)
                        fireballs.remove(fireball)
                        score += 2  # Bonus points for destroying an enemy
                        if score_sound:
                            score_sound.play()
                        break
                
                if fireball.x > SCREEN_WIDTH:
                    fireballs.remove(fireball)
            
            draw_score(score, speed_level)
            
            if check_collision(bird, pipes):
                game_state = GAME_STATE_OVER
                if collision_sound:
                    collision_sound.play()
            
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
            
            cityscape.draw()
            
            # Update and draw bird
            if bird.update_sucking():
                game_state = GAME_STATE_OVER
                if game_over_sound:
                    game_over_sound.play()
            bird.draw()
            
            for pipe in pipes:
                pipe.draw()
            
            draw_score(score, speed_level)
        
        elif game_state == GAME_STATE_START:
            cityscape.draw()
            
            bird.draw()
            
            font = pygame.font.Font(None, 36)
            text = font.render("Press SPACE to Start", True, BLACK)
            text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
            screen.blit(text, text_rect)
        
        elif game_state == GAME_STATE_NAME_ENTRY:
            cityscape.draw()
            
            font = pygame.font.Font(None, 36)
            prompt = font.render("Enter your name (3-10 chars):", True, BLACK)
            screen.blit(prompt, (SCREEN_WIDTH//2 - prompt.get_width()//2, SCREEN_HEIGHT//2 - 50))
            
            pygame.draw.rect(screen, BLACK, NAME_INPUT_BOX, 2)
            
            name_text = font.render(player_name, True, BLACK)
            screen.blit(name_text, (NAME_INPUT_BOX.x + 5, NAME_INPUT_BOX.y + 5))
            
            if pygame.time.get_ticks() % 1000 < 500:  # Blink every 500ms
                cursor_x = NAME_INPUT_BOX.x + 5 + name_text.get_width()
                pygame.draw.line(screen, BLACK, 
                                (cursor_x, NAME_INPUT_BOX.y + 5),
                                (cursor_x, NAME_INPUT_BOX.y + NAME_INPUT_BOX.height - 5), 2)
            
            submit_text = font.render("Press ENTER to submit", True, BLACK)
            screen.blit(submit_text, (SCREEN_WIDTH//2 - submit_text.get_width()//2, 
                                    SCREEN_HEIGHT//2 + 60))
        
        elif game_state == GAME_STATE_LEADERBOARD:
            cityscape.draw()
            
            leaderboard.draw_leaderboard(screen)
            
            font = pygame.font.Font(None, 36)
            continue_text = font.render("Press SPACE to continue", True, BLACK)
            screen.blit(continue_text, (SCREEN_WIDTH//2 - continue_text.get_width()//2, 
                                      SCREEN_HEIGHT - 50))
        
        elif game_state == GAME_STATE_WINNING:
            if winning_cutscene.update():
                game_state = GAME_STATE_COUNTDOWN
                countdown_start = pygame.time.get_ticks()
                print("Mario battle complete! Starting 3-second countdown...")
                score += 5
                print(f"Bonus points awarded! New score: {score}")
            
            cityscape.draw()
            
            winning_cutscene.draw(screen, bird)
        
        elif game_state == GAME_STATE_LUIGI_BATTLE:
            if luigi_battle.update():
                game_state = GAME_STATE_COUNTDOWN
                countdown_start = pygame.time.get_ticks()
                print("Luigi battle complete! Starting 3-second countdown...")
                score += 10
                print(f"Bonus points awarded! New score: {score}")
            
            cityscape.draw()
            
            luigi_battle.draw(screen, bird)
        
        elif game_state == GAME_STATE_COUNTDOWN:
            cityscape.draw()
            
            bird.draw()
            
            elapsed = (pygame.time.get_ticks() - countdown_start) // 1000  # Convert to seconds
            remaining = 3 - elapsed
            
            if remaining > 0:
                font = pygame.font.Font(None, 72)
                text = font.render(str(remaining), True, BLACK)
                text_rect = text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
                screen.blit(text, text_rect)
            else:
                bird = Bird()
                pipes = []
                enemies = []
                fireballs = []
                power_ups = []
                current_pipe_speed, speed_level = calculate_pipe_speed(score)
                game_state = GAME_STATE_PLAYING
                print(f"Countdown complete! Restarting with score {score}...")
        
        # Update and draw weather
        weather_system.update()
        weather_system.draw()
        
        pygame.display.flip()
        clock.tick(FPS)
        
        await asyncio.sleep(0)

if __name__ == "__main__":
    asyncio.run(main())
