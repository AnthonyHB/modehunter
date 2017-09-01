from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bs4 import BeautifulSoup as bsoup
import datetime as dt
import requests as rq
import pandas as pd
import numpy as np
import smtplib
import os

def send_email(units):
    unit_string = ""
    for unit in units:
        unit_string = unit_string + """- {}
    """.format(unit)
    text = """Hello, there are new units on Modeapts.com available: 

    {}""".format(unit_string)

    myEmail = input('My Email: ')
    myPassword = input('My Password: ')
    
    recipient1 = input('Sending To: ')

    recipients = [recipient1]

    msg = MIMEMultipart()
    text = MIMEText(text)

    msg.attach(text)

    # Send email
    msg['Subject'] = "Mode Units"
    msg['To'] = ", ".join(recipients)
    msg['From'] = myEmail

    mail = smtplib.SMTP(host='smtp.office365.com', port=587)
    mail.starttls()
    mail.login(myEmail, myPassword)
    mail.sendmail(myEmail, recipients, msg.as_string())
    mail.quit()

with rq.Session() as s:
    url = "http://modeapts.com/apartments-for-rent-in-phoenix-az/"
    r = s.get(url)
soup = bsoup(r.content, "lxml") 
units = {}

# For Rent
unit_num = 1
for div1 in soup.find_all("div", {"class": "ezcol ezcol-one-third"}):
    unit = str(unit_num)
    for a in div1.find_all("a"):
        # Get text from li, and use it to calculate totals
        data = a.get('title')
        link = a.get('href')
        text = a.get_text()

        if text and data:
            if data != "Check Availability":
                if link:
                    units.update({unit: {'name': text, 'url': link}})
                else:
                    units.update({unit: {'name': text, 'url': 'N/A'}})

    for p in div1.find_all('p'):
        for br in p.find_all('br'):
            next_s = br.nextSibling
            if not (next_s):
                continue
            next2_s = next_s.nextSibling
            if next2_s and next2_s.name == 'br':
                text = str(next_s).strip()
                if not 'Bed' in text and unit in units:
                    units[unit].update({'address': text})
                elif unit in units:
                    units[unit].update({'specs': text})
    unit_num = unit_num + 1

web_df = pd.DataFrame.from_dict(units, orient='index')
web_df = web_df.set_index('name')
web_df.sort_index(axis=1, inplace=True)
web_units = web_df.index

my_df = pd.read_csv('units.csv', index_col='name')
my_units = my_df.index

new_units = set(web_units) - set(my_units)

if new_units:
    send_email(new_units)
    web_df.to_csv('units.csv', header=True, index=True)
else:
    print("No email sent.")
