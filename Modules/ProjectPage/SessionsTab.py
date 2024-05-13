
from tkinter import END
import customtkinter as ctk
import datetime
from typing import Callable

from Modules.DbServices import DbServices
import Modules.ColorSchemes as colors
from Modules.ProjectPage.ProjectDataObjects import ActiveProjectHead, SessionData

# Sessions (Tab)
class SessionsTab():
    def __init__(self, sessionsFrame:ctk.CTkFrame, dbServices:DbServices, getProjectHead: Callable[[], ActiveProjectHead], updateOverview:Callable[[],None]):
        self.sessionsFrame = sessionsFrame
        self.dbServices = dbServices
        self.sessionsListView = None    # Sessions list widget, created last
        # Callable[[int], str] signifies a function that takes a single parameter of type int and returns a str.
        self.getProjectHead: Callable[[], ActiveProjectHead] = getProjectHead
        self.updateOverview: Callable[[],None] = updateOverview
        ############################################
        # Create session
        ############################################
        def createSession():
            print("Create Session!")
            if not self.getProjectHead():
                print("--> Error. self.getProjectHead() is None -> Return")
                return
            sessionsDbPath = self.getProjectHead().sessionsDbPath
            self.dbServices.createEmptySessionToDb(sessionsDbPath)
            self.updateSessionsListView()

        # New session
        sessionsTop = ctk.CTkFrame(master=self.sessionsFrame,fg_color="transparent")
        sessionsTop.pack(fill='x')
        startSessionButton = ctk.CTkButton(master=sessionsTop,text="New session",command=createSession)
        startSessionButton.pack(padx=20,pady=10,side='left')

        ############################################
        # Sessions listview - header
        ############################################
        # padx more on the right to match the scrollbar of sessions listview below
        sessionsHeader = ctk.CTkFrame(master=self.sessionsFrame,height=30)
        sessionsHeader.pack(padx=(30,56),pady=10,fill='x') 

        col1 = ctk.CTkLabel(master=sessionsHeader,text="description")
        col1.place(x=0,y=0,relwidth=(2/4))
        col2 = ctk.CTkLabel(master=sessionsHeader,text="date")
        col2.place(relx=(2/4),y=0,relwidth=(1/4))
        col3 = ctk.CTkLabel(master=sessionsHeader,text="hours")
        col3.place(relx=(3/4),y=0,relwidth=(1/4))

        ############################################
        # Sessions listview
        ############################################
        
        # Sessions list - entries
        sessionsListView = ctk.CTkScrollableFrame(master=self.sessionsFrame,height=400)
        sessionsListView.pack(padx=30,pady=(0,20),fill='both',expand=True)
        # Callback for updating DB from child widgets (SessionWidget)
        self.sessionsListView = sessionsListView
        # Run update on sessions listview 
        self.updateSessionsListView()

    def updateSessionsListView(self):
        print("updateSessionsListView")
        # Remove old list entries
        for w in reversed(self.sessionsListView.pack_slaves()):
            w.destroy()
        if not self.getProjectHead():
            print("--> self.getProjectHead() is None -> sessions list cleared -> update complete")
            return
        dbPath = self.getProjectHead().sessionsDbPath
        sessions = self.dbServices.getSessionRows(dbPath)
            
        # Create a session DO and a widget per session
        for row in sessions:
            # session row (tuple): ID, DATESTART, DATEEND, HOURS, DESCRIPTION
            sessionData = SessionData(row[0], row[1], row[2], row[3], row[4])
            sessionWidget = SessionWidget(self, self.sessionsListView, sessionData)
        print("--> update complete")

    def countTotalHours(self):
        print("countTotalHours")
        if not self.getProjectHead():
            print("--> self.getProjectHead() is None -> Return")
            return
        dbPath = self.getProjectHead().sessionsDbPath
        totalHours = 0.0
        hoursArray = self.dbServices.getAllColumnValuesFromSessions(dbPath, "HOURS")
        for i in hoursArray:
            totalHours += round(i,2)
        print("--> totalHours: " + str(totalHours))
        return totalHours
    
    # Update session data to db
    def updateSessionDataColumn(self, sessionId, column, newValue, updateListView=False):
        print(f"- updateSessionDataColumn ({column})")
        if not self.getProjectHead():
            print("--> Error. self.getProjectHead() is None -> Return")
            return
        sessionsDbPath = self.getProjectHead().sessionsDbPath
        self.dbServices.updateSessionColumn(sessionsDbPath, sessionId, column, newValue)
        if updateListView:
            self.updateSessionsListView()

    def updateProjectHeadColumn(self, column, newValue):
        print(f"- updateProjectHeadColumn  ({column})")
        if not self.getProjectHead():
            print("--> Error. self.getProjectHead() is None -> Return")
            return
        self.dbServices.updateProjectRow(self.getProjectHead().id, column, newValue)

    def updateTotalHoursOfAllSessions(self):
        # Update total hours count (All sessions)
        # Update Project head (db)
        self.updateProjectHeadColumn("HOURSTOTAL", self.countTotalHours())
        # Update project head (object)
        self.getProjectHead().hoursTotal = self.countTotalHours()
        # Update overview tab (call ProjectPage.updateOverview())
        self.updateOverview()

# Session -widget
class SessionWidget():
    def __init__(self, sessionsTab:SessionsTab, sessionsListView:ctk.CTkScrollableFrame, sessionData:SessionData):
        self.sessionsTab = sessionsTab
        self.sessionsListView = sessionsListView
        self.sessionData = sessionData
        # Widget values
        outerHeight = 50
        innerHeight = 40
        innerHeight2 = int(innerHeight/2)
        # Description (button). Custom colors (light, dark)
        descHoverColors = ("#C6DCD9","#404040")
        # Destroy (button). Custom colors (light, dark)
        destroyFgColors = ("#cfcfcf","#2b2b2b")
        destroyHoverColors = ("#C6DCD9","#404040")

        self.frame = ctk.CTkFrame(master=self.sessionsListView,height=outerHeight)
        self.frame.pack(padx=10,pady=10,fill='x')
        self.labelHours:ctk.CTkLabel = None
        # Time start edit
        def setStartTime():
            print("Set new start time.. for id: " + self.sessionData.id)
            dateStart = str(datetime.datetime.now())
            if ("." in dateStart):
                dateStart = dateStart.split(".")[0]
            self.sessionData.dateStart = dateStart
            # destroy Start-button, show label
            startDateButton.destroy()
            labelDateStart.place(relx=(2/4),y=5,relwidth=(1/4))
            labelDateStart.configure(text=dateStart)
            # PARAMS: (sessionId, column, newValue)
            self.sessionsTab.updateSessionDataColumn(self.sessionData.id,"DATESTART",dateStart)

        # Time end edit
        def setEndTime():
            print("Set new end time.. for id: " + self.sessionData.id)
            if(len(self.sessionData.dateStart)==0):
                print("--> Can't set end date before start date is set")
                return
            dateEnd = str(datetime.datetime.now())
            if ("." in dateEnd):
                dateEnd = dateEnd.split(".")[0]
            self.sessionData.dateEnd = dateEnd
            # destroy End-button, show label
            endDateButton.destroy()
            labelDateEnd.place(relx=(2/4),y=innerHeight2+5,relwidth=(1/4))
            labelDateEnd.configure(text=dateEnd)
            # PARAMS: (sessionId, column, newValue)
            self.sessionsTab.updateSessionDataColumn(self.sessionData.id,"DATEEND",dateEnd)
            # Update hours
            self.updateHours()

        # Description edit
        def editDescription():
            print("editDescription")
            frameEditDescription.place(x=0, y=0, relheight=1, relwidth=1)
            # Delete old and set text to TextBox
            textBoxDesc.delete(1.0,END) # From line1,character0 to END
            textBoxDesc.insert(1.0,self.sessionData.description)
            return "break"
        # .
        def saveDescription():
            print("Save Description")
            newValue = textBoxDesc.get(1.0,"end-1c" ) #-1c Removes automatic newline from end
            print("--> LEN(newValue):" +str( len(newValue)))
            self.sessionData.description = newValue
            buttonEditDesc.configure(text=newValue)
            closeEditDesc()
            # Save to DB
            self.sessionsTab.updateSessionDataColumn(self.sessionData.id,"DESCRIPTION",newValue)
        # .
        def cancelDescription():
            print("Cancel Description")
            closeEditDesc()
        # .
        def closeEditDesc():
            print("-> closeEditDesc")
            # Hide text box, set focus out to main widget
            frameEditDescription.place_forget()
            self.sessionsListView.focus()

        # Destroy session
        def destroySession():
            print("destroySession")
            dbPath = self.sessionsTab.getProjectHead().sessionsDbPath
            id = self.sessionData.id
            # Remove from db
            self.sessionsTab.dbServices.removeSessionRow(dbPath,id)
            # Remove widget
            self.frame.destroy()
            # Update total hours to project head (obj) 
            self.sessionsTab.updateTotalHoursOfAllSessions()

        ####################################################
        # Widgets
        ####################################################
        # Description (as button) - (Description edit frame is added last)
        buttonEditDesc = ctk.CTkButton(master=self.frame, 
                                       text=sessionData.description, 
                                       height=innerHeight, 
                                       fg_color=colors.getLayer4(), 
                                       text_color=colors.getText1(),
                                       hover_color=descHoverColors,
                                       command=editDescription)
        buttonEditDesc.place(x=5,y=5,relwidth=0.49)

        # Start Date
        labelDateStart = ctk.CTkLabel(master=self.frame, text=sessionData.dateStart,height=innerHeight2,corner_radius=0)
        labelDateStart.place(relx=(2/4),y=5,relwidth=(1/4))
        if not (len(sessionData.dateStart) > 0):
            startDateButton = ctk.CTkButton(master=self.frame,text="Start",command=setStartTime,height=innerHeight2)
            startDateButton.place(relx=(2/4),y=5,relwidth=(1/4))
            labelDateStart.place_forget()

        # End Date
        labelDateEnd = ctk.CTkLabel(master=self.frame, text=sessionData.dateEnd,height=innerHeight2,corner_radius=0)
        labelDateEnd.place(relx=(2/4),y=innerHeight2+5,relwidth=(1/4))
        if not (len(sessionData.dateEnd) > 0):
            endDateButton = ctk.CTkButton(master=self.frame,text="Stop",command=setEndTime,height=innerHeight2)
            endDateButton.place(relx=(2/4),y=innerHeight2+5,relwidth=(1/4))
            labelDateEnd.place_forget()
        
        # Hours
        labelHours = ctk.CTkLabel(master=self.frame, text=sessionData.hours,height=innerHeight)
        labelHours.place(relx=(3/4),y=5,relwidth=0.24)
        self.labelHours = labelHours
        
        # Destroy session
        buttonDestroy = ctk.CTkButton(master=self.frame,text="x", command=destroySession, width=14,height=14, text_color=destroyFgColors, fg_color=destroyFgColors, hover_color=destroyHoverColors)
        buttonDestroy.place(relx=1, y=0, anchor="ne")

        # Description edit frame
        frameEditDescription = ctk.CTkFrame(master=self.frame,height=outerHeight-10)
        frameEditDescription.place()
        descFrameRight = ctk.CTkFrame(master=frameEditDescription,width=60,fg_color="transparent")
        descFrameRight.pack(padx=10,side="right",fill='y')
        descFrameRight.pack_propagate(0)
        descFrameLeft = ctk.CTkFrame(master=frameEditDescription)
        descFrameLeft.pack(side="right",fill='both',expand=True)
        descFrameLeft.pack_propagate(0)

        textBoxDesc = ctk.CTkTextbox(master=descFrameLeft)
        textBoxDesc.pack(fill='both')
        buttonDescSave = ctk.CTkButton(master=descFrameRight,text="Save",command=saveDescription,height=20)
        buttonDescSave.pack()
        buttonDescCancel = ctk.CTkButton(master=descFrameRight,text="Cancel",command=cancelDescription,height=20)
        buttonDescCancel.pack(pady=4)
        frameEditDescription.place_forget()

    def updateHours(self):
        print("updateHours")
        if not self.sessionsListView:
            print("--> Can't update hours. sessionsListView is None")
            return
        if not self.sessionData:
            print("--> Can't update hours. sessionData is None")
            return
        # time string example. '2024-05-09 00:49:15' --> '%Y-%m-%d %H:%M:%S'
        dateEnd = self.sessionData.dateEnd 
        dateStart = self.sessionData.dateStart
        dateEndObject = datetime.datetime.strptime(dateEnd, "%Y-%m-%d %H:%M:%S")
        dateStartObject = datetime.datetime.strptime(dateStart, "%Y-%m-%d %H:%M:%S")

        # Get time between -> seconds -> /60 (to min) /60 (to h) --> total hours
        timeBetween = dateEndObject - dateStartObject
        totalHours = timeBetween.total_seconds() * (1/60) * (1/60)
        totalHours = round(totalHours,2)
        self.sessionData.hours = totalHours
        # Update label
        self.labelHours.configure(text=totalHours)
        # Update session db
        # PARAMS: (sessionId, column, newValue)
        self.sessionsTab.updateSessionDataColumn(self.sessionData.id,"HOURS",totalHours)
        # Update All sessions total hours count
        self.sessionsTab.updateTotalHoursOfAllSessions()
