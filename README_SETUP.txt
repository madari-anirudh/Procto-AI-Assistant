PROCTO PYSIDE6 WINDOWS FRONTEND
================================

This adds a native PySide6 floating overlay to your existing Python backend.

WHAT IT DOES
------------
- Waits for your existing "Hey Jarvis" wake-word detector.
- Shows a floating overlay when the wake word is detected.
- Shows a listening state while Azure Speech recognition is active.
- Shows the recognized user command as a subtitle.
- Shows Procto's spoken reply as a subtitle by wrapping the existing
  router.speak reference. Your existing TTS engine remains in use.
- Keeps your existing wake_word.py, stt.py, router.py and tts.py backend.

INSTALL
-------
Open PowerShell in C:\Users\aniru\procto and run:

    .\.venv\Scripts\python.exe -m pip install PySide6

Extract the ZIP into the project root, preserving the folders.
It adds:
    src\ui\__init__.py
    src\ui\assistant_window.py
    run_procto_gui.py

RUN
---
    cd C:\Users\aniru\procto
    .\.venv\Scripts\python.exe run_procto_gui.py

Keep SPEECH_KEY and SPEECH_REGION configured in the same PowerShell
session before launching, as in your existing backend setup.

IMPORTANT INTEGRATION NOTES
---------------------------
1. The GUI imports these existing backend interfaces:
       src.speech.wake_word.wait_for_wake_word()
       src.speech.stt.listen_once()
       src.assistant.router.handle_command(text)

2. It assumes router.py imports its TTS function as a module-level name
   called `speak` (for example: `from src.speech.tts import speak`).
   The GUI wraps that router.speak reference so subtitles appear before
   the existing speech output plays. If your router uses another name
   or calls TTS through a different object, the assistant subtitle hook
   will need to be adjusted.

3. Closing the overlay requests the worker to stop. The current
   wait_for_wake_word() backend call is blocking, so the audio listener
   may take a moment to return. Do not force-kill the worker thread.

4. This is a first working UI layer. It does not replace or change your
   existing backend command logic, Azure credentials, or wake-word model.