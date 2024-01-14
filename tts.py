# from torch import package, device, hub
from torch import package, hub
from sounddevice import play, stop
from time import sleep
from os import path

# device = device('cpu')

local_file = 'model.pt'
if not path.isfile(local_file):
    hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt', local_file)

model = package.PackageImporter(local_file).load_pickle("tts_models", "model")
# model.to(device)


def speak(what: str):
    audio = model.apply_tts(text=what + "..", speaker='aidar', sample_rate=48000, put_accent=True, put_yo=True)
    play(audio, 48000 * 1.05)
    sleep((len(audio) / 48000) + 0.5)
    stop()
