
import numpy as np
from scipy.io.wavfile import read
from openwakeword.model import Model

MODEL_PATH = (
    r".\.venv\Lib\site-packages\openwakeword"
    r"\resources\models\hey_jarvis_v0.1.onnx"
)

model = Model(
    wakeword_models=[MODEL_PATH],
    inference_framework="onnx",
)

sample_rate, audio = read("wake_live.wav")
audio = np.asarray(audio).reshape(-1).astype(np.int16)

if sample_rate != 16000:
    raise ValueError(f"Expected 16000 Hz, got {sample_rate}")

print("Testing saved recording in 1280-sample chunks...")
scores = []

for start in range(0, len(audio) - 1279, 1280):
    chunk = audio[start:start + 1280]
    prediction = model.predict(chunk)
    scores.append(float(prediction["hey_jarvis_v0.1"]))

print("Number of chunks:", len(scores))
print("Highest streaming score:", max(scores))
print("Last streaming score:", scores[-1])
