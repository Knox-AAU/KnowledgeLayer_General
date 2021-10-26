import requests
from knox_source_data_io.models.publication import Paragraph, Publication
import exceptions
from environment import EnvironmentVariables as Ev


class PreProcessor:
    """

    """
    def lemmatize(self, content: str, language: str) -> str:
        """
        Post's to the lemmatizer API defined in the environment (Ev)
        :param content: str - The content to be lemmatized
        :return: str - The lemmatized content
        """
        try:
            endpoint: str = Ev.instance.get_value(Ev.instance.LEMMATIZER_ENDPOINT)
            response: requests.Response = requests.post(endpoint, f'{{"language":{language}, "string":"{content}"}}')
        except (requests.exceptions.ConnectionError, requests.exceptions.ConnectTimeout) as e:
            raise exceptions.PostFailedException("ERROR: Error contacting Lemmatize API", e.response)
        except:
            raise exceptions.UnparsableException("ERROR: Unparseable by Lemmatize API")
        return response.json()

    def extract_all_text_from_paragraphs(self, data):
        """

        :param data:
        :return:
        """
        corpus = ""

        for article in data["content"]["articles"]:
            for paragraph in article["paragraphs"]:
                corpus += paragraph["value"] + " "

        return corpus

    def process(self, json_data):
        print("Not overridden")
