import shodan
from time import sleep
from tqdm import tqdm
from pprint import pprint

class shodan_Query():
    def __init__(self, lookout_config):
        self.SHODAN_API_KEY = lookout_config['shodan_token']
        self.shodan_outputFolder = lookout_config['lookout_default_outputFolder']

    def QueryIPs(self, ipList):
        resultsItemDict={}
        resultsList=[]

        shodanAPI=shodan.Shodan(self.SHODAN_API_KEY)
        for item in tqdm(ipList):
            try:
                results=shodanAPI.search(item)
                sleep(1.2)
                if results['total']>0:
                    resultsList.append(results)
            except shodan.APIError as e:
                print('Error: {}'.format(e))
                print(".", end='')
        return resultsList.copy()