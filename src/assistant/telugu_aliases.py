import re
import unicodedata

def _clean(text: str) -> str:
    text = unicodedata.normalize("NFC", text.lower())
    text = text.replace("\u200c", "").replace("\u200d", "")
    text = re.sub(r"[^\w\s\u0c00-\u0c7f]", " ", text)
    return " ".join(text.split())

ALIASES = {
    # Volume
    "వాల్యూం పెంచు": "volume up", "వాల్యూమ్ పెంచు": "volume up",
    "వాల్యూం అప్": "volume up", "వాల్యూమ్ అప్": "volume up",
    "సౌండ్ పెంచు": "volume up", "శబ్దం పెంచు": "volume up",
    "శబ్దం ఎక్కువ చెయ్యి": "volume up", "సౌండ్ ఎక్కువ చెయ్యి": "volume up",
    "వాల్యూమ్ ఎక్కువ చెయ్యి": "volume up", "వాల్యూం ఎక్కువ చేయి": "volume up",
    "వాల్యూం తగ్గించు": "volume down", "వాల్యూమ్ తగ్గించు": "volume down",
    "వాల్యూం డౌన్": "volume down", "వాల్యూమ్ డౌన్": "volume down",
    "సౌండ్ తగ్గించు": "volume down", "శబ్దం తగ్గించు": "volume down",
    "శబ్దం తక్కువ చెయ్యి": "volume down", "సౌండ్ తక్కువ చెయ్యి": "volume down",
    "వాల్యూమ్ తక్కువ చేయి": "volume down",

    # Mute / unmute
    "వాల్యూం ఆఫ్": "mute volume", "వాల్యూమ్ ఆఫ్": "mute volume",
    "సౌండ్ ఆఫ్": "mute volume", "శబ్దం ఆపు": "mute volume",
    "సౌండ్ ఆపు": "mute volume", "మ్యూట్ చెయ్యి": "mute volume",
    "వాల్యూం మ్యూట్": "mute volume", "వాల్యూమ్ మ్యూట్": "mute volume",
    "మ్యూట్ తీసేయి": "unmute volume", "సౌండ్ ఆన్ చెయ్యి": "unmute volume",
    "వాల్యూం ఆన్": "unmute volume", "వాల్యూమ్ ఆన్": "unmute volume",

    # Brightness
    "బ్రైట్‌నెస్ పెంచు": "brightness up", "బ్రైట్నెస్ పెంచు": "brightness up",
    "బ్రైట్నెస్ ఎక్కువ చెయ్యి": "brightness up",
    "స్క్రీన్ వెలుతురు పెంచు": "brightness up", "స్క్రీన్ లైట్ పెంచు": "brightness up",
    "డిస్‌ప్లే వెలుతురు పెంచు": "brightness up",
    "బ్రైట్‌నెస్ తగ్గించు": "brightness down", "బ్రైట్నెస్ తగ్గించు": "brightness down",
    "బ్రైట్నెస్ తక్కువ చెయ్యి": "brightness down",
    "స్క్రీన్ వెలుతురు తగ్గించు": "brightness down", "స్క్రీన్ లైట్ తగ్గించు": "brightness down",
    "డిస్‌ప్లే వెలుతురు తగ్గించు": "brightness down",

    # Folders: a folder name alone is accepted as an open request.
    "డౌన్‌లోడ్స్": "open downloads", "డౌన్లోడ్స్": "open downloads",
    "డౌన్ లోడ్స్": "open downloads", "డౌన్‌లోడ్": "open downloads",
    "డౌన్లోడ్": "open downloads", "డౌన్ లోడ్": "open downloads",
    "డౌన్‌లోడ్స్ తెరువు": "open downloads",
    "డౌన్లోడ్స్ ఓపెన్ చెయ్యి": "open downloads",
    "డౌన్‌లోడ్ ఫోల్డర్ తెరువు": "open downloads",
    "డౌన్‌లోడ్ ఫోల్డర్ ఓపెన్ చెయ్యి": "open downloads",
    "డాక్యుమెంట్స్": "open documents", "డాక్యుమెంట్స్ తెరువు": "open documents",
    "పిక్చర్స్": "open pictures", "పిక్చర్స్ తెరువు": "open pictures",
    "డెస్క్‌టాప్": "show desktop", "డెస్క్ టాప్": "show desktop",
    "డెస్క్‌టాప్ చూపించు": "show desktop", "డెస్క్‌టాప్ చూపించండి": "show desktop",
    "డెస్క్‌టాప్‌కి వెళ్ళు": "show desktop",
    "అన్ని విండోస్ మినిమైజ్ చెయ్యి": "show desktop",

    # Other approved actions
    "స్క్రీన్‌షాట్": "take screenshot", "స్క్రీన్ షాట్": "take screenshot",
    "స్క్రీన్ షాట్ తీయి": "take screenshot",
    "కంప్యూటర్ లాక్ చెయ్యి": "lock computer", "పీసీ లాక్ చెయ్యి": "lock computer",
    "సిస్టమ్ లాక్ చెయ్యి": "lock computer", "లాక్ కంప్యూటర్": "lock computer",
    "సెట్టింగ్స్": "settings", "సెట్టింగ్": "settings",
    "టాస్క్ మేనేజర్": "task manager", "కమాండ్ ప్రాంప్ట్": "command prompt",
    "బ్లూటూత్": "bluetooth", "వైఫై": "wifi", "వై ఫై": "wifi",
    "మైక్రోఫోన్ ఆఫ్": "microphone mute", "మైక్ ఆఫ్": "microphone mute",
    "మైక్రోఫోన్ మ్యూట్": "microphone mute", "మైక్ మ్యూట్": "microphone mute",
    "మైక్రోఫోన్ ఆన్": "microphone unmute", "మైక్ ఆన్": "microphone unmute",
    "మైక్రోఫోన్ అన్‌మ్యూట్": "microphone unmute",
}

# Conservative, explicit common speech-to-text spelling mistakes.
TYPO_ALIASES = {
    "వాలుం పెంచు": "volume up",
    "వాలుం తగ్గించు": "volume down",
    "వాల్యూం తగించు": "volume down",
    "బ్రైట్నెస్ తగించు": "brightness down",
    "డౌన్లోడ్స్": "open downloads",
    "డెస్క్ టాప్ చూపించు": "show desktop",
}

_NORMALIZED = {_clean(k): v for k, v in ALIASES.items()}
_NORMALIZED.update({_clean(k): v for k, v in TYPO_ALIASES.items()})

def normalize_telugu_aliases(command: str) -> str:
    """Translate known Telugu phrases; never fuzzy-match sensitive actions."""
    cleaned = _clean(command)
    if cleaned in _NORMALIZED:
        return _NORMALIZED[cleaned]

    for phrase in sorted(_NORMALIZED, key=len, reverse=True):
        cleaned = re.sub(
            rf"(?<!\w){re.escape(phrase)}(?!\w)",
            _NORMALIZED[phrase],
            cleaned,
        )
    return " ".join(cleaned.split())
