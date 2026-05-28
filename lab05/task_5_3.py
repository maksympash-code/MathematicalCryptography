from __future__ import annotations

from dataclasses import dataclass
from math import isqrt
from pathlib import Path
import secrets


REPORT_FILE = Path("task_5_3_report.txt")


@dataclass
class DiffieHellmanResult:
    p: int
    a: int
    order: int

    alice_private: int
    bob_private: int

    alice_public: int
    bob_public: int

    alice_shared_key: int
    bob_shared_key: int


def is_prime(n: int) -> bool:
    """
    Перевіряє, чи є число n простим.
    Для p з бінарною довжиною <= 20 цього достатньо.
    """
    if n < 2:
        return False

    if n == 2:
        return True

    if n % 2 == 0:
        return False

    limit = isqrt(n)

    for divisor in range(3, limit + 1, 2):
        if n % divisor == 0:
            return False

    return True


def factorize(n: int) -> dict[int, int]:
    """
    Розкладає число n на прості множники.

    Наприклад:
        22 = 2 * 11
        factorize(22) -> {2: 1, 11: 1}
    """
    factors: dict[int, int] = {}

    while n % 2 == 0:
        factors[2] = factors.get(2, 0) + 1
        n //= 2

    divisor = 3

    while divisor * divisor <= n:
        while n % divisor == 0:
            factors[divisor] = factors.get(divisor, 0) + 1
            n //= divisor

        divisor += 2

    if n > 1:
        factors[n] = factors.get(n, 0) + 1

    return factors


def is_primitive_element(a: int, p: int, prime_divisors: list[int]) -> bool:
    """
    Перевіряє, чи є a твірним елементом GF(p)^*.

    Критерій:
        a^((p - 1) / q) != 1 mod p

    для кожного простого дільника q числа p - 1.
    """
    if not (1 <= a <= p - 1):
        return False

    for q in prime_divisors:
        exponent = (p - 1) // q

        if pow(a, exponent, p) == 1:
            return False

    return True


def find_primitive_element(p: int) -> int:
    """
    Знаходить найменший твірний елемент групи GF(p)^*.
    """
    if p == 2:
        return 1

    if p % 2 == 0:
        raise ValueError("p має бути непарним простим числом.")

    if p.bit_length() > 20:
        raise ValueError("Бінарна довжина p має бути не більшою за 20.")

    if not is_prime(p):
        raise ValueError("p має бути простим числом.")

    factors = factorize(p - 1)
    prime_divisors = list(factors.keys())

    for a in range(2, p):
        if is_primitive_element(a, p, prime_divisors):
            return a

    raise RuntimeError("Твірний елемент не знайдено.")


def element_order(a: int, p: int) -> int:
    """
    Знаходить порядок елемента a в GF(p)^*.

    Порядок — це найменше додатне r таке, що:

        a^r ≡ 1 mod p
    """
    if not is_prime(p):
        raise ValueError("p має бути простим числом.")

    if not (1 <= a < p):
        raise ValueError("a має бути в діапазоні 1 <= a < p.")

    group_order = p - 1
    factors = factorize(group_order)

    order = group_order

    for q in factors:
        while order % q == 0 and pow(a, order // q, p) == 1:
            order //= q

    return order


def generate_private_key(order: int) -> int:
    """
    Генерує секретний ключ користувача.

    Беремо число з діапазону:
        1 <= x <= order - 1
    """
    if order <= 1:
        raise ValueError("Порядок групи має бути більшим за 1.")

    return secrets.randbelow(order - 1) + 1


def diffie_hellman_protocol(p: int, a: int) -> DiffieHellmanResult:
    """
    Реалізує протокол Діффі-Хеллмана в групі G = <a>.

    Alice:
        x_A — секрет
        A = a^x_A mod p

    Bob:
        x_B — секрет
        B = a^x_B mod p

    Спільний ключ:
        K_A = B^x_A mod p
        K_B = A^x_B mod p
    """
    if p.bit_length() > 20:
        raise ValueError("За умовою бінарна довжина p має бути <= 20.")

    if not is_prime(p):
        raise ValueError("p має бути простим числом.")

    if not (1 <= a < p):
        raise ValueError("a має бути елементом GF(p)^*.")

    order = element_order(a, p)

    alice_private = generate_private_key(order)
    bob_private = generate_private_key(order)

    alice_public = pow(a, alice_private, p)
    bob_public = pow(a, bob_private, p)

    alice_shared_key = pow(bob_public, alice_private, p)
    bob_shared_key = pow(alice_public, bob_private, p)

    return DiffieHellmanResult(
        p=p,
        a=a,
        order=order,
        alice_private=alice_private,
        bob_private=bob_private,
        alice_public=alice_public,
        bob_public=bob_public,
        alice_shared_key=alice_shared_key,
        bob_shared_key=bob_shared_key,
    )


def build_report(result: DiffieHellmanResult) -> str:
    lines = []

    lines.append("Лабораторна робота 5.3 — протокол Діффі-Хеллмана\n")
    lines.append("=" * 70 + "\n\n")

    lines.append("Параметри групи:\n")
    lines.append(f"p = {result.p}\n")
    lines.append(f"Бінарна довжина p: {result.p.bit_length()}\n")
    lines.append(f"a = {result.a}\n")
    lines.append(f"G = <a>\n")
    lines.append(f"Порядок групи G: {result.order}\n\n")

    lines.append("Секретні ключі сторін:\n")
    lines.append(f"Аліса: x_A = {result.alice_private}\n")
    lines.append(f"Боб:   x_B = {result.bob_private}\n\n")

    lines.append("Відкриті значення:\n")
    lines.append(f"Аліса обчислює A = a^x_A mod p = {result.alice_public}\n")
    lines.append(f"Боб обчислює   B = a^x_B mod p = {result.bob_public}\n\n")

    lines.append("Обчислення спільного ключа:\n")
    lines.append(f"Аліса обчислює K_A = B^x_A mod p = {result.alice_shared_key}\n")
    lines.append(f"Боб обчислює   K_B = A^x_B mod p = {result.bob_shared_key}\n\n")

    lines.append("Перевірка:\n")
    lines.append(f"K_A == K_B: {result.alice_shared_key == result.bob_shared_key}\n\n")

    lines.append("Пояснення:\n")
    lines.append(
        "Оскільки A = a^x_A mod p, а B = a^x_B mod p, то Аліса отримує "
        "K_A = B^x_A = (a^x_B)^x_A = a^(x_A*x_B) mod p. "
        "Боб отримує K_B = A^x_B = (a^x_A)^x_B = a^(x_A*x_B) mod p. "
        "Тому обидві сторони отримують однаковий спільний секретний ключ.\n\n"
    )

    lines.append("Висновок:\n")
    lines.append(
        "Було реалізовано протокол Діффі-Хеллмана на основі мультиплікативної групи "
        "G = <a> поля GF(p). Обидві сторони незалежно обчислили однаковий спільний ключ, "
        "не передаючи його напряму відкритим каналом.\n"
    )

    return "".join(lines)


def print_result(result: DiffieHellmanResult) -> None:
    print("=== Лабораторна робота 5.3 ===")
    print("Протокол Діффі-Хеллмана")
    print()

    print("Параметри групи:")
    print(f"p = {result.p}")
    print(f"a = {result.a}")
    print(f"Порядок G = <a>: {result.order}")
    print()

    print("Секретні ключі:")
    print(f"x_A = {result.alice_private}")
    print(f"x_B = {result.bob_private}")
    print()

    print("Відкриті значення:")
    print(f"A = a^x_A mod p = {result.alice_public}")
    print(f"B = a^x_B mod p = {result.bob_public}")
    print()

    print("Спільні ключі:")
    print(f"K_A = B^x_A mod p = {result.alice_shared_key}")
    print(f"K_B = A^x_B mod p = {result.bob_shared_key}")
    print()

    print(f"Ключі збігаються: {result.alice_shared_key == result.bob_shared_key}")


def main() -> None:
    raw_p = input("Введіть просте p з бінарною довжиною <= 20 [за замовчуванням 23]: ").strip()

    if raw_p:
        p = int(raw_p)
    else:
        p = 23

    if p.bit_length() > 20:
        raise ValueError("За умовою бінарна довжина p має бути <= 20.")

    if not is_prime(p):
        raise ValueError("p має бути простим числом.")

    default_a = find_primitive_element(p)

    raw_a = input(f"Введіть елемент a [за замовчуванням твірний a = {default_a}]: ").strip()

    if raw_a:
        a = int(raw_a)
    else:
        a = default_a

    result = diffie_hellman_protocol(p, a)

    print_result(result)

    report = build_report(result)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print()
    print(f"Звіт збережено у файл: {REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main()