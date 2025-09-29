import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

DOWNLOAD_DIR = r"D:\Coding\luigella\downloads" # <-- CHANGE THIS PATH

def open_browser_and_press_key(url, *keys_to_press):
    print("Setting up the Chrome browser...")

    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    # --- Configure Chrome Options ---
    chrome_options = Options()
    prefs = {"download.default_directory": DOWNLOAD_DIR}
    chrome_options.add_experimental_option("prefs", prefs)
    
    # Add arguments for running in a stable, automated environment
    chrome_options.add_argument("--no-sandbox") # Bypasses OS security model, required for some environments
    chrome_options.add_argument("--disable-dev-shm-usage") # Overcomes limited resource problems
    # chrome_options.add_argument("--headless") # Runs Chrome without a GUI, essential for servers
    chrome_options.add_argument("--window-size=1920,1080") # Set a window size for headless mode

    # Use the local chromedriver.exe from the project's root folder
    # This avoids issues with automatic driver downloads.
    driver = webdriver.Chrome(options=chrome_options)

    downloaded_file_path = None
    try:
        files_before = set(os.listdir(DOWNLOAD_DIR))
        print(f"Navigating to {url}...")
        driver.get(url)

        wait = WebDriverWait(driver, 10)
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

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
        print("Closing the browser.")
        driver.quit()
    
    return downloaded_file_path

if __name__ == '__main__':
    open_browser_and_press_key("https://www.google.com", Keys.CONTROL, Keys.ALT, 's')