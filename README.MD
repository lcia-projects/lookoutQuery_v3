# Louisiana State Police / Louisiana Cyber Investigators Alliance
 Project Lookout Query Tool: takes either a file or folder, pulls out all public IP addresses and queries multiple
   sources for threat information. Then builds a report

    Lookout Query v3 
    Usage: main.py <folder> [-w outfile] 

    optional arguments:

    --folder [FOLDER [FOLDER ...]] folder path, process files within folder
    --filename FILENAME   single file to process
    --cif                 query Cyber Intelligence Framework (CIFv5) (internal self-hosted server)
    --firehol             query FireHOL blocklists
    --scoutprime          query LookingGlass Scout Prime
    --shodan              query Shodan (very slow)
    --all                 query All available modules
    --fullreport          Full Indepth Report (MUCH longer)
    --output OUTPUT       set an output folder, if blank, folder will be date-time run
    -h, --help            Show this help message and exit


Usage examples:

    :> python3 lookout.py --file ./firewall.log  --all
    :> python3 lookout.py --folder ./ToProcess  --all 
    :> python3 lookout.py --folder ./ToProcess  --cif --scoutprime --shodan --firehol --output ./caseresult

 
Resources:

    -- Louisiana State Fusion Center http://www.la-safe.org : Louisiana State Police Fusion Center (our point of contect information)
    -- Shodan http://shodan.io : Search Engine of Internet of Things Devices
    -- Looking Glass Cyber http://lookingglasscyber.com : scoutPrime threat database
    -- csirtg.io http://csirtg.io : CIFv5 open source cyber threat database
    -- Abeebus: https://github.com/13Cubed/Abeebus : scrapes external ips from text file, geo locates them
   
