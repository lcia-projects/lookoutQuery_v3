# Louisiana State Police / Louisiana Cyber Investigators Alliance
# Project Lookout Query Tool: takes either a file or folder, pulls out all public IP addresses and queries multiple
#   sources for threat information. Then builds a report
# - Resources:
#   -- www.la-safe.org : Louisiana State Police Fusion Center (our point of contect information)
#   -- shodan.io : Search Engine of Internet of Things Devices
#   -- lookingglasscyber.com : scoutPrime threat database
#   -- csirtg.io : CIFv5 open source cyber threat database
#   -- Abeebus: https://github.com/13Cubed/Abeebus : scrapes external ips from text file, geo locates them

# Dependencies:
import yaml
import argparse
from os import path
from glob import glob


from Resources import libLookout
from Resources import libAbeebus

# Allows user to modify paremeters from commandline at runtime
def argsParse():
    # ArgParse Configuration
    parser = argparse.ArgumentParser(description='Lookout Query v3',
                                     usage='main.py <folder> [-w outfile] ', add_help=False)
    parser.add_argument('--folder', help='folder path, process files within folder', nargs="*")
    parser.add_argument('--filename', help='single file to process')
    parser.add_argument('--cif', action="store_true",
                        help='query Cyber Intelligence Framework (internal self-hosted server)', required=False)
    parser.add_argument('--firehol', action="store_true", help='query FireHOL blocklists', required=False)
    parser.add_argument('--scoutprime', action="store_true", help='query LookingGlass Scout Prime', required=False)
    parser.add_argument('--shodan', action="store_true", help='Query Shodan (very slow)', required=False)
    parser.add_argument('--all', action="store_true", help='Query All Available Modules', required=False)
    parser.add_argument('--fullreport', action="store_true", help='Full Indepth Report (MUCH longer)', required=False)
    parser.add_argument('--output', help='set an output folder, if blank, folder will be date-time', required=False)
    parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                        help='Show this help message and exit')
    args = vars(parser.parse_args())
    return args

# Main
if __name__ == '__main__':
    YAMLFILE="./lookout.yaml"
    queryResults={}

    if (path.exists(YAMLFILE)):
        print("Loading yaml settings file")
        # -- Loads Configuration File for LookOut --
        with open(YAMLFILE,"r") as file:
            lookout_config = yaml.load(file, Loader=yaml.FullLoader)
    else:
        print("ERROR: No config file, please refer to lookout.yml.example in root folder of script")
        exit()

    # Process and error check commandline arguments
    args=argsParse()

    # if no folder or file given, defaults to what is in the lookout.yaml configuration file
    if args['folder']==None and args['filename']==None:
        print (" --: No Folder or Filename given for processing, using default value in Lookout.yaml <input folder>")
        args['folder']=lookout_config['lookout_default_inputFolder']

    # Read in File(s)
    if args['folder']:
        folderName = ((args['folder']) + "/*")
        fileList = glob(folderName)
    elif args['filename']:
        fileList = []
        fileList.append(args['filename'])
        # print (fileList)
    else:
        print("ERROR:something went wrong, you cant have a folder and a file selection.")
        exit()

    print (" --: Folder:", folderName)
    print (" --: FileList to process:", fileList)
    lookoutObj=libLookout.lookout()
    # abeebus is an open source project that takes files, finds all the IP addresses and GeoLocates them.
    # i've modified the project into a class/library. It retains a python list of all the parsed IP addresses
    #       abeebusObj.getResults() # returns abeebus results
    #       abeebusObj.getFilteredAddresses() # returns list of unique IPs parsed from text files
    abeebusObj=libAbeebus.abeebus(fileList)
    uniqueIPs=abeebusObj.getIPs(fileList[0])

    UniqueIPs={}
    geoResults={}
    for filename in fileList:
        UniqueIPs[filename]={}
        UniqueIPs[filename]['IPs']=abeebusObj.getIPs(filename)
        UniqueIPs[filename]['geoIP']=abeebusObj.geoLocate(UniqueIPs[filename]['IPs'], apiToken=None)
    print (UniqueIPs)


