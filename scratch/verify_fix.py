import pygame
import os
import sys

# Mocking pygame display for headless environment
pygame.init()
pygame.display.set_mode((1, 1), pygame.HIDDEN)

# Add backend to path
sys.path.append(os.path.abspath("."))
from backend.game_logic import Duck

try:
    path = r"e:\Computer_Vision\wing-commander-duck-ops\frontend\images\yellow_duck_spritesheet.png"
    img = pygame.image.load(path).convert_alpha()
    print(f"Image Size: {img.get_size()}")
    
    # Create a dummy duck to test frame loading
    duck = Duck(1280, 720, img, "elite")
    print(f"Number of frames: {len(duck.frames)}")
    for i, frame in enumerate(duck.frames):
        size = frame.get_size()
        # Check transparency of a corner pixel
        p = frame.get_at((0, 0))
        print(f"Frame {i} size: {size}, Top-left pixel: {p}")
        
    if len(duck.frames) == 4:
        print("SUCCESS: 4 frames correctly loaded.")
    else:
        print(f"FAILURE: Expected 4 frames, got {len(duck.frames)}")
        
except Exception as e:
    import traceback
    traceback.print_exc()
    print(f"Error: {e}")
pygame.quit()
