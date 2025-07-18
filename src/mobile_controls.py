import pygame

class TouchControls:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.button_size = 60
        self.setup_buttons()
        
    def setup_buttons(self):
        # Control buttons for mobile
        margin = 20
        bottom = self.screen_height - margin - self.button_size
        
        self.buttons = {
            'left': pygame.Rect(margin, bottom, self.button_size, self.button_size),
            'right': pygame.Rect(margin + self.button_size + 10, bottom, self.button_size, self.button_size),
            'rotate': pygame.Rect(self.screen_width - margin - self.button_size, bottom, self.button_size, self.button_size),
            'down': pygame.Rect(self.screen_width - margin - self.button_size * 2 - 10, bottom, self.button_size, self.button_size)
        }
    
    def handle_touch(self, pos):
        for action, rect in self.buttons.items():
            if rect.collidepoint(pos):
                return action
        return None
    
    def draw(self, screen):
        colors = {
            'left': (100, 100, 255),
            'right': (100, 100, 255),
            'rotate': (255, 100, 100),
            'down': (100, 255, 100)
        }
        
        for action, rect in self.buttons.items():
            pygame.draw.rect(screen, colors[action], rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)