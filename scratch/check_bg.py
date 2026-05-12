import pygame
pygame.init()
try:
    img = pygame.image.load("e:/Computer_Vision/wing-commander-duck-ops/frontend/images/duck_flying.png")
    print(f"Has Alpha: {img.get_masks()[3] != 0}")
    # Check some corner pixels for background
    corners = [(0,0), (1023,0), (0,1023), (1023,1023)]
    for c in corners:
        print(f"Pixel at {c}: {img.get_at(c)}")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
