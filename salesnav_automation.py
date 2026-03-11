"""
Liatrio Sales Navigator Automation
===================================
Automates: contact research (Claude API) → Sales Nav browser automation → save to lists
Usage:
  python salesnav_automation.py                    # Full pipeline
  python salesnav_automation.py --date 2026-03-11  # Specific date
  python salesnav_automation.py --skip-research    # Use cached contacts
  python salesnav_automation.py --no-save          # Just open tabs, don't save to lists
  python salesnav_automation.py --no-browser       # Research + outreach only
Env vars:
  ANTHROPIC_API_KEY          - Claude API key
"""
import os, sys, json, time, csv, re, datetime, argparse, logging, urllib.parse
from pathlib import Path
try:
    from selenium import webdriver
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False
try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("salesnav")
OUTPUT_DIR = Path("output")
CONTACTS_DIR = OUTPUT_DIR / "contacts"
DELAY_BETWEEN_SEARCHES = 3
DELAY_BETWEEN_SAVES = 2
DELAY_PAGE_LOAD = 5
SALESNAV_SEARCH_URL = "https://www.linkedin.com/sales/search/people?query=(keywords%3A{keywords})"
try:
    from target_companies import TARGET_TITLES
except ImportError:
    TARGET_TITLES = ["CIO", "CTO", "VP of Engineering", "Director of Platform Engineering",
                     "Director of DevOps", "Head of Cloud", "Enterprise Architect"]
# ===========================================================================
# PHASE 1: Contact Research via Claude API
# ===========================================================================
def research_contacts_with_claude(report_path: str) -> dict:
    if not ANTHROPIC_AVAILABLE:
        log.error("pip install anthropic"); sys.exit(1)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        log.error("Set ANTHROPIC_API_KEY"); sys.exit(1)
    with open(report_path, "r") as f:
        report = json.load(f)
    companies = []
    for entry in report.get("top_10_companies", []):
        triggers = [l["headline"] for l in entry.get("leads", [])[:3]]
        companies.append({"name": entry["company"], "rank": entry["rank"], "triggers": triggers})
    title_list = ", ".join(TARGET_TITLES[:10])
    prompt = f"""You are a B2B sales research assistant. For each company, find 5-10 decision-maker contacts.
Target roles: {title_list}
Respond with ONLY valid JSON, no other text:
{{"companies": [{{"company": "Name", "contacts": [{{"name": "Full Name", "title": "Title", "linkedin_url": "https://linkedin.com/in/..."}}]}}]}}
Companies:
"""
    for c in companies:
        prompt += f"\\n{c['rank']}. {c['name']}"
        if c["triggers"]:
            prompt += f" (Trigger: {c['triggers'][0][:80]})"
    log.info("Sending research request to Claude API...")
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=8000,
                                     messages=[{"role": "user", "content": prompt}])
    response_text = message.content[0].text
    json_match = re.search(r'\\{[\\s\\S]*\\}', response_text)
    if not json_match:
        log.error("No JSON in response"); return {}
    try:
        data = json.loads(json_match.group())
    except json.JSONDecodeError:
        log.error("Bad JSON"); return {}
    contacts = {}
    for cd in data.get("companies", []):
        contacts[cd["company"]] = [
            {"name": c["name"], "title": c.get("title",""), "linkedin_url": c.get("linkedin_url","")}
            for c in cd.get("contacts", [])
        ]
    return contacts
# ===========================================================================
# PHASE 2: Sales Navigator Browser Automation
# ===========================================================================
def create_driver(chrome_profile_dir=None):
    if not SELENIUM_AVAILABLE:
        log.error("pip install selenium"); sys.exit(1)
    options = Options()
    if chrome_profile_dir:
        options.add_argument(f"--user-data-dir={chrome_profile_dir}")
    else:
        if sys.platform == "darwin":
            p = os.path.expanduser("~/Library/Application Support/Google/Chrome")
        elif sys.platform == "win32":
            p = os.path.expandvars(r"%LOCALAPPDATA%\\Google\\Chrome\\User Data")
        else:
            p = os.path.expanduser("~/.config/google-chrome")
        if os.path.exists(p):
            options.add_argument(f"--user-data-dir={p}")
    options.add_argument("--no-first-run")
    options.add_argument("--no-default-browser-check")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(10)
    return driver
def verify_salesnav_session(driver):
    driver.get("https://www.linkedin.com/sales/home")
    time.sleep(DELAY_PAGE_LOAD)
    try:
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, ".app-nav, .global-nav")))
        log.info("Sales Nav session verified")
        return True
    except TimeoutException:
        log.error("Not logged in to Sales Navigator"); return False
def find_existing_list(driver, list_name):
    try:
        links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/sales/lists/people/']")
        for link in links:
            if list_name.lower() in link.text.lower():
                return link.get_attribute("href").split("/sales/lists/people/")[-1].split("?")[0]
    except: pass
    return None
def create_lead_list(driver, list_name):
    driver.get("https://www.linkedin.com/sales/lists/people")
    time.sleep(DELAY_PAGE_LOAD)
    existing = find_existing_list(driver, list_name)
    if existing:
        log.info(f"List '{list_name}' exists (ID: {existing})"); return existing
    try:
        btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Create lead list')]")))
        btn.click(); time.sleep(1)
        inp = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text']")))
        inp.clear(); inp.send_keys(list_name); time.sleep(0.5)
        save = driver.find_element(By.XPATH, "//button[contains(., 'Save') or contains(., 'Create')]")
        save.click(); time.sleep(DELAY_BETWEEN_SAVES)
        new_id = find_existing_list(driver, list_name)
        if new_id:
            log.info(f"Created list '{list_name}' (ID: {new_id})"); return new_id
    except Exception as e:
        log.error(f"Failed to create list: {e}")
    return None
def search_and_save_contact(driver, contact, company, list_id):
    name = contact["name"]
    title_kw = extract_title_keywords(contact.get("title", ""))
    keywords = urllib.parse.quote(f"{name} {company} {title_kw}".strip())
    url = SALESNAV_SEARCH_URL.format(keywords=keywords)
    driver.get(url)
    time.sleep(DELAY_BETWEEN_SEARCHES)
    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "ol.search-results, .artdeco-list")))
    except TimeoutException:
        log.warning(f"  No results for {name}"); return False
    try:
        results = driver.find_elements(By.CSS_SELECTOR, "li.artdeco-list__item")
        if not results:
            return False
        first = results[0]
        try:
            save_btn = first.find_element(By.XPATH, ".//button[contains(., 'Save') and not(contains(., 'Saved'))]")
            save_btn.click(); time.sleep(1)
            return select_list_in_modal(driver, list_id)
        except NoSuchElementException:
            try:
                first.find_element(By.XPATH, ".//button[contains(., 'Saved')]")
                log.info(f"  {name} already saved"); return True
            except: pass
    except Exception as e:
        log.error(f"  Error: {e}")
    return False
def select_list_in_modal(driver, list_id):
    try:
        time.sleep(1)
        options = driver.find_elements(By.CSS_SELECTOR, "label, div[class*='list-option']")
        for opt in options:
            if list_id in (opt.get_attribute("data-list-id") or opt.text or ""):
                opt.click(); break
        done = driver.find_elements(By.XPATH, "//button[contains(., 'Save') or contains(., 'Done')]")
        for b in done:
            if b.is_displayed(): b.click(); break
        time.sleep(DELAY_BETWEEN_SAVES)
        return True
    except: return False
def extract_title_keywords(title):
    kw = ["CIO","CTO","CDO","CISO","VP","Director","Head","Chief","Architect","Engineering","Technology","DevOps","Platform","Cloud","Digital","AI"]
    return " ".join([w for w in kw if w.upper() in title.upper()][:3])
# ===========================================================================
# PHASE 3: Outreach Messages
# ===========================================================================
def generate_outreach(contacts, report):
    if not ANTHROPIC_AVAILABLE or not os.environ.get("ANTHROPIC_API_KEY"):
        return {}
    ctx = {}
    for entry in report.get("top_10_companies", []):
        ctx[entry["company"]] = {
            "triggers": [l["headline"] for l in entry.get("leads",[])[:3]],
            "service": entry["leads"][0]["liatrio_service_area"] if entry.get("leads") else ""
        }
    prompt = """Generate consultant-style outreach for each company. RULES:
- VERY bare about Liatrio. Do NOT sell.
- Formula: Relevancy → Problem → Solution hint → Consultant CTA
- 3-4 sentences max. One message per company.
- JSON only: {"messages": {"Company": "message"}}
Companies:\\n"""
    for co, c in ctx.items():
        prompt += f"\\n{co}: {'; '.join(c['triggers'][:2])}"
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    msg = client.messages.create(model="claude-sonnet-4-20250514", max_tokens=4000,
                                  messages=[{"role":"user","content":prompt}])
    m = re.search(r'\\{[\\s\\S]*\\}', msg.content[0].text)
    if m:
        try: return json.loads(m.group()).get("messages", {})
        except: pass
    return {}
# ===========================================================================
# MAIN PIPELINE
# ===========================================================================
def run_pipeline(args):
    date_str = args.date or datetime.datetime.now().strftime("%Y-%m-%d")
    report_path = OUTPUT_DIR / f"full_report_{date_str}.json"
    if not report_path.exists():
        log.error(f"Report not found: {report_path}. Run lead_generator.py first."); sys.exit(1)
    log.info(f"{'='*60}\\nLIATRIO SALES NAV AUTOMATION — {date_str}\\n{'='*60}")
    with open(report_path) as f:
        report = json.load(f)
    # Phase 1: Research
    contacts_file = CONTACTS_DIR / f"contacts_{date_str}.json"
    if args.skip_research and contacts_file.exists():
        log.info("Loading cached contacts...")
        with open(contacts_file) as f: contacts = json.load(f)
    else:
        contacts = research_contacts_with_claude(str(report_path))
        CONTACTS_DIR.mkdir(parents=True, exist_ok=True)
        with open(contacts_file, "w") as f: json.dump(contacts, f, indent=2)
    total = sum(len(v) for v in contacts.values())
    log.info(f"Contacts: {total} across {len(contacts)} companies")
    # Phase 2: Outreach
    messages = {}
    if not args.no_outreach:
        log.info("Generating outreach messages...")
        messages = generate_outreach(contacts, report)
        if messages:
            p = CONTACTS_DIR / f"outreach_{date_str}.json"
            with open(p, "w") as f: json.dump(messages, f, indent=2)
    # Phase 3: Browser automation
    if not args.no_browser:
        log.info("Opening Sales Navigator...")
        driver = create_driver(args.chrome_profile)
        try:
            if not verify_salesnav_session(driver): return
            for company, cc in contacts.items():
                log.info(f"\\n{'─'*40}\\n{company} ({len(cc)} contacts)\\n{'─'*40}")
                list_id = None
                if not args.no_save:
                    list_id = create_lead_list(driver, f"{company} - {date_str}")
                for c in cc:
                    if list_id:
                        ok = search_and_save_contact(driver, c, company, list_id)
                        log.info(f"  [{'OK' if ok else 'FAIL'}] {c['name']} — {c.get('title','')}")
                    else:
                        kw = urllib.parse.quote(f"{c['name']} {company}")
                        driver.execute_script(f"window.open('{SALESNAV_SEARCH_URL.format(keywords=kw)}','_blank')")
                        log.info(f"  [TAB] {c['name']}")
                    time.sleep(1.5)
        finally:
            if not args.close_browser:
                log.info("Browser left open for review.")
            else:
                driver.quit()
    # Summary CSV
    summary = OUTPUT_DIR / f"salesnav_summary_{date_str}.csv"
    with open(summary, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["Company","Name","Title","LinkedIn URL","Sales Nav Search URL","Outreach"])
        for co, cc in contacts.items():
            msg = messages.get(co, "")
            for c in cc:
                kw = urllib.parse.quote(f"{c['name']} {co}")
                w.writerow([co, c["name"], c.get("title",""), c.get("linkedin_url",""),
                           SALESNAV_SEARCH_URL.format(keywords=kw), msg])
    log.info(f"Summary: {summary}")
def main():
    p = argparse.ArgumentParser(description="Liatrio Sales Nav Automation")
    p.add_argument("--date", help="Date (YYYY-MM-DD), default=today")
    p.add_argument("--skip-research", action="store_true")
    p.add_argument("--no-browser", action="store_true")
    p.add_argument("--no-save", action="store_true")
    p.add_argument("--no-outreach", action="store_true")
    p.add_argument("--close-browser", action="store_true")
    p.add_argument("--chrome-profile", help="Chrome user data dir")
    main_args = p.parse_args()
    run_pipeline(main_args)
if __name__ == "__main__":
    main()
```
---
## File 2: Updated `requirements.txt`
```
feedparser==6.0.11
gspread==6.1.2
google-auth==2.29.0
requests==2.31.0
selenium==4.27.1
anthropic==0.42.0
