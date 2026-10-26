from hashlib import sha256
from secrets import token_urlsafe

from pwdlib import PasswordHash


password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


def create_session_token() -> tuple[str, str]:
    token = token_urlsafe(32)
    token_hash = sha256(token.encode("utf-8")).hexdigest()
    return token, token_hash