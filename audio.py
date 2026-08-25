import array
import math

import pygame


class AudioManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.themes = {}
        self.music_channel = None
        self.current_theme = None
        self.music_muted = False
        self._init_mixer()

    def _init_mixer(self):
        try:
            pygame.mixer.pre_init(44100, -16, 2, 512)
            pygame.mixer.init()
        except Exception:
            try:
                pygame.mixer.init(22050, -16, 2, 512)
            except Exception:
                return False

        try:
            pygame.mixer.set_num_channels(8)
        except Exception:
            pass

        self.enabled = True
        self.sounds["attack"] = self._make_tone(220, 0.07, 0.22)
        self.sounds["shoot"] = self._make_tone(560, 0.05, 0.18)
        self.sounds["dodge"] = self._make_tone(330, 0.09, 0.15)
        self.sounds["hit"] = self._make_tone(120, 0.09, 0.22)
        self.sounds["hurt"] = self._make_tone(90, 0.14, 0.28)
        self.sounds["victory"] = self._make_chord((220, 330, 440), 0.22, 0.18)
        self.sounds["death"] = self._make_tone(60, 0.28, 0.22)

        self.themes["menu"] = self._build_theme([
            (220, 0.56), (262, 0.48), (330, 0.72), (294, 0.48),
            (262, 0.56), (220, 0.52), (196, 0.76), (174, 0.52),
            (220, 0.56), (262, 0.48), (330, 0.72), (294, 0.48),
            (330, 0.56), (262, 0.52), (220, 0.68), (196, 0.44),
        ], tempo=60, volume=0.03)
        self.themes["game"] = self._build_theme([
            (174, 0.42), (220, 0.38), (262, 0.52), (220, 0.38),
            (174, 0.42), (146, 0.38), (196, 0.52), (220, 0.38),
            (262, 0.42), (220, 0.38), (174, 0.52), (146, 0.38),
            (196, 0.42), (220, 0.38), (262, 0.52), (330, 0.64),
            (262, 0.42), (220, 0.38), (196, 0.52), (174, 0.38),
            (146, 0.42), (174, 0.38), (196, 0.52), (220, 0.70),
        ], tempo=64, volume=0.025)
        return True

    def _make_tone(self, frequency, duration, volume):
        if not self.enabled:
            return None
        sample_rate = 22050
        frame_count = int(sample_rate * duration)
        pcm = array.array("h")
        for i in range(frame_count):
            time = i / sample_rate
            wave = math.sin(2 * math.pi * frequency * time)
            envelope = max(0.0, 1.0 - (i / frame_count))
            sample = int(32767 * volume * envelope * wave)
            pcm.append(sample)
        return pygame.mixer.Sound(buffer=pcm.tobytes())

    def _make_chord(self, frequencies, duration, volume):
        if not self.enabled:
            return None
        sample_rate = 22050
        frame_count = int(sample_rate * duration)
        pcm = array.array("h")
        for i in range(frame_count):
            value = 0.0
            for frequency in frequencies:
                time = i / sample_rate
                wave = math.sin(2 * math.pi * frequency * time)
                envelope = max(0.0, 1.0 - (i / frame_count))
                value += wave * envelope
            sample = int(32767 * volume * (value / len(frequencies)))
            pcm.append(sample)
        return pygame.mixer.Sound(buffer=pcm.tobytes())

    def _build_theme(self, pattern, tempo=100, volume=0.06):
        if not self.enabled:
            return None
        sample_rate = 22050
        pcm = array.array("h")
        beat = 60.0 / tempo
        for frequency, duration in pattern:
            frames = int(sample_rate * duration)
            for i in range(frames):
                time = i / sample_rate
                wave = math.sin(2 * math.pi * frequency * time)
                env = min(1.0, (i / max(1, frames // 4)) * 0.8)
                if i > frames * 0.7:
                    env = max(0.0, 1.0 - ((i - frames * 0.7) / max(1, frames // 4)))
                sample = int(32767 * volume * env * wave)
                pcm.append(sample)
        return pygame.mixer.Sound(buffer=pcm.tobytes())

    def play(self, name):
        if not self.enabled:
            return
        sound = self.sounds.get(name)
        if sound is not None:
            try:
                sound.set_volume(0.9)
                sound.play()
            except Exception:
                pass

    def toggle_music(self):
        if not self.enabled:
            return False
        self.music_muted = not self.music_muted
        if self.music_channel is None:
            if self.music_muted:
                return True
            if self.current_theme is not None:
                self.play_theme(self.current_theme)
                return False
        if self.music_muted and self.music_channel is not None:
            self.music_channel.set_volume(0.0)
        elif self.music_channel is not None:
            self.music_channel.set_volume(1.0)
        return self.music_muted

    def pause_music(self):
        if not self.enabled or self.music_channel is None:
            return
        try:
            self.music_channel.set_volume(0.0)
        except Exception:
            pass

    def resume_music(self):
        if not self.enabled or self.music_channel is None or self.music_muted:
            return
        try:
            self.music_channel.set_volume(1.0)
        except Exception:
            pass

    def play_theme(self, name):
        if not self.enabled:
            return
        if self.music_muted:
            return
        if self.current_theme == name and self.music_channel is not None and self.music_channel.get_busy():
            return
        theme = self.themes.get(name)
        if theme is None:
            return
        if self.music_channel is None:
            try:
                self.music_channel = pygame.mixer.Channel(0)
            except Exception:
                self.enabled = False
                return
        self.current_theme = name
        try:
            self.music_channel.set_volume(0.55)
            self.music_channel.play(theme, loops=-1)
        except Exception:
            self.enabled = False
