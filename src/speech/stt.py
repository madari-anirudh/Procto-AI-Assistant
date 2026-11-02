
import os
import azure.cognitiveservices.speech as speechsdk


def listen_once() -> str:
    key = os.environ.get("SPEECH_KEY")
    region = os.environ.get("SPEECH_REGION")

    if not key or not region:
        raise RuntimeError("Speech credentials are not configured.")

    config = speechsdk.SpeechConfig(
        subscription=key,
        region=region,
    )

    # Start with Telugu. Test English and mixed-language recognition
    # separately before choosing a production recognition strategy.
    config.speech_recognition_language = "te-IN"

    audio = speechsdk.audio.AudioConfig(use_default_microphone=True)
    recognizer = speechsdk.SpeechRecognizer(
        speech_config=config,
        audio_config=audio,
    )

    print("Listening... Speak a short Telugu command.")
    result = recognizer.recognize_once_async().get()

    if result.reason == speechsdk.ResultReason.RecognizedSpeech:
        print("Recognized:", result.text)
        return result.text

    if result.reason == speechsdk.ResultReason.NoMatch:
        print("No speech was recognized. Try again in a quieter room.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        details = result.cancellation_details
        print("Recognition canceled:", details.reason)
        print("Details:", details.error_details or "No extra details")

    return ""


if __name__ == "__main__":
    listen_once()
