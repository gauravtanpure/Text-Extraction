import os
import time
import re
import fitz  # PyMuPDF
import pandas as pd
import requests
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# === Setup ===
DOWNLOAD_DIR = r"D:\Prasaar_ML\Text_Extraction\PDFS"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 15)

driver.get("https://maharera.maharashtra.gov.in/agents-search-result")
time.sleep(4)

rows = driver.find_elements(By.CSS_SELECTOR, "table tbody tr")
print(f"🔍 Found {len(rows)} agent rows")

results = []

def download_pdf(pdf_url, filename):
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(pdf_url, headers=headers, timeout=15)
        if r.status_code == 200 and 'application/pdf' in r.headers.get('Content-Type', ''):
            file_path = os.path.join(DOWNLOAD_DIR, filename)
            with open(file_path, 'wb') as f:
                f.write(r.content)
            return file_path
    except Exception as e:
        print(f"❌ Error downloading PDF: {e}")
    return None

def extract_office_number(pdf_path):
    try:
        with fitz.open(pdf_path) as doc:
            text = "\n".join([page.get_text() for page in doc])
        patterns = [
            r'Office\s*Mobile\s*Number\s*[:\-]?\s*(\d{10})',
            r'Mobile\s*Number\s*[:\-]?\s*(\d{10})',
            r'Mobile\s*[:\-]?\s*(\d{10})',
            r'Phone\s*[:\-]?\s*(\d{10})'
        ]
        for pat in patterns:
            match = re.search(pat, text, re.IGNORECASE)
            if match:
                return match.group(1)
        match = re.search(r'\b\d{10}\b', text)
        return match.group(0) if match else "NOT FOUND"
    except:
        return "ERROR"

for idx, row in enumerate(rows):
    try:
        agent_name = row.find_element(By.XPATH, "./td[2]").text.strip()
        print(f"\n🔄 Processing {agent_name}...")

        # Open modal
        view_btn = row.find_element(By.CSS_SELECTOR, 'a[data-aflag="DocAgentViewCert"]')
        driver.execute_script("arguments[0].click();", view_btn)
        time.sleep(2)

        # Find eye icon
        eye_icon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[target="_blank"] > i.fa-eye')))
        parent_link = eye_icon.find_element(By.XPATH, "..")
        pdf_page_url = parent_link.get_attribute("href")

        # Open PDF page in new tab
        driver.execute_script("window.open(arguments[0]);", pdf_page_url)
        time.sleep(4)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(4)

        pdf_url = driver.current_url
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # Close modal
        try:
            close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.close')))
            close_btn.click()
        except:
            driver.execute_script("$('.modal').modal('hide');")

        # Download PDF
        filename = f"agent_{idx+1}.pdf"
        pdf_path = download_pdf(pdf_url, filename)

        # Extract number
        if pdf_path:
            office_number = extract_office_number(pdf_path)
        else:
            office_number = "NO PDF"

        results.append({
            "Agent Name": agent_name,
            "Office Number": office_number
        })

        print(f"✅ Done: {agent_name} → {office_number}")

    except Exception as e:
        print(f"❌ Failed for row {idx+1}: {e}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        results.append({
            "Agent Name": f"Row {idx+1}",
            "Office Number": "ERROR"
        })
        continue

driver.quit()

# Save to CSV
df = pd.DataFrame(results)
csv_path = os.path.join(DOWNLOAD_DIR, "agent_office_numbers.csv")
df.to_csv(csv_path, index=False)
print(f"\n✅ All done. Results saved to {csv_path}")
