from __future__ import annotations
from abc import abstractmethod
from typing import List, Any, Tuple, NamedTuple

from model import Document, Article
from rdf.RdfConstants import RelationTypeConstants
from rdf.RdfCreator import generate_uri_reference, generate_relation, generate_literal, store_rdf_triples, return_rdf_triples
from utils import load_model
from .TripleExtractorEnum import TripleExtractorEnum
from environment import EnvironmentVariables as Ev
Ev()

class TripleExtractor:
    """
    The superclass that all triple extractors should inherit from. Specifies common functionality for all triple
    extractors.
    """
    def __init__(self, spacy_model, tuple_label_dict, ignore_label_list, namespace) -> None:
        """

        :param spacy_model: The name/path of the spaCy model to be used
        :param tuple_label_dict: ???
        :param ignore_label_list: ???
        :param namespace: The URI to be used
        """
        # PreProcessor.nlp = self.nlp
        self.graph_name = None
        self.nlp = load_model(spacy_model)
        self.namespace = namespace
        self.triples = []
        self.named_individual = []
        self.tuple_label_dict = tuple_label_dict
        self.ignore_label_list = ignore_label_list

    def process_publication(self, document: Document) -> List[Triple]:
        """
        Initiates all processing and triple extraction of the document.

        :param document: The document object to be processed
        """
        # Extract publication info and adds it to the RDF triples.
        self.extract_publication(document)
        self.extract_content(document)
        # Adds named individuals to the triples list.
        self._append_named_individual()
        # Function from rdf.RdfCreator, writes triples to file
        store_rdf_triples(self.triples, self.graph_name)

        return self.triples

    def clear_stored_triples(self):
        """
        Clears all triples in the triple list.
        """
        self.triples = []

    def return_ttl(self, document: Document) -> str:
        """
        Extracts triples from the input document and returns a stringified version of these.

        :param document: The document to extract triples from
        :return: A string representation of the triples extracted
        """

        # Extract publication info and adds it to the RDF triples.
        self.extract_publication(document)
        self.extract_content(document)
        # Adds named individuals to the triples list.
        self._append_named_individual()
        # Function from rdf.RdfCreator, writes triples to file
        return str(return_rdf_triples(self.triples))

    def _queue_named_individual(self, prop_1, prop_2) -> None:
        """
        Adds the named individuals to the named_individual list if it's not already in it.

        :param prop_1: Name
        :param prop_2: Label
        """
        if [prop_1, prop_2] not in self.named_individual:
            self.named_individual.append([prop_1, prop_2])

    def extract_publication(self, document: Document) -> None:
        """

        :param document:
        :return:
        """
        if document.publication is not None:
            
            # Formatted name of a publisher and publication
            publication_formatted = document.publication.replace(" ", "_")
            publisher_formatted = document.publisher.replace(" ", "_")

            # Adds publication as a named individual
            self._queue_named_individual(publication_formatted, TripleExtractorEnum.PUBLICATION)
            # Add publication name as data property
            self._append_triples_literal([TripleExtractorEnum.PUBLICATION], publication_formatted,
                                          RelationTypeConstants.KNOX_NAME, document.publication)

            # Add publisher name as data property
            self._append_triples_literal([TripleExtractorEnum.PUBLISHER], publisher_formatted,
                                          RelationTypeConstants.KNOX_NAME, publisher_formatted)
            # Add the "Publisher publishes Publication" relation
            self._append_triples_uri([TripleExtractorEnum.PUBLISHER], publisher_formatted,
                                      [TripleExtractorEnum.PUBLICATION], publication_formatted,
                                      RelationTypeConstants.KNOX_PUBLISHES)

    def _convert_spacy_label_to_namespace(self, string: str) -> str:
        """

        :param string: A string matching a spacy label
        :return: A string matching a class in the ontology.
        """
        for label in self.tuple_label_dict:
            # Assumes that tuple_label_list is a list of dicts with the format: {"spacy_label": xxx, "target_label": xxx}
            if string == str(label['spacy_label']):
                # return the chosen name for the spaCy label
                return str(label['namespace'])
        else:
            return string

    def _append_token(self, article: Article, pair: Tuple[str, str]):
        """

        :param article:
        :param pair:
        """
        # Ensure formatting of the objects name is compatible, eg. Jens Jensen -> Jens_Jensen
        object_ref, object_label = pair
        object_ref = object_ref.replace(" ", "_")
        object_label = self._convert_spacy_label_to_namespace(object_label)

        # Each entity in article added to the "Article mentions Entity" triples
        _object = generate_uri_reference(self.namespace, [object_label], object_ref)
        _subject = generate_uri_reference(self.namespace, [TripleExtractorEnum.ARTICLE], article.id)
        relation = generate_relation(RelationTypeConstants.KNOX_MENTIONS)
        self.triples.append(Triple(_subject, relation, _object))
        # Each entity given the name data property
        self.triples.append(
            Triple(_object, generate_relation(RelationTypeConstants.KNOX_NAME), generate_literal(pair[0])))

    def _append_triples_literal(self, uri_types: List[str], uri_value: Any, relation_type: str, literal: str):
        """

        :param uri_types:
        :param uri_value:
        :param relation_type:
        :param literal:
        """
        self.triples.append(Triple(
            generate_uri_reference(self.namespace, uri_types, uri_value),
            generate_relation(relation_type),
            generate_literal(literal)
        ))

    def _append_triples_uri(self, uri_types1: List[str], uri_value1: Any,
                            uri_types2: List[str], uri_value2: Any, relation_type: str):
        """

        :param uri_types1:
        :param uri_value1:
        :param uri_types2:
        :param uri_value2:
        :param relation_type:
        """
        self.triples.append(Triple(
            generate_uri_reference(self.namespace, uri_types1, uri_value1),
            generate_relation(relation_type),
            generate_uri_reference(self.namespace, uri_types2, uri_value2),
        ))

    def _append_named_individual(self) -> None:
        """
        Appends each named individual to the triples list.
        """

        # prop1 = The specific location/person/organisation or so on
        # prop2 = The type of Knox:Class prop1 is a member of.
        for prop1, prop2 in self.named_individual:
            self.triples.append(Triple(
                generate_uri_reference(self.namespace, [prop2], prop1),
                generate_relation(RelationTypeConstants.RDF_TYPE),
                generate_relation(RelationTypeConstants.OWL_NAMED_INDIVIDUAL)
            ))

            self.triples.append(Triple(
                generate_uri_reference(self.namespace, [prop2], prop1),
                generate_relation(RelationTypeConstants.RDF_TYPE),
                generate_uri_reference(self.namespace, ref=prop2)
            ))

    @abstractmethod
    def extract_content(self, document: Document):
        pass


class Triple(NamedTuple):
    subject: str
    relation: str
    object: str
