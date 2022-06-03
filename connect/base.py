from abc import ABC, abstractmethod
import logging
from typing import Dict
import requests
from connect.exceptions import Unauthorized, TooManyRequests
from connect.rate_limiter import Throttler


logger = logging.getLogger('companies_house api')


class Connector(ABC):
    @abstractmethod
    def check_connection(self):
        pass

    @abstractmethod
    def run(self) -> Dict:
        pass


class Connect():
    """
    Base clase connecting to companies house rest api
    """

    http_exceptions = {
        401: Unauthorized,
        429: TooManyRequests,
        416: TooManyRequests
    }

    base_uri = "https://api.company-information.service.gov.uk/"

    def __init__(self,
                 api_key: str):
        self.session = requests.Session()
        self.session.auth = (api_key, '')

        self.response: requests.Response  = ''
        self.number_of_requests = 0
        self.first_request_time = None
        self.time_limit = 300

    def check_connection(self):
        self.get_url('status')

    def check_response_status(self):
        """
        Checks connection status of latest request
        """
        status_code = self.response.status_code
        if status_code == 200:
            logger.debug('Connection successful')
            return None

        error_message = f'Error: {self.response}'
        if status_code in self.http_exceptions:
            error_message += f' - {self.http_exceptions[status_code]}'
            logger.error(error_message)
            raise self.http_exceptions[status_code]()

        logger.error(error_message)
        raise Exception(error_message)

    @Throttler()
    def get_url(self,
                http_request_string: str) -> requests.Response:
        """
        Executes get request
        """
        url = self.base_uri + http_request_string
        logger.debug(f'GET {url}')
        self.response = self.session.get(url)
        self.check_response_status()
        return self.response

    def run(self,
             http_request_string: str) -> Dict:
        """
        Function used execute get request
        """
        self.get_url(http_request_string)
        return self.response.json()
