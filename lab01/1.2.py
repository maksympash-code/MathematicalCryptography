UKR_ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"

UKR_INDEX = {ch: i for i, ch in enumerate(UKR_ALPHABET)}


def normalize_ukrainian(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.lower() in UKR_ALPHABET)


def shift_add_ukr(a: str, b: str) -> str:
    return UKR_ALPHABET[(UKR_INDEX[a] + UKR_INDEX[b]) % len(UKR_ALPHABET)]


def shift_sub_ukr(a: str, b: str) -> str:
    return UKR_ALPHABET[(UKR_INDEX[a] - UKR_INDEX[b]) % len(UKR_ALPHABET)]


def vigenere_encrypt_ukr(plaintext: str, key: str) -> str:
    key_letters = list(normalize_ukrainian(key))

    if not key_letters:
        raise ValueError("Ключ для шифру Віженера не може бути порожнім.")

    result = []
    key_index = 0

    for ch in plaintext:
        low = ch.lower()

        if low in UKR_ALPHABET:
            k = key_letters[key_index % len(key_letters)]
            enc = shift_add_ukr(low, k)
            result.append(enc.upper() if ch.isupper() else enc)
            key_index += 1
        else:
            result.append(ch)

    return "".join(result)


def vigenere_decrypt_ukr(ciphertext: str, key: str) -> str:
    key_letters = list(normalize_ukrainian(key))

    if not key_letters:
        raise ValueError("Ключ для шифру Віженера не може бути порожнім.")

    result = []
    key_index = 0

    for ch in ciphertext:
        low = ch.lower()

        if low in UKR_ALPHABET:
            k = key_letters[key_index % len(key_letters)]
            dec = shift_sub_ukr(low, k)
            result.append(dec.upper() if ch.isupper() else dec)
            key_index += 1
        else:
            result.append(ch)

    return "".join(result)


def main() -> None:
    print("=== Шифр Віженера ===")
    key_vig = "ключ"
    text_vig = "Привіт, криптографіє!"
    cipher_vig = vigenere_encrypt_ukr(text_vig, key_vig)
    plain_vig = vigenere_decrypt_ukr(cipher_vig, key_vig)

    print("Відкритий текст :", text_vig)
    print("Ключ            :", key_vig)
    print("Шифротекст      :", cipher_vig)
    print("Розшифрування   :", plain_vig)
    print()


if __name__ == "__main__":
    main()