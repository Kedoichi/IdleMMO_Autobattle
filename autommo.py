import os
import time
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, WebDriverException
from retrying import retry

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

options = Options()
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

# Wait for the page to load
wait = WebDriverWait(driver, 10)

@retry(stop_max_attempt_number=3, wait_fixed=2000)
def get_url_with_retry(url):
    try:
        driver.get(url)
    except WebDriverException as e:
        logger.error(f"WebDriverException occurred: {e}")
        raise

def login():
    try:
        get_url_with_retry(os.getenv('BASE_URL'))
        loginBtn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Log in")))
        loginBtn.click()

        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(os.getenv('EMAIL'))

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(os.getenv('PASSWORD'))

        submit_button = driver.find_element(By.TAG_NAME, "button")
        submit_button.click()

        logger.info("Logged in successfully")
    except Exception as e:
        logger.error(f"Login failed: {e}")

# ... [rest of your functions remain the same, just replace print with logger.info or logger.error] ...

def main_loop():
    login()
    time.sleep(2)  # Wait for page to load after login
    while True:
        try:
            if not check_and_click_hunt_button():
                perform_conditional_click()
            time.sleep(0.5)  # Wait for 0.5 second before the next iteration
        except KeyboardInterrupt:
            logger.info("Script stopped by user.")
            break
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            time.sleep(0.5)  # Wait a bit before retrying

# Run the main loop
if __name__ == "__main__":
    try:
        main_loop()
    finally:
        driver.quit()