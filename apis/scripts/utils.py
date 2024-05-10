import os
import time

from scripts.css_selectors import LOGIN_BTN, PASSWORD_ELEMENT, USERNAME_ELEMENT
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

# Initialize the WebDriver
USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")


def visit_the_website(host, driver, retries=3, delay=10):
    for attempt in range(retries):
        try:
            driver.get(f"{host}")
            # If the click was successful, break out of the retry loop
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed with error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)


def fill_user_info(wait):
    username = wait.until(EC.element_to_be_clickable((By.ID, USERNAME_ELEMENT)))
    username.send_keys(USERNAME)
    password = wait.until(EC.element_to_be_clickable((By.ID, PASSWORD_ELEMENT)))
    password.send_keys(PASSWORD)

    login = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, LOGIN_BTN)))
    login.click()

    time.sleep(5)
