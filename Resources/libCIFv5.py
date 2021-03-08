# Louisiana State Police / Louisiana Cyber Investigators Alliance
#   -- csirtg.io : CIFv5 open source cyber threat database
#
# CIFv5 is an opensource self hosted indicator of threat database that can be queried using a REST API

from pprint import pprint
import requests
from datetime import datetime
import time
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
        pingString="ping -o -c 3 -W 3000 " + self.serverAddress
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
                #print ("->", item[0])

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
                #print (strLine)
                LineList.append(strLine)
            LineList.insert(0,"indicator,type,tlp,provider,confidence,count,report_time")
        return LineList.copy()


    def QueryCif(self, queryData):
        print ("Data to Query CIFv5")
        responseArray=[]
        resultsDict={}
        resultsDict.clear()
        responseArray.clear()
        processedResultsList=[]
        #try:
        for item in tqdm(queryData):
            headers = {'accept': 'application/json', }
            params = (('indicator', item), ('nolog', 1))
            response = requests.get(self.serverLink, headers=headers, params=params)
            if len(response.json()) > 0 :
                responseArray.append(response.json())

        return(self.processResultsData(responseArray))

        # except:
        #     print ("ERROR ON:", ":", item)
        # finally:
        #     print ("Complete")
        #     return processedResultsList.copy()

    def buildReport(self, resultsDict):
        strHeaderToWrite=('indicator'+','+'itype'+','+ 'tlp'+','+'provider'+','+ 'count'+','+'tags'+','+' confidence'+','+' description'+','+ 'countryCode'+','+ 'reportedDate'+','+ ' createdDate'+'\n')
        strWriteArray=[]

        print ("-->",type(resultsDict), resultsDict.keys())

        # for file in resultsDict:
        #     print ("type:", self.cif_outputFolder, type(self.cif_outputFolder), "type:", file, type(file))
        #     strFilenameWithPath=str(self.cif_outputFolder)+'/'+file
        #     print ("::",strFilenameWithPath)
        #     strFilenameWithPath=strFilenameWithPath.replace(".txt", "_CIFv5_results.csv")
        #     fileWriter = open(strFilenameWithPath, "w")
        #     fileWriter.write(strHeaderToWrite)
        #     print("CIF FILE:", file)
        #     for ipItem in resultsDict[file]:
        #         #print ("  :",ipItem, ":", resultsDict[file][ipItem])
        #         for cifItem in resultsDict[file][ipItem]:
        #             strWriteArray.append(cifItem)
        #     for item in strWriteArray:
        #         fileWriter.write(self.makeLine(item))
        #     fileWriter.close()

    def makeLine(self, data):
        #print ("Keys:", data.keys())
        if data['indicator']:
            strIndicator=data['indicator']
        else:
            strIndicator=' '

        if data['itype']:
            strItype=data['itype']
        else:
            strItype=' '

        if data['tlp']:
            strtlp=data['tlp']
        else:
            strtlp=' '

        if data['provider']:
            strProvider=data['provider']
        else:
            strProvider=' '

        strTags=""
        if data['tags']:
            #print ("Length of tags:", len(data['tags']))
            strTags=str(data['tags'])
            strTags=strTags.replace(",",":")
            strTags = strTags.replace("'", "")
            strTags = strTags.replace("[", "")
            strTags = strTags.replace("]", "")

        else:
            strTags = ' '

        if data['confidence']:
            strConfidence = str(data['confidence'])
        else:
            strConfidence = ' '

        if 'description' in data.keys():
            strDescription = data['description']
        else:
            strDescription = ' '

        if 'cc' in data.keys():
            strCountryCode = str(data['cc'])
        else:
            strCountryCode = ' '

        if 'reported_at' in data.keys():
            strReportedDate = data['reported_at']
            strReportedDate =time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(strReportedDate))
        else:
            strReportedDate = ' '

        if 'created_at' in data.keys():
            strCreatedDate = data['created_at']
            strCreatedDate = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(strCreatedDate))
        else:
            strCreatedDate = ' '

        if 'count' in data.keys():
            strCount = str(data['count'])
        else:
            strCount = ' '

        #strHeaderToWrite=('indicator'+','+'itype'+','+ 'tlp'+','+'provider'+','+ 'count'+','+'tags'+','+' confidence'+','+' description'+','+ 'countryCode'+','+ 'reportedDate'+','+ ' createdDate'+'\n')
        strLine= strIndicator+","+strItype+","+strtlp+","+strProvider+","+strCount+","+strTags+","+strConfidence+","+strDescription+","+strCountryCode+","+strReportedDate+","+strCreatedDate+"\n"
        return strLine