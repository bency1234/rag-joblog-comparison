import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

# Initialize the WebDriver
browser = webdriver.Chrome(
    "/home/andrea/.cache/selenium/chromedriver/linux64/124.0.6367.155/chromedriver"
)  # Change this to the WebDriver you downloaded
username = "bitcot"
# Navigate to the login page
browser.get(
    "https://d22e4rw124x1ri.cloudfront.net/"
)  # Replace with your login page URL

# Find the username and password fields and enter your credentials
username_field = browser.find_element(By.XPATH, '//*[@id="exampleInputEmail1"]')
username_field.send_keys(
    "bitcot"
)  # Replace "username" with the ID of your username input field

password_field = browser.find_element(
    By.XPATH, '//*[@id="exampleInputName"]'
)  # Replace "password" with the ID of your password input field
password_field.send_keys("123")

login_button = browser.find_element(
    By.XPATH, '//*[@id="root"]/div/div[2]/div[1]/div/div/form/div/button'
)  # Replace "submitButton" with the ID or XPath of your login button
login_button.click()


# username_field.send_keys("bitcot")  # Replace "your_username" with your actual username
# password_field.send_keys("123")  # Replace "your_password" with your actual password

# Submit the form (assuming there's a submit button)
# submit_button = driver.find_element_by_id("submit")  # Replace "submit" with the ID of your submit button
# submit_button.click()

# Optionally, add a delay to see the result
time.sleep(5)  # Waits for 5 seconds
