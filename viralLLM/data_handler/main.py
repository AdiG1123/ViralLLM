from data_ingestion import ESearchAPI, EFetchAPI


if __name__ == "__main__":
    
    search_terms = {
        "title" : "Measles",
        "abstract" : "Protein"
    }
    
    # esearch_pubmed = ESearchAPI(db="pubmed")
    esearch_pmc = ESearchAPI(db="pmc")

    # response_pubmed = esearch_pubmed.get_id_list(search_terms=search_terms)
    response_pmc = esearch_pmc.get_webenv_info(search_terms=search_terms)
    
    efetch = EFetchAPI()
    for x in efetch.get_xml(webenv_info=response_pmc):
        print(x)
    