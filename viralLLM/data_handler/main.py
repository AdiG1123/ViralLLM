from data_ingestion import ESearchAPI, EFetchAPI
from xml.etree import ElementTree

def write_binary_to_file(file_type: str, file_name: str, file_string: str):
    with open(f"{file_name}.{file_type}", "wb") as f:
        f.write(file_string)

if __name__ == "__main__":
    
    search_terms = {
        "abstract" : "measles"
    }
    
    # esearch_pubmed = ESearchAPI(db="pubmed")
    esearch_pmc = ESearchAPI(db="pmc")

    # response_pubmed = esearch_pubmed.get_id_list(search_terms=search_terms)
    response_pmc = esearch_pmc.get_webenv_info(search_terms=search_terms)

    efetch = EFetchAPI()

    for x in efetch.get_xml(webenv_info=response_pmc):
        
        print(x)
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

            print(f'Article {index} saved to {new_file_path}')