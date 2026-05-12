import pygame
pygame.init()
pygame.display.set_mode((1,1))
try:
    img = pygame.image.load("C:/Users/Admin/.gemini/antigravity/brain/a50304d5-0518-4127-977c-fbb42b214d79/yellow_duck_horiz_1778603000108.png")
    # Set top-left pixel (white) as colorkey
    colorkey = img.get_at((0,0))
    img.set_colorkey(colorkey)
    final = img.convert_alpha()
    pygame.image.save(final, "e:/Computer_Vision/wing-commander-duck-ops/frontend/images/yellow_duck_spritesheet.png")
    print("Saved horizontal yellow_duck_spritesheet.png")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
