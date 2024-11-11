import logging
import os
import re
import sys
from datetime import datetime
from typing import Dict, List

import pandas as pd

FOLDER_PATH = r'./raw_data/'
OUTPUT_FOLDER = r'./split_by_type_year_data/'

log_directory: str = r'./logs'
os.makedirs(log_directory, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_directory, 'data_split.log'),
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)


class FolderNotFoundError(Exception):
    """Exception raised when the specified folder does not exist."""

    def __init__(self, folder_path: str):
        super().__init__(f'Folder {folder_path} does not exist')
        self.folder_path = folder_path


def check_folder_exists(folder_path: str) -> None:
    '''Check if folder exists'''
    if not os.path.exists(folder_path):
        logging.error(f'Folder {folder_path} does not exist')
        raise FolderNotFoundError(folder_path)


def get_csv_files(folder_path: str) -> List[str]:
    '''Get list of CSV files in folder'''
    files = os.listdir(folder_path)
    csv_files = [os.path.join(folder_path, file)
                 for file in files if file.endswith('.csv')]
    return csv_files


def split_files_by_category(csv_files: List[str]) -> Dict[str, List[str]]:
    '''Split files into rent and sale categories'''
    rent_files = list(filter(lambda element: 'rent' in element, csv_files))
    sale_files = list(filter(lambda element: 'rent' not in element, csv_files))
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


def create_folder(folder_path: str) -> bool:
    '''Create folder and return status'''
    try:
        os.makedirs(folder_path, exist_ok=True)
        logging.info(f'Folder {folder_path} created or already exists')
        return True
    except Exception as e:
        logging.error(f'Error creating folder {folder_path}: {e}')
        return False


def save_dataframes_by_year(
        data_by_year: Dict[str, pd.DataFrame], output_folder: str, category: str) -> bool:
    '''Save dataframes by year into corresponding subfolders'''
    try:
        for year, df in data_by_year.items():
            year_folder = os.path.join(output_folder, f'{category}_{year}')
            if not create_folder(year_folder):
                logging.error(
                    f'Failed to create folder {year_folder} for category {category}')
                continue
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
        return True
    except Exception as e:
        logging.error(f'Error saving dataframes for category {category}: {e}')
        return False


def main():
    logging.info('-----Start-----')

    try:
        check_folder_exists(FOLDER_PATH)
    except FolderNotFoundError as e:
        logging.error(e)
        logging.error("Required folder does not exist. Exiting the program.")
        sys.exit(1)

    csv_files = get_csv_files(FOLDER_PATH)
    files_by_category = split_files_by_category(csv_files)

    rent_data_by_year = load_csv_files_by_year(files_by_category['rent'])
    sale_data_by_year = load_csv_files_by_year(files_by_category['sale'])

    if not create_folder(OUTPUT_FOLDER):
        logging.error("Failed to create output folder. Exiting the program.")
        sys.exit(1)

    if not save_dataframes_by_year(rent_data_by_year, OUTPUT_FOLDER, 'rent'):
        logging.error(
            "Failed to save rent data. Continuing with other categories.")

    if not save_dataframes_by_year(sale_data_by_year, OUTPUT_FOLDER, 'sale'):
        logging.error("Failed to save sale data.")

    logging.info('-----End-----')


if __name__ == "__main__":
    main()
