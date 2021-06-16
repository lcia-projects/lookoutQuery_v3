from ipwhois import IPWhois
from pprint import pprint
import csv
from tqdm import tqdm

class bulkWhois:
    def __init__(self, lookout_config):
        self.lookout_config=lookout_config

    def queryIPs(self,data):
        resultsList=[]
        for item in tqdm(data):
            try:
                obj = IPWhois(item)
                results = obj.lookup_whois()
                resultsList.append(results)
            except:
                print("error looking up:", item)
        return resultsList.copy()

    # def queryBulkWhois(self, data, filename):
    #     filename=filename.replace("./ToProcess","")
    #     filenameList=filename.split(".")
    #     print (filenameList)
    #     filename=filenameList[0]
    #     strFilenameWithpath = self.lookout_config['lookout_default_outputFolder']+filename+"_whois.csv"
    #     print("Filename:", strFilenameWithpath)
    #     headers=['nir', 'asn_registry', 'asn', 'asn_cidr', 'asn_country_code', 'asn_date', 'asn_description', 'query', 'nets', 'raw', 'referral', 'raw_referral']
    #     with open (strFilenameWithpath, "a+") as csvfile:
    #         writer = csv.DictWriter(csvfile, fieldnames=headers)
    #         writer.writeheader()
    #         for item in tqdm(data):
    #             try:
    #                 obj = IPWhois(item)
    #                 results = obj.lookup_whois()
    #                 print (results)
    #                 writer.writerow(results)
    #             except:
    #                 print ("error looking up:", item)



