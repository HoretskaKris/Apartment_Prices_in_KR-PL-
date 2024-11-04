import logging
import os
import re
from datetime import datetime
from typing import Dict, List

import pandas as pd

log_directory: str = r'./logs'
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_directory, 'data_split.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)


def check_folder_exists(folder_path: str) -> None:
    '''Check if folder exists'''
    if not os.path.exists(folder_path):
        logging.error(f'Folder {folder_path} does not exist')
        raise FileNotFoundError(f'Folder {folder_path} does not exist')


def get_csv_files(folder_path: str) -> List[str]:
    '''Get list of CSV files in folder'''
    files = os.listdir(folder_path)
    csv_files = [os.path.join(folder_path, file)
                 for file in files if file.endswith('.csv')]
    return csv_files


def split_files_by_category(csv_files: List[str]) -> Dict[str, List[str]]:
    '''Split files into rent and sale categories'''
    rent_files = [file for file in csv_files if 'rent' in file]
    sale_files = [file for file in csv_files if 'rent' not in file]
    return {'rent': rent_files, 'sale': sale_files}


def load_csv_files_by_year(file_paths: List[str]) -> Dict[str, pd.DataFrame]:
    '''Load CSV files by year'''
    data_by_year = {}
    year_pattern = re.compile(r'(\d{4})')

    for file_path in file_paths:
        try:
            match = year_pattern.search(file_path)
            if match:
                year = match.group(1)
                temp_df = pd.read_csv(file_path)
                if year not in data_by_year:
                    data_by_year[year] = pd.DataFrame()
                data_by_year[year] = pd.concat(
                    [data_by_year[year], temp_df], ignore_index=True)
                logging.info(f'Successfully loaded file: {file_path}')
            else:
                logging.warning(
                    f'Could not determine year in file: {file_path}')
        except Exception as e:
            logging.error(f'Error loading file {file_path}: {e}')

    return data_by_year


def create_folder(folder_path: str) -> None:
    '''Create folder'''
    try:
        os.makedirs(folder_path, exist_ok=True)
        logging.info(f'Folder {folder_path} created or already exists')
    except Exception as e:
        logging.error(f'Error creating folder {folder_path}: {e}')
        raise


def save_dataframes_by_year(data_by_year: Dict[str, pd.DataFrame], output_folder: str, category: str) -> None:
    '''Save dataframes by year into corresponding subfolders'''
    try:
        for year, df in data_by_year.items():
            year_folder = os.path.join(output_folder, f'{category}_{year}')
            create_folder(year_folder)
            current_datetime = datetime.now().strftime('%Y%m%d_%H%M%S')
            file_path = os.path.join(
                year_folder, f'{category}_data_{year}_{current_datetime}.csv')
            # Check if any file exists in the folder and overwrite if necessary
            existing_files = os.listdir(year_folder)
            if existing_files:
                for existing_file in existing_files:
                    os.remove(os.path.join(year_folder, existing_file))
                logging.info(
                    f'Existing files in {year_folder} have been removed')
            df.to_csv(file_path, index=False)
            logging.info(
                f'{category} data for {year} successfully saved to {file_path}')
    except Exception as e:
        logging.error(f'Error saving dataframes: {e}')
        raise


def main():
    logging.info('-----Start-----')
    folder_path = r'./raw_data/'
    output_folder = r'./split_by_type_year_data/'

    check_folder_exists(folder_path)

    csv_files = get_csv_files(folder_path)

    files_by_category = split_files_by_category(csv_files)

    rent_data_by_year = load_csv_files_by_year(files_by_category['rent'])
    sale_data_by_year = load_csv_files_by_year(files_by_category['sale'])

    create_folder(output_folder)

    save_dataframes_by_year(rent_data_by_year, output_folder, 'rent')
    save_dataframes_by_year(sale_data_by_year, output_folder, 'sale')
    logging.info('-----End-----')


if __name__ == "__main__":
    main()
