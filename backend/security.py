"""Password hashing (HMAC + Salt), password policy check and reset code (SHA-1)."""
import hashlib
import hmac
import os
import string

import config


def new_salt():
    """Random salt, different for every user."""
    return os.urandom(16).hex()


def hash_password(password, salt):
    """HMAC-SHA256: the salt is the key, the password is the message."""
    return hmac.new(bytes.fromhex(salt), password.encode("utf-8"), hashlib.sha256).hexdigest()


def check_password(password, salt, stored_hash):
    return hash_password(password, salt) == stored_hash


def load_dictionary():
    try:
        with open(config.DICTIONARY_FILE, encoding="utf-8") as f:
            return [line.strip().lower() for line in f if line.strip()]
    except FileNotFoundError:
        return []


def check_policy(password):
    """Returns a list of errors. An empty list means the password is OK."""
    errors = []
    if len(password) < config.PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {config.PASSWORD_MIN_LENGTH} characters long.")
    if config.PASSWORD_REQUIRE_UPPER and not any(c.isupper() for c in password):
        errors.append("Password must include at least one uppercase letter (A-Z).")
    if config.PASSWORD_REQUIRE_LOWER and not any(c.islower() for c in password):
        errors.append("Password must include at least one lowercase letter (a-z).")
    if config.PASSWORD_REQUIRE_DIGIT and not any(c.isdigit() for c in password):
        errors.append("Password must include at least one digit (0-9).")
    if config.PASSWORD_REQUIRE_SPECIAL and not any(c in string.punctuation for c in password):
        errors.append("Password must include at least one special character (e.g. ! @ # $).")
    if password.lower() in load_dictionary():
        errors.append("This password is too common. Please choose a stronger password.")
    return errors


def generate_reset_code():
    """Random value hashed with SHA-1 (as the assignment requires)."""
    return hashlib.sha1(os.urandom(32)).hexdigest()
