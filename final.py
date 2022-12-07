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
import queue

# Threading and Multiprocessing Libraries
import multiprocessing
from threading import Thread

# Setup Variables
# SERVICE = Service(ChromeDriverManager().install())
OPTIONS = Options()
OPTIONS.add_argument('--headless')

PATH = "D:\Documents\DLSU\Year 4 Term 1\OPESY\email_scraper\parallel_programming_scraper\msedgedriver.exe"

# Constants
URL = "https://www.dlsu.edu.ph/staff-directory"


class producer(multiprocessing.Process):
    def __init__(self, buffer, thread_id = 1):
        multiprocessing.Process.__init__(self)
        self.queue = buffer
        self.thread_id = thread_id
    def run(self):
        print("I will do the producer task")
        # producer_task(self.queue)
        wd = webdriver.Edge(PATH)
        wd.get(URL)

        time.sleep(20)

        scraped = []

        while True:

            scroll(wd, 2)
            scroll(wd, 2)

            # find button with onClick = "personnelLoadMoreAction()"
            try:
                not_scraped = []
                button = wd.find_element(By.XPATH, "//button[@onclick='personnelLoadMoreAction()']")
                print(button)
                person = wd.find_elements(By.NAME, "personnel")
                print(len(person))
                for p in person:
                    if p not in scraped:
                        scraped.append(p)
                        not_scraped.append(p)

                for p in not_scraped:
                    personnel_id = p.get_attribute('value')
                    print(personnel_id)
                    if personnel_id:
                        print("It exists")
                        self.queue.put(personnel_id)
                        print(personnel_id)

                button.click()
                time.sleep(10)
            except Exception as e:
                print(e)
                print("cannot find button")
                break
        self.queue.put(None)
        self.queue.put(None)
        self.queue.put(None)
        self.queue.put(None)
        self.queue.put(None)
        # get the value attribute of each personnel

        wd.close()

class consumer(multiprocessing.Process):
    def __init__(self, buffer, thread_id = 1):
        multiprocessing.Process.__init__(self)
        self.queue = buffer
        self.thread_id = thread_id
    def run(self):
        print("Doing the consumer task")
        time.sleep(25)
        print("Consumer: Starting loop")
        while True:
            personnel_id = self.queue.get() #queue.get()
            if personnel_id == None:
                break
            # wd = webdriver.Edge(URL + '?personnel=' + personnel_id)
            wd = webdriver.Edge(PATH)
            wd.get(f'{URL}?personnel={personnel_id}')


            name = wd.find_element(By.TAG_NAME, 'h3').get_attribute('innerHTML')

            dept_info = wd.find_element(By.CLASS_NAME, 'list-unstyled.text-capitalize.text-center').find_elements(By.TAG_NAME,'li')
            position = dept_info[0].get_attribute('innerHTML')[6:-7]
            department = dept_info[1].get_attribute('innerHTML')[6:-7]

            email_button = wd.find_element(By.CSS_SELECTOR, '.btn.btn-sm.btn-block.text-capitalize')
            email = email_button.get_attribute('href')[7:]

            print([name, department, position, email])
            wd.close()

def scroll(wd, delay):
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(delay)

def producer_task(buffer):

    wd = webdriver.Edge(PATH)
    wd.get(URL)

    time.sleep(10)

    while True:

        scroll(wd, 2)
        scroll(wd, 2)

        # find button with onClick = "personnelLoadMoreAction()"
        try:
            button = wd.find_element(By.XPATH, "//button[@onclick='personnelLoadMoreAction()']")
            print(button)
            person = wd.find_elements(By.NAME, "personnel")
            print(len(person))

            for p in person:
                if p.get_attribute('value') not in buffer:
                    buffer.put(p.get_attribute('value'))

            button.click()
            time.sleep(10)
        except:
            print("cannot find button")
            break
    buffer.put(None)
    buffer.put(None)
    buffer.put(None)
    buffer.put(None)
    buffer.put(None)
    # get the value attribute of each personnel

    wd.close()

def consumer_task(buffer):
    # wd = webdriver.Chrome(service = SERVICE, options = OPTIONS)
    time.sleep(15)
    while True:
        personnel_id = buffer.get() #queue.get()
        if personnel_id == None:
            break
        # wd = webdriver.Edge(URL + '?personnel=' + personnel_id)
        wd = webdriver.Edge(PATH)
        wd.get(f'{URL}?personnel={personnel_id}')


        name = wd.find_element(By.TAG_NAME, 'h3').get_attribute('innerHTML')

        dept_info = wd.find_element(By.CLASS_NAME, 'list-unstyled.text-capitalize.text-center').find_elements(By.TAG_NAME,'li')
        position = dept_info[0].get_attribute('innerHTML')[6:-7]
        department = dept_info[1].get_attribute('innerHTML')[6:-7]

        email_button = wd.find_element(By.CSS_SELECTOR, '.btn.btn-sm.btn-block.text-capitalize')
        email = email_button.get_attribute('href')[7:]

        print([name, department, position, email])
        wd.close()
    
# lock = multiprocessing.Lock()

def main():
    buffer = multiprocessing.Queue()

    num_consumers = 4

    p = producer(buffer, 1)
    print(p)
    p.start()

    consumers = []
    for i in range(num_consumers):
        c = consumer(buffer, i)
        consumers.append(c)
        c.start()

    p.join()
    for c in consumers:
        c.join()

if __name__ == '__main__':
    main()