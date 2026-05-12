import pygame
import os

pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)
try:
    path = r"e:\Computer_Vision\wing-commander-duck-ops\frontend\images\yellow_duck_spritesheet.png"
    img = pygame.image.load(path).convert_alpha()
    w, h = img.get_size()
    
    # Create a new surface with alpha
    new_img = pygame.Surface((w, h), pygame.SRCALPHA)
    
    # Background removal: anything bright becomes transparent
    # Also remove the black borders if possible? 
    # Let's stick to background first.
    for y in range(h):
        for x in range(w):
            p = img.get_at((x, y))
            # If it's a white-ish background pixel (threshold 230 to be safe)
            if p[0] > 230 and p[1] > 230 and p[2] > 230:
                new_img.set_at((x, y), (0, 0, 0, 0))
            else:
                new_img.set_at((x, y), p)
                
    # Find bounding box of non-transparent pixels
    min_x, min_y = w, h
    max_x, max_y = 0, 0
    found = False
    
    for y in range(h):
        for x in range(w):
            p = new_img.get_at((x, y))
            if p[3] > 0: # If not transparent
                min_x = min(min_x, x)
                min_y = min(min_y, y)
                max_x = max(max_x, x)
                max_y = max(max_y, y)
                found = True
                
    if found:
        # Crop to the ducks
        cropped_w = max_x - min_x + 1
        cropped_h = max_y - min_y + 1
        cropped = new_img.subsurface((min_x, min_y, cropped_w, cropped_h))
        
        # Save over the original! (Or to a new file first for safety)
        save_path = r"e:\Computer_Vision\wing-commander-duck-ops\frontend\images\yellow_duck_spritesheet.png"
        # Backup first
        backup_path = r"e:\Computer_Vision\wing-commander-duck-ops\frontend\images\yellow_duck_spritesheet_backup.png"
        if not os.path.exists(backup_path):
            os.rename(path, backup_path)
            
        pygame.image.save(cropped, save_path)
        print(f"Saved cleaned image to {save_path}")
        print(f"New Size: {cropped.get_size()}")
    else:
        print("No content found after background removal")
        
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
pygame.quit()
