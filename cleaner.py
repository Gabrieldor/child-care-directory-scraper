import pandas as pd
import requests
from multiprocessing import Pool
from itertools import repeat
import traceback

def test(info):
        tu, df = info
        index, row = tu
        print(f"Testing {row[1]}")

        try:
            r = requests.get(row[1], timeout=25)
            if r.status_code != 200:
                return index
        except:
            return index


if __name__ == "__main__":
    df = pd.read_excel("results - Copy (2).xlsx")[5000:]
    df.drop_duplicates(inplace=True)
    info = []

    for index, row in df.iterrows():
        try:
            remove = True
            email = row[3].lower()
            name_raw = row[0]
            web = row[1]
            info.append((index, row))

            if "//www." in web:
                web = web.split("//www.")[1].split(".")[0]
            else:
                web = web.split(".")[0].split("//")[1]

            try:
                initials = "".join([x[0].lower() for x in name_raw.split(" ")])[:2]
            except:
                initials = ""

            name = "".join(name_raw.split(" ")).lower()

            for n in name_raw.split(" "):
                n = n.lower().replace("'s", '')
                if n in email:
                    remove = False

            if (initials not in email and name not in email and web not in email and remove == True and "kid" not in email and "dance" not in email) or ("middleschool" in name or "college" in name or "highschool" in name):
                df.drop(index, inplace=True)
        except:
            print(traceback.format_exc())
            df.drop(index, inplace=True)
        

    indexes = []
        
    with Pool(32) as p:
        res = p.imap_unordered(test, zip(info, repeat(df)))
        for r in res:
            print(r)
            indexes.append(r)

    print("Started dropping")
        
    for index, row in df.iterrows():
        print("next row")
        if index in indexes:
            print(f"{index} dropped")
            df.drop(index, inplace=True)

    print(df.info())
    df.to_excel("testing.xlsx", index = False)