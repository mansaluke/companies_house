import logging
import pandas as pd
from connect import Search, Connect
from secret import API_KEY
from const import csv_path

# Set up logging
logging.basicConfig()
log = logging.getLogger('companies_house api')
log.setLevel(logging.INFO)

# Download data
log.info('Initiate search class')
s = Search(Connect(API_KEY))
log.info('Searching companies')
search_results_df = pd.DataFrame(
    s.search_companies('tesco')  # page_limit=2)
  )

# View results
print(search_results_df.head())

# We convert date columns to datetime
date_columns = ['date_of_creation', 'date_of_cessation']
search_results_df[date_columns] = search_results_df[date_columns].apply(pd.to_datetime)

log.info('Saving to csv')
search_results_df.to_csv(csv_path)
