from service.appservice import *
import requests
import time
from datetime import datetime, timedelta


def get_events_by_place_date(location_number, category_number, begin_date, end_date):
    event_string_list = []
    # if no input date then get 48 hours worth of data
    if begin_date == "" or end_date == "":
        begin_date_time = datetime.now()
        end_date_time = begin_date_time + timedelta(days=2)
        # beginDate
        begintime = time.mktime(begin_date_time.timetuple())
        begintime_str = str(int(begintime))
        # endDate
        endtime = time.mktime(end_date_time.timetuple())
        endtime_str = str(int(endtime))
    else:
        # beginDate
        begintm = time.strptime(begin_date, "%Y-%m-%d")
        begintime = time.mktime(begintm)
        begintime_str = str(int(begintime))
        # endDate
        endtm = time.strptime(end_date, "%Y-%m-%d")
        endtime = time.mktime(endtm)
        endtime_str = str(int(endtime))

    resp = requests.get(
        "https://groupexpro.com/schedule/embed/json.php?schedule&instructor_id=true&format=jsonp&a=110&location="
        + location_number
        + "&category="
        + category_number
        + "&start="
        + begintime_str
        + "&end="
        + endtime_str
        + "&callback=&_="
    )
    if resp.status_code != 200:
        # this is bad
        print("Response code: " + str(resp.status_code))
        print("Unexpected error")
    else:
        print(
            "Response received from https://groupexpro.com: "
            + str(resp.status_code)
            + " OK"
        )
        event_string_list = format_response_body(resp.text)

    event_list = format_column_string_to_column_list(event_string_list)
    event_list = convert_event_str_list_to_event_list(event_list)

    return event_list


def get_future_events():
    category_number = "8980"
    location_number = "701"
    event_string_list = []
    begin_date_time = datetime.now() + timedelta(days=2)
    end_date_time = begin_date_time
    # beginDate
    begintime = time.mktime(begin_date_time.timetuple())
    begintime_str = str(int(begintime))
    # endDate
    endtime = time.mktime(end_date_time.timetuple())
    endtime_str = str(int(endtime))

    resp = requests.get(
        "https://groupexpro.com/schedule/embed/json.php?schedule&instructor_id=true&format=jsonp&a=110&location="
        + location_number
        + "&category="
        + category_number
        + "&start="
        + begintime_str
        + "&end="
        + endtime_str
        + "&callback=&_="
    )
    if resp.status_code != 200:
        # this is bad
        print("Response code: " + str(resp.status_code))
        print("Unexpected error")
    else:
        print(
            "Response received from https://groupexpro.com: "
            + str(resp.status_code)
            + " OK"
        )
        event_string_list = format_response_body(resp.text)

    event_list = format_column_string_to_column_list(event_string_list)
    event_list = convert_event_str_list_to_event_list(event_list)
    print("There are: " + str(len(event_list)) + " events to pick from. Yay!")
    return event_list