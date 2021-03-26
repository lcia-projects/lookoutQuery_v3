# Louisiana State Police / Louisiana Cyber Investigators Alliance
#   -- csirtg.io : CIFv5 open source cyber threat database
#
# CIFv5 is an opensource self hosted indicator of threat database that can be queried using a REST API

import requests
from datetime import datetime
from tqdm import tqdm
import os

class CIFv5_Query:
    responseArray=[]
    resultsData = []
    def __init__(self, lookout_config):
        self.serverAddress = lookout_config['cif_server']
        self.serverPort=lookout_config['cif_port']
        self.serverLink = "http://" + str(self.serverAddress) + ":" + str(self.serverPort) +"/indicators"
        self.cif_outputFolder = lookout_config['lookout_default_outputFolder']
        self.resultsData.clear()
        self.resultsData=[]

    #checks to see if CIF server is online
    def checkForCIF(self):
        print ("-- Checking For CIF Server --")
#        pingString="ping -o -c 1 -W 3000 " + self.serverAddress
        pingString="ping -c 1 -W 3000 " + self.serverAddress
        ret = os.system(pingString)
        if ret != 0:
            print (" ERROR: No CIF Server Found")
            print ("--=========================--")
            return False
        else:
            print(" CIF Server Found")
            print("--=========================--")
            return True

    def processResultsData(self, resultsData):

        LineList=[]

        if resultsData:
            for item in resultsData:
                strIndicator=str(item[0]['indicator'])
                strType=str(item[0]['itype'])
                strTLP=str(item[0]['tlp'])
                strProvider=str(item[0]['provider'])
                strCount=str(item[0]['count'])
                strConfidence=str(item[0]['confidence'])
                if "description" in item[0].keys():
                    strDescription=str(item[0]['description'])
                else:
                    strDescription=""
                strReportTime=str(datetime.fromtimestamp(item[0]['reported_at']))
                strLine=strIndicator+","+strType+","+strTLP+","+strProvider+","+strConfidence+","+strCount+","+strReportTime
                LineList.append(strLine)
            LineList.insert(0,"indicator,type,tlp,provider,confidence,count,report_time")
        return LineList.copy()

    def QueryCif(self, queryData):
        responseArray=[]
        resultsDict={}
        resultsDict.clear()
        responseArray.clear()

        try:
            for item in tqdm(queryData):
                headers = {'accept': 'application/json', }
                params = (('indicator', item), ('nolog', 1))
                response = requests.get(self.serverLink, headers=headers, params=params)
                if len(response.json()) > 0 :
                    responseArray.append(response.json())

            return(self.processResultsData(responseArray))
        except:
            print ("ERROR ON:", ":", item)
