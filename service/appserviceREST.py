from service.appservice import *
import requests
import time
from datetime import datetime, timedelta 

def callEventsByLocationCategoryBeginDateEndDateGET(locationNumber, categoryNumber, beginDate, endDate):
    print ("app called callEventsByLocationCategoryBeginDateEndDateGET")
    eventStringList = []
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
        # beginDate
        begintm = time.strptime(beginDate, '%Y-%m-%d')
        begintime = time.mktime(begintm)
        begintime_str = str(int(begintime))
        # endDate
        endtm = time.strptime(endDate, '%Y-%m-%d')
        endtime = time.mktime(endtm)
        endtime_str = str(int(endtime))

    resp = requests.get('https://groupexpro.com/schedule/embed/json.php?schedule&instructor_id=true&format=jsonp&a=110&location='+ locationNumber +'&category=' + categoryNumber +'&start=' + begintime_str + '&end=' + endtime_str + '&callback=&_=')
    if resp.status_code != 200:
        # this is bad
        print("Response code: " + str(resp.status_code))
        print("Unexpected error") 
    else:
        print("Response code: " + str(resp.status_code))
        eventStringList = formatResponseBody(resp.text)
    
    eventList = formatColumnStringToColumnList(eventStringList)
    eventList = convertEventStrListToEventList(eventList)

    return eventList