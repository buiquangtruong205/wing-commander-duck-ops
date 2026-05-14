import pygame
import os

class AssetsManager:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.images = {}
        self.sounds = {}
        self.fonts = {}
        
    def load_all(self):
        # Images
        self.images['menu_bg'] = self.load_img("frontend/images/backgroudHome.png", (self.width, self.height))
        self.images['bg'] = self.images['menu_bg']
        self.images['menu_button'] = self.load_img("frontend/images/menu_button.png", None, alpha=True)
        self.images['tutorial_button'] = self.load_img("frontend/images/tutorial_button.png", None, alpha=True)
        self.images['history_button'] = self.load_img("frontend/images/lichsu.png", None, alpha=True)
        self.images['about_button'] = self.load_img("frontend/images/gioithieu.png", None, alpha=True)
        self.images['settings_button'] = self.load_img("frontend/images/caidat.png", None, alpha=True)
        self.images['play_select_panel'] = self.load_img("frontend/images/select.png", None, alpha=True)
        self.images['play_back_button'] = self.load_img("frontend/images/out.png", None, alpha=True)
        self.images['duck_sheet'] = self.load_img("frontend/images/duck_sprite.png", None, alpha=True)
        self.images['duck_flying'] = self.load_img("frontend/images/duck_flying.png", None, alpha=True)
        self.images['yellow_duck_sheet'] = self.load_img("frontend/images/yellow_duck_spritesheet.png", None, alpha=True)
        self.images['hit_explosion'] = self.load_img("frontend/images/danchung_explosion.png", (150, 150), alpha=True)
        
        # Level Backgrounds
        self.images['level_bg1'] = self.load_img("frontend/images/anh1.png", (self.width, self.height))
        self.images['level_bg2'] = self.load_img("frontend/images/anh2.png", (self.width, self.height))
        self.images['level_bg3'] = self.load_img("frontend/images/anh3.png", (self.width, self.height))
        
        # Sounds
        self.sounds['shot'] = self.load_snd("frontend/sounds/laser_shot.wav")
        self.sounds['hit'] = self.load_snd("frontend/sounds/duck_hit.wav")
        self.sounds['explosion'] = self.load_snd("frontend/sounds/explosion.wav")
        self.sounds['flying'] = self.load_snd("frontend/sounds/duck_flying_loop.wav")
        self.sounds['lobby'] = self.load_snd("frontend/sounds/lobby_theme.wav")
        self.sounds['click'] = self.load_snd("frontend/sounds/gunshot.wav")
        
        # Fonts
        # Try to find a cyberpunk-ish font or fallback to Arial
        font_names = ["Agency FB", "Bahnschrift", "Consolas", "Arial"]
        main_font_name = "Arial"
        for fn in font_names:
            if fn.lower() in [f.lower() for f in pygame.font.get_fonts()]:
                main_font_name = fn
                break
                
        self.fonts['main'] = pygame.font.SysFont(main_font_name, 32, bold=True)
        self.fonts['title'] = pygame.font.SysFont(main_font_name, 84, bold=True)
        self.fonts['small'] = pygame.font.SysFont(main_font_name, 24)
        self.fonts['neon'] = pygame.font.SysFont(main_font_name, 48, bold=True)
        vietnamese_font_path = r"C:\Windows\Fonts\arialbd.ttf"
        if os.path.exists(vietnamese_font_path):
            self.fonts['vietnamese_main'] = pygame.font.Font(vietnamese_font_path, 32)
            self.fonts['vietnamese_play'] = pygame.font.Font(vietnamese_font_path, 22)
        else:
            self.fonts['vietnamese_main'] = pygame.font.SysFont("Tahoma", 32, bold=True)
            self.fonts['vietnamese_play'] = pygame.font.SysFont("Tahoma", 22, bold=True)

    def load_img(self, path, size=None, alpha=False):
        try:
            img = pygame.image.load(path)
            if alpha:
                img = img.convert_alpha()
            else:
                img = img.convert()
            if size:
                img = pygame.transform.scale(img, size)
            return img
        except Exception as e:
            print(f"Error loading image {path}: {e}")
            fallback = pygame.Surface(size if size else (100, 100))
            fallback.fill((50, 50, 50))
            return fallback

    def load_snd(self, path):
        try:
            return pygame.mixer.Sound(path)
        except Exception as e:
            print(f"Error loading sound {path}: {e}")
            return None

    def apply_volumes(self, music_vol, sfx_vol):
        """Sets volumes for all loaded sounds."""
        # We'll treat lobby/flying as music-like and others as SFX.
        for key, snd in self.sounds.items():
            if snd:
                if key in ['flying', 'lobby']:
                    snd.set_volume(music_vol)
                else:
                    snd.set_volume(sfx_vol)
