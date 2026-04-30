import os
import random
import time
from pathlib import Path
from aes_core import AES

TRIALS = 100_000
BLOCK_SIZE = 16
TASK_2_2_REPORT_FILE = Path("task_2_2_report.txt")


def flip_bit(data: bytes, bit_index: int) -> bytes:
    """
    Перевертає один біт у байтовому рядку.
    bit_index рахується від 0 до len(data)*8 - 1.
    """
    if not (0 <= bit_index < len(data) * 8):
        raise ValueError("Некоректний індекс біта.")

    result = bytearray(data)
    byte_index = bit_index // 8
    bit_in_byte = bit_index % 8
    result[byte_index] ^= (1 << bit_in_byte)
    return bytes(result)


def flip_random_bit(data: bytes) -> tuple[bytes, int]:
    """
    Перевертає один випадковий біт і повертає:
    (нові_дані, індекс_біта)
    """
    bit_index = random.randrange(len(data) * 8)
    return flip_bit(data, bit_index), bit_index


def hamming_distance_bytes(a: bytes, b: bytes) -> int:
    """
    Кількість різних бітів у двох байтових рядках однакової довжини.
    """
    if len(a) != len(b):
        raise ValueError("Для відстані Гемінга довжини мають збігатися.")

    return sum((x ^ y).bit_count() for x, y in zip(a, b))


def average_changed_bits_when_flip_plaintext(key_size_bytes: int, trials: int = TRIALS) -> float:
    """
    Середня кількість змінених бітів криптотексту,
    якщо змінити 1 біт відкритого тексту.
    """
    total_changed_bits = 0

    for _ in range(trials):
        plaintext = os.urandom(BLOCK_SIZE)
        key = os.urandom(key_size_bytes)

        aes = AES(key)

        ciphertext_1 = aes.encrypt_block(plaintext)

        modified_plaintext, _ = flip_random_bit(plaintext)
        ciphertext_2 = aes.encrypt_block(modified_plaintext)

        total_changed_bits += hamming_distance_bytes(ciphertext_1, ciphertext_2)

    return total_changed_bits / trials


def average_changed_bits_when_flip_key(key_size_bytes: int, trials: int = TRIALS) -> float:
    """
    Середня кількість змінених бітів криптотексту,
    якщо змінити 1 біт ключа.
    """
    total_changed_bits = 0

    for _ in range(trials):
        plaintext = os.urandom(BLOCK_SIZE)
        key = os.urandom(key_size_bytes)

        ciphertext_1 = AES(key).encrypt_block(plaintext)

        modified_key, _ = flip_random_bit(key)
        ciphertext_2 = AES(modified_key).encrypt_block(plaintext)

        total_changed_bits += hamming_distance_bytes(ciphertext_1, ciphertext_2)

    return total_changed_bits / trials


def run_task_2_2(trials: int = TRIALS) -> list[dict]:
    variants = [
        ("AES-128", 16),
        ("AES-192", 24),
        ("AES-256", 32),
    ]

    results = []

    for name, key_size in variants:
        print(f"Починаю експеримент для {name}...")
        start_time = time.perf_counter()

        avg_plaintext_flip = average_changed_bits_when_flip_plaintext(key_size, trials)
        avg_key_flip = average_changed_bits_when_flip_key(key_size, trials)

        elapsed = time.perf_counter() - start_time

        results.append({
            "name": name,
            "key_size_bytes": key_size,
            "avg_plaintext_flip": avg_plaintext_flip,
            "avg_key_flip": avg_key_flip,
            "elapsed_seconds": elapsed,
        })

    return results


def build_task_2_2_report(results: list[dict], trials: int) -> str:
    lines = []

    lines.append("Лабораторна робота 2.2 — лавинний ефект AES\n")
    lines.append("=" * 60 + "\n\n")
    lines.append(f"Кількість випадкових випробувань для кожного експерименту: {trials}\n")
    lines.append("Рахується середня кількість змінених бітів у 128-бітному криптотексті.\n\n")

    lines.append("Результати:\n")
    lines.append(f"{'Криптосистема':<12} | {'1 біт plaintext':>15} | {'1 біт key':>12} | {'Час (с)':>10}\n")
    lines.append("-" * 60 + "\n")

    for item in results:
        lines.append(
            f"{item['name']:<12} | "
            f"{item['avg_plaintext_flip']:>15.6f} | "
            f"{item['avg_key_flip']:>12.6f} | "
            f"{item['elapsed_seconds']:>10.2f}\n"
        )

    lines.append("\n")
    lines.append("Короткий висновок:\n")
    lines.append(
        "Для добре реалізованого AES середня кількість змінених бітів "
        "має бути близькою до 64 із 128, тобто приблизно половина блока.\n"
    )

    return "".join(lines)


def print_task_2_2_results(results: list[dict], trials: int) -> None:
    print("\n=== РЕЗУЛЬТАТИ ЗАДАЧІ 2.2 ===")
    print(f"Кількість випробувань: {trials}\n")
    print(f"{'Криптосистема':<12} | {'1 біт plaintext':>15} | {'1 біт key':>12} | {'Час (с)':>10}")
    print("-" * 60)

    for item in results:
        print(
            f"{item['name']:<12} | "
            f"{item['avg_plaintext_flip']:>15.6f} | "
            f"{item['avg_key_flip']:>12.6f} | "
            f"{item['elapsed_seconds']:>10.2f}"
        )


def main_task_2_2() -> None:
    results = run_task_2_2(TRIALS)
    print_task_2_2_results(results, TRIALS)

    report = build_task_2_2_report(results, TRIALS)
    TASK_2_2_REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"\nЗвіт збережено у файл: {TASK_2_2_REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main_task_2_2()