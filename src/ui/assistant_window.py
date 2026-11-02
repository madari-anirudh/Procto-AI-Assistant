from PySide6.QtCore import Qt, QTimer, Signal, Slot, QThread, QObject
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QFrame, QPushButton, QSizePolicy
)
import sys


class BackendWorker(QThread):
    wake_detected = Signal()
    listening = Signal()
    user_text = Signal(str)
    assistant_text = Signal(str)
    status = Signal(str)
    failed = Signal(str)
    finished_backend = Signal()

    def __init__(self):
        super().__init__()
        self._keep_running = True

    def stop(self):
        self._keep_running = False

    def run(self):
        # Import inside the worker thread so the UI can start first.
        try:
            from src.speech.wake_word import wait_for_wake_word
            from src.speech.stt import listen_once
            import src.assistant.router as router

            # router imported speak directly in the existing backend.
            # Wrap that reference so every TTS response also appears as a subtitle.
            original_speak = getattr(router, "speak", None)
            if callable(original_speak):
                def speak_with_subtitle(message):
                    self.assistant_text.emit(str(message))
                    return original_speak(message)
                router.speak = speak_with_subtitle

            self.status.emit("Waiting for “Hey Jarvis”…")
            while self._keep_running:
                detected = wait_for_wake_word()
                if not self._keep_running:
                    break
                if not detected:
                    continue

                print("[Procto GUI] Wake word detected; starting speech recognition.", flush=True)
                self.wake_detected.emit()
                self.status.emit("Wake word detected · Listening")
                self.listening.emit()

                recognized = listen_once()
                if not self._keep_running:
                    break

                if not recognized or not str(recognized).strip():
                    self.status.emit("I didn't catch that. Say “Hey Jarvis” again.")
                    continue

                recognized = str(recognized).strip()
                self.user_text.emit(recognized)
                self.status.emit("Processing your command…")

                keep_running = router.handle_command(recognized)
                if keep_running is False:
                    self._keep_running = False
                    self.status.emit("Procto is shutting down…")
                    break

                self.status.emit("Waiting for “Hey Jarvis”…")

        except Exception as exc:
            print(f"[Procto GUI backend error] {type(exc).__name__}: {exc}", flush=True)
            self.failed.emit(f"{type(exc).__name__}: {exc}")
        finally:
            self.finished_backend.emit()


class ProctoWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Procto")
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setMinimumWidth(540)
        self.setMaximumWidth(720)

        self._build_ui()

        # Timers must exist before _set_standby() stops them.
        self.hide_timer = QTimer(self)
        self.hide_timer.setSingleShot(True)
        self.hide_timer.timeout.connect(self._set_standby)

        self.pulse_timer = QTimer(self)
        self.pulse_timer.timeout.connect(self._pulse)
        self._pulse_value = 0

        self._set_standby()
        self.worker = BackendWorker()
        self.worker.wake_detected.connect(self.show_wake_overlay)
        self.worker.listening.connect(self.show_listening)
        self.worker.user_text.connect(self.show_user_subtitle)
        self.worker.assistant_text.connect(self.show_assistant_subtitle)
        self.worker.status.connect(self.show_status)
        self.worker.failed.connect(self.show_error)
        self.worker.finished_backend.connect(self.backend_finished)
        # Do NOT quit the Qt app automatically when the backend thread exits.
        # Keep the UI visible so errors/status can be read and the GUI can be debugged.
        self.worker.start()

        self._position_window()

    def _build_ui(self):
        self.panel = QFrame()
        self.panel.setObjectName("panel")
        self.panel.setStyleSheet("""
            QFrame#panel {
                background-color: rgba(15, 20, 34, 242);
                border: 1px solid rgba(118, 139, 190, 105);
                border-radius: 22px;
            }
            QLabel { color: #F4F6FF; }
            QLabel#brand { color: #9BAEFF; font-size: 12px; font-weight: 700; letter-spacing: 3px; }
            QLabel#headline { font-size: 22px; font-weight: 700; }
            QLabel#status { color: #AAB4D0; font-size: 12px; }
            QLabel#user { color: #D8E0FF; font-size: 14px; }
            QLabel#assistant { color: #9CE6C5; font-size: 14px; }
            QLabel#hint { color: #7F8AA8; font-size: 11px; }
            QPushButton {
                background: rgba(255,255,255,18);
                color: #DCE3FF;
                border: 1px solid rgba(255,255,255,35);
                border-radius: 10px;
                padding: 6px 11px;
            }
            QPushButton:hover { background: rgba(255,255,255,35); }
        """)

        layout = QVBoxLayout(self.panel)
        layout.setContentsMargins(22, 18, 22, 18)
        layout.setSpacing(10)

        top = QHBoxLayout()
        brand = QLabel("P R O C T O")
        brand.setObjectName("brand")
        top.addWidget(brand)
        top.addStretch()
        self.close_button = QPushButton("×")
        self.close_button.setFixedSize(30, 28)
        self.close_button.clicked.connect(self.close)
        top.addWidget(self.close_button)
        layout.addLayout(top)

        self.headline = QLabel("I'm here.")
        self.headline.setObjectName("headline")
        layout.addWidget(self.headline)

        self.status_label = QLabel("Waiting for “Hey Jarvis”…")
        self.status_label.setObjectName("status")
        layout.addWidget(self.status_label)

        self.visualizer = QLabel("◉")
        self.visualizer.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.visualizer.setStyleSheet("color:#8EA5FF; font-size:34px; padding:2px;")
        layout.addWidget(self.visualizer)

        self.user_label = QLabel("")
        self.user_label.setObjectName("user")
        self.user_label.setWordWrap(True)
        self.user_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.user_label)

        self.assistant_label = QLabel("")
        self.assistant_label.setObjectName("assistant")
        self.assistant_label.setWordWrap(True)
        self.assistant_label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.assistant_label)

        self.hint = QLabel("Telugu · English · Tenglish")
        self.hint.setObjectName("hint")
        layout.addWidget(self.hint)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.addWidget(self.panel)

    def _position_window(self):
        screen = QApplication.primaryScreen()
        if screen:
            area = screen.availableGeometry()
            self.adjustSize()
            self.move(
                area.x() + (area.width() - self.width()) // 2,
                area.y() + area.height() - self.height() - 54
            )

    def _set_standby(self):
        self.pulse_timer.stop()
        self.user_label.clear()
        self.assistant_label.clear()
        self.headline.setText("I'm here.")
        self.status_label.setText("Waiting for “Hey Jarvis”…")
        self.visualizer.setText("◉")
        self.hide()

    @Slot()
    def show_wake_overlay(self):
        self.hide_timer.stop()
        self.user_label.clear()
        self.assistant_label.clear()
        self.headline.setText("Yes? How can I help?")
        self.status_label.setText("Wake word detected")
        self.visualizer.setText("◉")
        self._pulse_value = 0
        self.pulse_timer.start(420)
        self.show()
        self.raise_()
        self.activateWindow()
        self._position_window()

    @Slot()
    def show_listening(self):
        self.headline.setText("Listening…")
        self.status_label.setText("Speak your command")
        self.show()

    @Slot(str)
    def show_user_subtitle(self, text):
        self.user_label.setText(f"YOU  ·  {text}")
        self.show()
        self._schedule_hide()

    @Slot(str)
    def show_assistant_subtitle(self, text):
        self.assistant_label.setText(f"PROCTO  ·  {text}")
        self.headline.setText("Here's what I can do")
        self.show()
        self._schedule_hide()

    @Slot(str)
    def show_status(self, text):
        self.status_label.setText(text)
        if "Waiting for" in text:
            self.pulse_timer.stop()
            self._schedule_hide()

    @Slot(str)
    def show_error(self, text):
        self.headline.setText("Something went wrong")
        self.assistant_label.setText(f"PROCTO  ·  {text}")
        self.status_label.setText("Check the terminal for details")
        self.show()
        self._schedule_hide(9000)

    @Slot()
    def backend_finished(self):
        self.pulse_timer.stop()
        self.headline.setText("Backend stopped")
        self.status_label.setText("The listener has stopped. Check the terminal for details.")
        self.show()
        self.raise_()
        self.activateWindow()

    def _schedule_hide(self, milliseconds=6500):
        self.hide_timer.start(milliseconds)

    def _pulse(self):
        self._pulse_value = (self._pulse_value + 1) % 4
        dots = "●" * (1 + self._pulse_value) + "○" * (3 - self._pulse_value)
        self.visualizer.setText(dots)

    def closeEvent(self, event):
        if hasattr(self, "worker") and self.worker.isRunning():
            self.worker.stop()
            # The current wake-word function blocks while listening. Keep the
            # Qt application alive until it returns, rather than destroying a
            # running QThread. The app exits when finished_backend is emitted.
            self.hide()
            event.ignore()
            return
        event.accept()


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Procto")
    window = ProctoWindow()
    app.aboutToQuit.connect(window.close)
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
