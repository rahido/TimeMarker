

import customtkinter as ctk
from typing import Callable
from Modules.DbServices import DbServices
from Modules.ProjectPage.ProjectDataObjects import ActiveProjectHead
import Modules.ColorSchemes as colors

# Overview (Tab)
class OverviewTab():
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
        legends = ["Hours total","Project Name","Description","Project ID","Sessions DB Path","Created (Y-M-D h:m:s)"]
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
        descriptionLabel = ctk.CTkLabel(master=rowsForLabel[2],text=legends[2])
        idLabel = ctk.CTkLabel(master=rowsForLabel[3],text=legends[3])
        dbPathLabel = ctk.CTkLabel(master=rowsForLabel[4],text=legends[4])
        dateLabel = ctk.CTkLabel(master=rowsForLabel[5],text=legends[5])
        # Values
        self.hoursTotalValue = ctk.CTkLabel(master=rowsForValue[0],text="-")
        self.nameLabelValue = ctk.CTkLabel(master=rowsForValue[1],text="-")
        self.descriptionLabelValue = ctk.CTkLabel(master=rowsForValue[2],text="-")
        self.idLabelValue = ctk.CTkLabel(master=rowsForValue[3],text="-")
        self.dbPathLabelValue = ctk.CTkLabel(master=rowsForValue[4],text="-")
        self.dateLabelValue = ctk.CTkLabel(master=rowsForValue[5],text="-")

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
