import pygame
pygame.init()
pygame.display.set_mode((1, 1))
try:
    img = pygame.image.load("e:/Computer_Vision/wing-commander-duck-ops/frontend/images/duck_flying.png").convert_alpha()
    w, h = img.get_size()
    
    # Simple blob detection: find connected components of non-transparent pixels
    # Or just check quadrants again but with more care
    
    # Let's just save the whole thing and look at it? No.
    # Let's find the bounding box of all non-transparent pixels
    
    def get_bbox(surface):
        min_x, min_y = surface.get_width(), surface.get_height()
        max_x, max_y = 0, 0
        found = False
        for x in range(surface.get_width()):
            for y in range(surface.get_height()):
                if surface.get_at((x,y))[3] > 0:
                    min_x = min(min_x, x)
                    max_x = max(max_x, x)
                    min_y = min(min_y, y)
                    max_y = max(max_y, y)
                    found = True
        if not found: return None
        return (min_x, min_y, max_x - min_x + 1, max_y - min_y + 1)

    print(f"Total bbox: {get_bbox(img)}")
    
    # Check quadrants bboxes
    fw, fh = w // 2, h // 2
    for y in range(2):
        for x in range(2):
            sub = img.subsurface((x*fw, y*fh, fw, fh))
            print(f"Quadrant {x},{y} bbox: {get_bbox(sub)}")
            
except Exception as e:
    print(f"Error: {e}")
pygame.quit()
