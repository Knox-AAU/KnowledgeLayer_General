import spacy
from utils import logging
import re
from pre_processing.PreProcessor import PreProcessor


class GFPreProcessor(PreProcessor):
    """

    """

    def __init__(self, model):
        self.nlp = spacy.load(model)

    def process(self, document):
        """

        :return:
        """

        total_number_of_articles = len(document.articles)
        total_number_of_processed_articles = 0

        for article in document.articles:
            logging.LogF.log(
                f"GFPreprocces {document.publisher} - {article.title} - {int((total_number_of_processed_articles * 100) / total_number_of_articles)}%")
            # TODO: Decide what to do with emails, links, etc. in corpus
            text = self.__process_text__(document, article.title)
            article.title = text
            text = self.__process_text__(document, article.body)
            article.body = text
            total_number_of_processed_articles += 1

        logging.LogF.log(f"GFPreprocces {document.publisher} - 100%")

        return document

    def __process_text__(self, document, text: str):
        corpus = self.remove_special_characters(text)
        corpus = self.numbers_to_text(corpus)
        logging.LogF.log(
            f"GFLemmatize {document.publisher}")
        corpus = super().lemmatize(corpus, "en")
        logging.LogF.log(
            f"GFLemmatize {document.publisher}")
        return self.to_lower(corpus)

    def bigrams(self, sentence: str) -> str:
        # This is an experiment! Can be the basis for greatness later on

        # self.nlp.add_pipe("merge_noun_chunks")
        #
        # doc = self.nlp(corpus)
        # print("spaCy text: " + doc.text)
        # for chunk in list(doc.noun_chunks):
        #     print(chunk)
        #
        # for token in doc:
        #     print(token.text + ", " + token.pos_)
        return True

    def to_lower(self, words):
        """

        :param words:
        :return:
        """
        return words.lower()

    def remove_special_characters(self, txt):
        """

        :param txt:
        :return:
        """
        cleaned_text = re.sub("[^a-zA-Z0-9 ]", '', txt)
        return cleaned_text

    # TODO: Consider researching string builders for this
    def numbers_to_text(self, text):
        """

        :param text:
        :return:
        """
        numbers = {
            '0': 'zero',
            '1': 'one',
            '2': 'two',
            '3': 'three',
            '4': 'four',
            '5': 'five',
            '6': 'six',
            '7': 'seven',
            '8': 'eight',
            '9': 'nine'
        }

        result = ""
        just_seen_digit = False

        for character in text:
            if character.isnumeric():
                if just_seen_digit:
                    result += "_"
                result += numbers[character]
                just_seen_digit = True
            else:
                result += character
                just_seen_digit = False

        return result.strip()

#    def insert_pump_name(self, data, pump_name):
#        data = data.replace("the_pump", pump_name)
#        return data
