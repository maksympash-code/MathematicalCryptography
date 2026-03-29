from collections import Counter
from pathlib import Path
import matplotlib.pyplot as plt

ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "input"
OUTPUT_TABLE_FILE = BASE_DIR / "letter_frequencies.txt"
OUTPUT_CHART_FILE = BASE_DIR / "letter_frequencies.png"

ADD_ALPHABET_IF_SOME_LETTERS_MISSING = False

KNOWN_FREQ = {}


def read_text(file_name: Path) -> str:
    if not file_name.exists():
        raise FileNotFoundError(f"Файл не знайдено: {file_name}")
    return file_name.read_text(encoding="utf-8")


def normalize_text(text: str) -> str:
    text = text.lower()
    return "".join(ch for ch in text if ch in ALPHABET)


def prepare_text(text: str) -> str:
    filtered = normalize_text(text)

    if ADD_ALPHABET_IF_SOME_LETTERS_MISSING:
        if any(letter not in filtered for letter in ALPHABET):
            filtered += ALPHABET

    return filtered


def count_letters(text: str) -> tuple[int, dict[str, int], dict[str, float]]:
    counts = Counter(text)
    total = len(text)

    letter_counts = {letter: counts.get(letter, 0) for letter in ALPHABET}

    if total == 0:
        freqs = {letter: 0.0 for letter in ALPHABET}
    else:
        freqs = {letter: letter_counts[letter] / total for letter in ALPHABET}

    return total, letter_counts, freqs


def save_table(total: int, counts: dict[str, int], freqs: dict[str, float], file_name: str) -> None:
    lines = []
    lines.append(f"Загальна кількість літер N = {total}\n")
    lines.append("Літера | Кількість | Частота\n")
    lines.append("-" * 32 + "\n")

    for letter in ALPHABET:
        lines.append(f"{letter:^6} | {counts[letter]:^9} | {freqs[letter]:.6f}\n")

    Path(file_name).write_text("".join(lines), encoding="utf-8")


def print_table(total: int, counts: dict[str, int], freqs: dict[str, float]) -> None:
    print(f"Загальна кількість літер N = {total}")
    print("Літера | Кількість | Частота")
    print("-" * 32)

    for letter in ALPHABET:
        print(f"{letter:^6} | {counts[letter]:^9} | {freqs[letter]:.6f}")


def plot_frequencies(freqs: dict[str, float], file_name: str) -> None:
    letters = list(ALPHABET)
    values = [freqs[letter] for letter in letters]

    plt.figure(figsize=(16, 7))
    plt.bar(letters, values)
    plt.title("Частоти літер української абетки в тексті")
    plt.xlabel("Літери")
    plt.ylabel("Частота")
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig(file_name, dpi=200)
    plt.show()


def compare_with_known(freqs: dict[str, float], known_freq: dict[str, float]) -> None:
    if not known_freq:
        print("\nЕталонні частоти не задані, порівняння пропущено.")
        return

    missing = [letter for letter in ALPHABET if letter not in known_freq]
    if missing:
        print("\nУ словнику KNOWN_FREQ бракує літер:")
        print(", ".join(missing))
        return

    print("\nПорівняння з відомими частотами:")
    print("Літера | Отримана | Відома | Різниця")
    print("-" * 42)

    for letter in ALPHABET:
        current = freqs[letter]
        reference = known_freq[letter]
        diff = abs(current - reference)
        print(f"{letter:^6} | {current:.6f} | {reference:.6f} | {diff:.6f}")

    letters = list(ALPHABET)
    current_values = [freqs[letter] for letter in letters]
    reference_values = [known_freq[letter] for letter in letters]

    x = range(len(letters))
    width = 0.4

    plt.figure(figsize=(16, 7))
    plt.bar([i - width / 2 for i in x], current_values, width=width, label="Мій текст")
    plt.bar([i + width / 2 for i in x], reference_values, width=width, label="Відомі частоти")
    plt.title("Порівняння частот літер")
    plt.xlabel("Літери")
    plt.ylabel("Частота")
    plt.xticks(list(x), letters)
    plt.grid(axis="y", linestyle="--", alpha=0.5)
    plt.legend()
    plt.tight_layout()
    plt.show()


def main() -> None:
    text = read_text(INPUT_FILE)
    prepared_text = prepare_text(text)

    total, counts, freqs = count_letters(prepared_text)

    print_table(total, counts, freqs)
    save_table(total, counts, freqs, OUTPUT_TABLE_FILE)
    plot_frequencies(freqs, OUTPUT_CHART_FILE)
    compare_with_known(freqs, KNOWN_FREQ)


if __name__ == "__main__":
    main()