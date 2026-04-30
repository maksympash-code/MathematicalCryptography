import os
import random
import time
from pathlib import Path
from aes_core import AES

TRIALS_2_3 = 20_000
BLOCK_SIZE = 16
ROUNDS_TO_TEST = list(range(1, 15))   # 1..14
TASK_2_3_REPORT_FILE = Path("task_2_3_report.txt")


def flip_bit(data: bytes, bit_index: int) -> bytes:
    if not (0 <= bit_index < len(data) * 8):
        raise ValueError("Некоректний індекс біта.")

    result = bytearray(data)
    byte_index = bit_index // 8
    bit_in_byte = bit_index % 8
    result[byte_index] ^= (1 << bit_in_byte)
    return bytes(result)


def flip_random_bit(data: bytes) -> tuple[bytes, int]:
    bit_index = random.randrange(len(data) * 8)
    return flip_bit(data, bit_index), bit_index


def hamming_distance_bytes(a: bytes, b: bytes) -> int:
    if len(a) != len(b):
        raise ValueError("Довжини мають збігатися.")
    return sum((x ^ y).bit_count() for x, y in zip(a, b))


def average_changed_bits_flip_plaintext(rounds: int, trials: int = TRIALS_2_3) -> float:
    total_changed_bits = 0

    for _ in range(trials):
        plaintext = os.urandom(BLOCK_SIZE)
        key = os.urandom(16)  # AES-128 => 16 байт

        aes = AES(key, rounds_override=rounds)

        ciphertext_1 = aes.encrypt_block(plaintext)

        modified_plaintext, _ = flip_random_bit(plaintext)
        ciphertext_2 = aes.encrypt_block(modified_plaintext)

        total_changed_bits += hamming_distance_bytes(ciphertext_1, ciphertext_2)

    return total_changed_bits / trials


def average_changed_bits_flip_key(rounds: int, trials: int = TRIALS_2_3) -> float:
    total_changed_bits = 0

    for _ in range(trials):
        plaintext = os.urandom(BLOCK_SIZE)
        key = os.urandom(16)  # AES-128 => 16 байт

        ciphertext_1 = AES(key, rounds_override=rounds).encrypt_block(plaintext)

        modified_key, _ = flip_random_bit(key)
        ciphertext_2 = AES(modified_key, rounds_override=rounds).encrypt_block(plaintext)

        total_changed_bits += hamming_distance_bytes(ciphertext_1, ciphertext_2)

    return total_changed_bits / trials


def run_task_2_3(rounds_list: list[int], trials: int = TRIALS_2_3) -> list[dict]:
    results = []

    for rounds in rounds_list:
        print(f"Починаю експеримент для AES-128, rounds = {rounds}...")
        start_time = time.perf_counter()

        avg_plaintext_flip = average_changed_bits_flip_plaintext(rounds, trials)
        avg_key_flip = average_changed_bits_flip_key(rounds, trials)

        elapsed = time.perf_counter() - start_time

        results.append({
            "rounds": rounds,
            "avg_plaintext_flip": avg_plaintext_flip,
            "avg_key_flip": avg_key_flip,
            "elapsed_seconds": elapsed,
        })

    return results


def build_task_2_3_report(results: list[dict], trials: int) -> str:
    lines = []

    lines.append("Лабораторна робота 2.3 — вплив кількості раундів на лавинний ефект AES-128\n")
    lines.append("=" * 85 + "\n\n")
    lines.append(f"Кількість випадкових випробувань для кожного значення rounds: {trials}\n")
    lines.append("Досліджується AES-128 при зміні кількості раундів.\n")
    lines.append("Рахується середня кількість змінених бітів 128-бітного криптотексту.\n\n")

    lines.append(f"{'Раунди':>6} | {'1 біт plaintext':>15} | {'1 біт key':>12} | {'Час (с)':>10}\n")
    lines.append("-" * 56 + "\n")

    for item in results:
        lines.append(
            f"{item['rounds']:>6} | "
            f"{item['avg_plaintext_flip']:>15.6f} | "
            f"{item['avg_key_flip']:>12.6f} | "
            f"{item['elapsed_seconds']:>10.2f}\n"
        )

    lines.append("\n")
    lines.append("Якісний висновок:\n")
    lines.append(
        "При малій кількості раундів лавинний ефект слабший: змінюється суттєво менше бітів, "
        "ніж половина блока. Зі збільшенням числа раундів середня кількість змінених бітів "
        "наближається до ~64 і далі стабілізується.\n"
    )

    return "".join(lines)


def print_task_2_3_results(results: list[dict], trials: int) -> None:
    print("\n=== РЕЗУЛЬТАТИ ЗАДАЧІ 2.3 ===")
    print(f"Кількість випробувань: {trials}")
    print("AES-128 з різною кількістю раундів\n")

    print(f"{'Раунди':>6} | {'1 біт plaintext':>15} | {'1 біт key':>12} | {'Час (с)':>10}")
    print("-" * 56)

    for item in results:
        print(
            f"{item['rounds']:>6} | "
            f"{item['avg_plaintext_flip']:>15.6f} | "
            f"{item['avg_key_flip']:>12.6f} | "
            f"{item['elapsed_seconds']:>10.2f}"
        )


def main_task_2_3() -> None:
    results = run_task_2_3(ROUNDS_TO_TEST, TRIALS_2_3)
    print_task_2_3_results(results, TRIALS_2_3)

    report = build_task_2_3_report(results, TRIALS_2_3)
    TASK_2_3_REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"\nЗвіт збережено у файл: {TASK_2_3_REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main_task_2_3()