from function_gen import InstructionCompiler
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from dotenv import load_dotenv
import os

# load the .env file
load_dotenv()

# get the environment variables
username = os.getenv("amz_mail")
password = os.getenv("amz_pass")
with open("manual_plan.txt", "r") as f:
    instructions = f.read()

compiler = InstructionCompiler(instructions=instructions, model='gpt-4o-mini')

# Create a new instance of the Chrome driver
env = webdriver.Chrome()


