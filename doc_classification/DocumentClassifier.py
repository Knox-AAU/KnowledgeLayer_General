# from rdf import NJTripleExtractor, GFTripleExtractor
from utils import logging
from model.Document import Document, Article
from pre_processing import *
from environment import EnvironmentVariables as Ev

Ev()


class DocumentClassifier:
    """
    A module that classifies JSON data depending on the "type" attribute from the schema, and calls the
    appropriate pre-processing module (Currently, generator/app is used to identify Grundfos data).

    Ex. Data with type "Schema_Article" is classified as Nordjyske data and is passed to the NJPreProcessor for
    further pre-processing.
    """

    def __init__(self):
        self.nj_preprocessor = NJPreProcessor()
        self.gf_preprocessor = GFPreProcessor()
        # self.nj_triple_extractor = NJTripleExtractor(Ev.instance.get_value(Ev.instance.NJ_SPACY_MODEL))
        # self.gf_triple_extractor = GFTripleExtractor(Ev.instance.get_value(Ev.instance.GF_SPACY_MODEL))

    def classify(self, document_dict):
        """
        Constructs the intermediary Document object, then classifies the JSON data according to its data source and
        calls the appropriate word count pre-processor and triple extractor.

        :param document_dict: Dictionary containing document information
        :return: Document object containing document title, processed body, publisher, and path
        """

        # Construct Document object from document_dict
        publisher = document_dict["content"]["publisher"]
        document = Document(publisher)
        total_number_of_articles = len(document_dict["content"]["articles"])
        total_number_of_processed_articles = 0

        for article in document_dict["content"]["articles"]:
            title = article["headline"]
            logging.LogF.log(
                f"{int((total_number_of_processed_articles * 100) / total_number_of_articles)}% : Document Construction of {publisher} - {title}")
            # TODO: Why is extracted_from a list? Figure this out
            path = article["extracted_from"][0]
            body = ""

            for paragraph in article["paragraphs"]:
                body += ' ' + paragraph["value"]

            article = Article(title, body, path)
            document.articles.append(article)
            total_number_of_processed_articles += 1

        logging.LogF.log(f"100% : Document Construction of {publisher}")
        if document_dict["generator"]["app"] == "GrundfosManuals_Handler":
            logging.LogF.log(f"0% : GFPreProcessing of {document.publisher}")
            # self.gf_triple_extractor.process_publication(document)
            processed_document = self.gf_preprocessor.process(document)
        elif document_dict["type"] == "Publication":
            logging.LogF.log(f"0% : NJPreProcessing of {document.publisher}")
            # self.nj_triple_extractor.process_publication(document)
            processed_document = self.nj_preprocessor.process(document)
        else:
            raise Exception("Unable to classify document")

        return processed_document
