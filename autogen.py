# -*- coding: utf-8 -*-
"""
The following code is designed to run on the docker container acilbwh/chestimagingplatform linked below
The current version saves each step of the process into a result file csv

Code Written by Nathan Wies
6/28/2019
"""

import os
import pandas as pd
import numpy as np


#main function for running different aspects of the code
def main():
    makedirectories()
    operation = takeinput()
    files = os.listdir('DicomDataFiles/')
    if(operation == 1):
        print("Starting Scan Analysis...")
        runfiles(files,0)
    elif(operation == 2):
        print("Restarting Scan Analysis from scan 0...")
        runfiles(files,0)
    elif(operation == 3):
        start = startnum()
        print("Restarting analysis from scan" + str(start))
        runfiles(files, start)
    elif(operation == 4):
        combine()
#makes storage directories if needed
def makedirectories():
    directories = ["InputFiles", "FilterFiles","MapFiles","OutputFiles"]
    for direc in directories:
        if not os.path.exists(direc):
            os.makedirs(direc)
#handles user input for restarting code
def startnum():
    checkinput = True
    while(checkinput):
        inval = input("Where are you starting your analysis from (enter the integer from the last file you ran):")
        try: 
            int(inval)
            checkinput = False
            return(int(inval))
        except ValueError:
            checkinput = True
#handles user input for running code        
def takeinput():
    checkinput = True
    while(checkinput):
        inval = input("Would you like to: (1) run scan analysis, (2) restart analysis, (3) continue analysis from terminated process, (4) combine output files: ")
        try: 
            int(inval)
            checkinput = False
        except ValueError:
            checkinput = True
        if(checkinput == False and (int(inval)==1 or int(inval) == 2 or int(inval) == 3 or int(inval)==4)):
            return int(inval)
        else:
            checkinput = True
            print("Invalid Input, please enter a number 1, 2, 3 or 4")
#main pipeline for analysis         
def runfiles(files, startnum):
    i = startnum
    for filnam in files[startnum:]:
        print("Processing Scan Number " +str(i)+" of "+ str(len(files)-1) +" Named: " + filnam)
        os.system("ConvertDicom --dir DicomDataFiles/"+ filnam +" -o InputFiles/" + filnam + "_input.nrrd >/dev/null")
        os.system("GenerateMedianFilteredImage -i InputFiles/" + filnam + "_input.nrrd -o FilterFiles/" + filnam + "_filtered_ct.nrrd >/dev/null")
        os.system("GeneratePartialLungLabelMap --ict  FilterFiles/" + filnam + "_filtered_ct.nrrd -o MapFiles/" + filnam + "_partialLungLabelMap.nrrd >/dev/null")
        os.system("python ../ChestImagingPlatform/cip_python/phenotypes/parenchyma_phenotypes.py --in_ct InputFiles/" + filnam + "_input.nrrd --in_lm MapFiles/" + filnam + "_partialLungLabelMap.nrrd --cid InputFiles/" + filnam + "_input.nrrd -r WholeLung,LeftLung,RightLung --out_csv OutputFiles/" + filnam + "_total_parenchyma_phenotypes_file.csv >/dev/null")
        i = i+1
#combines output data into one file       
def combine():
    files = os.listdir("OutputFiles/")
    filnum = len(files)
    maindf = pd.read_csv("OutputFiles/"+files[0])
    for i in range(filnum-1):
        df = pd.read_csv("OutputFiles/" + files[i+1])
        maindf = maindf.append(df)
        maindf.to_csv("First"+str(filnum)+"Scans.csv", index = False)
main()