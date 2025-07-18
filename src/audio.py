import pygame

class AudioManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}
        self.music_volume = 0.7
        self.sfx_volume = 0.8
        
    def load_sounds(self):
        # You'll need to add sound files to assets/sounds/
        sound_files = {
            'line_clear': 'line_clear.wav',
            'block_drop': 'block_drop.wav',
            'game_over': 'game_over.wav',
            'level_up': 'level_up.wav'
        }
        
        for name, file in sound_files.items():
            try:
                self.sounds[name] = pygame.mixer.Sound(f'assets/sounds/{file}')
                self.sounds[name].set_volume(self.sfx_volume)
            except:
                pass  # Sound file not found
    
    def play_sound(self, sound_name):
        if sound_name in self.sounds:
            self.sounds[sound_name].play()