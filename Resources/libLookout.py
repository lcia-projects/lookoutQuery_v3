# Louisiana State Police / Louisiana Cyber Investigators Alliance
# Project Lookout Query Tool: takes either a file or folder, pulls out all public IP addresses and queries multiple
#   sources for threat information. Then builds a report

# Library for utility classes and methods:

class lookout:
    def __init__(self):
        print ("--=== Lookout Object Created ===--")

    def buildReport(self, UniqueIPDict):
        for file in UniqueIPDict:
            for module in UniqueIPDict[file]:
                if module == "FireHol":
                    self.processFireHol(UniqueIPDict[file][module])
                if module == "ScoutPrime":
                    self.processScoutPrime(UniqueIPDict[file][module])
                if module == "CIF":
                    self.processCIF(UniqueIPDict[file][module])
                if module == "geoIP":
                    self.processGeoIP(UniqueIPDict[file][module])

                # for item in UniqueIPDict[file][module]:
                #    print ("::", file, ":", module, ":", item)

    def processFireHol(self, FileHolList):
        print ("FireHol:", FileHolList)

    def processScoutPrime(self, ScoutPrimeList):
        print ("Scout Prime:", ScoutPrimeList)

    def processCIF(self, CIFList):
        print ("CIF:  ")
        for item in CIFList:
            print ("    ::", item[0])

    def processGeoIP(self, geoIPList):
        print ("GeoIP", geoIPList)

