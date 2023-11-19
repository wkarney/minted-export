import os
import re
from time import sleep

from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager

# Webdriver options; set to headless
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

# URL for minted addressbook
URL = "https://www.minted.com/addressbook/my-account/finalize/0?it=utility_nav"


states = {
    "AK": "Alaska",
    "AL": "Alabama",
    "AR": "Arkansas",
    "AS": "American Samoa",
    "AZ": "Arizona",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DC": "District of Columbia",
    "DE": "Delaware",
    "FL": "Florida",
    "GA": "Georgia",
    "GU": "Guam",
    "HI": "Hawaii",
    "IA": "Iowa",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "MA": "Massachusetts",
    "MD": "Maryland",
    "ME": "Maine",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MO": "Missouri",
    "MP": "Northern Mariana Islands",
    "MS": "Mississippi",
    "MT": "Montana",
    "NA": "National",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "NE": "Nebraska",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NV": "Nevada",
    "NY": "New York",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "PR": "Puerto Rico",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VA": "Virginia",
    "VI": "Virgin Islands",
    "VT": "Vermont",
    "WA": "Washington",
    "WI": "Wisconsin",
    "WV": "West Virginia",
    "WY": "Wyoming",
}


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

# Login form
email_elem = driver.find_element_by_name("email")
email_elem.send_keys(minted_email)
password_elem = driver.find_element_by_name("password")
password_elem.send_keys(minted_password)
login_submit = driver.find_element_by_xpath("/html/body/div/div[3]/div/form/div[2]/button[1]")
login_submit.click()

sleep(5)  # to load JS and be nice

driver.get("https://addressbook.minted.com/api/contacts/contacts/print/?")

html = driver.page_source
soup = BeautifulSoup(html, "lxml")
listings = soup.find("main")

address_book = pd.DataFrame()
addressees = listings.find_all("span", {"class": "contact-name"})
address_book["name"] = [name.text.strip() for name in addressees]
addresses = listings.find_all("span", {"class": "contact-address"})
street_details = [
    "".join(street.text.strip().split("\n")[:-1]).strip() for street in addresses
]
address_book["address"] = [" ".join(street.split()) for street in street_details]
city_details = [street.text.strip().split("\n")[-1].strip() for street in addresses]
address_book["locality"] = list(city_details)


def pull_state(address):
    """Isolates and formats State portion of address, if available"""
    try:
        field = re.findall(r"([a-zA-Z]{2,}) (\d{5})", address)[0][0]
        state = states.get(field.upper(), field)
    except:
        state = ""
    return state


def pull_zip(address):
    """Isolates and formats zipcode of address, if available"""
    try:
        zipcode = re.findall(r"([a-zA-Z]{2,}) (\d{5})", address)[0][1]
    except:
        zipcode = ""
    return zipcode


address_book["state"] = address_book["locality"].apply(pull_state)
address_book["zipcode"] = address_book["locality"].apply(pull_zip)
address_book["town"] = address_book["locality"].map(lambda x: x.split(",")[0])

column_titles = ["Name", "Address", "Town", "State", "Zipcode"]
address_book = address_book.reindex(columns=[col.lower() for col in column_titles])

address_book.to_excel("./data/minted-addresses.xlsx", header=column_titles)
address_book.to_csv("./data/minted-addresses.csv", index=False, header=column_titles)

driver.close()
