class Event():
    def __init__(self):
        self.day = ""
        self.date = ""
        self.time = ""
        self.category = ""
        self.studio = ""
        self.openSlots = ""
        self.location = ""
        self.title = ""
        self.year = ""
        self.metaData = ""
        self.beginDate = ""
        self.endDate = ""
        self.signUpURL = ""
        self.status = ""
        self.message = ""
        
    def createFromViewParams(self, time, category, studio, openSlots, title, beginDate, endDate):
        self.time = time
        self.category = category
        self.studio = studio
        self.openSlots = openSlots
        self.title = title
        self.beginDate = beginDate
        self.endDate = endDate
        
        return self

    def createFromGroupExParams(self, eventStr):
        self.day = eventStr[0]
        self.date = eventStr[1]
        self.year = eventStr[2]
        self.time = eventStr[3]
        self.title = eventStr[4]
        self.studio = eventStr[6]
        # compile the category
        self.category = eventStr[7] + ", "+ eventStr[8] + ", "+ eventStr[9] + ", "+ eventStr[10]
        self.location = eventStr[13]
        # extract openSlots and Signup URL
        metaList = list(eventStr[14].split("\\"))
        if len(metaList) > 12:
            self.openSlots = metaList[12].split(' ')[0]
            self.signUpURL = metaList[16]

        return self

    # param example: 'https://groupexpro.com/gxp/reservations/start/index/11612841/01/21/2021,Thursday,January 21,12:00pm-12:30pm,5,Boldt Pool,Appleton YMCA,Lap/Fitness Lane Reservation,Open Schedules (i.e., pool, gym, gymnastics)'
    def createFromString(self, eventStr):
        eventColumnList = []
        eventColumnList = eventStr.split(",")
        self.day = eventColumnList[1]
        self.date = eventColumnList[2]
        self.time = eventColumnList[3]
        self.category = eventColumnList[8] + ", "+ eventColumnList[9] + ", "+ eventColumnList[10] + ", "+ eventColumnList[11],
        self.studio = eventColumnList[5]
        self.openSlots = eventColumnList[4]
        self.location = eventColumnList[6]
        self.title = eventColumnList[7]
        self.year = ""
        self.metaData = ""
        self.beginDate = ""
        self.endDate = ""
        self.signUpURL = eventColumnList[0]
        self.status = ""
        self.message = ""

        return self
