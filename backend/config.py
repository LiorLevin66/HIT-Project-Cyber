"""
Configuration file - the system administrator can change these values.
"""
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------- Password policy ----------
PASSWORD_MIN_LENGTH = 10            # 1. password length
PASSWORD_REQUIRE_UPPER = True       # 2. complex password: uppercase letters
PASSWORD_REQUIRE_LOWER = True       #    lowercase letters
PASSWORD_REQUIRE_DIGIT = True       #    digits
PASSWORD_REQUIRE_SPECIAL = True     #    special characters
PASSWORD_HISTORY = 3                # 3. can't reuse the last 3 passwords
DICTIONARY_FILE = os.path.join(BASE_DIR, "forbidden_passwords.txt")  # 4. dictionary
MAX_LOGIN_ATTEMPTS = 3              # 5. login attempts
LOCKOUT_MINUTES = 15                # how long the user is blocked after that

# ---------- Database ----------
# "sqlite" runs without installing anything. Set DB_BACKEND=mysql for MySQL.
DB_BACKEND = os.environ.get("DB_BACKEND", "sqlite")
SQLITE_PATH = os.path.join(BASE_DIR, "comunication.db")
MYSQL = {
    "host": os.environ.get("MYSQL_HOST", "localhost"),
    "user": os.environ.get("MYSQL_USER", "root"),
    "password": os.environ.get("MYSQL_PASSWORD", ""),
    "database": os.environ.get("MYSQL_DATABASE", "comunication_ltd"),
}

# ---------- Mail ----------
# Without SMTP_HOST the mail is written to outbox.log instead of being sent.
SMTP_HOST = os.environ.get("SMTP_HOST", "")
SMTP_PORT = int(os.environ.get("SMTP_PORT", "587"))
SMTP_USER = os.environ.get("SMTP_USER", "")
SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD", "")
SMTP_SENDER = os.environ.get("SMTP_SENDER", "no-reply@comunication-ltd.com")
OUTBOX_PATH = os.path.join(BASE_DIR, "outbox.log")

# Key Flask uses to sign the session cookie
SECRET_KEY = os.environ.get("SECRET_KEY", "change-this-secret-key")
