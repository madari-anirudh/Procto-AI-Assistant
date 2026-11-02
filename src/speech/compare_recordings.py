
import numpy as np
from scipy.io.wavfile import read
from openwakeword.model import Model

MODEL_PATH = (
    r".\.venv\Lib\site-packages\openwakeword"
    r"\resources\models\hey_jarvis_v0.1.onnx"
)

filename = "wake_test_jarvis.wav"

sample_rate, audio = read(filename)
audio = np.asarray(audio).reshape(-1).astype(np.int16)

model = Model(
    wakeword_models=[MODEL_PATH],
    inference_framework="onnx",
)

print("Testing audio in 1280-sample chunks...\n")

for start in range(0, len(audio) - 1279, 1280):
    chunk = audio[start:start + 1280]
    rms = float(np.sqrt(np.mean(chunk.astype(np.float32) ** 2)))

    score = float(
        model.predict(chunk)["hey_jarvis_v0.1"]
    )

    print(
        f"Time {start / sample_rate:.2f}s | "
        f"RMS {rms:7.1f} | "
        f"Score {score:.6f}"
    )
