import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException

# Load environment variables
load_dotenv()

options = Options()
options.add_experimental_option("detach", True)

# For Heroku deployment, we need to use these options
options.add_argument("--headless")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Navigate to the login page
driver.get(os.getenv('BASE_URL'))

# Wait for the page to load
wait = WebDriverWait(driver, 10)

def login():
    try:
        loginBtn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, "Log in")))
        loginBtn.click()

        email_field = wait.until(EC.presence_of_element_located((By.ID, "email")))
        email_field.send_keys(os.getenv('EMAIL'))

        password_field = driver.find_element(By.ID, "password")
        password_field.send_keys(os.getenv('PASSWORD'))

        submit_button = driver.find_element(By.TAG_NAME, "button")
        submit_button.click()

        print("Logged in successfully")
    except Exception as e:
        print(f"Login failed: {e}")

def safe_get_text(xpath):
    try:
        return wait.until(EC.presence_of_element_located((By.XPATH, xpath))).text
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
        return None

def safe_click(xpath):
    try:
        wait.until(EC.element_to_be_clickable((By.XPATH, xpath))).click()
        return True
    except (NoSuchElementException, TimeoutException, StaleElementReferenceException):
        return False

def check_and_click_hunt_button():
    hunt_button_xpath = '//*[@id="game-container"]/div/div[2]/div[1]/div[1]/div[2]/div/div/div/div[1]/button'
    button_text = safe_get_text(hunt_button_xpath)
    if button_text == "Start Hunt":
        if safe_click(hunt_button_xpath):
            print("Clicked 'Start Hunt' button successfully.")
            return True
    return False

def perform_conditional_click():
    value_xpath = "/html/body/div[1]/main/div[1]/div/div[2]/div[2]/div/div[2]/div[1]/div[1]/div[2]/div/div[2]/div[1]/button/div"
    button_xpath = '//*[@id="game-container"]/div/div[2]/div[1]/div[1]/div[2]/div/div[2]/div[1]/button'
    alt_button_xpath = '//*[@id="game-container"]/div/div[2]/div[1]/div[1]/div[2]/div/div/div/div[1]/button'

    value_text = safe_get_text(value_xpath)
    
    if value_text is not None and float(value_text) > 0:
        print(f"Current value: {value_text}")
        if safe_click(button_xpath):
            print("Clicked the main button successfully.")
            time.sleep(0.2)
            time.sleep(20)
        elif safe_click(alt_button_xpath):
            print("Clicked the alternative button successfully.")
        else:
            print("Failed to click both buttons.")
    else:
        print("The value is not greater than 0 or element not found.")

def main_loop():
    login()
    time.sleep(2)  # Wait for page to load after login
    while True:
        try:
            if not check_and_click_hunt_button():
                perform_conditional_click()
            time.sleep(0,5)  # Wait for 1 second before the next iteration
        except KeyboardInterrupt:
            print("Script stopped by user.")
            driver.quit()
            break
        except Exception as e:
            print(f"An error occurred: {e}")
            time.sleep(0.5)  # Wait a bit before retrying

# Run the main loop
if __name__ == "__main__":
    main_loop()