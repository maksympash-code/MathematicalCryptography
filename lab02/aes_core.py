from __future__ import annotations

from typing import List


S_BOX = [
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
]

INV_S_BOX = [
    0x52, 0x09, 0x6A, 0xD5, 0x30, 0x36, 0xA5, 0x38, 0xBF, 0x40, 0xA3, 0x9E, 0x81, 0xF3, 0xD7, 0xFB,
    0x7C, 0xE3, 0x39, 0x82, 0x9B, 0x2F, 0xFF, 0x87, 0x34, 0x8E, 0x43, 0x44, 0xC4, 0xDE, 0xE9, 0xCB,
    0x54, 0x7B, 0x94, 0x32, 0xA6, 0xC2, 0x23, 0x3D, 0xEE, 0x4C, 0x95, 0x0B, 0x42, 0xFA, 0xC3, 0x4E,
    0x08, 0x2E, 0xA1, 0x66, 0x28, 0xD9, 0x24, 0xB2, 0x76, 0x5B, 0xA2, 0x49, 0x6D, 0x8B, 0xD1, 0x25,
    0x72, 0xF8, 0xF6, 0x64, 0x86, 0x68, 0x98, 0x16, 0xD4, 0xA4, 0x5C, 0xCC, 0x5D, 0x65, 0xB6, 0x92,
    0x6C, 0x70, 0x48, 0x50, 0xFD, 0xED, 0xB9, 0xDA, 0x5E, 0x15, 0x46, 0x57, 0xA7, 0x8D, 0x9D, 0x84,
    0x90, 0xD8, 0xAB, 0x00, 0x8C, 0xBC, 0xD3, 0x0A, 0xF7, 0xE4, 0x58, 0x05, 0xB8, 0xB3, 0x45, 0x06,
    0xD0, 0x2C, 0x1E, 0x8F, 0xCA, 0x3F, 0x0F, 0x02, 0xC1, 0xAF, 0xBD, 0x03, 0x01, 0x13, 0x8A, 0x6B,
    0x3A, 0x91, 0x11, 0x41, 0x4F, 0x67, 0xDC, 0xEA, 0x97, 0xF2, 0xCF, 0xCE, 0xF0, 0xB4, 0xE6, 0x73,
    0x96, 0xAC, 0x74, 0x22, 0xE7, 0xAD, 0x35, 0x85, 0xE2, 0xF9, 0x37, 0xE8, 0x1C, 0x75, 0xDF, 0x6E,
    0x47, 0xF1, 0x1A, 0x71, 0x1D, 0x29, 0xC5, 0x89, 0x6F, 0xB7, 0x62, 0x0E, 0xAA, 0x18, 0xBE, 0x1B,
    0xFC, 0x56, 0x3E, 0x4B, 0xC6, 0xD2, 0x79, 0x20, 0x9A, 0xDB, 0xC0, 0xFE, 0x78, 0xCD, 0x5A, 0xF4,
    0x1F, 0xDD, 0xA8, 0x33, 0x88, 0x07, 0xC7, 0x31, 0xB1, 0x12, 0x10, 0x59, 0x27, 0x80, 0xEC, 0x5F,
    0x60, 0x51, 0x7F, 0xA9, 0x19, 0xB5, 0x4A, 0x0D, 0x2D, 0xE5, 0x7A, 0x9F, 0x93, 0xC9, 0x9C, 0xEF,
    0xA0, 0xE0, 0x3B, 0x4D, 0xAE, 0x2A, 0xF5, 0xB0, 0xC8, 0xEB, 0xBB, 0x3C, 0x83, 0x53, 0x99, 0x61,
    0x17, 0x2B, 0x04, 0x7E, 0xBA, 0x77, 0xD6, 0x26, 0xE1, 0x69, 0x14, 0x63, 0x55, 0x21, 0x0C, 0x7D,
]

RCON = [
    0x00,  # не використовується, просто для зручної індексації
    0x01, 0x02, 0x04, 0x08, 0x10,
    0x20, 0x40, 0x80, 0x1B, 0x36,
    0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
]


def gf_mul(a: int, b: int) -> int:
    """Множення в GF(2^8) з модулем x^8 + x^4 + x^3 + x + 1."""
    result = 0
    for _ in range(8):
        if b & 1:
            result ^= a
        hi_bit = a & 0x80
        a = (a << 1) & 0xFF
        if hi_bit:
            a ^= 0x1B
        b >>= 1
    return result


def xor_words(a: List[int], b: List[int]) -> List[int]:
    return [x ^ y for x, y in zip(a, b)]


def rot_word(word: List[int]) -> List[int]:
    return word[1:] + word[:1]


def sub_word(word: List[int]) -> List[int]:
    return [S_BOX[x] for x in word]


def add_round_key(state: List[int], round_key: List[int]) -> List[int]:
    return [s ^ k for s, k in zip(state, round_key)]


def sub_bytes(state: List[int]) -> List[int]:
    return [S_BOX[x] for x in state]


def inv_sub_bytes(state: List[int]) -> List[int]:
    return [INV_S_BOX[x] for x in state]


def shift_rows(state: List[int]) -> List[int]:
    """
    State зберігається у column-major:
    state[r + 4*c] = елемент (r, c)
    """
    out = state.copy()
    for r in range(4):
        row = [state[r + 4 * c] for c in range(4)]
        row = row[r:] + row[:r]
        for c in range(4):
            out[r + 4 * c] = row[c]
    return out


def inv_shift_rows(state: List[int]) -> List[int]:
    out = state.copy()
    for r in range(4):
        row = [state[r + 4 * c] for c in range(4)]
        row = row[-r:] + row[:-r] if r != 0 else row
        for c in range(4):
            out[r + 4 * c] = row[c]
    return out


def mix_single_column(col: List[int]) -> List[int]:
    a0, a1, a2, a3 = col
    return [
        gf_mul(0x02, a0) ^ gf_mul(0x03, a1) ^ a2 ^ a3,
        a0 ^ gf_mul(0x02, a1) ^ gf_mul(0x03, a2) ^ a3,
        a0 ^ a1 ^ gf_mul(0x02, a2) ^ gf_mul(0x03, a3),
        gf_mul(0x03, a0) ^ a1 ^ a2 ^ gf_mul(0x02, a3),
    ]


def inv_mix_single_column(col: List[int]) -> List[int]:
    a0, a1, a2, a3 = col
    return [
        gf_mul(0x0E, a0) ^ gf_mul(0x0B, a1) ^ gf_mul(0x0D, a2) ^ gf_mul(0x09, a3),
        gf_mul(0x09, a0) ^ gf_mul(0x0E, a1) ^ gf_mul(0x0B, a2) ^ gf_mul(0x0D, a3),
        gf_mul(0x0D, a0) ^ gf_mul(0x09, a1) ^ gf_mul(0x0E, a2) ^ gf_mul(0x0B, a3),
        gf_mul(0x0B, a0) ^ gf_mul(0x0D, a1) ^ gf_mul(0x09, a2) ^ gf_mul(0x0E, a3),
    ]


def mix_columns(state: List[int]) -> List[int]:
    out = state.copy()
    for c in range(4):
        col = state[4 * c: 4 * c + 4]
        mixed = mix_single_column(col)
        out[4 * c: 4 * c + 4] = mixed
    return out


def inv_mix_columns(state: List[int]) -> List[int]:
    out = state.copy()
    for c in range(4):
        col = state[4 * c: 4 * c + 4]
        mixed = inv_mix_single_column(col)
        out[4 * c: 4 * c + 4] = mixed
    return out


def pkcs7_pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len]) * pad_len


def pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes:
    if not data or len(data) % block_size != 0:
        raise ValueError("Некоректна довжина даних для PKCS#7 unpad.")
    pad_len = data[-1]
    if pad_len < 1 or pad_len > block_size:
        raise ValueError("Некоректний padding.")
    if data[-pad_len:] != bytes([pad_len]) * pad_len:
        raise ValueError("Некоректний padding.")
    return data[:-pad_len]


def rcon_value(i: int) -> int:
    """
    Обчислює Rcon[i] для AES key schedule.
    Rcon[1] = 0x01, далі кожного разу множимо на 0x02 в GF(2^8).
    """
    if i < 1:
        raise ValueError("Rcon index має бути >= 1.")

    value = 0x01
    for _ in range(1, i):
       value = gf_mul(value, 0x02)
    return value



class AES:
    """
    Підтримує AES-128 / AES-192 / AES-256
    залежно від довжини ключа: 16 / 24 / 32 байти.
    """

    NB = 4  # кількість слів state = 4

    def __init__(self, key: bytes, rounds_override: int | None = None):
        if len(key) not in (16, 24, 32):
            raise ValueError("Ключ AES має мати довжину 16, 24 або 32 байти.")

        self.key = key
        self.nk = len(key) // 4
        default_nr = {4: 10, 6: 12, 8: 14}[self.nk]

        self.nr = rounds_override if rounds_override is not None else default_nr

        if self.nr < 1:
            raise ValueError("Кількість раундів має бути не меншою за 1.")

        self.round_keys = self._expand_key(key)


    def _expand_key(self, key: bytes) -> List[List[int]]:
        key_bytes = list(key)
        words: List[List[int]] = [
            key_bytes[4 * i: 4 * i + 4] for i in range(self.nk)
        ]

        total_words = self.NB * (self.nr + 1)

        for i in range(self.nk, total_words):
            temp = words[i - 1].copy()

            if i % self.nk == 0:
                temp = xor_words(sub_word(rot_word(temp)), [rcon_value(i // self.nk), 0, 0, 0])
            elif self.nk > 6 and i % self.nk == 4:
                temp = sub_word(temp)

            words.append(xor_words(words[i - self.nk], temp))

        round_keys: List[List[int]] = []
        for r in range(self.nr + 1):
            rk: List[int] = []
            for w in words[4 * r: 4 * r + 4]:
                rk.extend(w)
            round_keys.append(rk)

        return round_keys

    def encrypt_block(self, plaintext_block: bytes) -> bytes:
        if len(plaintext_block) != 16:
            raise ValueError("AES шифрує блоки рівно по 16 байт.")

        state = list(plaintext_block)

        state = add_round_key(state, self.round_keys[0])

        for rnd in range(1, self.nr):
            state = sub_bytes(state)
            state = shift_rows(state)
            state = mix_columns(state)
            state = add_round_key(state, self.round_keys[rnd])

        state = sub_bytes(state)
        state = shift_rows(state)
        state = add_round_key(state, self.round_keys[self.nr])

        return bytes(state)

    def decrypt_block(self, ciphertext_block: bytes) -> bytes:
        if len(ciphertext_block) != 16:
            raise ValueError("AES дешифрує блоки рівно по 16 байт.")

        state = list(ciphertext_block)

        state = add_round_key(state, self.round_keys[self.nr])

        for rnd in range(self.nr - 1, 0, -1):
            state = inv_shift_rows(state)
            state = inv_sub_bytes(state)
            state = add_round_key(state, self.round_keys[rnd])
            state = inv_mix_columns(state)

        state = inv_shift_rows(state)
        state = inv_sub_bytes(state)
        state = add_round_key(state, self.round_keys[0])

        return bytes(state)

    def encrypt_ecb(self, plaintext: bytes, use_padding: bool = True) -> bytes:
        if use_padding:
            plaintext = pkcs7_pad(plaintext, 16)
        elif len(plaintext) % 16 != 0:
            raise ValueError("Без padding довжина plaintext має ділитися на 16.")

        blocks = []
        for i in range(0, len(plaintext), 16):
            blocks.append(self.encrypt_block(plaintext[i:i + 16]))
        return b"".join(blocks)

    def decrypt_ecb(self, ciphertext: bytes, use_padding: bool = True) -> bytes:
        if len(ciphertext) % 16 != 0:
            raise ValueError("Довжина ciphertext має ділитися на 16.")

        blocks = []
        for i in range(0, len(ciphertext), 16):
            blocks.append(self.decrypt_block(ciphertext[i:i + 16]))
        data = b"".join(blocks)

        if use_padding:
            data = pkcs7_unpad(data, 16)
        return data


def self_test() -> None:
    """
    Відомі тест-вектори для AES.
    Якщо все правильно — отримаєш 'OK' для всіх трьох варіантів.
    """
    pt = bytes.fromhex("00112233445566778899aabbccddeeff")

    tests = [
        (
            "AES-128",
            bytes.fromhex("000102030405060708090a0b0c0d0e0f"),
            bytes.fromhex("69c4e0d86a7b0430d8cdb78070b4c55a"),
        ),
        (
            "AES-192",
            bytes.fromhex("000102030405060708090a0b0c0d0e0f1011121314151617"),
            bytes.fromhex("dda97ca4864cdfe06eaf70a0ec0d7191"),
        ),
        (
            "AES-256",
            bytes.fromhex("000102030405060708090a0b0c0d0e0f101112131415161718191a1b1c1d1e1f"),
            bytes.fromhex("8ea2b7ca516745bfeafc49904b496089"),
        ),
    ]

    for name, key, expected_ct in tests:
        aes = AES(key)
        ct = aes.encrypt_block(pt)
        dec = aes.decrypt_block(ct)

        print(f"{name}:")
        print("  ciphertext =", ct.hex())
        print("  expected   =", expected_ct.hex())
        print("  encrypt OK =", ct == expected_ct)
        print("  decrypt OK =", dec == pt)
        print()



def demo_text_mode() -> None:
    """
    Демонстрація шифрування/дешифрування довільного тексту в ECB.
    Для лабораторної зручно, але для реальних систем ECB — погана ідея.
    """
    message = "Привіт, це тест AES!".encode("utf-8")
    key_128 = b"1234567890abcdef"  # 16 байт

    aes = AES(key_128)
    ciphertext = aes.encrypt_ecb(message, use_padding=True)
    decrypted = aes.decrypt_ecb(ciphertext, use_padding=True)

    print("Повідомлення:", message)
    print("Ciphertext (hex):", ciphertext.hex())
    print("Розшифрування:", decrypted)
    print("OK:", decrypted == message)


if __name__ == "__main__":
    self_test()
    demo_text_mode()