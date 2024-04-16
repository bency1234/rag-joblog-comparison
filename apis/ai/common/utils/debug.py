import csv
import os
import time

from common.envs import get_secret_value_from_environment, logger

from ..colors import (
    pr_green,
    pr_light_gray,
    pr_light_purple,
    pr_pink,
    pr_red,
    pr_yellow,
)
from ..constants import COST, INITIAL_PROMPT, INITIAL_RESPONSE

VERBOSE = get_secret_value_from_environment("VERBOSE")
DEBUG_CSV = get_secret_value_from_environment("DEBUG_CSV")


FIELDS_DICT = {1: 2, 2: 3, 3: 4, 4: 5, INITIAL_PROMPT: 6, INITIAL_RESPONSE: 7, COST: 8}
FIELDS = [
    "user_input",
    "bot_response",
    "level1",
    "level2",
    "level3",
    "level4",
    INITIAL_PROMPT,
    INITIAL_RESPONSE,
    COST,
]
MAX_COLUMNS = len(FIELDS)
INITIAL_ROW = [""] * MAX_COLUMNS


def debug_steps(row, msg, level):
    """Debugs and logs the steps of a process."""

    if VERBOSE == "True":
        LOG = f"[DEBUG] - Level {level} - {msg}"
        current_message = row[FIELDS_DICT[level]]
        row[FIELDS_DICT[level]] = f"{current_message}\n{LOG}"
        pr_green(LOG)
        logger.info("=" * 20)


def debug(msg):
    """Prints a debug message."""

    if VERBOSE == "True":
        pr_pink(f"[DEBUG] - {msg}")


def debug_attribute(attribute, value):
    """Prints a debug message with attribute and value."""

    if VERBOSE == "True":
        pr_light_purple(attribute, end="")
        pr_yellow(value, end="\n")


def debug_error(msg):
    """Prints an error message in red."""

    pr_red(f"[ERROR] - {msg}")


def time_it(func):
    """Decorator function to measure the execution time of a function."""

    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        execution_time = end_time - start_time
        pr_light_gray(f"{func.__name__} took {execution_time:.5f} seconds to execute.")
        return result

    return wrapper


@time_it
def write_logs_to_csv(row, bot_response):
    """Writes logs to a CSV file."""

    if VERBOSE == "True" and DEBUG_CSV:
        debug(f"Writing the logs in {DEBUG_CSV}")
        MODE = "a" if os.path.exists(DEBUG_CSV) else "w"
        with open(DEBUG_CSV, MODE) as csvfile:
            # creating a csv writer object
            csvwriter = csv.writer(csvfile)

            if MODE == "w":
                # writing the fields
                csvwriter.writerow(FIELDS)

            row_length = len(row)
            if row_length != MAX_COLUMNS - 1:
                dummy_rows_to_add = MAX_COLUMNS - row_length - 2
                row.extend(("-" * dummy_rows_to_add).split("-"))
            # writing the data rows
            row[1] = bot_response
            csvwriter.writerows([row])
