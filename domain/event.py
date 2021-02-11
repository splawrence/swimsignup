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

    def create_from_view_params(
        self, time, category, studio, open_slots, title, begin_date, end_date
    ):
        self.time = time
        self.category = category
        self.studio = studio
        self.open_slots = open_slots
        self.title = title
        self.begin_date = begin_date
        self.end_date = end_date

        return self

    def create_from_group_ex_params(self, event_str):
        self.day = event_str[0]
        self.date = event_str[1]
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
        # extract openSlots and Signup URL
        meta_list = list(event_str[14].split("\\"))
        if len(meta_list) > 12:
            self.open_slots = meta_list[12].split(" ")[0]
            self.sign_up_url = meta_list[16]

        return self

    # param example: 'https://groupexpro.com/gxp/reservations/start/index/11612841/01/21/2021,Thursday,January 21,12:00pm-12:30pm,5,Boldt Pool,Appleton YMCA,Lap/Fitness Lane Reservation,Open Schedules (i.e., pool, gym, gymnastics)'
    def create_from_string(self, event_str):
        event_column_list = []
        event_column_list = event_str.split(",")
        self.day = event_column_list[1]
        self.date = event_column_list[2]
        self.time = event_column_list[3]
        self.category = (
            event_column_list[8]
            + ", "
            + event_column_list[9]
            + ", "
            + event_column_list[10]
            + ", "
            + event_column_list[11],
        )
        self.studio = event_column_list[5]
        self.open_slots = event_column_list[4]
        self.location = event_column_list[6]
        self.title = event_column_list[7]
        self.year = ""
        self.meta_data = ""
        self.begin_date = ""
        self.end_date = ""
        self.sign_up_url = event_column_list[0]
        self.status = ""
        self.message = ""

        return self

    def create_from_time(self, time):
        self.category = "Open Schedules (i.e., pool, gym, gymnastics)"
        self.studio = "Meter Pool"
        self.open_slots = "1"
        self.title = "Lap/Fitness Lane Reservation"
        self.time = time

        return self