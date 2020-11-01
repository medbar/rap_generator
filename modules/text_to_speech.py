import os
import argparse
from speechpro.cloud.speech import synthesis
import random

assert os.environ.get("SPEECHPRO_USERNAME") is not None and \
    os.environ.get("SPEECHPRO_DOMAIN_ID") is not None and \
    os.environ.get("SPEECHPRO_PASSWORD") is not None, RuntimeError("Auth parameters must be defined! see "
"https://github.com/speechpro/cloud-python#%D0%BF%D0%B5%D1%80%D0%B5%D0%BC%D0%B5%D0%BD%D0%BD%D1%8B%D0%B5-%D1%81%D1%80%D0%B5%D0%B4%D1%8B")


class Text2Speech:
    @staticmethod
    def add_args(parser: argparse.ArgumentParser):
        pass
        #parser.add_argument("--")

    def __init__(self, args):
        self.args = args
        self.сlient = synthesis.SynthesisClient()
        self.profile = synthesis.enums.PlaybackProfile.SPEAKER
        #random.seed()

    def synthesize(self, text, voice=synthesis.enums.Voice.VLADIMIR):
        audio = self.сlient.synthesize(voice, self.profile, text)
        return audio

    def get_random_voice(self):
        return random.choice(list(synthesis.enums.Voice))
