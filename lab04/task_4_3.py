from __future__ import annotations

from pathlib import Path
import secrets

from task_4_2 import (
    RSAKeyPair,
    generate_rsa_keypair,
    rsa_encrypt_int,
    rsa_decrypt_int_crt,
)


try:
    from sha256_core import sha256_bytes
except ImportError:
    import hashlib

    def sha256_bytes(data: bytes) -> bytes:
        return hashlib.sha256(data).digest()


SECRET_PRIME_BITS = 512
REPORT_FILE = Path("task_4_3_report.txt")

HASH_LEN = 32  # SHA-256 digest length = 32 bytes


def xor_bytes(a: bytes, b: bytes) -> bytes:
    """
    XOR двох байтових рядків однакової довжини.
    """
    if len(a) != len(b):
        raise ValueError("Для XOR довжини мають збігатися.")

    return bytes(x ^ y for x, y in zip(a, b))


def mgf1(seed: bytes, mask_len: int) -> bytes:
    """
    MGF1 — mask generation function на основі SHA-256.

    Генерує mask_len байтів псевдовипадкової маски:
        SHA256(seed || counter)
    """
    if mask_len < 0:
        raise ValueError("Довжина маски не може бути від'ємною.")

    result = b""
    counter = 0

    while len(result) < mask_len:
        counter_bytes = counter.to_bytes(4, byteorder="big")
        result += sha256_bytes(seed + counter_bytes)
        counter += 1

    return result[:mask_len]


def modulus_byte_length(n: int) -> int:
    """
    Розмір RSA-модуля n у байтах.
    """
    return (n.bit_length() + 7) // 8


def max_oaep_message_length(n: int) -> int:
    """
    Максимальна довжина одного OAEP-блока повідомлення.

    Для RSA-OAEP:
        mLen <= k - 2*hLen - 2

    де:
        k    — довжина RSA-модуля в байтах,
        hLen — довжина хешу в байтах.
    """
    k = modulus_byte_length(n)
    max_len = k - 2 * HASH_LEN - 2

    if max_len <= 0:
        raise ValueError(
            "RSA-модуль занадто малий для OAEP із SHA-256. "
            "Для SHA-256 потрібен модуль більший за 66 байтів."
        )

    return max_len


def oaep_encode(message: bytes, k: int, label: bytes = b"") -> bytes:
    """
    OAEP encoding.

    Формат:
        EM = 0x00 || maskedSeed || maskedDB

    де:
        DB = lHash || PS || 0x01 || M
    """
    message_len = len(message)
    max_len = k - 2 * HASH_LEN - 2

    if message_len > max_len:
        raise ValueError(
            f"Повідомлення занадто довге для одного OAEP-блока. "
            f"Максимум: {max_len} байт, отримано: {message_len} байт."
        )

    l_hash = sha256_bytes(label)

    ps_len = k - message_len - 2 * HASH_LEN - 2
    ps = b"\x00" * ps_len

    db = l_hash + ps + b"\x01" + message

    seed = secrets.token_bytes(HASH_LEN)

    db_mask = mgf1(seed, k - HASH_LEN - 1)
    masked_db = xor_bytes(db, db_mask)

    seed_mask = mgf1(masked_db, HASH_LEN)
    masked_seed = xor_bytes(seed, seed_mask)

    encoded_message = b"\x00" + masked_seed + masked_db

    if len(encoded_message) != k:
        raise ValueError("Внутрішня помилка OAEP: неправильна довжина EM.")

    return encoded_message


def oaep_decode(encoded_message: bytes, k: int, label: bytes = b"") -> bytes:
    """
    OAEP decoding.

    Повертає початкове повідомлення або кидає помилку,
    якщо структура OAEP некоректна.
    """
    if len(encoded_message) != k:
        raise ValueError("Некоректна довжина OAEP-блока.")

    if k < 2 * HASH_LEN + 2:
        raise ValueError("RSA-модуль занадто малий для OAEP із SHA-256.")

    y = encoded_message[0]
    masked_seed = encoded_message[1:1 + HASH_LEN]
    masked_db = encoded_message[1 + HASH_LEN:]

    if y != 0:
        raise ValueError("Некоректний OAEP-блок: перший байт не дорівнює 0x00.")

    seed_mask = mgf1(masked_db, HASH_LEN)
    seed = xor_bytes(masked_seed, seed_mask)

    db_mask = mgf1(seed, k - HASH_LEN - 1)
    db = xor_bytes(masked_db, db_mask)

    l_hash = sha256_bytes(label)
    l_hash_from_db = db[:HASH_LEN]

    if l_hash_from_db != l_hash:
        raise ValueError("Некоректний OAEP-блок: label hash не збігається.")

    rest = db[HASH_LEN:]

    separator_index = rest.find(b"\x01")

    if separator_index == -1:
        raise ValueError("Некоректний OAEP-блок: не знайдено розділювач 0x01.")

    padding = rest[:separator_index]

    if any(byte != 0 for byte in padding):
        raise ValueError("Некоректний OAEP-блок: padding має складатися з нулів.")

    message = rest[separator_index + 1:]

    return message


def rsa_oaep_encrypt_block(message: bytes, keypair: RSAKeyPair, label: bytes = b"") -> bytes:
    """
    RSA-OAEP шифрування одного блока.
    """
    k = modulus_byte_length(keypair.n)

    encoded_message = oaep_encode(message, k, label)
    m = int.from_bytes(encoded_message, byteorder="big")

    c = rsa_encrypt_int(m, keypair.n, keypair.e)

    return c.to_bytes(k, byteorder="big")


def rsa_oaep_decrypt_block(ciphertext: bytes, keypair: RSAKeyPair, label: bytes = b"") -> bytes:
    """
    RSA-OAEP дешифрування одного блока через CRT.
    """
    k = modulus_byte_length(keypair.n)

    if len(ciphertext) != k:
        raise ValueError("Некоректна довжина RSA-OAEP криптоблока.")

    c = int.from_bytes(ciphertext, byteorder="big")

    m = rsa_decrypt_int_crt(c, keypair)
    encoded_message = m.to_bytes(k, byteorder="big")

    return oaep_decode(encoded_message, k, label)


def split_blocks(data: bytes, block_size: int) -> list[bytes]:
    return [data[i:i + block_size] for i in range(0, len(data), block_size)]


def rsa_oaep_encrypt_message(data: bytes, keypair: RSAKeyPair, label: bytes = b"") -> bytes:
    """
    Шифрування повідомлення довільної довжини.

    Технічно RSA-OAEP зазвичай використовують для коротких повідомлень,
    наприклад для шифрування симетричного ключа.
    Але для лабораторної зручно реалізувати блоковий режим.
    """
    max_block_len = max_oaep_message_length(keypair.n)

    payload = len(data).to_bytes(4, byteorder="big") + data

    encrypted_blocks = []

    for block in split_blocks(payload, max_block_len):
        encrypted_blocks.append(rsa_oaep_encrypt_block(block, keypair, label))

    return b"".join(encrypted_blocks)


def rsa_oaep_decrypt_message(ciphertext: bytes, keypair: RSAKeyPair, label: bytes = b"") -> bytes:
    """
    Дешифрування повідомлення, зашифрованого rsa_oaep_encrypt_message.
    """
    k = modulus_byte_length(keypair.n)

    if len(ciphertext) % k != 0:
        raise ValueError("Некоректна довжина RSA-OAEP криптотексту.")

    decrypted_blocks = []

    for block in split_blocks(ciphertext, k):
        decrypted_blocks.append(rsa_oaep_decrypt_block(block, keypair, label))

    payload = b"".join(decrypted_blocks)

    if len(payload) < 4:
        raise ValueError("Некоректний розшифрований payload.")

    original_length = int.from_bytes(payload[:4], byteorder="big")
    message = payload[4:4 + original_length]

    return message


def build_report(
    keypair: RSAKeyPair,
    plaintext: bytes,
    ciphertext: bytes,
    decrypted: bytes,
    label: bytes,
) -> str:
    k = modulus_byte_length(keypair.n)
    max_block_len = max_oaep_message_length(keypair.n)

    lines = []

    lines.append("Лабораторна робота 4.3 — RSA-OAEP\n")
    lines.append("=" * 60 + "\n\n")

    lines.append("Параметри RSA:\n")
    lines.append(f"Бінарна довжина p: {keypair.p.bit_length()}\n")
    lines.append(f"Бінарна довжина q: {keypair.q.bit_length()}\n")
    lines.append(f"Бінарна довжина n = p*q: {keypair.n.bit_length()}\n")
    lines.append(f"Розмір RSA-модуля k: {k} байт\n")
    lines.append(f"Відкритий показник e: {keypair.e}\n\n")

    lines.append("Параметри OAEP:\n")
    lines.append("Хеш-функція: SHA-256\n")
    lines.append(f"hLen: {HASH_LEN} байт\n")
    lines.append(f"Максимальна довжина одного OAEP-блока: {max_block_len} байт\n")
    lines.append(f"Label: {label!r}\n\n")

    lines.append("Відкрите повідомлення:\n")
    lines.append(plaintext.decode("utf-8") + "\n\n")

    lines.append("Криптотекст у hex:\n")
    lines.append(ciphertext.hex() + "\n\n")

    lines.append("Розшифроване повідомлення:\n")
    lines.append(decrypted.decode("utf-8") + "\n\n")

    lines.append("Перевірка:\n")
    lines.append(f"Розшифрування збігається з оригіналом: {decrypted == plaintext}\n\n")

    lines.append("Короткий опис OAEP:\n")
    lines.append(
        "OAEP формує закодований блок EM = 0x00 || maskedSeed || maskedDB. "
        "Усередині DB міститься hash(label), нульовий padding, розділювач 0x01 "
        "та саме повідомлення. Для маскування використовуються випадковий seed "
        "і функція MGF1 на основі SHA-256. Завдяки випадковому seed однакові "
        "повідомлення при повторному шифруванні дають різні криптотексти.\n\n"
    )

    lines.append("Висновок:\n")
    lines.append(
        "Було реалізовано RSA-OAEP. На відміну від textbook RSA, OAEP додає "
        "випадковість і структурований padding перед RSA-піднесенням до степеня. "
        "Дешифрування RSA виконано через китайську теорему про остачі, після чого "
        "виконується зворотне OAEP-декодування. Отримане повідомлення збігається "
        "з початковим.\n"
    )

    return "".join(lines)


def main() -> None:
    print("Генерую RSA-ключі для RSA-OAEP...")
    keypair, generation_info = generate_rsa_keypair(SECRET_PRIME_BITS)

    print("Ключі згенеровано.")
    print(f"p bit length: {keypair.p.bit_length()}")
    print(f"q bit length: {keypair.q.bit_length()}")
    print(f"n bit length: {keypair.n.bit_length()}")
    print()

    plaintext = (
        "Привіт! Це демонстрація RSA-OAEP для лабораторної роботи 4.3."
    ).encode("utf-8")

    label = b"lab-4-3"

    print("Шифрую повідомлення через RSA-OAEP...")
    ciphertext = rsa_oaep_encrypt_message(plaintext, keypair, label)

    print("Дешифрую повідомлення через RSA-OAEP + CRT...")
    decrypted = rsa_oaep_decrypt_message(ciphertext, keypair, label)

    print("\n=== РЕЗУЛЬТАТ ===")
    print("Оригінал:", plaintext.decode("utf-8"))
    print("Розшифровано:", decrypted.decode("utf-8"))
    print("OK:", decrypted == plaintext)
    print(f"Криптотекст hex: {ciphertext.hex()}")
    print()

    report = build_report(
        keypair=keypair,
        plaintext=plaintext,
        ciphertext=ciphertext,
        decrypted=decrypted,
        label=label,
    )

    REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"Звіт збережено у файл: {REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main()