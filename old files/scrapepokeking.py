import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from urllib.parse import urljoin, urlparse
import time
import traceback # Import traceback module

# --- IMPORTANT: FILL IN YOUR CREDENTIALS HERE ---
YOUR_USERNAME = ""
YOUR_PASSWORD = ""
# -------------------------------------------------

def initialize_driver():
    """Initializes and returns a Chrome WebDriver."""
    chrome_options = Options()
    # Uncomment the line below for debugging (to see the browser window)
    # chrome_options.add_argument("--headless=new") # For observation, you might want to comment this out temporarily

    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    return driver

def perform_login(driver, login_url, username, password):
    """
    Navigates to the login page, attempts to log in, and handles the post-login pop-up.
    Handles a browser-level JavaScript alert.
    """
    print(f"Attempting to log in to: {login_url}")
    driver.get(login_url)
    time.sleep(3) # Initial page load time for login form elements

    try:
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'username'))
        )
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, '__BVID__17'))
        )
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'btnLogin'))
        )

        username_field.send_keys(username)
        password_field.send_keys(password)

        time.sleep(0.5)
        print("   Credentials entered. Clicking login button...")
        login_button.click()

        print("   Waiting for login success alert...")
        WebDriverWait(driver, 10).until(EC.alert_is_present())

        alert = driver.switch_to.alert
        alert_text = alert.text
        print(f"   Alert detected: '{alert_text}'")

        alert.accept()
        print("   Alert accepted.")
        time.sleep(2)

        print("   Attempting to dismiss any potential in-page pop-up by sending ENTER key (if applicable)...")
        driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ENTER)

        time.sleep(5)
        print("   Login interaction complete.")

        return True
    except Exception as e:
        print(f"Login failed: {e}")
        driver.save_screenshot("login_failed.png")
        print("Screenshot 'login_failed' saved for debugging.")
        return False

def extract_nested_data(driver, parent_element, nested_depth=0):
    """
    Recursively extracts data from nested collapsible items.
    'parent_element' is the element containing the 'node-div' elements.
    """
    nested_items_data = []
    
    indent = "    " * (3 + nested_depth) # For console output indentation

    # Find all 'node-div' elements within the current parent_element.
    all_nested_item_containers = parent_element.find_elements(By.CSS_SELECTOR, 'div.node-div')
    
    if not all_nested_item_containers:
        print(f"{indent}No more nested items found at this level.")
        return nested_items_data

    print(f"{indent}Found {len(all_nested_item_containers)} nested items at depth {nested_depth}.")

    for j, nested_item_element in enumerate(all_nested_item_containers):
        nested_data = {
            "nested_index": f"{nested_depth}-{j+1}",
            "nested_header_label_text": "N/A",
            "nested_header_operate_text": "N/A",
            "nested_trick_text": "N/A",
            "nested_body_label_text": "N/A",
            "nested_body_operate_text": "N/A",
            "nested_warning_badge_text": "N/A",  # Added for the new requirement
            "sub_nested_items": [] # To store recursively found items
        }

        try:
            # The clickable part within the container (likely div.node-title)
            nested_header_div = WebDriverWait(nested_item_element, 5).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div.node-title'))
            )
            # The actual content area after expansion is the `node-div` itself or a sibling `div.collapse`
            nested_body_element_to_scrape = nested_item_element # We'll scrape from here after expansion

            # --- Scrape from HEADER of nested item (these are the "collapsed" values for nested items) ---
            print(f"{indent}  Extracting collapsed values for Nested item {nested_data['nested_index']}...")
            try:
                nested_header_label_element = nested_header_div.find_element(By.CSS_SELECTOR, 'b.node-label')
                nested_data['nested_header_label_text'] = nested_header_label_element.text.strip()
                print(f"{indent}    Nested header label (collapsed): {nested_data['nested_header_label_text']}")
            except Exception:
                print(f"{indent}    Nested header label (collapsed): Not found.")
                pass

            try:
                nested_header_operate_element = nested_header_div.find_element(By.CSS_SELECTOR, 'b.node-operate')
                nested_data['nested_header_operate_text'] = nested_header_operate_element.text.strip()
                print(f"{indent}    Nested header operate (collapsed): {nested_data['nested_header_operate_text']}")
            except Exception:
                print(f"{indent}    Nested header operate (collapsed): Not found.")
                pass

            # --- MODIFICATION: Unconditionally click the nested header ---
            print(f"{indent}  Attempting native click on nested item {nested_data['nested_index']}...")
            nested_header_div.click() # PERFORM NATIVE CLICK

            # Wait for content to appear or for the state to change
            try:
                # Reduced timeout from 10 to 5 seconds
                WebDriverWait(nested_item_element, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div[role="alert"] b, b.node-label, b.node-operate, div.node-div, span.badge.badge-warning')) # Added badge-warning to expected elements
                )
                time.sleep(0.5) # Small stabilization pause after content appears
                print(f"{indent}  Nested item {nested_data['nested_index']} expanded via native click.")
            except Exception as click_wait_e:
                print(f"{indent}  Warning: After clicking nested item {nested_data['nested_index']}, expected content not found quickly: {click_wait_e}")
                pass

            # Scrape the "trick" text (if any) from the alert within the nested_body_element_to_scrape
            try:
                nested_trick_element = nested_body_element_to_scrape.find_element(By.CSS_SELECTOR, 'div[role="alert"] b')
                nested_data['nested_trick_text'] = nested_trick_element.text.strip()
                print(f"{indent}    Nested trick text (expanded): {nested_data['nested_trick_text']}")
            except Exception:
                print(f"{indent}    Nested trick text (expanded): Not found.")
                pass

            # --- NEW: Scrape the badge badge-warning from the nested item's body ---
            try:
                nested_warning_badge_element = nested_body_element_to_scrape.find_element(By.CSS_SELECTOR, 'span.badge.badge-warning')
                nested_data['nested_warning_badge_text'] = nested_warning_badge_element.text.strip()
                print(f"{indent}    Nested warning badge text (expanded): {nested_data['nested_warning_badge_text']}")
            except Exception:
                print(f"{indent}    Nested warning badge text (expanded): Not found.")
                pass

            # --- Scrape from BODY of nested item (if present after expansion) ---
            try:
                body_labels_and_operates = nested_body_element_to_scrape.find_elements(By.CSS_SELECTOR, 'b.node-label, b.node-operate')
                
                filtered_body_elements = []
                for el in body_labels_and_operates:
                    if not el.find_elements(By.XPATH, './ancestor::div[@class="node-title"]'):
                        filtered_body_elements.append(el.text.strip())

                if len(filtered_body_elements) >= 1:
                    nested_data['nested_body_label_text'] = filtered_body_elements[0]
                if len(filtered_body_elements) >= 2:
                    nested_data['nested_body_operate_text'] = filtered_body_elements[1]

                print(f"{indent}    Nested body label (expanded): {nested_data['nested_body_label_text']}")
                print(f"{indent}    Nested body operate (expanded): {nested_data['nested_body_operate_text']}")
            except Exception as e:
                print(f"{indent}    Error scraping body content for nested item {nested_data['nested_index']}: {e}. Full error: {traceback.format_exc()}")
                pass

            # --- RECURSIVE CALL for further nested items ---
            print(f"{indent}  Checking for sub-nested items within {nested_data['nested_index']}...")
            nested_data["sub_nested_items"] = extract_nested_data(driver, nested_body_element_to_scrape, nested_depth + 1)
            
            # Removed the collapse logic here. The item will remain expanded.
            
        except Exception as nested_e:
            print(f"{indent}Error processing nested item {nested_data['nested_index']}: {nested_e}. Full error: {traceback.format_exc()}")
            nested_data['nested_trick_text'] = "Error during processing, data not captured."
            nested_data['nested_body_label_text'] = "Error during processing, data not captured."
            nested_data['nested_body_operate_text'] = "Error during processing, data not captured."
            nested_data['nested_warning_badge_text'] = "Error during processing, data not captured." # Handle error for new field
            
        nested_items_data.append(nested_data)

    return nested_items_data


def extract_specific_data_from_page(driver, url):
    """
    Extracts specific desired data points from alert boxes and collapsible cards.
    Returns the extracted data as a list of dictionaries.
    Each dictionary will contain page_x, page_y, and either card data or alert box data.
    """
    print(f"\n--- Extracting data from: {url} ---")

    all_extracted_data = []

    parsed_url = urlparse(url)
    path_segments = [s for s in parsed_url.path.split('/') if s]
    current_x = "N/A"
    current_y = "N/A"
    if len(path_segments) >= 3 and path_segments[-3] == 'home': # Adjusted index for home/x/y
        try:
            current_x = int(path_segments[-2])
            current_y = int(path_segments[-1])
        except ValueError:
            pass

    # --- Attempt to scrape alert box content ---
    alert_box_selector = 'div[role="alert"].alert-success'
    alert_box_found = False
    try:
        alert_box_div = WebDriverWait(driver, 5).until( # Short wait for alert box
            EC.presence_of_element_located((By.CSS_SELECTOR, alert_box_selector))
        )
        print(f"   Found alert box on {url}.")
        alert_box_found = True

        alert_text_elements = alert_box_div.find_elements(By.XPATH, './/div[@data-v-51cd036b and not(./button)]')

        alert_texts = []
        for element in alert_text_elements:
            text_content = element.text.strip()
            if text_content:
                alert_texts.append(text_content)

        if alert_texts:
            all_extracted_data.append({
                "type": "alert_box_data",
                "page_x": current_x,
                "page_y": current_y,
                "alert_box_texts": alert_texts
            })
            print(f"   Extracted alert box text: {alert_texts}")
        else:
            print(f"   Alert box found but no relevant text extracted (possibly only button or empty content).")

    except Exception:
        print(f"   No alert box detected on {url}.")

    # --- Attempt to scrape collapsible card content ---
    card_container_selector = '.col-lg-9 div[role="tablist"]'

    try:
        card_container_wait_time = 3 if alert_box_found else 7

        all_card_headers = WebDriverWait(driver, card_container_wait_time).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, f'{card_container_selector} > div.card.mb-1 header[role="tab"] div[role="button"]'))
        )
        
        card_ids = [header.get_attribute('aria-controls') for header in all_card_headers if header.get_attribute('aria-controls')]

        if not card_ids:
            print(f"   No top-level card headers found with aria-controls on {url}.")
            fallback_cards = driver.find_elements(By.CSS_SELECTOR, 'div.card.mb-1')
            if fallback_cards:
                print(f"   Found {len(fallback_cards)} cards with fallback selector but no aria-controls for dynamic expansion.")
            else:
                print(f"   No collapsible cards found on {url}.")
            return all_extracted_data


        print(f"   Found {len(card_ids)} top-level collapsible cards to process on {url}.")

        for i, card_body_id in enumerate(card_ids):
            card_item_data = {
                "type": "card_data",
                "card_index": i + 1,
                "page_x": current_x,
                "page_y": current_y,
                "pokemon_name": "N/A",
                "red_bold_text": "N/A",
                "warning_badge_text": "N/A",
                "primary_trick_text": "N/A",
                "nested_items": []
            }

            try:
                clickable_header_div = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, f'header[role="tab"] div[role="button"][aria-controls="{card_body_id}"]'))
                )

                parent_card_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, f'div.card.mb-1:has(header[role="tab"] div[role="button"][aria-controls="{card_body_id}"])'))
                )

                print(f"    Extracting collapsed values for Main card {i+1}...")
                try:
                    poke_name_element = parent_card_element.find_element(By.CSS_SELECTOR, 'b[style*="margin-left: 5px"]')
                    card_item_data['pokemon_name'] = poke_name_element.text.strip()
                    print(f"      Pokemon Name (collapsed): {card_item_data['pokemon_name']}")
                except Exception:
                    print(f"      Pokemon Name (collapsed): Not found.")
                    pass

                try:
                    red_bold_element = parent_card_element.find_element(By.CSS_SELECTOR, 'b[style*="color: red"]')
                    card_item_data['red_bold_text'] = red_bold_element.text.strip()
                    print(f"      Red Bold Text (collapsed): {card_item_data['red_bold_text']}")
                except Exception:
                    print(f"      Red Bold Text (collapsed): Not found.")
                    pass

                try:
                    warning_badge_element = parent_card_element.find_element(By.CSS_SELECTOR, 'span.badge.badge-warning')
                    card_item_data['warning_badge_text'] = warning_badge_element.text.strip()
                    print(f"      Warning Badge Text (collapsed): {card_item_data['warning_badge_text']}")
                except Exception:
                    print(f"      Warning Badge Text (collapsed): Not found.")
                    pass

            except Exception as e:
                print(f"    Error in card {i+1} on page {current_x}/{current_y} (header initialization or primary element finding): {e}")
                print(f"    Full error: {traceback.format_exc()}")
                all_extracted_data.append(card_item_data)
                continue

            try:
                # --- MODIFICATION: Unconditionally click the main card header ---
                print(f"    Main card {i+1} attempting native click to expand...")
                
                clickable_header_div.click() # PERFORM NATIVE CLICK
                time.sleep(1) # Add 1-second pause after click
                time.sleep(1.5) # Allow some time for content to load after click

                # Reduced timeout from 7 to 5 seconds for card expansion waits
                WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, card_body_id))
                )
                WebDriverWait(driver, 5).until(
                     EC.text_to_be_present_in_element_attribute((By.CSS_SELECTOR, f'header[role="tab"] div[role="button"][aria-controls="{card_body_id}"]'), 'aria-expanded', 'true')
                )
                # REMOVED: WebDriverWait for presence of div.node-div or b.node-label
                
                time.sleep(0.5) # Small stabilization pause after content appears
                print(f"    Main card {i+1} expanded via native click.")
                
                # Reduced timeout from 7 to 5 seconds for card body element visibility
                card_body_element = WebDriverWait(driver, 5).until(
                    EC.visibility_of_element_located((By.ID, card_body_id))
                )

                card_item_data['primary_trick_text'] = "N/A"
                print(f"      Primary Trick Text: {card_item_data['primary_trick_text']}")

                print(f"    Processing nested items for Main card {i+1}...")
                card_item_data["nested_items"] = extract_nested_data(driver, card_body_element, nested_depth=0)

                # Removed the collapse logic here. The card will remain expanded.

            except Exception as e:
                print(f"    Error processing main card {i+1} on page {current_x}/{current_y} (body expansion/extraction): {e}. Full error: {traceback.format_exc()}")

            all_extracted_data.append(card_item_data)

    except Exception as e:
        print(f"   An error occurred while trying to find or process main collapsible cards: {e}. Full error: {traceback.format_exc()}")

    if not all_extracted_data:
        print(f"   No data (alert box or cards) found on {url}.")

    return all_extracted_data

# The __main__ block remains the same
if __name__ == "__main__":
    base_first_url = "http://www.pokeking.icu/king/tree/first/"

    driver = None
    output_base_dir = "pokeking_scraped_data_by_x"
    os.makedirs(output_base_dir, exist_ok=True)

    written_x_categories = set()

    try:
        driver = initialize_driver()

        initial_login_url = "http://www.pokeking.icu/king/tree/first/1"
        print(f"Attempting initial login using: {initial_login_url}")
        login_successful = perform_login(driver, initial_login_url, YOUR_USERNAME, YOUR_PASSWORD)

        if not login_successful:
            print("\n--- Script finished. Login failed. Browser is still open for inspection. ---")
            input("Login failed. Press Enter to manually close the browser and exit script...")
            exit()

        print("\nLogin successful!")

        for first_page_num in range(1, 26 + 1):
            current_first_url = f"{base_first_url}{first_page_num}"
            print(f"\n--- Navigating to First Page: {current_first_url} ---")
            driver.get(current_first_url)
            time.sleep(3)

            try:
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 'div.pet-dev'))
                )
                print(f"   Images loaded on {current_first_url}.")
            except Exception as e:
                print(f"   No pet-dev images found on {current_first_url} or page load issue: {e}. Full error: {traceback.format_exc()}")
                driver.save_screenshot(f"no_images_first_{first_page_num}.png")
                continue

            num_images = len(driver.find_elements(By.CSS_SELECTOR, 'div.pet-dev'))
            print(f"   Found {num_images} images to click on {current_first_url}.")

            for i in range(num_images):
                try:
                    pet_dev_elements = WebDriverWait(driver, 10).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.pet-dev'))
                    )
                    if i >= len(pet_dev_elements):
                        print(f"    Skipping image {i+1}: Element no longer present after re-locating.")
                        continue
                    image_to_click = pet_dev_elements[i]

                    link_element = None
                    try:
                        link_element = image_to_click.find_element(By.XPATH, './ancestor::a[1]')
                    except:
                        print(f"    Warning: Could not find parent <a> for image {i+1}. Skipping.")
                        continue

                    if link_element and link_element.tag_name == 'a':
                        relative_href = link_element.get_attribute('href')
                        target_url = urljoin(driver.current_url, relative_href)
                    else:
                        print(f"    Warning: No valid link (href) found for image {i+1} on {current_first_url}. Skipping.")
                        continue

                    print(f"    Clicking image {i+1}/{num_images} to go to: {target_url}")
                    driver.execute_script("arguments[0].click();", image_to_click)

                    WebDriverWait(driver, 20).until(EC.url_to_be(target_url))
                    print(f"    Successfully navigated to: {driver.current_url}")

                    time.sleep(3)

                    parsed_target_url = urlparse(driver.current_url)
                    path_segments_target = [s for s in parsed_target_url.path.split('/') if s]
                    x_val_from_link = "unknown_x"
                    try:
                        if len(path_segments_target) >= 3 and path_segments_target[-3] == 'home':
                            x_val_from_link = int(path_segments_target[-2])
                    except ValueError:
                            pass

                    extracted_data_for_page = extract_specific_data_from_page(driver, driver.current_url)

                    if extracted_data_for_page:
                        file_name = f"pokeking_icu_home_X_{x_val_from_link}_data.txt"
                        file_path = os.path.join(output_base_dir, file_name)

                        formatted_output_lines = []
                        for data_item in extracted_data_for_page:
                            formatted_output_lines.append("=" * 10 + f" Data from page {data_item.get('page_x', 'N/A')}/{data_item.get('page_y', 'N/A')} " + "=" * 10)

                            if data_item.get("type") == "alert_box_data":
                                formatted_output_lines.append(f"--- Alert Box Data ---")
                                for text in data_item.get("alert_box_texts", []):
                                    formatted_output_lines.append(f"  Alert Text: {text}")
                            elif data_item.get("type") == "card_data":
                                formatted_output_lines.append(f"--- Card Entry (Card {data_item.get('card_index', 'N/A')}) ---")

                                formatted_output_lines.append(f"pokemon_name: {data_item.get('pokemon_name', 'N/A')}")
                                formatted_output_lines.append(f"red_bold_text: {data_item.get('red_bold_text', 'N/A')}")
                                formatted_output_lines.append(f"warning_badge_text: {data_item.get('warning_badge_text', 'N/A')}")
                                formatted_output_lines.append(f"primary_trick_text: {data_item.get('primary_trick_text', 'N/A')}")

                                # Helper function to format nested items
                                def format_nested(nested_list, depth=0):
                                    nested_lines = []
                                    indent_str = "  " * (depth + 1)
                                    if nested_list:
                                        nested_lines.append(f"{indent_str}--- Nested Items ({len(nested_list)}) ---")
                                        for nested_entry in nested_list:
                                            nested_lines.append(f"{indent_str}  Nested Item {nested_entry.get('nested_index', 'N/A')}:")
                                            nested_lines.append(f"{indent_str}    nested_header_label_text (collapsed): {nested_entry.get('nested_header_label_text', 'N/A')}")
                                            nested_lines.append(f"{indent_str}    nested_header_operate_text (collapsed): {nested_entry.get('nested_header_operate_text', 'N/A')}")
                                            nested_lines.append(f"{indent_str}    nested_trick_text (expanded): {nested_entry.get('nested_trick_text', 'N/A')}")
                                            nested_lines.append(f"{indent_str}    nested_body_label_text (expanded): {nested_entry.get('nested_body_label_text', 'N/A')}")
                                            nested_lines.append(f"{indent_str}    nested_body_operate_text (expanded): {nested_entry.get('nested_body_operate_text', 'N/A')}")
                                            nested_lines.append(f"{indent_str}    nested_warning_badge_text (expanded): {nested_entry.get('nested_warning_badge_text', 'N/A')}") # Added this line
                                            
                                            # Recursively format sub-nested items
                                            sub_nested_data = nested_entry.get('sub_nested_items', [])
                                            nested_lines.extend(format_nested(sub_nested_data, depth + 1))
                                            nested_lines.append(f"{indent_str}  --------------------")
                                    return nested_lines

                                formatted_output_lines.extend(format_nested(data_item.get('nested_items', []))) # Changed to call the helper function

                                formatted_output_lines.append("-" * 30)

                        final_output_string = "\n".join(formatted_output_lines)

                        with open(file_path, "a", encoding="utf-8") as f:
                            f.write(final_output_string + "\n\n")
                        print(f"    Appended data for X={x_val_from_link} to {file_path}")
                        written_x_categories.add(x_val_from_link)
                    else:
                        print(f"    No extractable data found on {driver.current_url}. No data written to file.")

                    print(f"    Going back to {current_first_url} to continue image clicks.")
                    driver.back()
                    WebDriverWait(driver, 10).until(EC.url_to_be(current_first_url))
                    time.sleep(2)

                except Exception as img_click_error:
                    print(f"    Error processing image {i+1} on {current_first_url}: {img_click_error}. Full error: {traceback.format_exc()}")
                    driver.save_screenshot(f"error_image_click_first_{first_page_num}_img_{i+1}.png")
                    if driver.current_url != current_first_url:
                        print(f"    Attempting to go back to {current_first_url} after error.")
                        driver.back()
                        WebDriverWait(driver, 10).until(EC.url_to_be(current_first_url))
                        time.sleep(2)
                    continue

        print(f"\n--- Script execution complete. Data saved for X categories: {sorted(list(written_x_categories))}. ---")

    except Exception as main_error:
        print(f"An unexpected error occurred during the main scraping process: {main_error}. Full error: {traceback.format_exc()}")
    finally:
        if driver:
            print("\n--- Browser is still open for inspection. ---")
            print(f"Scraped data saved in the '{output_base_dir}' folder.")
            input("Press Enter to manually close the browser and exit script...")
            driver.quit()
        else:
            print("\n--- Script finished without initializing browser. ---")