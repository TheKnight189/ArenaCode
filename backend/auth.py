import hashlib
import secrets
import re

def hash_password(password: str, salt: str | None = None) -> tuple[str, str]:
    """
    Hash password with PBKDF2-HMAC-SHA256 and a cryptographic salt.
    Returns (hex_hash, hex_salt).
    """
    if salt is None:
        salt = secrets.token_hex(16)
    salt_bytes = bytes.fromhex(salt)
    key = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt_bytes,
        iterations=100_000
    )
    return key.hex(), salt

def verify_password(password: str, stored_hash: str, salt: str) -> bool:
    """
    Verify if the provided password matches the stored hash given its salt.
    """
    new_hash, _ = hash_password(password, salt=salt)
    return secrets.compare_digest(new_hash, stored_hash)

def generate_avatar(name: str) -> str:
    """
    Extract uppercase 2-letter initials from name, e.g. "Hoàng Anh Tú" -> "AT",
    "Quản trị viên" -> "AD".
    """
    words = [w for w in re.split(r'\s+', name.strip()) if w]
    if not words:
        return "U"
    if len(words) == 1:
        return words[0][:2].upper()
    return (words[0][0] + words[-1][0]).upper()

