## Minted.com Address Book Export
My fiancée and I were just under 100 days until our wedding and I was trying to export the addresses that we had previously saved to [minted.com](https://minted.com) from our Save the Dates, but was dismayed to learn that there was no export feature!
So I built a Python script to effectively export the saved address book.

Check out my [blog post](https://medium.com/@willkarnasiewicz/wedding-planning-meets-hacking-1c95be79035e) for more info.

## 2025 Update (Special thanks to @hantswilliams for his contributions!)
Minted has updated their website since the original script was written. Key changes include:
- **New login page**: Login is now at `https://login.minted.com/` (previously `https://www.minted.com/login`)
- **Updated form fields**: The email field ID changed from `email` to `identifierMNTD`
- **New address book URL**: `https://www.minted.com/addressbook/my-account/finalize/0`
- **Selenium 4.x compatibility**: Updated to use the new `Service` object pattern

A new script `minted_address_export.py` has been created to handle these changes. The legacy `minted_api_request.py` script is still available but may not work with the current Minted website.

## Usage
There are currently two different ways to implement this tool and export your address book from minted.com:
1. **Automated script** (recommended): Export data as CSV and XLSX files using Python and Selenium WebDriver. See [Automated Method](#getting-started---automated-method) below.
2. **Manual approach**: Download the data as a JSON file and optionally convert to CSV or XLSX formats. See [Manual Method](#getting-started---manual-approach) below.

## Getting Started - Automated Method
1. Assuming you have [Python 3.9+](https://www.python.org) and a [GitHub](https://www.github.com) account, clone the repo:

```bash
git clone https://github.com/wkarney/minted-export.git
```

2. Navigate into the repository you just cloned:

```bash
cd minted-export
```

3. Start a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

>You can deactivate the virtual environment with `deactivate`.

4. Export your Minted address book:

Before getting the addresses, you'll need to have your Minted login credentials handy.
You can add them as environment variables called `minted_email` and `minted_password`, or simply run the script and input them when prompted.

```bash
# Option 1: Set environment variables (optional)
export minted_email="your@email.com"
export minted_password="yourpassword"

# Option 2: Run the script (will prompt for credentials if not set)
python minted_address_export.py
```

The script will:
- Open a Chrome browser window (non-headless by default so you can see what's happening)
- Log in to your Minted account
- First attempt to export via the API endpoint
- Fall back to scraping the address book page if the API is unavailable
- Export your contacts to CSV and XLSX files in the `data/` directory

**Note**: If automated login fails (due to CAPTCHA, 2FA, etc.), the script will pause and prompt you to complete the login manually in the browser window, then press Enter to continue.

### Troubleshooting
- **Browser window doesn't appear**: Check your Dock for a Chrome icon and click it to bring the window forward
- **Login fails**: The script will prompt you to complete login manually if automatic login doesn't work
- **"No module named 'openpyxl'"**: Run `pip install openpyxl`

## Getting Started - Manual Approach
If you are having issues setting up the Python environment or running the automated script, there's a more manual method available.

1. Navigate to [Minted](https://www.minted.com) in your browser and login. Once logged in, navigate to https://addressbook.minted.com/api/contacts/contacts/?format=json.

2. Save the page source to this directory on your computer. This should be a .json file containing all of your address book entries.

In order to convert this JSON file to a CSV or XLSX file, you can either use a json-csv converter of your choice (e.g. https://json-csv.com), or run the script included in this repo.

3. Make sure you have your Python environment setup [(see Steps 1-3 above)](#getting-started---automated-method).

To run the conversion script:

```bash
python convert_json.py
```
Running the above will convert the JSON file and save both CSV and XLSX files into the `data/` dir of the project.

See the [example folder](./example/) for example input/output of the `convert_json.py` script.

## Scripts

| Script | Description |
|--------|-------------|
| `minted_address_export.py` | **Recommended (2025)** - Updated script with new login flow and selectors |
| `minted_api_request.py` | Legacy script (may not work with current Minted website) |
| `convert_json.py` | Convert manually downloaded JSON to CSV/XLSX |

## Requirements
- Python 3.9+
- Chrome browser installed
- Dependencies listed in `requirements.txt`:
  - pandas
  - selenium
  - requests
  - beautifulsoup4
  - webdriver-manager
  - openpyxl

### Need Assistance?
Are you running into an issue and don't know what to do next? Write a comment in [the discussions page](https://github.com/wkarney/minted-export/discussions) and I'll help you get it sorted.

### Improvements & Suggestions
Experienced developer with comments or tweaks? Fork the repo and file a pull request with your changes.
