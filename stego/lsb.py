from PIL import Image

from .binary import bytes_to_bits, bits_to_bytes


BITS_PER_CHANNEL = 1
CHANNELS = 3


def calculate_capacity(image: Image.Image) -> int:
    """
    Return raw capacity in bytes.

    Uses 1 LSB from each RGB channel.
    """

    width, height = image.size

    total_bits = width * height * CHANNELS

    return total_bits // 8


def encode_data(
    image: Image.Image,
    data: bytes
) -> Image.Image:

    image = image.convert("RGB")

    capacity = calculate_capacity(image)

    if len(data) > capacity:
        raise ValueError(
            "Data is too large for this image."
        )

    bits = bytes_to_bits(data)

    pixels = image.load()

    bit_index = 0

    width, height = image.size

    for y in range(height):

        for x in range(width):

            r, g, b = pixels[x, y]

            channels = [r, g, b]

            for channel_index in range(3):

                if bit_index >= len(bits):
                    pixels[x, y] = tuple(channels)
                    return image

                channels[channel_index] = (
                    channels[channel_index] & 0b11111110
                ) | bits[bit_index]

                bit_index += 1

            pixels[x, y] = tuple(channels)

    return image


def extract_data(
    image: Image.Image,
    byte_length: int
) -> bytes:

    image = image.convert("RGB")

    required_bits = byte_length * 8

    capacity = calculate_capacity(image)

    if byte_length > capacity:
        raise ValueError(
            "Requested data exceeds image capacity."
        )

    pixels = image.load()

    bits = []

    width, height = image.size

    for y in range(height):

        for x in range(width):

            r, g, b = pixels[x, y]

            for channel in (r, g, b):

                bits.append(channel & 1)

                if len(bits) >= required_bits:
                    return bits_to_bytes(bits)

    return bits_to_bytes(bits)