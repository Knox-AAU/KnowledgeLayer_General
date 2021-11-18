import dataclasses
import json
from typing import List

import requests

from data_access.data_transfer_objects.DocumentWordCountDto import DocumentWordCountDto
from environment import EnvironmentVariables as Ev
from requests.exceptions import ConnectionError
import logging

# logging.basicConfig(
#     format='%(asctime) | %(message)',
#     datefmt='%Y %m %d @ %H:%M:%S'
# )

logger = logging.getLogger()

class WordCountDao:
    """

    """

    @staticmethod
    def send_word_count(documentWordCounts: List[DocumentWordCountDto]):
        """

        :param documentWordCounts:
        :return:
        """
        objects_as_dict = list(map(lambda x: dataclasses.asdict(x), documentWordCounts))
        url = Ev.instance.get_value(Ev.instance.WORD_COUNT_DATA_ENDPOINT)

        try:
            res = requests.post(url, json=objects_as_dict)
            res.raise_for_status()
            logger.warning(str(res) + ": " + str(res.text))
        except ConnectionError as error:
            logger.warning("Connection error: " + str(error))
            raise error
        except Exception as error:
            logger.warning("Something unexpected happened: " + str(error))
            logger.warning("Error type: " + str(type(error)))
            raise error

        return True
    
