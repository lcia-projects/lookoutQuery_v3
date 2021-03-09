# Louisiana State Police / Louisiana Cyber Investigators Alliance
# Project Lookout Query Tool: takes either a file or folder, pulls out all public IP addresses and queries multiple
#   sources for threat information. Then builds a report

# Library for utility classes and methods:
import csv

class lookout:
    def __init__(self, lookout_config):
        print ("--=== Lookout Started, Please Wait ===--")
        self.lookout_config=lookout_config

    def buildReport(self, UniqueIPDict):
        for file in UniqueIPDict:
            for module in UniqueIPDict[file]:
                if module == "FireHol":
                    self.processFireHol(UniqueIPDict[file][module], file)
                if module == "ScoutPrime":
                    self.processScoutPrime(UniqueIPDict[file][module], file)
                if module == "CIF":
                    self.processCIF(UniqueIPDict[file][module], file)
                if module == "geoIP":
                    self.processGeoIP(UniqueIPDict[file][module], file)

    def processFireHol(self, FileHolList, file):
        print ("--: Writing FireHol: ", file)
        fireholDescDict={}

        # Loads descriptions for Firehol Lists
        with open("./Resources/firehol_tag_descriptions.csv", 'r') as data:
            for line in csv.DictReader(data):
                fireholDescDict[line['name']]=line['info']


        reportName=file
        reportName=reportName.replace(self.lookout_config["lookout_default_inputFolder"],"")
        reportName=reportName.replace(".csv","")
        reportName=reportName.replace(" ","_")
        reportName = reportName.replace("/", "")
        reportName=self.lookout_config['lookout_default_outputFolder'] + "/"+reportName+"_firehol.csv"

        csvWriter=open(reportName,"w")

        for item in FileHolList:
            strTagDesc=""
            for tag in FileHolList[item]:
                strTagDesc = strTagDesc + ":" + tag+"::" + fireholDescDict[tag]  +":::"
            strTagDesc = strTagDesc.replace(",", "")
            strLineToWrite=file + "," + item + "," + str(FileHolList[item]) + "," + strTagDesc + "\n"
            csvWriter.write(strLineToWrite)
        csvWriter.close()

    def processScoutPrime(self, ScoutPrimeList, file):
        print ("--: Writing Scout Prime: ", file)
        reportName = file
        reportName = reportName.replace(self.lookout_config["lookout_default_inputFolder"], "")
        reportName = reportName.replace(".csv", "")
        reportName = reportName.replace(" ", "_")
        reportName = reportName.replace("/", "")
        reportName = self.lookout_config['lookout_default_outputFolder'] + "/" + reportName + "_scoutprime.csv"

        csvWriter = open(reportName, "w")
        csvWriter.write("file,provider,tic_score,scoutPrime_Ref_ID,classification,sources\n")
        if ScoutPrimeList:
            for item in ScoutPrimeList:
                strLineToWrite=file +","+ item+","+str(ScoutPrimeList[item]['provider'])+","+str(ScoutPrimeList[item]['ticScore'])+","+str(ScoutPrimeList[item]['scout_ref_ID'])+","+str(ScoutPrimeList[item]['classification'])+","+str(ScoutPrimeList[item]['sources'])+","+"\n"
                csvWriter.write(strLineToWrite)
        csvWriter.close()

    def processCIF(self, CIFList, file):
        print ("--: Writing CIF:  ", file)
        reportName = file
        reportName = reportName.replace(self.lookout_config["lookout_default_inputFolder"], "")
        reportName = reportName.replace(".csv", "")
        reportName = reportName.replace(" ", "_")
        reportName = reportName.replace("/", "")
        reportName = self.lookout_config['lookout_default_outputFolder'] + "/" + reportName + "_cif.csv"

        csvWriter = open(reportName, "w")
        for item in CIFList:
            strLineToWrite=file+","+item+"\n"
            csvWriter.write(strLineToWrite)
        csvWriter.close()

    def processGeoIP(self, geoIPList, file):
        print ("--: Writing GeoIP: ", file)
        reportName = file
        reportName = reportName.replace(self.lookout_config["lookout_default_inputFolder"], "")
        reportName = reportName.replace(".csv", "")
        reportName = reportName.replace(" ", "_")
        reportName = reportName.replace("/", "")
        reportName = self.lookout_config['lookout_default_outputFolder'] + "/" + reportName + "_geo.csv"

        csvWriter = open(reportName, "w")
        for item in geoIPList:
            strLine=str(item)+"\n"
            csvWriter.write(strLine)
        csvWriter.close()