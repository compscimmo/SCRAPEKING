import os
import re
import traceback
import argparse
import string
import unicodedata

def clean_text(text):
    """
    Removes English letters, punctuation, numbers, math symbols, and emojis.
    Replaces removed characters with a space.
    """
    cleaned_chars = []
    for char in text:
        # Remove English letters
        if 'a' <= char <= 'z' or 'A' <= char <= 'Z':
            cleaned_chars.append(' ')
            continue

        # Remove punctuation
        if char in string.punctuation:
            cleaned_chars.append(' ')
            continue

        # Remove numbers
        if char.isdigit():
            cleaned_chars.append(' ')
            continue

        # Remove math symbols
        # This covers a broad range of unicode math symbols
        if unicodedata.category(char).startswith('Sm') or \
           unicodedata.category(char).startswith('N'): # 'N' for Number, covers various number forms
            cleaned_chars.append(' ')
            continue

        # Remove emojis (common unicode ranges and categories for emojis)
        # This is a heuristic and might not catch all emojis, but covers many.
        if 0x1F600 <= ord(char) <= 0x1F64F or \
           0x1F300 <= ord(char) <= 0x1F5FF or \
           0x1F680 <= ord(char) <= 0x1F6FF or \
           0x1F1E0 <= ord(char) <= 0x1F1FF or \
           0x2600 <= ord(char) <= 0x26FF or \
           0x2700 <= ord(char) <= 0x27BF:
            cleaned_chars.append(' ')
            continue
        
        # Specific examples you provided
        if char in ['【', '】', '，', '（', '）', '？', '+', '%', '.', '/', '👇🏻', '👇', '①', '②', '👆🏻', '🐭', '💡', '。', '⚠️', '🐸', '!', '：', '↓', '④', '③']:
            cleaned_chars.append(' ')
            continue

        cleaned_chars.append(char)

    # Join and then split by spaces to handle multiple spaces from removals
    # Then join with a single space to normalize
    return ' '.join("".join(cleaned_chars).split())


def extract_and_format_data(input_dir, output_file_path):
    """
    Reads through all .txt files in the specified input directory,
    extracts specific data values, filters out 'N/A' entries,
    removes English, punctuation, numbers, math symbols, and emojis,
    and stores them in a set to automatically handle duplicates.
    Finally, it writes the unique, space-separated values to a single output file.
    """
    # Use a set to store extracted values to automatically handle duplicates
    all_extracted_values = set()

    # Define the regex patterns for the data points we want to extract
    patterns = {
        "alert_text": re.compile(r'^\s*Alert Text: (.*)$'),
        "pokemon_name": re.compile(r'^\s*pokemon_name: (.*)$'),
        "red_bold_text": re.compile(r'^\s*red_bold_text: (.*)$'),
        "warning_badge_text": re.compile(r'^\s*warning_badge_text: (.*)$'),
        "nested_header_label_text": re.compile(r'^\s*nested_header_label_text \(collapsed\): (.*)$'),
        "nested_header_operate_text": re.compile(r'^\s*nested_header_operate_text \(collapsed\): (.*)$'),
        "nested_trick_text": re.compile(r'^\s*nested_trick_text \(expanded\): (.*)$'),
        "nested_body_label_text": re.compile(r'^\s*nested_body_label_text \(expanded\): (.*)$'),
        "nested_body_operate_text": re.compile(r'^\s*nested_body_operate_text \(expanded\): (.*)$'),
        "nested_warning_badge_text": re.compile(r'^\s*nested_warning_badge_text \(expanded\): (.*)$')
    }

    print(f"Starting data extraction from files in: {input_dir}")

    if not os.path.exists(input_dir):
        print(f"Error: Input directory '{input_dir}' not found.")
        return

    # Iterate through all files in the specified directory
    for filename in os.listdir(input_dir):
        if filename.startswith("pokeking_icu_home_X_") and filename.endswith(".txt"):
            filepath = os.path.join(input_dir, filename)
            print(f"    Processing file: {filename}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()

                        for key, pattern in patterns.items():
                            match = pattern.match(line)
                            if match:
                                value = match.group(1).strip()
                                # Only add values that are not "N/A"
                                if value and value.upper() != 'N/A':
                                    cleaned_value = clean_text(value)
                                    # Split the cleaned value by spaces and add each part to the set
                                    # This handles the "make a column for every space separated value" requirement
                                    if cleaned_value: # Only add if something remains after cleaning
                                        for item in cleaned_value.split():
                                            if item: # Ensure no empty strings are added
                                                all_extracted_values.add(item)
                                break

            except Exception as e:
                print(f"    Error processing file {filename}: {e}")
                traceback.print_exc()

    # Join all collected unique values with a newline to put each on its own "column" (line)
    final_output_string = "\n".join(sorted(list(all_extracted_values)))

    # Create the output directory if it doesn't exist
    output_dir = os.path.dirname(output_file_path)
    if output_dir and not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")
        except OSError as e:
            print(f"Error creating output directory '{output_dir}': {e}")
            traceback.print_exc()
            return

    # Write the formatted data to the output file
    try:
        with open(output_file_path, 'w', encoding='utf-8') as f:
            f.write(final_output_string)
        print(f"\nSuccessfully extracted and saved unique data to: {output_file_path}")
    except Exception as e:
        print(f"Error writing to output file '{output_file_path}': {e}")
        traceback.print_exc()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Extracts specific text values from Pokeking scraped data files and saves unique, cleaned values to an output file."
    )

    parser.add_argument(
        "-i", "--input_dir",
        type=str,
        default="pokeking_scraped_data_by_x", # Default input directory
        help="The directory containing the .txt files with scraped Pokeking data."
    )

    parser.add_argument(
        "-o", "--output_filename",
        type=str,
        default="extracted_pokeking_values.txt", # Default name for the output file
        help="The name of the file where unique extracted values will be saved (e.g., 'my_unique_data.txt'). This file will be saved in the input directory."
    )

    args = parser.parse_args()

    # Construct the full output file path to be inside the input directory
    full_output_file_path = os.path.join(args.input_dir, args.output_filename)

    # Call your function with the input directory and the newly constructed full output path
    extract_and_format_data(args.input_dir, full_output_file_path)