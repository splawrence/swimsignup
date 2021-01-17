from logging import exception
import requests
from flask import Flask, render_template, request
import time
from datetime import datetime, timedelta 
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException 
from selenium.webdriver.chrome.options import Options

def configureEvents(eventList):
    print ("configureEvents")
    configuredEventList = []
    for event in eventList:
        headerDict = {
        "day": event[0],
        "date": event[1],
        "year": event[2],
        "time": event[3],
        "title": event[4],
        "studio": event[6],
        "category": event[7] + ", "+ event[8] + ", "+ event[9] + ", "+ event[10],
        "location": event[13],
        "metaData": event[14]
    }
        metaString = headerDict["metaData"]
        metaList = list(metaString.split("\\"))
        if len(metaList) > 12:
            headerDict["openSlots"] = metaList[12].split(' ')[0]
            headerDict["signUpURL"]= metaList[16]
            del headerDict["metaData"]
            configuredEventList.append(dict(headerDict))
        else:
            continue
        
    return configuredEventList

def getParsedEvents(locationNumber, categoryNumber, beginDate, endDate):
    print ("getParsedEvents")

    # if no input date then get 48 hours worth of data
    if beginDate == "" or endDate == "":
        beginDateTime = datetime.now()
        endDateTime = beginDateTime + timedelta(days=2) 
        # beginDate
        begintime = time.mktime(beginDateTime.timetuple())
        begintime_str = str(int(begintime))
        # endDate
        endtime = time.mktime(endDateTime.timetuple())
        endtime_str = str(int(endtime))
    else:
        # This works locally
        # # beginDate
        # begintm = time.strptime(beginDate, '%Y-%m-%d')
        # begintime = time.mktime(begintm)
        # begintime_str = str(int(begintime))
        # # endDate
        # endtm = time.strptime(endDate, '%Y-%m-%d')
        # endtime = time.mktime(endtm)
        # endtime_str = str(int(endtime))
        # This works in the cloud
        # beginDate
        beginDateTime = datetime.strptime(beginDate, '%Y-%m-%d')
        beginTimeFloat = time.mktime((beginDateTime + timedelta(days=1)).timetuple())
        begintime_str = str(int(beginTimeFloat))
        # endDate
        endDateTime = datetime.strptime(endDate, '%Y-%m-%d')
        endTimeFloat = time.mktime((endDateTime + timedelta(days=1)).timetuple())
        endtime_str = str(int(endTimeFloat))

    # resp = requests.get('https://groupexpro.com/schedule/embed/json.php?schedule&instructor_id=true&format=jsonp&a=110&location='+ locationNumber +'&category=' + categoryNumber +'&start=' + begintime_str + '&end=' + endtime_str + '&callback=jQuery35108719133265827776_1610171732530&_=1610171732536')
    resp = requests.get('https://groupexpro.com/schedule/embed/json.php?schedule&instructor_id=true&format=jsonp&a=110&location='+ locationNumber +'&category=' + categoryNumber +'&start=' + begintime_str + '&end=' + endtime_str + '&callback=&_=')
    if resp.status_code != 200:
        # this is bad
        print(resp.status_code)
        return "Unexpected error"
    else:
        print(resp.status_code)
        responseBody = resp.text
        # format payload
        # yikes the payload is not intended for this
        nonJSONPayLoad = responseBody.find('aaData')+8
        JSONPayLoad = responseBody[nonJSONPayLoad:]
        JSONPayLoad = JSONPayLoad.rstrip("})")
        JSONPayLoad = JSONPayLoad.replace("\n","")
        JSONPayLoad = JSONPayLoad.replace("\t","")
        JSONPayLoad = JSONPayLoad.replace("\t","")
        JSONPayLoad = JSONPayLoad.replace("],[","|")
        JSONPayLoad = JSONPayLoad.replace("[","")
        JSONPayLoad = JSONPayLoad.replace("]","")
        JSONPayLoad = JSONPayLoad.replace("&nbsp;","")
        JSONPayLoad = JSONPayLoad.replace("&nbsp;","")
        JSONPayLoad = JSONPayLoad.replace("<br><strong>Staff</strong><br />","")
        JSONPayLoad = JSONPayLoad.replace('"', '')

    eventStringList = list(JSONPayLoad.split("|"))

    eventList = []
    # setup event string list
    for rowString in eventStringList:
        x = 0
        # split string row to columns
        columnList = list(rowString.split(',')) 
        # clean up the header list
        for column in columnList:
            columnList[x] = column.strip()
            x = x + 1
        eventList.append(columnList)
    eventList = configureEvents(eventList)
    return eventList
# find events based on search criteria
def getEventByDayTitleCategoryStudioOpenSlots(availibleEventList, inputEvent):
    print("getEventByDayTitleCategoryStudiosOpenSlots")
    desiredEventList = []
    for event in availibleEventList:
        if (event["title"] == inputEvent["title"] 
        and event["category"] == inputEvent["category"] 
        and event["studio"] == inputEvent["studio"]
        and event["openSlots"] >= inputEvent["openSlots"]):
                try:
                    desiredEventList.append(dict(event))
                except:
                    print("Error")
    return desiredEventList
# find events based on search criteria
def getEventByDayTimeTitleCategoryOpenSlots(availibleEventList, inputEvent):
    print("getEventByDayTimeTitleCategoryStudioOpenSlots")
    desiredEventList = []
    for event in availibleEventList:
        if (event["time"] == inputEvent["time"] 
        and event["title"] == inputEvent["title"] 
        and event["category"] == inputEvent["category"] 
        and event["studio"] == inputEvent["studio"]
        and event["openSlots"] >= inputEvent["openSlots"]):
                try:
                    desiredEventList.append(dict(event))
                except:
                    print("Error")
    return desiredEventList

app = Flask(__name__)

@app.route('/spawnlings')
def main():
    time  = request.args.get('times', None)
    category  = request.args.get('categories', None)
    studio  = request.args.get('studios', None)
    openSlots  = request.args.get('openSlots', None)
    title  = request.args.get('titles', None)
    beginDate  = request.args.get('beginDate', None)
    endDate  = request.args.get('endDate', None)
    locationObj = {
        "Boldt Pool": "1941",
        "Meter Pool": "701",
        "Yard Pool": "701"
    }

    categoryObj = {
        "Open Schedules (i.e., pool, gym, gymnastics)": "8980"
    }

    locationNumber = locationObj[studio]
    categoryNumber = categoryObj[category]

    inputEventQuery = {
        "time": time,
        "title": title,
        "category": category,
        "studio": studio,
        "openSlots": openSlots
    }
    # get parsed list of dates
    eventList = getParsedEvents(locationNumber=locationNumber, categoryNumber=categoryNumber, beginDate=beginDate, endDate=endDate)
    availibleEventList = []
    for event in eventList:
        if event["openSlots"] != 'WAITLIST' and event["openSlots"] != 'CLASS':
                    try:
                        availibleEventList.append(dict(event))
                    except:
                        print("Class is full")
        
    if inputEventQuery["time"] == "":
        desiredEventList = getEventByDayTitleCategoryStudioOpenSlots(availibleEventList=availibleEventList, inputEvent=inputEventQuery)
    else:
        desiredEventList = getEventByDayTimeTitleCategoryOpenSlots(availibleEventList=availibleEventList, inputEvent=inputEventQuery)
    
    return render_template('home.html', data=desiredEventList)
    
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/register', methods=['POST'])
def reservations():
    email  = request.form['email']
    password  = request.form['password']
    urlList = request.form['urlList'].split(',')
    returnMessageList = []
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver', chrome_options=chrome_options)
    for url in urlList:
        driver.get(url)
        try:
            emailEl = driver.find_element_by_id('login')
            emailEl.send_keys(email)
            passwordEl = driver.find_element_by_id("password")
            passwordEl.send_keys(password)
            submitEl = driver.find_element_by_name('submit')
            submitEl.click()
            submitEl = driver.find_element_by_name('submit')
            submitEl.click() 
            messageList = driver.find_elements_by_class_name('alert')
            for message in messageList:
                messageText = message.get_attribute('innerText')
                returnMessageList.append(messageText)
            return render_template('success.html', data=returnMessageList)
        except:
            messageList = driver.find_elements_by_class_name('alert')
            for message in messageList:
                messageText = message.get_attribute('innerText')
                returnMessageList.append(messageText)
            return render_template('error.html', data=returnMessageList)
    driver.close()

if __name__ == '__main__':
    app.run(debug=True)