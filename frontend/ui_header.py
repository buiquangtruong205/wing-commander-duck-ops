import pygame
import random

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
    def __init__(self, x, y, width, height, text, font, icon=None, icon_right=None, color=WHITE, hover_color=GOLD, assets=None, style='default'):
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
        w, h = self.rect.width, self.rect.height
        shadow_surf = pygame.Surface((w + 6, h + 6), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surf, (0, 0, 0, 60), (0, 0, w + 6, h + 6), border_radius=14)
        screen.blit(shadow_surf, (self.rect.x - 3, self.rect.y + 3))
        btn_surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for row in range(h):
            t = row / h
            cf = max(0, min(1, 1 - abs(t - 0.35) * 2.0))
            r = min(255, int(105 + 60 * cf) + (25 if self.is_hovered else 0))
            g = min(255, int(68 + 42 * cf) + (18 if self.is_hovered else 0))
            b = min(255, int(28 + 22 * cf) + (10 if self.is_hovered else 0))
            pygame.draw.line(btn_surf, (r, g, b), (0, row), (w, row))
        mask = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(mask, (255, 255, 255, 255), (0, 0, w, h), border_radius=12)
        btn_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        screen.blit(btn_surf, self.rect.topleft)
        hl = pygame.Surface((w - 16, 2), pygame.SRCALPHA)
        hl.fill((255, 230, 170, 50))
        screen.blit(hl, (self.rect.x + 8, self.rect.y + 4))
        bc = (225, 195, 100) if self.is_hovered else (195, 165, 85)
        pygame.draw.rect(screen, bc, self.rect, width=3, border_radius=12)
        ir = self.rect.inflate(-8, -8)
        isf = pygame.Surface((ir.width, ir.height), pygame.SRCALPHA)
        pygame.draw.rect(isf, (210, 180, 110, 45), (0, 0, ir.width, ir.height), width=1, border_radius=9)
        screen.blit(isf, ir.topleft)
        if self.icon and isinstance(self.icon, (str, bytes)):
            ifont = pygame.font.SysFont("Segoe UI Emoji", int(h * 0.42))
            isurf = ifont.render(self.icon, True, (255, 225, 160))
            screen.blit(isurf, isurf.get_rect(midleft=(self.rect.left + 18, self.rect.centery)))
        tc = (255, 255, 240) if self.is_hovered else (255, 245, 215)
        sh = self.font.render(self.text, True, (50, 30, 10))
        screen.blit(sh, sh.get_rect(center=(self.rect.centerx, self.rect.centery + 2)))
        ts = self.font.render(self.text, True, tc)
        screen.blit(ts, ts.get_rect(center=self.rect.center))
        if self.icon_right and isinstance(self.icon_right, (str, bytes)):
            ifont = pygame.font.SysFont("Segoe UI Emoji", int(h * 0.42))
            isurf = ifont.render(self.icon_right, True, (255, 225, 160))
            screen.blit(isurf, isurf.get_rect(midright=(self.rect.right - 18, self.rect.centery)))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.is_hovered:
                if self.assets and self.assets.sounds.get('click'):
                    self.assets.sounds['click'].play()
                return True
        return False
