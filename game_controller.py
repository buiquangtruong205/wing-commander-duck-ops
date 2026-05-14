import pygame
import cv2
import numpy as np
import time
import random
import os
import ctypes

from backend.hand_tracker import HandTracker
from backend.game_logic import Duck, Crosshair, Particle, Explosion
from frontend.assets_manager import AssetsManager
from frontend.ui_system import UISystem, UIButton, UIInputField, UISlider, UIToggle, NEON_BLUE, NEON_PINK, NEON_GREEN, GOLD, WHITE
from backend.database import DatabaseManager

# Configuration
WIDTH, HEIGHT = 1280, 720
FPS = 60
MAX_CHALLENGE_LEVEL = 10
BASE_CHALLENGE_TARGET = 100
BOSS_REWARD_PER_LEVEL = 100
BOSS_MINION_SPAWN_COUNT = 2
BOSS_MINION_MAX_ACTIVE = 12
BOSS_MINION_SIZE = 60

class DuckOpsGame:
    def __init__(self):
        self.configure_windows_app_id()
        pygame.init()
        # Optimize mixer for low latency (buffer size 512)
        pygame.mixer.pre_init(44100, -16, 2, 512)
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wing Commander: Duck Ops - AI Version 2.0")
        self.set_window_icon()
        self.clock = pygame.time.Clock()
        
        # Initialize Database
        self.db = DatabaseManager()
        
        # Load Assets
        self.assets = AssetsManager(WIDTH, HEIGHT)
        self.assets.load_all()
        
        # UI System
        self.ui = UISystem(self.screen, self.assets)
        self.setup_ui_elements()
        
        # Game State
        self.current_user = None
        self.user_settings = {
            'music_volume': 0.5,
            'sfx_volume': 0.5,
            'is_fullscreen': 0,
            'camera_index': 0,
            'flip_camera': 1,
            'tracking_sensitivity': 1.0
        }
        last_user = self.db.get_last_user()
        if last_user:
            self.current_user = last_user
            self.user_settings = self.db.get_player_settings(last_user)
            self.assets.apply_volumes(self.user_settings['music_volume'], self.user_settings['sfx_volume'])
            self.setup_settings_ui()
            self.state = "HOME"
        else:
            self.state = "LOGIN"

        self.game_mode = None
        self.score = 0
        self.missiles = 3
        self.lives = 3
        self.start_time = 0
        self.last_shot_time = 0
        self.last_rocket_time = 0
        self.last_menu_action_time = 0

        # Camera & AI
        self.cap = cv2.VideoCapture(0)
        self.tracker = HandTracker()
        self.current_bg = self.assets.images['level_bg1']

        # New Mechanics
        self.pending_mode = None
        self.camera_noise = 0
        self.boss_active = False
        self.feathers = pygame.sprite.Group()
        self.story_start_time = 0
        self.screen_shake_until = 0
        self.screen_shake_magnitude = 0
        self.boot_message_until = 0

        # Smoothing (Increased for better responsiveness)
        self.hand_x, self.hand_y = WIDTH // 2, HEIGHT // 2
        self.lerp_factor = 0.4

        # Groups
        self.ducks = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()

        self.crosshair = Crosshair(NEON_BLUE)
        self.all_sprites.add(self.crosshair)

        self.settings_elements = {}
        self.lobby_music_playing = False
        self.confirm_exit_game = False
        self.exit_confirm_started = 0

        self.running = True

        self.assets.apply_volumes(self.user_settings['music_volume'], self.user_settings['sfx_volume'])

    def configure_windows_app_id(self):
        if os.name != "nt":
            return

        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("WingCommander.DuckOps")
        except Exception as exc:
            print(f"Could not set Windows AppUserModelID: {exc}")

    def set_window_icon(self):
        icon_path = os.path.join("frontend", "images", "app_logo.png")
        try:
            icon = pygame.image.load(icon_path).convert_alpha()
            pygame.display.set_icon(icon)
        except Exception as exc:
            print(f"Could not load window icon {icon_path}: {exc}")

    def setup_ui_elements(self):
        btn_font = self.assets.fonts['main']
        cx = WIDTH // 2
        bw, bh = 350, 75
        menu_w, menu_h = 300, 54
        menu_x = cx - menu_w // 2

        self.login_input = UIInputField(cx - 220, 310, 440, 58, btn_font, "Tên chỉ huy")
        self.login_btn = UIButton(cx - 150, 400, 300, 64, "VÀO GAME", btn_font, icon="*", assets=self.assets, style='wood')

        self.home_buttons = {
            "play": UIButton(menu_x, 215, menu_w, menu_h, "Chơi", btn_font, icon="shield", icon_right="gamepad", assets=self.assets, style='wood'),
            "tutorial": UIButton(menu_x, 298, menu_w, menu_h, "Cách chơi", btn_font, icon="book", icon_right="book_open", assets=self.assets, style='wood', image_key='tutorial_button'),
            "leaderboard": UIButton(menu_x, 381, menu_w, menu_h, "Lịch sử", btn_font, icon="scroll", icon_right="duck", assets=self.assets, style='wood', image_key='history_button'),
            "about": UIButton(menu_x, 464, menu_w, menu_h, "Giới thiệu", btn_font, icon="bulb", icon_right="medal", assets=self.assets, style='wood', image_key='about_button'),
            "settings": UIButton(menu_x, 547, menu_w, menu_h, "Cài đặt", btn_font, icon="gear", icon_right="gears", assets=self.assets, style='wood', image_key='settings_button')
        }

        bw_wide = 620
        cx_wide = cx - bw_wide // 2
        select_h = int(bw_wide * 404 / 1024)
        select_y = 271 - select_h // 2
        row_centers = (
            select_y + int(select_h * 0.180),
            select_y + int(select_h * 0.505),
            select_y + int(select_h * 0.815),
        )
        self.play_buttons = {
            "quick": UIButton(cx_wide, row_centers[0] - bh // 2, bw_wide, bh, "Chơi nhanh (60 giây, bắn tự do)", btn_font, color=GOLD, assets=self.assets),
            "challenge": UIButton(cx_wide, row_centers[1] - bh // 2, bw_wide, bh, "Thử thách (Đạt mục tiêu, vịt nhanh dần)", btn_font, color=NEON_BLUE, assets=self.assets),
            "endless": UIButton(cx_wide, row_centers[2] - bh // 2, bw_wide, bh, "Vô tận (3 mạng, không giới hạn)", btn_font, color=NEON_PINK, assets=self.assets),
            "back": UIButton(cx_wide, 550, bw_wide, 66, "QUAY LẠI", btn_font, assets=self.assets)
        }
        
        # Shared Back Button
        self.back_btn = UIButton(cx - bw // 2, 600, bw, bh, "BACK TO MENU", btn_font, assets=self.assets)
        
        # Story Screen Button
        self.story_btn = UIButton(cx - bw // 2, 600, bw, bh, "BẮT ĐẦU NHIỆM VỤ", btn_font, icon=">", assets=self.assets)

        hud_button_font = pygame.font.SysFont("Arial", 17, bold=True)
        self.exit_game_btn = UIButton(WIDTH - 180, 108, 166, 38, "BACK TO MENU >", hud_button_font, color=WHITE, hover_color=GOLD, assets=self.assets)
        self.exit_yes_btn = UIButton(cx - 170, 395, 140, 58, "C\u00d3", btn_font, color=NEON_GREEN, hover_color=GOLD, assets=self.assets)
        self.exit_no_btn = UIButton(cx + 30, 395, 140, 58, "KH\u00d4NG", btn_font, color=NEON_PINK, hover_color=GOLD, assets=self.assets)

    def setup_settings_ui(self):
        if not self.user_settings: return
        
        s_font = self.assets.fonts['main']
        cx = WIDTH // 2
        
        self.settings_elements = {
            'music_volume': UISlider(cx - 400, 200, 300, 20, "MUSIC VOLUME", s_font, value=self.user_settings['music_volume'], color=NEON_GREEN),
            'sfx_volume': UISlider(cx + 50, 200, 300, 20, "SFX VOLUME", s_font, value=self.user_settings['sfx_volume'], color=NEON_GREEN),
            'tracking_sensitivity': UISlider(cx - 400, 380, 700, 20, "TRACKING SENSITIVITY", s_font, value=self.user_settings['tracking_sensitivity'], color=NEON_BLUE),
            'flip_camera': UIToggle(cx - 400, 420, 800, 40, "FLIP CAMERA (MIRROR)", s_font, value=bool(self.user_settings['flip_camera']), color=NEON_BLUE),
            'is_fullscreen': UIToggle(cx - 400, 520, 800, 40, "FULLSCREEN MODE", s_font, value=bool(self.user_settings['is_fullscreen']), color=NEON_PINK)
        }

    def save_settings(self):
        if not self.current_user: return
        
        updated = {
            'music_volume': self.settings_elements['music_volume'].value,
            'sfx_volume': self.settings_elements['sfx_volume'].value,
            'tracking_sensitivity': self.settings_elements['tracking_sensitivity'].value,
            'flip_camera': int(self.settings_elements['flip_camera'].value),
            'is_fullscreen': int(self.settings_elements['is_fullscreen'].value)
        }
        self.db.update_settings(self.current_user, updated)
        self.user_settings.update(updated) # Sync local copy
        
        # Apply display settings
        if updated['is_fullscreen']:
            pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
        else:
            pygame.display.set_mode((WIDTH, HEIGHT))

    def login(self):
        username = self.login_input.text.strip()
        if username:
            self.db.login_player(username)
            self.db.set_last_user(username)
            self.current_user = username
            self.user_settings = self.db.get_player_settings(username)
            self.assets.apply_volumes(self.user_settings['music_volume'], self.user_settings['sfx_volume'])
            self.setup_settings_ui()
            self.state = "HOME"

    def update_lobby_music(self):
        lobby_states = {"LOGIN", "HOME", "PLAY_SELECT", "SETTINGS", "LEADERBOARD", "TUTORIAL", "ABOUT", "STORY"}
        lobby_music = self.assets.sounds.get('lobby')
        if not lobby_music:
            return

        if self.state in lobby_states:
            if not self.lobby_music_playing:
                lobby_music.play(-1)
                self.lobby_music_playing = True
        elif self.lobby_music_playing:
            lobby_music.stop()
            self.lobby_music_playing = False

    def spawn_duck(self):
        max_ducks = 5 + (self.level if self.game_mode == "CHALLENGE" else 0)
        if len(self.ducks) < max_ducks:
            # Different probabilities per level
            if self.level == 1:
                weights = [70, 10, 5, 15] # 15% elite
            elif self.level == 2:
                weights = [40, 25, 10, 25] # 25% elite
            else: # Level 3+
                weights = [20, 30, 20, 30] # 30% elite
                
            d_type = random.choices(["normal", "fast", "zigzag", "elite"], weights=weights)[0]
            speed_mult = 1.0
            if self.game_mode == "CHALLENGE":
                speed_mult = 1.0 + (self.level - 1) * 0.25
            elif self.game_mode == "ENDLESS":
                elapsed = time.time() - self.start_time
                speed_mult = 1.0 + (elapsed // 20) * 0.15 # Faster increase
            
            sheet = self.assets.images['yellow_duck_sheet'] if d_type == "elite" else self.assets.images['duck_sheet']
            duck = Duck(WIDTH, HEIGHT, sheet, d_type, speed_mult)
            self.ducks.add(duck)
            self.all_sprites.add(duck)

    def spawn_formation(self):
        """Spawns 3-5 ducks in a horizontal line."""
        count = random.randint(3, 5)
        y_pos = random.randint(100, HEIGHT - 250)
        start_x = -150
        spacing = 120
        speed = random.uniform(3, 5)
        
        for i in range(count):
            duck = Duck(WIDTH, HEIGHT, self.assets.images['duck_sheet'], "normal")
            duck.rect.x = start_x - (i * spacing)
            duck.rect.y = y_pos
            duck.speed_x = speed
            duck.speed_y = 0
            self.ducks.add(duck)
            self.all_sprites.add(duck)

    def spawn_boss(self):
        from backend.game_logic import Boss
        self.boss_active = True
        self.trigger_boot_arrival_effect()
        boss = Boss(WIDTH, HEIGHT, self.assets.images['yellow_duck_sheet'])
        self.ducks.add(boss)
        self.all_sprites.add(boss)

    def spawn_boss_minions(self, pos):
        active_minions = sum(1 for d in self.ducks if getattr(d, 'from_boss', False) and not d.is_hit)
        spawn_count = min(BOSS_MINION_SPAWN_COUNT, BOSS_MINION_MAX_ACTIVE - active_minions)
        if spawn_count <= 0:
            return

        for _ in range(spawn_count):
            minion = Duck(WIDTH, HEIGHT, self.assets.images['duck_sheet'], "normal")
            minion.frames = [pygame.transform.scale(frame, (BOSS_MINION_SIZE, BOSS_MINION_SIZE)) for frame in minion.frames]
            minion.image = minion.frames[0]
            minion.rect = minion.image.get_rect(center=pos)
            minion.speed_x = random.uniform(-4, 4)
            minion.speed_y = random.uniform(3, 6) + (self.level * 0.15)
            minion.health = 1
            minion.from_boss = True
            self.ducks.add(minion)
            self.all_sprites.add(minion)

    def trigger_boot_arrival_effect(self):
        self.screen_shake_until = pygame.time.get_ticks() + 900
        self.screen_shake_magnitude = 14
        self.boot_message_until = pygame.time.get_ticks() + 1800

    def get_screen_shake_offset(self):
        now = pygame.time.get_ticks()
        if now >= self.screen_shake_until:
            return (0, 0)

        remaining = (self.screen_shake_until - now) / 900
        magnitude = max(1, int(self.screen_shake_magnitude * remaining))
        return (random.randint(-magnitude, magnitude), random.randint(-magnitude, magnitude))

    def draw_boot_message(self):
        if pygame.time.get_ticks() >= self.boot_message_until:
            return

        text = "boot xu\u1ea5t hi\u1ec7n"
        font = self.assets.fonts['title']
        text_surf = font.render(text, True, GOLD)
        text_rect = text_surf.get_rect(center=(WIDTH // 2, 140))

        panel = pygame.Surface((text_rect.width + 90, text_rect.height + 36), pygame.SRCALPHA)
        pygame.draw.rect(panel, (0, 0, 0, 180), panel.get_rect(), border_radius=12)
        pygame.draw.rect(panel, (*NEON_PINK, 220), panel.get_rect(), width=3, border_radius=12)
        panel_rect = panel.get_rect(center=text_rect.center)

        self.screen.blit(panel, panel_rect)
        self.screen.blit(text_surf, text_rect)

    def get_level_bg(self):
        bg_key = f'level_bg{min(self.level, 3)}'
        return self.assets.images.get(bg_key, self.assets.images['level_bg1'])

    def get_challenge_target_score(self, level):
        return BASE_CHALLENGE_TARGET * (2 ** (level - 1))

    def get_boss_reward(self):
        return self.level * BOSS_REWARD_PER_LEVEL

    def reset_game(self, mode):
        self.state = "PLAYING"
        self.confirm_exit_game = False
        self.exit_confirm_started = 0
        if self.assets.sounds.get('lobby'):
            self.assets.sounds['lobby'].stop()
        self.lobby_music_playing = False
        self.game_mode = mode
        self.score = 0
        self.missiles = 3
        self.lives = 3
        self.level = 1
        self.target_score = self.get_challenge_target_score(self.level) if mode == "CHALLENGE" else 0
        self.start_time = time.time()
        self.ducks.empty()
        self.all_sprites.empty()
        self.all_sprites.add(self.crosshair)
        self.particles.empty()
        self.feathers.empty()
        self.current_bg = self.get_level_bg()
        self.boss_active = False
        self.camera_noise = 0
        
        # Start ambient sound
        if self.assets.sounds.get('flying'):
            self.assets.sounds['flying'].play(-1) # Loop indefinitely

    def request_exit_game(self):
        self.confirm_exit_game = True
        self.exit_confirm_started = time.time()

    def cancel_exit_game(self):
        if self.exit_confirm_started and self.start_time:
            self.start_time += time.time() - self.exit_confirm_started
        self.confirm_exit_game = False
        self.exit_confirm_started = 0

    def confirm_exit_to_home(self):
        self.confirm_exit_game = False
        self.exit_confirm_started = 0
        self.boss_active = False
        self.camera_noise = 0
        self.ducks.empty()
        self.feathers.empty()
        self.particles.empty()
        self.all_sprites.empty()
        self.all_sprites.add(self.crosshair)
        if self.assets.sounds.get('flying'):
            self.assets.sounds['flying'].stop()
        self.state = "HOME"

    def handle_shooting(self, pos, trigger):
        now = time.time()
        # Reduced cooldown from 0.3 to 0.15 for faster response
        if trigger and now - self.last_shot_time > 0.15:
            if self.assets.sounds['shot']: self.assets.sounds['shot'].play()
            self.last_shot_time = now
            hit_list = [d for d in self.ducks if d.rect.collidepoint(pos)]
            for duck in hit_list:
                if not duck.is_hit:
                    duck.health -= 1
                    if duck.health <= 0:
                        duck.is_hit = True
                        points = 10
                        if getattr(duck, 'is_boss', False): points = 0
                        elif duck.duck_type == "fast": points = 25
                        elif duck.duck_type == "zigzag": points = 50
                        elif duck.duck_type == "elite": points = 100
                        self.score += points
                        if self.assets.sounds['hit']: self.assets.sounds['hit'].play()
                        self.create_explosion(duck.rect.center, NEON_PINK if duck.duck_type != "elite" else GOLD)
                    else:
                        # Feedback for hitting but not killing
                        if self.assets.sounds['hit']: self.assets.sounds['hit'].play()
                        self.create_explosion(duck.rect.center, WHITE)
            
            # Hit feathers
            for feather in self.feathers:
                if feather.rect.collidepoint(pos):
                    feather.kill()
                    if self.assets.sounds['hit']: self.assets.sounds['hit'].play()
                    self.create_explosion(feather.rect.center, WHITE)

    def handle_rocket(self, trigger):
        now = time.time()
        if trigger and self.missiles > 0 and now - self.last_rocket_time > 2.0:
            if self.assets.sounds['explosion']: self.assets.sounds['explosion'].play()
            self.last_rocket_time = now
            self.missiles -= 1
            for duck in self.ducks:
                if not duck.is_hit:
                    duck.health -= 5 # Rockets do massive damage
                    if duck.health <= 0:
                        duck.is_hit = True
                        if not getattr(duck, 'is_boss', False):
                            self.score += 5 if duck.duck_type != "elite" else 20
                        self.create_explosion(duck.rect.center, NEON_BLUE)

    def create_explosion(self, pos, color):
        explosion_img = self.assets.images.get('hit_explosion')
        if explosion_img:
            blast = Explosion(pos, explosion_img)
            self.particles.add(blast)
            self.all_sprites.add(blast)
            return

        for _ in range(20):
            p = Particle(pos, color)
            self.particles.add(p)
            self.all_sprites.add(p)

    def update_game_logic(self):
        # Camera noise decay
        if self.camera_noise > 0:
            self.camera_noise -= 0.02

        # Regular spawning if boss not active
        if not self.boss_active:
            if random.random() < 0.01: # 1% chance for formation
                self.spawn_formation()
            else:
                self.spawn_duck()
        
        # Boss Logic
        for duck in list(self.ducks):
            if getattr(duck, 'is_boss', False) and not duck.is_hit:
                # Spawn small ducks
                if time.time() - duck.last_minion_spawn_time > 2.0:
                    self.spawn_boss_minions(duck.rect.center)
                    duck.last_minion_spawn_time = time.time()

        # Update feathers and check for ground hits
        for f in self.feathers:
            if f.update(): # Returns True if hit bottom
                self.camera_noise = 2.0 # Trigger noise effect
        
        # Check for escaped ducks (lives penalty in ENDLESS)
        for duck in list(self.ducks):
            if duck.rect.right >= 0 and duck.rect.left <= WIDTH and duck.rect.bottom >= 0 and duck.rect.top <= HEIGHT:
                duck.has_entered_screen = True

            escaped_right = duck.rect.x > WIDTH + 150 and duck.speed_x > 0
            escaped_left = duck.rect.x < -150 and duck.speed_x < 0
            escaped_bottom = duck.rect.y > HEIGHT + 50 and duck.speed_y > 0
            if escaped_right or escaped_left or escaped_bottom:
                if not duck.is_hit:
                    if self.game_mode == "ENDLESS" and getattr(duck, 'has_entered_screen', False):
                        self.lives = max(0, self.lives - 1)
                    duck.kill()

        if self.game_mode == "ENDLESS":
            if self.lives <= 0:
                self.end_game()
                return
        elif self.game_mode == "QUICK":
            elapsed = time.time() - self.start_time
            if elapsed > 60:
                self.end_game()
        elif self.game_mode == "CHALLENGE":
            elapsed = time.time() - self.start_time
            if elapsed > 30:
                if self.score >= self.target_score:
                    # Check for Boss spawning at end of levels
                    if self.level % 1 == 0 and not self.boss_active: # Boss every level for now
                        self.spawn_boss()
                    
                    if not self.boss_active: # Only progress if boss is dead
                        if self.level >= MAX_CHALLENGE_LEVEL:
                            self.win_game()
                            return
                        # Level Up
                        self.level += 1
                        self.target_score = self.get_challenge_target_score(self.level)
                        self.start_time = time.time() # Reset timer for next level
                        self.ducks.empty() # Clear screen for next level
                        self.current_bg = self.get_level_bg()
                elif not self.boss_active: # If timer runs out and no boss
                    self.end_game()
            
            # Special case: Boss is dead, progress level
            if self.boss_active:
                boss_still_alive = any(getattr(d, 'is_boss', False) for d in self.ducks)
                if not boss_still_alive:
                    self.boss_active = False
                    self.score += self.get_boss_reward()
                    if self.level >= MAX_CHALLENGE_LEVEL:
                        self.win_game()
                        return
                    # Trigger level up immediately after boss
                    self.level += 1
                    self.target_score = self.get_challenge_target_score(self.level)
                    self.start_time = time.time()
                    self.ducks.empty()
                    self.current_bg = self.get_level_bg()

    def win_game(self):
        self.state = "VICTORY"
        self.ducks.empty()
        self.feathers.empty()
        self.boss_active = False
        # Stop ambient sound
        if self.assets.sounds.get('flying'):
            self.assets.sounds['flying'].stop()
            
        # Play victory feedback
        if self.assets.sounds.get('hit'):
            self.assets.sounds['hit'].play()
            
        if self.current_user:
            self.db.add_high_score(self.current_user, self.score, self.game_mode)

    def end_game(self):
        self.state = "GAMEOVER"
        self.ducks.empty()
        self.feathers.empty()
        self.particles.empty()
        self.boss_active = False
        # Stop ambient sound
        if self.assets.sounds.get('flying'):
            self.assets.sounds['flying'].stop()
            
        # Play game over sound
        if self.assets.sounds.get('explosion'):
            self.assets.sounds['explosion'].play()
            
        if self.current_user:
            self.db.add_high_score(self.current_user, self.score, self.game_mode)

    def run(self):
        while self.running:
            self.update_lobby_music()
            ret, frame = self.cap.read()
            if ret:
                if self.user_settings.get('flip_camera', 1):
                    frame = cv2.flip(frame, 1)
                
                self.tracker.process_frame(frame)
                hand_pos = self.tracker.get_hand_coords(WIDTH, HEIGHT)
                gestures = self.tracker.check_gestures()
                
                # Smooth hand movement
                if hand_pos:
                    sensitivity = self.user_settings.get('tracking_sensitivity', 1.0)
                    # Sensitivity scales the lerp factor (0.1 to 0.8)
                    actual_lerp = max(0.1, min(0.8, self.lerp_factor * (0.5 + sensitivity)))
                    self.hand_x += (hand_pos[0] - self.hand_x) * actual_lerp
                    self.hand_y += (hand_pos[1] - self.hand_y) * actual_lerp
                    hand_pos = (int(self.hand_x), int(self.hand_y))
            else:
                hand_pos = None
                gestures = {"shoot": False, "rocket": False}
            
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
                
                if self.state == "LOGIN":
                    if self.login_input.handle_event(event) == "SUBMIT": self.login()
                    if self.login_btn.handle_event(event): self.login()

                elif self.state == "HOME":
                    if self.home_buttons["play"].handle_event(event): self.state = "PLAY_SELECT"
                    if self.home_buttons["leaderboard"].handle_event(event): self.state = "LEADERBOARD"
                    if self.home_buttons["tutorial"].handle_event(event): self.state = "TUTORIAL"
                    if self.home_buttons["about"].handle_event(event): self.state = "ABOUT"
                    if self.home_buttons["settings"].handle_event(event): 
                        self.setup_settings_ui() # Refresh elements with current settings
                        self.state = "SETTINGS"
                
                elif self.state == "PLAY_SELECT":
                    if self.play_buttons["quick"].handle_event(event): 
                        self.pending_mode = "QUICK"
                        self.state = "STORY"
                        self.story_start_time = pygame.time.get_ticks()
                    if self.play_buttons["challenge"].handle_event(event): 
                        self.pending_mode = "CHALLENGE"
                        self.state = "STORY"
                        self.story_start_time = pygame.time.get_ticks()
                    if self.play_buttons["endless"].handle_event(event): 
                        self.pending_mode = "ENDLESS"
                        self.state = "STORY"
                        self.story_start_time = pygame.time.get_ticks()
                    if self.play_buttons["back"].handle_event(event): self.state = "HOME"
                
                elif self.state == "STORY":
                    if self.story_btn.handle_event(event): self.reset_game(self.pending_mode)

                elif self.state == "PLAYING":
                    if self.confirm_exit_game:
                        if self.exit_yes_btn.handle_event(event): self.confirm_exit_to_home()
                        if self.exit_no_btn.handle_event(event): self.cancel_exit_game()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.cancel_exit_game()
                    else:
                        if self.exit_game_btn.handle_event(event): self.request_exit_game()
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.request_exit_game()

                elif self.state == "SETTINGS":
                    if self.back_btn.handle_event(event):
                        self.save_settings()
                        self.state = "HOME"
                    
                    for el in self.settings_elements.values():
                        el.handle_event(event)

                elif self.state in ["LEADERBOARD", "TUTORIAL", "ABOUT", "GAMEOVER", "VICTORY"]:
                    if self.back_btn.handle_event(event): self.state = "HOME"

            # Hand Control Emulation for Menus
            if hand_pos:
                # Update crosshair for menu feedback
                self.crosshair.update(hand_pos)
                
                # Continuous interaction (Sliders)
                if self.state == "SETTINGS":
                    for key, el in self.settings_elements.items():
                        if hasattr(el, 'knob_rect'): # It's a slider
                            if el.rect.collidepoint(hand_pos) or el.knob_rect.collidepoint(hand_pos):
                                el.update_value(hand_pos[0])
                                # Immediate volume feedback
                                if key in ['music_volume', 'sfx_volume']:
                                    mv = self.settings_elements.get('music_volume')
                                    sv = self.settings_elements.get('sfx_volume')
                                    if mv and sv:
                                        self.assets.apply_volumes(mv.value, sv.value)

                if self.state == "PLAYING" and gestures["shoot"] and time.time() - self.last_menu_action_time > 0.25:
                    if self.confirm_exit_game:
                        if self.exit_yes_btn.rect.collidepoint(hand_pos):
                            self.last_menu_action_time = time.time()
                            self.confirm_exit_to_home()
                        elif self.exit_no_btn.rect.collidepoint(hand_pos):
                            self.last_menu_action_time = time.time()
                            self.cancel_exit_game()
                    elif self.exit_game_btn.rect.collidepoint(hand_pos):
                        self.last_menu_action_time = time.time()
                        self.request_exit_game()

                # Discrete interaction (Buttons/Toggles) - Reduced cooldown to 0.2
                if self.state != "PLAYING" and gestures["shoot"] and time.time() - self.last_shot_time > 0.2:
                    self.last_shot_time = time.time()
                    
                    if self.state == "LOGIN":
                        if self.login_input.rect.collidepoint(hand_pos): pass # Focus handled by mouse usually
                        if self.login_btn.rect.collidepoint(hand_pos): self.login()
                    elif self.state == "HOME":
                        for key, btn in self.home_buttons.items():
                            if btn.rect.collidepoint(hand_pos):
                                if key == "play": self.state = "PLAY_SELECT"
                                elif key == "leaderboard": self.state = "LEADERBOARD"
                                elif key == "tutorial": self.state = "TUTORIAL"
                                elif key == "about": self.state = "ABOUT"
                                elif key == "settings": 
                                    self.setup_settings_ui()
                                    self.state = "SETTINGS"
                    elif self.state == "PLAY_SELECT":
                        for key, btn in self.play_buttons.items():
                            if btn.rect.collidepoint(hand_pos):
                                if key == "back": self.state = "HOME"
                                else:
                                    self.pending_mode = key.upper()
                                    self.state = "STORY"
                                    self.story_start_time = pygame.time.get_ticks()
                    elif self.state == "STORY":
                        if self.story_btn.rect.collidepoint(hand_pos):
                            self.reset_game(self.pending_mode)
                    elif self.state == "SETTINGS":
                        if self.back_btn.rect.collidepoint(hand_pos):
                            self.save_settings()
                            self.state = "HOME"
                        for el in self.settings_elements.values():
                            if isinstance(el, UIToggle):
                                toggle_rect = pygame.Rect(el.rect.right - 80, el.rect.y, 80, el.rect.height)
                                if toggle_rect.collidepoint(hand_pos):
                                    el.value = not el.value
                                    if self.assets.sounds.get('click'): self.assets.sounds['click'].play()
                    elif self.state in ["LEADERBOARD", "TUTORIAL", "ABOUT", "GAMEOVER", "VICTORY"]:
                        if self.back_btn.rect.collidepoint(hand_pos): self.state = "HOME"
            else:
                # Mouse fallback for menu crosshair
                m_pos = pygame.mouse.get_pos()
                self.crosshair.update(m_pos)

            # Draw
            if self.state == "LOGIN":
                self.ui.draw_login_screen(self.login_input, self.login_btn)
            elif self.state == "HOME":
                self.ui.draw_home_screen(self.home_buttons, self.current_user)
            elif self.state == "PLAY_SELECT":
                self.ui.draw_play_selection(self.play_buttons)
            elif self.state == "STORY":
                self.ui.draw_story_screen(self.story_btn, self.story_start_time)
            elif self.state == "PLAYING":
                draw_screen = self.screen
                if not self.confirm_exit_game:
                    self.update_game_logic()
                if hand_pos:
                    self.crosshair.update(hand_pos)
                    if not self.confirm_exit_game:
                        self.handle_shooting(hand_pos, gestures["shoot"])
                        self.handle_rocket(gestures["rocket"])
                else:
                    m_pos = pygame.mouse.get_pos()
                    self.crosshair.update(m_pos)
                    if not self.confirm_exit_game:
                        self.handle_shooting(m_pos, pygame.mouse.get_pressed()[0])
                if not self.confirm_exit_game:
                    self.all_sprites.update()
                shake_offset = self.get_screen_shake_offset()
                if shake_offset != (0, 0):
                    self.screen = pygame.Surface((WIDTH, HEIGHT))
                    self.ui.screen = self.screen
                self.screen.blit(self.current_bg, (0, 0))
                self.all_sprites.draw(self.screen)
                self.ui.draw_camera_noise(self.camera_noise)
                self.draw_hud()
                self.exit_game_btn.draw(self.screen)
                if shake_offset != (0, 0):
                    draw_screen.fill((0, 0, 0))
                    draw_screen.blit(self.screen, shake_offset)
                    self.screen = draw_screen
                    self.ui.screen = draw_screen
                self.draw_boot_message()
            elif self.state == "LEADERBOARD":
                leaderboard = self.db.get_leaderboard()
                self.ui.draw_leaderboard(leaderboard, self.back_btn)
            elif self.state == "TUTORIAL":
                self.ui.draw_tutorial(self.back_btn)
            elif self.state == "ABOUT":
                self.ui.draw_about(self.back_btn)
            elif self.state == "SETTINGS":
                self.ui.draw_settings(self.settings_elements, self.back_btn)
            elif self.state == "GAMEOVER":
                self.ui.draw_background()
                self.ui.draw_text_centered("MISSION FAILED", 'title', 200, NEON_PINK)
                self.ui.draw_text_centered(f"FINAL SCORE: {self.score}", 'neon', 300, WHITE)
                self.back_btn.draw(self.screen)
            elif self.state == "VICTORY":
                self.ui.draw_background()
                self.ui.draw_text_centered("MISSION COMPLETE", 'title', 190, NEON_GREEN)
                self.ui.draw_text_centered("YOU CLEARED LEVEL 10", 'neon', 280, GOLD)
                self.ui.draw_text_centered(f"FINAL SCORE: {self.score}", 'neon', 350, WHITE)
                self.back_btn.draw(self.screen)

            if ret:
                # Draw small camera preview
                small_frame = cv2.resize(frame, (200, 150))
                small_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)
                frame_surf = pygame.surfarray.make_surface(np.transpose(small_frame, (1, 0, 2)))
                cam_x, cam_y = WIDTH - 220, HEIGHT - 170
                self.screen.blit(frame_surf, (cam_x, cam_y))
                
                # Draw border around preview
                border_color = NEON_GREEN if hand_pos else NEON_PINK
                pygame.draw.rect(self.screen, border_color, (cam_x, cam_y, 200, 150), 2)
                
                # Hand Detection Label
                status_text = "AI TRACKING ACTIVE" if hand_pos else "SEARCHING FOR COMMANDER..."
                status_surf = self.assets.fonts['small'].render(status_text, True, border_color)
                self.screen.blit(status_surf, (cam_x, cam_y - 25))

            if self.state == "PLAYING" and self.confirm_exit_game:
                self.draw_exit_confirmation()

            # Draw crosshair in menus/play, but keep confirmation dialogs readable.
            if not (self.state == "PLAYING" and self.confirm_exit_game):
                if hand_pos:
                    self.screen.blit(self.crosshair.image, self.crosshair.rect)
                elif self.state != "PLAYING":
                    self.screen.blit(self.crosshair.image, self.crosshair.rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        self.cap.release()
        pygame.quit()

    def draw_exit_confirmation(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 155))
        self.screen.blit(overlay, (0, 0))

        panel_rect = pygame.Rect(0, 0, 700, 300)
        panel_rect.center = (WIDTH // 2, HEIGHT // 2)
        panel = pygame.Surface(panel_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(panel, (18, 22, 26, 235), panel.get_rect(), border_radius=18)
        pygame.draw.rect(panel, (*NEON_PINK, 190), panel.get_rect(), width=3, border_radius=18)
        pygame.draw.rect(panel, (*GOLD, 110), panel.get_rect().inflate(-12, -12), width=1, border_radius=14)
        self.screen.blit(panel, panel_rect.topleft)

        title = "K\u1ebeT TH\u00daC M\u00c0N CH\u01a0I?"
        question = "B\u1ea1n c\u00f3 ch\u1eafc ch\u1eafn mu\u1ed1n k\u1ebft th\u00fac kh\u00f4ng?"
        note = "Ch\u1ecdn C\u00d3 \u0111\u1ec3 v\u1ec1 m\u00e0n h\u00ecnh ch\u00ednh."

        bold_vn_font = r"C:\Windows\Fonts\arialbd.ttf"
        regular_vn_font = r"C:\Windows\Fonts\arial.ttf"
        title_font = pygame.font.Font(bold_vn_font, 43) if os.path.exists(bold_vn_font) else pygame.font.SysFont("Tahoma", 43, bold=True)
        question_font = pygame.font.Font(bold_vn_font, 31) if os.path.exists(bold_vn_font) else pygame.font.SysFont("Tahoma", 31, bold=True)
        note_font = pygame.font.Font(regular_vn_font, 24) if os.path.exists(regular_vn_font) else pygame.font.SysFont("Tahoma", 24)
        title_surf = title_font.render(title, True, GOLD)
        question_surf = question_font.render(question, True, WHITE)
        note_surf = note_font.render(note, True, (220, 230, 240))

        self.screen.blit(title_surf, title_surf.get_rect(center=(WIDTH // 2, panel_rect.top + 58)))
        self.screen.blit(question_surf, question_surf.get_rect(center=(WIDTH // 2, panel_rect.top + 126)))
        self.screen.blit(note_surf, note_surf.get_rect(center=(WIDTH // 2, panel_rect.top + 170)))

        button_y = panel_rect.top + 210
        self.exit_yes_btn.rect = pygame.Rect(WIDTH // 2 - 195, button_y, 140, 58)
        self.exit_no_btn.rect = pygame.Rect(WIDTH // 2 + 55, button_y, 140, 58)

        self.exit_yes_btn.draw(self.screen)
        self.exit_no_btn.draw(self.screen)

    def draw_hud(self):
        hud_h = 78
        overlay = pygame.Surface((WIDTH, hud_h), pygame.SRCALPHA)
        for y in range(hud_h):
            t = y / max(1, hud_h - 1)
            alpha = int(235 - 55 * t)
            shade = int(9 + 10 * t)
            pygame.draw.line(overlay, (shade, shade + 3, shade + 7, alpha), (0, y), (WIDTH, y))
        pygame.draw.line(overlay, (26, 116, 152, 190), (0, 0), (WIDTH, 0), 4)
        pygame.draw.line(overlay, (255, 255, 255, 34), (0, hud_h - 1), (WIDTH, hud_h - 1), 1)
        self.screen.blit(overlay, (0, 0))

        label_font = pygame.font.SysFont("Arial", 19, bold=True)
        small_label_font = pygame.font.SysFont("Arial", 17, bold=True)
        score_font = pygame.font.SysFont("Arial", 47, bold=True)
        value_font = pygame.font.SysFont("Arial", 39, bold=True)
        fps_font = pygame.font.SysFont("Arial", 40, bold=True)

        mode_label = "QUICK" if self.game_mode == "QUICK" else "CHALLENGE" if self.game_mode == "CHALLENGE" else "ENDLESS"
        self._draw_lightning_icon(24, 23, GOLD)
        self._draw_shadow_text("MODE", label_font, GOLD, (44, 8))
        self._draw_shadow_text(mode_label, pygame.font.SysFont("Arial", 27, bold=True), GOLD, (44, 29))

        score_x = 242
        score_text = f"SCORE: {self.score}"
        self._draw_shadow_text(score_text, score_font, NEON_BLUE, (score_x, 17))
        score_surf = score_font.render(score_text, True, NEON_BLUE)
        self._draw_trophy_icon(score_x + score_surf.get_width() + 14, 19, NEON_BLUE)

        center_x = WIDTH // 2
        status_label = "TIMER REMAINING"
        status_value = ""
        
        if self.game_mode == "ENDLESS":
            status_label = "LIVES REMAINING"
            status_value = str(max(0, self.lives))
        elif self.game_mode == "QUICK":
            elapsed = int(time.time() - self.start_time)
            status_value = f"{max(0, 60 - elapsed)}s"
        elif self.game_mode == "CHALLENGE":
            elapsed = int(time.time() - self.start_time)
            status_label = f"LVL {self.level}  TARGET {self.target_score}"
            status_value = f"{max(0, 30 - elapsed)}s"

        label_surf = label_font.render(status_label, True, WHITE)
        self._draw_timer_icon(center_x - label_surf.get_width() // 2 - 18, 19, WHITE)
        self._draw_shadow_text(status_label, label_font, WHITE, (center_x - label_surf.get_width() // 2, 10))
        value_surf = value_font.render(status_value, True, WHITE)
        self._draw_shadow_text(status_value, value_font, WHITE, (center_x - value_surf.get_width() // 2, 31))

        missiles_x = WIDTH - 370
        self._draw_missile_icon(missiles_x, 25, NEON_GREEN, scale=0.62)
        self._draw_shadow_text("MISSILES", small_label_font, NEON_GREEN, (missiles_x + 26, 9))
        self._draw_shadow_text(str(self.missiles), value_font, NEON_GREEN, (missiles_x + 26, 32))
        for i in range(2):
            self._draw_missile_icon(missiles_x + 67 + i * 27, 45, (176, 186, 131), scale=0.62)

        fps = int(self.clock.get_fps())
        fps_color = NEON_PINK if fps < 30 else WHITE
        fps_txt = f"FPS: {fps}"
        fps_surf = fps_font.render(fps_txt, True, fps_color)
        self._draw_shadow_text(fps_txt, fps_font, fps_color, (WIDTH - fps_surf.get_width() - 18, 19))

        # Boss HP Bar
        if self.boss_active:
            boss = next((d for d in self.ducks if getattr(d, 'is_boss', False)), None)
            if boss:
                bar_width = 400
                bar_height = 20
                bar_x = (WIDTH - bar_width) // 2
                bar_y = 70
                
                # Background
                pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
                # HP Fill
                hp_pct = max(0, boss.health / boss.max_health)
                pygame.draw.rect(self.screen, (255, 0, 255), (bar_x, bar_y, int(bar_width * hp_pct), bar_height))
                # Border
                pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
                # Label
                boss_label = self.assets.fonts['small'].render("GENERAL SIR QUACKALOT", True, (255, 255, 255))
                self.screen.blit(boss_label, (bar_x, bar_y - 25))

    def _draw_shadow_text(self, text, font, color, pos):
        shadow = font.render(text, True, (0, 0, 0))
        self.screen.blit(shadow, (pos[0] + 2, pos[1] + 2))
        surf = font.render(text, True, color)
        self.screen.blit(surf, pos)

    def _draw_lightning_icon(self, x, y, color):
        points = [(x + 8, y - 13), (x + 18, y - 13), (x + 13, y - 1), (x + 21, y - 1), (x + 8, y + 18), (x + 11, y + 4), (x + 4, y + 4)]
        pygame.draw.polygon(self.screen, (0, 0, 0), [(px + 2, py + 2) for px, py in points])
        pygame.draw.polygon(self.screen, color, points)

    def _draw_trophy_icon(self, x, y, color):
        pygame.draw.rect(self.screen, color, (x + 17, y + 4, 28, 28), border_radius=3)
        pygame.draw.arc(self.screen, color, (x + 2, y + 5, 24, 22), 1.55, 4.85, 4)
        pygame.draw.arc(self.screen, color, (x + 36, y + 5, 24, 22), -1.7, 1.55, 4)
        pygame.draw.rect(self.screen, color, (x + 28, y + 31, 8, 12))
        pygame.draw.rect(self.screen, color, (x + 21, y + 43, 22, 5), border_radius=2)

    def _draw_timer_icon(self, x, y, color):
        pygame.draw.circle(self.screen, color, (x, y), 8, 2)
        pygame.draw.rect(self.screen, color, (x - 3, y - 13, 6, 3), border_radius=1)
        pygame.draw.line(self.screen, color, (x, y), (x, y - 5), 2)
        pygame.draw.line(self.screen, color, (x, y), (x + 4, y + 2), 2)

    def _draw_missile_icon(self, x, y, color, scale=1.0):
        pts = [
            (x + int(0 * scale), y + int(6 * scale)),
            (x + int(24 * scale), y - int(6 * scale)),
            (x + int(31 * scale), y - int(4 * scale)),
            (x + int(11 * scale), y + int(14 * scale)),
        ]
        pygame.draw.polygon(self.screen, color, pts)
        pygame.draw.polygon(self.screen, (80, 95, 73), [
            (x + int(4 * scale), y + int(7 * scale)),
            (x - int(5 * scale), y + int(7 * scale)),
            (x + int(1 * scale), y + int(14 * scale)),
        ])
        pygame.draw.polygon(self.screen, (80, 95, 73), [
            (x + int(14 * scale), y + int(12 * scale)),
            (x + int(12 * scale), y + int(22 * scale)),
            (x + int(20 * scale), y + int(15 * scale)),
        ])

