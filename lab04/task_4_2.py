from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math
import secrets
import time


SECRET_PRIME_BITS = 512
MILLER_RABIN_ROUNDS = 100
PUBLIC_EXPONENT = 65537

REPORT_FILE = Path("task_4_2_report.txt")


SMALL_PRIMES = [
    3, 5, 7, 11, 13, 17, 19, 23, 29, 31,
    37, 41, 43, 47, 53, 59, 61, 67, 71, 73,
    79, 83, 89, 97,
]


@dataclass
class RSAKeyPair:
    n: int
    e: int
    d: int
    p: int
    q: int
    dp: int
    dq: int
    q_inv: int


def generate_odd_number_with_bit_length(bit_length: int) -> int:
    """
    Генерує випадкове непарне число заданої бінарної довжини.
    """
    if bit_length < 2:
        raise ValueError("Бінарна довжина має бути не меншою за 2.")

    n = secrets.randbits(bit_length)

    # Старший біт = 1, щоб число точно мало потрібну бінарну довжину.
    n |= 1 << (bit_length - 1)

    # Молодший біт = 1, щоб число було непарним.
    n |= 1

    return n


def decompose_n_minus_1(n: int) -> tuple[int, int]:
    """
    Розкладає n - 1 у вигляді:

        n - 1 = 2^s * d,

    де d — непарне.
    """
    d = n - 1
    s = 0

    while d % 2 == 0:
        d //= 2
        s += 1

    return s, d


def miller_rabin_round(n: int, a: int, s: int, d: int) -> bool:
    """
    Один раунд тесту Міллера-Рабіна.

    True  -> n пройшло тест для основи a.
    False -> a є свідком складеності n.
    """
    x = pow(a, d, n)

    if x == 1 or x == n - 1:
        return True

    for _ in range(s - 1):
        x = pow(x, 2, n)

        if x == n - 1:
            return True

    return False


def is_probable_prime(n: int, rounds: int = MILLER_RABIN_ROUNDS) -> bool:
    """
    Перевірка числа на ймовірну простоту тестом Міллера-Рабіна.
    """
    if n < 2:
        return False

    if n in (2, 3):
        return True

    if n % 2 == 0:
        return False

    # Швидкий відсів малими простими числами.
    for p in SMALL_PRIMES:
        if n == p:
            return True
        if n % p == 0:
            return False

    s, d = decompose_n_minus_1(n)

    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2

        if not miller_rabin_round(n, a, s, d):
            return False

    return True


def generate_probable_prime(bit_length: int, e: int = PUBLIC_EXPONENT) -> tuple[int, int]:
    """
    Генерує ймовірно просте число заданої бінарної довжини.

    Додатково перевіряємо gcd(e, p - 1) = 1,
    щоб потім можна було нормально побудувати RSA-ключ.
    """
    attempts = 0

    while True:
        attempts += 1
        candidate = generate_odd_number_with_bit_length(bit_length)

        if math.gcd(e, candidate - 1) != 1:
            continue

        if is_probable_prime(candidate, MILLER_RABIN_ROUNDS):
            return candidate, attempts


def generate_rsa_keypair(prime_bits: int = SECRET_PRIME_BITS) -> tuple[RSAKeyPair, dict]:
    """
    Генерує RSA-ключ.

    p і q — секретні прості числа довжини prime_bits.
    n = p * q.
    e = 65537.
    d = e^(-1) mod phi(n).
    """
    start_time = time.perf_counter()

    p, p_attempts = generate_probable_prime(prime_bits, PUBLIC_EXPONENT)

    while True:
        q, q_attempts = generate_probable_prime(prime_bits, PUBLIC_EXPONENT)
        if q != p:
            break

    n = p * q
    phi = (p - 1) * (q - 1)

    if math.gcd(PUBLIC_EXPONENT, phi) != 1:
        # Теоретично ми це вже контролюємо через gcd(e, p-1) і gcd(e, q-1),
        # але хай буде як додаткова перевірка.
        raise ValueError("e не є взаємно простим з phi(n). Потрібно згенерувати інші p і q.")

    d = pow(PUBLIC_EXPONENT, -1, phi)

    dp = d % (p - 1)
    dq = d % (q - 1)

    # q_inv = q^(-1) mod p.
    # Потрібно для CRT-дешифрування.
    q_inv = pow(q, -1, p)

    elapsed = time.perf_counter() - start_time

    keypair = RSAKeyPair(
        n=n,
        e=PUBLIC_EXPONENT,
        d=d,
        p=p,
        q=q,
        dp=dp,
        dq=dq,
        q_inv=q_inv,
    )

    info = {
        "p_attempts": p_attempts,
        "q_attempts": q_attempts,
        "elapsed_seconds": elapsed,
    }

    return keypair, info


def rsa_encrypt_int(message: int, n: int, e: int) -> int:
    """
    RSA-шифрування одного числа:

        c = m^e mod n
    """
    if not (0 <= message < n):
        raise ValueError("Повідомлення як число має бути в діапазоні 0 <= m < n.")

    return pow(message, e, n)


def rsa_decrypt_int_standard(ciphertext: int, keypair: RSAKeyPair) -> int:
    """
    Звичайне RSA-дешифрування:

        m = c^d mod n

    Ця функція потрібна для перевірки.
    Основне дешифрування для лабораторної робимо через CRT.
    """
    return pow(ciphertext, keypair.d, keypair.n)


def rsa_decrypt_int_crt(ciphertext: int, keypair: RSAKeyPair) -> int:
    """
    RSA-дешифрування через китайську теорему про остачі.

    Обчислюємо:

        m1 = c^dp mod p
        m2 = c^dq mod q

    Потім відновлюємо m modulo n за CRT:

        h = q_inv * (m1 - m2) mod p
        m = m2 + q * h
    """
    p = keypair.p
    q = keypair.q

    m1 = pow(ciphertext % p, keypair.dp, p)
    m2 = pow(ciphertext % q, keypair.dq, q)

    h = ((m1 - m2) * keypair.q_inv) % p
    message = m2 + q * h

    return message


def get_plain_block_size(n: int) -> int:
    """
    Максимальний розмір блока відкритого тексту в байтах.

    Беремо трохи менше за розмір n, щоб кожен блок як число був < n.
    """
    return (n.bit_length() - 1) // 8


def get_cipher_block_size(n: int) -> int:
    """
    Розмір блока криптотексту в байтах.
    """
    return (n.bit_length() + 7) // 8


def split_blocks(data: bytes, block_size: int) -> list[bytes]:
    return [data[i:i + block_size] for i in range(0, len(data), block_size)]


def rsa_encrypt_bytes(data: bytes, keypair: RSAKeyPair) -> bytes:
    """
    Шифрує байтове повідомлення RSA.

    Для коректного відновлення довжини додаємо 4 байти довжини повідомлення.
    Потім ділимо на блоки.
    """
    plain_block_size = get_plain_block_size(keypair.n)
    cipher_block_size = get_cipher_block_size(keypair.n)

    payload = len(data).to_bytes(4, byteorder="big") + data

    encrypted_blocks = []

    for block in split_blocks(payload, plain_block_size):
        # Доповнюємо останній блок нулями справа,
        # щоб при int.from_bytes не втратити структуру блоку.
        block = block.ljust(plain_block_size, b"\x00")

        m = int.from_bytes(block, byteorder="big")
        c = rsa_encrypt_int(m, keypair.n, keypair.e)

        encrypted_blocks.append(c.to_bytes(cipher_block_size, byteorder="big"))

    return b"".join(encrypted_blocks)


def rsa_decrypt_bytes_crt(ciphertext: bytes, keypair: RSAKeyPair) -> bytes:
    """
    Дешифрує байтове повідомлення RSA через CRT.
    """
    plain_block_size = get_plain_block_size(keypair.n)
    cipher_block_size = get_cipher_block_size(keypair.n)

    if len(ciphertext) % cipher_block_size != 0:
        raise ValueError("Некоректна довжина криптотексту.")

    decrypted_blocks = []

    for block in split_blocks(ciphertext, cipher_block_size):
        c = int.from_bytes(block, byteorder="big")
        m = rsa_decrypt_int_crt(c, keypair)

        decrypted_blocks.append(m.to_bytes(plain_block_size, byteorder="big"))

    payload = b"".join(decrypted_blocks)

    original_length = int.from_bytes(payload[:4], byteorder="big")
    message = payload[4:4 + original_length]

    return message


def build_report(
    keypair: RSAKeyPair,
    generation_info: dict,
    plaintext: bytes,
    ciphertext: bytes,
    decrypted: bytes,
    standard_decrypted_int_ok: bool,
) -> str:
    lines = []

    lines.append("Лабораторна робота 4.2 — криптосистема RSA\n")
    lines.append("=" * 60 + "\n\n")

    lines.append("Параметри RSA:\n")
    lines.append(f"Бінарна довжина секретного простого p: {keypair.p.bit_length()}\n")
    lines.append(f"Бінарна довжина секретного простого q: {keypair.q.bit_length()}\n")
    lines.append(f"Бінарна довжина модуля n = p*q: {keypair.n.bit_length()}\n")
    lines.append(f"Відкритий показник e: {keypair.e}\n")
    lines.append(f"Бінарна довжина секретного показника d: {keypair.d.bit_length()}\n")
    lines.append(f"Кількість спроб для p: {generation_info['p_attempts']}\n")
    lines.append(f"Кількість спроб для q: {generation_info['q_attempts']}\n")
    lines.append(f"Час генерації ключів: {generation_info['elapsed_seconds']:.4f} с\n\n")

    lines.append("CRT-параметри:\n")
    lines.append(f"dp = d mod (p - 1), бінарна довжина: {keypair.dp.bit_length()}\n")
    lines.append(f"dq = d mod (q - 1), бінарна довжина: {keypair.dq.bit_length()}\n")
    lines.append(f"q_inv = q^(-1) mod p, бінарна довжина: {keypair.q_inv.bit_length()}\n\n")

    lines.append("Тестове повідомлення:\n")
    lines.append(plaintext.decode("utf-8") + "\n\n")

    lines.append("Криптотекст у hex:\n")
    lines.append(ciphertext.hex() + "\n\n")

    lines.append("Розшифроване повідомлення:\n")
    lines.append(decrypted.decode("utf-8") + "\n\n")

    lines.append("Перевірки:\n")
    lines.append(f"Дешифрування через CRT збігається з оригіналом: {decrypted == plaintext}\n")
    lines.append(f"Стандартне дешифрування одного тестового блока збігається з CRT: {standard_decrypted_int_ok}\n\n")

    lines.append("Висновок:\n")
    lines.append(
        "Було реалізовано криптосистему RSA з генерацією секретних простих чисел p і q "
        "заданої бінарної довжини. Для перевірки простоти використано тест Міллера-Рабіна. "
        "Шифрування виконується за формулою c = m^e mod n, а дешифрування реалізовано "
        "через китайську теорему про остачі за допомогою значень dp, dq та q_inv.\n"
    )

    return "".join(lines)


def main() -> None:
    print("Генерую RSA-ключі...")
    keypair, generation_info = generate_rsa_keypair(SECRET_PRIME_BITS)

    print("Ключі згенеровано.")
    print(f"p bit length: {keypair.p.bit_length()}")
    print(f"q bit length: {keypair.q.bit_length()}")
    print(f"n bit length: {keypair.n.bit_length()}")
    print(f"e: {keypair.e}")
    print()

    plaintext = "Привіт! Це тест RSA для лабораторної роботи 4.2.".encode("utf-8")

    print("Шифрую повідомлення...")
    ciphertext = rsa_encrypt_bytes(plaintext, keypair)

    print("Дешифрую повідомлення через CRT...")
    decrypted = rsa_decrypt_bytes_crt(ciphertext, keypair)

    # Маленька перевірка на одному числовому повідомленні.
    test_m = 123456789
    test_c = rsa_encrypt_int(test_m, keypair.n, keypair.e)
    test_dec_standard = rsa_decrypt_int_standard(test_c, keypair)
    test_dec_crt = rsa_decrypt_int_crt(test_c, keypair)

    standard_decrypted_int_ok = (
        test_dec_standard == test_dec_crt == test_m
    )

    print("=== РЕЗУЛЬТАТ ===")
    print("Оригінал:", plaintext.decode("utf-8"))
    print("Розшифровано:", decrypted.decode("utf-8"))
    print("CRT OK:", decrypted == plaintext)
    print("Стандартне дешифрування == CRT:", standard_decrypted_int_ok)
    print(f"Криптотекст hex: {ciphertext.hex()}")
    print()

    report = build_report(
        keypair=keypair,
        generation_info=generation_info,
        plaintext=plaintext,
        ciphertext=ciphertext,
        decrypted=decrypted,
        standard_decrypted_int_ok=standard_decrypted_int_ok,
    )

    REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"Звіт збережено у файл: {REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main()