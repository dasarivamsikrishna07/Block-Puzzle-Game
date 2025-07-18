import asyncio
import pygame
from game import Game, COLORS

async def main():
    pygame.init()
    
    SCREEN_WIDTH = 1000
    SCREEN_HEIGHT = 700
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Neon Tetris - Block Puzzle Game")
    
    game = Game(SCREEN_WIDTH, SCREEN_HEIGHT)
    await game.initialize()  # Initialize the game properly
    clock = pygame.time.Clock()

    def draw_gradient_background(screen):
        """Draw a cool gradient background"""
        for y in range(SCREEN_HEIGHT):
            color_ratio = y / SCREEN_HEIGHT
            r = int(10 + color_ratio * 20)
            g = int(5 + color_ratio * 15)
            b = int(30 + color_ratio * 40)
            pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))

    def draw_neon_border(screen, rect, color, width=3):
        """Draw a glowing neon border effect"""
        for i in range(width):
            expanded_rect = pygame.Rect(rect.x - i, rect.y - i, rect.width + 2*i, rect.height + 2*i)
            pygame.draw.rect(screen, color, expanded_rect, 1)

    def draw_start_screen(screen, game):
        """Draw the start screen"""
        # Title
        title_font = pygame.font.Font(None, 96)
        title_text = title_font.render("NEON TETRIS", True, COLORS["cyan"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 150))
        screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_font = pygame.font.Font(None, 48)
        subtitle_text = subtitle_font.render("Block Puzzle Game", True, COLORS["magenta"])
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, 220))
        screen.blit(subtitle_text, subtitle_rect)
        
        # Instructions
        font = pygame.font.Font(None, 36)
        instructions = [
            "Press SPACE to Start",
            "Press H for High Scores",
            "",
            "Controls:",
            "Arrow Keys - Move/Rotate",
            "Down Arrow - Drop Faster"
        ]
        
        y_start = 320
        for i, instruction in enumerate(instructions):
            if instruction == "":
                y_start += 20
                continue
            color = COLORS["yellow"] if i < 2 else COLORS["white"]
            text = font.render(instruction, True, color)
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 40))
            screen.blit(text, text_rect)

    def draw_high_scores_screen(screen, game):
        """Draw the high scores screen"""
        # Title
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("HIGH SCORES", True, COLORS["yellow"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(title_text, title_rect)
        
        # High scores
        font = pygame.font.Font(None, 48)
        y_start = 200
        
        if game.high_score_manager.high_scores:
            for i, score_data in enumerate(game.high_score_manager.high_scores):
                # Handle both dict format and simple number format
                if isinstance(score_data, dict):
                    name = score_data.get("name", "Anonymous")
                    score = score_data.get("score", 0)
                    display_text = f"{i+1}. {name}: {score:,}"
                else:
                    # Fallback for old format
                    display_text = f"{i+1}. Anonymous: {score_data:,}"
                
                score_text = font.render(display_text, True, COLORS["white"])
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, y_start + i * 60))
                screen.blit(score_text, score_rect)
        else:
            no_scores_text = font.render("No high scores yet!", True, COLORS["white"])
            no_scores_rect = no_scores_text.get_rect(center=(SCREEN_WIDTH // 2, y_start + 60))
            screen.blit(no_scores_text, no_scores_rect)
        
        # Back instruction
        back_font = pygame.font.Font(None, 36)
        back_text = back_font.render("Press H to go back", True, COLORS["cyan"])
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH // 2, 550))
        screen.blit(back_text, back_rect)

    def draw_name_input_screen(screen, game):
        """Draw name input screen for high scores"""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        screen.blit(overlay, (0, 0))
        
        # Title
        title_font = pygame.font.Font(None, 72)
        title_text = title_font.render("NEW HIGH SCORE!", True, COLORS["yellow"])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
        screen.blit(title_text, title_rect)
        
        # Score
        score_font = pygame.font.Font(None, 48)
        score_text = score_font.render(f"Score: {game.score:,}", True, COLORS["white"])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        screen.blit(score_text, score_rect)
        
        # Name input
        name_font = pygame.font.Font(None, 36)
        name_prompt = name_font.render("Enter your name:", True, COLORS["cyan"])
        name_rect = name_prompt.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        screen.blit(name_prompt, name_rect)
        
        # Name field
        name_display = game.player_name + "_" if len(game.player_name) < 15 else game.player_name
        name_text = name_font.render(name_display, True, COLORS["white"])
        name_text_rect = name_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        
        # Name field background
        field_rect = pygame.Rect(name_text_rect.x - 10, name_text_rect.y - 5, 
                               max(200, name_text_rect.width + 20), name_text_rect.height + 10)
        pygame.draw.rect(screen, (40, 40, 60), field_rect)
        pygame.draw.rect(screen, COLORS["cyan"], field_rect, 2)
        
        screen.blit(name_text, name_text_rect)
        
        # Instructions
        instruction_text = name_font.render("Press ENTER to save", True, COLORS["yellow"])
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 120))
        screen.blit(instruction_text, instruction_rect)

    def draw_next_block_panel(screen, game):
        """Draw an enhanced next block preview panel"""
        panel_x = game.grid_width * game.cell_size + 30
        panel_y = 80
        panel_width = 200
        panel_height = 150
        
        # Panel background with neon border
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (20, 20, 40), panel_rect)
        draw_neon_border(screen, panel_rect, COLORS["cyan"])
        
        # Title
        font = pygame.font.Font(None, 28)
        title_text = font.render("NEXT BLOCK", True, COLORS["cyan"])
        screen.blit(title_text, (panel_x + 10, panel_y + 10))
        
        # Draw next block if it exists
        if game.next_block:
            # Center the block in the panel
            shape = game.next_block.get_rotated_shape()
            block_width = len(shape[0]) * 25
            block_height = len(shape) * 25
            
            block_start_x = panel_x + (panel_width - block_width) // 2
            block_start_y = panel_y + 50 + (80 - block_height) // 2
            
            for y, row in enumerate(shape):
                for x, cell in enumerate(row):
                    if cell:
                        block_rect = pygame.Rect(
                            block_start_x + x * 25, 
                            block_start_y + y * 25, 
                            23, 23
                        )
                        # Draw block with glow effect
                        pygame.draw.rect(screen, game.next_block.color, block_rect)
                        # Add highlight
                        highlight_rect = pygame.Rect(block_rect.x + 2, block_rect.y + 2, 
                                                   block_rect.width - 4, block_rect.height - 4)
                        highlight_color = tuple(min(255, c + 80) for c in game.next_block.color)
                        pygame.draw.rect(screen, highlight_color, highlight_rect, 2)
                        # Border
                        pygame.draw.rect(screen, (255, 255, 255), block_rect, 1)

    def draw_stats_panel(screen, game):
        """Draw enhanced stats panel"""
        panel_x = game.grid_width * game.cell_size + 30
        panel_y = 260
        panel_width = 200
        panel_height = 250
        
        # Panel background
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, (20, 20, 40), panel_rect)
        draw_neon_border(screen, panel_rect, COLORS["yellow"])
        
        # Stats
        font = pygame.font.Font(None, 24)
        y_offset = panel_y + 20
        
        # Score
        score_text = font.render(f"SCORE", True, COLORS["yellow"])
        screen.blit(score_text, (panel_x + 10, y_offset))
        score_value = font.render(f"{game.score:,}", True, COLORS["white"])
        screen.blit(score_value, (panel_x + 10, y_offset + 25))
        
        # High Score
        high_score = 0
        if game.high_score_manager.high_scores:
            high_score = max(s["score"] for s in game.high_score_manager.high_scores)
        high_score_text = font.render(f"HIGH SCORE", True, COLORS["yellow"])
        screen.blit(high_score_text, (panel_x + 10, y_offset + 70))
        high_score_value = font.render(f"{high_score:,}", True, COLORS["white"])
        screen.blit(high_score_value, (panel_x + 10, y_offset + 95))
        
        # Time
        if not game.game_over:
            elapsed_time = (pygame.time.get_ticks() - game.start_time) // 1000
            time_text = font.render(f"TIME", True, COLORS["yellow"])
            screen.blit(time_text, (panel_x + 10, y_offset + 140))
            time_value = font.render(f"{elapsed_time}s", True, COLORS["white"])
            screen.blit(time_value, (panel_x + 10, y_offset + 165))
        
        # Level
        level_text = font.render(f"LEVEL", True, COLORS["yellow"])
        screen.blit(level_text, (panel_x + 10, y_offset + 190))
        level_value = font.render(f"{game.level}", True, COLORS["white"])
        screen.blit(level_value, (panel_x + 10, y_offset + 215))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            await game.handle_input(event)  # Make this async

        await game.update()  # Make this async
        
        # Draw gradient background
        draw_gradient_background(screen)

        if not game.game_started:
            if game.show_high_scores:
                print("Drawing high scores screen")  # Debug
                draw_high_scores_screen(screen, game)
            else:
                print("Drawing start screen")  # Debug
                draw_start_screen(screen, game)
        elif game.show_name_input:
            draw_name_input_screen(screen, game)
        else:
            # Draw game elements with enhanced graphics
            game.draw_grid(screen)
            
            # Draw particles
            game.draw_particles(screen)
            
            if game.current_block and not game.game_over:
                game.draw_block(screen, game.current_block)

            # Draw enhanced UI panels
            draw_next_block_panel(screen, game)
            draw_stats_panel(screen, game)

            # Game Over screen with effects
            if game.game_over:
                # Semi-transparent overlay
                overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                screen.blit(overlay, (0, 0))
                
                # Check if it's a high score
                is_high_score = game.high_score_manager.is_high_score(game.score)
                
                # Game over text with glow
                game_over_font = pygame.font.Font(None, 84)
                game_over_text = game_over_font.render("GAME OVER", True, COLORS["red"])
                text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 100))
                screen.blit(game_over_text, text_rect)
                
                # Final score
                score_font = pygame.font.Font(None, 48)
                score_text = score_font.render(f"Final Score: {game.score:,}", True, COLORS["white"])
                score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
                screen.blit(score_text, score_rect)
                
                # High score notification
                if is_high_score:
                    high_score_font = pygame.font.Font(None, 36)
                    high_score_text = high_score_font.render("NEW HIGH SCORE!", True, COLORS["yellow"])
                    high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                    screen.blit(high_score_text, high_score_rect)
                
                # Instructions
                restart_font = pygame.font.Font(None, 36)
                restart_text = restart_font.render("Press R to Restart", True, COLORS["cyan"])
                restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
                screen.blit(restart_text, restart_rect)
                
                menu_text = restart_font.render("Press M for Main Menu", True, COLORS["cyan"])
                menu_rect = menu_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
                screen.blit(menu_text, menu_rect)

        pygame.display.flip()
        clock.tick(60)
        await asyncio.sleep(0)  # Required for pygbag

    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())














