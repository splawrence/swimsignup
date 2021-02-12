from domain.event import Event
from service.appservice import *
from service.appserviceREST import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime as dt
from selenium.common.exceptions import NoSuchElementException


def main():
    if (dt.now().date() - dt(2021, 2, 9).date()).days % 2 == 0:
        print("Program starting " + str(dt.now()))
        do_stuff()
        print("Program complete " + str(dt.now()))
    else:
        print("Not running today.")


def do_stuff():
    first_timeslot = Event()
    second_timeslot = Event()

    # check if it is a weekend
    week_no = dt.today().weekday()
    if week_no < 3 or week_no > 4:
        first_timeslot.create_from_time("5:00pm-5:30pm")
        second_timeslot.create_from_time("5:30pm-6:00pm")
        print("Using 5-6 timeframe.")
    else:  # 5 Sat, 6 Sun
        first_timeslot.create_from_time("11:00am-11:30am")
        second_timeslot.create_from_time("11:30am-12:00pm")
        print("Using 11-12 timeframe.")

    person_list = []
    # add user login information here


    input_events = []
    input_events.append(first_timeslot)
    input_events.append(second_timeslot)

    event_list = []
    event_list = get_future_events()

    desired_event_list = []

    for input_event in input_events:
        desired_event_list.append(find_one_event_from_inputs(event_list, input_event))

    if desired_event_list[0] is not None and desired_event_list[1] is not None:
        print("Slots found. Commencing registration.")
        for person in person_list:
            reservations(person["email"], person["password"], desired_event_list)
    else:
        print("Slot could not be found")


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
    chrome_options.add_argument("--headless")
    # run on armv7i
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=chrome_options)
    # run on windows
    # driver = webdriver.Chrome(options=chrome_options)
    is_logged_in = False
    for event in desired_event_list:
        time_stamp = str(email) + str(" for ") + str(event.month) + " " + str(event.date) + " " + str(event.time)
        driver.get(event.sign_up_url)
        try:
            if is_logged_in is False:
                # login
                login(driver, email, password)
                # reserve slot page
                submit(driver)
                print("Successfully registered: " + time_stamp)
                is_logged_in = True
            else:
                # reserve slot page
                submit(driver)
                print("Successfully registered: " + time_stamp)
        except NoSuchElementException:
            print("Failed to register: " + time_stamp)
    driver.close()


if __name__ == "__main__":
    main()
