import time

from css_selectors import (
    AGREEMENT_CHECKBOX,
    CHAT_WITH_US_BTN,
    EMAIL_SELECTOR,
    NAME_SELECTOR,
    SUBMIT_FORM,
    TERMS_BTN_AGREE,
    THINGS_YOU_SHOULD_KNOW,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

NAME = "Syed"
EMAIL = "syed@bitcot.com"


import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Initialize the WebDriver


def visit_the_website(host, driver, wait, retries=3, delay=10):
    for attempt in range(retries):
        try:
            driver.get(f"{host}")
            time.sleep(delay)
            chat_with_us = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, CHAT_WITH_US_BTN))
            )
            chat_with_us.click()
            # If the click was successful, break out of the retry loop
            break
        except Exception as e:
            print(f"Attempt {attempt+1} failed with error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)


def fill_user_info(driver, wait):
    # username_field = driver.find_element(By.XPATH, '//*[@id="exampleInputEmail1"]')
    # username_field.send_keys(
    #     "bitcot"
    # )  # Replace "username" with the ID of your username input field

    # password_field = driver.find_element(
    #     By.XPATH, '//*[@id="exampleInputName"]'
    # )  # Replace "password" with the ID of your password input field
    # password_field.send_keys("123")

    # login_button = driver.find_element(
    #     By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div/form/div/button'
    # )  # Replace "submitButton" with the ID or XPath of your login button
    # login_button.click()

    username = wait.until(EC.element_to_be_clickable((By.ID, "exampleInputEmail1")))
    username.send_keys("bitcot")
    password = wait.until(EC.element_to_be_clickable((By.ID, EMAIL_SELECTOR)))
    password.send_keys(EMAIL)
    driver.find_element(By.CSS_SELECTOR, AGREEMENT_CHECKBOX).click()
    driver.find_element(By.CSS_SELECTOR, SUBMIT_FORM).click()
    scrollable_feed = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, THINGS_YOU_SHOULD_KNOW))
    )
    # Use JavaScript to scroll
    driver.execute_script(
        "arguments[0].scrollTop = arguments[0].scrollHeight", scrollable_feed
    )
    terms_btn = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, TERMS_BTN_AGREE))
    )
    terms_btn.click()
    EC.text_to_be_present_in_element(
        (By.CSS_SELECTOR, "div[class*=chat_header] h4"), "syed-test"
    )
    time.sleep(5)

    # login_button = driver.find_element(
    #     By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div/form/div/button'
    # )  # Replace "submitButton" with the ID or XPath of your login button
    # login_button.click()
