import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def open_browser_and_press_key(url, key_to_press):
    """
    Opens a Chrome browser, navigates to a URL, and simulates a keypress on the page.

    Args:
        url (str): The URL to navigate to.
        key_to_press: The key to press. Should be a value from selenium.webdriver.common.keys.Keys.
                      For example, Keys.SPACE, Keys.ENTER, or a character like 'a'.
    """
    print("Setting up the Chrome browser...")
    # Automatically downloads and manages the correct chromedriver
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

    try:
        print(f"Navigating to {url}...")
        driver.get(url)

        # Use an explicit wait for better reliability.
        # Waits up to 10 seconds for the body element to be present.
        wait = WebDriverWait(driver, 10)
        body = wait.until(EC.presence_of_element_located((By.TAG_NAME, 'body')))

        print(f"Simulating keypress on the page body.")
        body.send_keys(key_to_press)

        # Wait a moment to observe the action.
        print("Action complete. Browser will close shortly.")
        time.sleep(3)

    finally:
        # This block ensures the browser is always closed, even if errors occur.
        print("Closing the browser.")
        driver.quit()

if __name__ == '__main__':
    # Example usage: Go to Google and press the SPACE key.
    open_browser_and_press_key("https://www.google.com", Keys.SPACE)