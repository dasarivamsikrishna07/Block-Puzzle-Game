import pygame

class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init()
            self.sounds = {}
            self.music_volume = 0.7
            self.sfx_volume = 0.8
            self.enabled = True
        except:
            self.enabled = False
        
    def load_sounds(self):
        if not self.enabled:
            return
            
        # For web deployment, sounds are optional
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
                pass  # Sound file not found - game works without audio
    
    def play_sound(self, sound_name):
        if self.enabled and sound_name in self.sounds:
            try:
                self.sounds[sound_name].play()
            except:
                pass  # Ignore audio errors in web environment
