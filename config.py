# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ── Email ─────────────────────────────────────
EMAIL_SENDER   = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")
SMTP_SERVER    = "smtp.gmail.com"
SMTP_PORT      = 465

# ── Stream ────────────────────────────────────
STREAM_URL = os.getenv("STREAM_URL", "0")
if STREAM_URL == "0":
    STREAM_URL = 0

# ── Model ─────────────────────────────────────
MODEL_PATH           = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.55
FRAME_SKIP           = 3
INPUT_WIDTH          = 640
INPUT_HEIGHT         = 480

# ── Alerts ────────────────────────────────────
ALERT_COOLDOWN_SECONDS = 30
VOICE_RATE             = 150
VOICE_VOLUME           = 1.0

# ── Storage ───────────────────────────────────
SCREENSHOT_DIR         = "screenshots"
SCREENSHOT_COOLDOWN    = 10       # seconds between screenshots

# ── Dashboard ─────────────────────────────────
DASHBOARD_PORT = 5000

# ── GPS ───────────────────────────────────────
BASE_LOCATION  = [30.7333, 76.7794]

# ── Validation ────────────────────────────────
_missing = [
    k for k, v in {
        "EMAIL_SENDER"  : EMAIL_SENDER,
        "EMAIL_PASSWORD": EMAIL_PASSWORD,
        "EMAIL_RECEIVER": EMAIL_RECEIVER,
    }.items() if not v
]
if _missing:
    print(f"[Config] ⚠️  Missing .env values: {_missing}")
else:
    print(f"[Config] ✅ Credentials loaded for: {EMAIL_SENDER}")
