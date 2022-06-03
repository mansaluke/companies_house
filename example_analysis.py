import logging
import pandas as pd
from const import csv_path

# Set up logging
logging.basicConfig()
log = logging.getLogger('companies_house api')
log.setLevel(logging.INFO)


date_columns = ['date_of_creation', 'date_of_cessation']
search_results_df = pd.read_csv(csv_path, parse_dates=date_columns)

log.info(f'Number of companies: {len(search_results_df.index)}')


status_categories = search_results_df['company_status'].unique()
log.info(f'Possible company categories include: {status_categories.tolist()}')

active_companies = search_results_df[search_results_df['company_status']=="active"]
log.info(f'Number of active companies: {len(active_companies.index)}')

dissolved_companies = search_results_df[search_results_df['company_status']=="dissolved"]

days = (
    dissolved_companies['date_of_cessation'] - dissolved_companies['date_of_creation']
).dt.days.astype('Int64')

average_life = days.sum() / len(dissolved_companies.index)
log.info(f'Average life of companies: {average_life} days')

ltd_companies = search_results_df[search_results_df['company_type']=="ltd"]
first_ltd_date = ltd_companies['date_of_creation'].min()
log.info(f'First ltd creation date: {first_ltd_date}')
