import os

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


SALT_SIZE = 16
NONCE_SIZE = 12

KEY_SIZE = 32
ITERATIONS = 600_000


def derive_key(password: str, salt: bytes) -> bytes:

    if not password:
        raise ValueError("Password cannot be empty.")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=ITERATIONS,
    )

    return kdf.derive(password.encode("utf-8"))


def encrypt_message(
    message: bytes,
    password: str
) -> tuple[bytes, bytes, bytes]:

    salt = os.urandom(SALT_SIZE)
    nonce = os.urandom(NONCE_SIZE)

    key = derive_key(password, salt)

    aes = AESGCM(key)

    ciphertext = aes.encrypt(
        nonce,
        message,
        None
    )

    return ciphertext, salt, nonce


def decrypt_message(
    ciphertext: bytes,
    password: str,
    salt: bytes,
    nonce: bytes
) -> bytes:

    key = derive_key(password, salt)

    aes = AESGCM(key)

    try:
        return aes.decrypt(
            nonce,
            ciphertext,
            None
        )

    except Exception as exc:
        raise ValueError(
            "Incorrect password or corrupted hidden data."
        ) from exc