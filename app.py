from domain.event import Event
from service.appservice import *
from service.appserviceREST import *
from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

app = Flask(__name__)

@app.route('/')
def home():
     return render_template('home.html')

@app.route('/spawnlings')
def main():
    input_event = Event()
    input_event.create_from_view_params(request.args.get('times', None),
                                    request.args.get('categories', None),
                                    request.args.get('studios', None),
                                    request.args.get('openSlots', None),
                                    request.args.get('titles', None),
                                    request.args.get('beginDate', None),
                                    request.args.get('endDate', None))
    location_dict = {
        "Boldt Pool": "1941",
        "Meter Pool": "701",
        "Yard Pool": "701"
    }

    category_dict = {
        "Open Schedules (i.e., pool, gym, gymnastics)": "8980"
    }

    location_number = location_dict[input_event.studio]
    category_number = category_dict[input_event.category]

    # get parsed list of dates
    event_list = get_events_by_place_date(location_number, category_number, input_event.begin_date, input_event.end_date)
    availible_event_list = []
    for event in event_list:
        if event.openSlots != "WAITLIST" and event.openSlots != "CLASS":
                    try:
                        availible_event_list.append(event)
                    except:
                        print("Class is full")
        
    if input_event.time == "":
        desired_event_list = find_event_without_time(availible_event_list, input_event)
    else:
        desired_event_list = find_event_with_time(availible_event_list, input_event)
    
    return render_template('home.html', data=desired_event_list)
    
def login(driver, email, password):
    email_element = driver.find_element_by_id("login")
    email_element.send_keys(email)
    password_element = driver.find_element_by_id("password")
    password_element.send_keys(password)
    submit(driver)

def submit(driver):
    submit_element = driver.find_element_by_name("submit")
    submit_element.click()


@app.route("/register", methods=["POST"])
def reservations():
    email = request.form["email"]
    password = request.form["password"]
    event_str_list = str(request.form["eventList"])[1:-1] 
    selected_event_str_list = event_str_list.split("],[")
    selected_event_list = []

    # start webdriver and keep it running globally
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # run on armv7i
    # driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=chrome_options)
    # run on windows
    driver = webdriver.Chrome(options=chrome_options)
    is_loggen_in = False
    for event_str in selected_event_str_list:
        message_list = []
        new_event = Event()
        new_event.create_from_string(event_str)
        response_message_ist = []
        driver.get(new_event.sign_up_url)

        if is_loggen_in is False:
            try:
                # login page
                login(driver, email, password)
                # reserve slot page
                submit(driver)
                message_list = driver.find_elements_by_class_name("alert")
                for message in message_list:
                    message_text = message.get_attribute("innerText")
                    response_message_ist.append(message_text)
                """<a class="cancelReservation" href="/gxp/reservations/start/index/11612896/01/22/2021?method=cancelReservation&amp;e=0&amp;type=">Cancel Reservation</a>"""
                new_event.message = response_message_ist
                new_event.status = "success"
            except:
                message_list = driver.find_elements_by_class_name("alert")
                for message in message_list:
                    message_text = message.get_attribute("innerText")
                    response_message_ist.append(message_text)
                    new_event.message = response_message_ist
                    new_event.status = "error"
            selected_event_list.append(new_event)
            is_loggen_in = True
        else:
            try:
                # reserve slot page
                submit(driver)
                message_list = driver.find_elements_by_class_name("alert")
                for message in message_list:
                    message_text = message.get_attribute("innerText")
                    response_message_ist.append(message_text)
                """<a class="cancelReservation" href="/gxp/reservations/start/index/11612896/01/22/2021?method=cancelReservation&amp;e=0&amp;type=">Cancel Reservation</a>"""
                new_event.message = response_message_ist
                new_event.status = "success"
            except:
                message_list = driver.find_elements_by_class_name("alert")
                for message in message_list:
                    message_text = message.get_attribute("innerText")
                    response_message_ist.append(message_text)
                    new_event.message = response_message_ist
                    new_event.status = "error"
            selected_event_list.append(new_event)

    driver.close()
    return render_template("confirmation.html", data=selected_event_list)

if __name__ == '__main__':
    app.run(debug=True)