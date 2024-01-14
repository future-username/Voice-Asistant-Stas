from vosk import Model, KaldiRecognizer
from sounddevice import RawInputStream
from queue import Queue
from json import loads

model = Model("model")

queue = Queue()


def listen(callback):
    with RawInputStream(samplerate=16000, blocksize=8000, dtype='int16', channels=1,
                        callback=lambda in_data, frames, time, status: queue.put(bytes(in_data))):

        rec = KaldiRecognizer(model, 16000)
        while True:
            data = queue.get()
            if rec.AcceptWaveform(data):
                callback(loads(rec.Result())["text"])
