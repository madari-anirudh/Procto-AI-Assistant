
import os
import azure.cognitiveservices.speech as speechsdk


def speak(text: str) -> None:
    key = os.environ.get("SPEECH_KEY")
    region = os.environ.get("SPEECH_REGION")

    if not key or not region:
        raise RuntimeError(
            "Speech is not configured. Set SPEECH_KEY and SPEECH_REGION."
        )

    config = speechsdk.SpeechConfig(
        subscription=key,
        region=region,
    )
    config.speech_synthesis_voice_name = "te-IN-ShrutiNeural"

    synthesizer = speechsdk.SpeechSynthesizer(
        speech_config=config
    )

    result = synthesizer.speak_text_async(text).get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech output completed.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        raise RuntimeError(
            f"Speech synthesis failed: {details.reason}. "
            "Check the resource region, key, network, and quota."
        )


if __name__ == "__main__":
    speak(
        "Namaskaram! I am Procto, your personal AI assistant. "
        "Nenu meeku help cheyadaniki ready ga unnanu."
    )
