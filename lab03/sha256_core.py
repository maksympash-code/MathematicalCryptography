from __future__ import annotations

from pathlib import Path


MASK_32 = 0xFFFFFFFF


H0 = [
    0x6A09E667,
    0xBB67AE85,
    0x3C6EF372,
    0xA54FF53A,
    0x510E527F,
    0x9B05688C,
    0x1F83D9AB,
    0x5BE0CD19,
]

K = [
    0x428A2F98, 0x71374491, 0xB5C0FBCF, 0xE9B5DBA5,
    0x3956C25B, 0x59F111F1, 0x923F82A4, 0xAB1C5ED5,
    0xD807AA98, 0x12835B01, 0x243185BE, 0x550C7DC3,
    0x72BE5D74, 0x80DEB1FE, 0x9BDC06A7, 0xC19BF174,
    0xE49B69C1, 0xEFBE4786, 0x0FC19DC6, 0x240CA1CC,
    0x2DE92C6F, 0x4A7484AA, 0x5CB0A9DC, 0x76F988DA,
    0x983E5152, 0xA831C66D, 0xB00327C8, 0xBF597FC7,
    0xC6E00BF3, 0xD5A79147, 0x06CA6351, 0x14292967,
    0x27B70A85, 0x2E1B2138, 0x4D2C6DFC, 0x53380D13,
    0x650A7354, 0x766A0ABB, 0x81C2C92E, 0x92722C85,
    0xA2BFE8A1, 0xA81A664B, 0xC24B8B70, 0xC76C51A3,
    0xD192E819, 0xD6990624, 0xF40E3585, 0x106AA070,
    0x19A4C116, 0x1E376C08, 0x2748774C, 0x34B0BCB5,
    0x391C0CB3, 0x4ED8AA4A, 0x5B9CCA4F, 0x682E6FF3,
    0x748F82EE, 0x78A5636F, 0x84C87814, 0x8CC70208,
    0x90BEFFFA, 0xA4506CEB, 0xBEF9A3F7, 0xC67178F2,
]


def rotr(x: int, n: int) -> int:
    """Циклічний зсув вправо для 32-бітного слова."""
    return ((x >> n) | (x << (32 - n))) & MASK_32


def shr(x: int, n: int) -> int:
    """Звичайний зсув вправо."""
    return x >> n


def ch(x: int, y: int, z: int) -> int:
    """Choice."""
    return (x & y) ^ ((~x & MASK_32) & z)


def maj(x: int, y: int, z: int) -> int:
    """Majority."""
    return (x & y) ^ (x & z) ^ (y & z)


def big_sigma_0(x: int) -> int:
    return rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22)


def big_sigma_1(x: int) -> int:
    return rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25)


def small_sigma_0(x: int) -> int:
    return rotr(x, 7) ^ rotr(x, 18) ^ shr(x, 3)


def small_sigma_1(x: int) -> int:
    return rotr(x, 17) ^ rotr(x, 19) ^ shr(x, 10)


def sha256_pad(data: bytes) -> bytes:
    """
    Паддинг SHA-256:
    1) додаємо 1 біт (тобто байт 0x80),
    2) додаємо нулі, щоб довжина стала congruent 56 mod 64,
    3) додаємо початкову довжину повідомлення у бітах як 64-бітне число.
    """
    bit_length = len(data) * 8

    padded = data + b"\x80"

    while (len(padded) % 64) != 56:
        padded += b"\x00"

    padded += bit_length.to_bytes(8, byteorder="big")
    return padded


def sha256_bytes(data: bytes) -> bytes:
    """
    Повертає SHA-256 digest як 32 байти.
    """
    h = H0.copy()
    padded = sha256_pad(data)

    for chunk_start in range(0, len(padded), 64):
        chunk = padded[chunk_start:chunk_start + 64]

        w = [0] * 64

        for i in range(16):
            w[i] = int.from_bytes(chunk[4 * i:4 * i + 4], byteorder="big")

        for i in range(16, 64):
            w[i] = (
                small_sigma_1(w[i - 2]) +
                w[i - 7] +
                small_sigma_0(w[i - 15]) +
                w[i - 16]
            ) & MASK_32

        a, b, c, d, e, f, g, hh = h

        for i in range(64):
            t1 = (hh + big_sigma_1(e) + ch(e, f, g) + K[i] + w[i]) & MASK_32
            t2 = (big_sigma_0(a) + maj(a, b, c)) & MASK_32

            hh = g
            g = f
            f = e
            e = (d + t1) & MASK_32
            d = c
            c = b
            b = a
            a = (t1 + t2) & MASK_32

        h[0] = (h[0] + a) & MASK_32
        h[1] = (h[1] + b) & MASK_32
        h[2] = (h[2] + c) & MASK_32
        h[3] = (h[3] + d) & MASK_32
        h[4] = (h[4] + e) & MASK_32
        h[5] = (h[5] + f) & MASK_32
        h[6] = (h[6] + g) & MASK_32
        h[7] = (h[7] + hh) & MASK_32

    return b"".join(x.to_bytes(4, byteorder="big") for x in h)


def sha256_hex(data: bytes) -> str:
    return sha256_bytes(data).hex()


def sha256_text(text: str, encoding: str = "utf-8") -> str:
    return sha256_hex(text.encode(encoding))


def sha256_file(file_path: str | Path) -> str:
    path = Path(file_path)
    data = path.read_bytes()
    return sha256_hex(data)


def self_test() -> None:
    """
    Базові тест-вектори SHA-256.
    """
    tests = [
        (b"", "e3b0c44298fc1c149afbf4c8996fb924"
              "27ae41e4649b934ca495991b7852b855"),
        (b"abc", "ba7816bf8f01cfea414140de5dae2223"
                 "b00361a396177a9cb410ff61f20015ad"),
        (b"hello", "2cf24dba5fb0a30e26e83b2ac5b9e29e"
                   "1b161e5c1fa7425e73043362938b9824"),
    ]

    print("=== SELF TEST SHA-256 ===")
    for message, expected in tests:
        actual = sha256_hex(message)
        print(f"message  = {message!r}")
        print(f"actual   = {actual}")
        print(f"expected = {expected}")
        print(f"OK       = {actual == expected}")
        print()


def demo() -> None:
    text = "Привіт, SHA-256!"
    digest = sha256_text(text)

    print("=== DEMO ===")
    print("Текст:", text)
    print("SHA-256:", digest)


if __name__ == "__main__":
    self_test()
    demo()