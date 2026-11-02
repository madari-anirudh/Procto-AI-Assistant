
import queue

import numpy as np
import sounddevice as sd
from openwakeword.model import Model


MODEL_PATH = (
    r".\.venv\Lib\site-packages\openwakeword"
    r"\resources\models\hey_jarvis_v0.1.onnx"
)

# Keep only a small buffer of audio chunks.
audio_queue = queue.Queue(maxsize=8)

# Load the wake-word model only once per Procto process.
_model = None


def get_wake_word_model():
    global _model

    if _model is None:
        print("Loading wake-word detector for the first time...")
        _model = Model(
            wakeword_models=[MODEL_PATH],
            inference_framework="onnx",
        )

    return _model


def audio_callback(indata, frames, time_info, status):
    if status:
        print("Audio status:", status)

    try:
        audio_queue.put_nowait(indata.copy())
    except queue.Full:
        # Drop the oldest chunk if processing falls behind.
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            pass

        try:
            audio_queue.put_nowait(indata.copy())
        except queue.Full:
            pass
def wait_for_wake_word():
    model = get_wake_word_model()

    # Clear audio left over from a previous listening session.
    while not audio_queue.empty():
        try:
            audio_queue.get_nowait()
        except queue.Empty:
            break

    print("\nListening for 'Hey Jarvis'...")
    print("Say the phrase clearly several times. Press Ctrl+C to stop.\n")

    chunk_count = 0

    with sd.InputStream(
        device=1,
        samplerate=16000,
        channels=1,
        dtype="int16",
        blocksize=1280,
        callback=audio_callback,
    ):
        while True:
            audio = audio_queue.get()
            audio = np.asarray(audio).reshape(-1).astype(np.int16)

            if audio.size != 1280:
                print(f"Unexpected audio chunk size: {audio.size}")
                continue

            predictions = model.predict(audio)
            chunk_count += 1

            score = float(predictions["hey_jarvis_v0.1"])

            # Print diagnostics occasionally instead of every 12 chunks.
            if chunk_count % 100 == 0:
                rms = float(
                    np.sqrt(np.mean(audio.astype(np.float32) ** 2))
                )
                print(f"Mic level: {rms:.0f} | Score: {score:.4f}")

            if score > 0.15:
                print(
                    f"\nWake word detected: "
                    f"hey_jarvis_v0.1 ({score:.2f})"
                )
                return True


if __name__ == "__main__":
    try:
        wait_for_wake_word()
    except KeyboardInterrupt:
        print("\nTest stopped.")
    except Exception as error:
        print(f"\nERROR: {type(error).__name__}: {error}")
