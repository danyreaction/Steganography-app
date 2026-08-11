def bytes_to_bits(data: bytes) -> list[int]:
    """Convert bytes into a list of bits."""

    bits = []

    for byte in data:
        for i in range(7, -1, -1):
            bits.append((byte >> i) & 1)

    return bits


def bits_to_bytes(bits: list[int]) -> bytes:
    """Convert a list of bits back into bytes."""

    if len(bits) % 8 != 0:
        raise ValueError("Bit count must be divisible by 8.")

    result = bytearray()

    for i in range(0, len(bits), 8):
        byte = 0

        for bit in bits[i:i + 8]:
            byte = (byte << 1) | bit

        result.append(byte)

    return bytes(result)