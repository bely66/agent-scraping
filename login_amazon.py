import os
# load dotenv in the base root
from dotenv import load_dotenv

# load the .env file
load_dotenv()

# get the environment variables
username = os.getenv("amz_mail")
password = os.getenv("amz_pass")

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time

# Create a new instance of the Chrome driver
driver = webdriver.Chrome()


try:
    # Open amazon.eg
    driver.get("https://www.amazon.eg")

    # Find the login button and click it
    login_button = driver.find_element(By.XPATH, "//a[contains(normalize-space(), 'تسجيل الدخول')]")
    login_button.click()

    # Wait for 2 seconds
    # time.sleep(2)

    # Find all text input elements
    text_inputs = driver.find_elements(By.TAG_NAME, "input")

    # Loop through the input elements to find the username/email field
    for input_element in text_inputs:
        name_attr = input_element.get_attribute('name')
        if name_attr and ("user" in name_attr.lower() or "email" in name_attr.lower()):
            input_element.send_keys(username)  # Replace with your email
            input_element.send_keys(Keys.ENTER)
            break

    # Wait for 2 seconds
    time.sleep(2)

    # Find the password input field and enter the password
    password_input = driver.find_element(By.XPATH, "//input[contains(@type, 'password')]")
    password_input.send_keys(password)  # Replace with your password

    password_input.send_keys(Keys.ENTER)

    time.sleep(2)

    # Find the 'Your Orders' button and click it
    orders_button = driver.find_element(By.XPATH, "//a[contains(normalize-space(), 'Orders')]")
    orders_button.click()

    # find drop down menu containing the years of orders on the left side of "placed in" text
    drop_down_menu = driver.find_element(By.XPATH, "//select[contains(@name, 'orderFilter')]")
    
    # Find all order detail elements
    order_objects = driver.find_elements(By.XPATH, "//div[contains(normalize-space(), 'View order details')]")
    order_urls = []
    for order in order_objects:
        view_order_button = order.find_element(By.XPATH, ".//a[contains(normalize-space(), 'View order details')]")
        order_urls.append(view_order_button.get_attribute('href'))

    # Visit each order detail page and download the HTML
    for url in order_urls:
        driver.get(url)
        time.sleep(2)  # Adjust as needed
        order_html = driver.page_source
        with open(f"order_{order_urls.index(url)}.html", "w", encoding="utf-8") as file:
            file.write(order_html)


    time.sleep(5)

finally:
    # Close the driver
    driver.quit()