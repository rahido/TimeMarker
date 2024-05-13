# App -file for TimeMarker

# Custom tkinter
# https://customtkinter.tomschimansky.com/

from Modules.DbServices import DbServices
from Modules.LandindPage import LandingPage
from Modules.ProjectPage.ProjectPage import ActiveProjectHead, ProjectPage
from Modules.Settings import AppSettings

from tkinter import *
import customtkinter as ctk

# for documenting
from PIL import Image,ImageGrab


class TimeMarker:
    def __init__(self) -> None:
        print("\n")
        print(10*"-")
        print("TimeMarker init")
        
        #################################################################
        # APP SETTINGS
        #################################################################
        
        self.appSettings = AppSettings()
        # General Theme ("light" | "dark")
        if (self.appSettings.getDarkTheme() == 1):
            ctk.set_appearance_mode("dark") 
            print("-> Using dark theme")
        else:
            ctk.set_appearance_mode("light") # "light" | "dark"
            print("-> Using light theme")
        # Color theme
        # ctk.set_default_color_theme("green")

        #################################################################
        # ROOT, other
        #################################################################
        
        self.root = ctk.CTk()
        self.root.geometry("580x400")
        self.root.minsize(200, 200)
        self.root.title('TimeMarker')

        # NOT USED IN PRODUCTION
        # for documenting
        # self.root.bind("<Control-s>", self.grabScreenshot)

        # Database services class
        self.dbServices = DbServices()

        # TopBar Title text (StringVar)
        strDefaultTitle = "Time Marker Projects"
        self.svTitleText = ctk.StringVar(value=strDefaultTitle)


        def setBackButtonVisibility(toVisible) -> None:
            if toVisible:
                backButton.place(x=8,rely=0.5,anchor="w")
            else:
                backButton.place_forget()

        def onActiveProjectIdChange(object,b,mode) -> None:
            print("onActiveProjectIdChange." + self.getActiveProjectId())
            val = self.getActiveProjectId()
            if (val==""):
                # To landing page
                projectPageFrame.pack_forget()
                landingPageFrame.pack(fill='x')
                self.setTopBarTitleText(strDefaultTitle)
                setBackButtonVisibility(False)
                landingPage.updateProjectsListView()
            else:
                # To project page
                p = self.dbServices.getProjectWithId(val)
                if(p):
                    activeProjectHead = ActiveProjectHead(p[0],p[1],p[2],p[3],p[4],p[5])
                    landingPageFrame.pack_forget()
                    projectPageFrame.pack(fill='x')

                    self.setTopBarTitleText(activeProjectHead.name)
                    projectPage.setProjectHead(activeProjectHead)
                    projectPage.updateSessions()
                    projectPage.updateOverView()
                    setBackButtonVisibility(True)
                    
                else:
                    print("--> Error. couldn't find project with id")

        # Active project id value (or "" for landing page)
        self.svActiveProjectId = ctk.StringVar(value="")
        self.svActiveProjectId.trace_add("write", onActiveProjectIdChange)

        #################################################################
        # TOP BAR (visible through out the app)
        #################################################################

        titleBar = ctk.CTkFrame(master=self.root, height=60)
        titleBar.pack(padx=20, pady=20, fill='x')
        titleLabel = ctk.CTkLabel(titleBar, textvariable=self.svTitleText, fg_color="transparent")
        titleLabel.place(relwidth=1,relheight=1,anchor="nw")
        backButton = ctk.CTkButton(master=titleBar,text="<",width=16,height=16,command=self.returnToLandingPage)
        backButton.place(x=8,rely=0.5,anchor="w")
        # Hide backButton at landingpage
        setBackButtonVisibility(False)

        #################################################################
        # LANDINGPAGE (SECTIONS)
        #################################################################

        landingPageFrame = ctk.CTkFrame(master=self.root)
        landingPageFrame.pack(fill='x')
        landingPage = LandingPage(landingPageFrame, self.dbServices, self.appSettings, self.setViewFromActiveId)

        #################################################################
        # ACTIVE PROJECT (SESSIONS & OVERVIEW)
        #################################################################

        # Active Project
        projectPageFrame = ctk.CTkFrame(master=self.root)
        projectPageFrame.pack()
        projectPage = ProjectPage(projectPageFrame, self.dbServices, self.returnToLandingPage)
        # Hide project -page
        projectPageFrame.pack_forget()
    
    def setTopBarTitleText(self,title) -> None:
        self.svTitleText.set(title)

    def setViewFromActiveId(self,id) -> None:
        self.svActiveProjectId.set(id)

    def getActiveProjectId(self) -> str:
        return self.svActiveProjectId.get()

    def returnToLandingPage(self) -> None:
        print(10*"-")
        print("\nReturn To LandingPage")
        self.setViewFromActiveId("")

    def run(self) -> None:
        self.root.mainloop()

    # NOT USED IN PRODUCTION
    # for documenting (screenshot app and save to ../folder)
    def grabScreenshot(self,event):
        toPath = "../Screenshot.png"
        geom = self.root.geometry() #"580x400+52+52"
        x1,y1 = int(geom.split("+")[1]) +8  ,int(geom.split("+")[2])+1
        x2,y2 = x1 + self.root.winfo_width(), y1+ self.root.winfo_height() +30
        bbox = (x1,y1,x2,y2) # left, top, right, bottom
        print("screengrab bbox: " + str(bbox))
        img = ImageGrab.grab(bbox=bbox, include_layered_windows=False, all_screens=False, xdisplay=None)
        img.save(toPath)

app = TimeMarker()
app.run()