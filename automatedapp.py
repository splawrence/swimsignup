import requests
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
import sys
import json

# sets the environmental variables
active_profile = "prod"
# active_profile = "dev"

# scheduleing details
# even or odd run day option. by default this is 9
run_day = 9
# run_day = 10

# weekday run options
weekday_run_hour = 17
weekday_timeslot1 = "5:00pm-5:30pm"
weekday_timeslot2 = "5:30pm-6:00pm"

# weekend run options
weekend_run_hour = 11
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
log_list = []
log_list.append("success")

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
        first_event = event()
        second_event = event()

        first_event.create_user_event(time_slot1)
        second_event.create_user_event(time_slot2)

        # set time list
        input_events = [first_event, second_event]
        do_stuff(input_events)
        if log_list[0] == "error":
            for l in log_list:
                print(str(l))
    
def do_stuff(input_events):
    person_list = []
    # add user login information here
    if active_profile == "prod":
        # for use on the server
        file = open("/home/ubuntu/apps/login.csv", "r")
    else:
        # local development
        file = open("D:\Apps\git\login.csv", "r")

    for login in file:
        person_list.append(login.split(","))
    file.close()

    event_list = find_events(input_events)

    if len(event_list) > 0:
        for person in person_list:
            make_reservations(person[0], person[1], event_list)
    else:
        log_list.append(str(datetime.now()) + " Error: Slots could not be found")
        log_list[0] = "error"
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
            log_list.append(str(datetime.now()) + ": Waitlisted: " + str(time_stamp))
            log_list[0] = "error"

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
        slot_info = (str(email) + str(" for ") + str(datetime.now().month) + "/" + str(event.date) + "/" + str(datetime.now().year) + " " + str(event.time))
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
            log_list.append(str(datetime.now()) + ": Failed to register: " + str(slot_info))
            log_list[0] = "error"

    driver.close()

def find_events(input_events):
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
        + location_number + "&category=" + category_number + "&start=" + begintime_str + "&end=" + endatetimeime_str + "&callback=&_=")
    response = requests.get(url)
    desired_event_list = []

    log_list.append(str(datetime.now()) + ": Response: " + str(response.status_code))
    if response.status_code == 200:
        # get json from response
        event_str_list = response_mapper(response.text)

        # loop through each event string and create and event from each
        event_list = create_event_from_string(event_str_list)

        for user_event in input_events:
            event_found = find_one_event_from_inputs(event_list, user_event)
            if event_found is not None:
                desired_event_list.append(event_found)
    else:
        log_list[0] = "error"

    return desired_event_list

def response_mapper(response_text):
    # format for valid json
    response_text = response_text.lstrip("( ").rstrip(" )").replace("&nbsp;", "")
    json_obj = json.loads(response_text)

    # create a list using pipes as delimiter
    return list(json_obj["aaData"])

def create_event_from_string(event_str_list):
    event_list = []
    for event_str in event_str_list:
        new_event = event()
        new_event = new_event.create_system_event(event_str)
        event_list.append(new_event)
    return event_list

# find one event based on search criteria
def find_one_event_from_inputs(availible_event_list, user_event):
    for event in availible_event_list:
        if (event.time == user_event.time
            and event.title == user_event.title
            and event.category == user_event.category
            and event.studio == user_event.studio
        ):
            log_list.append(str(datetime.now()) + ": Event found")
            if event.date == user_event.date:
                log_list.append(str(datetime.now()) + ": Date found")
                log_list.append(str(datetime.now()) + ": Slots availible: " + str(event.open_slots))
                if event.open_slots >= user_event.open_slots:
                    return event

class event:
    def create_system_event(self, event_str):
        self.date = event_str[0].split(" ")[2].rstrip(",")
        self.time = event_str[1]
        self.title = event_str[2]
        self.studio = event_str[4]
        self.category = event_str[5]
        # extract sign_up_url and open_slots from the html tag
        html_tag = event_str[9].split("=")
        if len(html_tag) > 6:
            self.open_slots = html_tag[6].split(" ")[0].split('"')[1]
            self.sign_up_url = html_tag[8].split('"')[1]
        return self

    def create_user_event(self, time):
        date = datetime.now() + time_offset
        self.date = str(date.day)
        self.time = time
        self.title = event_title
        self.studio = studio_description
        self.category = category_description
        self.open_slots = open_slots_number
        return self

if __name__ == "__main__":
    main()
