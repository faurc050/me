import array
import math
import os

import pygame


class AudioManager:
    def __init__(self):
        self.enabled = False
        self.sounds = {}
        self.music_channel = None
        self.current_theme = None
        self.music_muted = False

        self.music_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "music",
            "THE LAST SHADOW.mp3"
        )

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

        # Sound effects only
        self.sounds["attack"] = self._make_tone(220, 0.07, 0.22)
        self.sounds["shoot"] = self._make_tone(560, 0.05, 0.18)
        self.sounds["dodge"] = self._make_tone(330, 0.09, 0.15)
        self.sounds["hit"] = self._make_tone(120, 0.09, 0.22)
        self.sounds["hurt"] = self._make_tone(90, 0.14, 0.28)
        self.sounds["victory"] = self._make_chord(
            (220, 330, 440), 0.22, 0.18
        )
        self.sounds["death"] = self._make_tone(60, 0.28, 0.22)
        self.sounds["sword_voice"] = self._make_voice(
            160, 0.18, 0.16
        )
        self.sounds["boss_roar"] = self._make_voice(
            72, 0.3, 0.22
        )

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
            sample = int(
                32767 * volume * envelope * wave
            )
            pcm.append(sample)

        return pygame.mixer.Sound(buffer=pcm.tobytes())

    def _make_chord(self, frequencies, duration, volume):
        if not self.enabled:
            return None

        sample_rate = 22050
        frame_count = int(sample_rate * duration)
        pcm = array.array("h")

        for i in range(frame_count):
            time = i / sample_rate
            envelope = max(0.0, 1.0 - (i / frame_count))
            value = 0.0

            for frequency in frequencies:
                value += math.sin(
                    2 * math.pi * frequency * time
                )

            value /= len(frequencies)

            sample = int(
                32767 * volume * envelope * value
            )

            pcm.append(sample)

        return pygame.mixer.Sound(buffer=pcm.tobytes())

    def _make_voice(self, base_frequency, duration, volume):
        if not self.enabled:
            return None

        sample_rate = 22050
        frame_count = int(sample_rate * duration)
        pcm = array.array("h")

        for i in range(frame_count):
            time = i / sample_rate
            envelope = max(0.0, 1.0 - (i / frame_count))

            vibrato = 1.0 + 0.12 * math.sin(
                2 * math.pi * 6 * time
            )

            tremor = math.sin(
                2 * math.pi
                * (base_frequency * vibrato)
                * time
            )

            formant = math.sin(
                2 * math.pi
                * (base_frequency * 0.5)
                * time
                + 0.7
            )

            sample = int(
                32767
                * volume
                * envelope
                * (0.65 * tremor + 0.35 * formant)
            )

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

    def play_theme(self, name):
        """
        There is only ONE music track now.
        Menu and game both use THE LAST SHADOW.mp3.
        """

        if not self.enabled or self.music_muted:
            return

        if not os.path.exists(self.music_path):
            print("Music not found:")
            print(self.music_path)
            return

        try:
            # Don't restart the song if it is already playing.
            if pygame.mixer.music.get_busy():
                self.current_theme = name
                return

            pygame.mixer.music.load(self.music_path)
            pygame.mixer.music.set_volume(0.55)
            pygame.mixer.music.play(-1)

            self.current_theme = name

        except Exception as e:
            print("Music error:", e)

    def toggle_music(self):
        if not self.enabled:
            return False

        self.music_muted = not self.music_muted

        if self.music_muted:
            pygame.mixer.music.set_volume(0.0)
        else:
            pygame.mixer.music.set_volume(0.55)

            if not pygame.mixer.music.get_busy():
                self.play_theme(
                    self.current_theme or "game"
                )

        return self.music_muted

    def pause_music(self):
        if not self.enabled:
            return

        try:
            pygame.mixer.music.set_volume(0.0)
        except Exception:
            pass

    def resume_music(self):
        if not self.enabled or self.music_muted:
            return

        try:
            pygame.mixer.music.set_volume(0.55)

            if not pygame.mixer.music.get_busy():
                self.play_theme(
                    self.current_theme or "game"
                )

        except Exception:
            pass