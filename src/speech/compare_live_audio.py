
import queue

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import read
from openwakeword.model import Model

MODEL_PATH = (
    r".\.venv\Lib\site-packages\openwakeword"
    r"\resources\models\hey_jarvis_v0.1.onnx"
)

audio_queue = queue.Queue()


def callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)
    audio_queue.put(indata.copy())


def new_model():
    return Model(
        wakeword_models=[MODEL_PATH],
        inference_framework="onnx",
    )


# First: replay the known-good recording in streaming chunks.
_, saved_audio = read("wake_test_jarvis.wav")
saved_audio = np.asarray(saved_audio).reshape(-1).astype(np.int16)

model = new_model()
saved_scores = []

for start in range(0, len(saved_audio) - 1279, 1280):
    result = model.predict(saved_audio[start:start + 1280])
    saved_scores.append(float(result["hey_jarvis_v0.1"]))

print("Saved recording peak score:", max(saved_scores))

# Reset model state before live testing.
model = new_model()

while not audio_queue.empty():
    audio_queue.get_nowait()

print("\nSay 'Hey Jarvis' clearly during the live test.")

with sd.InputStream(
    device=1,
    samplerate=16000,
    channels=1,
    dtype="int16",
    blocksize=1280,
    callback=callback,
):
    live_scores = []

    for _ in range(100):  # Approximately 8 seconds
        audio = np.asarray(audio_queue.get()).reshape(-1).astype(np.int16)
        result = model.predict(audio)
        live_scores.append(float(result["hey_jarvis_v0.1"]))

print("Live peak score:", max(live_scores))
print("Live average score:", float(np.mean(live_scores)))
