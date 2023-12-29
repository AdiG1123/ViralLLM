import requests
import logging
import os
from dotenv import load_dotenv
from xml.etree import ElementTree

load_dotenv()

logging.basicConfig(filename="logs.log", filemode='w', format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = r"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/eutils.ncbi.nlm.nih.gov/entrez/eutils/"
ESEARCH_URL = f"{BASE_URL}esearch.fcgi"
EFETCH_URL = f"{BASE_URL}efetch.fcgi"
DATABASES = ["pmc"]
API_KEY = os.getenv("API_KEY")

class ESearchAPI:
    
    def __init__(self, db: str):
        """
        Initialize the EsearchAPI
        """
        try:
            self.api_key = API_KEY
        except:
            logger.info("No API Key Found")
        
        if db not in DATABASES:
            raise Exception("Invalid database name. Can only be 'pmc' or 'pubmed'")
        else:
            self.db = db 
        self.term = str()
    
    def _set_search_term(self, search_terms: dict):
        """
        Creates Search term for api
        """
        self.term = str()

        # The pcm database needs to specify open access journals
        if self.db == "pmc":
            self.term = '"open access"[filter]'

        
        for k, v in search_terms.items():
            if v:
                self.term = self.term + f' AND "{v}"[{k}]' 
        
    
    def _get_response(self, url=ESEARCH_URL):
        """
        Calls API with parameters
        """
        
        params = {
            "db" : self.db,
            "term" : self.term,
            "api_key" : self.api_key,
            "retmode": "json",
            "retmax": 10000,
            "usehistory" : "y"
        }
        
        res = requests.get(url=url, params=params)

        return res.json()
    
   
    def get_webenv_info(self, search_terms: dict):
        """
        Get the list of article Ids returned from the API
        """
        
        logger.info("Started Esearch")
        
        self._set_search_term(search_terms=search_terms)
        response = self._get_response()
        ret = {
            "db" : self.db,
            "count": response['esearchresult']['count'],
            "querykey": response['esearchresult']['querykey'],
            "webenv" : response['esearchresult']['webenv']
                }
        
        logger.info(ret)
        logger.info("Esearch Complete")
       
        return ret


class EFetchAPI:
    
    def __init__(self):
        """
        Initialize the EFetchAPI
        """
        try:
            self.api_key = API_KEY
        except:
            logger.info("No API Key Found")
        
        # the max amount of entries acquired in single api call
        # All params are inputted as strings
        self.retmax = "10"
        self.retmax_int = int(self.retmax)
        
        self.db = str()
        self.webenv = str()
        self.query_key = str()
        
        self.usehistory = 'y'
        
        # the count is the total ids from the Esearch
        self.count = 0
        
    def _parse_webenv(self, webenv_info: dict):
        try:
            self.db= webenv_info['db']
            self.webenv = webenv_info['webenv']
            self.query_key = webenv_info['querykey']
            self.count = int(webenv_info['count'])
        except:
            raise Exception("Invalid web env input. Need keys 'webenv' and 'querykey'")
    
    def _get_response(self, retstart: str, url=EFETCH_URL):
        """
        Calls API with parameters
        """
        
        
        params = {
            "db" : self.db,
            "api_key" : self.api_key,
            "retmax" : self.retmax,
            "retstart" : retstart,
            "WebEnv" : self.webenv,
            "query_key" : self.query_key,
            "usehistory" : self.usehistory
            }
        
        res = requests.get(url=url, params=params)
        logger.info(res.status_code)
        tree_element = ElementTree.fromstring(res.text)
        
        pmc_id = tree_element.find('.//article-id[@pub-id-type="pmc"]').text
        logger.info(f"{params}: PMC ID: {pmc_id}")
        
        return tree_element
    
    def get_xml(self, webenv_info: dict):
        """
        Get the list of article Ids returned from the API
        """
        
        logger.info("Starting efetch")
        
        self._parse_webenv(webenv_info=webenv_info)
        
        # parse the string params as ints for range
    
        for i in range(0, self.count, self.retmax_int):
            response = self._get_response(retstart=str(i))
            logger.info(f"{i}: {response.find('.//article-id[@pub-id-type="pmc"]').text}")
            # responses.append(response)
            yield response
        logger.info("Efetch complete")

        # return responses