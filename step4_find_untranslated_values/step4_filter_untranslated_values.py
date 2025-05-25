# cmd prompt ex:
# python step4_filter_untranslated_values.py 
# "C:\Users\wilso\Documents\code\SCRAPEKING\step4_find_untranslated_values\dictionary.json" 
# "C:\Users\wilso\Documents\code\SCRAPEKING\step4_find_untranslated_values\new_values_to_check.txt" 
# "C:\Users\wilso\Documents\code\SCRAPEKING\step4_find_untranslated_values\untranslated_lines.txt"

import json
import argparse # Import the argparse module
import os # Keep os for potential path manipulation, though argparse handles much of it now

def get_untranslated_new_values_substring_match(dictionary_path, new_values_path, output_path):
    """
    Compares values from a new text file against keys (Chinese terms) in a dictionary.json
    by looking for substrings, prioritizing longer dictionary terms.
    Writes lines that do not contain any significant translated term to a new file.

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
            existing_chinese_terms = sorted(dictionary.keys(), key=len, reverse=True)
        print(f"Loaded {len(existing_chinese_terms)} existing Chinese terms from '{dictionary_path}', sorted by length.")
    except FileNotFoundError:
        print(f"Error: Dictionary file not found at '{dictionary_path}'. Please check the path.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{dictionary_path}'. Ensure it's valid JSON.")
        return

    # Process the new values file
    untranslated_lines = []
    try:
        with open(new_values_path, 'r', encoding='utf-8') as f:
            for line in f:
                original_line = line.strip() # Keep original for output
                if not original_line: # Skip empty lines
                    continue

                found_translation_in_line = False
                for term in existing_chinese_terms:
                    # Check if the dictionary term is a substring of the line
                    if term in original_line:
                        found_translation_in_line = True
                        # print(f"DEBUG: Found '{term}' in '{original_line}'") # For debugging
                        break # Found a match for this line, no need to check other terms

                if not found_translation_in_line:
                    untranslated_lines.append(original_line)
        print(f"Found {len(untranslated_lines)} potentially untranslated lines in '{new_values_path}'.")
    except FileNotFoundError:
        print(f"Error: New values file not found at '{new_values_path}'. Please check the path.")
        return

    # Write the untranslated lines to the output file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            for line_to_write in untranslated_lines:
                f.write(line_to_write + '\n')
        print(f"Successfully wrote potentially untranslated lines to '{output_path}'.")
    except IOError:
        print(f"Error: Could not write to output file '{output_path}'.")

# --- How to Use from Command Prompt ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Find untranslated values in a text file by comparing against a JSON dictionary.")
    parser.add_argument("dictionary_file", help="The path to your dictionary.json file.")
    parser.add_argument("new_values_file", help="The path to your new text file with values to check.")
    parser.add_argument("output_file", help="The path where the new file with untranslated values will be saved.")

    args = parser.parse_args()

    # The paths are now taken directly from the command-line arguments
    dictionary_path = args.dictionary_file
    new_text_file_path = args.new_values_file
    output_new_file_path = args.output_file

    get_untranslated_new_values_substring_match(dictionary_path, new_text_file_path, output_new_file_path)