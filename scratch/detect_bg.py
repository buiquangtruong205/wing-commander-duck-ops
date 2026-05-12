import pygame
pygame.init()
pygame.display.set_mode((1,1))
try:
    img = pygame.image.load("e:/Computer_Vision/wing-commander-duck-ops/frontend/images/yellow_duck_spritesheet.png").convert_alpha()
    # Check top-left pixel
    print(f"Top-left: {img.get_at((0,0))}")
    # Check a few pixels away
    print(f"Pixel at (10,10): {img.get_at((10,10))}")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
