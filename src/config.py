import os
from dataclasses import dataclass
from importlib.util import find_spec
from pathlib import Path


def _env_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return int(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be an integer.") from exc


def _env_float(name: str, default: float) -> float:
    value = os.getenv(name)
    if value is None or not value.strip():
        return default
    try:
        return float(value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a number.") from exc


def _default_model_path() -> Path:
    package = find_spec("openwakeword")
    if package and package.submodule_search_locations:
        return (
            Path(next(iter(package.submodule_search_locations)))
            / "resources"
            / "models"
            / "hey_jarvis_v0.1.onnx"
        )
    return Path("hey_jarvis_v0.1.onnx")


@dataclass(frozen=True)
class Settings:
    speech_key: str | None
    speech_region: str | None
    speech_recognition_language: str
    speech_synthesis_voice: str
    wake_word_model_path: Path
    wake_word_threshold: float
    audio_device: int | str | None
    audio_sample_rate: int
    audio_block_size: int

    @classmethod
    def from_environment(cls) -> "Settings":
        device = os.getenv("PROCTO_AUDIO_DEVICE")
        parsed_device: int | str | None = device
        if device is not None:
            try:
                parsed_device = int(device)
            except ValueError:
                if not device.strip():
                    parsed_device = None

        threshold = _env_float("PROCTO_WAKE_WORD_THRESHOLD", 0.15)
        if not 0 <= threshold <= 1:
            raise RuntimeError("PROCTO_WAKE_WORD_THRESHOLD must be between 0 and 1.")

        model_path = os.getenv("PROCTO_WAKE_WORD_MODEL")
        if not model_path or not model_path.strip():
            model_path = str(_default_model_path())

        return cls(
            speech_key=os.getenv("SPEECH_KEY"),
            speech_region=os.getenv("SPEECH_REGION"),
            speech_recognition_language=os.getenv(
                "PROCTO_SPEECH_RECOGNITION_LANGUAGE", "te-IN"
            ),
            speech_synthesis_voice=os.getenv(
                "PROCTO_SPEECH_SYNTHESIS_VOICE", "te-IN-ShrutiNeural"
            ),
            wake_word_model_path=Path(model_path).expanduser(),
            wake_word_threshold=threshold,
            audio_device=parsed_device,
            audio_sample_rate=_env_int("PROCTO_AUDIO_SAMPLE_RATE", 16000),
            audio_block_size=_env_int("PROCTO_AUDIO_BLOCK_SIZE", 1280),
        )


settings = Settings.from_environment()
