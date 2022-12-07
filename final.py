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
import PySimpleGUI as sg
# from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import time
import queue
import os
import sys

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

            scroll(wd, 5)
            scroll(wd, 5)

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
                time.sleep(15)
                button.click()
                time.sleep(20)
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
    def __init__(self, buffer, lock, p_counter, e_counter, thread_id = 1):
        multiprocessing.Process.__init__(self)
        self.queue = buffer
        self.thread_id = thread_id
        self.p_counter = p_counter
        self.e_counter = e_counter
        self.lock = lock
    def run(self):
        print("Doing the consumer task")
        time.sleep(25)
        print("Consumer: Starting loop")
        while True:
            personnel_id = self.queue.get() #queue.get()
            self.lock.acquire()
            self.p_counter.value += 1
            self.lock.release()
            if personnel_id == None:
                break
            # wd = webdriver.Edge(URL + '?personnel=' + personnel_id)
            wd = webdriver.Edge(PATH)
            wd.get(f'{URL}?personnel={personnel_id}')


            name = wd.find_element(By.TAG_NAME, 'h3').get_attribute('innerHTML')

            dept_info = wd.find_element(By.CLASS_NAME, 'list-unstyled.text-capitalize.text-center').find_elements(By.TAG_NAME,'li')
            position = dept_info[0].get_attribute('innerHTML')[6:-7]
            department = dept_info[1].get_attribute('innerHTML')[6:-7]

            try:
                email_button = wd.find_element(By.CSS_SELECTOR, '.btn.btn-sm.btn-block.text-capitalize')

                # if email_button.get_attribute('href') and re.match(r'^mailto:[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', email_button.get_attribute('href')):
                email = email_button.get_attribute('href')[7:]
            except:
                print("No email")
                continue

            print([name, department, position, email])
            self.lock.acquire()
            # write to csv file
            # check if email.csv exists
            # if not, create it
            # if yes, append to it
            self.e_counter.value += 1
            with open('data.csv', 'a') as f:
                f.write(f'{name},{department},{position},{email}\n')
            # close file
            self.lock.release()
            wd.close()

# class writer(multiprocessing.Process):
#     def __init__(self, buffer, thread_id = 1):
#         multiprocessing.Process.__init__(self)
#         self.queue = buffer
#         self.thread_id = thread_id
#     def run(self):
#         print("Doing the writer task")
#         time.sleep(30)
#         with open('data.csv', 'w') as f:
#             f.write('Name,Department,Position,Email')

def scroll(wd, delay):
    wd.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(delay)

def main():
    sg.theme('DarkTeal9')
    layout = [
        [sg.Text("E-mail Web Scraper")],
        [sg.Text("Enter URL:"), sg.InputText()],
        [sg.Text("Enter Time to Scrape:"), sg.InputText()],
        [sg.Text("Enter Number of Threads(Optional):"), sg.InputText()],
        [sg.Button("Start"), sg.Button("Exit")]
    ]

    window = sg.Window("E-mail Web Scraper", layout)
    while True:
        event, values = window.read()
        if event == sg.WIN_CLOSED or event == "Exit":
            break
        
        if values[0] == "" or values[1] == "":
            sg.popup("Please enter a URL and time to scrape")
        else:
            if values[2] == "":
                buffer = multiprocessing.Queue()
                # info = multiprocessing.Queue()
                lock = multiprocessing.Lock()

                num_consumers = 4
                manager=multiprocessing.Manager()
                page_counter =manager.Value('i',0)
                email_counter = manager.Value('i',0)

                num_emails = 0
                
                # if data.csv exists, delete it
                if os.path.exists('data.csv'):
                    os.remove('data.csv')
                # create data.csv
                with open('data.csv', 'w') as f:
                    f.write('LastName,FirstName,Department,Position,Email\n')

                p = producer(buffer, 1)
                print(p)
                p.start()

                consumers = []
                for i in range(num_consumers):
                    c = consumer(buffer, lock, page_counter, email_counter, i)
                    consumers.append(c)
                    c.start()

                # print the current time
                print(time.strftime("%H:%M:%S", time.localtime()))
                print("Start")
                time.sleep(int(values[1]) * 60)
                print("End")
                print(time.strftime("%H:%M:%S", time.localtime()))
                p.terminate()
                for c in consumers:
                    c.terminate()

                p.join()
                for c in consumers:
                    c.join()

                print(page_counter.value)
                print(email_counter.value)

                # if stat.txt exists, delete it
                if os.path.exists('stat.txt'):
                    os.remove('stat.txt')
                # create stat.txt
                with open('stat.txt', 'w') as f:
                    f.write(f'URL scraped: {URL}\n')
                    f.write(f'Number of pages scraped: {page_counter.value}\n')
                    f.write(f'Number of emails scraped: {email_counter.value}\n')
                sys.exit(0)
            else:
                buffer = multiprocessing.Queue()
                # info = multiprocessing.Queue()
                lock = multiprocessing.Lock()

                num_consumers = int(values[2])
                manager=multiprocessing.Manager()
                page_counter =manager.Value('i',0)
                email_counter = manager.Value('i',0)

                num_emails = 0
                
                # if data.csv exists, delete it
                if os.path.exists('data.csv'):
                    os.remove('data.csv')
                # create data.csv
                with open('data.csv', 'w') as f:
                    f.write('LastName,FirstName,Department,Position,Email\n')

                p = producer(buffer, 1)
                print(p)
                p.start()

                consumers = []
                for i in range(num_consumers):
                    c = consumer(buffer, lock, page_counter, email_counter, i)
                    consumers.append(c)
                    c.start()

                # print the current time
                print(time.strftime("%H:%M:%S", time.localtime()))
                print("Start")
                time.sleep(int(values[1]) * 60)
                print("End")
                print(time.strftime("%H:%M:%S", time.localtime()))
                p.terminate()
                for c in consumers:
                    c.terminate()

                p.join()
                for c in consumers:
                    c.join()

                print(page_counter.value)
                print(email_counter.value)
                # if stat.txt exists, delete it
                if os.path.exists('stat.txt'):
                    os.remove('stat.txt')
                # create stat.txt
                with open('stat.txt', 'w') as f:
                    f.write(f'URL scraped: {URL}\n')
                    f.write(f'Number of pages scraped: {page_counter.value}\n')
                    f.write(f'Number of emails scraped: {email_counter.value}\n')
                sys.exit(0)

if __name__ == '__main__':
    main()