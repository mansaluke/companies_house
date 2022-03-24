from typing import Any, AnyStr, Optional
import logging
import pandas as pd

from .base import Connect

logger = logging.getLogger('companies_house api')

class Search(Connect):
    """
    Class used to communicate requests with Connect
    """
    def __init__(self,
                 api_key: AnyStr):
        super().__init__(api_key)

        self.response_json: Any = ''
        self.response_df: pd.DataFrame = self.update_df()

    @staticmethod
    def _create_http_request_string(search_term,
                                    **kwargs) -> AnyStr:
        """
        Create http request string for url
        """
        http_request = search_term
        for key, val in kwargs.items():
            http_request += f'&{key}={val}'
        return http_request

    def update_df(self, update_dict: Optional[dict]=None) -> pd.DataFrame:
        """
        Updates dataframe with dictionary and creates it if not exists
        """
        if hasattr(self, 'response_df'):
            return self.response_df.append(update_dict, ignore_index=True)
        return pd.DataFrame()

    def _search_companies(self,
                          search_term,
                          **kwargs) -> dict:
        """
        Searches single page and returns as json
        """
        self.response_json = self.exec(
            self._create_http_request_string(search_term, **kwargs)
        )
        return self.response_json

    def search_companies(self,
                         search_term,
                         items_per_page=100,
                         start_page=0,
                         page_limit=999) -> pd.DataFrame:
        """
        Loops through max number of pages for all results
        """
        for page in range(start_page, page_limit):
            logger.debug(f'Page number: {page}')

            resp = self._search_companies(
                search_term,
                items_per_page=items_per_page,
                start_index=page
            )
            self.response_df = self.update_df(resp['items'])
            num_items = len(resp['items'])
            no_items = num_items==0
            logger.debug(f'Number of companies in page: {num_items}')
            if no_items:
                break
            if page == page_limit and not num_items:
                logger.warning('Last page reached. Likely more results available')
        return self.response_df
