"""Constants for the Hatch Rest integration."""
from datetime import timedelta

DOMAIN = "hatch_rest"

# Config entry data keys
CONF_ADDRESS = "address"

# Device info
MANUFACTURER = "Hatch Baby"
MODEL = "Rest (1st Gen)"

# Update interval (fallback if notifications fail)
DEFAULT_SCAN_INTERVAL = timedelta(seconds=30)

# Sound mapping (PyHatchBabyRestSound enum to friendly names)
SOUND_MAP = {
    0: "None",
    2: "Stream",
    3: "White Noise",
    4: "Dryer",
    5: "Ocean",
    6: "Wind",
    7: "Rain",
    9: "Bird",
    10: "Crickets",
    11: "Brahms Lullaby",
    13: "Twinkle Twinkle",
    14: "Rockabye",
}

# Reverse mapping for media player (future use)
SOUND_NAMES = {v: k for k, v in SOUND_MAP.items()}

# Platforms
PLATFORMS = ["light"]
