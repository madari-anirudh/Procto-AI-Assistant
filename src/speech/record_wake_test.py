
import sounddevice as sd
from scipy.io.wavfile import write

SAMPLE_RATE = 16000
DURATION = 4

phrase = input("Which phrase will you record? (jarvis/procto): ").strip().lower()

if phrase not in ("jarvis", "procto"):
    raise SystemExit("Enter either jarvis or procto.")

output_file = f"wake_test_{phrase}.wav"

input(f"Press Enter, then say 'Hey {phrase.title()}' clearly...")
print("Recording for 4 seconds...")

audio = sd.rec(
    int(DURATION * SAMPLE_RATE),
    samplerate=SAMPLE_RATE,
    channels=1,
    dtype="int16",
    device=1,
)
sd.wait()

write(output_file, SAMPLE_RATE, audio)
print(f"Recording saved as {output_file}")
