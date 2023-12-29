from data_ingestion import ESearchAPI, EFetchAPI
from xml.etree import ElementTree
import logging
import os

logger = logging.getLogger(__name__)

def ingest(search_terms: dict, db: str):
    # Esearch component
    esearch_pmc = ESearchAPI(db=db)

    response_pmc = esearch_pmc.get_webenv_info(search_terms=search_terms)

    # Efetch component
    efetch = EFetchAPI()

    for x in efetch.get_xml(webenv_info=response_pmc):
        
        # find all articles
        articles = x.findall('.//article')
        
        for index, article_element in enumerate(articles, start=1):

            # Get the root for the new XML Doc
            new_root = ElementTree.Element('pmc-articleset')
            new_root.append(article_element)
            
            # get the pmc id
            pmc_id_element = article_element.find('.//article-id[@pub-id-type="pmc"]')
            pmc_id = pmc_id_element.text if pmc_id_element is not None else f'unknown_pmc_id_{index}'

            # Create a new XML tree
            new_tree = ElementTree.ElementTree(new_root)

            # Write the new XML document to a file
            new_file_path = f'database/{pmc_id}.xml'
            new_tree.write(new_file_path, encoding='utf-8', xml_declaration=True)

            logger.info(f'Article {index} saved to {new_file_path}')


if __name__ == "__main__":
    
    # Change these search terms to download data with that keyword
    search_terms = {
        "abstract" : "P protein",
        "title" : "Measles"
    }
    
    if not os.path.exists(os.path.join(os.getcwd(), "database")):
        os.mkdir(os.path.join(os.getcwd(), "database"))
        
    ingest(search_terms=search_terms, db="pmc")
    
    
    