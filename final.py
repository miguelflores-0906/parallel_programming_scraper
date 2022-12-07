# Web Scraping Libraries
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import codecs
import re
import requests
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time

# Threading and Multiprocessing Libraries
import multiprocessing

# Setup Variables
# SERVICE = Service(ChromeDriverManager().install())
OPTIONS = Options()
OPTIONS.add_argument('--headless')

PATH = "D:\Documents\DLSU\Year 4 Term 1\OPESY\email_scraper\parallel_programming_scraper\msedgedriver.exe"

# Constants
URL = "https://www.dlsu.edu.ph/staff-directory"

def scroll(wd, delay):
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(delay)

def producer():

    wd = webdriver.Edge(PATH)
    wd.get(URL)

    time.sleep(1)

    while True:

        scroll(wd, 5)
        scroll(wd, 5)

        # find button with onClick = "personnelLoadMoreAction()"
        try:
            button = wd.find_element(By.XPATH, "//button[@onclick='personnelLoadMoreAction()']")
            print(button)
            person = wd.find_elements(By.NAME, "personnel")
            print(len(person))
            button.click()
            time.sleep(10)
        except:
            print("cannot find button")
            break

    # get the value attribute of each personnel
    for p in person:
        val_queue.append(p.get_attribute('value'))

    wd.close()


val_queue = []

wd = webdriver.Edge(PATH)
wd.get(URL)

time.sleep(10)

# get the value attribute of each personnel
# for p in person:
#     val_queue.append(p.get_attribute('value'))

while True:

    scroll(wd, 5)
    scroll(wd, 5)

    # find button with onClick = "personnelLoadMoreAction()"
    try:
        button = wd.find_element(By.XPATH, "//button[@onclick='personnelLoadMoreAction()']")
        print(button)
        person = wd.find_elements(By.NAME, "personnel")
        print(len(person))
        button.click()
        time.sleep(10)
    except:
        print("cannot find button")
        break


# wd.close()