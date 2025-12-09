import json

import pandas as pd

# Update './contacts.json' to match the path of your downloaded json file, if applicable
with open("./contacts.json", encoding="utf-8") as f:
    data = json.load(f)

address_book = pd.DataFrame(data)
address_book.to_excel("./data/minted-addresses-converted.xlsx")
address_book.to_csv("./data/minted-addresses-converted.csv", index=False)
