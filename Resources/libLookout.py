# Louisiana State Police / Louisiana Cyber Investigators Alliance
# Project Lookout Query Tool: takes either a file or folder, pulls out all public IP addresses and queries multiple
#   sources for threat information. Then builds a report

# ToDo:
# - once files are processed in the "ToProcess" folder they are moved to a "completed" folder
# - LOTS of error checking

# Library for utility classes and methods:
import csv

class lookout:
    def __init__(self, lookout_config):
        print ("  --=== Lookout Started, Please Wait ===--")
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
                if module == "cymru":
                    print ("cymru")
                if module == "greynoise":
                    self.processGreyNoise(UniqueIPDict[file][module],file)
                if module == "whois":
                    self.processWhoIs(UniqueIPDict[file][module], file)

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
        try:
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
        except:
            print ("There was an error writing the cif file")

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

    def processGreyNoise(self, GreyNoiseList, file):
        print ("--: Writing GreyNoise:", file)

        reportName = file
        reportName = reportName.replace(self.lookout_config["lookout_default_inputFolder"], "")
        reportName = reportName.replace(".csv", "")
        reportName = reportName.replace(" ", "_")
        reportName = reportName.replace("/", "")
        reportName = self.lookout_config['lookout_default_outputFolder'] + "/" + reportName + "_greynoise.csv"

        csvWriter = open(reportName, "w")
        strHeader = "ip,name,noise,riot,link,last_seen\n"
        csvWriter.write(strHeader)
        for item in GreyNoiseList:
            if 'ip' in item.keys():
                strLineItem=item['ip']
            else:
                strLineItem=" ,"
            if 'classification' in item.keys():
                strLineItem+= ","+str(item['classification'])
            else:
                strLineItem += "," + " "

            if 'name' in item.keys():
                strLineItem+= ","+str(item['name'])
            else:
                strLineItem += "," + " "

            if 'noise' in item.keys():
                strLineItem+= ","+str(item['noise'])
            else:
                strLineItem += "," + " "

            if 'riot' in item.keys():
                strLineItem+= ","+str(item['riot'])
            else:
                strLineItem += "," + " "

            if 'link' in item.keys():
                strLineItem+= ","+str(item['link']) + " "
            else:
                strLineItem += "," + " "

            if 'last_seen' in item.keys():
                strLineItem+= ","+str(item['last_seen'])
            else:
                strLineItem += "," + " "

            strLineItem += "\n"
            csvWriter.write(strLineItem)
        csvWriter.close()

    def processWhoIs(self,WhoIsList, file):
        print("--: Writing WhoIs", file)

        # formats the report filename
        reportName = file
        reportName = reportName.replace(self.lookout_config["lookout_default_inputFolder"], "")
        reportName = reportName.replace(".csv", "")
        reportName = reportName.replace(" ", "_")
        reportName = reportName.replace("/", "")
        reportName = self.lookout_config['lookout_default_outputFolder'] + "/" + reportName + "_whois.csv"
        csvWriter = open(reportName, "w")

        strHeader="ip," + "nir," + "asn_registry," + "asn," + "asn_cidr," + "asn_country_code," + "asn_date," + \
                  "asn_description," + "query," + "cidr," + "name," + "handle," + "range," + "description," + \
                  "country," + "state," + "city," + "address," + "postal_code," + "emails," + "created," + \
                  "updated," + "raw," + "referral," + "raw_referral\n"

        csvWriter.write(strHeader)
        for item in WhoIsList:
            strLine=item['query']
            for key in item.keys():
                if key in item.keys():
                    if key == "nets": #each entry might have a multiple "nets" entries in a list
                        for net_entry in item[key]:
                            for netItem in net_entry.keys():
                                net_entry[netItem]=str(net_entry[netItem])
                                net_entry[netItem]=net_entry[netItem].replace(","," ")
                                net_entry[netItem]=net_entry[netItem].replace("\n", " ")
                                net_entry[netItem]=net_entry[netItem].strip()
                                strLine+=str(net_entry[netItem] )+","
                    else:
                        if item[key] != None:
                            item[key]=item[key].replace(","," ")
                            item[key] = item[key].replace("\n", " ")
                            strLine=strLine + item[key]+","
                        else:
                            strLine = strLine + " " + ","
                else:
                    strLine=strLine+" ,"
            strLine+="\n"
            csvWriter.write(strLine)
        csvWriter.close()