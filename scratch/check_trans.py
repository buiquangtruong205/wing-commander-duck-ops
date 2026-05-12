import pygame
pygame.init()
pygame.display.set_mode((1,1))
try:
    img = pygame.image.load("e:/Computer_Vision/wing-commander-duck-ops/frontend/images/yellow_duck_spritesheet.png")
    print(f"Top-left pixel: {img.get_at((0,0))}")
    print(f"Alpha at (0,0): {img.get_at((0,0))[3]}")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
