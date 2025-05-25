# SCRAPEKING
for pokeking: scrape and clean data. finds untranslated values that need to be added to dictionary.


cmd prompt

before any script:
cd C:\Users\wilso\Documents\code\SCRAPEKING

step1

set YOUR_USERNAME=""
set YOUR_PASSWORD=""
python step1_scrapepokeking.py directory_name

step2
python step2_data_by_x_into_txt.py --input_dir directory_name 
optional if want to change txt name: --output_filename name.txt 
ex:
python step2_data_by_x_into_txt.py  --i 8E8EBC6ECBC9DEE4FE9BFAEC97A05375_code



step3
cd C:\Users\wilso\Documents\code\SCRAPEKING\step3_find_untranslated_values

python step3_filter_untranslated_values.py "dictionary.json" "new_values_to_check_wildtaste.txt" "untranslated_lines_wildtaste.txt"



