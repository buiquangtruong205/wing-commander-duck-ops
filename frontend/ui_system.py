import pygame

# Colors
NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_GREEN = (57, 255, 20)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 20)
GLASS_BG = (255, 255, 255, 30) # Very subtle white for glass effect
GLASS_BORDER = (255, 255, 255, 80)

class UIButton:
    def __init__(self, x, y, width, height, text, font, icon=None, color=WHITE, hover_color=GOLD, assets=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.icon = icon
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.assets = assets

    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Draw Glassmorphism Base
        glass_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        # Background
        pygame.draw.rect(glass_surf, (100, 100, 0, 100) if self.is_hovered else (50, 50, 50, 120), 
                         (0, 0, self.rect.width, self.rect.height), border_radius=15)
        # Border
        pygame.draw.rect(glass_surf, (*current_color, 150), 
                         (0, 0, self.rect.width, self.rect.height), width=2, border_radius=15)
        screen.blit(glass_surf, self.rect.topleft)

        # Draw Icon (if exists)
        text_offset = 0
        if self.icon and isinstance(self.icon, (str, bytes)):
            icon_font = pygame.font.SysFont("Segoe UI Emoji", int(self.rect.height * 0.5))
            icon_surf = icon_font.render(self.icon, True, WHITE)
            icon_rect = icon_surf.get_rect(midleft=(self.rect.left + 20, self.rect.centery))
            screen.blit(icon_surf, icon_rect)
            text_offset = 40

        # Draw Text
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 20 + text_offset, self.rect.centery))
        screen.blit(text_surf, text_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                if self.assets and self.assets.sounds.get('click'):
                    self.assets.sounds['click'].play()
                return True
        return False

class UIInputField:
    def __init__(self, x, y, width, height, font, label=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.font = font
        self.label = label
        self.text = ""
        self.active = True
        self.cursor_visible = True
        self.last_cursor_toggle = 0

    def draw(self, screen):
        # Draw Label
        if self.label:
            lbl_surf = self.font.render(self.label, True, (255, 215, 0))
            screen.blit(lbl_surf, (self.rect.x, self.rect.y - 40))

        # Draw Box
        color = (255, 215, 0) if self.active else (150, 150, 150)
        glass_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass_surf, (50, 50, 50, 180), (0, 0, self.rect.width, self.rect.height), border_radius=10)
        pygame.draw.rect(glass_surf, color, (0, 0, self.rect.width, self.rect.height), width=2, border_radius=10)
        screen.blit(glass_surf, self.rect.topleft)

        # Draw Text
        display_text = self.text
        if self.active:
            now = pygame.time.get_ticks()
            if now - self.last_cursor_toggle > 500:
                self.cursor_visible = not self.cursor_visible
                self.last_cursor_toggle = now
            if self.cursor_visible:
                display_text += "|"

        txt_surf = self.font.render(display_text, True, (255, 255, 255))
        txt_rect = txt_surf.get_rect(midleft=(self.rect.x + 15, self.rect.centery))
        screen.blit(txt_surf, txt_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return "SUBMIT"
            else:
                if len(self.text) < 20: # Limit length
                    self.text += event.unicode
        return None

class UISystem:
    def __init__(self, screen, assets):
        self.screen = screen
        self.assets = assets
        self.width = screen.get_width()
        self.height = screen.get_height()
        
    def draw_background(self, bg_key='menu_bg'):
        if bg_key in self.assets.images:
            self.screen.blit(self.assets.images[bg_key], (0, 0))
        else:
            self.screen.fill(BLACK)
        
        # Overlay subtle grid/cyberpunk scanlines
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 4):
            pygame.draw.line(overlay, (0, 255, 255, 10), (0, y), (self.width, y))
        self.screen.blit(overlay, (0, 0))

    def draw_text_centered(self, text, font_key, y_pos, color=WHITE):
        font = self.assets.fonts.get(font_key, self.assets.fonts['main'])
        text_surf = font.render(text, True, color)
        rect = text_surf.get_rect(center=(self.width // 2, y_pos))
        
        # Shadow/Glow effect
        shadow = font.render(text, True, (0, 0, 0))
        self.screen.blit(shadow, (rect.x + 2, rect.y + 2))
        self.screen.blit(text_surf, rect)

    def draw_home_screen(self, buttons, username):
        self.draw_background()
        
        # Title "DUCK OPS" with style
        title_font = self.assets.fonts['title']
        sub_font = self.assets.fonts['main']
        
        # Yellow Title with shadow for 3D effect
        title_text = "DUCK OPS"
        t_shadow = title_font.render(title_text, True, (150, 100, 0))
        t_main = title_font.render(title_text, True, GOLD)
        
        t_rect = t_main.get_rect(center=(self.width // 2, 100))
        self.screen.blit(t_shadow, (t_rect.x + 4, t_rect.y + 4))
        self.screen.blit(t_main, t_rect)
        
        # "WING COMMANDER"
        wc_text = "W I N G   C O M M A N D E R"
        wc_surf = sub_font.render(wc_text, True, WHITE)
        wc_rect = wc_surf.get_rect(center=(self.width // 2, 160))
        self.screen.blit(wc_surf, wc_rect)
        
        # Commander info
        self.draw_text_centered(f"👮 Chỉ huy: {username}", 'small', 200, GOLD)
        
        for btn in buttons.values():
            btn.draw(self.screen)
            
        # Footer
        footer_txt = "© 2026 Duck Ops Team — AI Vision Powered"
        self.draw_text_centered(footer_txt, 'small', self.height - 40, (200, 200, 200))

    def draw_login_screen(self, input_field, start_button):
        self.draw_background()
        self.draw_text_centered("MISSION INITIALIZATION", 'neon', 150, GOLD)
        input_field.draw(self.screen)
        start_button.draw(self.screen)

    def draw_leaderboard(self, data, back_button):
        self.draw_background()
        self.draw_text_centered("LEADERBOARD", 'neon', 80, NEON_BLUE)
        
        # Headers
        y = 180
        header_font = self.assets.fonts['main']
        h_rank = header_font.render("RANK", True, NEON_PINK)
        h_name = header_font.render("NAME", True, NEON_PINK)
        h_score = header_font.render("SCORE", True, NEON_PINK)
        
        self.screen.blit(h_rank, (self.width//2 - 250, y))
        self.screen.blit(h_name, (self.width//2 - 100, y))
        self.screen.blit(h_score, (self.width//2 + 150, y))
        
        y += 50
        pygame.draw.line(self.screen, NEON_BLUE, (self.width//2 - 300, y), (self.width//2 + 300, y), 2)
        
        # Rows
        row_font = self.assets.fonts['small']
        for i, entry in enumerate(data):
            y += 40
            r_txt = row_font.render(f"#{i+1}", True, WHITE)
            n_txt = row_font.render(entry['name'], True, WHITE)
            s_txt = row_font.render(str(entry['score']), True, NEON_GREEN)
            
            self.screen.blit(r_txt, (self.width//2 - 250, y))
            self.screen.blit(n_txt, (self.width//2 - 100, y))
            self.screen.blit(s_txt, (self.width//2 + 150, y))

        back_button.draw(self.screen)

    def draw_tutorial(self, back_button):
        self.draw_background()
        self.draw_text_centered("HOW TO PLAY", 'neon', 80, NEON_BLUE)
        
        instructions = [
            "1. DI CHUYỂN NGÓN TRỎ ĐỂ ĐIỀU KHIỂN TÂM SÚNG",
            "2. GẬP NGÓN TRỎ ĐỂ BẮN",
            "3. DÙNG CỬ CHỈ CHỮ V ĐỂ PHÓNG TÊN LỬA",
            "4. BẮN VỊT ĐỂ KIẾM ĐIỂM",
            "5. VỊT SẼ BAY NGẪU NHIÊN VÀ RA KHỎI MÀN HÌNH",
            "",
            "MẸO: VỊT CÀNG NHANH ĐIỂM CÀNG CAO!"
        ]
        
        y = 200
        for line in instructions:
            self.draw_text_centered(line, 'small', y, WHITE)
            y += 40
            
        back_button.draw(self.screen)

    def draw_shop(self, items, back_button):
        self.draw_background()
        self.draw_text_centered("CYBER SHOP", 'neon', 80, NEON_PINK)
        
        y = 180
        for item in items:
            pygame.draw.rect(self.screen, DARK_GRAY, (self.width//2 - 300, y, 600, 60), border_radius=5)
            pygame.draw.rect(self.screen, NEON_BLUE, (self.width//2 - 300, y, 600, 60), width=1, border_radius=5)
            
            name_txt = self.assets.fonts['main'].render(item['name'], True, WHITE)
            price_txt = self.assets.fonts['main'].render(f"{item['price']}G", True, NEON_GREEN)
            
            self.screen.blit(name_txt, (self.width//2 - 280, y + 15))
            self.screen.blit(price_txt, (self.width//2 + 180, y + 15))
            y += 80

        back_button.draw(self.screen)

    def draw_settings(self, settings, back_button):
        self.draw_background()
        self.draw_text_centered("SETTINGS", 'neon', 80, NEON_BLUE)
        
        y = 200
        for key, val in settings.items():
            label = self.assets.fonts['main'].render(key.upper(), True, WHITE)
            status = "ON" if val else "OFF"
            color = NEON_GREEN if val else NEON_PINK
            status_txt = self.assets.fonts['main'].render(status, True, color)
            
            self.screen.blit(label, (self.width//2 - 200, y))
            self.screen.blit(status_txt, (self.width//2 + 100, y))
            y += 60
            
        back_button.draw(self.screen)

    def draw_play_selection(self, buttons):
        self.draw_background()
        self.draw_text_centered("SELECT MODE", 'neon', 80, NEON_BLUE)
        for btn in buttons.values():
            btn.draw(self.screen)

    def draw_about(self, back_button):
        self.draw_background()
        self.draw_text_centered("ABOUT DUCK OPS", 'neon', 80, NEON_PINK)
        
        info = [
            "VERSION: 2.0.0 (AI ENHANCED)",
            "DEVELOPER: WING COMMANDER TEAM",
            "POWERED BY: PYGAME & MEDIAPIPE",
            "",
            "CONTACT: DUCKOPS@CYBERPUNK.NET",
            "© 2026 ALL RIGHTS RESERVED"
        ]
        
        y = 220
        for line in info:
            self.draw_text_centered(line, 'small', y, WHITE)
            y += 45
            
        back_button.draw(self.screen)
