# Louisiana State Police / Louisiana Cyber Investigators Alliance
# Project Lookout Query Tool: takes either a file or folder, pulls out all public IP addresses and queries multiple
#   sources for threat information. Then builds a report

# Library for utility classes and methods:

class lookout:
    def __init__(self):
        print ("--=== Lookout Object Created ===--")