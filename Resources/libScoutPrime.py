# this is a wrapper library for the Scout Prime API, just so it matches the rest of the methods in the script
from pprint import pprint
from Resources.ScoutPrime import scoutprime

class ScoutPrime_Query:
    def __init__(self, lookout_config):
        self.scout_api_token=lookout_config['scout_api_token']
        self.scout_server=lookout_config['scout_server']
        self.scout_query_url=lookout_config['scout_query_url']
        self.scout_outputFolder = lookout_config['lookout_default_outputFolder']
        self.sp = scoutprime.ScoutPrime(config=lookout_config['scout_config_file'], debug=True)

    def QueryIPs(self, ipList):
        sp_master_results={}
        # scout prime takes in an array of IP addresses, so we need to iterate through the dictionary to get the array
        # of IP's from each file
        #for item in ipList:

        list_of_elements = ipList.copy()
        if list_of_elements:
            list_of_elements = str(list_of_elements)
            list_of_elements = list_of_elements.replace('\'', r'"')
            self.sp.sp_query = self.sp.ne_query
            self.sp.sp_query = self.sp.sp_query.replace("_network_elements_data_", list_of_elements)

        try:
            sp_results = self.sp.submit_graph_query(minutes=2000000)
            sp_results=self.processResults(sp_results['results'])
            # pprint (sp_results)
            # sp_master_results=sp_results.copy()
            # sp_master_results=self.processResults(sp_results)
            # print ("--::",sp_master_results)
            return sp_results

        except Exception as e:
            msg = "The following error occurred: {}".format(e)
            print(msg)
            #self.buildReport(sp_master_results)
        # finally:
        #    print ("::-::",sp_master_results)
        #    return sp_master_results

    def processResults(self, sp_results):
        indicatorDict = {}

        for item in sp_results:
            #pprint (item)
            indicator_Name=item['left']['name']
            indicator_Sources = item['left']['threatNames']
            indicator_TIC = item['left']['ticScore']
            indicator_ScoutRefID = item['ref']['left']['id']
            indicator_Classifciations=item['right']['classifications']
            indicator_Provider=item['sources']

            if indicator_Classifciations=="":
                indicator_Classifciations=None
            indicatorData={"provider": indicator_Provider, "ticScore": indicator_TIC, "scout_ref_ID": indicator_ScoutRefID,"classification":indicator_Classifciations, "sources": indicator_Sources}
            indicatorDict[indicator_Name]=indicatorData.copy()
            indicatorData.clear()

        return indicatorDict

    def buildReport(self, dataDict):
        print ("building scout prime report")
        provider=""
        sources=""
        strHeaderToWrite=('file'+','+'indicator'+','+'provider'+','+ 'ticScore'+',''scout_ref_ID'+','+ 'classification'+','+'sources'+'\n')
        for file in dataDict:
            print ("Scout Prime:", file)
            strFileNameAndPath=self.scout_outputFolder+"/"+file
            strFileNameAndPath=strFileNameAndPath.replace(".txt","_scoutPrime_results.csv")
            fileWriter=open(strFileNameAndPath,"w")
            fileWriter.write(strHeaderToWrite)
            for ipItem in dataDict[file]:
                #print ("    ", ipItem, ":", dataDict[file][ipItem])
                provider=','.join(dataDict[file][ipItem]['provider'])
                #print ("    -",provider)
                sources=','.join(dataDict[file][ipItem]['sources'])
                #print ("    -", sources)
                classification=','.join(dataDict[file][ipItem]['classification'])
                strLineToWrite=(file+','+ipItem+','+provider+','+ str(dataDict[file][ipItem]['ticScore'])+','+str(dataDict[file][ipItem]['scout_ref_ID'])+',"'+ classification+'","'+sources+'"\n')
                fileWriter.write(strLineToWrite)
                #print (strLineToWrite)
            fileWriter.close()
