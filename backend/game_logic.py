import pygame
import random
import math
import time

class Duck(pygame.sprite.Sprite):
    def __init__(self, screen_width, screen_height, sprite_sheet, duck_type="normal", speed_multiplier=1.0):
        super().__init__()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.duck_type = duck_type
        self.speed_multiplier = speed_multiplier
        
        # Load and scale sprite
        self.frames = self.load_frames(sprite_sheet)
        self.current_frame = 0
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect()
        
        # Random starting position from any side
        self.side = random.choice(["left", "right", "bottom"])
        if self.side == "left":
            self.rect.x = -100
            self.rect.y = random.randint(50, screen_height - 300)
            self.speed_x = random.uniform(3, 7) * speed_multiplier
            self.speed_y = random.uniform(-2, 2) * speed_multiplier
        elif self.side == "right":
            self.rect.x = screen_width + 100
            self.rect.y = random.randint(50, screen_height - 300)
            self.speed_x = random.uniform(-7, -3) * speed_multiplier
            self.speed_y = random.uniform(-2, 2) * speed_multiplier
        else: # bottom
            self.rect.x = random.randint(200, screen_width - 200)
            self.rect.y = screen_height + 100
            self.speed_x = random.uniform(-3, 3) * speed_multiplier
            self.speed_y = random.uniform(-7, -4) * speed_multiplier
        
        # Adjust behavior based on type
        if duck_type == "fast":
            self.speed_x *= 1.5
            self.speed_y *= 1.5
            self.health = 1
            self.color_mod = (255, 100, 100) # Reddish
        elif duck_type == "zigzag":
            self.speed_x *= 1.2
            self.health = 1
            self.color_mod = (100, 100, 255)
        elif duck_type == "elite":
            self.health = 3
            self.color_mod = None
            # Scale up the elite duck
            self.frames = [pygame.transform.scale(f, (120, 120)) for f in self.frames]
            self.image = self.frames[0]
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.health = 1
            self.color_mod = None
            
        self.animation_speed = 0.1
        self.last_update = time.time()
        self.is_hit = False
        self.has_entered_screen = False

    def load_frames(self, sheet):
        frames = []
        w, h = sheet.get_size()
        
        # If the sheet is wide, assume it's a 4-frame animation
        if w > h * 1.2:
            frame_w = w // 4
            for i in range(4):
                # We already cleaned the borders from the image asset
                rect = (i * frame_w, 0, frame_w, h)
                try:
                    frame = sheet.subsurface(rect)
                    frame = pygame.transform.scale(frame, (100, 100))
                    frames.append(frame)
                except ValueError:
                    # Fallback
                    frame = sheet.subsurface((i * frame_w, 0, frame_w, h))
                    frame = pygame.transform.scale(frame, (100, 100))
                    frames.append(frame)

        elif abs(w - h) < 50: # Square-ish
            # Check if it might be a 4-frame row with lots of vertical padding
            # Or a 2x2 grid. For the yellow duck specifically, we now crop it,
            # but if it's still square-ish, we prefer splitting horizontally if w is large.
            fw, fh = w // 2, h // 2
            for y in range(2):
                for x in range(2):
                    frame = sheet.subsurface((x * fw, y * fh, fw, fh))
                    frame = pygame.transform.scale(frame, (100, 100))
                    frames.append(frame)
        else:
            # Single frame image
            frame = pygame.transform.scale(sheet, (100, 100))
            frames.append(frame)
        return frames


    def update(self):
        if not self.is_hit:
            self.rect.x += self.speed_x
            self.rect.y += self.speed_y
            
            # Sinusoidal movement for some types
            if self.duck_type == "zigzag":
                self.rect.y += math.sin(time.time() * 5) * 5

            # Change direction if hitting top/bottom after entering the play area.
            hit_top = self.rect.top < 50 and self.speed_y < 0
            hit_bottom = self.rect.bottom > self.screen_height - 150 and self.speed_y > 0 and self.rect.top < self.screen_height - 150
            if hit_top or hit_bottom:
                self.speed_y *= -1
            
            # Animation
            now = time.time()
            if now - self.last_update > self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                
                # Flip image if flying left
                if self.speed_x < 0:
                    self.image = pygame.transform.flip(self.image, True, False)
                self.last_update = now
        else:
            # Falling animation if hit
            self.rect.y += 10
            self.image = pygame.transform.rotate(self.frames[0], 180)

        # Remove if off screen
        if (self.rect.x < -200 or self.rect.x > self.screen_width + 200 or 
            self.rect.y > self.screen_height + 100):
            self.kill()

class Boss(Duck):
    def __init__(self, screen_width, screen_height, sprite_sheet, speed_multiplier=1.0):
        super().__init__(screen_width, screen_height, sprite_sheet, "elite", speed_multiplier)
        self.health = 25
        self.max_health = 25
        
        # Scale to giant size
        self.frames = [pygame.transform.scale(f, (250, 250)) for f in self.frames]
        self.image = self.frames[0]
        self.rect = self.image.get_rect(center=(screen_width // 2, -150))
        
        self.speed_x = random.uniform(1, 2) * speed_multiplier
        self.speed_y = 1.0 # Descend initially
        self.is_boss = True
        self.last_minion_spawn_time = time.time()

    def update(self):
        if not self.is_hit:
            # Boss specific movement: descend to 100-200 range then move horizontally
            if self.rect.y < 100:
                self.rect.y += self.speed_y
            else:
                self.rect.x += self.speed_x
                # Hovering effect
                self.rect.y += math.sin(time.time() * 2) * 2
                
                # Bounce off walls
                if self.rect.right > self.screen_width - 50 or self.rect.left < 50:
                    self.speed_x *= -1
            
            # Animation
            now = time.time()
            if now - self.last_update > self.animation_speed:
                self.current_frame = (self.current_frame + 1) % len(self.frames)
                self.image = self.frames[self.current_frame]
                if self.speed_x < 0:
                    self.image = pygame.transform.flip(self.image, True, False)
                self.last_update = now
        else:
            # Falling
            self.rect.y += 5
            self.image = pygame.transform.rotate(self.frames[0], 180)
            if self.rect.y > self.screen_height + 100:
                self.kill()

class Feather(pygame.sprite.Sprite):
    def __init__(self, pos, screen_width, screen_height):
        super().__init__()
        self.screen_height = screen_height
        # Create a simple feather shape or use a surface
        self.image = pygame.Surface((20, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 255, 255, 200), (0, 0, 20, 40))
        pygame.draw.line(self.image, (200, 200, 200), (10, 0), (10, 40), 2)
        
        self.rect = self.image.get_rect(center=pos)
        self.speed_y = random.uniform(4, 7)
        self.speed_x = random.uniform(-2, 2)
        self.rotation = 0

    def update(self):
        self.rect.y += self.speed_y
        self.rect.x += self.speed_x
        self.rotation = (self.rotation + 5) % 360
        # For simplicity, we won't rotate the actual image here to keep it light
        
        if self.rect.top > self.screen_height:
            self.kill()
            return True # Signal hit bottom
        return False

class Crosshair(pygame.sprite.Sprite):
    def __init__(self, color=(0, 255, 255)):
        super().__init__()
        self.color = color
        self.image = self.create_image(color)
        self.rect = self.image.get_rect()

    def create_image(self, color):
        surface = pygame.Surface((60, 60), pygame.SRCALPHA)
        # Outer circle
        pygame.draw.circle(surface, color, (30, 30), 25, 2)
        # Cross lines
        pygame.draw.line(surface, color, (30, 5), (30, 20), 2)
        pygame.draw.line(surface, color, (30, 40), (30, 55), 2)
        pygame.draw.line(surface, color, (5, 30), (20, 30), 2)
        pygame.draw.line(surface, color, (40, 30), (55, 30), 2)
        # Center dot
        pygame.draw.circle(surface, color, (30, 30), 3)
        return surface

    def update(self, pos=None):
        if pos:
            self.rect.center = pos

class Particle(pygame.sprite.Sprite):
    def __init__(self, pos, color):
        super().__init__()
        size = random.randint(2, 6)
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=pos)
        self.vel = [random.uniform(-7, 7), random.uniform(-7, 7)]
        self.lifetime = random.randint(15, 30)

    def update(self):
        self.rect.x += self.vel[0]
        self.rect.y += self.vel[1]
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()

class Explosion(pygame.sprite.Sprite):
    def __init__(self, pos, image, lifetime=18):
        super().__init__()
        self.base_image = image
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.image = self.base_image.copy()
        self.rect = self.image.get_rect(center=pos)

    def update(self):
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()
            return

        progress = 1 - (self.lifetime / self.max_lifetime)
        scale = 0.75 + progress * 0.45
        alpha = max(0, int(255 * (self.lifetime / self.max_lifetime)))
        width = max(1, int(self.base_image.get_width() * scale))
        height = max(1, int(self.base_image.get_height() * scale))
        center = self.rect.center

        self.image = pygame.transform.smoothscale(self.base_image, (width, height))
        self.image.set_alpha(alpha)
        self.rect = self.image.get_rect(center=center)
