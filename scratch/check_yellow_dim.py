import pygame
pygame.init()
try:
    img = pygame.image.load("e:/Computer_Vision/wing-commander-duck-ops/frontend/images/yellow_duck_spritesheet.png")
    print(f"Dimensions: {img.get_size()}")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
