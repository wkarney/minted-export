## Minted.com Address Book Export
My fiancée and I were just under 100 days until our wedding and I was trying to export the addresses that we had previously saved to [minted.com](https://minted.com) from our Save the Dates, but was dismayed to learn that there was no export feature! 
So I built a Python script to effectively export the saved address book.

Check out my [blog post](https://medium.com/@willkarnasiewicz/wedding-planning-meets-hacking-1c95be79035e) for more info.

## Usage
Based on feedback (thanks, [@dlithio](https://github.com/wkarney/minted-export/discussions/7#discussion-71480)), there are currently two different ways to implement this tool and export your address book from minted.com.
1. Fully-automated scripts to export data as csv and xlsx files using Python and Selenium Webdriver. See below for [steps](#Getting-Started---Automated-Method) on how to run this script.
2. A more manual approach to download the data as a json file, and optionally convert to json to csv or xlsx formats. See below for [steps](#Getting-Started---Automated-Method) on how to run this script.

## Getting Started - Automated Method
1. Assuming you have [Python 3.6+](https://www.python.org) and a [GitHub](https://www.github.com) account, clone the repo:

```bash
git clone https://github.com/wkarney/minted-export.git
```

2. Navigate into the repository you just cloned:

```bash
cd minted-export
```

3. Start a virtual environment:

```bash
python3 -m venv env
source env/bin/activate
pip install --upgrade pip # Optional but helpful
pip install -r requirements-dev.txt
```

>You can deactivate the virtual environment with `deactivate`.


4. Export your Minted address book:

Before getting the addresses, you'll need to have your Minted login credentials handy. 
It might be helpful to add them as environment variables called `minted_email` and `minted_password`, respectively. Or simply run the script and input them when prompted.

To run the script:

```bash
python minted_api_request.py
```

Running the above will scrape all of the events and output the address book fields as csv and xlsx file into a new `data/` dir of the project.

## Getting Started - Manual Approach
If you are having issues setting up the Python environment or running the `minted_api_request.py` script, there's another more manual method that you can implement as well.

1. Navigate to [Minted](https://www.minted.com) in your browser and login. Once logged in, navigate to https://addressbook.minted.com/api/contacts/contacts/?format=json.

2. Save the page source to this directory on your computer. This should be a .json file containing all of your address book entries.

In order to convert this json file to a csv or xlsx file, you can either use a json-csv converter of your choice (e.g. https://json-csv.com), or run the script included in this repo.

3. Make sure you have your python environment setup [(see Steps 1-3 above)](#Getting-Started---Automated-Method).

To run the script:

```bash
python convert_json.py
```
Running the above will convert the json file and save both csv and xlsx files in a new `data/` dir of the project.

See the [example folder](./example/) for example input/output of the `convert_json.py` script. 🎅

### Need Assistance?
Are you running into an issue and don't know what to do next? Write a comment in [the discussions page](https://github.com/wkarney/minted-export/discussions) and I'll help you get it sorted.

### Improvements & Suggestions
Experienced developer with comments or tweaks? Fork the repo and file a pull request with your changes.
