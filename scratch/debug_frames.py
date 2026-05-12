import pygame
pygame.init()
pygame.display.set_mode((1, 1)) # Dummy mode
try:
    img = pygame.image.load("e:/Computer_Vision/wing-commander-duck-ops/frontend/images/duck_flying.png").convert_alpha()
    w, h = img.get_size()
    fw, fh = w // 2, h // 2
    for y in range(2):
        for x in range(2):
            rect = (x * fw, y * fh, fw, fh)
            sub = img.subsurface(rect)
            pygame.image.save(sub, f"e:/Computer_Vision/wing-commander-duck-ops/scratch/frame_{x}_{y}.png")
            print(f"Saved frame_{x}_{y}.png, size: {sub.get_size()}")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
