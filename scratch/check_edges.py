import pygame
pygame.init()
pygame.display.set_mode((1, 1))
for y in range(2):
    for x in range(2):
        img = pygame.image.load(f"e:/Computer_Vision/wing-commander-duck-ops/scratch/frame_{x}_{y}.png")
        w, h = img.get_size()
        # Check edges for non-transparent pixels
        edge_content = False
        # Top/Bottom edges
        for tx in range(w):
            if img.get_at((tx, 0))[3] > 0 or img.get_at((tx, h-1))[3] > 0:
                edge_content = True
                break
        # Left/Right edges
        if not edge_content:
            for ty in range(h):
                if img.get_at((0, ty))[3] > 0 or img.get_at((w-1, ty))[3] > 0:
                    edge_content = True
                    break
        print(f"Frame {x},{y} hits edges: {edge_content}")
pygame.quit()
