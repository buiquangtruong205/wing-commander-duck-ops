import pygame
import os

pygame.init()
try:
    path = r"e:\Computer_Vision\wing-commander-duck-ops\frontend\images\yellow_duck_spritesheet.png"
    img = pygame.image.load(path)
    print(f"Path: {path}")
    print(f"Size: {img.get_size()}")
    
    # Find bounding box of non-white pixels
    # White is approx (254, 254, 254)
    min_x, min_y = img.get_width(), img.get_height()
    max_x, max_y = 0, 0
    
    found = False
    # Sample to speed up
    for y in range(0, img.get_height(), 2):
        for x in range(0, img.get_width(), 2):
            p = img.get_at((x, y))
            # If not white-ish (assuming background is > 250)
            if p[0] < 250 or p[1] < 250 or p[2] < 250:
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                found = True
                
    if found:
        print(f"Bounding Box: ({min_x}, {min_y}, {max_x}, {max_y})")
        print(f"Width: {max_x - min_x + 1}, Height: {max_y - min_y + 1}")
    else:
        print("No non-white pixels found")
        
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
