# FILE CONTENTS
# Project Page includes bots Overview and Sessions pages, navigated by tabs
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

from Modules.DbServices import DbServices
import Modules.ColorSchemes as colors
from Modules.ProjectPage.OverviewTab import OverviewTab
from Modules.ProjectPage.ProjectDataObjects import ActiveProjectHead
from Modules.ProjectPage.SessionsTab import SessionsTab

# Project main page
class ProjectPage():
    def __init__(self, projectPageFrame:ctk.CTkFrame, dbServices:DbServices, returnToLandingPage:Callable[[],None]):
        self.projectPageFrame :ctk.CTkFrame = projectPageFrame
        self.dbServices : DbServices = dbServices
        self.sessionsTab : SessionsTab = None
        self.overviewTab : OverviewTab = None
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
                self.overviewTab.updateOverView()

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
        self.sessionsTab = SessionsTab(sessionsFrame, self.dbServices, self.getProjectHead, self.updateOverView)

        ###################################
        # Overview frame
        ###################################
        overviewFrame = ctk.CTkFrame(master=projectPageFrame)
        overviewFrame.pack(fill='both')
        self.overviewTab = OverviewTab(overviewFrame, self.dbServices, self.getProjectHead, self.deleteProject)
        overviewFrame.pack_forget()

    def setProjectHead(self, projectHead:ActiveProjectHead):
        print(f"setProjectHead to {projectHead.name}")
        self.projectHead = projectHead
    def getProjectHead(self) -> ActiveProjectHead:
        return self.projectHead
    def updateSessions(self):
        print("updateSessions")
        self.sessionsTab.updateSessionsListView()
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
        print("- updateOverView (call overviewTab)")
        if not (self.overviewTab):
            print("--> Couldn't get projectPageFrame -> return")
            return
        self.overviewTab.updateOverView()
