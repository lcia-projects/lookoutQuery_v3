import os
import sys
from pprint import pprint
from datetime import datetime
import time
from tqdm import tqdm
from pathlib import Path
import shutil
import git
import yaml
from glob import glob

class fireHol_Query:
    ipFileList = []
    ipBlockList = {}
    tagDescDict = {}

    def __init__(self, lookout_config):
        print ("creating firehol object")
        #pprint (lookout_config)
        self.lookout_config=lookout_config
        self.fireHol_dataFolder=lookout_config['fireHol_feed_folder']
        self.fireHol_lastUpdate=lookout_config['firehol_download_date']
        self.fireHol_outputFolder=lookout_config['lookout_default_outputFolder']
        self.processBlockLists()
        self.readProviderDescriptions()

        print ("FireHol :: Last Update:", datetime.fromtimestamp(self.fireHol_lastUpdate))
        self.checkForUpdateData()

        #self.processIPList()

    def checkForUpdateData(self):
        # checks the last update date from the lookout.yml, if its greater than a day, it pulls new indicators from
        # git repository

        currentDate=datetime.now()
        dateDifference=(currentDate-datetime.fromtimestamp(self.fireHol_lastUpdate))

        if dateDifference.days > 1:
            print ("Updating IP Sets from GIT repository, this could take a min or two.. please wait")
            self.pullListsFromGit()
            self.lookout_config['firehol_download_date']=time.time()
            print ("Firehol Databases Updated: new datetime/saved", self.lookout_config['firehol_download_date'])
            self.saveYAMLConfig()

        else:
            print ("Data from FireHol is up to date")

    def pullListsFromGit(self):
        try:
            print ("Pulling new datasets from GIT, this could take a minute or two, please wait..")
            #remove previous data
            dirpath = Path(self.fireHol_dataFolder)
            if dirpath.exists() and dirpath.is_dir():
                shutil.rmtree(dirpath)
            #pull new data
            print ("Getting new data Lists.....")
            git.Git(".").clone("git://github.com/firehol/blocklist-ipsets.git")
            print ("Updated data sets recieved, moving forward with analysis")
        except:
            print ("Error")

    def saveYAMLConfig(self):
        with open(r'lookout.yaml', 'w') as file:
            documents = yaml.dump(self.lookout_config, file)

    def processBlockLists(self):
        print ("Pulling all IP data from Datasets, This could take a min or two, please wait ...")
        blockListFileNames=fileList = glob((self.fireHol_dataFolder+"/*"))

        for file in tqdm(blockListFileNames):
            if ".ipset" in file: # @@ figure out how to add an OR for .netsets, eventually figure out how to add the founders of countries
                with open(file, "r") as filehandler:
                    for line in filehandler:
                        try:
                            if line[0] != "#":
                                line = line.replace("\n", "")
                                self.addToIPDict(line, file)
                        except:
                            e = sys.exc_info()[0]
                            print("ERROR:", e)
                            errorString = "LoadFile ERROR: " + line + " : " + str(e) + "\n"
                            # pprint.pprint(self.deDupedDict)
        print ("IP Data pulled from datasets and processed, moving forward with analysis")

    def addToIPDict(self, address, file):
        tag = file
        tag = tag.replace("./blocklist-ipsets/", "")
        tag = tag.replace(".ipset", "")
        tagArray = []

        if address in self.ipBlockList.keys():  # already found, add new tag
            self.ipBlockList[address].append(tag)
        else:
            tagArray.append(tag)
            self.ipBlockList[address] = tagArray.copy()

    def readProviderDescriptions(self):
        print ("Reading in data descriptions..")
        with open("./Resources/firehol_tag_descriptions.csv", "r") as filehandler:
            for line in filehandler:
                # try:
                if line[0] != "#":
                    line = line.replace("\n", "")
                    tagAndDescList=line.split(",",1)
                    tagAndDescList[1]=tagAndDescList[1].replace('"','')
                    tagAndDescList[1] = tagAndDescList[1].replace('\xa0', ': ')
                    self.tagDescDict[tagAndDescList[0]]=tagAndDescList[1]

    def QueryFireHol(self, IPList):
        itemDict={}
        fileDict={}

        # @@ still need to replace filenames with descriptions
        print ("time to Query!")
        for item in IPList:
            # print ("    --: ", item)
            if item in self.ipBlockList.keys():
                itemDict[item]=self.ipBlockList[item].copy()
                fileDict=itemDict.copy()
        #self.buildReport(fileDict)
        return fileDict.copy()

    def buildReport(self, dataDict):
        print ("building report for firehol")

        strCSV_Header=("file"+","+"Indicator"+"," "blocklist file"+","+ "blocklist description"+"\n")
        for file in dataDict:
            #print (" FireHol File:", file)
            strOutputFileAndPath=self.fireHol_outputFolder + "/"+ file
            strOutputFileAndPath=strOutputFileAndPath.replace(".txt", "_fireHol_results.csv")
            #print (strOutputFileAndPath)
            fileWriter=open(strOutputFileAndPath,"w")
            fileWriter.write(strCSV_Header)
            for ipItem in dataDict[file]:
                #print ("   -: ", ipItem)
                for listItem in dataDict[file][ipItem]:
                    #print ("    --", listItem," : ", self.tagDescDict[listItem])
                    strLineToWrite=(file + ',' + ipItem + ',' + listItem + ',' + '"'+ self.tagDescDict[listItem]+'"' + '\n')
                    #print (strLineToWrite)
                    fileWriter.write(strLineToWrite)
            fileWriter.close()
