"""
Liatrio Sales Nav Automation (No API keys needed)
==================================================
Reads a contacts JSON file (that you generate from Claude research),
opens Sales Nav, and saves each contact to a company-specific list.
Setup:
  pip install selenium
  brew install chromedriver  (or download from https://chromedriver.chromium.org)
Usage:
  # After Claude researches contacts, save them to output/contacts/contacts_YYYY-MM-DD.json
  # Then run:
  python salesnav_automation.py --date 2026-03-11
  # Just open tabs without saving to lists:
  python salesnav_automation.py --date 2026-03-11 --no-save
  # Use a custom contacts file:
  python salesnav_automation.py --file my_contacts.json
"""
import os, sys, json, time, argparse, logging, urllib.parse, datetime
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, NoSuchElementException, ElementClickInterceptedException
)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("salesnav")
# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
OUTPUT_DIR = Path("output")
CONTACTS_DIR = OUTPUT_DIR / "contacts"
DELAY_SEARCH = 4          # wait after loading search results
DELAY_SAVE = 2            # wait after save actions
DELAY_PAGE = 5            # wait for page loads
DELAY_BETWEEN = 1.5       # between processing contacts
SALESNAV_SEARCH = (
    "https://www.linkedin.com/sales/search/people"
    "?query=(keywords%3A{keywords})"
)
# ---------------------------------------------------------------------------
# Browser setup — uses your existing Chrome profile so you're logged in
# ---------------------------------------------------------------------------
def create_driver(profile_dir=None):
    options = Options()
    if profile_dir:
        options.add_argument(f"--user-data-dir={profile_dir}")
    else:
        # Auto-detect Chrome profile
        if sys.platform == "darwin":
            p = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        elif sys.platform == "win32":
            p = os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\User Data")
        else:
            p = os.path.expanduser("~/.config/google-chrome")
        if os.path.exists(p):
            options.add_argument(f"--user-data-dir={p}")
            log.info(f"Using Chrome profile: {p}")
        else:
            log.warning("Chrome profile not found — you may need to log in manually")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    driver.set_window_size(1400, 900)
    return driver
def verify_session(driver):
    """Make sure we're logged into Sales Navigator."""
    driver.get("https://www.linkedin.com/sales/home")
    time.sleep(DELAY_PAGE)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "button, a[href*='/sales/']"))
        )
        log.info("Sales Navigator session OK")
        return True
    except TimeoutException:
        log.error("Not logged into Sales Navigator. Log in first, then retry.")
        return False
# ---------------------------------------------------------------------------
# List management
# ---------------------------------------------------------------------------
def find_list_id(driver, list_name):
    """Find an existing list by name, return its ID."""
    try:
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/sales/lists/people/']")
        for link in links:
            if list_name.lower() in link.text.strip().lower():
                href = link.get_attribute("href")
                return href.split("/sales/lists/people/")[-1].split("?")[0]
    except Exception:
        pass
    return None
def create_list(driver, list_name):
    """Create a new lead list or find existing one. Returns list ID."""
    driver.get("https://www.linkedin.com/sales/lists/people")
    time.sleep(DELAY_PAGE)
    # Check if already exists
    existing = find_list_id(driver, list_name)
    if existing:
        log.info(f"  List exists: '{list_name}' → {existing}")
        return existing
    # Click "Create lead list"
    try:
        create_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Create lead list')]")
            )
        )
        create_btn.click()
        time.sleep(1.5)
        # Type list name in the modal input
        name_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR,
                 "input[placeholder*='name'], input[placeholder*='Name'], "
                 "input[data-test-modal-input]")
            )
        )
        name_input.clear()
        name_input.send_keys(list_name)
        time.sleep(0.5)
        # Click Create/Save
        for text in ["Create", "Save"]:
            try:
                btn = driver.find_element(
                    By.XPATH,
                    f"//button[contains(., '{text}') and not(contains(., 'Cancel'))]"
                )
                if btn.is_displayed() and btn.is_enabled():
                    btn.click()
                    break
            except NoSuchElementException:
                continue
        time.sleep(DELAY_SAVE)
        # Verify creation
        new_id = find_list_id(driver, list_name)
        if new_id:
            log.info(f"  Created list: '{list_name}' → {new_id}")
            return new_id
        else:
            log.warning(f"  Could not verify list creation for '{list_name}'")
    except Exception as e:
        log.error(f"  Failed to create list '{list_name}': {e}")
    return None
# ---------------------------------------------------------------------------
# Contact search + save
# ---------------------------------------------------------------------------
def search_contact(driver, name, company):
    """Search Sales Nav for a contact. Returns True if results found."""
    keywords = urllib.parse.quote(f"{name} {company}")
    url = SALESNAV_SEARCH.format(keywords=keywords)
    driver.get(url)
    time.sleep(DELAY_SEARCH)
    # Check for results
    try:
        results_text = driver.find_element(
            By.XPATH, "//*[contains(text(), 'result')]"
        ).text
        if "0 result" in results_text:
            return False
        return True
    except NoSuchElementException:
        return True  # Assume results exist if we can't find the count
def save_first_result_to_list(driver, list_name):
    """
    Select the first search result and save it to the specified list.
    Uses the checkbox + "Save to list" bulk action approach.
    """
    try:
        # Step 1: Check the first result's checkbox
        checkboxes = driver.find_elements(
            By.CSS_SELECTOR, "input[type='checkbox'][id*='ember']"
        )
        # Skip "Select all" — find the first per-result checkbox
        for cb in checkboxes:
            label = cb.get_attribute("aria-label") or ""
            if "select all" not in label.lower() and "Add" in label:
                if not cb.is_selected():
                    try:
                        cb.click()
                    except ElementClickInterceptedException:
                        driver.execute_script("arguments[0].click();", cb)
                time.sleep(0.5)
                break
        # Step 2: Click "Save to list" button
        save_btn = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//button[contains(., 'Save to list')]")
            )
        )
        save_btn.click()
        time.sleep(1.5)
        # Step 3: In the dropdown/modal, find and select the target list
        # Look for list options in the dropdown
        list_options = driver.find_elements(
            By.XPATH,
            "//div[contains(@class, 'dropdown')]//label | "
            "//div[contains(@class, 'modal')]//label | "
            "//li[contains(@class, 'overflow-menu')]//button | "
            "//div[contains(@class, 'list-selector')]//label | "
            "//div[@role='listbox']//div[@role='option']"
        )
        found = False
        for opt in list_options:
            text = opt.text.strip() or opt.get_attribute("aria-label") or ""
            if list_name.lower() in text.lower():
                opt.click()
                found = True
                time.sleep(0.5)
                break
        if not found:
            # Try scrolling through list options and searching
            all_opts = driver.find_elements(By.CSS_SELECTOR, "label, [role='option']")
            for opt in all_opts:
                if list_name.lower() in (opt.text or "").lower():
                    opt.click()
                    found = True
                    break
        # Step 4: Click Save/Done/Apply
        for btn_text in ["Save", "Done", "Apply"]:
            try:
                done_btn = driver.find_element(
                    By.XPATH, f"//button[contains(., '{btn_text}')]"
                )
                if done_btn.is_displayed():
                    done_btn.click()
                    break
            except NoSuchElementException:
                continue
        time.sleep(DELAY_SAVE)
        return found
    except Exception as e:
        log.warning(f"    Save error: {e}")
        return False
def open_as_tab(driver, name, company):
    """Just open a Sales Nav search in a new tab (no saving)."""
    keywords = urllib.parse.quote(f"{name} {company}")
    url = SALESNAV_SEARCH.format(keywords=keywords)
    driver.execute_script(f"window.open('{url}', '_blank');")
# ---------------------------------------------------------------------------
# Load contacts from JSON
# ---------------------------------------------------------------------------
def load_contacts(path):
    """
    Load contacts JSON. Expected format:
    {
      "Company Name": [
        {"name": "Full Name", "title": "Job Title", "linkedin_url": "..."},
        ...
      ],
      ...
    }
    """
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def run(args):
    # Find contacts file
    if args.file:
        contacts_path = Path(args.file)
    else:
        date_str = args.date or datetime.datetime.now().strftime("%Y-%m-%d")
        contacts_path = CONTACTS_DIR / f"contacts_{date_str}.json"
    if not contacts_path.exists():
        log.error(f"Contacts file not found: {contacts_path}")
        log.error("Save your Claude research output to this file first.")
        log.error("Expected format: {\\"Company\\": [{\\"name\\": \\"...\\", \\"title\\": \\"...\\"}]}")
        sys.exit(1)
    contacts = load_contacts(str(contacts_path))
    total = sum(len(v) for v in contacts.values())
    log.info(f"Loaded {total} contacts across {len(contacts)} companies")
    # Start browser
    driver = create_driver(args.chrome_profile)
    try:
        if not verify_session(driver):
            return
        for company, people in contacts.items():
            log.info(f"\\n{'━'*50}")
            log.info(f"  {company} — {len(people)} contacts")
            log.info(f"{'━'*50}")
            # Create/find list for this company
            list_name = None
            list_id = None
            if not args.no_save:
                date_str = args.date or datetime.datetime.now().strftime("%Y-%m-%d")
                list_name = f"{company} {date_str}"
                list_id = create_list(driver, list_name)
                if not list_id:
                    log.warning(f"  Could not create/find list, opening tabs instead")
            for contact in people:
                name = contact["name"]
                title = contact.get("title", "")
                if args.no_save or not list_id:
                    # Just open in new tab
                    open_as_tab(driver, name, company)
                    log.info(f"    [TAB] {name} — {title}")
                else:
                    # Search and save to list
                    found = search_contact(driver, name, company)
                    if found:
                        saved = save_first_result_to_list(driver, list_name)
                        status = "SAVED" if saved else "FOUND (save failed)"
                    else:
                        status = "NOT FOUND"
                    log.info(f"    [{status}] {name} — {title}")
                time.sleep(DELAY_BETWEEN)
        log.info(f"\\n{'━'*50}")
        log.info("DONE — All contacts processed")
        log.info(f"{'━'*50}")
    finally:
        if args.close:
            driver.quit()
        else:
            log.info("Browser left open for review. Close manually when done.")
def main():
    p = argparse.ArgumentParser(description="Sales Nav Contact Automation")
    p.add_argument("--date", help="Date for contacts file (YYYY-MM-DD)")
    p.add_argument("--file", help="Path to contacts JSON file")
    p.add_argument("--no-save", action="store_true", help="Just open tabs, don't save to lists")
    p.add_argument("--close", action="store_true", help="Close browser when done")
    p.add_argument("--chrome-profile", help="Chrome user data directory path")
    args = p.parse_args()
    run(args)
if __name__ == "__main__":
    main()
