import pygame
import cv2
import numpy as np
import time
import sys
import random

from backend.hand_tracker import HandTracker
from backend.game_logic import Duck, Crosshair, Particle
from frontend.assets_manager import AssetsManager
from frontend.ui_system import UISystem, UIButton, UIInputField, NEON_BLUE, NEON_PINK, NEON_GREEN, GOLD, WHITE
from backend.database import DatabaseManager

# Configuration
WIDTH, HEIGHT = 1280, 720
FPS = 60

class DuckOpsGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Wing Commander: Duck Ops - AI Version 2.0")
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
        last_user = self.db.get_last_user()
        if last_user:
            self.current_user = last_user
            self.user_settings = self.db.get_player_settings(last_user)
            self.assets.apply_volumes(self.user_settings['music_volume'], self.user_settings['sfx_volume'])
            self.state = "HOME"
        else:
            self.state = "LOGIN"
            self.current_user = None
            self.user_settings = None
        
        self.game_mode = None 
        self.score = 0
        self.missiles = 3
        self.lives = 3
        self.start_time = 0
        self.last_shot_time = 0
        self.last_rocket_time = 0
        
        # Camera & AI
        self.cap = cv2.VideoCapture(0)
        self.tracker = HandTracker()
        self.current_bg = self.assets.images['level_bg1']
        
        # Groups
        self.ducks = pygame.sprite.Group()
        self.all_sprites = pygame.sprite.Group()
        self.particles = pygame.sprite.Group()
        
        self.crosshair = Crosshair(NEON_BLUE)
        self.all_sprites.add(self.crosshair)
        
        self.running = True

    def setup_ui_elements(self):
        btn_font = self.assets.fonts['main']
        bw, bh = 350, 75
        cx = WIDTH // 2 - bw // 2
        
        # Login Screen
        self.login_input = UIInputField(WIDTH // 2 - 200, HEIGHT // 2 - 40, 400, 60, btn_font, label="ENTER COMMANDER NAME")
        self.login_btn = UIButton(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 60, "START", btn_font, assets=self.assets)
        
        # Home Screen Buttons
        start_y = 250
        spacing = 90
        self.home_buttons = {
            "play": UIButton(cx, start_y, bw, bh, "Chơi", btn_font, icon="🎮", assets=self.assets),
            "tutorial": UIButton(cx, start_y + spacing, bw, bh, "Cách chơi", btn_font, icon="📖", assets=self.assets),
            "leaderboard": UIButton(cx, start_y + spacing*2, bw, bh, "Lịch sử", btn_font, icon="📜", assets=self.assets),
            "about": UIButton(cx, start_y + spacing*3, bw, bh, "Giới thiệu", btn_font, icon="💡", assets=self.assets),
            "settings": UIButton(cx, start_y + spacing*4, bw, bh, "Cài đặt", btn_font, icon="⚙️", assets=self.assets)
        }
        
        # Play Selection Buttons
        bw_wide = 600
        cx_wide = WIDTH // 2 - bw_wide // 2
        self.play_buttons = {
            "quick": UIButton(cx_wide, 180, bw_wide, bh, "Chơi nhanh (60 giây, bắn tự do)", btn_font, icon="⚡", color=NEON_GREEN, assets=self.assets),
            "challenge": UIButton(cx_wide, 270, bw_wide, bh, "Thử thách (Đạt mục tiêu, vịt nhanh dần)", btn_font, icon="🏆", color=NEON_BLUE, assets=self.assets),
            "endless": UIButton(cx_wide, 360, bw_wide, bh, "Vô tận (3 mạng, không giới hạn)", btn_font, icon="♾️", color=NEON_PINK, assets=self.assets),
            "back": UIButton(cx_wide, 500, bw_wide, bh, "QUAY LẠI", btn_font, icon="🔙", assets=self.assets)
        }
        
        # Shared Back Button
        self.back_btn = UIButton(cx, 600, bw, bh, "BACK TO MENU", btn_font, assets=self.assets)

    def login(self):
        username = self.login_input.text.strip()
        if username:
            self.db.login_player(username)
            self.db.set_last_user(username)
            self.current_user = username
            self.user_settings = self.db.get_player_settings(username)
            self.assets.apply_volumes(self.user_settings['music_volume'], self.user_settings['sfx_volume'])
            self.state = "HOME"

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

    def get_level_bg(self):
        bg_key = f'level_bg{min(self.level, 3)}'
        return self.assets.images.get(bg_key, self.assets.images['level_bg1'])

    def reset_game(self, mode):
        self.state = "PLAYING"
        self.game_mode = mode
        self.score = 0
        self.missiles = 3
        self.lives = 3
        self.level = 1
        self.target_score = 50 if mode == "CHALLENGE" else 0
        self.start_time = time.time()
        self.ducks.empty()
        self.all_sprites.empty()
        self.all_sprites.add(self.crosshair)
        self.particles.empty()
        self.current_bg = self.get_level_bg()
        
        # Start ambient sound
        if self.assets.sounds.get('flying'):
            self.assets.sounds['flying'].play(-1) # Loop indefinitely

    def handle_shooting(self, pos, trigger):
        now = time.time()
        if trigger and now - self.last_shot_time > 0.3:
            if self.assets.sounds['shot']: self.assets.sounds['shot'].play()
            self.last_shot_time = now
            hit_list = [d for d in self.ducks if d.rect.collidepoint(pos)]
            for duck in hit_list:
                if not duck.is_hit:
                    duck.health -= 1
                    if duck.health <= 0:
                        duck.is_hit = True
                        points = 10
                        if duck.duck_type == "fast": points = 25
                        elif duck.duck_type == "zigzag": points = 50
                        elif duck.duck_type == "elite": points = 100
                        self.score += points
                        if self.assets.sounds['hit']: self.assets.sounds['hit'].play()
                        self.create_explosion(duck.rect.center, NEON_PINK if duck.duck_type != "elite" else GOLD)
                    else:
                        # Feedback for hitting but not killing
                        if self.assets.sounds['hit']: self.assets.sounds['hit'].play()
                        self.create_explosion(duck.rect.center, WHITE)

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
                        self.score += 5 if duck.duck_type != "elite" else 20
                        self.create_explosion(duck.rect.center, NEON_BLUE)

    def create_explosion(self, pos, color):
        for _ in range(20):
            p = Particle(pos, color)
            self.particles.add(p)
            self.all_sprites.add(p)

    def update_game_logic(self):
        self.spawn_duck()
        
        # Check for escaped ducks (lives penalty in ENDLESS)
        for duck in self.ducks:
            if duck.rect.x > WIDTH + 150 or duck.rect.x < -150 or duck.rect.y > HEIGHT + 50:
                if not duck.is_hit:
                    if self.game_mode == "ENDLESS":
                        self.lives -= 1
                    duck.kill()

        if self.game_mode == "ENDLESS":
            if self.lives <= 0:
                self.end_game()
        elif self.game_mode == "QUICK":
            elapsed = time.time() - self.start_time
            if elapsed > 60:
                self.end_game()
        elif self.game_mode == "CHALLENGE":
            elapsed = time.time() - self.start_time
            if elapsed > 30:
                if self.score >= self.target_score:
                    # Level Up
                    self.level += 1
                    self.target_score += 50 + (self.level * 20)
                    self.start_time = time.time() # Reset timer for next level
                    self.ducks.empty() # Clear screen for next level
                    self.current_bg = self.get_level_bg()
                else:
                    self.end_game()

    def end_game(self):
        self.state = "GAMEOVER"
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
            ret, frame = self.cap.read()
            if ret:
                frame = cv2.flip(frame, 1)
                self.tracker.process_frame(frame)
                hand_pos = self.tracker.get_hand_coords(WIDTH, HEIGHT)
                gestures = self.tracker.check_gestures()
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
                    if self.home_buttons["settings"].handle_event(event): self.state = "SETTINGS"
                
                elif self.state == "PLAY_SELECT":
                    if self.play_buttons["quick"].handle_event(event): self.reset_game("QUICK")
                    if self.play_buttons["challenge"].handle_event(event): self.reset_game("CHALLENGE")
                    if self.play_buttons["endless"].handle_event(event): self.reset_game("ENDLESS")
                    if self.play_buttons["back"].handle_event(event): self.state = "HOME"
                
                elif self.state in ["LEADERBOARD", "TUTORIAL", "ABOUT", "SETTINGS", "GAMEOVER"]:
                    if self.back_btn.handle_event(event): self.state = "HOME"

            # Hand Control Emulation for Menus
            if hand_pos:
                # Update crosshair for menu feedback
                self.crosshair.update(hand_pos)
                
                # Check for "shoot" gesture to simulate button clicks
                if gestures["shoot"] and time.time() - self.last_shot_time > 0.5:
                    self.last_shot_time = time.time()
                    # Create a dummy mouse event for button interaction
                    click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {"button": 1, "pos": hand_pos})
                    
                    if self.state == "LOGIN":
                        if self.login_btn.rect.collidepoint(hand_pos): self.login()
                    elif self.state == "HOME":
                        for key, btn in self.home_buttons.items():
                            if btn.rect.collidepoint(hand_pos):
                                if key == "play": self.state = "PLAY_SELECT"
                                elif key == "leaderboard": self.state = "LEADERBOARD"
                                elif key == "tutorial": self.state = "TUTORIAL"
                                elif key == "about": self.state = "ABOUT"
                                elif key == "settings": self.state = "SETTINGS"
                    elif self.state == "PLAY_SELECT":
                        for key, btn in self.play_buttons.items():
                            if btn.rect.collidepoint(hand_pos):
                                if key == "back": self.state = "HOME"
                                else: self.reset_game(key.upper())
                    elif self.state in ["LEADERBOARD", "TUTORIAL", "ABOUT", "SETTINGS", "GAMEOVER"]:
                        if self.back_btn.rect.collidepoint(hand_pos): self.state = "HOME"

            # Draw
            if self.state == "LOGIN":
                self.ui.draw_login_screen(self.login_input, self.login_btn)
            elif self.state == "HOME":
                self.ui.draw_home_screen(self.home_buttons, self.current_user)
            elif self.state == "PLAY_SELECT":
                self.ui.draw_play_selection(self.play_buttons)
            elif self.state == "PLAYING":
                self.update_game_logic()
                if hand_pos:
                    self.crosshair.update(hand_pos)
                    self.handle_shooting(hand_pos, gestures["shoot"])
                    self.handle_rocket(gestures["rocket"])
                else:
                    m_pos = pygame.mouse.get_pos()
                    self.crosshair.update(m_pos)
                    self.handle_shooting(m_pos, pygame.mouse.get_pressed()[0])
                self.all_sprites.update()
                self.screen.blit(self.current_bg, (0, 0))
                self.all_sprites.draw(self.screen)
                self.draw_hud()
            elif self.state == "LEADERBOARD":
                leaderboard = self.db.get_leaderboard()
                self.ui.draw_leaderboard(leaderboard, self.back_btn)
            elif self.state == "TUTORIAL":
                self.ui.draw_tutorial(self.back_btn)
            elif self.state == "ABOUT":
                self.ui.draw_about(self.back_btn)
            elif self.state == "SETTINGS":
                self.ui.draw_settings(self.user_settings, self.back_btn)
            elif self.state == "GAMEOVER":
                self.ui.draw_background()
                self.ui.draw_text_centered("MISSION FAILED", 'title', 200, NEON_PINK)
                self.ui.draw_text_centered(f"FINAL SCORE: {self.score}", 'neon', 300, WHITE)
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

            # Draw crosshair in all states if hand is detected to show cursor
            if hand_pos:
                self.screen.blit(self.crosshair.image, self.crosshair.rect)

            pygame.display.flip()
            self.clock.tick(FPS)

        self.cap.release()
        pygame.quit()

    def draw_hud(self):
        overlay = pygame.Surface((WIDTH, 60), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))
        
        # Mode & Basic Info
        mode_label = "QUICK" if self.game_mode == "QUICK" else "CHALLENGE" if self.game_mode == "CHALLENGE" else "ENDLESS"
        mode_txt = self.assets.fonts['small'].render(f"MODE: {mode_label}", True, GOLD)
        self.screen.blit(mode_txt, (20, 5))
        
        score_txt = self.assets.fonts['main'].render(f"SCORE: {self.score}", True, NEON_BLUE)
        self.screen.blit(score_txt, (20, 25))
        
        if self.game_mode == "ENDLESS":
            lives_txt = self.assets.fonts['main'].render(f"LIVES: {'❤️' * self.lives}", True, NEON_PINK)
            self.screen.blit(lives_txt, (300, 20))
        elif self.game_mode == "QUICK":
            elapsed = int(time.time() - self.start_time)
            time_txt = self.assets.fonts['main'].render(f"TIME: {max(0, 60 - elapsed)}s", True, WHITE)
            self.screen.blit(time_txt, (300, 20))
        elif self.game_mode == "CHALLENGE":
            elapsed = int(time.time() - self.start_time)
            level_txt = self.assets.fonts['main'].render(f"LVL {self.level}", True, NEON_GREEN)
            target_txt = self.assets.fonts['small'].render(f"TARGET: {self.target_score}", True, GOLD)
            time_txt = self.assets.fonts['main'].render(f"TIME: {max(0, 30 - elapsed)}s", True, WHITE)
            
            self.screen.blit(level_txt, (300, 20))
            self.screen.blit(target_txt, (450, 25))
            self.screen.blit(time_txt, (650, 20))
            
        missile_txt = self.assets.fonts['main'].render(f"MISSILES: {self.missiles}", True, NEON_GREEN)
        self.screen.blit(missile_txt, (WIDTH - 250, 20))

if __name__ == "__main__":
    game = DuckOpsGame()
    game.run()
