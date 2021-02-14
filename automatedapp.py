from domain.event import Event
from service.appservice import *
from service.appserviceREST import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from datetime import datetime as dt
from selenium.common.exceptions import NoSuchElementException


def main():
    # scheduling logic
    # run every other day
    # if registration is for weekend, run at 12 for 11-12
    # else run at 6 for 5-6
    if (dt.now().date() - dt(2021, 2, 9).date()).days % 2 == 0:
        print("Program starting " + str(dt.now()))
        week_no = dt.today().weekday()
        first_timeslot = Event()
        second_timeslot = Event()
        # check if registration is for a weekend
        if week_no < 3 or week_no > 4:
            # if run occurs at 6pm
            if dt.now().hour == 18:
                first_timeslot.create_from_time("5:00pm-5:30pm")
                second_timeslot.create_from_time("5:30pm-6:00pm")
                print("Using 5-6 timeframe.")
                # set time list
                input_events = [first_timeslot, second_timeslot]
                do_stuff(input_events)
                print("Program complete " + str(dt.now()))
        else:
            # if run occurs at 12pm
            if dt.now().hour == 12:
                first_timeslot.create_from_time("11:00am-11:30am")
                second_timeslot.create_from_time("11:30am-12:00pm")
                print("Using 11-12 timeframe.")
                # set time list
                input_events = [first_timeslot, second_timeslot]
                do_stuff(input_events)
                print("Program complete " + str(dt.now()))


def do_stuff(input_events):
    person_list = []
    # add user login information here
    file = open("login.csv", "r")
    for login in file:
        person_list.append(login.split(","))
    file.close()

    event_list = []
    event_list = get_future_events()

    desired_event_list = []

    for input_event in input_events:
        desired_event_list.append(find_one_event_from_inputs(event_list, input_event))

    if desired_event_list[0] is not None and desired_event_list[1] is not None:
        print("Slots found. Commencing registration.")
        for person in person_list:
            reservations(person[0], person[1], desired_event_list)
    else:
        print("Slots could not be found")


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
    driver = webdriver.Chrome(
        "/usr/lib/chromium-browser/chromedriver", options=chrome_options
    )
    # run on windows
    # driver = webdriver.Chrome(options=chrome_options)
    is_logged_in = False
    for event in desired_event_list:
        time_stamp = (
            str(email)
            + str(" for ")
            + str(event.month)
            + " "
            + str(event.date)
            + " "
            + str(event.time)
        )
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
