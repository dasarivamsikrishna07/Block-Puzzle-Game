# Neon Tetris

A modern Tetris clone with neon aesthetics built with Pygame.

## Play Online

You can play the game online at: [https://your-netlify-site.netlify.app](https://your-netlify-site.netlify.app)

## Features

- Neon visual effects with glowing blocks
- Particle effects when clearing lines
- High score system that saves your top 5 scores
- Next block preview
- Game statistics display
- Start screen and game over screen

## Controls

- **Arrow Left/Right**: Move block
- **Arrow Up**: Rotate block
- **Arrow Down**: Move block down faster
- **Space**: Start game (on start screen)
- **H**: View high scores
- **R**: Restart game (after game over)
- **M**: Return to main menu (after game over)

## Development

This game was built with:
- Python 3.x
- Pygame
- Pygbag (for web export)

## Running Locally

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the game:
   ```
   python src/main.py
   ```

3. Build for web:
   ```
   python -m pygbag --build src
   ```