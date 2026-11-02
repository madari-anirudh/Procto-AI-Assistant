
import time

from src.speech.wake_word import wait_for_wake_word
from src.speech.stt import listen_once
from src.assistant.router import handle_command


def main() -> None:
    print("=" * 45)
    print("       PROCTO VOICE ASSISTANT")
    print("=" * 45)
    print("Language: Telugu + English/Tenglish")
    print("Mode: Wake-word activation")
    print("Wake word: Hey Jarvis")
    print("Say 'stop procto' after activation to exit.")
    print("Press Ctrl+C to stop at any time.")
    print("=" * 45)

    print("Starting Procto...")

    running = True

    try:
        while running:
            try:
                # Wait until the wake word is detected.
                wait_for_wake_word()

                print("Wake word detected. Listening for your command...")

                # Recognize one command using the existing Azure STT.
                recognized_text = listen_once()

                if not recognized_text.strip():
                    print("No command recognized. Returning to standby.")
                    time.sleep(0.3)
                    continue

                # Preserve the existing command router.
                running = handle_command(recognized_text)

                # Pause before waiting for the next wake word.
                time.sleep(0.3)

            except KeyboardInterrupt:
                raise

            except Exception as error:
                print(f"\nA voice operation failed: {error}")
                print("Retrying in 2 seconds...")
                time.sleep(2)

    except KeyboardInterrupt:
        print("\nStopping Procto...")

    finally:
        print("Procto has stopped.")


if __name__ == "__main__":
    main()
