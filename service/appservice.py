from domain.event import Event
from service.appservice import *


def format_column_string_to_column_list(event_string_list):
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
    json_pay_load = json_pay_load.replace("<br><strong>Staff</strong><br />", "")
    json_pay_load = json_pay_load.replace('"', "")

    # create a list using pipes as delimiter
    return list(json_pay_load.split("|"))


def convert_event_str_list_to_event_list(event_str_list):
    print("app called convert_event_str_list_to_event_list")
    event_list = []
    for event_str in event_str_list:
        new_event = Event()
        new_event = new_event.create_from_group_ex_params(event_str)
        event_list.append(new_event)
    return event_list


# find events based on search criteria
def find_event_without_time(availible_event_list, input_event):
    print("find_event_without_time")
    desired_event_list = []
    for event in availible_event_list:
        if (
            event.title == input_event.title
            and event.category == input_event.category
            and event.studio == input_event.studio
            and event.openSlots >= input_event.openSlots
        ):
            try:
                desired_event_list.append(event)
            except:
                print("Error")
    return desired_event_list


# find events based on search criteria
def find_event_with_time(availible_event_list, input_event):
    print("find_event_with_time")
    desired_event_list = []
    for event in availible_event_list:
        if (
            event.time == input_event.time
            and event.title == input_event.title
            and event.category == input_event.category
            and event.studio == input_event.studio
            and event.openSlots >= input_event.openSlots
        ):
            try:
                desired_event_list.append(event)
            except:
                print("Error")
    return desired_event_list


# find one event based on search criteria
def find_one_event_from_inputs(availible_event_list, input_event):
    print("find_one_event_from_inputs")
    for event in availible_event_list:
        if (
            event.time == input_event.time
            and event.title == input_event.title
            and event.category == input_event.category
            and event.studio == input_event.studio
            and event.openSlots >= input_event.openSlots
        ):
            return event
