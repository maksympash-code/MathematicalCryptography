from __future__ import annotations

from math import isqrt
from pathlib import Path


REPORT_FILE = Path("task_5_2_report.txt")


def is_prime(n: int) -> bool:
    """
    Перевіряє, чи є n простим.
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
    Розклад числа n на прості множники.
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
    """
    if not (1 <= a <= p - 1):
        return False

    for q in prime_divisors:
        if pow(a, (p - 1) // q, p) == 1:
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


def ceil_sqrt(n: int) -> int:
    """
    Обчислює ceil(sqrt(n)).
    """
    root = isqrt(n)

    if root * root == n:
        return root

    return root + 1


def element_order(a: int, p: int) -> int:
    """
    Знаходить порядок елемента a в GF(p)^*.

    Порядок — це найменше додатне r таке, що:

        a^r ≡ 1 mod p
    """
    if not (1 <= a < p):
        raise ValueError("a має бути в діапазоні 1 <= a < p.")

    if not is_prime(p):
        raise ValueError("p має бути простим числом.")

    group_order = p - 1
    factors = factorize(group_order)

    order = group_order

    for q in factors:
        while order % q == 0 and pow(a, order // q, p) == 1:
            order //= q

    return order


def baby_step_giant_step(a: int, b: int, p: int, order: int | None = None) -> dict:
    """
    Розв'язує задачу дискретного логарифма:

        a^x ≡ b mod p

    у групі G = <a>.

    Повертає словник із:
        x,
        m,
        baby_steps,
        giant_steps,
        order.
    """
    if not is_prime(p):
        raise ValueError("p має бути простим числом.")

    if not (1 <= a < p):
        raise ValueError("a має бути в діапазоні 1 <= a < p.")

    if not (1 <= b < p):
        raise ValueError("b має бути в діапазоні 1 <= b < p.")

    if order is None:
        order = element_order(a, p)

    # Перевіряємо, що b справді належить групі <a>.
    # Якщо b лежить у <a>, тоді b^order ≡ 1 mod p.
    if pow(b, order, p) != 1:
        raise ValueError("b не належить групі G = <a>, тому дискретний логарифм не існує.")

    m = ceil_sqrt(order)

    baby_steps: dict[int, int] = {}

    current = 1

    for j in range(m):
        if current not in baby_steps:
            baby_steps[current] = j

        current = (current * a) % p

    # factor = a^(-m) mod p
    a_inverse = pow(a, -1, p)
    factor = pow(a_inverse, m, p)

    giant_steps = []

    gamma = b

    for i in range(m + 1):
        giant_steps.append((i, gamma))

        if gamma in baby_steps:
            j = baby_steps[gamma]
            x = i * m + j

            if x < order and pow(a, x, p) == b:
                return {
                    "x": x,
                    "m": m,
                    "order": order,
                    "baby_steps": baby_steps,
                    "giant_steps": giant_steps,
                    "found_i": i,
                    "found_j": j,
                }

        gamma = (gamma * factor) % p

    raise ValueError("Дискретний логарифм не знайдено.")


def brute_force_discrete_log(a: int, b: int, p: int, order: int) -> int | None:
    """
    Повільна перевірка результату.
    Перебирає x від 0 до order - 1.
    """
    current = 1

    for x in range(order):
        if current == b:
            return x

        current = (current * a) % p

    return None


def build_report(p: int, a: int, b: int, result: dict, brute_x: int | None) -> str:
    x = result["x"]
    m = result["m"]
    order = result["order"]
    found_i = result["found_i"]
    found_j = result["found_j"]

    lines = []

    lines.append("Лабораторна робота 5.2 — алгоритм малих і великих кроків\n")
    lines.append("=" * 75 + "\n\n")

    lines.append("Задача дискретного логарифма:\n")
    lines.append(f"Знайти x з рівняння: {a}^x ≡ {b} mod {p}\n\n")

    lines.append("Параметри групи:\n")
    lines.append(f"p = {p}\n")
    lines.append(f"Бінарна довжина p: {p.bit_length()}\n")
    lines.append(f"a = {a}\n")
    lines.append(f"b = {b}\n")
    lines.append(f"Порядок групи G = <a>: {order}\n")
    lines.append(f"m = ceil(sqrt(order)) = {m}\n\n")

    lines.append("Результат алгоритму:\n")
    lines.append(f"Знайдено збіг при i = {found_i}, j = {found_j}\n")
    lines.append(f"x = i*m + j = {found_i}*{m} + {found_j} = {x}\n")
    lines.append(f"Перевірка: pow(a, x, p) = {pow(a, x, p)}\n")
    lines.append(f"Очікуване b = {b}\n")
    lines.append(f"Результат правильний: {pow(a, x, p) == b}\n\n")

    lines.append("Перевірка повним перебором:\n")
    lines.append(f"x, знайдений brute force: {brute_x}\n")
    lines.append(f"Збігається з BSGS: {brute_x == x}\n\n")

    lines.append("Baby steps: значення a^j mod p\n")
    sorted_baby = sorted(result["baby_steps"].items(), key=lambda item: item[1])

    for value, j in sorted_baby:
        lines.append(f"j = {j:3d}, a^j mod p = {value}\n")

    lines.append("\nGiant steps: значення b * a^(-i*m) mod p\n")

    for i, gamma in result["giant_steps"]:
        lines.append(f"i = {i:3d}, gamma = {gamma}\n")

    lines.append("\nВисновок:\n")
    lines.append(
        "Було реалізовано алгоритм малих і великих кроків для знаходження "
        "дискретного логарифма в групі G = <a>. Алгоритм зменшує складність "
        "порівняно з повним перебором з O(N) до O(sqrt(N)) за часом і пам'яттю.\n"
    )

    return "".join(lines)


def print_result(p: int, a: int, b: int, result: dict, brute_x: int | None) -> None:
    x = result["x"]

    print("=== Лабораторна робота 5.2 ===")
    print("Алгоритм малих і великих кроків")
    print()

    print(f"p = {p}")
    print(f"a = {a}")
    print(f"b = {b}")
    print(f"Порядок G = <a>: {result['order']}")
    print(f"m = ceil(sqrt(order)) = {result['m']}")
    print()

    print(f"Знайдено x = {x}")
    print(f"Перевірка: {a}^{x} mod {p} = {pow(a, x, p)}")
    print(f"b = {b}")
    print(f"Результат правильний: {pow(a, x, p) == b}")
    print()

    print(f"Перевірка brute force: x = {brute_x}")
    print(f"Brute force збігається з BSGS: {brute_x == x}")


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

    raw_a = input(f"Введіть генератор a [за замовчуванням {default_a}]: ").strip()

    if raw_a:
        a = int(raw_a)
    else:
        a = default_a

    order = element_order(a, p)

    print(f"Порядок елемента a: {order}")

    raw_b = input("Введіть b для рівняння a^x = b mod p [за замовчуванням a^6]: ").strip()

    if raw_b:
        b = int(raw_b)
    else:
        b = pow(a, 6, p)

    result = baby_step_giant_step(a, b, p, order)
    brute_x = brute_force_discrete_log(a, b, p, order)

    print_result(p, a, b, result, brute_x)

    report = build_report(p, a, b, result, brute_x)
    REPORT_FILE.write_text(report, encoding="utf-8")

    print()
    print(f"Звіт збережено у файл: {REPORT_FILE.resolve()}")


if __name__ == "__main__":
    main()