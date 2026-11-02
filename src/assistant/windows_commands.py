import ctypes
import os
import re
import subprocess
from pathlib import Path

# Fixed allowlist; spoken text is never passed to a shell.
APP_COMMANDS = {
    "notepad": ["notepad.exe"], "calculator": ["calc.exe"],
    "paint": ["mspaint.exe"], "file explorer": ["explorer.exe"],
    "task manager": ["taskmgr.exe"], "command prompt": ["cmd.exe"],
    "powershell": ["powershell.exe"], "vscode": ["code"],
    "word": ["winword"], "excel": ["excel"],
}

def _run(args):
    subprocess.Popen(args, shell=False)

def _audio():
    try:
        from pycaw.pycaw import AudioUtilities
    except ImportError as exc:
        raise RuntimeError("Install audio controls with: .\\.venv\\Scripts\\python.exe -m pip install pycaw comtypes") from exc
    return AudioUtilities

def _speaker_endpoint():
    return _audio().GetSpeakers().EndpointVolume

def _set_volume(value):
    value = int(value)
    if not 0 <= value <= 100:
        raise ValueError("Volume must be between 0 and 100 percent.")
    _speaker_endpoint().SetMasterVolumeLevelScalar(value / 100, None)

def _change_volume(delta):
    endpoint = _speaker_endpoint()
    current = round(endpoint.GetMasterVolumeLevelScalar() * 100)
    _set_volume(max(0, min(100, current + int(delta))))

def _mic_endpoint():
    AudioUtilities = _audio()
    for device in AudioUtilities.GetAllDevices():
        try:
            if getattr(device, "DataFlow", None) == 1 and getattr(device, "EndpointVolume", None):
                return device.EndpointVolume
        except Exception:
            pass
    raise RuntimeError("No controllable microphone found. Check Windows Settings > System > Sound > Input.")

def _brightness():
    try:
        import screen_brightness_control as sbc
    except ImportError as exc:
        raise RuntimeError("Install brightness control with: .\\.venv\\Scripts\\python.exe -m pip install screen-brightness-control") from exc
    return sbc

def _set_brightness(value):
    value = int(value)
    if not 0 <= value <= 100:
        raise ValueError("Brightness must be between 0 and 100 percent.")
    _brightness().set_brightness(value)

def _change_brightness(delta):
    sbc = _brightness()
    current = sbc.get_brightness()
    if isinstance(current, list):
        current = current[0]
    _set_brightness(max(0, min(100, int(current) + int(delta))))

def _key_combo(keys):
    user32 = ctypes.windll.user32
    for key in keys:
        user32.keybd_event(key, 0, 0, 0)
    for key in reversed(keys):
        user32.keybd_event(key, 0, 2, 0)

def _normalize_spoken_command(command: str) -> str:
    """Normalize a few Telugu words that may remain after router alias matching."""
    command = command.lower().replace("\u200c", "").replace("\u200d", "")
    words = {
        "సెట్": "set",
        "వాల్యూం": "volume",
        "వాల్యూమ్": "volume",
        "డౌన్": "down",
        "అప్": "up",
        "పెంచు": "up",
        "తగ్గించు": "down",
        "బై": "by",
        "కి": "to",
        "పర్సెంట్": "percent",
        "శాతం": "percent",
    }
    for telugu, english in sorted(words.items(), key=lambda item: len(item[0]), reverse=True):
        command = re.sub(rf"(?<!\w){re.escape(telugu)}(?!\w)", english, command)
    command = re.sub(r"[^\w\s]", " ", command)
    return " ".join(command.split())

def _handle_percentage_command(command: str) -> bool:
    # Examples:
    # "set volume 90", "set volume to 90 percent", "volume 90"
    match = re.fullmatch(
        r"(?:set )?volume(?: level)?(?: to)? (\d{1,3})(?: percent)?",
        command,
    )
    if match:
        value = int(match.group(1))
        _set_volume(value)
        print(f"Volume set to {value}%.")
        return True

    # "volume down by 10" means subtract 10 percentage points.
    match = re.fullmatch(
        r"volume (up|down) by (\d{1,3})(?: percent)?",
        command,
    )
    if match:
        amount = int(match.group(2))
        delta = amount if match.group(1) == "up" else -amount
        _change_volume(delta)
        print(f"Volume changed {'up' if delta > 0 else 'down'} by {amount} percentage points.")
        return True

    # Short forms such as "volume up 20" / "volume down 10".
    match = re.fullmatch(r"volume (up|down) (\d{1,3})(?: percent)?", command)
    if match:
        amount = int(match.group(2))
        delta = amount if match.group(1) == "up" else -amount
        _change_volume(delta)
        print(f"Volume changed {'up' if delta > 0 else 'down'} by {amount} percentage points.")
        return True

    return False

def handle_windows_command(command: str) -> bool:
    command = _normalize_spoken_command(command)

    # Handle exact volume percentages and relative percentage changes first.
    if _handle_percentage_command(command):
        return True

    m = re.fullmatch(r"(?:set )?brightness(?: to)? (\d{1,3})(?: percent)?", command)
    if m:
        _set_brightness(int(m.group(1))); return True

    if command in {"volume up", "increase volume"}:
        _change_volume(5); return True
    if command in {"volume down", "decrease volume"}:
        _change_volume(-5); return True
    if command in {"mute volume", "toggle mute", "mute sound", "volume off"}:
        ep = _speaker_endpoint(); ep.SetMute(not bool(ep.GetMute()), None); return True
    if command in {"unmute volume", "sound on", "volume on"}:
        _speaker_endpoint().SetMute(False, None); return True

    if command in {"microphone mute", "mute microphone", "mic mute", "microphone off"}:
        _mic_endpoint().SetMute(True, None); return True
    if command in {"microphone unmute", "unmute microphone", "mic unmute", "microphone on"}:
        _mic_endpoint().SetMute(False, None); return True

    if command in {"brightness up", "increase brightness"}:
        _change_brightness(10); return True
    if command in {"brightness down", "decrease brightness"}:
        _change_brightness(-10); return True

    if command in {"show desktop", "minimize all windows"}:
        _key_combo([0x5B, 0x44]); return True
    if command in {"take screenshot", "capture screenshot"}:
        _key_combo([0x5B, 0x2C]); return True
    if command in {"lock computer", "lock computer now", "lock pc"}:
        if not ctypes.windll.user32.LockWorkStation():
            raise OSError("Windows could not lock the workstation.")
        return True

    if re.fullmatch(r"(?:open|launch|start) settings", command):
        os.startfile("ms-settings:"); return True
    if re.fullmatch(r"(?:open|launch|start) (?:wifi|wi-fi|network settings)", command):
        os.startfile("ms-settings:network"); return True
    if re.fullmatch(r"(?:open|launch|start) (?:bluetooth|bluetooth settings)", command):
        os.startfile("ms-settings:bluetooth"); return True

    folders = {name: Path.home() / name.title() for name in ("downloads", "documents", "pictures")}
    m = re.fullmatch(r"(?:open|launch|start) (downloads|documents|pictures)(?: folder)?", command)
    if m:
        folder = folders[m.group(1)]
        if not folder.is_dir():
            raise FileNotFoundError(f"Folder not found: {folder}")
        _run(["explorer.exe", str(folder)]); return True

    m = re.fullmatch(r"(?:open|launch|start) (notepad|calculator|paint|file explorer|task manager|command prompt|powershell|vscode|word|excel)", command)
    if m:
        app = m.group(1)
        _run(APP_COMMANDS[app]); return True
    return False
