import os
import time
import logging
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from agents import InstructionCompiler
import os

html_tmp = 'html_data/'

# Create folder if it does not exist
if not os.path.exists(html_tmp):
    os.makedirs(html_tmp)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables
load_dotenv()
amz_username = os.getenv("amz_mail")
amz_password = os.getenv("amz_pass")

# Read instructions from file
with open("instructions.txt", "r") as f:
    instructions = f.read()

# Initialize Instruction Compiler

# Function to execute actions
def execute_action(action, ldict, compiler, max_attempts=3):
    action = action.replace("```", "")
    action = action.replace("python", "")
    for attempt in range(1, max_attempts + 1):
        try:
            print(action)
            exec(action, globals(), ldict)
            logging.info(f"Action executed successfully on attempt {attempt}")
            return True
        except Exception as e:
            logging.error(f"Attempt {attempt} failed with error: {e}")
            # retry the compiler again
            action = compiler.retry(str(e))['action_output']
            action = action.replace("```", "")
            action = action.replace("python", "")
            time.sleep(1)
    return False

# Main function to perform the automation
def html_scraper():
    # Create a new instance of the Chrome driver
    compiler = InstructionCompiler(instructions=instructions, model='gpt-4o-mini')

    driver = webdriver.Chrome()
    ldict = {"env": driver, "Keys": Keys,}

    try:
        while compiler.instructions_queue:
            # Fetch the next instruction step
            step = compiler.step()
            instruction = step["instruction"]
            action = step["action_output"]
            logging.info(f"Instruction: {instruction}")

            logging.info(f"Action: {action}")

            # Attempt to execute the action
            if not execute_action(action, ldict, compiler):
                logging.error("Failed to execute action after multiple attempts")
                break
    finally:
        # Ensure the browser is closed
        driver.quit()

if __name__ == "__main__":
    html_scraper()
