from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt

UKR_ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
ALPHABET_SIZE = len(UKR_ALPHABET)
INDEX = {ch: i for i, ch in enumerate(UKR_ALPHABET)}

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "input"
REFERENCE_TEXT_FILE = BASE_DIR / "reference_text.txt"
CIPHERTEXT_FILE = BASE_DIR / "ciphertext.txt"
DECRYPTED_FILE = BASE_DIR / "decrypted.txt"
REPORT_FILE = BASE_DIR / "analysis_report.txt"
IC_CHART_FILE = BASE_DIR / "ic_chart.png"

KEY = "мехмат"
MAX_KEY_LENGTH = 20
TOP_KEY_LENGTHS = 3

STANDARD_FREQ = {
    "а": 0.080120, "б": 0.016710, "в": 0.057412, "г": 0.011997, "ґ": 0.000000,
    "д": 0.036418, "е": 0.044130, "є": 0.013282, "ж": 0.009854, "з": 0.025278,
    "и": 0.068552, "і": 0.050985, "ї": 0.001714, "й": 0.013710, "к": 0.032562,
    "л": 0.033419, "м": 0.024850, "н": 0.070266, "о": 0.089546, "п": 0.030848,
    "р": 0.040703, "с": 0.044559, "т": 0.064267, "у": 0.034276, "ф": 0.002142,
    "х": 0.010283, "ц": 0.004713, "ч": 0.016710, "ш": 0.008569, "щ": 0.005998,
    "ь": 0.020566, "ю": 0.012425, "я": 0.023136,
}


def normalize_text(text: str) -> str:
    return "".join(ch.lower() for ch in text if ch.lower() in INDEX)


def read_text(file_path: Path) -> str:
    if not file_path.exists():
        raise FileNotFoundError(f"Файл не знайдено: {file_path}")
    return file_path.read_text(encoding="utf-8")


def save_text(file_path: Path, text: str) -> None:
    file_path.write_text(text, encoding="utf-8")


def normalize_frequencies(freq: dict[str, float]) -> dict[str, float]:
    total = sum(freq.values())
    return {ch: freq[ch] / total for ch in UKR_ALPHABET}


def get_reference_frequencies() -> tuple[dict[str, float], str]:
    if REFERENCE_TEXT_FILE.exists():
        reference_text = normalize_text(read_text(REFERENCE_TEXT_FILE))
        if len(reference_text) >= 100:
            counts = Counter(reference_text)
            total = len(reference_text)
            freq = {ch: counts.get(ch, 0) / total for ch in UKR_ALPHABET}
            return freq, f"reference_text.txt (N = {total})"

    return normalize_frequencies(STANDARD_FREQ), "вбудовані стандартні частоти"


def shift_encrypt(plain_char: str, key_char: str) -> str:
    return UKR_ALPHABET[(INDEX[plain_char] + INDEX[key_char]) % ALPHABET_SIZE]


def shift_decrypt(cipher_char: str, key_char: str) -> str:
    return UKR_ALPHABET[(INDEX[cipher_char] - INDEX[key_char]) % ALPHABET_SIZE]


def vigenere_encrypt(plaintext: str, key: str) -> str:
    plaintext = normalize_text(plaintext)
    key = normalize_text(key)

    if not key:
        raise ValueError("Ключ не може бути порожнім.")

    result = []

    for i, ch in enumerate(plaintext):
        result.append(shift_encrypt(ch, key[i % len(key)]))

    return "".join(result)


def vigenere_decrypt(ciphertext: str, key: str) -> str:
    ciphertext = normalize_text(ciphertext)
    key = normalize_text(key)

    if not key:
        raise ValueError("Ключ не може бути порожнім.")

    result = []

    for i, ch in enumerate(ciphertext):
        result.append(shift_decrypt(ch, key[i % len(key)]))

    return "".join(result)


def index_of_coincidence(text: str) -> float:
    text = normalize_text(text)
    n = len(text)

    if n < 2:
        return 0.0

    counts = Counter(text)
    numerator = sum(count * (count - 1) for count in counts.values())
    denominator = n * (n - 1)

    return ALPHABET_SIZE * numerator / denominator


def average_ic_for_key_length(ciphertext: str, key_length: int) -> float:
    groups = [ciphertext[i::key_length] for i in range(key_length)]
    values = [index_of_coincidence(group) for group in groups]
    return sum(values) / len(values)


def compute_ic_scores(ciphertext: str, max_key_length: int) -> dict[int, float]:
    scores = {}

    for key_length in range(1, max_key_length + 1):
        scores[key_length] = average_ic_for_key_length(ciphertext, key_length)

    return scores


def choose_top_key_lengths(scores: dict[int, float], top_n: int = 3) -> list[int]:
    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    return [key_length for key_length, _ in ranked[:top_n]]


def chi_square_stat(text: str, expected_freq: dict[str, float]) -> float:
    text = normalize_text(text)
    n = len(text)
    counts = Counter(text)

    value = 0.0

    for ch in UKR_ALPHABET:
        observed = counts.get(ch, 0)
        expected = n * expected_freq[ch]

        if expected > 0:
            value += (observed - expected) ** 2 / expected

    return value


def decrypt_group_with_shift(group: str, shift: int) -> str:
    return "".join(UKR_ALPHABET[(INDEX[ch] - shift) % ALPHABET_SIZE] for ch in group)


def guess_key_char(group: str, expected_freq: dict[str, float]) -> tuple[str, float]:
    best_shift = 0
    best_score = float("inf")

    for shift in range(ALPHABET_SIZE):
        decrypted_group = decrypt_group_with_shift(group, shift)
        score = chi_square_stat(decrypted_group, expected_freq)

        if score < best_score:
            best_score = score
            best_shift = shift

    return UKR_ALPHABET[best_shift], best_score


def guess_key(ciphertext: str, key_length: int, expected_freq: dict[str, float]) -> tuple[str, list[float]]:
    key_chars = []
    scores = []

    for i in range(key_length):
        group = ciphertext[i::key_length]
        key_char, score = guess_key_char(group, expected_freq)
        key_chars.append(key_char)
        scores.append(score)

    return "".join(key_chars), scores


def plot_ic_scores(scores: dict[int, float], output_file: Path) -> None:
    x = list(scores.keys())
    y = list(scores.values())

    plt.figure(figsize=(11, 6))
    plt.bar(x, y)
    plt.xlabel("Довжина ключа")
    plt.ylabel("Середній IC")
    plt.title("Оцінка довжини ключа за Index of Coincidence")
    plt.xticks(x)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(output_file, dpi=200)
    plt.show()


def compress_repeated_key(key: str) -> str:
    for size in range(1, len(key) + 1):
        if len(key) % size == 0:
            block = key[:size]
            if block * (len(key) // size) == key:
                return block
    return key


def build_report(
    plaintext: str,
    ciphertext: str,
    ic_scores: dict[int, float],
    top_lengths: list[int],
    analysis_results: list[dict],
    reference_source: str,
) -> str:
    lines = []

    lines.append("Лабораторна робота 1.3 — криптоаналіз шифру Віженера\n")
    lines.append("=" * 65 + "\n\n")

    lines.append(f"Довжина очищеного відкритого тексту: {len(plaintext)}\n")
    lines.append(f"Використаний ключ для шифрування: {KEY}\n")
    lines.append(f"Довжина використаного ключа: {len(normalize_text(KEY))}\n")
    lines.append(f"Джерело еталонних частот: {reference_source}\n\n")

    lines.append("Середні значення IC для довжин ключа:\n")
    for k, value in ic_scores.items():
        lines.append(f"{k:2d}: {value:.6f}\n")

    lines.append("\n")
    lines.append(f"Топ-{len(top_lengths)} довжин ключа: {', '.join(map(str, top_lengths))}\n\n")

    for i, result in enumerate(analysis_results, start=1):
        lines.append(f"=== Кандидат {i} ===\n")
        lines.append(f"Довжина ключа: {result['key_length']}\n")
        lines.append(f"Відновлений ключ: {result['guessed_key']}\n")
        lines.append(f"Стиснений ключ: {result['short_key']}\n")
        lines.append(f"Розшифрування повністю збігається: {result['decrypted_text'] == plaintext}\n")
        lines.append("Значення хі-квадрат для літер ключа:\n")

        for j, score in enumerate(result["key_scores"], start=1):
            lines.append(f"позиція {j}: {score:.6f}\n")

        lines.append("\n")
        lines.append("Перші 300 символів розшифрованого тексту:\n")
        lines.append(result["decrypted_text"][:300] + "\n\n")

    lines.append("Перші 300 символів відкритого тексту:\n")
    lines.append(plaintext[:300] + "\n\n")

    lines.append("Перші 300 символів криптотексту:\n")
    lines.append(ciphertext[:300] + "\n")

    return "".join(lines)


def main() -> None:
    raw_plaintext = read_text(INPUT_FILE)
    plaintext = normalize_text(raw_plaintext)

    if len(plaintext) < 200:
        raise ValueError(
            "Текст занадто короткий. Для нормального криптоаналізу краще взяти хоча б 200-300 літер."
        )

    reference_freq, reference_source = get_reference_frequencies()

    ciphertext = vigenere_encrypt(plaintext, KEY)
    save_text(CIPHERTEXT_FILE, ciphertext)

    ic_scores = compute_ic_scores(ciphertext, MAX_KEY_LENGTH)
    top_lengths = choose_top_key_lengths(ic_scores, TOP_KEY_LENGTHS)

    analysis_results = []

    for idx, key_length in enumerate(top_lengths, start=1):
        guessed_key, key_scores = guess_key(ciphertext, key_length, reference_freq)
        short_key = compress_repeated_key(guessed_key)
        decrypted_text = vigenere_decrypt(ciphertext, guessed_key)

        output_file = BASE_DIR / f"decrypted_top_{idx}.txt"
        save_text(output_file, decrypted_text)

        analysis_results.append({
            "key_length": key_length,
            "guessed_key": guessed_key,
            "short_key": short_key,
            "key_scores": key_scores,
            "decrypted_text": decrypted_text,
            "output_file": output_file,
        })

    report = build_report(
        plaintext=plaintext,
        ciphertext=ciphertext,
        ic_scores=ic_scores,
        top_lengths=top_lengths,
        analysis_results=analysis_results,
        reference_source=reference_source,
    )
    save_text(REPORT_FILE, report)

    print("=== РЕЗУЛЬТАТ ===")
    print(f"Довжина тексту: {len(plaintext)}")
    print(f"Справжній ключ: {normalize_text(KEY)}")
    print(f"Топ-{TOP_KEY_LENGTHS} довжин ключа: {top_lengths}")
    print()

    for i, result in enumerate(analysis_results, start=1):
        print(f"--- Кандидат {i} ---")
        print(f"Оцінена довжина ключа: {result['key_length']}")
        print(f"Відновлений ключ: {result['guessed_key']}")
        print(f"Стиснений ключ: {result['short_key']}")
        print(f"Розшифрування збігається з оригіналом: {result['decrypted_text'] == plaintext}")
        print("Перші 200 символів дешифрування:")
        print(result["decrypted_text"][:200])
        print()

    print("IC для довжин ключа:")
    for k, value in ic_scores.items():
        print(f"{k:2d}: {value:.6f}")

    plot_ic_scores(ic_scores, IC_CHART_FILE)


if __name__ == "__main__":
    main()