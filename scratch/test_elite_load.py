import pygame
import os
import sys

# Add path to import backend
sys.path.append(os.path.abspath("e:/Computer_Vision/wing-commander-duck-ops"))

from backend.game_logic import Duck

pygame.init()
pygame.display.set_mode((1, 1))

try:
    print("Testing elite duck loading...")
    sheet = pygame.image.load("e:/Computer_Vision/wing-commander-duck-ops/frontend/images/yellow_duck_spritesheet.png")
    duck = Duck(1280, 720, sheet, "elite")
    print(f"Duck type: {duck.duck_type}, frames: {len(duck.frames)}")
except Exception as e:
    print(f"Error: {e}")

pygame.quit()
