import pygame
import random
import json
import os
import asyncio

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.velocity_x = random.uniform(-3, 3)
        self.velocity_y = random.uniform(-5, -1)
        self.lifetime = 60
        self.max_lifetime = 60
        
    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.velocity_y += 0.1  # Gravity
        self.lifetime -= 1
        
    def draw(self, screen):
        if self.lifetime > 0:
            alpha = self.lifetime / self.max_lifetime
            size = int(4 * alpha)
            if size > 0:
                pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

# Enhanced color palette with neon/glow effects
COLORS = {
    "black": (0, 0, 0),
    "white": (255, 255, 255),
    "red": (255, 50, 50),
    "green": (50, 255, 50),
    "blue": (50, 50, 255),
    "cyan": (50, 255, 255),
    "magenta": (255, 50, 255),
    "yellow": (255, 255, 50),
    "orange": (255, 165, 50),
    "purple": (200, 50, 255),
    "lime": (150, 255, 50),
    "pink": (255, 100, 150),
}

# Block shapes and their rotations
SHAPES = {
    "I": [
        [0, 0, 0, 0],
        [1, 1, 1, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
    ],
    "J": [
        [1, 0, 0],
        [1, 1, 1],
        [0, 0, 0],
    ],
    "L": [
        [0, 0, 1],
        [1, 1, 1],
        [0, 0, 0],
    ],
    "O": [
        [1, 1],
        [1, 1],
    ],
    "S": [
        [0, 1, 1],
        [1, 1, 0],
        [0, 0, 0],
    ],
    "T": [
        [0, 1, 0],
        [1, 1, 1],
        [0, 0, 0],
    ],
    "Z": [
        [1, 1, 0],
        [0, 1, 1],
        [0, 0, 0],
    ],
}

class Block:
    def __init__(self, shape, color):
        self.shape = shape
        self.color = color
        self.rotation = 0
        self.x = 0
        self.y = 0

    def get_rotated_shape(self):
        rotated = self.shape
        for _ in range(self.rotation):
            rotated = [list(row) for row in zip(*rotated[::-1])]
        return rotated

class HighScoreManager:
    def __init__(self):
        self.high_scores = []
        self.player_name = "Anonymous"
        
    async def initialize(self):
        """Initialize and load scores"""
        await self.load_scores()
    
    async def load_scores(self):
        """Load high scores from local storage or file"""
        try:
            # Try to load from local file for desktop
            if os.path.exists("highscores.json"):
                with open("highscores.json", 'r') as f:
                    scores_data = json.load(f)
                    if scores_data and isinstance(scores_data[0], dict):
                        self.high_scores = scores_data
                    else:
                        self.high_scores = [{"name": "Anonymous", "score": score} for score in scores_data]
            else:
                self.high_scores = []
        except:
            self.high_scores = []
    
    async def add_score(self, score: int):
        """Add a new score"""
        try:
            self.high_scores.append({"name": self.player_name, "score": score})
            self.high_scores.sort(key=lambda x: x["score"], reverse=True)
            self.high_scores = self.high_scores[:5]
            
            # Try to save to file for desktop
            try:
                with open("highscores.json", 'w') as f:
                    json.dump(self.high_scores, f)
            except:
                pass  # Ignore file save errors in web environment
            
            return True
        except:
            return False
    
    def is_high_score(self, score):
        """Check if score qualifies for high score list"""
        if len(self.high_scores) < 5:
            return True
        return score > min(s["score"] for s in self.high_scores) if self.high_scores else True

class Game:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.grid_width = 10
        self.grid_height = 20
        self.cell_size = 30
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.current_block = None
        self.next_block = None
        self.particles = []
        self.score = 0
        self.game_over = False
        self.game_started = False
        self.show_high_scores = False
        self.show_name_input = False
        self.player_name = ""
        self.game_tick = 500
        self.last_fall_time = pygame.time.get_ticks()
        self.start_time = pygame.time.get_ticks()
        self.high_score_manager = HighScoreManager()
        self.combo_count = 0
        self.last_clear_time = 0
        self.screen_shake = 0
        self.level = 1
        self.lines_cleared_total = 0
        
        # Initialize blocks
        self.generate_next_block()
        self.spawn_block()

    def generate_next_block(self):
        """Generate a new random block"""
        shape_name = random.choice(list(SHAPES.keys()))
        color = random.choice(list(COLORS.values())[2:])  # Skip black and white
        self.next_block = Block(SHAPES[shape_name], color)
    
    def spawn_block(self):
        """Spawn the next block as current block"""
        if self.next_block is None:
            self.generate_next_block()
        
        self.current_block = self.next_block
        self.current_block.x = self.grid_width // 2 - 1
        self.current_block.y = 0
        
        # Generate new next block
        self.generate_next_block()
        
        # Check for game over
        if self.check_collision(self.current_block):
            asyncio.create_task(self.handle_game_over())
    
    async def initialize(self):
        """Initialize game with database"""
        await self.high_score_manager.initialize()
    
    async def handle_game_over(self):
        """Handle game over with database save"""
        if self.high_score_manager.is_high_score(self.score):
            self.show_name_input = True
        else:
            self.game_over = True
    
    async def save_high_score(self):
        """Save high score with player name"""
        if self.player_name.strip():
            self.high_score_manager.player_name = self.player_name.strip()
            await self.high_score_manager.add_score(self.score)
        self.show_name_input = False
        self.game_over = True

    def start_game(self):
        """Start a new game"""
        self.game_started = True
        self.show_high_scores = False
        self.reset_game()

    def show_start_screen(self):
        """Show start screen"""
        self.game_started = False
        self.show_high_scores = False

    def toggle_high_scores(self):
        """Toggle high scores display"""
        self.show_high_scores = not self.show_high_scores

    def draw_grid(self, screen):
        """Draw the game grid"""
        for y, row in enumerate(self.grid):
            for x, cell in enumerate(row):
                rect = pygame.Rect(x * self.cell_size, y * self.cell_size, 
                                 self.cell_size, self.cell_size)
                if cell != 0:
                    pygame.draw.rect(screen, cell, rect)
                    pygame.draw.rect(screen, (255, 255, 255), rect, 1)
                else:
                    pygame.draw.rect(screen, (40, 40, 60), rect, 1)

    def draw_block(self, screen, block):
        """Draw block with enhanced graphics"""
        shape = block.get_rotated_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    rect = pygame.Rect(
                        (block.x + x) * self.cell_size, 
                        (block.y + y) * self.cell_size, 
                        self.cell_size, 
                        self.cell_size
                    )
                    
                    # Main block color
                    pygame.draw.rect(screen, block.color, rect)
                    
                    # Inner highlight for 3D effect
                    highlight_rect = pygame.Rect(rect.x + 2, rect.y + 2, rect.width - 4, rect.height - 4)
                    highlight_color = tuple(min(255, c + 80) for c in block.color)
                    pygame.draw.rect(screen, highlight_color, highlight_rect, 2)
                    
                    # Outer border
                    pygame.draw.rect(screen, (255, 255, 255), rect, 1)

    async def update(self):
        if not self.game_started or self.game_over:
            return

        # Update particles
        self.particles = [p for p in self.particles if p.lifetime > 0]
        for particle in self.particles:
            particle.update()

        current_time = pygame.time.get_ticks()
        if current_time - self.last_fall_time > self.game_tick:
            self.current_block.y += 1
            if self.check_collision(self.current_block):
                self.current_block.y -= 1
                self.lock_block()
                self.clear_lines()
                self.spawn_block()
            self.last_fall_time = current_time

    async def handle_input(self, event):
        if self.show_name_input:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    await self.save_high_score()
                elif event.key == pygame.K_BACKSPACE:
                    self.player_name = self.player_name[:-1]
                else:
                    if len(self.player_name) < 15 and event.unicode.isprintable():
                        self.player_name += event.unicode
            return
        
        if not self.game_started:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.start_game()
                elif event.key == pygame.K_h:
                    print(f"H pressed! Current show_high_scores: {self.show_high_scores}")
                    self.toggle_high_scores()
                    print(f"After toggle: {self.show_high_scores}")
                    print(f"High scores data: {self.high_score_manager.high_scores}")
            return

        if self.game_over:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    self.reset_game()
                elif event.key == pygame.K_m:
                    self.show_start_screen()
            return

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.move_block(-1, 0)
            elif event.key == pygame.K_RIGHT:
                self.move_block(1, 0)
            elif event.key == pygame.K_DOWN:
                self.move_block(0, 1)
            elif event.key == pygame.K_UP:
                self.rotate_block()

    def reset_game(self):
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.score = 0
        self.game_over = False
        self.game_started = True
        self.last_fall_time = pygame.time.get_ticks()
        self.start_time = pygame.time.get_ticks()
        self.particles = []
        self.current_block = None
        self.next_block = None
        self.generate_next_block()
        self.spawn_block()

    def move_block(self, dx, dy):
        self.current_block.x += dx
        self.current_block.y += dy
        if self.check_collision(self.current_block):
            self.current_block.x -= dx
            self.current_block.y -= dy

    def rotate_block(self):
        original_rotation = self.current_block.rotation
        self.current_block.rotation = (self.current_block.rotation + 1) % 4
        if self.check_collision(self.current_block):
            self.current_block.rotation = original_rotation

    def check_collision(self, block):
        shape = block.get_rotated_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    grid_x = block.x + x
                    grid_y = block.y + y
                    if not (0 <= grid_x < self.grid_width and 0 <= grid_y < self.grid_height):
                        return True
                    if self.grid[grid_y][grid_x] != 0:
                        return True
        return False

    def lock_block(self):
        shape = self.current_block.get_rotated_shape()
        for y, row in enumerate(shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_block.y + y][self.current_block.x + x] = self.current_block.color

    def clear_lines(self):
        lines_cleared = 0
        full_rows = []
        for y, row in enumerate(self.grid):
            if all(cell != 0 for cell in row):
                lines_cleared += 1
                full_rows.append(y)

        if lines_cleared > 0:
            # Combo system
            current_time = pygame.time.get_ticks()
            if current_time - self.last_clear_time < 3000:  # 3 second window
                self.combo_count += 1
            else:
                self.combo_count = 1
            self.last_clear_time = current_time
            
            # Screen shake for big clears
            if lines_cleared >= 3:
                self.screen_shake = 10
            
            # Enhanced scoring with combos
            base_score = lines_cleared * 100 * self.level
            combo_bonus = self.combo_count * 50
            self.score += base_score + combo_bonus
            
            # Level progression
            self.lines_cleared_total += lines_cleared
            new_level = (self.lines_cleared_total // 10) + 1
            if new_level > self.level:
                self.level = new_level
                self.game_tick = max(50, 500 - (self.level * 30))  # Faster drops
            
            # Particle effects
            for y in full_rows:
                for x in range(self.grid_width):
                    for _ in range(15):  # More particles
                        particle_x = (x * self.cell_size) + (self.cell_size / 2)
                        particle_y = (y * self.cell_size) + (self.cell_size / 2)
                        self.particles.append(Particle(particle_x, particle_y, self.grid[y][x]))

            # Remove the cleared lines from the grid
            new_grid = [row for i, row in enumerate(self.grid) if i not in full_rows]
            # Add new empty lines at the top
            for _ in range(lines_cleared):
                new_grid.insert(0, [0 for _ in range(self.grid_width)])
            self.grid = new_grid

    def draw_particles(self, screen):
        """Draw particle effects"""
        for particle in self.particles:
            particle.draw(screen)


























