import pygame
pygame.init()
try:
    img = pygame.image.load("e:/Computer_Vision/wing-commander-duck-ops/frontend/images/duck_flying.png")
    w, h = img.get_size()
    quads = [
        (0, 0, w//2, h//2),
        (w//2, 0, w//2, h//2),
        (0, h//2, w//2, h//2),
        (w//2, h//2, w//2, h//2)
    ]
    for i, q in enumerate(quads):
        sub = img.subsurface(q)
        # Check if there are any non-transparent pixels
        has_content = False
        for x in range(w//2):
            for y in range(h//2):
                if sub.get_at((x,y))[3] > 0:
                    has_content = True
                    break
            if has_content: break
        print(f"Quadrant {i} has content: {has_content}")
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
