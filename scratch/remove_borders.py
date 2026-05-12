import pygame
import os

pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

try:
    path = r"e:\Computer_Vision\wing-commander-duck-ops\frontend\images\yellow_duck_spritesheet.png"
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    
    # We know there are 4 frames
    frame_w = w // 4
    new_img = pygame.Surface((w, h), pygame.SRCALPHA)
    
    for i in range(4):
        # Extract frame
        frame = img.subsurface((i * frame_w, 0, frame_w, h))
        fw, fh = frame.get_size()
        
        # Find the duck's bounding box in this frame
        # We assume the duck is the main thing that isn't white or a thin border line
        min_x, min_y = fw, fh
        max_x, max_y = 0, 0
        found = False
        
        for y in range(fh):
            for x in range(fw):
                p = frame.get_at((x, y))
                # If not transparent
                if p[3] > 0:
                    # Ignore pixels that are exactly on the edges (borders)
                    if x < 5 or x > fw - 5 or y < 5 or y > fh - 5:
                        continue
                        
                    min_x = min(min_x, x)
                    min_y = min(min_y, y)
                    max_x = max(max_x, x)
                    max_y = max(max_y, y)
                    found = True
        
        if found:
            # Crop the duck from the frame and blit it back centered or just clean the frame
            # Actually, let's just copy everything inside the found bounding box
            # and set everything else in this frame to transparent.
            for y in range(fh):
                for x in range(fw):
                    p = frame.get_at((x, y))
                    if x >= min_x and x <= max_x and y >= min_y and y <= max_y:
                        new_img.set_at((i * frame_w + x, y), p)
                    else:
                        new_img.set_at((i * frame_w + x, y), (0, 0, 0, 0))
        else:
            # If not found, just keep it transparent
            pass

    pygame.image.save(new_img, path)
    print(f"Cleaned borders from {path}")
    
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
pygame.quit()
