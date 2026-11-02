
from wake_word import wait_for_wake_word

if __name__ == "__main__":
    try:
        wait_for_wake_word()
        print("SUCCESS! Wake word detected.")
    except KeyboardInterrupt:
        print("\nWake-word test stopped.")
    except Exception as error:
        print(f"ERROR: {error}")
