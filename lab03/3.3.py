import os
import time
from pathlib import Path

from sha256_core import sha256_bytes


MIN_K = 5
MAX_K = 15
ATTEMPTS_PER_K = 100

REPORT_FILE = Path("task_3_3_report.txt")


def first_k_bits(digest: bytes, k: int) -> int:
    """
    Повертає перші k бітів digest як ціле число.
    Наприклад, якщо k = 10, беремо перші 10 бітів SHA-256.
    """
    if not (1 <= k <= len(digest) * 8):
        raise ValueError("Некоректне значення k.")

    bytes_needed = (k + 7) // 8
    prefix_bytes = digest[:bytes_needed]

    prefix_int = int.from_bytes(prefix_bytes, byteorder="big")

    extra_bits = bytes_needed * 8 - k

    return prefix_int >> extra_bits


def random_message() -> bytes:
    """
    Генерує випадкове повідомлення.
    """
    return os.urandom(32)


def find_partial_collision(k: int) -> dict:
    """
    Шукає два різні повідомлення, SHA-256 яких має однакові перші k бітів.
    Використовується birthday-підхід:
    генеруємо повідомлення, рахуємо префікс хешу, зберігаємо вже побачені префікси.
    """
    seen: dict[int, bytes] = {}

    hashes_checked = 0
    start_time = time.perf_counter()

    while True:
        message = random_message()
        digest = sha256_bytes(message)
        prefix = first_k_bits(digest, k)

        hashes_checked += 1

        if prefix in seen and seen[prefix] != message:
            elapsed_time = time.perf_counter() - start_time

            return {
                "k": k,
                "prefix": prefix,
                "message_1": seen[prefix],
                "message_2": message,
                "hash_1": sha256_bytes(seen[prefix]),
                "hash_2": digest,
                "hashes_checked": hashes_checked,
                "elapsed_time": elapsed_time,
            }

        seen[prefix] = message


def run_experiments() -> list[dict]:
    """
    Для кожного k від 5 до 15 виконує 100 спроб
    і рахує середній час пошуку часткової колізії.
    """
    results = []

    for k in range(MIN_K, MAX_K + 1):
        print(f"Починаю експерименти для k = {k}...")

        total_time = 0.0
        total_hashes_checked = 0
        example_collision = None

        for attempt in range(1, ATTEMPTS_PER_K + 1):
            collision = find_partial_collision(k)

            total_time += collision["elapsed_time"]
            total_hashes_checked += collision["hashes_checked"]

            if example_collision is None:
                example_collision = collision

        average_time = total_time / ATTEMPTS_PER_K
        average_hashes_checked = total_hashes_checked / ATTEMPTS_PER_K

        results.append({
            "k": k,
            "average_time": average_time,
            "average_hashes_checked": average_hashes_checked,
            "example_collision": example_collision,
        })

    return results


def print_results(results: list[dict]) -> None:
    print("\n=== Л3.3 — Часткові колізії SHA-256 ===\n")

    print(f"{'k':>3} | {'Середній час (с)':>18} | {'Середня кількість хешів':>25}")
    print("-" * 55)

    for item in results:
        print(
            f"{item['k']:>3} | "
            f"{item['average_time']:>18.8f} | "
            f"{item['average_hashes_checked']:>25.2f}"
        )


def build_report(results: list[dict]) -> str:
    lines = []

    lines.append("Лабораторна робота 3.3 — пошук часткових колізій SHA-256\n")
    lines.append("=" * 75 + "\n\n")

    lines.append("Мета: знайти часткові колізії для перших k бітів SHA-256, де 5 <= k <= 15.\n")
    lines.append(f"Для кожного k виконано {ATTEMPTS_PER_K} незалежних спроб.\n")
    lines.append("У таблиці наведено середній час пошуку та середню кількість обчислених хешів.\n\n")

    lines.append(f"{'k':>3} | {'Середній час (с)':>18} | {'Середня кількість хешів':>25}\n")
    lines.append("-" * 55 + "\n")

    for item in results:
        lines.append(
            f"{item['k']:>3} | "
            f"{item['average_time']:>18.8f} | "
            f"{item['average_hashes_checked']:>25.2f}\n"
        )

    lines.append("\nПриклади знайдених часткових колізій:\n\n")

    for item in results:
        collision = item["example_collision"]
        k = item["k"]
        prefix = collision["prefix"]

        lines.append(f"k = {k}\n")
        lines.append(f"Спільні перші {k} бітів: {prefix:0{k}b}\n")
        lines.append(f"Повідомлення 1 hex: {collision['message_1'].hex()}\n")
        lines.append(f"Повідомлення 2 hex: {collision['message_2'].hex()}\n")
        lines.append(f"SHA-256 повідомлення 1: {collision['hash_1'].hex()}\n")
        lines.append(f"SHA-256 повідомлення 2: {collision['hash_2'].hex()}\n")
        lines.append(f"Кількість перевірених хешів у прикладі: {collision['hashes_checked']}\n")
        lines.append(f"Час пошуку прикладу: {collision['elapsed_time']:.8f} с\n\n")

    lines.append("Висновок:\n")
    lines.append(
        "Зі збільшенням k пошук часткової колізії в середньому потребує більше часу "
        "та більшої кількості обчислень хеш-функції. Це очікувано, оскільки кількість "
        "можливих k-бітних префіксів дорівнює 2^k. Завдяки birthday-парадоксу колізія "
        "зазвичай знаходиться приблизно після 2^(k/2) перевірок, а не після 2^k.\n"
    )

    return "".join(lines)


def main() -> None:
    results = run_experiments()

    print_results(results)

    report = build_report(results)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"\nЗвіт збережено у файл: {REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main()