
# Active project data
class ActiveProjectHead():
    def __init__(self, id, name, sessionsDbPath, date, description, hoursTotal):
        self.id :str = id
        self.name :str = name
        self.sessionsDbPath :str = sessionsDbPath
        self.date :str = date
        self.description :str = description
        self.hoursTotal :float = hoursTotal

# Session data
class SessionData():
    # Object matches* values with db row (*Object-> camel case. Db-> upper case)
    # (session row: ID, DATESTART, DATEEND, HOURS, DESCRIPTION)
    def __init__(self, id="", dateStart="", dateEnd="", hours=0.0, description=""):
        self.id = id
        self.dateStart = dateStart
        self.dateEnd = dateEnd
        self.hours = hours
        self.description = description
