from domain.Event import Event
from service.appservice import *

def formatColumnStringToColumnList(eventStringList):
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
    return eventList

def formatResponseBody(responseBody):
    # format payload
    # find the right of this position
    nonJSONPayLoad = responseBody.find('aaData')+8
    # remove these things
    JSONPayLoad = responseBody[nonJSONPayLoad:]
    JSONPayLoad = JSONPayLoad.rstrip("})")
    JSONPayLoad = JSONPayLoad.replace("\n","")
    JSONPayLoad = JSONPayLoad.replace("\t","")
    JSONPayLoad = JSONPayLoad.replace("\t","")
    # add pipes for delimiting later
    JSONPayLoad = JSONPayLoad.replace("],[","|")
    # remove these things
    JSONPayLoad = JSONPayLoad.replace("[","")
    JSONPayLoad = JSONPayLoad.replace("]","")
    JSONPayLoad = JSONPayLoad.replace("&nbsp;","")
    JSONPayLoad = JSONPayLoad.replace("&nbsp;","")
    JSONPayLoad = JSONPayLoad.replace("<br><strong>Staff</strong><br />","")
    JSONPayLoad = JSONPayLoad.replace('"', '')

    # create a list using pipes as delimiter
    return list(JSONPayLoad.split("|"))

def convertEventStrListToEventList(eventStrList):
    print ("app called convertEventStrListToEventList")
    eventList = []
    for eventStr in eventStrList:
        newEvent = Event()
        newEvent = newEvent.createFromGroupExParams(eventStr)
        eventList.append(newEvent)
    return eventList


# find events based on search criteria
def findEventByTitleCategoryStudioOpenSlots(availibleEventList, inputEvent):
    print("getEventByDayTitleCategoryStudiosOpenSlots")
    desiredEventList = []
    for event in availibleEventList:
        if (event.title == inputEvent.title 
        and event.category == inputEvent.category 
        and event.studio == inputEvent.studio
        and event.openSlots >= inputEvent.openSlots):
                try:
                    desiredEventList.append(event)
                except:
                    print("Error")
    return desiredEventList
# find events based on search criteria
def findEventByTimeTitleCategoryOpenSlots(availibleEventList, inputEvent):
    print("getEventByDayTimeTitleCategoryStudioOpenSlots")
    desiredEventList = []
    for event in availibleEventList:
        if (event.time == inputEvent.time 
        and event.title == inputEvent.title 
        and event.category == inputEvent.category 
        and event.studio == inputEvent.studio
        and event.openSlots >= inputEvent.openSlots):
                try:
                    desiredEventList.append(event)
                except:
                    print("Error")
    return desiredEventList
