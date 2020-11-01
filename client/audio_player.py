import argparse
import os
import time
import pygame
import glob
import logging
import random
import io

logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s -   %(message)s", datefmt="%m/%d/%Y %H:%M:%S", level=logging.INFO,
)
logger = logging.getLogger(__name__)


class AudioPlayer:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        parser.add_argument('--minus_dir', type=str, default='audio/')
        parser.add_argument('--minus_volume', type=float, default=0.85)
        pass

    def __init__(self, args):
        self.args = args
        self.all_minuses = [p for p in glob.glob(self.args.minus_dir + '/*.wav')]
        self.all_minuses.extend([p for p in glob.glob(self.args.minus_dir + '/*.mp3')])
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.init()
        pygame.mixer.set_num_channels(1)
        self.channel = pygame.mixer.find_channel()
        pygame.mixer.music.set_volume(args.minus_volume)
        random.seed()

    def load_all_bg_sounds(self):
        self.play_sound_bg(self.all_minuses[0])
        for s in self.all_minuses[1:]:
            pygame.mixer.music.queue(s)

    def play_sound_bg(self, sound_fn=None):
        if sound_fn is None:
            sound_fn = random.choice(self.all_minuses)
        logger.info('Playing {} background music.'.format(sound_fn))
        pygame.mixer.music.load(sound_fn)
        pygame.mixer.music.play()

    def play_sound(self, sound_fn):
        s = pygame.mixer.Sound(sound_fn)
        s.play()

    def play_sound_from_bytes(self, bytes):
        b_stream = io.BytesIO(bytes)
        s = pygame.mixer.Sound(buffer=bytes)
        if self.channel.get_busy():
            self.channel.queue(s)
        else:
            self.channel.play(s)

