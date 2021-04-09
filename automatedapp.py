import requests
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import sys

# sets the environmental variables
# active_profile = "prod"
active_profile = "dev"

# scheduleing details
# even or odd run day option. by default this is 9
# run_day = 9
run_day = 10

# weekday run options
# weekday_run_hour = 17
weekday_run_hour = 17
weekday_timeslot1 = "5:00pm-5:30pm"
weekday_timeslot2 = "5:30pm-6:00pm"

# weekend run options
# weekend_run_hour = 11
weekend_run_hour = 12
weekend_timeslot1 = "11:00am-11:30am"
weekend_timeslot2 = "11:30am-12:00pm"

# days in advance to run
time_offset = timedelta(days=2)

# slot details
# searched event details
category_number = "8980"
location_number = "701"

# input event details
category_description = "Open Schedules (i.e., pool, gym, gymnastics)"
studio_description = "Meter Pool"
open_slots_number = "1"
event_title = "Lap/Fitness Lane Reservation"

def main():
    # scheduling logic
    # run every other day
    # if registration is for weekend, run at 11:30 for 11-12
    # else run at 5:30 for 5-6
    if (datetime.now().date() - datetime(2021, 2, run_day).date()).days % 2 == 0:

        # set up time slots
        week_no = datetime.today().weekday()

        # check if registration is for a weekend
        if week_no < 3 or week_no > 4:
            # if run occurs at 5pm
            if datetime.now().hour == weekday_run_hour:
                setup_slots(weekday_timeslot1, weekday_timeslot2)
        else:
            # if run occurs at 11am
            if datetime.now().hour == weekend_run_hour:
                setup_slots(weekend_timeslot1, weekend_timeslot2)

def setup_slots(time_slot1, time_slot2):
        first_event = Event()
        second_event = Event()

        first_event.create_from_time(time_slot1)
        second_event.create_from_time(time_slot2)

        # set time list
        input_events = [first_event, second_event]
        do_stuff(input_events)

def do_stuff(input_events):
    person_list = []
    # add user login information here
    if active_profile == "prod":
        # for use on the server
        file = open("/home/ubuntu/apps/login.csv", "r")
    else:
        # local development
        file = open("login.csv", "r")

    for login in file:
        person_list.append(login.split(","))
    file.close()

    event_list = get_future_events()

    desired_event_list = []
    for input_event in input_events:
        desired_event_list.append(
            find_one_event_from_inputs(event_list, input_event))

    if desired_event_list[0] is not None and desired_event_list[1] is not None:
        print("Slots found. Commencing registration.")
        for person in person_list:
            make_reservations(person[0], person[1], desired_event_list)
    else:
        print("Error: Slots could not be found")
        print("Input event date was: " + str(input_event.date))
        print("Actual event date was: " + str(event_list[0].date))
        sys.exit(404)

def login(driver, email, password):
    email_element = driver.find_element_by_id("login")
    email_element.send_keys(email)
    password_element = driver.find_element_by_id("password")
    password_element.send_keys(password)
    submit(driver)

def submit(driver):
    submit_element = driver.find_element_by_name("submit")
    submit_element.click()

def check_for_waitlisted(driver, time_stamp):
        # check that there is an availible slot
        if(driver.find_element_by_name("action").get_attribute("value") == "waitlist"):
            print("Waitlisted: " + time_stamp)
        else:
            print("Successfully registered: " + time_stamp)

def make_reservations(email, password, desired_event_list):
    chrome_options = Options()
    if active_profile == "prod":
        # for use on the server
        # run on armv7i chromedriver
        chrome_options.add_argument("--headless")
        driver = webdriver.Chrome("/usr/lib/chromium-browser/chromedriver", options=chrome_options)
    else:
        # local development
        # run on windows chromedriver.exe
        driver = webdriver.Chrome(options=chrome_options)

    is_logged_in = False
    for event in desired_event_list:
        slot_info = (str(email) + str(" for ") + str(event.month) + " " + str(event.date) + " " + str(event.time))
        driver.get(event.sign_up_url)
        try:
            if is_logged_in is False:
                # login
                login(driver, email, password)

                # check waitlisted status
                check_for_waitlisted(driver, slot_info)

                # reserve slot
                submit(driver)
                is_logged_in = True
            else:
                # check is waitlisted
                check_for_waitlisted(driver, slot_info)

                # reserve slot
                submit(driver)
        except NoSuchElementException:
            print("Error: Failed to register: " + slot_info)

    driver.close()

def get_future_events():
    event_str_list = []
    begin_date_time = datetime.now() + time_offset
    end_date_time = begin_date_time
    # beginDate
    begintime = time.mktime(begin_date_time.timetuple())
    begintime_str = str(int(begintime))
    # endDate
    endatetimeime = time.mktime(end_date_time.timetuple())
    endatetimeime_str = str(int(endatetimeime))

    event_list = []
    url = str("https://groupexpro.com/schedule/embed/json.php?schedule&instructor_id=true&format=jsonp&a=110&location="
        + location_number
        + "&category="
        + category_number
        + "&start="
        + begintime_str
        + "&end="
        + endatetimeime_str
        + "&callback=&_=")
    response = requests.get(url)

    if response.status_code != 200:
        # this is bad
        print("Response code: " + str(response.status_code))
    else:
        print(
            "Response received from https://groupexpro.com: "
            + str(response.status_code)
            + " OK"
        )
        # remove code and invalid characters from response
        str_list = format_response_body(response.text)
        # loop through each string and format the columns
        event_str_list = format_columns(str_list)
        # loop through each event string and create and event from each
        event_list = create_event_from_string(event_str_list)

        print("There are: " + str(len(event_list)) + " events to pick from. Yay!")

    return event_list

def format_columns(event_string_list):
    event_list = []
    # setup event string list
    for row_string in event_string_list:
        x = 0
        # split string row to columns
        column_list = list(row_string.split(","))
        # clean up the header list
        for column in column_list:
            column_list[x] = column.strip()
            x = x + 1
        event_list.append(column_list)
    return event_list

def format_response_body(response_body):
    # format payload
    # find the right of this position
    non_json_pay_load = response_body.find("aaData") + 8
    # remove these things
    json_pay_load = response_body[non_json_pay_load:]
    json_pay_load = json_pay_load.rstrip("})")
    json_pay_load = json_pay_load.replace("\n", "")
    json_pay_load = json_pay_load.replace("\t", "")
    json_pay_load = json_pay_load.replace("\t", "")
    # add pipes for delimiting later
    json_pay_load = json_pay_load.replace("],[", "|")
    # remove these things
    json_pay_load = json_pay_load.replace("[", "")
    json_pay_load = json_pay_load.replace("]", "")
    json_pay_load = json_pay_load.replace("&nbsp;", "")
    json_pay_load = json_pay_load.replace("&nbsp;", "")
    json_pay_load = json_pay_load.replace(
        "<br><strong>Staff</strong><br />", "")
    json_pay_load = json_pay_load.replace('"', "")

    # create a list using pipes as delimiter
    return list(json_pay_load.split("|"))

def create_event_from_string(event_str_list):
    event_list = []
    for event_str in event_str_list:
        new_event = Event()
        new_event = new_event.create_from_group_ex_params(event_str)
        event_list.append(new_event)
    return event_list

# find one event based on search criteria
def find_one_event_from_inputs(availible_event_list, input_event):
    for event in availible_event_list:
        if (
            event.time == input_event.time
            and event.title == input_event.title
            and event.category == input_event.category
            and event.studio == input_event.studio
            and event.open_slots >= input_event.open_slots
            and event.date == input_event.date
        ):
            return event

class Event:
    def __init__(self):
        self.day = ""
        self.date = ""
        self.time = ""
        self.category = ""
        self.studio = ""
        self.open_slots = ""
        self.location = ""
        self.title = ""
        self.year = ""
        self.meta_data = ""
        self.begin_date = ""
        self.end_date = ""
        self.sign_up_url = ""
        self.status = ""
        self.message = ""

    def create_from_group_ex_params(self, event_str):
        self.day = event_str[0]
        self.month = event_str[1].split(" ")[0]
        self.date = event_str[1].split(" ")[1]
        self.year = event_str[2]
        self.time = event_str[3]
        self.title = event_str[4]
        self.studio = event_str[6]
        # compile the category
        self.category = (
            event_str[7]
            + ", "
            + event_str[8]
            + ", "
            + event_str[9]
            + ", "
            + event_str[10]
        )
        self.location = event_str[13]
        # extract open_slots and Signup URL
        meta_list = list(event_str[14].split("\\"))
        if len(meta_list) > 12:
            self.open_slots = meta_list[12].split(" ")[0]
            self.sign_up_url = meta_list[16]

        return self

    def create_from_time(self, time):
        self.category = category_description
        self.studio = studio_description
        self.open_slots = open_slots_number
        self.title = event_title
        self.time = time
        date = datetime.now() + time_offset
        self.date = str(date.day)
        return self

if __name__ == "__main__":
    main()
