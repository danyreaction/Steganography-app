import struct


MAGIC = b"STEG"
VERSION = 1

SALT_SIZE = 16
NONCE_SIZE = 12

# MAGIC + VERSION + SALT + NONCE + CIPHERTEXT_LENGTH
HEADER_FORMAT = f"!4sB{SALT_SIZE}s{NONCE_SIZE}sQ"
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)


def create_header(
    salt: bytes,
    nonce: bytes,
    ciphertext_length: int
) -> bytes:

    if len(salt) != SALT_SIZE:
        raise ValueError("Invalid salt size.")

    if len(nonce) != NONCE_SIZE:
        raise ValueError("Invalid nonce size.")

    return struct.pack(
        HEADER_FORMAT,
        MAGIC,
        VERSION,
        salt,
        nonce,
        ciphertext_length
    )


def parse_header(data: bytes) -> dict:

    if len(data) < HEADER_SIZE:
        raise ValueError("Image does not contain a complete header.")

    magic, version, salt, nonce, ciphertext_length = struct.unpack(
        HEADER_FORMAT,
        data[:HEADER_SIZE]
    )

    if magic != MAGIC:
        raise ValueError("This image does not contain a SteganoTool message.")

    if version != VERSION:
        raise ValueError(f"Unsupported header version: {version}")

    return {
        "version": version,
        "salt": salt,
        "nonce": nonce,
        "ciphertext_length": ciphertext_length
    }