import os
import re
import traceback # Import traceback for detailed error logging
import argparse # Import the argparse module

def extract_and_format_data(input_dir, output_file): # Remove default values here
    """
    Reads through all .txt files in the specified input directory,
    extracts specific data values, filters out 'N/A' entries,
    and stores them in a set to automatically handle duplicates.
    Finally, it writes the unique, space-separated values to a single output file.
    """
    # Use a set to store extracted values to automatically handle duplicates
    all_extracted_values = set()

    # Define the regex patterns for the data points we want to extract
    # The (.*) captures everything after the label and colon/parentheses
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
            print(f"   Processing file: {filename}")
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip() # Remove leading/trailing whitespace

                        for key, pattern in patterns.items():
                            match = pattern.match(line)
                            if match:
                                value = match.group(1).strip()
                                # Only add values that are not "N/A"
                                if value and value.upper() != 'N/A':
                                    # Split the value by spaces and add each part to the set
                                    # Using update() with a set allows adding multiple items from an iterable
                                    all_extracted_values.update(value.split())
                                break # Move to the next line after finding a match

            except Exception as e:
                print(f"   Error processing file {filename}: {e}")
                traceback.print_exc() # Print full traceback for debugging

    # Join all collected unique values with a single space.
    # Since sets do not guarantee order, the output order might vary slightly
    # but all values will be unique.
    final_output_string = " ".join(sorted(list(all_extracted_values))) # Sort for consistent output order

    # Write the formatted data to the output file
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(final_output_string)
        print(f"\nSuccessfully extracted and saved unique data to: {output_file}")
    except Exception as e:
        print(f"Error writing to output file '{output_file}': {e}")
        traceback.print_exc()

if __name__ == "__main__":
    # 1. Create the parser
    parser = argparse.ArgumentParser(
        description="Extracts specific text values from Pokeking scraped data files and saves unique values to an output file."
    )

    # 2. Add arguments
    parser.add_argument(
        "-i", "--input_dir",
        type=str,
        default="pokeking_scraped_data_by_x", # Default input directory
        help="The directory containing the .txt files with scraped Pokeking data."
    )

    parser.add_argument(
        "-o", "--output_file",
        type=str,
        default="extracted_pokeking_values.txt", # Default output file name
        help="The name of the file where unique extracted values will be saved."
    )

    # 3. Parse the arguments from the command line
    args = parser.parse_args()

    # 4. Call your function with the arguments received from the command line
    extract_and_format_data(args.input_dir, args.output_file)