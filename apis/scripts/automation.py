import datetime
import os
import re
import time

import pandas as pd
import xlsxwriter
from common.envs import logger
from scripts.constants import MAX_REQUESTS_PER_MINUTE, TIME_INTERVAL
from scripts.css_selectors import RESPONSE_CONTAINER
from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from tqdm import tqdm
from webdriver_manager.chrome import ChromeDriverManager

logger.info(f"XLSX Writer version - {xlsxwriter.__version__}")

HOST = os.getenv("HOST")

WAIT_TIMEOUT = 40
SHEET_COLUMNS = ["USER_INPUT", "RESPONSE", "HTML_RESPONSE"]

# Get the current date and time
current_datetime = datetime.datetime.now()

# Format the timestamp as a string
timestamp_str = current_datetime.strftime("%Y%m%d%H%M%S")

INPUT_SHEET_PATH = os.getenv("INPUT_SHEET_PATH")
URL = os.getenv("URL")
file_name_without_extension = os.path.splitext(os.path.basename(INPUT_SHEET_PATH))[0]
OUTPUT_SHEET_PATH = f"joblog_{file_name_without_extension}_{timestamp_str}.xlsx"

driver = webdriver.Chrome(
    service=ChromeService(ChromeDriverManager().install())
)  # Change this to the WebDriver you downloaded
# If you are getting issues with chrome driver, please download the chrome driver from https://googlechromelabs.github.io/chrome-for-testing/#stable and uncomment below code
# driver = webdriver.Chrome(executable_path='./chromedriver')
wait = WebDriverWait(driver, WAIT_TIMEOUT)
driver.get(URL)


def validating_timestamp_and_process_excel(
    requests_in_current_minute, data_dict, start_time
):
    records = df
    combined_df = pd.DataFrame(columns=SHEET_COLUMNS)

    with tqdm(total=len(records)) as pbar:
        for index, row in df.iterrows():
            time.sleep(5)
            # Check if the current minute has elapsed or if the request limit is reached
            current_time = time.time()
            elapsed_time = current_time - start_time

            if elapsed_time >= TIME_INTERVAL:
                # If a new minute has started, reset the request counter
                start_time = current_time
                requests_in_current_minute = 0

            if requests_in_current_minute >= MAX_REQUESTS_PER_MINUTE:
                sleep_time = TIME_INTERVAL - elapsed_time % TIME_INTERVAL
                logger.info(f"Sleeping {sleep_time} seconds")
                # If the request limit is reached for this minute, wait until the next minute
                time.sleep(sleep_time)
                # Reset the request counter for the new minute
                requests_in_current_minute = 0

            # To pass the user input to the bot and get the response
            response_df = fetch_user_input_and_get_response(row, index, skipped_rows)
            if response_df is not None:
                combined_df = pd.concat([combined_df, response_df], ignore_index=True)
            # Increment the request counter for the current minute
            requests_in_current_minute += 1

            pbar.update(1)

    # Store the DataFrame for the current sheet in the dictionary
    data_dict[sheet_name] = combined_df
    return data_dict


def fetch_user_input_and_get_response(row, index, skipped_rows):
    user_input = row["user_input"]

    if len(user_input) < 500:
        try:
            input_element = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, "#myTextArea"))
            )
            input_element.clear()

            logger.info(f"Trying this question - {user_input}")

            lines = re.split(r"[\n\t]", user_input)

            # Iterate through each line and send it to the text area
            for line in lines:
                input_element.send_keys(line)
                input_element.send_keys(Keys.SHIFT + Keys.ENTER)

            input_element.send_keys(Keys.RETURN)

            # Find the element with a class containing "bot_span"
            check_element_length(RESPONSE_CONTAINER, index + 1 - skipped_rows)
            all_paragraphs = driver.find_elements(By.CSS_SELECTOR, RESPONSE_CONTAINER)
            response = all_paragraphs[-1]

            if "Sorry" in response.text:
                time.sleep(5)

            response_df = pd.DataFrame(
                {
                    SHEET_COLUMNS[0]: [user_input],
                    SHEET_COLUMNS[1]: [response.text],
                    SHEET_COLUMNS[2]: [response.get_attribute("innerHTML")],
                }
            )
            return response_df
        except NoSuchElementException as e:
            # Handle the case where the input element is not found
            logger.info(f"Element not found for index {index}: {e}")
    else:
        skipped_rows += 1
        response = "Question is too long"
        response_df = pd.DataFrame(
            {
                SHEET_COLUMNS[0]: [user_input],
                SHEET_COLUMNS[1]: [response],
                SHEET_COLUMNS[2]: [response],
            }
        )
        return response_df


def check_element_length(css_selector, length):
    selector = (By.CSS_SELECTOR, css_selector)
    elements = wait.until(EC.presence_of_all_elements_located(selector))
    while len(elements) != length:
        time.sleep(10)
        elements = driver.find_elements(*selector)


def store_response_in_excel(data_dict):
    # Create an Excel writer
    writer = pd.ExcelWriter(OUTPUT_SHEET_PATH, engine="xlsxwriter")

    # Save each DataFrame in a separate sheet
    for sheet_name, df in data_dict.items():
        df.to_excel(writer, sheet_name=sheet_name, index=False)

    # Close the writer to save the Excel file
    writer.close()


combined_df = pd.DataFrame()

xls = pd.ExcelFile(INPUT_SHEET_PATH)


# Create a dictionary to store DataFrames for each sheet
data_dict = {}


for sheet_name in xls.sheet_names:
    df = pd.read_excel(xls, sheet_name=sheet_name)

    # Initialize a counter to keep track of requests in the current minute
    requests_in_current_minute = 0

    # Initialize the start_time variable to track the current minute
    start_time = time.time()

    skipped_rows = 0

    data_dict = validating_timestamp_and_process_excel(
        requests_in_current_minute, data_dict, start_time
    )

store_response_in_excel(data_dict)
