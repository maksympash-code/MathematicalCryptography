from __future__ import annotations

import secrets
from pathlib import Path


BIT_LENGTH = 512
ROUNDS = 100
TEST_NUMBERS_COUNT = 5

REPORT_FILE = Path("task_4_1_report.txt")


def generate_odd_number_with_bit_length(bit_length: int) -> int:
    """
    Генерує випадкове непарне число заданої бінарної довжини.

    Для 512 бітів:
    - старший біт = 1, щоб число справді мало довжину 512;
    - молодший біт = 1, щоб число було непарним.
    """
    if bit_length < 2:
        raise ValueError("Бінарна довжина має бути не меншою за 2.")

    n = secrets.randbits(bit_length)

    # Встановлюємо старший біт.
    n |= 1 << (bit_length - 1)

    # Встановлюємо молодший біт, щоб число було непарним.
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

    Повертає:
    - True, якщо число n пройшло тест для основи a;
    - False, якщо знайдено свідка складеності.
    """
    x = pow(a, d, n)

    if x == 1 or x == n - 1:
        return True

    for _ in range(s - 1):
        x = pow(x, 2, n)

        if x == n - 1:
            return True

    return False


def miller_rabin_test(n: int, rounds: int = 100) -> dict:
    """
    Ймовірнісний тест простоти Міллера-Рабіна.

    Якщо хоча б один раунд знаходить свідка складеності,
    результат — "складене".

    Якщо всі rounds раундів пройдені,
    результат — "можливо просте".
    """
    if n < 2:
        return {
            "n": n,
            "status": "складене",
            "reason": "n < 2",
            "rounds_completed": 0,
            "witnesses": [],
        }

    if n in (2, 3):
        return {
            "n": n,
            "status": "просте",
            "reason": "n дорівнює 2 або 3",
            "rounds_completed": 0,
            "witnesses": [],
        }

    if n % 2 == 0:
        return {
            "n": n,
            "status": "складене",
            "reason": "n парне",
            "rounds_completed": 0,
            "witnesses": [],
        }

    s, d = decompose_n_minus_1(n)

    witnesses = []

    for round_index in range(1, rounds + 1):
        a = secrets.randbelow(n - 3) + 2
        witnesses.append(a)

        passed = miller_rabin_round(n, a, s, d)

        if not passed:
            return {
                "n": n,
                "status": "складене",
                "reason": f"основа a = {a} є свідком складеності",
                "rounds_completed": round_index,
                "witnesses": witnesses,
                "s": s,
                "d": d,
            }

    return {
        "n": n,
        "status": "можливо просте",
        "reason": f"усі {rounds} раундів пройдено",
        "rounds_completed": rounds,
        "witnesses": witnesses,
        "s": s,
        "d": d,
    }


def format_test_result(result: dict, number_index: int) -> str:
    lines = []

    n = result["n"]

    lines.append(f"=== Тестове число #{number_index} ===\n")
    lines.append(f"n = {n}\n")
    lines.append(f"Бінарна довжина n: {n.bit_length()}\n")
    lines.append(f"Статус: {result['status']}\n")
    lines.append(f"Причина: {result['reason']}\n")
    lines.append(f"Кількість виконаних раундів: {result['rounds_completed']}\n")

    if "s" in result and "d" in result:
        lines.append(f"Розклад n - 1 = 2^s * d:\n")
        lines.append(f"s = {result['s']}\n")
        lines.append(f"d = {result['d']}\n")

    lines.append("\nВипадкові основи a:\n")

    for i, a in enumerate(result["witnesses"], start=1):
        lines.append(f"Раунд {i:3d}: a = {a}\n")

    lines.append("\n")

    return "".join(lines)


def run_lab_4_1() -> list[dict]:
    results = []

    for i in range(1, TEST_NUMBERS_COUNT + 1):
        print(f"Генерую тестове число #{i}...")

        n = generate_odd_number_with_bit_length(BIT_LENGTH)
        result = miller_rabin_test(n, ROUNDS)

        results.append(result)

        print(f"n #{i}: {result['status']}")
        print(f"Виконано раундів: {result['rounds_completed']}")
        print()

    return results


def build_report(results: list[dict]) -> str:
    lines = []

    lines.append("Лабораторна робота 4.1 — тест простоти Міллера-Рабіна\n")
    lines.append("=" * 70 + "\n\n")

    lines.append(f"Бінарна довжина тестових чисел: {BIT_LENGTH}\n")
    lines.append(f"Максимальна кількість раундів для одного числа: {ROUNDS}\n")
    lines.append(f"Кількість тестових чисел: {TEST_NUMBERS_COUNT}\n\n")

    for i, result in enumerate(results, start=1):
        lines.append(format_test_result(result, i))

    return "".join(lines)


def main() -> None:
    results = run_lab_4_1()

    report = build_report(results)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print(f"Звіт збережено у файл: {REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main()