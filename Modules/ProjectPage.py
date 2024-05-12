# FILE CONTENTS
# - Classes related to the active (open) project
# - Widget for the active project page
###
# MORE INFO
###
# One project can be open at time (ActiveProjectHead). 
# - All ProjectHeads are saved in TimeMarkerProjects.db.
# - ProjectHead includes general info and a path to a unique Sessions db.
# Sessions db has all the sessions of to the project.
# - One Session has a Start and End date --> total hours per session

from tkinter import *
import customtkinter as ctk
from typing import Callable

import datetime
from Modules.DbServices import DbServices
import Modules.ColorSchemes as colors

# Active project data
class ActiveProjectHead():
    def __init__(self, id, name, sessionsDbPath, date, description, hoursTotal):
        self.id :str = id
        self.name :str = name
        self.sessionsDbPath :str = sessionsDbPath
        self.date :str = date
        self.description :str = description
        self.hoursTotal :float = hoursTotal

# Project main page
class ProjectPage():
    def __init__(self, projectPageFrame:ctk.CTkFrame, dbServices:DbServices, returnToLandingPage:Callable[[],None]):
        self.projectPageFrame :ctk.CTkFrame = projectPageFrame
        self.dbServices : DbServices = dbServices
        self.sessionsPage : SessionsPage = None
        self.overviewPage : OverviewPage = None
        self.projectHead : ActiveProjectHead = None
        self.returnToLandingPage : Callable[[],] = returnToLandingPage

        ###################################
        # Tabs
        ###################################
        def onTabChange(value):
            print("onTabChange -> open tab: " + value)
            if (value == "Sessions"):
                overviewFrame.pack_forget()
                sessionsFrame.pack(fill='both')
            else:
                sessionsFrame.pack_forget()
                overviewFrame.pack(fill='both')
                self.overviewPage.updateOverView()

        tabsVar = StringVar(value="Sessions")
        tabsFrame = ctk.CTkFrame(master=projectPageFrame,fg_color=colors.getLayer1())
        tabsFrame.pack(fill='x')

        tabs = ctk.CTkSegmentedButton(
            master=tabsFrame,
            fg_color=colors.getLayer2(),
            selected_color=colors.getTabSelected(),
            unselected_color=colors.getTabUnselected(),
            selected_hover_color=colors.getTabSelectedHover(),
            unselected_hover_color=colors.getTabUnselectedHover(),
            text_color=colors.getText1(),
            values=["Sessions", "Overview"],
            variable=tabsVar,
            dynamic_resizing=True,
            command=onTabChange)
        tabs.set("Sessions")
        tabs.pack(padx=20,fill='x')

        ###################################
        # Sessions frame
        ###################################
        sessionsFrame = ctk.CTkFrame(master=projectPageFrame)
        sessionsFrame.pack(fill='both')
        self.sessionsPage = SessionsPage(self, sessionsFrame, self.dbServices, self.getProjectHead)

        ###################################
        # Overview frame
        ###################################
        overviewFrame = ctk.CTkFrame(master=projectPageFrame)
        overviewFrame.pack(fill='both')
        self.overviewPage = OverviewPage(overviewFrame, self.dbServices, self.getProjectHead, self.deleteProject)
        overviewFrame.pack_forget()

    def setProjectHead(self, projectHead:ActiveProjectHead):
        print(f"setProjectHead to {projectHead.name}")
        self.projectHead = projectHead
    def getProjectHead(self) -> ActiveProjectHead:
        return self.projectHead
    def updateSessions(self):
        print("updateSessions")
        self.sessionsPage.updateSessionsListView()
    def deleteProject(self):
        print("deleteProject")
        if not (self.getProjectHead()):
            print("--> Couldn't get projectHead -> return")
            return

        # Delete sessions db file
        success:bool = self.dbServices.deleteSessionDb(self.getProjectHead().sessionsDbPath)
        
        # Delete project row from Projects.db
        self.dbServices.removeRowFromProjectsDb(self.getProjectHead().id)

        # Return to landing page (Projects list updates at change)
        self.returnToLandingPage()

    def updateOverView(self):
        print("- updateOverView (call overviewPage)")
        if not (self.overviewPage):
            print("--> Couldn't get projectPageFrame -> return")
            return
        self.overviewPage.updateOverView()

# Overview (Tab)
class OverviewPage():
    def __init__(self, overviewFrame:ctk.CTkFrame, dbServices:DbServices, getProjectHead: Callable[[],ActiveProjectHead], deleteProject):
        self.overviewFrame:ctk.CTkFrame = overviewFrame
        self.dbServices:DbServices = dbServices
        self.getProjectHead:Callable[[],ActiveProjectHead] = getProjectHead
        self.deleteProject:Callable[[],] = deleteProject

        headFrame = ctk.CTkScrollableFrame(master=overviewFrame,height=500)
        headFrame.pack(padx=20,pady=20,fill='both',expand=True)

        # Rows (frames). Change color every second row
        rowsForLabel = []
        rowsForValue = []
        legends = ["Hours total","Project Name","Project ID","Sessions DB Path","Created (Y-M-D h:m:s)","Description"]
        for i in range(0,len(legends)):
            row1 = ctk.CTkFrame(master=headFrame,fg_color=colors.getLayer2())
            row2 = ctk.CTkFrame(master=headFrame,fg_color=colors.getLayer3())
            row1.pack(fill='x')
            row2.pack(fill='x')
            rowsForLabel.append(row1)
            rowsForValue.append(row2)

        # Legends
        hoursTotalLabel = ctk.CTkLabel(master=rowsForLabel[0],text=legends[0])
        nameLabel = ctk.CTkLabel(master=rowsForLabel[1],text=legends[1])
        idLabel = ctk.CTkLabel(master=rowsForLabel[2],text=legends[2])
        dbPathLabel = ctk.CTkLabel(master=rowsForLabel[3],text=legends[3])
        dateLabel = ctk.CTkLabel(master=rowsForLabel[4],text=legends[4])
        descriptionLabel = ctk.CTkLabel(master=rowsForLabel[5],text=legends[5])
        # Values
        self.hoursTotalValue = ctk.CTkLabel(master=rowsForValue[0],text="-")
        self.nameLabelValue = ctk.CTkLabel(master=rowsForValue[1],text="-")
        self.idLabelValue = ctk.CTkLabel(master=rowsForValue[2],text="-")
        self.dbPathLabelValue = ctk.CTkLabel(master=rowsForValue[3],text="-")
        self.dateLabelValue = ctk.CTkLabel(master=rowsForValue[4],text="-")
        self.descriptionLabelValue = ctk.CTkLabel(master=rowsForValue[5],text="-")

        # Pack widgets
        padLegend = (20,0)
        padValue = (50,0)
        hoursTotalLabel.pack(padx=padLegend,anchor="w")
        self.hoursTotalValue.pack(padx=padValue,anchor="w")
        nameLabel.pack(padx=padLegend,anchor="w")
        self.nameLabelValue.pack(padx=padValue,anchor="w")
        descriptionLabel.pack(padx=padLegend,anchor="w")
        self.descriptionLabelValue.pack(padx=padValue,anchor="w")
        idLabel.pack(padx=padLegend,anchor="w")
        self.idLabelValue.pack(padx=padValue,anchor="w")
        dbPathLabel.pack(padx=padLegend,anchor="w")
        self.dbPathLabelValue.pack(padx=padValue,anchor="w")
        dateLabel.pack(padx=padLegend,anchor="w")
        self.dateLabelValue.pack(padx=padValue,anchor="w")

        # Remove project section at bottom
        row1 = ctk.CTkFrame(master=headFrame,fg_color=colors.getLayer2())
        row2 = ctk.CTkFrame(master=headFrame,fg_color=colors.getLayer3())
        row1.pack(fill='x')
        row2.pack(fill='x')
        deleteProjectLabel = ctk.CTkLabel(master=row1,text="Delete Project")
        deleteProjectLabel.pack(padx=padLegend,anchor="w")
        deleteProjectButton = ctk.CTkButton(master=row2,text="Delete Project",command=self.deleteProject)
        deleteProjectButton.pack(padx=padValue)

    def updateOverView(self):
        print("-- updateOverView")
        if(self.getProjectHead()):
            self.hoursTotalValue.configure(text=self.getProjectHead().hoursTotal)
            self.idLabelValue.configure(text=self.getProjectHead().id)
            self.nameLabelValue.configure(text=self.getProjectHead().name)
            self.dbPathLabelValue.configure(text=self.getProjectHead().sessionsDbPath)
            self.dateLabelValue.configure(text=self.getProjectHead().date)
            self.descriptionLabelValue.configure(text=self.getProjectHead().description)

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

# Sessions (Tab)
class SessionsPage():
    def __init__(self, projectPage:ProjectPage, sessionsFrame:ctk.CTkFrame, dbServices:DbServices, getProjectHead: Callable[[], ActiveProjectHead]):
        self.dbServices = dbServices
        self.projectPage = projectPage
        self.sessionsListView = None    # Sessions list widget, created last
        # self.activeProjectHead = None   # Project Head Data. Set in main file: onActiveProjectIdChange
        # Callable[[int], str] signifies a function that takes a single parameter of type int and returns a str.
        self.getProjectHead: Callable[[], ActiveProjectHead] = getProjectHead
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
        sessionsTop = ctk.CTkFrame(master=sessionsFrame,fg_color="transparent")
        sessionsTop.pack(fill='x')
        startSessionButton = ctk.CTkButton(master=sessionsTop,text="New session",command=createSession)
        startSessionButton.pack(padx=20,pady=10,side='left')

        ############################################
        # Sessions listview - header
        ############################################
        # padx more on the right to match the scrollbar of sessions listview below
        sessionsHeader = ctk.CTkFrame(master=sessionsFrame,height=30)
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
        sessionsListView = ctk.CTkScrollableFrame(master=sessionsFrame,height=400)
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
        # Update overview
        self.projectPage.updateOverView()

# Session -widget
class SessionWidget():
    def __init__(self, sessionsPage:SessionsPage, sessionsListView:ctk.CTkScrollableFrame, sessionData:SessionData):
        self.sessionsPage = sessionsPage
        self.sessionsListView = sessionsListView
        self.sessionData = sessionData
        # Widget values
        outerHeight = 50
        innerHeight = 40
        innerHeight2 = int(innerHeight/2)
        # Description (button). Custom colors (light, dark)
        descFgColors = ("#cfcfcf","#2b2b2b")
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
            self.sessionsPage.updateSessionDataColumn(self.sessionData.id,"DATESTART",dateStart)

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
            self.sessionsPage.updateSessionDataColumn(self.sessionData.id,"DATEEND",dateEnd)

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
            self.sessionsPage.updateSessionDataColumn(self.sessionData.id,"DESCRIPTION",newValue)
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
            dbPath = self.sessionsPage.getProjectHead().sessionsDbPath
            id = self.sessionData.id
            # Remove from db
            self.sessionsPage.dbServices.removeSessionRow(dbPath,id)
            # Remove widget
            self.frame.destroy()

            # Update total hours to project head (obj) 
            self.sessionsPage.updateTotalHoursOfAllSessions()


        # Description (edit widget added last)
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

        ################################
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
        self.sessionsPage.updateSessionDataColumn(self.sessionData.id,"HOURS",totalHours)

        # Update All sessions total hours count
        self.sessionsPage.updateTotalHoursOfAllSessions()

