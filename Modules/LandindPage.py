# Widget for the Landing page (Sections: "All" & "New")

from tkinter import *
import customtkinter as ctk
from typing import Callable, List
import Modules.ColorSchemes as colors
from Modules.DbServices import DbServices
from Modules.Settings import AppSettings

class LandingPage():
    def __init__(self, landingPageFrame:ctk.CTkFrame, dbServices:DbServices, appSettings:AppSettings, setViewFromActiveId:Callable[[],None]):
        self.landingPageFrame : ctk.CTkFrame = landingPageFrame 
        self.dbServices : DbServices = dbServices
        self.appSettings : AppSettings = appSettings
        self.setViewFromActiveId : Callable[[],None] = setViewFromActiveId
        self.projectsListView : ctk.CTkFrame = None
        self.projectsFrame : ctk.CTkFrame = None
        self.creationFrame : ctk.CTkFrame = None
        self.segmentsButton : ctk.CTkSegmentedButton = None
        self.segmentNames : List[str] = ["All Projects", "Create New", "App Settings"]
        ####################################################
        # Top bar
        ####################################################
        sectionsTopBar = ctk.CTkFrame(master=self.landingPageFrame,fg_color=colors.getLayer1())
        sectionsTopBar.pack(fill='x')

        segmentsButton = ctk.CTkSegmentedButton(
            master=sectionsTopBar,
            fg_color=colors.getLayer2(),
            selected_color=colors.getTabSelected(),
            unselected_color=colors.getTabUnselected(),
            selected_hover_color=colors.getTabSelectedHover(),
            unselected_hover_color=colors.getTabUnselectedHover(),
            text_color=colors.getText1(),
            values=self.segmentNames,
            dynamic_resizing=True,
            command=self.navigateToSection)
        segmentsButton.set(self.segmentNames[0])
        segmentsButton.pack(padx=20,fill='x',expand=True)
        self.segmentsButton = segmentsButton
        self.segmentsButton.prev = self.segmentNames[0]

        ####################################################
        # Sections Frame (Projects view / Creation View)
        ####################################################
        sectionsFrame = ctk.CTkFrame(master=self.landingPageFrame)
        sectionsFrame.pack(fill='x')

        ####################################################
        # All Projects 
        ####################################################
        projectsFrame = ctk.CTkFrame(master=sectionsFrame)
        projectsFrame.pack(padx=20,fill='x')
        self.projectsFrame = projectsFrame
        # Label
        allLabel = ctk.CTkLabel(master=projectsFrame, text=self.segmentNames[0],fg_color=colors.getLayer3())
        allLabel.pack(pady=(10))
        # Projects
        projectsListView = ctk.CTkScrollableFrame(master=projectsFrame,fg_color=colors.getLayer3())
        projectsListView.pack(fill='x')
        self.projectsListView = projectsListView

        self.updateProjectsListView()

        ####################################################
        # Create New Project
        ####################################################
        creationFrame = ctk.CTkFrame(master=sectionsFrame)
        creationFrame.pack(padx=20,fill='x')
        self.creationFrame = creationFrame
        # Label
        newLabel = ctk.CTkLabel(master=creationFrame, text=self.segmentNames[1],fg_color=colors.getLayer3())
        newLabel.pack(pady=(10))
        # Inputs
        nameEntry = ctk.CTkEntry(creationFrame, placeholder_text="Name")
        nameEntry.pack(padx=20,fill='x')
        self.creationFrame.nameEntry = nameEntry
        descEntry = ctk.CTkEntry(creationFrame, placeholder_text="Description")
        descEntry.pack(padx=20,fill='x')
        self.creationFrame.descEntry = descEntry
        # Create
        newButton = ctk.CTkButton(master=creationFrame,text="Create!",command=lambda:self.createNewProject(nameEntry.get(),descEntry.get()))
        newButton.pack(padx=20,pady=20)
        # hide
        creationFrame.pack_forget()

        ####################################################
        # App Settings
        ####################################################
        settingsFrame = ctk.CTkFrame(master=sectionsFrame)
        settingsFrame.pack(padx=20,fill='x')
        self.settingsFrame = settingsFrame
        # Label
        settingsLabel = ctk.CTkLabel(master=settingsFrame, text=self.segmentNames[2],fg_color=colors.getLayer3())
        settingsLabel.pack(pady=(10))
        # Theme
        def changeTheme():
            print("changeTheme: " + str(ivTheme.get()))
            self.appSettings.setValue("main","darkTheme",ivTheme.get())
            # newTheme = "light"
            # if(ivTheme.get() == 1): 
            newTheme = "dark" if ivTheme.get()==1 else "light"
            ctk.set_appearance_mode(newTheme)
           
        ivTheme = IntVar(value=self.appSettings.getDarkTheme())
        themeCheckbox = ctk.CTkCheckBox(master=settingsFrame, text="Dark theme",onvalue=1,offvalue=0,variable=ivTheme,command=changeTheme)
        themeCheckbox.pack(padx=20,pady=20)
        # hide
        settingsFrame.pack_forget()

    def navigateToSection(self,val) -> None:
            print("Change langingpage segment to: " +val)
            if val == self.segmentsButton.prev:
                print("--> val == self.segmentsButton.prev --> return")
                return
            # "All projects"
            if(val == self.segmentNames[0]):
                self.creationFrame.pack_forget()
                self.settingsFrame.pack_forget()
                self.projectsFrame.pack(padx=20,fill='x')
            # "Create New"
            elif (val == self.segmentNames[1]):
                self.projectsFrame.pack_forget()
                self.settingsFrame.pack_forget()
                self.creationFrame.pack(padx=20,fill='x')
            # "App settings"
            else:
                self.projectsFrame.pack_forget()
                self.creationFrame.pack_forget()
                self.settingsFrame.pack(padx=20,fill='x')
                 
            self.segmentsButton.prev = val
            self.clearCreationInputs()

    def openProject(self,id) -> None:
            print(10*"-")
            print("\nOpen Project. id: " + id)
            self.setViewFromActiveId(id)

    def updateProjectsListView(self) -> None:
        print("updateProjectsListView")
        # Remove old list entries
        for w in reversed(self.projectsListView.pack_slaves()):
            w.destroy()
        # ID, NAME, SESSIONSDBPATH, DATE, DESCRIPTION
        projects = self.dbServices.getProjects()
        for proj in projects:
            projTitle = str(proj[1] + " " + proj[3])
            print(" - Add project to list: " + projTitle + "with id: " +proj[0])
            b = ctk.CTkButton(
                 master=self.projectsListView,
                 text=projTitle, 
                 command=lambda val=proj[0]:self.openProject(val))
            b.pack(padx=10,pady=5,fill='x')

    def createNewProject(self,name,description) -> None:
        print(f"createNewProject. name: {name}, description: {description}")
        projectId = self.dbServices.createNewProjectDbFiles(name,description)

        # Change landingpage segment to projects view, update projects list. (Same function as pressing segment button)
        self.segmentsButton.set("All")
        self.navigateToSection("All")
        self.updateProjectsListView()

        # Change view into Project
        self.setViewFromActiveId(projectId)

    def clearCreationInputs(self) -> None:
        # Clear text if has any, set focus out to main widget
        if(len(self.creationFrame.nameEntry.get()) > 0):
            self.creationFrame.nameEntry.delete(0,END)
        if(len(self.creationFrame.descEntry.get()) > 0):
            self.creationFrame.descEntry.delete(0,END)
        self.landingPageFrame.focus()