from torch import package, hub
from sounddevice import play, stop
from time import sleep
from os import path

from vosk import Model, KaldiRecognizer
from sounddevice import RawInputStream
from queue import Queue
from json import loads


class Voice:
    def __init__(self):
        self.local_file = 'model.pt'
        self.model = package.PackageImporter(self.local_file).load_pickle("tts_models", "model")
        if not path.isfile(self.local_file):
            hub.download_url_to_file('https://models.silero.ai/models/tts/ru/v3_1_ru.pt', self.local_file)

    def speak(self, what: str):
        audio = self.model.apply_tts(text=f"{what}..", speaker='aidar', sample_rate=48000, put_accent=True, put_yo=True)
        play(audio, 48000 * 1.05)
        sleep((len(audio) / 48000) + 0.5)
        stop()


class Microphone:
    def __init__(self):
        self.model = Model("model")
        self.queue = Queue()

    def listen(self, callback):
        with RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1,
                            callback=lambda in_data, frames, time, status: self.queue.put(bytes(in_data))):

            rec = KaldiRecognizer(self.model, 16000)
            while True:
                data = self.queue.get()
                if rec.AcceptWaveform(data):
                    callback(loads(rec.Result())["text"])
