import re
import os

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
                # 1. Remove English letters (a-z, A-Z)
                # 2. Remove numbers (0-9)
                # 3. Remove common punctuation and math symbols.
                #    This regex targets:
                #    - \p{P}: Unicode punctuation (covers most punctuation)
                #    - \d: Digits (numbers)
                #    - [a-zA-Z]: English alphabet
                #    - [+\-*/=<>(){}[\]]: Specific math symbols and parentheses/brackets
                #    The re.UNICODE flag is important for \p{P} to work correctly.
                cleaned_line = re.sub(r'[a-zA-Z0-9\p{P}+\-*/=<>(){}[\]]', ' ', line, flags=re.UNICODE)

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

# --- How to use the script ---
if __name__ == "__main__":
    # IMPORTANT: Replace 'your_input_file.txt' with the actual path to your file.
    # For example: 'data/scraped_text.txt' or 'C:\\Users\\YourUser\\Documents\\my_scraped_data.txt'
    input_file_name = 'C:\Users\wilso\Documents\code\SCRAPEKING\pokeking_scraped_data_by_x\extracted_pokeking_values.txt'

    # The output file will be created in the same directory as the script,
    # or you can specify a full path like 'C:\\cleaned_output.txt'
    output_file_name = 'C:\Users\wilso\Documents\code\SCRAPEKING\step4_find_untranslated_values\new_values_to_check.txt'

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # Construct full paths
    input_path = os.path.join(script_dir, input_file_name)
    output_path = os.path.join(script_dir, output_file_name)

    # You can uncomment the line below and replace with your specific paths if needed
    # input_path = "path/to/your/scraped_data.txt"
    # output_path = "path/to/save/cleaned_data.txt"

    clean_text_file(input_path, output_path)
