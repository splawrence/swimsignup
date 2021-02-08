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
    inputEvent = Event()
    inputEvent.createFromViewParams(request.args.get('times', None),
                                    request.args.get('categories', None),
                                    request.args.get('studios', None),
                                    request.args.get('openSlots', None),
                                    request.args.get('titles', None),
                                    request.args.get('beginDate', None),
                                    request.args.get('endDate', None))
    locationObj = {
        "Boldt Pool": "1941",
        "Meter Pool": "701",
        "Yard Pool": "701"
    }

    categoryObj = {
        "Open Schedules (i.e., pool, gym, gymnastics)": "8980"
    }

    locationNumber = locationObj[inputEvent.studio]
    categoryNumber = categoryObj[inputEvent.category]

    # get parsed list of dates
    eventList = callEventsByLocationCategoryBeginDateEndDateGET(locationNumber, categoryNumber, inputEvent.beginDate, inputEvent.endDate)
    availibleEventList = []
    for event in eventList:
        if event.openSlots != "WAITLIST" and event.openSlots != "CLASS":
                    try:
                        availibleEventList.append(event)
                    except:
                        print("Class is full")
        
    if inputEvent.time == "":
        desiredEventList = findEventByTitleCategoryStudioOpenSlots(availibleEventList, inputEvent)
    else:
        desiredEventList = findEventByTimeTitleCategoryOpenSlots(availibleEventList, inputEvent)
    
    return render_template('home.html', data=desiredEventList)
    
@app.route("/register", methods=["POST"])
def reservations():
    email = request.form["email"]
    password = request.form["password"]
    eventStrList = str(request.form["eventList"])[1:-1] 
    selectedEventStrList = eventStrList.split("],[")
    selectedEventList = []

    # start webdriver and keep it running globally
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    # run on armv7i
    # driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=chrome_options)
    # run on windows
    driver = webdriver.Chrome(options=chrome_options)
    isLoggedIn = False
    for eventStr in selectedEventStrList:
        messageList = []
        newEvent = Event()
        newEvent.createFromString(eventStr)
        responseMessageList = []
        driver.get(newEvent.signUpURL)

        if isLoggedIn is False:
            try:
                # login page
                emailEl = driver.find_element_by_id("login")
                emailEl.send_keys(email)
                passwordEl = driver.find_element_by_id("password")
                passwordEl.send_keys(password)
                submitEl = driver.find_element_by_name("submit")
                submitEl.click()
                # reserve slot page
                submitEl = driver.find_element_by_name("submit")
                submitEl.click()
                messageList = driver.find_elements_by_class_name("alert")
                for message in messageList:
                    messageText = message.get_attribute("innerText")
                    responseMessageList.append(messageText)
                """<a class="cancelReservation" href="/gxp/reservations/start/index/11612896/01/22/2021?method=cancelReservation&amp;e=0&amp;type=">Cancel Reservation</a>"""
                newEvent.message = responseMessageList
                newEvent.status = "success"
            except:
                messageList = driver.find_elements_by_class_name("alert")
                for message in messageList:
                    messageText = message.get_attribute("innerText")
                    responseMessageList.append(messageText)
                    newEvent.message = responseMessageList
                    newEvent.status = "error"
            selectedEventList.append(newEvent)
            isLoggedIn = True
        else:
            try:
                # reserve slot page
                submitEl = driver.find_element_by_name("submit")
                submitEl.click()
                messageList = driver.find_elements_by_class_name("alert")
                for message in messageList:
                    messageText = message.get_attribute("innerText")
                    responseMessageList.append(messageText)
                """<a class="cancelReservation" href="/gxp/reservations/start/index/11612896/01/22/2021?method=cancelReservation&amp;e=0&amp;type=">Cancel Reservation</a>"""
                newEvent.message = responseMessageList
                newEvent.status = "success"
            except:
                messageList = driver.find_elements_by_class_name("alert")
                for message in messageList:
                    messageText = message.get_attribute("innerText")
                    responseMessageList.append(messageText)
                    newEvent.message = responseMessageList
                    newEvent.status = "error"
            selectedEventList.append(newEvent)

    driver.close()
    return render_template("confirmation.html", data=selectedEventList)

if __name__ == '__main__':
    app.run(debug=True)