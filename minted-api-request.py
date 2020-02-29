from seleniumrequests import Chrome
from selenium.webdriver.chrome.options import Options
import os
from time import sleep
import pandas as pd

# Webdriver options; set to headless
options = Options()
options.add_argument("--headless")
driver = Chrome(options=options)

# URL for minted addressbook
url = 'https://www.minted.com/login'

# Set your minted.com email and password as the env vars:
# minted_email and minted_password
try:
    minted_email = os.environ['minted_email']
except KeyError:
    minted_email = input("Enter your minted.com email address:")
try:
    minted_password = os.environ['minted_password']
except KeyError:
    minted_password = input("Enter your minted.com password:")

driver.get(url)

# Selenium deals with lgin form
email_elem = driver.find_element_by_name('email')
email_elem.send_keys(minted_email)
password_elem = driver.find_element_by_name('password')
password_elem.send_keys(minted_password) 
login_submit = driver.find_element_by_class_name('loginButton')
login_submit.click()

sleep(5) # to load JS and be nice

# Request address book contents as json
response = driver.request('GET','https://addressbook.minted.com/api/contacts/contacts/?format=json')
listings = response.json()

# Create dataframe to hold addresses
address_book = pd.DataFrame(listings)

# Export to excel and csv
address_book.to_excel('./data/minted-addresses-api.xlsx')
address_book.to_csv('./data/minted-addresses-api.csv', index=False)

# Close selenium webdriver
driver.close()
