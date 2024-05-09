import time

from css_selectors import (
    USERNAME_ELEMENT, PASSWORD_ELEMENT, LOGIN_BTN
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

import time

from selenium.webdriver.common.by import By

# Initialize the WebDriver


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
    username.send_keys("bitcot")
    password = wait.until(EC.element_to_be_clickable((By.ID, PASSWORD_ELEMENT)))
    password.send_keys("123")
    
    login = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, LOGIN_BTN)))
    login.click()
    
    time.sleep(5)

