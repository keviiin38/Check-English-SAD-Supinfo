#!/usr/bin/python3

import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from selenium import webdriver

IDBOOSTER = ""
SUPINFO_PASSWORD = ""
GMAIL_ADDRESS = ""
GMAIL_PASSWORD = ""
RECEIVER_ADDRESS = ""
BROWSER = ""

if "" in (IDBOOSTER, SUPINFO_PASSWORD, GMAIL_ADDRESS, GMAIL_PASSWORD, RECEIVER_ADDRESS, BROWSER):
    print("Please run INSTALL.sh first !")
    exit(1)


def check_available_slot(inner_html):
    if "<span style=\"color: green;\">" in inner_html:
        return True
    else:
        return False


def get_date(inner_html):
    if "<span style=\"color: green;\">" not in inner_html:
        return False

    # Get the Year
    i = inner_html.index("2018</strong>")
    i_end = i + 4

    # Get the month
    while inner_html[i] != ">":
        i -= 1

    # Get the month and year
    date = str(inner_html[i + 1:i_end])

    # Get the time
    i = inner_html.index("<span style=\"color: green;\">")
    slot_time = inner_html[i + 28: i + 30] + "h to " + inner_html[i + 37: i + 39] + "h"

    # Get the day number
    i = inner_html.index("<span style=\"color: green;\">")

    while inner_html[i:i + 18] != "<span class=\"day\">":
        i += 1

    # Add some text
    date += " from " + slot_time

    if inner_html[i + 19] == "<":
        return str(inner_html[i + 18] + " " + date)
    else:
        return str(inner_html[i + 18:i + 20] + " " + date)


def send_mail(place_time):
    msg = MIMEMultipart()
    msg['From'] = GMAIL_ADDRESS
    msg['To'] = RECEIVER_ADDRESS
    msg['Subject'] = "[English - Check] " + str(len(place_time)) + " slot(s) available !"

    body = "They are " + str(len(place_time)) + " slot(s) available on http://english.sad.supinfo.com/\n\n"

    for slot_time in place_time:
        body += "The " + slot_time + "\n\n"

    msg.attach(MIMEText(body))

    mail_server = smtplib.SMTP('smtp.gmail.com', 587)
    mail_server.starttls()
    mail_server.login(GMAIL_ADDRESS, GMAIL_PASSWORD)
    mail_server.sendmail(GMAIL_ADDRESS, RECEIVER_ADDRESS, msg.as_string())
    mail_server.quit()


def get_html_site():
    if BROWSER == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--headless")
        browser = webdriver.Firefox(firefox_options=options)
    elif BROWSER in ("chrome", "chromium"):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")
        browser = webdriver.Chrome(chrome_options=options)

    # Go to the English website
    browser.get("http://english.sad.supinfo.com")

    time.sleep(2)

    # Find and input the IDBOOSTER
    id_booster = browser.find_element_by_name("boosterId")
    id_booster.send_keys(IDBOOSTER)

    # Log in to the website
    button = browser.find_element_by_xpath("//input[@value='Connexion']")
    button.click()

    time.sleep(2)

    # Log in to the SSO
    password = browser.find_element_by_id("Password")
    password.send_keys(SUPINFO_PASSWORD)

    button = browser.find_element_by_id("LoginButton")
    button.click()

    time.sleep(2)

    # Go to the calendar tab
    browser.get("http://english.sad.supinfo.com/student/calendar")

    time.sleep(2)

    return browser


def main():
    browser = get_html_site()

    slot_time = []

    # Check for the current month and the 4 next ones
    for i in range(5):
        if i != 0:
            next_month_button = browser.find_element_by_xpath("//*[contains(text(),'>')]")
            next_month_button.click()

        inner_html = browser.execute_script("return document.body.innerHTML")

        if check_available_slot(inner_html):
            slot_time.append(get_date(inner_html))

    browser.quit()

    if not slot_time:
        print("Found " + str(len(slot_time)) + "slot(s) available !")
        send_mail(slot_time)
    else:
        print("Nothing found ..."


main()
