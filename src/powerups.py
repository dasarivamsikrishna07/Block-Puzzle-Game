import random
import pygame

class PowerUp:
    def __init__(self, type_name, x, y):
        self.type = type_name
        self.x = x
        self.y = y
        self.lifetime = 300  # 5 seconds at 60fps
        
    def update(self):
        self.lifetime -= 1
        
    def draw(self, screen, cell_size):
        if self.lifetime > 0:
            alpha = min(255, self.lifetime * 2)
            color = (255, 255, 0, alpha)  # Yellow glow
            rect = pygame.Rect(self.x * cell_size, self.y * cell_size, cell_size, cell_size)
            pygame.draw.rect(screen, color[:3], rect)
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)

class PowerUpManager:
    def __init__(self):
        self.power_ups = []
        self.spawn_chance = 0.1  # 10% chance per line clear
        
    def maybe_spawn_powerup(self, cleared_rows, grid_width):
        if random.random() < self.spawn_chance:
            x = random.randint(0, grid_width - 1)
            y = random.choice(cleared_rows)
            power_type = random.choice(['clear_line', 'slow_time', 'ghost_block'])
            self.power_ups.append(PowerUp(power_type, x, y))
    
    def update(self):
        self.power_ups = [p for p in self.power_ups if p.lifetime > 0]
        for power_up in self.power_ups:
            power_up.update()
    
    def check_collection(self, block_x, block_y):
        for power_up in self.power_ups[:]:
            if power_up.x == block_x and power_up.y == block_y:
                self.power_ups.remove(power_up)
                return power_up.type
        return None