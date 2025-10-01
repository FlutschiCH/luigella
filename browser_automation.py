import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DOWNLOAD_DIR = r"downloads"  # <-- CHANGE THIS PATH
PROFILE_DIR = r"chrome_profile" # Directory to store cookies and user data

def create_new_driver():
    """Configures and creates a new Selenium WebDriver instance."""
    # --- Configure Chrome Options ---
    chrome_options = Options()
    # When using a user profile, Chrome's saved settings can override the download path.
    # This more comprehensive pref dictionary forces Chrome to use the path specified here.
    prefs = {
        "download.default_directory": os.path.abspath(DOWNLOAD_DIR), # Use absolute path for reliability
        "download.prompt_for_download": False, # Disable the "Save As..." dialog
        "download.directory_upgrade": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)
    if not os.path.exists(PROFILE_DIR):
        os.makedirs(PROFILE_DIR)
    
    # Add arguments for running in a stable, automated environment
    chrome_options.add_argument(f"--user-data-dir={os.path.abspath(PROFILE_DIR)}") # This line saves cookies/logins
    chrome_options.add_argument("--no-sandbox")  # Bypasses OS security model
    chrome_options.add_argument("--disable-dev-shm-usage")  # Overcomes limited resource problems
    # chrome_options.add_argument("--headless")  # Runs Chrome without a GUI
    chrome_options.add_argument("--window-size=1920,1080")  # Set window size

    # Use manually downloaded ChromeDriver from the project root
    chromedriver_path = os.path.join(os.path.dirname(__file__), "chromedriver" if os.name != "nt" else "chromedriver.exe")
    if not os.path.exists(chromedriver_path):
        raise FileNotFoundError(f"ChromeDriver not found at {chromedriver_path}. Please place chromedriver in the project root.")
    service = ChromeService(executable_path=chromedriver_path)
    return webdriver.Chrome(service=service, options=chrome_options)

def open_browser_and_press_key(url, timeframe=None, keys_to_press=()):
    driver = create_new_driver()
    downloaded_file_path = None
    try:
        files_before = set(os.listdir(DOWNLOAD_DIR))
        print(f"Navigating to {url}...")
        driver.get(url)

        time.sleep(5)
        wait = WebDriverWait(driver, 10)
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        if timeframe:
            print(f"Setting timeframe to '{timeframe}'...")
            # Type each character of the timeframe individually
            for char in str(timeframe):
                body.send_keys(char)
            body.send_keys(Keys.ENTER)
            print("Timeframe set. Waiting for chart to update...")
            time.sleep(3) # Give the chart a moment to load the new timeframe data

        print(f"Simulating keypress(es) on the page body.")
        body.send_keys(*keys_to_press)

        print("Waiting for download to complete...")
        end_time = time.time() + 20  # 20-second timeout for download
        new_file_path = None
        while time.time() < end_time:
            files_after = set(os.listdir(DOWNLOAD_DIR))
            new_files = files_after - files_before
            if new_files:
                new_file_name = new_files.pop()
                if new_file_name.endswith('.crdownload'):
                    time.sleep(0.5)
                    continue
                
                new_file_path = os.path.join(DOWNLOAD_DIR, new_file_name)
                print(f"Download detected: {new_file_name}")
                last_size = -1
                while last_size != os.path.getsize(new_file_path):
                    last_size = os.path.getsize(new_file_path)
                    time.sleep(1)
                downloaded_file_path = new_file_path
                print("Download complete.")
                break
            time.sleep(0.5)

    finally:
        if driver:
            print("Closing the browser.")
            driver.quit()
    
    return downloaded_file_path

if __name__ == '__main__':
    open_browser_and_press_key("https://www.tradingview.com/chart/?symbol=NASDAQ:AAPL", timeframe="240", keys_to_press=(Keys.CONTROL, Keys.ALT, 's'))