from __future__ import annotations

from math import isqrt


def is_prime(n: int) -> bool:
    """
    Перевіряє, чи є число n простим.

    Оскільки в умові p має бінарну довжину не більше 20,
    тобто p <= 2^20, простого trial division більш ніж достатньо.
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

    Повертає словник:
        простий_дільник -> степінь

    Наприклад:
        22 = 2 * 11
        factorize(22) -> {2: 1, 11: 1}

        36 = 2^2 * 3^2
        factorize(36) -> {2: 2, 3: 2}
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
    Перевіряє, чи є a твірним елементом групи GF(p)^*.

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

    raise RuntimeError("Твірний елемент не знайдено. Для простого p такого не має статись.")


def generate_powers(a: int, p: int) -> list[int]:
    """
    Генерує послідовність:
        a^1, a^2, ..., a^(p-1) mod p

    Якщо a — твірний елемент, ця послідовність містить усі числа 1..p-1.
    """
    powers = []

    current = 1

    for _ in range(1, p):
        current = (current * a) % p
        powers.append(current)

    return powers


def print_report(p: int, a: int) -> None:
    factors = factorize(p - 1)
    prime_divisors = list(factors.keys())
    powers = generate_powers(a, p)

    print("=== Лабораторна робота 5.1 ===")
    print("Пошук твірного елемента групи GF(p)^*")
    print()

    print(f"p = {p}")
    print(f"Бінарна довжина p: {p.bit_length()}")
    print(f"Порядок групи GF(p)^*: p - 1 = {p - 1}")
    print(f"Розклад p - 1 на прості множники: {factors}")
    print(f"Прості дільники p - 1: {prime_divisors}")
    print()

    print(f"Знайдений твірний елемент a = {a}")
    print()

    print("Перевірка критерію:")
    for q in prime_divisors:
        exponent = (p - 1) // q
        value = pow(a, exponent, p)
        print(f"a^(({p} - 1) / {q}) mod {p} = {value}")

    print()

    print("Перевірка кількості різних степенів:")
    print(f"Кількість степенів: {len(powers)}")
    print(f"Кількість різних значень: {len(set(powers))}")

    if len(set(powers)) == p - 1:
        print("Висновок: a справді є твірним елементом GF(p)^*.")
    else:
        print("Висновок: a не є твірним елементом. Щось пішло не так.")

    print()

    if p <= 100:
        print("Степені a modulo p:")
        for i, value in enumerate(powers, start=1):
            print(f"{a}^{i:2d} mod {p} = {value}")


def main() -> None:
    raw = input("Введіть непарне просте число p з бінарною довжиною <= 20: ").strip()

    if not raw:
        p = 23
        print("p не введено, використовую приклад p = 23")
    else:
        p = int(raw)

    a = find_primitive_element(p)
    print_report(p, a)


if __name__ == "__main__":
    main()