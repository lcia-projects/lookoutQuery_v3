# Converted abeebus project to a class so i can use it within other projects
# https://github.com/13Cubed/Abeebus/blob/master/abeebus.py

import sys
import json
import re
import csv
import argparse
import urllib
from tqdm import tqdm
import geoip2.database

class abeebus:
    def __init__(self, filenames, lookout_config):
        self.filenames=filenames
        self.lookout_config=lookout_config
        #dataResults = self.getData(self.filenames, "")

    def getIPs(self, filename):
        addresses=[]
        filteredAddresses=[]
        # Open each specified file for processing
        try:
            f = open(filename, 'r', encoding='ISO-8859-1')
        except IOError:
            print('Could not find the specified file:', filename)
            sys.exit(1)

        # Parse file for valid IPv4 addresses via RegEx
        addresses += re.findall(
            r'(\b(?:(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\.){3}(?:25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9]?[0-9])\b)',
            f.read())
        f.close()

        # Count number of occurrences for each IP address
        from collections import Counter
        addressCounts = Counter(addresses)

        # Remove duplicates from list
        addresses = set(addresses)

        # Filter list to eliminate bogon addresses, the loopback network, link local addresses, and RFC 1918 ranges; add results to new list
        for address in addresses:
            if not (re.match(
                    r'^0.\d{1,3}.\d{1,3}.\d{1,3}$|^127.\d{1,3}.\d{1,3}.\d{1,3}$|^169.254.\d{1,3}.\d{1,3}$|^10.\d{1,3}.\d{1,3}.\d{1,3}$|^172.(1[6-9]|2[0-9]|3[0-1]).[0-9]{1,3}.[0-9]{1,3}$|^192.168.\d{1,3}.\d{1,3}$',
                    address)):
                filteredAddresses.append(address)

        total = len(filteredAddresses)
        i = 0
        self.filteredAddresses=filteredAddresses
        return filteredAddresses.copy()

    def geoLocate(self, ipList, apiToken):
        from urllib.request import urlopen

        addresses = []
        filteredAddresses = []
        results = []

        for filteredAddress in tqdm(ipList):
            formattedData = ''
            try:
                if apiToken:
                    url = ('https://ipinfo.io/' + filteredAddress + '/json/?token=' + apiToken)
                else:
                    url = ('https://ipinfo.io/' + filteredAddress + '/json')
            except:
                print ("Hit Limit, exiting")
                return

            try:
                rawData = urlopen(url).read()
                rawData = json.loads(rawData.decode())
            except:
                if apiToken:
                    print('\n\nIs your API key valid?')

                print('Error parsing address:', filteredAddress)
                sys.exit(1)

            keys = ['ip', 'hostname', 'country', 'region', 'city', 'postal', 'loc', 'org']

            for key in keys:
                try:
                    # If the key exists but is null, set its value to 'N/A'
                    if (rawData[key] == ""):
                        rawData[key] = 'N/A'

                    # If the key is loc, add a trailing comma to the end of the value
                    if (key == 'loc'):
                        formattedData += rawData[key] + ','
                    # If the key is anything else, strip the commas from the value, then add a trailing comma to the end of the value
                    else:
                        formattedData += rawData[key].replace(',', '') + ','

                except:
                    # If the loc key is missing, add 'N/A,N/A' and a trailing comma
                    if (key == 'loc'):
                        formattedData += 'N/A,N/A,'
                    # If any other key is missing, add 'N/A' and a trailing comma
                    else:
                        formattedData += 'N/A,'

            results.append(formattedData)
        self.dataDict=results.copy()

        # Add column headers
        results.insert(0, 'IP Address,Hostname,Country,Region,City,Postal Code,Latitude,Longitude,ASN,Count')
        #self.printData(results)
        return results.copy()

    def geoLocateLocal(self, ipList):
        
        geoList=[]
        if 'maxmind_path' in self.lookout_config.keys() and self.lookout_config['maxmind_path']!= None:
            dbPath=self.lookout_config['maxmind_path']
            reader = geoip2.database.Reader(dbPath+'/GeoLite2-City.mmdb')

            for item in tqdm(ipList):
                geo_iso = ""
                geo_countryName = ""
                geo_specificName = ""
                geo_subDivision = ""
                geo_city = ""
                geo_postal = ""
                geo_Lat = ""
                geo_Long = ""
                geo_Traits = ""
                try:
                    response = reader.city(item)
                    if response.country.iso_code:
                        geo_iso=str(response.country.iso_code)
                    if response.country.name:
                        geo_countryName=str(response.country.name)
                    if response.subdivisions.most_specific.name:
                        geo_specificName=str(response.subdivisions.most_specific.name)
                    if response.subdivisions.most_specific.iso_code:
                        geo_subDivision=str(response.subdivisions.most_specific.iso_code)
                    if response.city.name:
                        geo_city=str(response.city.name)
                    if response.postal.code:
                        geo_postal=str(response.postal.code)
                    if response.location.latitude:
                        geo_Lat=str(response.location.latitude)
                    if response.location.longitude:
                        geo_Long=str(response.location.longitude)
                    if response.traits.network:
                        geo_Traits=str(response.traits.network)
                    strGeoLine=item+","+geo_iso+","+geo_countryName+","+geo_specificName+","+geo_subDivision+","+geo_city+","+geo_postal+","+ geo_Lat + "," + geo_Long+","+geo_Traits
                    geoList.append(strGeoLine)
                except:
                    test=1
        else:
            print ("Error, no maxmind geoIP db path set in configuration file, must exit")
        geoList.insert(0, 'IP Address,ISO,Country,SpecificName,SubDivision,City,PostalCode,Lat,Long,CIDR')
        return geoList

    def printData(self,results):
        rows = list(csv.reader(results))
        widths = [max(len(row[i]) for row in rows) for i in range(len(rows[0]))]
        for row in rows:
            print(' | '.join(cell.ljust(width) for cell, width in zip(row, widths)))

    def writeData(self, results, outfile):
        try:
            f = open(outfile, 'w')
        except IOError:
            print('Could not write the specified file:', outfile)
            sys.exit(1)
        for result in results:
            # While Unicode characters will not be displayed via stdout, they will be written to the file
            f.write(result + '\n')
        f.close()