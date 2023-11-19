import os
from time import sleep

import pandas as pd
import requests
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

# Webdriver options; set to headless
options = Options()
options.add_argument("--headless")
driver = Chrome(executable_path=ChromeDriverManager().install(), options=options)

# URL for minted login page
URL = "https://www.minted.com/login"

# Set your minted.com email and password as the env vars:
# minted_email and minted_password
try:
    minted_email = os.environ["minted_email"]
except KeyError:
    minted_email = input("Enter your minted.com email address:")
try:
    minted_password = os.environ["minted_password"]
except KeyError:
    minted_password = input("Enter your minted.com password:")

driver.get(URL)

# Selenium deals with lgin form
email_elem = driver.find_element(By.NAME, "email")
email_elem.send_keys(minted_email)
password_elem = driver.find_element(By.NAME, "password")
password_elem.send_keys(minted_password)
login_submit = driver.find_element(
    By.XPATH, "/html/body/div/div[3]/div/form/div[2]/button[1]"
)
login_submit.click()

sleep(5)  # to load JS and be nice

# Obtain cookies from selenium session
cookies = {c["name"]: c["value"] for c in driver.get_cookies()}

# Request address book contents as json
response = requests.get(
    "https://addressbook.minted.com/api/contacts/contacts/?format=json", cookies=cookies
)
listings = response.json()

# Create dataframe to hold addresses
address_book = pd.DataFrame(listings)

# Export to excel and csv
address_book.to_excel("./data/minted-addresses-api.xlsx")
address_book.to_csv("./data/minted-addresses-api.csv", index=False)

# Close selenium webdriver
driver.close()
