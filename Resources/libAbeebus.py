# Converted abeebus project to a class so i can use it within other projects
# https://github.com/13Cubed/Abeebus/blob/master/abeebus.py

import sys
import json
import re
import csv
import argparse
import urllib
from tqdm import tqdm

class abeebus:
    def __init__(self, filenames):
        self.filenames=filenames
        dataResults = self.getData(self.filenames, "")

    def getData(self, filenames, apiToken):
        """
          The given file is scraped for IPv4 addresses, and the addresses are used
          with the GeoIP location provider to obtain location data in JSON format.
          The JSON data is then parsed and appended to the 'results' list.
          """
        from urllib.request import urlopen

        addresses = []
        filteredAddresses = []
        results = []
        print ("Pulling IPs from Files and Geo Locating Them, Please Wait..")
        for filename in filenames:
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
        # Iterate through new list and obtain GeoIP information from ipinfo.io
        for filteredAddress in tqdm(filteredAddresses):
            # Show progress bar
            #self.progressBar(i, total, status='Getting Results')
            #i += 1

            formattedData = ''
            # Build query URL from found addresses

            # Sort addresses by count (descending)
            results = sorted(results, key=lambda x: int(x.split(',')[9]), reverse=True)

            if apiToken:
                url = ('https://ipinfo.io/' + filteredAddress + '/json/?token=' + apiToken)
            else:
                url = ('https://ipinfo.io/' + filteredAddress + '/json')

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

            # Get number of occurrences for IP address and add to results
            addressCount = addressCounts[filteredAddress]
            formattedData += str(addressCount)

            # Add final formatted data string to list
            results.append(formattedData)

        # Sort results from highest count to lowest
        results = sorted(results, key=lambda x: int(x.split(',')[9]), reverse=True)
        self.dataDict=results.copy()

        # Add column headers
        results.insert(0, 'IP Address,Hostname,Country,Region,City,Postal Code,Latitude,Longitude,ASN,Count')
        self.printData(results)

    def getResults(self):
        return self.dataDict.copy()

    def progressBar(count, total, status=''):
        # From https://gist.github.com/vladignatyev/06860ec2040cb497f0f3
        bar_len = 60
        filled_len = int(round(bar_len * count / float(total)))
        percents = round(100.0 * count / float(total), 1)
        bar = '#' * filled_len + '.' * (bar_len - filled_len)
        sys.stdout.write('[%s] %s%s ...%s\r' % (bar, percents, '%', status))
        sys.stdout.flush()

    def getFilteredAddresses(self):
        return self.filteredAddresses

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