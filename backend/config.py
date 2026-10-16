import os
import secrets


SECRET_KEY = os.environ.get("FLASK_SECRET_KEY") or secrets.token_hex(32)
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USERNAME = os.environ.get("SMTP_USERNAME", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_FROM = os.environ.get("SMTP_FROM", SMTP_USERNAME)
FRONTEND_BASE_URL = os.environ.get(
	"FRONTEND_BASE_URL",
	"http://127.0.0.1:5500"
).rstrip("/")
