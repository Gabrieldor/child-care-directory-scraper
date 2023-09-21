from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from multiprocessing import Pool
from itertools import repeat
import time
import pandas as pd
import traceback
import requests
from bs4 import BeautifulSoup as bs

#Name, Website, location, email, phone

class Scraper():
    def __init__(self):
        self.cities = [x[1] + ', ' + x[0] for x in pd.read_csv("cities.csv").values.tolist()]
        self.cities.append("New York, NY")
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
        with open("cats.txt", 'r') as f:
            self.cats = [x.strip() for x in f.readlines()]

        try:
            self.df = pd.read_excel("results.xlsx")
        except:
            self.df = pd.DataFrame()


    def save(self, res):
        self.df = pd.concat([self.df, pd.DataFrame(res)])
        self.df.drop_duplicates(inplace=True)
        self.df.to_excel("results.xlsx", index=False)


    def get_info(self, link):
        try:    
            r = requests.get(link)
            soup = bs(r.content, features="lxml")
            
            name = soup.find("h1", {"class": "dockable business-name"}).text
            try:
                website = soup.find("a", {"class": "website-link dockable"})["href"]
                phone = soup.find("a", {"class": "phone dockable"})["href"].split(":")[1]
                email = soup.find("a", {"class": "email-business"})["href"].split(":")[1]
                address = soup.find("span", {"class": "address"}).get_text(" - ")
            except:
                #print(traceback.format_exc())
                return

            return {"Name": name, "Website": website, "Address": address, "Email": email, "Phone": phone}
        except:
            print(traceback.format_exc())
            return


    def search(self, cat, city):
        try:
            links = []
            print("Opening Chrome")
            driver = webdriver.Chrome(options=self.chrome_options)
            driver.get(f"https://www.yellowpages.com/")

            driver.find_element(By.XPATH,"//input[@id='query']").send_keys(cat)

            driver.find_element(By.XPATH,"//input[@id='location']").clear()
            time.sleep(0.5)
            driver.find_element(By.XPATH,"//input[@id='location']").send_keys(city)

            driver.find_element(By.XPATH,"//button[@type='submit']").click()

            while True:
                links = links + [x.get_attribute("href") for x in driver.find_elements(By.XPATH, "//a[@class='business-name']")]
                try:
                    next = driver.find_element(By.XPATH, "//a[@class='next ajax-page']")
                    next.click()
                    time.sleep(5)
                except:
                    break
                
            print("Closing Chrome")
            driver.quit()
            result = []
            with Pool(16) as p:
                res = p.imap_unordered(self.get_info, links)
                for r in res:
                    print(r)
                    if r != None:
                        result.append(r)
            return result

        except:
            print(traceback.format_exc())
           


    def loop(self):
        for cat in self.cats:
            for city in self.cities:
                r = self.search(cat, city)
                self.save(r)




    


if __name__ == "__main__":
    s = Scraper()
    s.loop()


