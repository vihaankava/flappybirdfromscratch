import os
import sys
import json
import random
import base64
import io
import sqlite3
from datetime import datetime
from threading import Thread, Lock
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
pygame.init()
try:
    pygame.mixer.init()
except pygame.error:
    print("Warning: Could not initialize audio. Running without sound.")
    class DummySound:
        def play(self): pass
        def stop(self): pass
    
    pygame.mixer.Sound = DummySound

from flappy_bird import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, PIPE_SPAWN_INTERVAL,
    Bird, Pipe, PowerUp, Enemy, Fireball, WeatherSystem, Cityscape,
    DonkeyKong, DeathCutscene, LuigiBattle, WinningCutscene,
    check_collision, draw_score, calculate_pipe_speed
)

class ServerLeaderboard:
    def __init__(self, db_path='leaderboard.db'):
        self.db_path = db_path
        self.scores = []
        self.init_db()
        self.load_scores()
        self.previous_top_score = self.get_top_score()
        self.previous_top_name = self.get_top_name()
        self.beat_message_active = False
        self.beat_message_timer = 0
        self.beat_message_duration = 180  # 3 seconds at 60 FPS
        self.beat_message_scale = 1.0
        self.beat_message_growing = True
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS leaderboard (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            score INTEGER NOT NULL,
            date TEXT NOT NULL
        )
        ''')
        conn.commit()
        conn.close()

    def load_scores(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM leaderboard ORDER BY score DESC')
            rows = cursor.fetchall()
            conn.close()
            
            self.scores = [dict(row) for row in rows]
        except Exception as e:
            print(f"Error loading leaderboard from database: {e}")
            self.scores = []

    def save_scores(self):
        pass

    def add_score(self, name, score):
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO leaderboard (name, score, date) VALUES (?, ?, ?)',
                      (name, score, current_time))
        conn.commit()
        conn.close()
        
        self.load_scores()

    def get_top_score(self):
        return self.scores[0]['score'] if self.scores else 0

    def get_top_name(self):
        return self.scores[0]['name'] if self.scores else ""

    def is_high_score(self, score):
        if not self.scores:
            return True
        return len(self.scores) < 10 or score > self.scores[-1]['score']

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

class GameInstance:
    """Server-side game instance that handles game logic and rendering"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.game_state = 'START'  # START, PLAYING, OVER, LEADERBOARD
        self.score = 0
        self.high_score = 0
        
        self.bird = Bird()
        self.pipes = []
        self.power_ups = []
        self.enemies = []
        self.fireballs = []
        self.weather = WeatherSystem()
        self.cityscape = Cityscape()
        self.donkey_kong = DonkeyKong()
        self.death_cutscene = DeathCutscene()
        self.luigi_battle = LuigiBattle()
        self.winning_cutscene = WinningCutscene()
        
        self.leaderboard = ServerLeaderboard()
        
        self.last_pipe_spawn = 0
        self.pipe_speed = 2
        self.last_update = pygame.time.get_ticks()
        self.frame_count = 0
        
        self.lock = Lock()
        
        self.reset_game()
    
    def reset_game(self):
        """Reset the game state"""
        with self.lock:
            self.bird.reset()
            self.pipes = []
            self.power_ups = []
            self.enemies = []
            self.fireballs = []
            self.score = 0
            self.last_pipe_spawn = pygame.time.get_ticks()
            self.pipe_speed = 2
            self.game_state = 'START'
    
    def start_game(self):
        """Start the game"""
        with self.lock:
            if self.game_state == 'START':
                self.game_state = 'PLAYING'
                self.reset_game()
    
    def handle_jump(self):
        """Handle jump action"""
        with self.lock:
            if self.game_state == 'PLAYING':
                self.bird.jump()
    
    def handle_fire(self):
        """Handle fire action"""
        with self.lock:
            if self.game_state == 'PLAYING' and self.bird.can_shoot:
                self.fireballs.append(Fireball(self.bird.x, self.bird.y))
    
    def update(self):
        """Update game state"""
        with self.lock:
            current_time = pygame.time.get_ticks()
            dt = current_time - self.last_update
            self.last_update = current_time
            
            if self.game_state == 'PLAYING':
                self.bird.update()
                
                if current_time - self.last_pipe_spawn > PIPE_SPAWN_INTERVAL:
                    self.last_pipe_spawn = current_time
                    
                    self.pipe_speed = calculate_pipe_speed(self.score)
                    
                    new_pipe = Pipe(self.pipe_speed)
                    self.pipes.append(new_pipe)
                    
                    if random.random() < 0.2:  # 20% chance
                        power_up_type = random.choice(['shield', 'slow', 'points'])
                        self.power_ups.append(PowerUp(SCREEN_WIDTH, random.randint(100, SCREEN_HEIGHT - 100), power_up_type))
                    
                    if random.random() < 0.15:  # 15% chance
                        self.enemies.append(Enemy(SCREEN_WIDTH, random.randint(100, SCREEN_HEIGHT - 100)))
                
                for pipe in self.pipes[:]:
                    pipe.update()
                    
                    if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                        pipe.passed = True
                        self.score += 1
                    
                    if pipe.x < -pipe.width:
                        self.pipes.remove(pipe)
                
                for power_up in self.power_ups[:]:
                    power_up.update()
                    
                    if check_collision(self.bird.get_rect(), power_up.get_rect()):
                        if power_up.type == 'shield':
                            self.bird.activate_shield()
                        elif power_up.type == 'slow':
                            for pipe in self.pipes:
                                pipe.speed *= 0.5
                        elif power_up.type == 'points':
                            self.score += 5
                        
                        self.power_ups.remove(power_up)
                    
                    if power_up.x < -power_up.width:
                        self.power_ups.remove(power_up)
                
                for enemy in self.enemies[:]:
                    enemy.update()
                    
                    if check_collision(self.bird.get_rect(), enemy.get_rect()):
                        if not self.bird.shield_active:
                            self.game_over()
                        else:
                            self.enemies.remove(enemy)
                    
                    for fireball in self.fireballs[:]:
                        if check_collision(fireball.get_rect(), enemy.get_rect()):
                            self.enemies.remove(enemy)
                            self.fireballs.remove(fireball)
                            self.score += 2
                            break
                    
                    if enemy.x < -enemy.width:
                        self.enemies.remove(enemy)
                
                for fireball in self.fireballs[:]:
                    fireball.update()
                    
                    if fireball.x > SCREEN_WIDTH:
                        self.fireballs.remove(fireball)
                
                self.cityscape.update()
                self.weather.update()
                
                for pipe in self.pipes:
                    if check_collision(self.bird.get_rect(), pipe.get_top_rect()) or \
                       check_collision(self.bird.get_rect(), pipe.get_bottom_rect()):
                        if not self.bird.shield_active:
                            self.game_over()
                
                if self.bird.y < 0 or self.bird.y > SCREEN_HEIGHT:
                    self.game_over()
            
            elif self.game_state == 'OVER':
                self.death_cutscene.update()
    
    def game_over(self):
        """Handle game over"""
        with self.lock:
            self.game_state = 'OVER'
            self.death_cutscene.start(self.bird.x, self.bird.y)
            
            if self.score > self.high_score:
                self.high_score = self.score
    
    def render(self):
        """Render the game state to a surface and return as base64 image"""
        with self.lock:
            self.screen.fill((135, 206, 235))  # Sky blue
            
            self.cityscape.draw()
            
            self.weather.draw()
            
            for pipe in self.pipes:
                pipe.draw(self.screen)
            
            for power_up in self.power_ups:
                power_up.draw(self.screen)
            
            for enemy in self.enemies:
                enemy.draw(self.screen)
            
            for fireball in self.fireballs:
                fireball.draw(self.screen)
            
            self.bird.draw(self.screen)
            
            draw_score(self.screen, self.score)
            
            if self.game_state == 'OVER':
                self.death_cutscene.draw(self.screen)
            
            image_data = pygame.image.tostring(self.screen, 'RGB')
            image = pygame.image.fromstring(image_data, (SCREEN_WIDTH, SCREEN_HEIGHT), 'RGB')
            
            buffer = io.BytesIO()
            pygame.image.save(image, buffer, 'PNG')
            buffer.seek(0)
            
            img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
            
            return img_base64
    
    def get_state(self):
        """Get the current game state"""
        with self.lock:
            return {
                'game_state': self.game_state,
                'score': self.score,
                'high_score': self.high_score,
                'frame': self.render()
            }

class GameServer:
    """Server that manages multiple game instances"""
    
    def __init__(self):
        self.games = {}
        self.lock = Lock()
        self.update_thread = Thread(target=self._update_loop)
        self.update_thread.daemon = True
        self.update_thread.start()
    
    def get_game(self, user_id):
        """Get or create a game instance for a user"""
        with self.lock:
            if user_id not in self.games:
                self.games[user_id] = GameInstance(user_id)
            return self.games[user_id]
    
    def remove_game(self, user_id):
        """Remove a game instance"""
        with self.lock:
            if user_id in self.games:
                del self.games[user_id]
    
    def _update_loop(self):
        """Update all game instances in a separate thread"""
        while True:
            with self.lock:
                for game in self.games.values():
                    game.update()
            time.sleep(1 / FPS)  # Target FPS

game_server = GameServer()
