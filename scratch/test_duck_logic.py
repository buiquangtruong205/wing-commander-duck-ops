import pygame
import os
import sys

# Add path to import backend
sys.path.append(os.path.abspath("e:/Computer_Vision/wing-commander-duck-ops"))

from backend.game_logic import Duck

pygame.init()
screen = pygame.display.set_mode((1280, 720))

# Mock assets
try:
    duck_sheet = pygame.Surface((1624, 378))
    duck_flying = pygame.Surface((1024, 1024))
    
    print("Testing normal duck...")
    d1 = Duck(1280, 720, duck_sheet, "normal")
    print(f"Normal duck frames: {len(d1.frames)}, health: {d1.health}")
    
    print("Testing elite duck...")
    d2 = Duck(1280, 720, duck_flying, "elite")
    print(f"Elite duck frames: {len(d2.frames)}, health: {d2.health}")
    
    assert len(d1.frames) == 4
    assert len(d2.frames) == 1
    assert d1.health == 1
    assert d2.health == 3
    
    print("Test passed!")
except Exception as e:
    print(f"Test failed: {e}")
    import traceback
    traceback.print_exc()

pygame.quit()
