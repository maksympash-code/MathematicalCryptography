UKR_ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
ENG_ALPHABET_25 = "abcdefghiklmnopqrstuvwxyz"

UKR_INDEX = {ch: i for i, ch in enumerate(UKR_ALPHABET)}
ENG25_INDEX = {ch: i for i, ch in enumerate(ENG_ALPHABET_25)}


def normalize_ukrainian(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.lower() in UKR_ALPHABET)


def normalize_english_25(text: str) -> str:
    result = []

    for ch in text.lower():
        if "a" <= ch <= "z":
            if ch == "j":
                ch = "i"
            if ch in ENG_ALPHABET_25:
                result.append(ch)

    return "".join(result)


def shift_add_ukr(a: str, b: str) -> str:
    return UKR_ALPHABET[(UKR_INDEX[a] + UKR_INDEX[b]) % len(UKR_ALPHABET)]


def shift_sub_ukr(a: str, b: str) -> str:
    return UKR_ALPHABET[(UKR_INDEX[a] - UKR_INDEX[b]) % len(UKR_ALPHABET)]


# =========================
# 1. Шифр підстановки
# =========================

def validate_substitution_key(key: str, alphabet: str = UKR_ALPHABET) -> str:
    cleaned = "".join(ch.lower() for ch in key if ch.lower() in alphabet)

    if len(cleaned) != len(alphabet):
        raise ValueError(
            f"Ключ повинен містити рівно {len(alphabet)} різних літер алфавіту."
        )

    if set(cleaned) != set(alphabet):
        raise ValueError("Ключ повинен бути перестановкою всіх літер алфавіту.")

    return cleaned


def encrypt_substitution(plaintext: str, key: str, alphabet: str = UKR_ALPHABET) -> str:
    key = validate_substitution_key(key, alphabet)

    lower_map = {a: b for a, b in zip(alphabet, key)}
    upper_map = {a.upper(): b.upper() for a, b in zip(alphabet, key)}

    result = []

    for ch in plaintext:
        if ch in lower_map:
            result.append(lower_map[ch])
        elif ch in upper_map:
            result.append(upper_map[ch])
        else:
            result.append(ch)

    return "".join(result)


def decrypt_substitution(ciphertext: str, key: str, alphabet: str = UKR_ALPHABET) -> str:
    key = validate_substitution_key(key, alphabet)

    lower_map = {b: a for a, b in zip(alphabet, key)}
    upper_map = {b.upper(): a.upper() for a, b in zip(alphabet, key)}

    result = []

    for ch in ciphertext:
        if ch in lower_map:
            result.append(lower_map[ch])
        elif ch in upper_map:
            result.append(upper_map[ch])
        else:
            result.append(ch)

    return "".join(result)


# =========================
# 2. Шифр з автоключем
# =========================

def autokey_encrypt_ukr(plaintext: str, key: str) -> str:
    key_letters = list(normalize_ukrainian(key))

    if not key_letters:
        raise ValueError("Ключ для автоключового шифру не може бути порожнім.")

    stream = key_letters[:]
    stream_index = 0
    result = []

    for ch in plaintext:
        low = ch.lower()

        if low in UKR_ALPHABET:
            k = stream[stream_index]
            enc = shift_add_ukr(low, k)
            result.append(enc.upper() if ch.isupper() else enc)

            stream.append(low)
            stream_index += 1
        else:
            result.append(ch)

    return "".join(result)


def autokey_decrypt_ukr(ciphertext: str, key: str) -> str:
    key_letters = list(normalize_ukrainian(key))

    if not key_letters:
        raise ValueError("Ключ для автоключового шифру не може бути порожнім.")

    stream = key_letters[:]
    stream_index = 0
    result = []

    for ch in ciphertext:
        low = ch.lower()

        if low in UKR_ALPHABET:
            k = stream[stream_index]
            dec = shift_sub_ukr(low, k)
            result.append(dec.upper() if ch.isupper() else dec)

            stream.append(dec)
            stream_index += 1
        else:
            result.append(ch)

    return "".join(result)


# =========================
# 3. Шифр чотирьох квадратів
# =========================

def build_square_25(square_text: str):
    cleaned = normalize_english_25(square_text)

    if len(cleaned) != 25:
        raise ValueError("Кожен квадрат повинен містити рівно 25 літер.")

    if len(set(cleaned)) != 25:
        raise ValueError("У квадраті всі 25 літер мають бути різними.")

    if set(cleaned) != set(ENG_ALPHABET_25):
        raise ValueError("Квадрат повинен містити всі літери англійського алфавіту без j.")

    grid = [list(cleaned[i:i + 5]) for i in range(0, 25, 5)]
    pos = {}

    for r in range(5):
        for c in range(5):
            pos[grid[r][c]] = (r, c)

    return grid, pos


def keyword_square_25(keyword: str) -> str:
    seen = set()
    result = []

    for ch in normalize_english_25(keyword) + ENG_ALPHABET_25:
        if ch not in seen:
            seen.add(ch)
            result.append(ch)

    return "".join(result)


def four_square_encrypt(
    plaintext: str,
    top_left: str,
    top_right: str,
    bottom_left: str,
    bottom_right: str,
    pad: str = "x"
) -> str:
    tl_grid, tl_pos = build_square_25(top_left)
    tr_grid, _ = build_square_25(top_right)
    bl_grid, _ = build_square_25(bottom_left)
    br_grid, br_pos = build_square_25(bottom_right)

    text = normalize_english_25(plaintext)

    if len(text) % 2 == 1:
        text += pad

    result = []

    for i in range(0, len(text), 2):
        a = text[i]
        b = text[i + 1]

        r1, c1 = tl_pos[a]
        r2, c2 = br_pos[b]

        result.append(tr_grid[r1][c2])
        result.append(bl_grid[r2][c1])

    return "".join(result)


def four_square_decrypt(
    ciphertext: str,
    top_left: str,
    top_right: str,
    bottom_left: str,
    bottom_right: str
) -> str:
    tl_grid, _ = build_square_25(top_left)
    tr_grid, tr_pos = build_square_25(top_right)
    bl_grid, bl_pos = build_square_25(bottom_left)
    br_grid, _ = build_square_25(bottom_right)

    text = normalize_english_25(ciphertext)

    if len(text) % 2 == 1:
        raise ValueError("Довжина криптотексту для шифру чотирьох квадратів повинна бути парною.")

    result = []

    for i in range(0, len(text), 2):
        a = text[i]
        b = text[i + 1]

        r1, c2 = tr_pos[a]
        r2, c1 = bl_pos[b]

        result.append(tl_grid[r1][c1])
        result.append(br_grid[r2][c2])

    return "".join(result)


# =========================
# Демонстрація роботи
# =========================

def main() -> None:
    print("=== 1. Шифр підстановки ===")
    substitution_key = UKR_ALPHABET[::-1]
    text1 = "Привіт, криптографіє!"
    cipher1 = encrypt_substitution(text1, substitution_key)
    plain1 = decrypt_substitution(cipher1, substitution_key)

    print("Відкритий текст :", text1)
    print("Ключ            :", substitution_key)
    print("Шифротекст      :", cipher1)
    print("Розшифрування   :", plain1)
    print()

    print("=== 2. Шифр з автоключем ===")
    key2 = "зима"
    text2 = "білі мухи налетіли"
    cipher2 = autokey_encrypt_ukr(text2, key2)
    plain2 = autokey_decrypt_ukr(cipher2, key2)

    print("Відкритий текст :", text2)
    print("Ключ            :", key2)
    print("Шифротекст      :", cipher2)
    print("Розшифрування   :", plain2)
    print()

    print("=== 3. Шифр чотирьох квадратів ===")
    top_left = "kingdomabcefhlpqrstuvwxyz"
    top_right = "vqeokwrfmixshanytlbgzupcd"
    bottom_left = "zyxwvutsrqplhfecbamodgnik"
    bottom_right = "dcpuzgbltynahsximfrwkoeqv"

    text3 = "university"
    cipher3 = four_square_encrypt(
        text3,
        top_left,
        top_right,
        bottom_left,
        bottom_right
    )
    plain3 = four_square_decrypt(
        cipher3,
        top_left,
        top_right,
        bottom_left,
        bottom_right
    )

    print("Відкритий текст :", text3)
    print("Шифротекст      :", cipher3)
    print("Розшифрування   :", plain3)
    print()

    print("=== 4. Дешифрування прикладу ===")
    sample_cipher = "sknromra"
    sample_plain = four_square_decrypt(
        sample_cipher,
        top_left,
        top_right,
        bottom_left,
        bottom_right
    )

    print("Криптотекст     :", sample_cipher)
    print("Розшифрування   :", sample_plain)


if __name__ == "__main__":
    main()