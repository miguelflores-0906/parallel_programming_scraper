import threading
import PySimpleGUI as sg
from collections import deque
from urllib.parse import urlsplit
from bs4 import BeautifulSoup
import pandas as pd
import requests
import re

def start_scrape(starting_url, time, num_threads):
    unscraped = deque([starting_url])
    scraped = set()
    emails = set()

    while len(unscraped):
        url = unscraped.popleft()
        scraped.add(url)

        parts = urlsplit(url)

        base_url = "{0.scheme}://{0.netloc}".format(parts)
        if '/' in parts.path:
            path = url[:url.rfind('/')+1]
        else:
            path = url
        print("Crawling URL %s" % url)
        try:
            response = requests.get(url)
        except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            continue
 
        new_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.com", response.text, re.I))
        ph_emails = set(re.findall(r"[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.ph", response.text, re.I))
        emails.update(new_emails) 
        emails.update(ph_emails)
    
        soup = BeautifulSoup(response.text, 'lxml')
    
        for anchor in soup.find_all("a"):
            if "href" in anchor.attrs:
                link = anchor.attrs["href"]
            else:
                link = ''
        
                if link.startswith('/'):
                    link = base_url + link
                
                elif not link.startswith('http'):
                    link = path + link

    df = pd.DataFrame(emails, columns=["Email"]) # replace with column name you prefer
    df.to_csv('email.csv', index=False)
    return

def main():
    # print("Hello World")
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
        # values[0] is the URL
        # values[1] is the time to scrape
        if values[0] == "" or values[1] == "":
            sg.popup("Please enter a URL and time to scrape")
        else:
            if values[2] == "":
                start_scrape(values[0], values[1], 3)
            else:
                start_scrape(values[0], values[1], values[2])
    return

if __name__ == '__main__':
    main()