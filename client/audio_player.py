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
        pass

    def __init__(self, args):
        self.args = args
        self.all_minuses = [p for p in glob.glob(self.args.minus_dir + '/*.wav')]
        self.all_minuses.extend([p for p in glob.glob(self.args.minus_dir + '/*.mp3')])
        pygame.mixer.pre_init(frequency=22050, size=-16, channels=1, buffer=512)
        pygame.mixer.init()
        random.seed()

    def load_all_bg_sounds(self):
        for s in self.all_minuses:
            pygame.mixer.music.queue(s)

    def play_sound_bg(self, sound_fn=None):
        if sound_fn is None:
            sound_fn = random.choice(self.all_minuses)
        logger.info('Playing {} background music.'.format(sound_fn))
        pygame.mixer.music.load(sound_fn)
        pygame.mixer.music.play()

    def play_sound(self, sound_fn):
        pygame.mixer.Sound(sound_fn).play()

    def play_sound_from_bytes(self, bytes):
        b_stream = io.BytesIO(bytes)
        pygame.mixer.Sound(buffer=b_stream)

