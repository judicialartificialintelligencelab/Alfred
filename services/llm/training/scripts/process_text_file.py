import os
import re
import unicodedata


def get_input_file_path():
    """
    Constructs the path to the specific South African Constitutional Court document
    relative to the script's location.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))

    file_path = os.path.join(
        os.path.dirname(script_dir),
        "data",
        "South Africa: Constitutional Court",
        "S v Makwanyane and Another (CCT3_94) [1995] ZACC 3; 1995 (6) BCLR 665; 1995 (3) SA 391; [1996] 2 CHRLD 164; 1995 (2) SACR 1 (6 June 1995).txt",
    )

    return file_path


def clean_word(word):
    """
    Removes ALL types of punctuation and special characters from a word.
    Keeps only letters (no numbers) and discards single-letter words.
    """
    # First, normalize unicode characters
    word = unicodedata.normalize("NFKD", word)

    # Remove any non-letter characters (keeps only a-z and A-Z)
    cleaned = re.sub(r"[^a-zA-Z]", "", word)

    # Return cleaned word only if it's longer than 1 character
    cleaned = cleaned.strip()
    return cleaned if len(cleaned) > 1 else ""


def process_text_file():
    """
    Reads the document, writes all words to lines, then removes duplicates.
    Excludes single-letter words.
    """
    input_file = get_input_file_path()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    temp_file = os.path.join(script_dir, "corpus", "temp.txt")
    final_file = os.path.join(script_dir, "corpus", "processed_makwanyane.txt")

    try:
        # Read the input file and process each word
        with open(input_file, "r", encoding="utf-8") as f:
            text = f.read()

        # Write all words to temporary file
        with open(temp_file, "w", encoding="utf-8") as f:
            for word in text.split():
                cleaned_word = clean_word(word)
                if (
                    cleaned_word
                ):  # Only write non-empty words (and longer than 1 letter)
                    f.write(cleaned_word + "\n")

        # Read all words, remove duplicates, and write to final file
        seen_words = set()
        with open(temp_file, "r", encoding="utf-8") as infile, open(
            final_file, "w", encoding="utf-8"
        ) as outfile:
            for line in infile:
                word = line.strip()
                if word not in seen_words:
                    outfile.write(line)
                    seen_words.add(word)

        # Remove temporary file
        os.remove(temp_file)

        print(
            f"Processing complete. {len(seen_words)} unique words written to {final_file}"
        )
        print("All punctuation, special characters, and numbers have been removed.")
        print("Single-letter words have been discarded.")
        print("Duplicate words have been removed while maintaining original order.")

    except FileNotFoundError:
        print(f"Error: Could not find the input file at '{input_file}'")
        print("Please verify that the file exists and the path is correct.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    process_text_file()
