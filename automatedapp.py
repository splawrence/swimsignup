from domain.event import Event
from service.appservice import *
from service.appserviceREST import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime as dt


def main():
    if (dt.now().date() - dt(2021, 2, 9).date()).days % 2 == 0:
        do_stuff()
    else:
        print("bye")


def do_stuff():
    first_timeslot = Event()
    second_timeslot = Event()

    first_timeslot.create_from_time("5:00pm-5:30pm")
    second_timeslot.create_from_time("5:30pm-6:00pm")
    person_list = []
    # add user login information here
    user = {"email": "", "password": ""}

    person_list.append(user)

    input_events = []
    input_events.append(first_timeslot)
    input_events.append(second_timeslot)

    event_list = []
    event_list = get_future_events()

    desired_event_list = []

    for input_event in input_events:
        desired_event_list.append(find_one_event_from_inputs(event_list, input_event))

    for person in person_list:
        reservations(person["email"], person["password"], desired_event_list)


def login(driver, email, password):
    email_element = driver.find_element_by_id("login")
    email_element.send_keys(email)
    password_element = driver.find_element_by_id("password")
    password_element.send_keys(password)
    submit(driver)


def submit(driver):
    submit_element = driver.find_element_by_name("submit")
    submit_element.click()


def reservations(email, password, desired_event_list):
    # start webdriver and keep it running globally
    chrome_options = Options()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # run on armv7i
    # driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=chrome_options)
    # run on windows
    driver = webdriver.Chrome(options=chrome_options)
    is_logged_in = False
    for event in desired_event_list:
        driver.get(event.signUpURL)

        if is_logged_in is False:
            # login
            login(driver, email, password)
            # reserve slot page
            submit(driver)
            is_logged_in = True
        else:
            # reserve slot page
            submit(driver)

    driver.close()


if __name__ == "__main__":
    main()