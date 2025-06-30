import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
# === Setup download directory ===
DOWNLOAD_DIR = r"D:\Prasaar_ML\Text_Extraction\PDFS"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
# === Chrome options ===
chrome_options = Options()
chrome_options.add_experimental_option("prefs", {
    "download.default_directory": DOWNLOAD_DIR,
    "download.prompt_for_download": False,
    "plugins.always_open_pdf_externally": False  # Use Chrome PDF Viewer
})
chrome_options.add_argument("--start-maximized")
# === Start driver ===
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
wait = WebDriverWait(driver, 20)
# === Load the site ===
driver.get("https://maharera.maharashtra.gov.in/agents-search-result")
time.sleep(5)
# === Find 'View Application' buttons ===
view_app_buttons = driver.find_elements(By.CSS_SELECTOR, 'a[data-aflag="DocAgentViewCert"]')
print(f"🔍 Found {len(view_app_buttons)} 'View Application' buttons")
for idx, btn in enumerate(view_app_buttons):
    try:
        driver.execute_script("arguments[0].scrollIntoView(true);", btn)
        time.sleep(1)
        btn.click()
        print(f"🟡 Opened 'View Application' modal for row {idx+1}")
        time.sleep(2)
        # Click eye icon
        eye_icon = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[target="_blank"] > i.fa-eye')))
        parent_link = eye_icon.find_element(By.XPATH, "..")
        parent_link.click()
        print(f"👁️ Opened PDF in new tab for row {idx+1}")
        time.sleep(2)
        # Switch to new tab (PDF preview)
        driver.switch_to.window(driver.window_handles[1])
        # Wait for iframe
        iframe = wait.until(EC.presence_of_element_located((By.TAG_NAME, "iframe")))
        driver.switch_to.frame(iframe)
        # Click the download arrow
        download_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[aria-label="Download"]')))
        download_btn.click()
        print(f"✅ Clicked download for row {idx+1}")
        time.sleep(4)  # Allow time to download
        # Close iframe tab and return to main window
        driver.switch_to.default_content()
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        # Close the modal
        close_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button.close')))
        close_btn.click()
        time.sleep(1)
    except Exception as e:
        print(f"❌ Failed for row {idx+1}: {e}")
        if len(driver.window_handles) > 1:
            driver.close()
            driver.switch_to.window(driver.window_handles[0])
        try:
            close = driver.find_element(By.CSS_SELECTOR, 'button.close')
            close.click()
        except:
            pass
        continue
driver.quit()
print("✅ All PDFs processed.")