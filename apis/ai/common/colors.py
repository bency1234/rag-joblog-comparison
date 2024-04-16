# Reference - https://www.geeksforgeeks.org/print-colors-python-terminal/

"""Prints the given text in the specified color."""
from common.envs import logger


def pr_light_gray(skk):
    logger.info(f"\033[90m {skk}\033[00m")


def pr_red(skk):
    # Use for errors but ensure sensitive details are not logged
    logger.info(f"\033[91m {skk}\033[00m")


def pr_green(skk):
    logger.info(f"\033[92m {skk}\033[00m")


def pr_yellow(skk):
    logger.info(f"\033[93m {skk}\033[00m")


def pr_light_purple(skk):
    logger.info(f"\033[94m {skk}\033[00m")


def pr_purple(skk):
    logger.info(f"\033[95m {skk}\033[00m")


def pr_black(skk):
    # Corrected ANSI code for black
    logger.info(f"\033[30m {skk}\033[00m")


def pr_pink(skk):
    # Corrected ANSI code for pink if intended (assuming light magenta)
    logger.info(f"\033[95m {skk}\033[00m")


def pr_cyan(skk):
    logger.info(f"\033[96m {skk}\033[00m")


def pr_bot_response(msg):
    # Consider using a more appropriate log level if this contains sensitive info
    pr_cyan(f"Bot: {msg}")
