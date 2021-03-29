# Louisiana State Police / Louisiana Cyber Investigators Alliance
#   -- csirtg.io : CIFv5 open source cyber threat database
#
# GreyNoise.io

import requests
import json
from pprint import pprint

class greynoise:
    def __init__(self):
        print ("Grey Noise Object Created")

    def QueryGreyNoise(self, queryData, filename):
        responseList=[]

        headers = {
            "Accept": "application/json",
            "User-Agent": "API-Reference-Test"
        }

        for item in queryData:
            #url = "https://api.greynoise.io/v3/community/ip"
            url = "https://api.greynoise.io/v3/community/"+item
            response = requests.request("GET", url, headers=headers)
            responseList.append(json.loads(response.text))
            print (response.text)

        return (responseList.copy())
