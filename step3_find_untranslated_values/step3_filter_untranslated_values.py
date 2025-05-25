# cmd prompt ex:
# python step4_filter_untranslated_values.py 
# "C:\Users\wilso\Documents\code\SCRAPEKING\step4_find_untranslated_values\dictionary.json" 
# "C:\Users\wilso\Documents\code\SCRAPEKING\step4_find_untranslated_values\new_values_to_check.txt" 
# "C:\Users\wilso\Documents\code\SCRAPEKING\step4_find_untranslated_values\untranslated_lines.txt"

import json
import argparse
import os

def get_untranslated_new_values_substring_match(dictionary_path, new_values_path, output_path):
    """
    Compares values from a new text file against keys (Chinese terms) in a dictionary.json
    by attempting to "consume" parts of the line with dictionary terms.
    Writes individual characters or short sequences that are not found in the dictionary
    to a new file.

    Args:
        dictionary_path (str): The path to your dictionary.json file.
        new_values_path (str): The path to your new text file with values to check.
        output_path (str): The path where the new file with untranslated values will be saved.
    """
    # Load the existing dictionary keys and sort them by length (descending)
    existing_chinese_terms = []
    try:
        with open(dictionary_path, 'r', encoding='utf-8') as f:
            dictionary = json.load(f)
            # Extract keys (Chinese terms) and sort by length descending
            # This prioritizes matching longer terms first, which is crucial for
            # correct "consumption" of the line.
            existing_chinese_terms = sorted(dictionary.keys(), key=len, reverse=True)
        print(f"Loaded {len(existing_chinese_terms)} existing Chinese terms from '{dictionary_path}', sorted by length.")
    except FileNotFoundError:
        print(f"Error: Dictionary file not found at '{dictionary_path}'. Please check the path.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{dictionary_path}'. Ensure it's valid JSON.")
        return

    # Process the new values file
    all_untranslated_chars_and_substrings = set() # Use a set to store unique untranslated parts
    try:
        with open(new_values_path, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                original_line = line.strip()
                if not original_line:
                    continue

                remaining_line = original_line
                line_untranslated_parts = []

                # We iterate while there's still content in the line to process
                while remaining_line:
                    found_match_in_segment = False
                    best_match_len = 0
                    matched_term = ""

                    # Try to find the longest possible dictionary term at the beginning of remaining_line
                    for term in existing_chinese_terms:
                        if remaining_line.startswith(term):
                            if len(term) > best_match_len:
                                best_match_len = len(term)
                                matched_term = term
                                found_match_in_segment = True
                                # No break here, as we want to find the *longest* match

                    if found_match_in_segment:
                        # If a match is found, "consume" it by removing it from the beginning of remaining_line
                        remaining_line = remaining_line[best_match_len:]
                    else:
                        # If no dictionary term matches the beginning of the remaining_line,
                        # take the first character as an untranslated part.
                        # This assumes single characters are the smallest unit of untranslation.
                        untranslated_char = remaining_line[0]
                        line_untranslated_parts.append(untranslated_char)
                        remaining_line = remaining_line[1:] # Move past this character

                if line_untranslated_parts:
                    # Add unique untranslated parts from this line to the global set
                    for part in line_untranslated_parts:
                        all_untranslated_chars_and_substrings.add(part)

        print(f"Finished processing '{new_values_path}'. Found {len(all_untranslated_chars_and_substrings)} unique untranslated parts.")

    except FileNotFoundError:
        print(f"Error: New values file not found at '{new_values_path}'. Please check the path.")
        return

    # Write the unique untranslated parts to the output file, one per line
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            # Sort for consistent output, though a set doesn't guarantee order
            sorted_untranslated_parts = sorted(list(all_untranslated_chars_and_substrings), key=len, reverse=True)
            for part_to_write in sorted_untranslated_parts:
                f.write(part_to_write + '\n')
        print(f"Successfully wrote unique untranslated parts to '{output_path}'.")
    except IOError:
        print(f"Error: Could not write to output file '{output_path}'.")

# --- How to Use from Command Prompt ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find untranslated characters/substrings in a text file by comparing against a JSON dictionary.")
    parser.add_argument("dictionary_file", help="The path to your dictionary.json file.")
    parser.add_argument("new_values_file", help="The path to your new text file with values to check.")
    parser.add_argument("output_file", help="The path where the new file with untranslated values will be saved.")

    args = parser.parse_args()

    dictionary_path = args.dictionary_file
    new_text_file_path = args.new_values_file
    output_new_file_path = args.output_file

    get_untranslated_new_values_substring_match(dictionary_path, new_text_file_path, output_new_file_path)