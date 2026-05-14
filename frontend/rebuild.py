import sys
header = open('frontend/ui_header.py', 'r', encoding='utf-8').read()
old = open('frontend/ui_system.py', 'r', encoding='utf-8').read()

rest = "class UIInputField:\n"
rest += "    def __init__(self, x, y, width, height, font, label=''):\n"
rest += "        self.rect = pygame.Rect(x, y, width, height)\n"
rest += "        self.font = font\n"
rest += "        self.label = label\n"
rest += old  # old starts with self.text = ""

combined = header + "\n\n" + rest
with open('frontend/ui_system.py', 'w', encoding='utf-8') as f:
    f.write(combined)
print("Done, lines:", combined.count('\n'))
