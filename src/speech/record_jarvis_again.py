
import sounddevice as sd
import numpy as np
from scipy.io.wavfile import write

SAMPLE_RATE = 16000
DURATION = 8
DEVICE_ID = 1

input("Press Enter, then say 'Hey Jarvis' three times...")
print("Recording for 8 seconds. Start speaking after one second.")

audio = sd.rec(
    DURATION * SAMPLE_RATE,
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    device=DEVICE_ID,
)

sd.wait()

audio = audio.reshape(-1)
write("wake_jarvis_again.wav", SAMPLE_RATE, audio)

print("\nAudio levels:")
for start in range(0, len(audio), SAMPLE_RATE):
    chunk = audio[start:start + SAMPLE_RATE]
    rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))
    print(f"{start}-{start + 1}s: RMS {rms:.0f}")

print("\nSaved wake_jarvis_again.wav")
