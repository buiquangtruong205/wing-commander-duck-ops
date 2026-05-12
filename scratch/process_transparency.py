import pygame
pygame.init()
pygame.display.set_mode((1,1))
try:
    img = pygame.image.load("C:/Users/Admin/.gemini/antigravity/brain/a50304d5-0518-4127-977c-fbb42b214d79/yellow_duck_v2_1778602808109.png")
    # Some generators might make it slightly off-green. 
    # We'll set colorkey to the top-left pixel color.
    colorkey = img.get_at((0,0))
    img.set_colorkey(colorkey)
    # Convert to alpha to keep transparency when saving
    final = img.convert_alpha()
    pygame.image.save(final, "e:/Computer_Vision/wing-commander-duck-ops/frontend/images/yellow_duck_spritesheet.png")
    print("Processed and saved yellow_duck_spritesheet.png")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
