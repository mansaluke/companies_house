from typing import Dict, List
import logging

from .base import Connector

logger = logging.getLogger('companies_house api')

def create_http_request_string(search_term,
                                **kwargs) -> str:
    """
    Create http request string for url
    """
    http_request = search_term
    for key, val in kwargs.items():
        http_request += f'&{key}={val}'
    return http_request


class Search:
    """
    Runs Connector class passing in http request strings
    """
    def __init__(self, connect: Connector):

        self.con: Connector = connect
        self.response_json: Dict = {}

    def _search_companies(self,
                          search_term: str,
                          **kwargs) -> List[dict]:
        """
        Searches single page and returns as json
        """
        self.response_json = self.con.run(
            create_http_request_string(search_term, **kwargs)
        )
        return self.response_json

    def search_companies(self,
                         search_term: str,
                         search_string: str='search/companies?q=',
                         items_per_page: int=100,
                         start_page: int=0,
                         page_limit: int=999) -> List:
        """
        Loops through max number of pages for all results
        """
        response = []
        for page in range(start_page, page_limit):
            print(page)
            logger.debug(f'Page number: {page}')

            resp = self._search_companies(
                search_string + search_term,
                items_per_page=items_per_page,
                start_index=page
            )
            response.extend(resp['items'])
            num_items = len(resp['items'])
            no_items = num_items==0
            logger.debug(f'Number of companies in page: {num_items}')
            if no_items:
                break
            if page == page_limit and not num_items:
                logger.warning('Last page reached. Likely more results available')
        return response
