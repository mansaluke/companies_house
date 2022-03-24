from typing import AnyStr
import logging
import datetime
import time
import requests


logger = logging.getLogger('companies_house api')

class TooManyRequests(Exception):
    pass

class Unauthorized(Exception):
    pass

class Connect():
    """
    Base clase connecting to api with requests session
    "https://api.companieshouse.gov.uk/search/companies"
    """

    http_exceptions = {
        401: Unauthorized,
        429: TooManyRequests,
        416: TooManyRequests
    }

    def __init__(self,
                 api_key: AnyStr):
        self.base_uri: AnyStr = "https://api.company-information.service.gov.uk/search/companies?q="
        self.session = requests.Session()
        self.session.auth = (api_key, '')

        self.response: requests.Response  = ''
        self.number_of_requests = 0
        self.first_request_time = None
        self.time_limit = 300

    def check_status(self):
        """
        Checks connection status of latest request
        """
        status_code = self.response.status_code
        if status_code == 200:
            logger.debug('Connection successful')

        if status_code != 200:
            error_message = f'Error: {self.response}'
            if status_code in self.http_exceptions:
                error_message += f' - {self.http_exceptions[status_code]}'
                logger.error(error_message)
                raise self.http_exceptions[status_code]

            logger.error(error_message)
            raise Exception (error_message)

    def _get_url(self,
                 http_request: AnyStr) -> requests.Response:
        """
        Executes get request
        """
        while True:
            try:
                url = self.base_uri + http_request
                self._rate_limiter()
                logger.debug(f'GET {url}')
                self.response = self.session.get(url)
                self.check_status()
                return self.response
            except TooManyRequests:
                logger.info('Reached request limit - Retrying in 60 seconds. Please wait.')
                time.sleep(60)
                self.reset_rate_limiter()

    def reset_rate_limiter(self):
        self.number_of_requests = 0
        self.first_request_time = None

    def _rate_limiter(self):
        """
        We need to implement the rate limits imposed by the API
        See more here: https://developer.company-information.service.gov.uk/developer-guidelines

        You can make up to 600 requests within a 5 minute period
        """
        self.number_of_requests += 1
        if self.number_of_requests==1:
            self.first_request_time = datetime.datetime.now()

        if self.number_of_requests==600:
            current_time = datetime.datetime.now()
            time_difference = (
                current_time - self.first_request_time
            ).total_seconds()
            wait_time = max(
                self.time_limit - time_difference, 0)
            logger.info(f'Number of requests reached limit. Waiting {wait_time//60} minutes')
            time.sleep(wait_time)

    def exec(self,
             http_request: str) -> dict:
        """
        Function used execute get request
        """
        self._get_url(http_request)
        return self.response.json()
