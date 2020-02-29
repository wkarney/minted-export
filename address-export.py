import pandas as pd
from selenium import webdriver
from bs4 import BeautifulSoup
from time import sleep
import re
import os

# Webdriver options; set to headless
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(options=options)

# URL for minted addressbook
url = 'https://www.minted.com/addressbook/my-account/finalize/0?it=utility_nav'


states = {
        'AK': 'Alaska',
        'AL': 'Alabama',
        'AR': 'Arkansas',
        'AS': 'American Samoa',
        'AZ': 'Arizona',
        'CA': 'California',
        'CO': 'Colorado',
        'CT': 'Connecticut',
        'DC': 'District of Columbia',
        'DE': 'Delaware',
        'FL': 'Florida',
        'GA': 'Georgia',
        'GU': 'Guam',
        'HI': 'Hawaii',
        'IA': 'Iowa',
        'ID': 'Idaho',
        'IL': 'Illinois',
        'IN': 'Indiana',
        'KS': 'Kansas',
        'KY': 'Kentucky',
        'LA': 'Louisiana',
        'MA': 'Massachusetts',
        'MD': 'Maryland',
        'ME': 'Maine',
        'MI': 'Michigan',
        'MN': 'Minnesota',
        'MO': 'Missouri',
        'MP': 'Northern Mariana Islands',
        'MS': 'Mississippi',
        'MT': 'Montana',
        'NA': 'National',
        'NC': 'North Carolina',
        'ND': 'North Dakota',
        'NE': 'Nebraska',
        'NH': 'New Hampshire',
        'NJ': 'New Jersey',
        'NM': 'New Mexico',
        'NV': 'Nevada',
        'NY': 'New York',
        'OH': 'Ohio',
        'OK': 'Oklahoma',
        'OR': 'Oregon',
        'PA': 'Pennsylvania',
        'PR': 'Puerto Rico',
        'RI': 'Rhode Island',
        'SC': 'South Carolina',
        'SD': 'South Dakota',
        'TN': 'Tennessee',
        'TX': 'Texas',
        'UT': 'Utah',
        'VA': 'Virginia',
        'VI': 'Virgin Islands',
        'VT': 'Vermont',
        'WA': 'Washington',
        'WI': 'Wisconsin',
        'WV': 'West Virginia',
        'WY': 'Wyoming'
}


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

# Login form
emailElem = driver.find_element_by_name('email')
emailElem.send_keys(minted_email) 
passwordElem = driver.find_element_by_name('password')
passwordElem.send_keys(minted_password) 
loginSubmit = driver.find_element_by_class_name('loginButton')
loginSubmit.click()

sleep(5) # to load JS and be nice

driver.get('https://addressbook.minted.com/api/contacts/contacts/print/?')

html = driver.page_source
soup = BeautifulSoup(html, 'lxml')
listings = soup.find('main')

address_book = pd.DataFrame()
addressees = listings.find_all('span',{'class':'contact-name'})
address_book['name'] = [name.text.strip() for name in addressees]
addresses = listings.find_all('span',{'class':'contact-address'})
street_details = [''.join(street.text.strip().split('\n')[:-1]).strip() for street in addresses]
address_book['address'] = [' '.join(street.split()) for street in street_details]
city_details = [street.text.strip().split('\n')[-1].strip() for street in addresses]
address_book['locality'] = [_ for _ in city_details]

def pull_state(address):
    try:
        field = re.findall(r'([a-zA-Z]{2,}) (\d{5})',address)[0][0]
        state = states.get(field.upper(), field)
    except:
        state = ''
    return state

def pull_zip(address):
    try:
        zipcode = re.findall(r'([a-zA-Z]{2,}) (\d{5})',address)[0][1]
    except:
        zipcode = ''
    return zipcode

address_book['state'] = address_book['locality'].apply(pull_state)
address_book['zipcode'] = address_book['locality'].apply(pull_zip)
address_book['town'] = address_book['locality'].map(lambda x: x.split(',')[0])

columnsTitles = ['Name', 'Address', 'Town', 'State','Zipcode']

address_book.to_excel('./data/minted-addresses.xlsx')
address_book.to_csv('./data/minted-addresses.csv', index=False)

driver.close()
