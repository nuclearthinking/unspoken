import hashlib


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()
