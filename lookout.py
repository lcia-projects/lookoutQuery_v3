# Louisiana State Police / Louisiana Cyber Investigators Alliance
# Project Lookout Query Tool: takes either a file or folder, pulls out all public IP addresses and queries multiple
#   sources for threat information. Then builds a report
# - Resources:
#   -- www.la-safe.org : Louisiana State Police Fusion Center (our point of contect information)
#   -- shodan.io : Search Engine of Internet of Things Devices
#   -- lookingglasscyber.com : scoutPrime threat database
#   -- csirtg.io : CIFv5 open source cyber threat database
#   -- Abeebus: https://github.com/13Cubed/Abeebus : scrapes external ips from text file, geo locates them

import argparse
from glob import glob
from os import path

# Dependencies:
import yaml
from termcolor import colored

# Custom Resource Libraries to make using outside API's easier
from Resources import libCIFv5
from Resources import libFireHol
from Resources import libGeo
from Resources import libLookout
from Resources import libScoutPrime
from Resources import libShodan
from Resources import libTeamCymru
from Resources import libGreyNoiseCommunityAPI
from Resources import libWhois


# Allows user to modify paremeters from commandline at runtime
def argsParse():
    # ArgParse Configuration
    parser = argparse.ArgumentParser(description='Lookout Query v3',
                                     usage='main.py <folder> [-w outfile] ', add_help=False)
    parser.add_argument('--folder', help='folder path, process files within folder', nargs="*")
    parser.add_argument('--filename', help='single file to process')
    parser.add_argument('--cif', action="store_true",
                        help='query Cyber Intelligence Framework (internal self-hosted server)', required=False)
    parser.add_argument('--geo', action="store_true", help='GeoIP IP Addresses', required=False)
    parser.add_argument('--firehol', action="store_true", help='query FireHOL blocklists', required=False)
    parser.add_argument('--scoutprime', action="store_true", help='query LookingGlass Scout Prime', required=False)
    parser.add_argument('--shodan', action="store_true", help='Query Shodan (very slow)', required=False)
    parser.add_argument('--cymru', action="store_true", help='Query Team Cymru', required=False)
    parser.add_argument('--greynoise', action="store_true", help='greynoise.io query', required=False)
    parser.add_argument('--whois', action="store_true", help='greynoise.io query', required=False)
    parser.add_argument('--all', action="store_true", help='Query All Available Modules', required=False)
    parser.add_argument('--fullreport', action="store_true", help='Full Indepth Report (MUCH longer)', required=False)
    parser.add_argument('--output', help='set an output folder, if blank, folder will be date-time', required=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit')
    args = vars(parser.parse_args())
    return args


# Main
if __name__ == '__main__':
    YAMLFILE = "./lookout.yaml"  # System Configuration and Variables
    queryResults = {}

    if (path.exists(YAMLFILE)):
        # -- Loads Configuration File for LookOut --
        with open(YAMLFILE, "r") as file:
            lookout_config = yaml.load(file, Loader=yaml.FullLoader)
    else:
        print("ERROR: No config file, please refer to lookout.yml.example in root folder of script")
        exit()

    # Process and error check commandline arguments
    args = argsParse()

    # if no folder or file given, defaults to what is in the lookout.yaml configuration file
    if args['folder'] == None and args['filename'] == None:
        print(" --: No Folder or Filename given for processing, using default value in Lookout.yaml <input folder>")
        args['folder'] = lookout_config['lookout_default_inputFolder']

    # Read in File(s)
    if args['folder']:
        folderName = ((args['folder'][0]) + "/*")
        fileList = glob(folderName)
    elif args['filename']:
        fileList = []
        fileList.append(args['filename'])
    else:
        print("ERROR:something went wrong, you cant have a folder and a file selection.")
        exit()

    print(colored("--===================================================--", "blue"))
    print(colored("--                  Lookout v3                      --", "blue"))
    print(colored("--===================================================--", "blue"))
    print(colored(("       --: Folder To Process:" + folderName), "blue"))
    print(colored(("       --: FileList to process:" + str(fileList)), "blue"))
    print(colored("--===================================================--", "blue"))
    lookoutObj = libLookout.lookout(lookout_config)
    # abeebus is an open source project that takes files, finds all the IP addresses and GeoLocates them.
    # i've modified the project into a class/library. It retains a python list of all the parsed IP addresses
    #       abeebusObj.getResults() # returns abeebus results
    #       abeebusObj.getFilteredAddresses() # returns list of unique IPs parsed from text files
    #
    geoObj = libGeo.Geo(fileList, lookout_config)

    cifObj = libCIFv5.CIFv5_Query(lookout_config)
    fireHolObj = libFireHol.fireHol_Query(lookout_config)
    scoutPrimeObj = libScoutPrime.ScoutPrime_Query(lookout_config)
    shodanObj = libShodan.shodan_Query(lookout_config)
    cymruObj = libTeamCymru.teamCymru(lookout_config)
    greynoiseObj= libGreyNoiseCommunityAPI.greynoise()
    whoisObj=libWhois.bulkWhois(lookout_config)

    uniqueIPs = geoObj.getIPs(fileList[0])

    UniqueIPs = {}
    geoResults = {}
    print("\n")
    for filename in fileList:
        print(" ")
        print(colored("===========================================================================", "blue"))
        print(colored(("               Processing: " + filename), "blue"))
        print(colored("===========================================================================", "blue"))
        UniqueIPs[filename] = {}
        UniqueIPs[filename]['IPs'] = geoObj.getIPs(filename)
        if args['geo'] == True or args['all'] == True:
            print("----: Geo Locating IP Addresses:")
            UniqueIPs[filename]['geoIP'] = geoObj.geoLocateLocal(UniqueIPs[filename]['IPs'])
        if args['firehol'] == True or args['all'] == True:
            print("----: Querying Firehol Databases:")
            UniqueIPs[filename]['FireHol'] = fireHolObj.QueryFireHol(UniqueIPs[filename]['IPs'])
        if args['scoutprime'] == True or args['all'] == True:
            print("----: Querying Scout Prime Databases")
            UniqueIPs[filename]['ScoutPrime'] = scoutPrimeObj.QueryIPs(UniqueIPs[filename]['IPs'])
        if args['cif'] == True or args['all'] == True:
            print("----: Querying CIF:")
            if cifObj.checkForCIF():
                UniqueIPs[filename]['CIF'] = cifObj.QueryCif(UniqueIPs[filename]['IPs'])
        if args['greynoise'] == True or args['all'] == True:
            print("----: Querying GreyNoise.io:")
            UniqueIPs[filename]['greynoise'] = greynoiseObj.QueryGreyNoise(UniqueIPs[filename]['IPs'], filename)

        if args['whois'] == True or args['all'] == True:
            print("----: Querying BulkWhoIs:")
            UniqueIPs[filename]['whois'] = whoisObj.queryIPs(UniqueIPs[filename]['IPs'])

        # Not included in "All" because its REALLY slow..
        if args['shodan'] == True:
            print("----: Querying Shodan:")
            UniqueIPs[filename]['Shodan'] = shodanObj.QueryIPs(UniqueIPs[filename]['IPs'])
        # Not included in "All" because we can only do 10 queries a day
        if args['cymru'] == True:
            print("----: Querying Cymru:")
            UniqueIPs[filename]['cymru'] = cymruObj.queryCymru(UniqueIPs[filename]['IPs'], filename)

    print("\n")
    print(colored("----==============================================================-----", "blue"))
    print(colored("--: Saving Data", "blue"))
    print(colored(("--: Report Location:" + lookout_config['lookout_default_outputFolder']), "blue"))
    print(colored("----=============================================================-----", "blue"))
    lookoutObj.buildReport(UniqueIPs)
