# pylint: skip-file

"""
Minted Address Book Export Script

This script logs into Minted, navigates to the address book,
and exports all contacts to CSV and Excel formats.
"""

import os
from time import sleep

import pandas as pd
import requests
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager


def get_credentials():
    """Get Minted credentials from environment variables or user input."""
    try:
        email = os.environ["minted_email"]
    except KeyError:
        email = input("Enter your minted.com email address: ")

    try:
        password = os.environ["minted_password"]
    except KeyError:
        password = input("Enter your minted.com password: ")

    return email, password


def setup_driver(headless=False):
    """Set up Chrome WebDriver with options."""
    options = Options()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    # Avoid detection as automated browser
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    # Keep browser open and visible
    options.add_experimental_option("detach", False)

    print("Starting Chrome browser (window should appear)...")
    service = Service(ChromeDriverManager().install())
    driver = Chrome(service=service, options=options)

    # Further avoid detection
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    # Make sure window is visible and positioned on screen
    sleep(1)
    driver.set_window_position(100, 100)
    driver.set_window_size(1200, 900)
    sleep(1)
    print("Browser window should now be visible")

    return driver


def login_to_minted(driver, email, password):
    """Log in to Minted via the login page."""
    login_url = "https://login.minted.com/"
    print(f"Navigating to login page: {login_url}")
    driver.get(login_url)

    wait = WebDriverWait(driver, 20)

    try:
        # Wait for page to load
        sleep(2)

        # Try multiple selectors for email field
        email_field = None
        email_selectors = [
            (By.ID, "identifierMNTD"),
            (By.NAME, "identifierMNTD"),
            (By.CSS_SELECTOR, "input[type='email']"),
            (By.CSS_SELECTOR, "[data-cy='email'] input"),
            (By.XPATH, "//input[@type='email']"),
        ]

        for selector_type, selector in email_selectors:
            try:
                email_field = driver.find_element(selector_type, selector)
                if email_field and email_field.is_displayed():
                    print(f"Found email field using: {selector}")
                    break
            except NoSuchElementException:
                continue

        if not email_field:
            print("ERROR: Could not find email field. Dumping page source...")
            # Print input fields found on page for debugging
            inputs = driver.find_elements(By.TAG_NAME, "input")
            print(f"Found {len(inputs)} input fields:")
            for inp in inputs[:10]:  # First 10
                print(
                    f"  - id='{inp.get_attribute('id')}' name='{inp.get_attribute('name')}' type='{inp.get_attribute('type')}'"
                )
            return False

        sleep(0.5)
        email_field.clear()
        email_field.send_keys(email)
        print("Entered email")

        # Try multiple selectors for password field
        password_field = None
        password_selectors = [
            (By.ID, "password"),
            (By.NAME, "password"),
            (By.CSS_SELECTOR, "input[type='password']"),
            (By.CSS_SELECTOR, "[data-cy='password'] input"),
        ]

        for selector_type, selector in password_selectors:
            try:
                password_field = driver.find_element(selector_type, selector)
                if password_field and password_field.is_displayed():
                    print(f"Found password field using: {selector}")
                    break
            except NoSuchElementException:
                continue

        if not password_field:
            print("ERROR: Could not find password field")
            return False

        password_field.clear()
        password_field.send_keys(password)
        print("Entered password")

        sleep(1)  # Small delay before clicking

        # Find and click login button - try multiple selectors
        login_button = None
        button_selectors = [
            (By.XPATH, "//button[@type='submit']"),
            (By.XPATH, "//button[contains(text(), 'Log In')]"),
            (By.XPATH, "//button[contains(text(), 'Log in')]"),
            (By.XPATH, "//button[contains(text(), 'Sign In')]"),
            (By.XPATH, "//button[contains(text(), 'Sign in')]"),
            (By.CSS_SELECTOR, "button[type='submit']"),
            (By.CSS_SELECTOR, "form button"),
        ]

        for selector_type, selector in button_selectors:
            try:
                buttons = driver.find_elements(selector_type, selector)
                for btn in buttons:
                    if btn.is_displayed() and btn.is_enabled():
                        login_button = btn
                        break
                if login_button:
                    break
            except NoSuchElementException:
                continue

        if login_button:
            # Use JavaScript click as it's more reliable
            driver.execute_script("arguments[0].click();", login_button)
            print(f"Clicked login button: {login_button.text or 'submit'}")
        else:
            # Try pressing Enter on password field as fallback
            from selenium.webdriver.common.keys import Keys

            password_field.send_keys(Keys.RETURN)
            print("Submitted form via Enter key")

        # Wait for login to complete - check for redirect away from login page
        print("Waiting for login to complete...")
        max_wait = 30  # seconds
        for i in range(max_wait):
            sleep(1)
            current_url = driver.current_url
            if "login.minted.com" not in current_url:
                print(f"Login successful! Redirected to: {current_url}")
                return True
            if i % 5 == 4:
                print(f"  Still on login page after {i+1} seconds...")

        # If we're still on login page, check for error messages
        print(f"Current URL after {max_wait}s: {driver.current_url}")

        # Check for any error messages on the page
        try:
            error_elements = driver.find_elements(
                By.CSS_SELECTOR, "[class*='error'], [class*='Error'], [role='alert']"
            )
            for elem in error_elements:
                if elem.text.strip():
                    print(f"Error on page: {elem.text}")
        except:
            pass

        # Even if still on login page, let user manually complete login if needed
        print("\n" + "=" * 50)
        print("LOGIN REQUIRES MANUAL INTERVENTION")
        print("=" * 50)
        print("The browser window should be open.")
        print("Please complete the login manually if needed.")
        print("(There may be a CAPTCHA, 2FA, or other verification)")
        print("")
        print("After you've logged in successfully, press Enter here.")
        print("Or press Ctrl+C to abort.")
        print("=" * 50)

        try:
            input("\n>>> Press Enter when logged in: ")
            sleep(2)  # Give page time to settle
            current_url = driver.current_url
            print(f"Current URL: {current_url}")
            if "login.minted.com" not in current_url:
                print("Login successful!")
                return True
            else:
                print("Still on login page. Please try again or check credentials.")
        except KeyboardInterrupt:
            print("\nAborted by user")
            return False

        return False

    except TimeoutException:
        print(
            "ERROR: Login page elements not found. The page structure may have changed."
        )
        return False


def try_api_export(driver):
    """Try to export contacts via the API (legacy method)."""
    print("Attempting API export...")
    cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

    api_endpoints = [
        "https://addressbook.minted.com/api/contacts/contacts/?format=json",
        "https://addressbook.minted.com/api/contacts/?format=json",
    ]

    for endpoint in api_endpoints:
        try:
            response = requests.get(endpoint, cookies=cookies, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    print(f"API export successful from {endpoint}")
                    return data
        except Exception as e:
            print(f"API endpoint {endpoint} failed: {e}")

    print("API export not available, falling back to page scraping")
    return None


def scrape_address_book(driver):
    """Scrape contacts from the address book page."""
    address_book_url = "https://www.minted.com/addressbook/my-account/finalize/0"
    print(f"Navigating to address book: {address_book_url}")
    driver.get(address_book_url)

    wait = WebDriverWait(driver, 20)
    contacts = []

    try:
        # Wait for contacts table to load
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "[data-cy='abk_contactsTable']")
            )
        )
        sleep(2)  # Additional wait for dynamic content

        # Find all contact rows
        contact_rows = driver.find_elements(
            By.CSS_SELECTOR, "[data-cy='abk_contactRow']"
        )
        print(f"Found {len(contact_rows)} contacts")

        for i, row in enumerate(contact_rows):
            try:
                contact_data = extract_contact_from_row(driver, row, i)
                if contact_data:
                    contacts.append(contact_data)
                    print(
                        f"  Extracted contact {i+1}: {contact_data.get('name', 'Unknown')}"
                    )
            except Exception as e:
                print(f"  Error extracting contact {i+1}: {e}")

    except TimeoutException:
        print("ERROR: Address book page did not load properly")

    return contacts


def extract_contact_from_row(driver, row, index):
    """Extract contact information from a single row, expanding if needed."""
    contact = {}

    try:
        # Get name from the row
        name_elem = row.find_element(By.CSS_SELECTOR, ".css-f8pz0c")
        contact["name"] = name_elem.text.strip()
    except NoSuchElementException:
        contact["name"] = ""

    try:
        # Get visible street address
        address_div = row.find_element(By.CSS_SELECTOR, ".css-1mzdrva div:first-child")
        contact["street_line1"] = address_div.text.strip()
    except NoSuchElementException:
        contact["street_line1"] = ""

    # Try to expand the row to get more details
    try:
        expand_button = row.find_element(
            By.CSS_SELECTOR, "[data-cy='abk_expandContactButton'] button"
        )
        driver.execute_script("arguments[0].click();", expand_button)
        sleep(0.5)  # Wait for expansion

        # Look for expanded content with full address details
        # The expanded view typically shows city, state, zip
        expanded_content = row.find_elements(By.CSS_SELECTOR, "div")

        # Parse expanded content for additional address fields
        full_text = row.text
        lines = full_text.split("\n")

        # Try to identify city, state, zip from the expanded text
        for line in lines:
            line = line.strip()
            # Skip the name we already have
            if line == contact.get("name"):
                continue
            # Skip the street we already have
            if line == contact.get("street_line1"):
                continue
            # Look for city, state ZIP pattern
            import re

            city_state_zip = re.search(
                r"^([^,]+),\s*([A-Z]{2})\s+(\d{5}(?:-\d{4})?)$", line
            )
            if city_state_zip:
                contact["city"] = city_state_zip.group(1)
                contact["state"] = city_state_zip.group(2)
                contact["zip"] = city_state_zip.group(3)

        # Collapse the row
        driver.execute_script("arguments[0].click();", expand_button)
        sleep(0.3)

    except NoSuchElementException:
        pass
    except Exception as e:
        print(f"    Warning: Could not expand contact details: {e}")

    # If we didn't get full address from expansion, try the edit modal
    if "city" not in contact:
        try:
            contact = get_contact_from_edit_modal(driver, row, contact)
        except Exception as e:
            print(f"    Warning: Could not get details from edit modal: {e}")

    return contact


def get_contact_from_edit_modal(driver, row, contact):
    """Open the edit modal to get full contact details."""
    try:
        edit_button = row.find_element(
            By.CSS_SELECTOR, "[data-cy='abk_editContactButton'] button"
        )
        driver.execute_script("arguments[0].click();", edit_button)
        sleep(1)  # Wait for modal to open

        # Look for form fields in the modal
        field_mappings = {
            "firstName": "first_name",
            "lastName": "last_name",
            "addressLine1": "street_line1",
            "addressLine2": "street_line2",
            "city": "city",
            "state": "state",
            "zipCode": "zip",
            "country": "country",
        }

        for field_id, contact_key in field_mappings.items():
            try:
                field = driver.find_element(By.ID, field_id)
                value = field.get_attribute("value")
                if value:
                    contact[contact_key] = value
            except NoSuchElementException:
                pass

        # Also try by name attribute
        for field_name, contact_key in field_mappings.items():
            try:
                field = driver.find_element(By.NAME, field_name)
                value = field.get_attribute("value")
                if value:
                    contact[contact_key] = value
            except NoSuchElementException:
                pass

        # Close the modal - look for close/cancel button
        close_selectors = [
            (By.CSS_SELECTOR, "[aria-label='Close']"),
            (By.CSS_SELECTOR, "button[aria-label='close']"),
            (By.XPATH, "//button[contains(text(), 'Cancel')]"),
            (By.XPATH, "//button[contains(text(), 'Close')]"),
            (By.CSS_SELECTOR, ".modal-close"),
        ]

        for selector_type, selector in close_selectors:
            try:
                close_button = driver.find_element(selector_type, selector)
                driver.execute_script("arguments[0].click();", close_button)
                sleep(0.5)
                break
            except NoSuchElementException:
                continue

        # If no close button found, press Escape
        from selenium.webdriver.common.keys import Keys

        driver.find_element(By.TAG_NAME, "body").send_keys(Keys.ESCAPE)
        sleep(0.5)

    except Exception as e:
        print(f"    Edit modal error: {e}")

    return contact


def export_contacts(contacts, output_dir="./data"):
    """Export contacts to CSV and Excel files."""
    if not contacts:
        print("No contacts to export")
        return

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Create DataFrame
    df = pd.DataFrame(contacts)

    # Reorder columns if they exist
    preferred_order = [
        "name",
        "first_name",
        "last_name",
        "street_line1",
        "street_line2",
        "city",
        "state",
        "zip",
        "country",
    ]

    existing_cols = [col for col in preferred_order if col in df.columns]
    other_cols = [col for col in df.columns if col not in preferred_order]
    df = df[existing_cols + other_cols]

    # Export to CSV
    csv_path = os.path.join(output_dir, "minted-addresses.csv")
    df.to_csv(csv_path, index=False)
    print(f"Exported {len(contacts)} contacts to {csv_path}")

    # Export to Excel
    excel_path = os.path.join(output_dir, "minted-addresses.xlsx")
    df.to_excel(excel_path, index=False)
    print(f"Exported {len(contacts)} contacts to {excel_path}")

    return df


def main():
    """Main function to orchestrate the export process."""
    print("=" * 50)
    print("Minted Address Book Export")
    print("=" * 50)

    # Get credentials
    email, password = get_credentials()

    # Set up driver (set headless=False to see the browser)
    print("\nSetting up browser...")
    driver = setup_driver(headless=True)

    try:
        # Login
        print("\nLogging in...")
        if not login_to_minted(driver, email, password):
            print("Login failed. Exiting.")
            return

        # Try API export first
        contacts = try_api_export(driver)

        # If API didn't work, scrape the page
        if not contacts:
            print("\nScraping address book page...")
            contacts = scrape_address_book(driver)

        # Export results
        if contacts:
            print(f"\nExporting {len(contacts)} contacts...")
            export_contacts(contacts)
            print("\nExport complete!")
        else:
            print("\nNo contacts found to export.")

    except Exception as e:
        print(f"Error: {e}")
        import traceback

        traceback.print_exc()

    finally:
        print("\nClosing browser...")
        driver.quit()


if __name__ == "__main__":
    main()
