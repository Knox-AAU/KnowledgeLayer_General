import urllib.parse

from typing import List, Tuple

import requests
from rdflib import Graph, Literal, BNode
from rdflib.namespace import NamespaceManager, RDFS, OWL, XSD, RDF
from environment.EnvironmentConstants import EnvironmentVariables as ev
from requests.exceptions import ConnectionError
from rdflib.namespace import ClosedNamespace
from rdflib import URIRef
from environment.EnvironmentConstants import EnvironmentVariables as Ev
from utils import logging

Ev()


def store_rdf_triples(rdf_triples: List[Tuple], graph_name: str):
    """
    Input:
        rdfTriples: list of RDF triples with correct type - List containing triples on the form (Subject, RelationPredicate, Object).
        output_file_name: str - The Name of the outputted file
    
    Takes in a list of RDF triples and parse them into a ready RDF format.
    The format and output folder of the files are dependent of the configation of the .env file
    
    """

    # Get the "graph" in order to contain the rdfTriples
    # Switch the bad namespacemanager with the good one which do not create prefix'es
    graph: Graph = Graph()
    name_space_manager = KnoxNameSpaceManager(graph)
    graph.namespace_manager = name_space_manager

    for sub, rel, obj in rdf_triples:
        graph.add((sub, rel, obj))
        logging.LogF.log(f'sub: {urllib.parse.unquote(sub)}, rel: {urllib.parse.unquote(rel)}, obj: {urllib.parse.unquote(obj)}')

    serialized_graph = graph.serialize(format='turtle', encoding="utf-8")
    # with open(path, 'wb') as f:
    #     f.write(serialized_graph)
    payload = dict(graph=graph_name, turtle=serialized_graph)
    success = requests.post(ev.instance.get_value(ev.instance.TRIPLE_DATA_ENDPOINT),
                            data=payload, headers={}, files=[])
    if not success:
        logging.LogF.log(f'ERROR: Unable to send file to database')
        raise ConnectionError('Unable to post to the database')
    logging.LogF.log(f'Successfully sent publication to server')


def return_rdf_triples(rdfTriples):
    """
    Converts triples to RDF Turtle representation.

    :param rdfTriples: The triples to be converted to Turtle
    :return: The triples following RDF Turtle format
    """

    # Get the "graph" in order to contain the rdfTriples
    # Switch the bad namespacemanager with the good one which do not create prefix'es
    graph: Graph = Graph()
    name_space_manager = KnoxNameSpaceManager(graph)
    graph.namespace_manager = name_space_manager

    for sub, rel, obj in rdfTriples:
        graph.add((sub, rel, obj))
        logging.LogF.log(
            f'sub: {urllib.parse.unquote(sub)}, rel: {urllib.parse.unquote(rel)}, obj: {urllib.parse.unquote(obj)}')

    return graph.serialize(format='turtle').decode("utf-8").replace("<", "&lt;").replace(">", "&gt;")


def generate_blank_node():
    """
    Returns:
        A new instance of RDF class BNode (blank node)

    Creates a blank node for the RDF graph.
    The blank node represents a resource where the URI or Literal is unknown or hasn't been given.
    By the RDF standard a blank node can only be used as the subject or object in an RDF triple.
    """
    return BNode()


def generate_literal(value):
    """
    Input:
        value: A Python primitive type - The value to be associated with the resulting RDF Literal Node for the graph
    Returns:
        A new instance of RDF class Literal, with literal value and type based on value:
    
    Takes in a value and creates a RDF Literal instance containing the value and associated type.
    """
    return Literal(value)


def generate_uri_reference(namespace, sub_uri_list=[], ref=""):
    """
    Input:
        namespace: str - The base namespace for the resource URL
        sub_uri_list: list - A sorted list of sub uri's from the namespace, used navigating to the correct resource
        ref: str - The resource reference
    Returns:
        An instance of the RDF URIRef class, containing the combined URL for the specified resource
    
    Generates an URI reference to a RDF resource.

    Example of usage:
    To generate the URL resource: http://example.org/person/important/localhero/BobTheMan  
    The following values should be used:  
        namespace: http://example.org/  
        sub_uri_list: ["person", "important", "localhero"]  
        ref: "BobTheMan"  
    """
    reference_str = namespace

    for sub_uri in sub_uri_list:
        reference_str += urllib.parse.quote(sub_uri) + "/"

    reference_str += urllib.parse.quote(ref.replace("/", "-"))
    return URIRef(reference_str)


def generate_relation(relationTypeConstant):
    """
    Input:
        relationTypeConstants - str - A string formatted in the form of <type>:<name> used in RdfConstants
    Returns:
        A relation predicate for the correct type as specified in relationTypeConstants:
    Raises:
        Exception - If <relationTypeConstant> has not been defined in the function
    """
    relType, relValue = relationTypeConstant.split(":")
    if relType == "rdf":
        return RDF.term(relValue)
    elif relType == "rdfs":
        return RDFS.term(relValue)
    elif relType == "owl":
        return OWL.term(relValue)
    elif relType == "xsd":
        return XSD.term(relValue)
    elif relType == "knox":
        return KNOX.term(relValue)
    else:
        raise Exception(
            "Relation namespace: " + relType + " not defined in RdfConstants. Input was: " + relationTypeConstant)


def __calculateFileExtention__(format):
    """
    Inputs:
        format: str - The format in which the file generated by the RDF triples are to be saved
    Returns:
        str - The file extension associated with the format. "" (empty string) if a matching format could not be found
    
    Calculates the file extension for the given format
    """
    switch = {
        "turtle": ".ttl",
        "html": ".html",
        "hturtle": ".ttl",
        "mdata": ".IVD",
        "microdata": ".IVD",
        "n3": ".n3",
        "nquads": ".nq",
        "nt": ".nt",
        "rdfa": ".xml",
        "rdfa1.0": ".xml",
        "rdfa1.1": ".xml",
        "trix": ".xml",
        "xml": ".xml"}

    return switch.get(format, "")



KNOX = ClosedNamespace(
    uri=URIRef(Ev.instance.get_value(Ev.instance.ONTOLOGY_NAMESPACE)),
    terms=[
        "isPublishedBy", "mentions", "isPublishedOn", "publishes", "Email", "DateMention", "Link",
        "Name", "PublicationDay", "PublicationMonth", "PublicationYear", "ArticleTitle", "isWrittenBy", "PumpRelates"]
)


class KnoxNameSpaceManager(NamespaceManager):
    """
    An override of rdflib built-in NamespaceManager.
    This is used in order to escape the default prefix'es being added to the output
    """

    def __init__(self, graph):
        self.graph = graph
        self.__cache = {}
        self.__cache_strict = {}
        self.__log = None
        self.__strie = {}
        self.__trie = {}
        for p, n in self.namespaces():  # self.bind is not always called
            super().insert_trie(self.__trie, str(n))
