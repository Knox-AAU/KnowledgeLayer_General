import datetime
import logging
import os
import uuid

import da_core_news_sm

import spacy
from environment import EnvironmentVariables as Ev

from pre_processing import PreProcessor
from publication_generator import PublicationGenerator
from performace_test_suite import PerformanceTestCase
Ev()
logger = logging.getLogger()
##nlp = spacy.load("da_core_news_sm")
Lemma = da_core_news_sm.load()

def Lemmatization(string):
    doc = Lemma(string.lower())
    return " ".join([token.lemma_ for token in doc])

def run_tests():
    numbWordcount = 1000
    numbIterations = 10

    generator = PublicationGenerator("NJ")
    generator.repeat_amount = numbIterations
    generator.stop_word_density = 0
    generator.paragraph_word_count = numbWordcount
    preprocessor = PreProcessor()


    while numbWordcount <= 10000:
        generator.paragraph_word_count = numbWordcount
        argList = []

        #generate list
        for i in range(numbIterations):
            argList.append([generator.generate_paragraph()['value']])

        suite = PerformanceTestCase(Lemmatization, argList)

        path = os.path.join(Ev.instance.get_value(Ev.instance.PERFORMANCE_OUTPUT_FOLDER),
                            f"test_lemma_internal_{uuid.uuid4()}.csv")
        with open(path, 'a') as f:
            f.write(str(numbWordcount) + ", " + str(suite.run()).replace("[", "").replace("]", "") + "\n")

        numbWordcount += 1000


if __name__ == "__main__":
    run_tests()