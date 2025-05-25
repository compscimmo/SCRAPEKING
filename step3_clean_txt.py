# in cmd prompt
# python step3_clean_txt.py 
# "C:\Users\wilso\Documents\code\SCRAPEKING\pokeking_scraped_data_by_x\extracted_pokeking_values.txt" - input file
# "C:\Users\wilso\Documents\code\SCRAPEKING\step4_find_untranslated_values\new_values_to_check.txt" - output file
import re
import os
import argparse # Import the argparse module
import string # Import the string module to get punctuation characters

def clean_text_file(input_filepath, output_filepath):
    """
    Cleans a text file by removing English letters, punctuation, numbers,
    math symbols, and parentheses. Replaces removed characters with a space.
    Then, puts each space-separated value on a new line and removes duplicates.

    Args:
        input_filepath (str): The path to the input .txt file.
        output_filepath (str): The path where the cleaned .txt file will be saved.
    """
    cleaned_values = set() # Use a set to automatically handle duplicates

    try:
        with open(input_filepath, 'r', encoding='utf-8') as infile:
            for line in infile:
                # Define a regex pattern to remove:
                # 1. English letters (a-z, A-Z)
                # 2. Numbers (0-9)
                # 3. Common punctuation (using string.punctuation)
                # 4. Specific math symbols and parentheses/brackets (already in the original regex)
                #    re.escape(string.punctuation) ensures all punctuation characters are treated literally.
                #    We combine this with the other character classes.
                punctuation_pattern = re.escape(string.punctuation)
                # The pattern now explicitly lists characters to remove.
                # Note: The original regex included [+\-*/=<>(){}[\]] which are mostly covered by string.punctuation
                # but it's safer to explicitly add them if there's any doubt.
                # For simplicity and to fix the \p{P} issue, we'll use string.punctuation.
                # If you need to be very specific about math symbols, you can add them back.
                # For this fix, we'll focus on replacing \p{P} with string.punctuation.
                
                # The new regex will remove:
                # - a-zA-Z (English letters)
                # - 0-9 (numbers)
                # - All characters in string.punctuation (e.g., !, ", #, $, %, &, ', (, ), *, +, ,, -, ., /, :, ;, <, =, >, ?, @, [, \, ], ^, _, `, {, |, }, ~)
                # We need to be careful with characters like - in a character set, it needs to be at the start or end, or escaped.
                # Let's build a robust character set.
                
                # Characters to remove:
                # - English letters: a-zA-Z
                # - Numbers: 0-9
                # - Punctuation: using string.punctuation
                # - Specific math symbols/parentheses: +-*/=<>(){}[] (these are largely covered by string.punctuation)
                
                # A more robust pattern for the standard re module:
                # We create a character class that includes letters, numbers, and escaped punctuation.
                # The `re.escape` function is crucial here to ensure characters like `.` or `*` in `string.punctuation`
                # are treated as literal characters in the regex, not special regex operators.
                chars_to_remove_pattern = f'[a-zA-Z0-9{re.escape(string.punctuation)}]'
                
                cleaned_line = re.sub(chars_to_remove_pattern, ' ', line, flags=re.UNICODE)

                # Replace multiple spaces with a single space and strip leading/trailing spaces
                cleaned_line = re.sub(r'\s+', ' ', cleaned_line).strip()

                # Split the line into space-separated values and add to the set
                if cleaned_line: # Only process if there's content after cleaning
                    for value in cleaned_line.split(' '):
                        if value: # Ensure the value is not an empty string
                            cleaned_values.add(value)

        # Write the unique, cleaned values to the output file, each on a new line
        with open(output_filepath, 'w', encoding='utf-8') as outfile:
            # Sort the values for consistent output, though not strictly required by prompt
            for value in sorted(list(cleaned_values)):
                outfile.write(value + '\n')

        print(f"File cleaned successfully! Cleaned content saved to: {output_filepath}")

    except FileNotFoundError:
        print(f"Error: Input file not found at '{input_filepath}'")
    except Exception as e:
        print(f"An error occurred: {e}")

# --- How to use the script with command-line arguments ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean a text file by removing specific characters and extracting unique values.")
    parser.add_argument("input_file", help="The path to the input .txt file.")
    parser.add_argument("output_file", help="The path where the cleaned .txt file will be saved.")

    args = parser.parse_args()

    # The paths are now taken directly from the command-line arguments
    input_path = args.input_file
    output_path = args.output_file

    clean_text_file(input_path, output_path)
