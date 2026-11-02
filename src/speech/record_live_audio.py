
import queue

import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write

SAMPLE_RATE = 16000
CHUNK_SIZE = 1280
DURATION_SECONDS = 8
DEVICE_ID = 1

audio_queue = queue.Queue()


def callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)

    audio_queue.put(indata.copy())


print("Recording live microphone audio...")
print("Speak 'Hey Jarvis' clearly several times.")

with sd.InputStream(
    device=DEVICE_ID,
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    blocksize=CHUNK_SIZE,
    callback=callback,
):
    chunks = []

    for _ in range(
        DURATION_SECONDS * SAMPLE_RATE // CHUNK_SIZE
    ):
        chunk = audio_queue.get()
        chunks.append(chunk.copy())

audio = np.concatenate(chunks, axis=0)

write("wake_live.wav", SAMPLE_RATE, audio)

audio_float = audio.astype(np.float32)
rms = float(np.sqrt(np.mean(audio_float ** 2)))
peak = int(np.max(np.abs(audio.astype(np.int32))))

print("\nSaved as wake_live.wav")
print("Samples:", len(audio))
print("RMS volume:", round(rms, 2))
print("Peak volume:", peak)
