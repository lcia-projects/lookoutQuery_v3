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

from Resources import libLookout

# Main
if __name__ == '__main__':
    lookoutObj=libLookout.lookout()