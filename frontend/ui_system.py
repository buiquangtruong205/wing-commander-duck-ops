import pygame
import random
import math

NEON_BLUE = (0, 255, 255)
NEON_PINK = (255, 0, 255)
NEON_GREEN = (57, 255, 20)
GOLD = (255, 215, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_GRAY = (20, 20, 20)
GLASS_BG = (255, 255, 255, 30)
GLASS_BORDER = (255, 255, 255, 80)

class UIButton:
    def __init__(self, x, y, width, height, text, font, icon=None, icon_right=None, color=WHITE, hover_color=GOLD, assets=None, style='default', image_key='menu_button'):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.icon = icon
        self.icon_right = icon_right
        self.color = color
        self.hover_color = hover_color
        self.is_hovered = False
        self.assets = assets
        self.style = style
        self.image_key = image_key

    def draw(self, screen):
        if self.style == 'wood':
            self._draw_wood(screen)
            return
        current_color = self.hover_color if self.is_hovered else self.color
        if self.is_hovered:
            glow_surf = pygame.Surface((self.rect.width + 10, self.rect.height + 10), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (*current_color, 50), (0, 0, self.rect.width + 10, self.rect.height + 10), border_radius=18)
            screen.blit(glow_surf, (self.rect.x - 5, self.rect.y - 5))
        glass_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        bg_alpha = 150 if self.is_hovered else 100
        pygame.draw.rect(glass_surf, (30, 30, 30, bg_alpha), (0, 0, self.rect.width, self.rect.height), border_radius=15)
        pygame.draw.rect(glass_surf, (*current_color, 180), (0, 0, self.rect.width, self.rect.height), width=2, border_radius=15)
        screen.blit(glass_surf, self.rect.topleft)
        text_offset = 0
        if self.icon and isinstance(self.icon, (str, bytes)):
            icon_font = pygame.font.SysFont("Segoe UI Emoji", int(self.rect.height * 0.4))
            icon_surf = icon_font.render(self.icon, True, WHITE)
            icon_rect = icon_surf.get_rect(midleft=(self.rect.left + 20, self.rect.centery))
            screen.blit(icon_surf, icon_rect)
            text_offset = 45
        text_surf = self.font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(midleft=(self.rect.left + 20 + text_offset, self.rect.centery))
        screen.blit(text_surf, text_rect)

    def _draw_wood(self, screen):
        menu_button = self.assets.images.get(self.image_key) if self.assets else None
        if menu_button:
            target_rect = self.rect.inflate(76, 60)
            target_rect.center = self.rect.center

            button_surf = pygame.transform.smoothscale(menu_button, target_rect.size)
            screen.blit(button_surf, target_rect.topleft)

            tc = (255, 255, 240) if self.is_hovered else (255, 245, 215)
            text_center = (self.rect.left + int(self.rect.width * 0.42), self.rect.centery + 1)
            sh = self.font.render(self.text, True, (48, 29, 14))
            screen.blit(sh, sh.get_rect(center=(text_center[0] + 3, text_center[1] + 4)))
            ts = self.font.render(self.text, True, tc)
            screen.blit(ts, ts.get_rect(center=text_center))
            return

        w, h = self.rect.width, self.rect.height
        shadow_surf = pygame.Surface((w + 28, h + 22), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (25, 18, 8, 120), (12, 10, w + 4, h + 4), border_radius=8)
        screen.blit(shadow_surf, (self.rect.x - 14, self.rect.y - 5))

        plate_rect = self.rect.inflate(18, 10)
        self._draw_metal_frame(screen, plate_rect, radius=7)

        btn_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for row in range(h):
            t = row / h
            cf = max(0, min(1, 1 - abs(t - 0.42) * 2.2))
            r = min(255, int(92 + 60 * cf) + (22 if self.is_hovered else 0))
            g = min(255, int(52 + 38 * cf) + (14 if self.is_hovered else 0))
            b = min(255, int(24 + 20 * cf) + (8 if self.is_hovered else 0))
            pygame.draw.line(btn_surf, (r, g, b), (0, row), (w, row))

        for yy, drift in ((int(h * 0.26), -1), (int(h * 0.55), 1), (int(h * 0.78), 0)):
            pygame.draw.line(btn_surf, (65, 36, 18, 70), (16, yy), (w - 18, yy + drift), 1)
        for knot_x in (int(w * 0.28), int(w * 0.67)):
            knot_y = int(h * (0.36 if knot_x < w // 2 else 0.65))
            pygame.draw.ellipse(btn_surf, (69, 37, 18, 55), (knot_x - 22, knot_y - 7, 44, 14), 1)

        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=6)
        btn_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(btn_surf, self.rect.topleft)

        pygame.draw.line(screen, (245, 203, 120), (self.rect.left + 10, self.rect.top + 5), (self.rect.right - 12, self.rect.top + 5), 2)
        pygame.draw.line(screen, (48, 28, 16), (self.rect.left + 10, self.rect.bottom - 5), (self.rect.right - 12, self.rect.bottom - 5), 2)
        bc = (245, 213, 136) if self.is_hovered else (176, 142, 83)
        pygame.draw.rect(screen, (56, 36, 21), self.rect, width=5, border_radius=6)
        pygame.draw.rect(screen, bc, self.rect.inflate(-4, -4), width=2, border_radius=5)

        ir = self.rect.inflate(-14, -14)
        isf = pygame.Surface((ir.width, ir.height), pygame.SRCALPHA)
        pygame.draw.rect(isf, (255, 225, 160, 36), (0, 0, ir.width, ir.height), width=1, border_radius=4)
        screen.blit(isf, ir.topleft)

        left_badge = pygame.Rect(self.rect.left - 30, self.rect.top - 8, 72, h + 16)
        right_badge = pygame.Rect(self.rect.right - 42, self.rect.top - 8, 72, h + 16)
        self._draw_icon_badge(screen, left_badge, self.icon)
        if self.icon_right:
            self._draw_icon_badge(screen, right_badge, self.icon_right)

        tc = (255, 255, 240) if self.is_hovered else (255, 245, 215)
        text_x = self.rect.left + 72
        sh = self.font.render(self.text, True, (43, 25, 12))
        screen.blit(sh, sh.get_rect(midleft=(text_x + 2, self.rect.centery + 3)))
        ts = self.font.render(self.text, True, tc)
        screen.blit(ts, ts.get_rect(midleft=(text_x, self.rect.centery)))

    def _draw_metal_frame(self, screen, rect, radius=8):
        pygame.draw.rect(screen, (42, 45, 43), rect, border_radius=radius)
        pygame.draw.rect(screen, (210, 190, 150), rect.inflate(-4, -4), width=2, border_radius=radius)
        pygame.draw.rect(screen, (32, 28, 24), rect, width=3, border_radius=radius)
        pygame.draw.line(screen, (250, 232, 184), (rect.left + 9, rect.top + 4), (rect.right - 9, rect.top + 4), 1)

    def _draw_icon_badge(self, screen, rect, icon):
        if not icon:
            return
        cx, cy = rect.center
        badge = pygame.Surface(rect.size, pygame.SRCALPHA)
        local = badge.get_rect()
        pygame.draw.polygon(
            badge,
            (76, 62, 48, 245),
            [(local.centerx, 3), (local.right - 6, 16), (local.right - 12, local.bottom - 12), (local.centerx, local.bottom - 3), (12, local.bottom - 12), (6, 16)]
        )
        pygame.draw.polygon(
            badge,
            (206, 180, 120, 255),
            [(local.centerx, 8), (local.right - 13, 19), (local.right - 18, local.bottom - 17), (local.centerx, local.bottom - 9), (18, local.bottom - 17), (13, 19)],
            width=3
        )
        pygame.draw.circle(badge, (118, 78, 45, 230), local.center, min(rect.width, rect.height) // 3)
        screen.blit(badge, rect.topleft)

        color = (242, 222, 170)
        dark = (45, 32, 24)
        r = min(rect.width, rect.height) // 4
        if icon in ("shield", "medal"):
            pts = [(cx, cy - r), (cx + r, cy - 4), (cx + r - 4, cy + r), (cx, cy + r + 7), (cx - r + 4, cy + r), (cx - r, cy - 4)]
            pygame.draw.polygon(screen, dark, pts)
            pygame.draw.polygon(screen, color, pts, 3)
        elif icon in ("book", "book_open"):
            pygame.draw.rect(screen, dark, (cx - r - 8, cy - r, r + 8, r * 2), border_radius=3)
            pygame.draw.rect(screen, dark, (cx, cy - r, r + 8, r * 2), border_radius=3)
            pygame.draw.rect(screen, color, (cx - r - 8, cy - r, r + 8, r * 2), 2, border_radius=3)
            pygame.draw.rect(screen, color, (cx, cy - r, r + 8, r * 2), 2, border_radius=3)
            pygame.draw.line(screen, color, (cx, cy - r), (cx, cy + r), 2)
        elif icon == "scroll":
            pygame.draw.rect(screen, color, (cx - r, cy - r, r * 2, r * 2), 2, border_radius=3)
            pygame.draw.line(screen, color, (cx - r + 5, cy - 4), (cx + r - 5, cy - 4), 2)
            pygame.draw.line(screen, color, (cx - r + 5, cy + 5), (cx + r - 7, cy + 5), 2)
        elif icon == "duck":
            pygame.draw.circle(screen, color, (cx - 3, cy - 2), r - 3, 2)
            pygame.draw.polygon(screen, color, [(cx + r - 4, cy - 4), (cx + r + 9, cy), (cx + r - 4, cy + 4)])
            pygame.draw.arc(screen, color, (cx - r, cy + 1, r * 2, r), math.pi, math.tau, 2)
        elif icon == "bulb":
            pygame.draw.circle(screen, color, (cx, cy - 5), r - 3, 2)
            pygame.draw.rect(screen, color, (cx - 7, cy + r - 6, 14, 8), 2)
            pygame.draw.line(screen, color, (cx - 10, cy + r + 5), (cx + 10, cy + r + 5), 2)
        elif icon in ("gear", "gears"):
            pygame.draw.circle(screen, color, (cx, cy), r, 2)
            pygame.draw.circle(screen, color, (cx, cy), 5, 2)
            for i in range(8):
                ang = i * math.pi / 4
                x1 = cx + int(math.cos(ang) * (r + 1))
                y1 = cy + int(math.sin(ang) * (r + 1))
                x2 = cx + int(math.cos(ang) * (r + 8))
                y2 = cy + int(math.sin(ang) * (r + 8))
                pygame.draw.line(screen, color, (x1, y1), (x2, y2), 2)
        elif icon == "gamepad":
            pygame.draw.rect(screen, color, (cx - r - 8, cy - 10, r * 2 + 16, 20), 3, border_radius=8)
            pygame.draw.line(screen, color, (cx - r, cy), (cx - r + 12, cy), 2)
            pygame.draw.line(screen, color, (cx - r + 6, cy - 6), (cx - r + 6, cy + 6), 2)
            pygame.draw.circle(screen, color, (cx + r - 5, cy - 3), 3)
            pygame.draw.circle(screen, color, (cx + r + 4, cy + 4), 3)
        else:
            mark = pygame.font.SysFont("Arial", 28, bold=True).render(str(icon)[:1], True, color)
            screen.blit(mark, mark.get_rect(center=(cx, cy)))

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
    def __init__(self, x, y, width, height, font, label=''):
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

class UISlider:
    def __init__(self, x, y, width, height, label, font, value=0.5, color=NEON_BLUE):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.font = font
        self.value = value # 0.0 to 1.0
        self.color = color
        self.is_dragging = False
        self.knob_rect = pygame.Rect(0, 0, 20, height + 10)
        self.update_knob_pos()

    def update_knob_pos(self):
        self.knob_rect.centerx = self.rect.x + (self.value * self.rect.width)
        self.knob_rect.centery = self.rect.centery

    def draw(self, screen):
        # Draw Label
        lbl_surf = self.font.render(self.label, True, WHITE)
        screen.blit(lbl_surf, (self.rect.x, self.rect.y - 35))

        # Draw Background Track
        pygame.draw.rect(screen, (50, 50, 50), self.rect, border_radius=5)
        # Draw Filled Track
        fill_width = int(self.value * self.rect.width)
        if fill_width > 0:
            pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y, fill_width, self.rect.height), border_radius=5)
        
        # Draw Knob
        pygame.draw.rect(screen, WHITE, self.knob_rect, border_radius=5)
        # Percentage text
        pct_txt = self.font.render(f"{int(self.value * 100)}%", True, WHITE)
        screen.blit(pct_txt, (self.rect.right + 15, self.rect.y - 5))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.knob_rect.collidepoint(event.pos) or self.rect.collidepoint(event.pos):
                self.is_dragging = True
                self.update_value(event.pos[0])
                return True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                self.update_value(event.pos[0])
                return True
        return False

    def update_value(self, mouse_x):
        rel_x = mouse_x - self.rect.x
        self.value = max(0.0, min(1.0, rel_x / self.rect.width))
        self.update_knob_pos()

class UIToggle:
    def __init__(self, x, y, width, height, label, font, value=False, color=NEON_GREEN):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.font = font
        self.value = value
        self.color = color
        self.is_hovered = False

    def draw(self, screen):
        # Draw Label
        lbl_surf = self.font.render(self.label, True, WHITE)
        screen.blit(lbl_surf, (self.rect.x, self.rect.y + (self.rect.height - lbl_surf.get_height()) // 2))

        # Draw Toggle Box
        toggle_rect = pygame.Rect(self.rect.right - 80, self.rect.y, 80, self.rect.height)
        pygame.draw.rect(screen, (50, 50, 50), toggle_rect, border_radius=15)
        
        # Knob
        knob_color = self.color if self.value else NEON_PINK
        knob_x = toggle_rect.right - 35 if self.value else toggle_rect.left + 5
        pygame.draw.rect(screen, knob_color, (knob_x, toggle_rect.y + 5, 30, toggle_rect.height - 10), border_radius=12)
        
        # Status text
        status = "ON" if self.value else "OFF"
        status_surf = self.font.render(status, True, knob_color)
        status_rect = status_surf.get_rect(midright=(toggle_rect.left - 15, self.rect.centery))
        screen.blit(status_surf, status_rect)

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            toggle_rect = pygame.Rect(self.rect.right - 80, self.rect.y, 80, self.rect.height)
            if toggle_rect.collidepoint(event.pos):
                self.value = not self.value
                return True
        return False

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
        
        if bg_key != 'menu_bg':
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
        
        title_font = self.assets.fonts['title']
        sub_font = self.assets.fonts['main']
        small_font = self.assets.fonts['small']
        cx = self.width // 2
        
        # === "DUCK OPS" Title with multi-layer glow ===
        title_text = "DUCK OPS"
        
        # Outer glow layer (large, soft)
        glow_surf = pygame.Surface((self.width, 160), pygame.SRCALPHA)
        for offset in range(8, 0, -2):
            alpha = 25 - offset * 2
            glow_color = (255, 200, 0, max(alpha, 5))
            g_text = title_font.render(title_text, True, glow_color[:3])
            g_text.set_alpha(glow_color[3])
            for dx in [-offset, 0, offset]:
                for dy in [-offset, 0, offset]:
                    g_rect = g_text.get_rect(center=(cx + dx, 70 + dy))
                    glow_surf.blit(g_text, g_rect)
        self.screen.blit(glow_surf, (0, 0))
        
        # Dark outline (depth)
        for dx in [-3, -2, 0, 2, 3]:
            for dy in [-3, -2, 0, 2, 3]:
                outline = title_font.render(title_text, True, (80, 50, 0))
                o_rect = outline.get_rect(center=(cx + dx, 95 + dy))
                self.screen.blit(outline, o_rect)
        
        # Drop shadow
        t_shadow = title_font.render(title_text, True, (120, 80, 0))
        t_rect = t_shadow.get_rect(center=(cx + 3, 98))
        self.screen.blit(t_shadow, t_rect)
        
        # Main title
        t_main = title_font.render(title_text, True, GOLD)
        t_rect = t_main.get_rect(center=(cx, 95))
        self.screen.blit(t_main, t_rect)
        
        # Highlight (top-half bright line)
        highlight = title_font.render(title_text, True, (255, 245, 150))
        h_surf = pygame.Surface(t_rect.size, pygame.SRCALPHA)
        h_surf.blit(highlight, (0, 0))
        h_surf.set_alpha(100)
        self.screen.blit(h_surf, t_rect)
        
        # === Decorative separator lines ===
        line_y = 145
        line_half_w = 180
        for i in range(line_half_w):
            alpha = int(255 * (i / line_half_w))
            line_surf = pygame.Surface((1, 2), pygame.SRCALPHA)
            line_surf.fill((255, 215, 0, alpha))
            self.screen.blit(line_surf, (cx - line_half_w + i, line_y))
        for i in range(line_half_w):
            alpha = int(255 * (1 - i / line_half_w))
            line_surf = pygame.Surface((1, 2), pygame.SRCALPHA)
            line_surf.fill((255, 215, 0, alpha))
            self.screen.blit(line_surf, (cx + i, line_y))
        
        # Small diamond in center
        diamond_pts = [(cx, line_y - 4), (cx + 5, line_y + 1), (cx, line_y + 6), (cx - 5, line_y + 1)]
        pygame.draw.polygon(self.screen, GOLD, diamond_pts)
        
        # === "WING COMMANDER" subtitle ===
        wc_text = "W I N G   C O M M A N D E R"
        wc_shadow = sub_font.render(wc_text, True, (50, 50, 50))
        wc_shadow_rect = wc_shadow.get_rect(center=(cx + 2, 170))
        self.screen.blit(wc_shadow, wc_shadow_rect)
        wc_surf = sub_font.render(wc_text, True, (220, 230, 240))
        wc_rect = wc_surf.get_rect(center=(cx, 168))
        self.screen.blit(wc_surf, wc_rect)
        
        # === Commander badge panel ===
        badge_text = f"CHI HUY: {username.upper()}"
        badge_surf = small_font.render(badge_text, True, GOLD)
        badge_w = badge_surf.get_width() + 60
        badge_h = 36
        badge_x = cx - badge_w // 2
        badge_y = 195
        
        # Glass badge background
        badge_bg = pygame.Surface((badge_w, badge_h), pygame.SRCALPHA)
        pygame.draw.rect(badge_bg, (0, 0, 0, 120), (0, 0, badge_w, badge_h), border_radius=18)
        pygame.draw.rect(badge_bg, (255, 215, 0, 100), (0, 0, badge_w, badge_h), width=1, border_radius=18)
        self.screen.blit(badge_bg, (badge_x, badge_y))
        
        # Star icon (text-based, no emoji)
        star_font = pygame.font.SysFont("Arial", 18, bold=True)
        star = star_font.render("★", True, GOLD)
        self.screen.blit(star, (badge_x + 12, badge_y + 8))
        
        # Commander name
        badge_rect = badge_surf.get_rect(midleft=(badge_x + 35, badge_y + badge_h // 2))
        self.screen.blit(badge_surf, badge_rect)
        
        for btn in buttons.values():
            btn.draw(self.screen)

    def draw_home_screen(self, buttons, username):
        self.draw_background()
        cx = self.width // 2
        self._draw_home_title(cx)
        self._draw_commander_badge(cx, 154, f"CHI HUY: {(username or 'TRUONG').upper()}")

        for btn in buttons.values():
            btn.draw(self.screen)

    def _draw_home_title(self, cx):
        title_font = pygame.font.SysFont("Georgia", 72, bold=True)
        subtitle_font = pygame.font.SysFont("Arial", 30, bold=True)
        title = "DUCK OPS"
        y = 70

        for dx, dy in [(-5, 0), (5, 0), (0, -5), (0, 5), (-3, -3), (3, 3), (-3, 3), (3, -3)]:
            surf = title_font.render(title, True, (62, 42, 26))
            self.screen.blit(surf, surf.get_rect(center=(cx + dx, y + dy)))

        shadow = title_font.render(title, True, (28, 23, 18))
        self.screen.blit(shadow, shadow.get_rect(center=(cx + 4, y + 6)))
        main = title_font.render(title, True, (192, 154, 84))
        main_rect = main.get_rect(center=(cx, y))
        self.screen.blit(main, main_rect)
        top = title_font.render(title, True, (255, 230, 156))
        top.set_alpha(120)
        self.screen.blit(top, main_rect.move(0, -2))

        subtitle = "W I N G   C O M M A N D E R"
        for dx, dy in [(-2, 0), (2, 0), (0, 2)]:
            s = subtitle_font.render(subtitle, True, (63, 54, 47))
            self.screen.blit(s, s.get_rect(center=(cx + dx, 126 + dy)))
        s = subtitle_font.render(subtitle, True, (229, 224, 211))
        self.screen.blit(s, s.get_rect(center=(cx, 124)))

    def _draw_commander_badge(self, cx, y, text):
        font = pygame.font.SysFont("Arial", 23, bold=True)
        text_surf = font.render(text, True, (64, 45, 27))
        w = text_surf.get_width() + 72
        rect = pygame.Rect(cx - w // 2, y, w, 38)
        pygame.draw.rect(self.screen, (89, 69, 48), rect.inflate(8, 8), border_radius=5)
        pygame.draw.rect(self.screen, (221, 195, 143), rect, border_radius=5)
        pygame.draw.rect(self.screen, (61, 43, 27), rect, width=3, border_radius=5)
        pygame.draw.line(self.screen, (255, 239, 180), (rect.left + 12, rect.top + 5), (rect.right - 12, rect.top + 5), 2)
        pygame.draw.circle(self.screen, (67, 45, 28), (rect.left + 19, rect.centery), 4)
        pygame.draw.circle(self.screen, (67, 45, 28), (rect.right - 19, rect.centery), 4)
        self.screen.blit(text_surf, text_surf.get_rect(center=rect.center))

    def draw_login_screen(self, input_field, start_button):
        self.draw_background()
        self.draw_text_centered("MISSION INITIALIZATION", 'neon', 150, GOLD)
        input_field.draw(self.screen)
        start_button.draw(self.screen)

    def draw_leaderboard(self, data, back_button):
        self.draw_background()
        self.draw_text_centered("HIGH SCORES BY MODE", 'neon', 80, NEON_BLUE)
        
        # Headers
        y = 180
        header_font = self.assets.fonts['main']
        h_rank = header_font.render("RANK", True, NEON_PINK)
        h_name = header_font.render("NAME", True, NEON_PINK)
        h_mode = header_font.render("MODE", True, NEON_PINK)
        h_score = header_font.render("SCORE", True, NEON_PINK)
        
        self.screen.blit(h_rank, (self.width//2 - 360, y))
        self.screen.blit(h_name, (self.width//2 - 210, y))
        self.screen.blit(h_mode, (self.width//2 + 20, y))
        self.screen.blit(h_score, (self.width//2 + 220, y))
        
        y += 50
        pygame.draw.line(self.screen, NEON_BLUE, (self.width//2 - 410, y), (self.width//2 + 410, y), 2)
        
        # Rows
        row_font = self.assets.fonts['small']
        for i, entry in enumerate(data):
            y += 40
            r_txt = row_font.render(f"#{i+1}", True, WHITE)
            n_txt = row_font.render(entry['name'], True, WHITE)
            mode_txt = row_font.render(self.format_mode_label(entry.get('mode', '')), True, GOLD)
            s_txt = row_font.render(str(entry['score']), True, NEON_GREEN)
            
            self.screen.blit(r_txt, (self.width//2 - 360, y))
            self.screen.blit(n_txt, (self.width//2 - 210, y))
            self.screen.blit(mode_txt, (self.width//2 + 20, y))
            self.screen.blit(s_txt, (self.width//2 + 220, y))

        back_button.draw(self.screen)

    def format_mode_label(self, mode):
        labels = {
            "QUICK": "Quick",
            "CHALLENGE": "Challenge",
            "ENDLESS": "Endless",
        }
        return labels.get(mode, mode or "Unknown")

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

    def draw_panel(self, x, y, width, height, title=None, color=NEON_BLUE):
        panel_rect = pygame.Rect(x, y, width, height)
        glass_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        pygame.draw.rect(glass_surf, (15, 25, 35, 200), (0, 0, width, height), border_radius=20)
        pygame.draw.rect(glass_surf, (*color, 100), (0, 0, width, height), width=2, border_radius=20)
        self.screen.blit(glass_surf, (x, y))
        
        if title:
            title_surf = self.assets.fonts['main'].render(title, True, color)
            self.screen.blit(title_surf, (x + 20, y - 15))

    def draw_settings(self, settings_elements, back_button):
        self.draw_background()
        self.draw_text_centered("SYSTEM CONFIGURATION", 'neon', 60, NEON_BLUE)
        
        # Group 1: Audio
        self.draw_panel(self.width//2 - 450, 140, 900, 140, "AUDIO CHANNELS", NEON_GREEN)
        if 'music_volume' in settings_elements: settings_elements['music_volume'].draw(self.screen)
        if 'sfx_volume' in settings_elements: settings_elements['sfx_volume'].draw(self.screen)
        
        # Group 2: Camera & AI
        self.draw_panel(self.width//2 - 450, 310, 900, 160, "VISUAL RECOGNITION", NEON_BLUE)
        if 'tracking_sensitivity' in settings_elements: settings_elements['tracking_sensitivity'].draw(self.screen)
        if 'flip_camera' in settings_elements: settings_elements['flip_camera'].draw(self.screen)
        
        # Group 3: System
        self.draw_panel(self.width//2 - 450, 500, 900, 80, "INTERFACE", NEON_PINK)
        if 'is_fullscreen' in settings_elements: settings_elements['is_fullscreen'].draw(self.screen)
        
        back_button.draw(self.screen)

    def draw_play_selection(self, buttons):
        self.draw_background()
        self._draw_play_title()

        panel = self.assets.images.get('play_select_panel')
        shared_width = min(620, self.width - 320)
        panel_width = shared_width
        panel_height = int(panel_width * 404 / 1024)
        panel_rect = pygame.Rect(0, 0, panel_width, panel_height)
        panel_rect.center = (self.width // 2, 271)

        if panel:
            panel_surf = pygame.transform.smoothscale(panel, panel_rect.size)
            self.screen.blit(panel_surf, panel_rect.topleft)

        back_img = self.assets.images.get('play_back_button')
        back_button = buttons.get("back")
        if back_button and back_img:
            back_width = shared_width
            back_height = int(back_width * 116 / 1024)
            back_rect = pygame.Rect(0, 0, back_width, back_height)
            back_rect.center = back_button.rect.center
            back_surf = pygame.transform.smoothscale(back_img, back_rect.size)
            self.screen.blit(back_surf, back_rect.topleft)

        mode_buttons = (buttons.get("quick"), buttons.get("challenge"), buttons.get("endless"))
        label_font = self.assets.fonts.get('vietnamese_play', self.assets.fonts['main'])
        text_x = panel_rect.left + int(panel_rect.width * 0.215)
        row_centers = (
            panel_rect.top + int(panel_rect.height * 0.180),
            panel_rect.top + int(panel_rect.height * 0.505),
            panel_rect.top + int(panel_rect.height * 0.815),
        )
        for btn, row_y in zip(mode_buttons, row_centers):
            if not btn:
                continue
            btn.rect.center = (panel_rect.centerx, row_y)
            self._draw_embossed_text(btn.text, label_font, (text_x, row_y), midleft=True)

        if back_button:
            back_x = back_button.rect.left + int(back_button.rect.width * 0.20)
            self._draw_embossed_text(back_button.text, label_font, (back_x, back_button.rect.centery), midleft=True)

    def _draw_play_title(self):
        title_font = self.assets.fonts.get('neon', self.assets.fonts['main'])
        text = "SELECT MODE"
        center = (self.width // 2, 64)
        for radius, color in ((5, (73, 39, 16)), (3, (111, 67, 24)), (1, (235, 174, 86))):
            for dx in range(-radius, radius + 1):
                for dy in range(-radius, radius + 1):
                    if dx * dx + dy * dy <= radius * radius:
                        surf = title_font.render(text, True, color)
                        self.screen.blit(surf, surf.get_rect(center=(center[0] + dx, center[1] + dy)))
        shadow = title_font.render(text, True, (35, 20, 10))
        self.screen.blit(shadow, shadow.get_rect(center=(center[0] + 3, center[1] + 4)))
        main = title_font.render(text, True, (255, 222, 142))
        self.screen.blit(main, main.get_rect(center=center))
        shine = title_font.render(text, True, (255, 247, 200))
        shine.set_alpha(120)
        self.screen.blit(shine, shine.get_rect(center=(center[0], center[1] - 2)))

    def _draw_embossed_text(self, text, font, pos, midleft=False):
        anchor = "midleft" if midleft else "center"
        for dx, dy in ((3, 4), (2, 2)):
            shadow = font.render(text, True, (52, 27, 12))
            rect = shadow.get_rect(**{anchor: (pos[0] + dx, pos[1] + dy)})
            self.screen.blit(shadow, rect)
        outline = font.render(text, True, (88, 47, 21))
        for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1)):
            rect = outline.get_rect(**{anchor: (pos[0] + dx, pos[1] + dy)})
            self.screen.blit(outline, rect)
        text_surf = font.render(text, True, (255, 248, 222))
        self.screen.blit(text_surf, text_surf.get_rect(**{anchor: pos}))

    def _draw_hover_wash(self, rect, color, alpha):
        surf = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.rect(surf, (*color, alpha), surf.get_rect(), border_radius=12)
        pygame.draw.rect(surf, (255, 255, 230, min(alpha + 45, 110)), surf.get_rect().inflate(-6, -6), width=2, border_radius=10)
        self.screen.blit(surf, rect.topleft)

    def draw_about(self, back_button):
        self.draw_background()
        self.draw_text_centered("GIỚI THIỆU", 'neon', 80, NEON_PINK)
        
        info = [
            "WING COMMANDER: DUCK OPS",
            "",
            "Một game bắn vịt arcade tốc độ cao, nơi bạn trở thành chỉ huy",
            "phòng không cuối cùng trong chiến dịch chống lại binh đoàn vịt nổi loạn.",
            "Mỗi màn chơi là một trận không chiến hỗn loạn với vịt thường, vịt nhanh,",
            "vịt zigzag, vịt elite và những mục tiêu đặc biệt xuất hiện bất ngờ.",
            "",
            "Điểm đặc biệt của Duck Ops là hệ thống điều khiển bằng thị giác máy tính.",
            "Bạn có thể dùng chuột để ngắm bắn, hoặc bật webcam để điều khiển tâm ngắm",
            "bằng cử chỉ tay: giơ ngón trỏ để nhắm, gập ngón để bắn và tạo dấu chữ V",
            "để phóng tên lửa dọn sạch bầu trời khi trận địa trở nên quá căng.",
            "",
            "Hãy ghi điểm, giữ combo, vượt qua từng cấp độ và leo lên bảng thành tích.",
            "Bầu trời đang bị chiếm đóng. Nhiệm vụ của bạn là giành lại nó, từng phát bắn một.",
            "",
            "POWERED BY PYGAME, OPENCV & MEDIAPIPE"
        ]
        
        y = 170
        info_font = self.assets.fonts.get('vietnamese_play', self.assets.fonts['small'])
        title_font = self.assets.fonts.get('vietnamese_main', self.assets.fonts['main'])
        for line in info:
            if line == "WING COMMANDER: DUCK OPS":
                txt_surf = title_font.render(line, True, GOLD)
                line_gap = 42
            elif line.startswith("POWERED BY"):
                txt_surf = info_font.render(line, True, NEON_GREEN)
                line_gap = 34
            else:
                txt_surf = info_font.render(line, True, WHITE)
                line_gap = 34 if line else 22
            txt_rect = txt_surf.get_rect(center=(self.width // 2, y))
            self.screen.blit(txt_surf, txt_rect)
            y += line_gap
            
        back_button.draw(self.screen)

    def draw_story_screen(self, start_button, start_time=0):
        self.draw_background()
        
        # Story Box
        margin = 100
        box_rect = pygame.Rect(margin, 120, self.width - margin*2, self.height - 300)
        
        # Glass effect for box
        glass_surf = pygame.Surface((box_rect.width, box_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(glass_surf, (0, 20, 40, 180), (0, 0, box_rect.width, box_rect.height), border_radius=20)
        pygame.draw.rect(glass_surf, NEON_BLUE, (0, 0, box_rect.width, box_rect.height), width=3, border_radius=20)
        self.screen.blit(glass_surf, box_rect.topleft)
        
        # Create a surface for clipping the scrolling text
        clip_surf = pygame.Surface((box_rect.width - 40, box_rect.height - 100), pygame.SRCALPHA)
        
        # Title
        self.draw_text_centered("MISSION BRIEFING: YEAR 2029", 'neon', 170, GOLD)
        
        # Narrative Text
        story_lines = [
            "Năm 2029, bầu trời không còn thuộc về con người.",
            "Từ những tầng mây nhiễu sóng, Liên minh Vịt Trời trỗi dậy như",
            "một đội không kích lông vũ: nhanh, ồn ào và cực kỳ khó chịu.",
            "Chúng không chiếm thành phố bằng xe tăng hay tên lửa, mà bằng",
            "tiếng quạc siêu âm, đội hình zigzag và những cú bổ nhào không báo trước.",
            "",
            "Các trạm radar lần lượt im bặt. Kho đạn bị phong tỏa. Bộ chỉ huy",
            "chỉ còn nhận được một dòng tín hiệu cuối cùng: DUCKS INCOMING.",
            "Khi cả lực lượng phòng không rơi vào hỗn loạn, một đơn vị đặc nhiệm",
            "được kích hoạt lại từ kho lưu trữ tuyệt mật: Wing Commander: Duck Ops.",
            "",
            "Bạn là chỉ huy cuối cùng còn đứng vững trước làn sóng vịt nổi loạn.",
            "Trong tay bạn là khẩu laser thử nghiệm, hệ thống khóa mục tiêu bằng",
            "webcam và một nhiệm vụ nghe có vẻ đơn giản: bắn hạ mọi mục tiêu bay",
            "trước khi chúng phá nát vùng trời chiến thuật.",
            "",
            "Nhưng đừng xem thường chúng. Vịt thường bay theo đàn để gây rối.",
            "Vịt nhanh lao qua màn hình như một vệt vàng. Vịt zigzag đánh lừa",
            "tâm ngắm bằng quỹ đạo bất ổn. Vịt elite lì đòn hơn, tinh ranh hơn,",
            "và luôn xuất hiện đúng lúc bạn tưởng mình đã kiểm soát được trận địa.",
            "",
            "LỢI THẾ CHIẾN THUẬT: bạn có thể điều khiển tâm ngắm bằng cử chỉ tay.",
            "Giơ ngón trỏ để khóa mục tiêu. Gập ngón để khai hỏa. Tạo dấu chữ V",
            "để phóng tên lửa khi bầu trời trở nên quá đông và quá hỗn loạn.",
            "",
            "Hãy giữ bình tĩnh, căn chuẩn từng phát bắn, nối combo và sống sót",
            "qua từng đợt tấn công. Bầu trời đang chờ mệnh lệnh của bạn.",
            "",
            "SẴN SÀNG VÀO VỊ TRÍ, CHỈ HUY. CHIẾN DỊCH DUCK OPS BẮT ĐẦU!"
        ]

        # Calculate scroll offset
        elapsed = pygame.time.get_ticks() - start_time
        scroll_speed = 0.045 # pixels per ms
        scroll_y = box_rect.height - 100 - (elapsed * scroll_speed)
        
        # Stop scrolling when the last line is visible
        min_scroll = 50 
        scroll_y = max(min_scroll, scroll_y)
        
        curr_y = scroll_y
        story_font = self.assets.fonts.get('vietnamese_play', self.assets.fonts['small'])
        for line in story_lines:
            color = WHITE if "LỢI THẾ" not in line and "SẴN SÀNG" not in line else NEON_GREEN
            txt_surf = story_font.render(line, True, color)
            txt_rect = txt_surf.get_rect(center=((box_rect.width - 40) // 2, curr_y))
            clip_surf.blit(txt_surf, txt_rect)
            curr_y += 35
            
        self.screen.blit(clip_surf, (box_rect.left + 20, box_rect.top + 80))
        
        # Only show button after some time or if scroll is finished
        if elapsed > 3000 or scroll_y == min_scroll:
            start_button.draw(self.screen)

    def draw_camera_noise(self, intensity):
        """Draws a static/noise overlay to simulate camera interference."""
        if intensity <= 0: return
        
        noise_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        alpha = min(200, int(intensity * 100))
        
        # Draw random small white/gray dots or lines
        for _ in range(int(intensity * 50)):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            size = random.randint(1, 4)
            color = random.choice([(255, 255, 255, alpha), (200, 200, 200, alpha), (100, 100, 100, alpha)])
            pygame.draw.circle(noise_surf, color, (x, y), size)
            
        # Draw some scanline noise
        for _ in range(int(intensity * 5)):
            y = random.randint(0, self.height)
            pygame.draw.line(noise_surf, (255, 255, 255, alpha // 2), (0, y), (self.width, y), 1)
            
        self.screen.blit(noise_surf, (0, 0))
