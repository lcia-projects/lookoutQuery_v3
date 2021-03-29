import requests
import json
from datetime import datetime
from datetime import date
from pprint import pprint

class teamCymru:
    def __init__(self, lookout_config):
        self.lookout_config=lookout_config
        self.cymru_url=lookout_config['cymru_url']
        self.cymru_token=lookout_config['cymru_token']

    def queryCymru(self, queryData,filename):
        # import base64

        strQuery=self.buildQueryArray(queryData)
        ItemCount=(len(strQuery))
        strJobName="Lookout Script: "+ str(datetime.now())
        strJobDescription=str(filename)+ " "+ str(ItemCount) + " Items"
        ipList=self.buildQueryArray(queryData)

        ipList=str(ipList)
        ipList=ipList.replace("[","")
        ipList = ipList.replace("]", "")
        ipList = ipList.replace('"', '')
        ipList=ipList.replace("'","")

        url = self.cymru_url

        # all the ip address related queries, this method runs ALL of them.. "the works"
        queryType_list=["ddos_attacks","ddos_commands","bars_controllers","bars_victims", "dns_derived_domains_via_ip",
                        "dns_derived_ips_via_ip","banners_ptr","dns_query","nmap_dnsrr","pdns","pdns_nxd","pdns_other",
                        "banners","dns_fingerprint","nmap_port","nmap_fingerprint","ntp_server","open_ports",
                        "os_fingerprint","router","sip","snmp","ssh","tor","x509","compromised_hosts","open_resolvers",
                        "conpot_honeypot","cowrie_honeypot","darknet","dionaea_honeypot","portscan","scanner","beacons",
                        "cookies","rdp_traffic","urls","useragents","flows","apt_dns","apt_ip"
                        ]
        queryList=[]
        for queryType in queryType_list:
            strQuery={
                'query_type': queryType,
                'any_ip_addr':ipList,
            }
            queryList.append(strQuery)

        today = date.today()
        end_date_now = str(today.strftime("%m/%d/%Y")+" " + "00:00:00")


        payload = {
            'job_name': strJobName,
            'job_description': strJobDescription,
            'start_date': '01/01/2020 00:00:00',
            'end_date': end_date_now,
            'priority': 25,
            'queries': queryList
        }

        authToken="Token " + self.cymru_token

        headers = {
            "Content-Type": "application/json",
            "Authorization": authToken
        }
        pprint (payload)
        response = requests.request("POST", url, data=json.dumps(payload), headers=headers)
        # print ("Response:", response)
        # print (response.content)
        print ("Sending Query to Team Cymru, please wait (this can take up to 2min)")

    def buildQueryArray(self, queryData):
        returnArray=[]

        for item in  queryData:
            if item == "8.8.8.8" or item == "8.8.4.4":
                continue
            else:
                returnArray.append(item)
        return returnArray.copy()